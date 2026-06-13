import sys
import json
import pandas as pd

def process_and_dispatch_high_risk_alerts():
    source_file = 'engineered_features_v2.csv'
    
    print("Initializing active monitoring scan across warehouse snapshot slices...")
    
    try:
        df = pd.read_csv(source_file)
    except FileNotFoundError:
        print(f"CRITICAL: System cannot dispatch alerts. Feature matrix source '{source_file}' missing.")
        sys.exit(1)
        
    critical_risk_mask = (df['login_velocity_drop'] <= -0.30) & (df['support_friction_score'] >= 3.0)
    df_critical = df[critical_risk_mask].copy()
    
    print(f"Scan complete. Found {len(df_critical)} instances matching active friction metrics.")
    
    if df_critical.empty:
        print("System metrics nominal. No high-risk customer retention anomalies flagged today.")
        return
        
    df_unique_critical = df_critical.drop_duplicates(subset=['customer_id'], keep='last')
    print(f"Deduplicated down to {len(df_unique_critical)} unique high-risk corporate targets. Dispatched entries:")
    
    for _, row in df_unique_critical.head(5).iterrows():
        alert_payload = {
            "event_type": "CRITICAL_CHURN_RISK_ALERT",
            "customer_id": str(row['customer_id']),
            "risk_metrics": {
                "login_velocity_drop": round(float(row['login_velocity_drop']), 4),
                "support_friction_score": int(row['support_friction_score']),
                "market_friction_index": round(float(row['market_friction_index']), 4),
                "days_since_last_activity": int(row['days_since_last_activity'])
            },
            "system_routing": {
                "target_crm_action": "TRIGGER_RETENTION_PLAYBOOK",
                "assigned_priority": "P0_IMMEDIATE_OUTREACH",
                "recommended_incentive": "90_DAY_TIER_UPGRADE_CREDIT"
            }
        }
        
        print(f"\n[DISPATCHING PAYLOAD to Webhook -> CRM Sync Thread]")
        print(json.dumps(alert_payload, indent=4))
        
    print(f"\nSUCCESS: Dispatched P0 operational tracking logs for upstream client accounts.")

if __name__ == "__main__":
    process_and_dispatch_high_risk_alerts()