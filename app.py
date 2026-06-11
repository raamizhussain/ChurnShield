import streamlit as st
import pandas as pd

st.set_page_config(page_title="ChurnShield Command Center", layout="wide")

st.title("🛡️ ChurnShield: Causal Analytics & Retention ROI Engine")
st.markdown("Transforming survival probabilities and individualized treatment effects into profitable interventions.")

@st.cache_data
def load_data():
    df = pd.read_csv('causal_uplift_predictions.csv')
    return df

try:
    df_master = load_data()
    
    st.sidebar.header("Financial Parameters")
    clv_input = st.sidebar.number_input("Customer Lifetime Value ($)", min_value=10, max_value=5000, value=200, step=10)
    cost_input = st.sidebar.number_input("Intervention Cost ($)", min_value=1, max_value=500, value=8, step=1)
    
    df_master['expected_roi'] = (clv_input * df_master['uplift_score']) - cost_input
    
    persuadables = df_master[df_master['expected_roi'] > 0]
    total_savings = persuadables['expected_roi'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers Evaluated", len(df_master))
    col2.metric("High-Risk Profiles Found (30d)", len(df_master[df_master['churn_prob_30d'] > 0.05]))
    col3.metric("Persuadables Targeted", len(persuadables))
    col4.metric("Projected Net ROI Savings", f"${total_savings:,.2f}")
    
    st.markdown("---")
    
    st.subheader("🎯 High-Value Optimized Campaign Target List")
    st.markdown("This list filters out Sure Things and Lost Causes, prioritizing customers where the intervention directly drives positive ROI.")
    
    df_display = df_master.sort_values(by='expected_roi', ascending=False).copy()
    df_display['Action Strategy'] = df_display['expected_roi'].apply(lambda x: "🚀 Target Immediate Offer" if x > 0 else "🛑 Hold (No Offer)")
    
    show_cols = ['customer_id', 'churn_prob_30d', 'uplift_score', 'expected_roi', 'Action Strategy']
    st.dataframe(df_display[show_cols].style.format({'churn_prob_30d': '{:.2%}', 'uplift_score': '{:.4f}', 'expected_roi': '${:.2f}'}), width='stretch')
    
    csv_data = df_display[df_display['expected_roi'] > 0][show_cols].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Optimized Marketing Campaign List",
        data=csv_data,
        file_name="churnshield_optimized_campaign.csv",
        mime="text/csv"
    )
    
except FileNotFoundError:
    st.error("Error: causal_uplift_predictions.csv not found. Please verify that all upstream model processing steps executed successfully.")