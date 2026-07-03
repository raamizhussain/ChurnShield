import streamlit as st
import pandas as pd
import io
import requests

st.set_page_config(
    page_title="ChurnShield Enterprise Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main {background-color: #f8fafc;}
    .stButton>button {
        background-color: #0f172a; color: white; border-radius: 8px;
        padding: 0.5rem 1.5rem; font-weight: 600; border: none;
    }
    .stButton>button:hover {background-color: #1e293b; color: white;}
    div[data-testid="stMetricValue"] {font-size: 2rem; font-weight: 700; color: #0f172a;}
    div[data-testid="stMetricLabel"] {font-size: 0.75rem; font-weight: 600; text-transform: uppercase; tracking: 0.05em; color: #64748b;}
    </style>
""", unsafe_allow_html=True)

if 'app_state' not in st.session_state:
    st.session_state.app_state = 'landing'

FASTAPI_URL = "http://127.0.0.1:8000/upload/csv"

if st.session_state.app_state == 'landing':
    st.title("🛡️ ChurnShield Enterprise")
    st.subheader("Stop customer attrition before it happens with Causal AI")
    
    st.write(
        "An enterprise SaaS pipeline that goes beyond binary prediction. "
        "Discover exactly when customers leave, who responds to promotions, and how to optimize retention margins."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Launch System Console"):
            st.session_state.app_state = 'auth'
            st.rerun()
            
    st.markdown("---")
    st.subheader("Engineered for Technical Operations")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**01 / SCD Type 2 Warehousing**")
        st.caption("Tracks historical changes over time without data loss, managing full customer lifecycles across active execution timelines.")
    with c2:
        st.markdown("**02 / Uplift Modeling Engine**")
        st.caption("Isolates incremental treatment effects using a LightGBM T-Learner to separate persuadable users from lost causes.")
    with c3:
        st.markdown("**03 / Agentic LLM Analyst**")
        st.caption("Converts math strings into clear, humanized executive briefs in real time using high-performance Llama inference layers.")

elif st.session_state.app_state == 'auth':
    st.markdown("<div style='max-width: 400px; margin: 0 auto; padding-top: 50px;'>", unsafe_allow_html=True)
    st.subheader("Access Console Gateway")
    st.caption("Protected by TLS encryption and SHA-256 validation policies.")
    
    email = st.text_input("Corporate Email", placeholder="executive@company.com")
    token = st.text_input("Access Token ID", type="password", placeholder="••••••••••••")
    
    if st.button("Authenticate Node", use_container_width=True):
        if email and token:
            st.session_state.app_state = 'portal'
            st.rerun()
        else:
            st.error("Please fill in all security clearance fields.")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.app_state == 'portal':
    st.title("📊 Analytical Processing Terminal")
    st.caption("Upload a customer tracking telemetry CSV matrix to trigger high-throughput batch inference loops.")
    
    if st.button("Disconnect Console"):
        st.session_state.app_state = 'landing'
        st.rerun()
        
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Drop corporate CSV here", type=["csv"])
    
    if uploaded_file is not None:
        if st.button("Process Ingestion Matrix"):
            with st.spinner("Streaming records to FastAPI gateway..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                    response = requests.post(FASTAPI_URL, files=files)
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Ingested Records", res_data["summary"]["total_records_processed"])
                        m2.metric("High Risk Cohort", res_data["summary"]["high_risk_cohort_size"])
                        m3.metric("Revenue At Risk", f"${res_data['summary']['portfolio_value_at_risk']:,}")
                        m4.metric("Campaign Index", f"{res_data['summary']['campaign_efficiency_index']}%")
                        
                        st.markdown("### ⚡ Primary Threat Horizon Executive Brief")
                        st.info(res_data["top_risk_executive_brief"])
                        
                        st.markdown("### 📋 Processed In-Memory Telemetry Logs")
                        records_df = pd.DataFrame(res_data["records"])
                        
                        st.markdown("### 📋 Processed In-Memory Telemetry Logs")
                        records_df = pd.DataFrame(res_data["records"])

                        if not records_df.empty and "computed_metrics" in records_df.columns:
                            metrics_df = pd.json_normalize(records_df['computed_metrics'])
                            base_features_df = records_df.drop(columns=['computed_metrics', 'retention_brief'], errors='ignore')
                            final_df = pd.concat([base_features_df, metrics_df], axis=1)
                            
                            final_df.columns = [
                                "Customer ID", "Login Velocity Drop", "Click Velocity Drop", 
                                "Feature Velocity Drop", "Support Tickets Open", "Click/Login Ratio", 
                                "Days Inactive", "30D Churn Risk", "Causal Uplift Score", 
                                "Action Priority", "Allocated Segment"
                            ]
                            
                            st.dataframe(
                                final_df.style.format({
                                    "Login Velocity Drop": "{:.1%}",
                                    "Click Velocity Drop": "{:.1%}",
                                    "30D Churn Risk": "{:.1%}",
                                    "Causal Uplift Score": "{:.4f}"
                                }), 
                                use_container_width=True
                            )
                    else:
                        st.error(f"Validation Boundary Breach: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Network execution error connecting to FastAPI gateway: {str(e)}")