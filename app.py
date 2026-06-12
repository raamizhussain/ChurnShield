import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="ChurnShield Command Center", layout="wide")

st.title("🛡️ ChurnShield: Enterprise Retention ROI Engine")
st.markdown("Transforming multi-tier survival predictions into optimized business value outcomes.")

@st.cache_data
def load_data():
    df_causal = pd.read_csv('causal_uplift_predictions.csv')
    df_profiles = pd.read_csv('mock_customer_profiles.csv')
    return pd.merge(df_causal, df_profiles, on='customer_id')

try:
    df_master = load_data()
    
    st.sidebar.header("🎛️ Tier-Based Valuation Controls")
    st.sidebar.markdown("**Customer Lifetime Value (CLV)**")
    clv_free = st.sidebar.number_input("Free Tier CLV ($)", value=10)
    clv_prem = st.sidebar.number_input("Premium Tier CLV ($)", value=120)
    clv_ent = st.sidebar.number_input("Enterprise Tier CLV ($)", value=1500)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Intervention Coupon Costs**")
    cost_free = st.sidebar.number_input("Free Offer Cost ($)", value=2)
    cost_prem = st.sidebar.number_input("Premium Offer Cost ($)", value=20)
    cost_ent = st.sidebar.number_input("Enterprise Offer Cost ($)", value=150)
    
    clv_map = {'Free': clv_free, 'Premium': clv_prem, 'Enterprise': clv_ent}
    cost_map = {'Free': cost_free, 'Premium': cost_prem, 'Enterprise': cost_ent}
    
    df_master['assigned_clv'] = df_master['current_tier'].map(clv_map)
    df_master['assigned_cost'] = df_master['current_tier'].map(cost_map)
    df_master['expected_roi'] = (df_master['assigned_clv'] * df_master['uplift_score']) - df_master['assigned_cost']
    
    persuadables = df_master[df_master['expected_roi'] > 0]
    total_savings = persuadables['expected_roi'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Profiles Evaluated", len(df_master))
    col2.metric("High-Risk (30d Churn > 50%)", len(df_master[df_master['churn_prob_30d'] > 0.5]))
    col3.metric("Profitable Campaign Targets", len(persuadables))
    col4.metric("Projected Financial Savings", f"${total_savings:,.2f}")
    
    st.markdown("---")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("📈 Kaplan-Meier Survival Curves (By Tier)")
        
        timeline = np.arange(1, 91)
        fig_km = go.Figure()
        
        for tier in ['Free', 'Premium', 'Enterprise']:
            tier_df = df_master[df_master['current_tier'] == tier]
            if len(tier_df) > 0:
                mean_30 = tier_df['churn_prob_30d'].mean()
                mean_60 = tier_df['churn_prob_60d'].mean()
                mean_90 = tier_df['churn_prob_90d'].mean()
                
                decay_rates = []
                for t in timeline:
                    if t <= 30:
                        val = 1 - (mean_30 * (t / 30))
                    elif t <= 60:
                        val = 1 - mean_30 - ((mean_60 - mean_30) * ((t - 30) / 30))
                    else:
                        val = 1 - mean_60 - ((mean_90 - mean_60) * ((t - 60) / 30))
                    decay_rates.append(max(0.0, val))
                
                fig_km.add_trace(go.Scatter(x=timeline, y=decay_rates, mode='lines', name=f'{tier} Cohort'))
                
        fig_km.update_layout(
            xaxis_title="Timeline Horizons (Days)",
            yaxis_title="Probability of Remaining Subscribed",
            margin=dict(l=20, r=20, t=20, b=20),
            height=350,
            template="plotly_dark"
        )
        st.plotly_chart(fig_km, use_container_width=True)
        
    with chart_col2:
        st.subheader("🎯 Custom Qini Uplift Evaluation Curve")
        
        df_qini = df_master.sort_values(by='uplift_score', ascending=False).copy()
        df_qini['cum_targets'] = np.arange(1, len(df_qini) + 1)
        df_qini['cum_spend'] = df_qini['assigned_cost'].cumsum()
        df_qini['cum_saved_value'] = (df_qini['assigned_clv'] * df_qini['actual_outcome']).cumsum() - df_qini['cum_spend']
        
        random_y = np.linspace(0, df_qini['cum_saved_value'].iloc[-1], len(df_qini))
        
        fig_qini = go.Figure()
        fig_qini.add_trace(go.Scatter(x=df_qini['cum_targets'], y=df_qini['cum_saved_value'], mode='lines', name='ChurnShield Strategy', line=dict(color='#00FFCC')))
        fig_qini.add_trace(go.Scatter(x=df_qini['cum_targets'], y=random_y, mode='lines', name='Random Strategy (Baseline)', line=dict(dash='dash', color='#FF6666')))
        
        fig_qini.update_layout(
            xaxis_title="Population Targeted (Sorted by Score)",
            yaxis_title="Incremental Value Generated ($)",
            margin=dict(l=20, r=20, t=20, b=20),
            height=350,
            template="plotly_dark",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        st.plotly_chart(fig_qini, use_container_width=True)
        
    st.markdown("---")
    st.subheader("📋 Cross-Tier Campaign Target Directory")
    
    df_display = df_master.sort_values(by='expected_roi', ascending=False).copy()
    df_display['Action Strategy'] = df_display['expected_roi'].apply(lambda x: "🚀 Target Immediate Offer" if x > 0 else "🛑 Hold (No Offer)")
    
    show_cols = ['customer_id', 'current_tier', 'churn_prob_30d', 'uplift_score', 'expected_roi', 'Action Strategy']
    st.dataframe(
        df_display[show_cols].style.format({
            'churn_prob_30d': '{:.2%}', 
            'uplift_score': '{:.4f}', 
            'expected_roi': '${:.2f}'
        }), 
        use_container_width=True
    )
    
except FileNotFoundError:
    st.error("Data tracking files missing. Please run the master orchestrator script first.")