import sys
import os
import io
from datetime import datetime, timedelta
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from llm_explanation_worker import generate_retention_brief

load_dotenv()

app = FastAPI(title="ChurnShield Autonomous Raw-Log SaaS Engine", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CustomerInferencePayload(BaseModel):
    customer_id: str = Field(..., example="CUST_99999")
    login_velocity_drop: float = Field(..., example=-0.45)
    click_velocity_drop: float = Field(..., example=-0.22)
    feature_velocity_drop: float = Field(..., example=-0.10)
    support_friction_score: float = Field(..., example=3.0)
    click_to_login_ratio: float = Field(..., example=1.25)
    days_since_last_activity: float = Field(..., example=4.0)

@app.get("/health")
def health_check():
    return {"status": "GREEN", "services_bound": True}

@app.post("/predict/uplift")
def predict_realtime_uplift(payload: CustomerInferencePayload):
    try:
        raw_input = payload.model_dump()
        return process_single_customer(raw_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference execution failure: {str(e)}")

@app.post("/upload/csv")
async def upload_corporate_sheet(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a valid .csv spreadsheet.")
    
    try:
        contents = await file.read()
        df_raw = pd.read_csv(io.BytesIO(contents))
        
        required_columns = ["customer_id", "timestamp", "activity_type", "resolved"]
        missing = [col for col in required_columns if col not in df_raw.columns]
        if missing:
            raise HTTPException(
                status_code=420, 
                detail=f"Schema validation failed. Missing raw logging attributes: {missing}"
            )
            
        df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'])
        
        computed_features = []
        unique_customers = df_raw['customer_id'].unique()
        
        max_date = df_raw['timestamp'].max()
        window_7d = max_date - timedelta(days=7)
        window_14d = max_date - timedelta(days=14)
        
        for cust_id in unique_customers:
            df_cust = df_raw[df_raw['customer_id'] == cust_id]
            
            logins_recent = len(df_cust[(df_cust['timestamp'] >= window_7d) & (df_cust['activity_type'] == 'login')])
            logins_prior = len(df_cust[(df_cust['timestamp'] >= window_14d) & (df_cust['timestamp'] < window_7d) & (df_cust['activity_type'] == 'login')])
            
            clicks_recent = len(df_cust[(df_cust['timestamp'] >= window_7d) & (df_cust['activity_type'] == 'click')])
            clicks_prior = len(df_cust[(df_cust['timestamp'] >= window_14d) & (df_cust['timestamp'] < window_7d) & (df_cust['activity_type'] == 'click')])
            
            login_drop = (logins_recent - logins_prior) / max(1, logins_prior)
            click_drop = (clicks_recent - clicks_prior) / max(1, clicks_prior)
            
            unresolved_tickets = len(df_cust[(df_cust['activity_type'] == 'support_ticket') & (df_cust['resolved'] == False)])
            
            total_logins = len(df_cust[df_cust['activity_type'] == 'login'])
            total_clicks = len(df_cust[df_cust['activity_type'] == 'click'])
            click_ratio = total_clicks / max(1, total_logins)
            
            last_activity = df_cust['timestamp'].max()
            days_inactive = float((max_date - last_activity).days)
            
            features = {
                "customer_id": cust_id,
                "login_velocity_drop": round(float(login_drop), 2),
                "click_velocity_drop": round(float(click_drop), 2),
                "feature_velocity_drop": 0.0,
                "support_friction_score": float(unresolved_tickets),
                "click_to_login_ratio": round(float(click_ratio), 2),
                "days_since_last_activity": days_inactive
            }
            
            computed_features.append(features)
            
        processed_customers = []
        high_risk_count = 0
        total_revenue_at_risk = 0.0
        
        for cust_feat in computed_features:
            result = process_single_customer(cust_feat, generate_llm=False)
            processed_customers.append(result)
            
            if result["computed_metrics"]["action_priority"] == "HIGH":
                high_risk_count += 1
                total_revenue_at_risk += 4500.00
                
        if processed_customers:
            top_risk = max(processed_customers, key=lambda x: x["computed_metrics"]["churn_probability_30d"])
            
            full_feature_profile = next(f for f in computed_features if f["customer_id"] == top_risk["customer_id"])
            
            detailed_brief = process_single_customer(full_feature_profile, generate_llm=True)["retention_brief"]
        else:
            detailed_brief = "No active customer records discovered inside the uploaded matrix dataset."

        return {
            "status": "SUCCESS",
            "summary": {
                "total_records_processed": len(unique_customers),
                "high_risk_cohort_size": high_risk_count,
                "portfolio_value_at_risk": total_revenue_at_risk,
                "campaign_efficiency_index": round((high_risk_count / len(unique_customers)) * 100, 2) if len(unique_customers) > 0 else 0
            },
            "top_risk_executive_brief": detailed_brief,
            "records": processed_customers
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file structure: {str(e)}")

def process_single_customer(data: dict, generate_llm: bool = True):
    simulated_lift = (abs(data['login_velocity_drop']) * 0.45) + (data['support_friction_score'] * 0.05)
    simulated_churn = min(0.99, (data['days_since_last_activity'] * 0.12) + abs(data['login_velocity_drop'] * 0.35))
    
    churn_probability = round(float(simulated_churn), 4)
    causal_uplift_score = round(float(simulated_lift), 4)
    action_priority = "HIGH" if causal_uplift_score > 0.15 else "STANDARD"
    allocated_segment = "Persuadable" if action_priority == "HIGH" else "Sure Thing"
    
    response = {
        "customer_id": data['customer_id'],
        "login_velocity_drop": data['login_velocity_drop'],
        "click_velocity_drop": data['click_velocity_drop'],
        "feature_velocity_drop": data['feature_velocity_drop'],
        "support_friction_score": data['support_friction_score'],
        "click_to_login_ratio": data['click_to_login_ratio'],
        "days_since_last_activity": data['days_since_last_activity'],
        "computed_metrics": {
            "churn_probability_30d": churn_probability,
            "causal_uplift_score": causal_uplift_score,
            "action_priority": action_priority,
            "allocated_segment": allocated_segment
        }
    }
    
    if generate_llm:
        if data['support_friction_score'] >= 3.0:
            top_driver = f"high support friction score of {data['support_friction_score']} unresolved tickets"
        elif data['login_velocity_drop'] <= -0.30:
            top_driver = f"critical login velocity drop of {data['login_velocity_drop'] * 100:.1f}%"
        else:
            top_driver = "general drop-off across interface interaction velocities"
            
        response["retention_brief"] = generate_retention_brief(
            customer_id=data['customer_id'],
            churn_prob=churn_probability,
            uplift_score=causal_uplift_score,
            segment=allocated_segment,
            top_driver=top_driver,
            clv=4500.00
        )
    return response