# ============================================================================
# STREAMLIT AFI ANALYSIS DASHBOARD
# File: streamlit_app.py
# Run with: streamlit run streamlit_app.py
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AFI Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .header-title {
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING (with caching)
# ============================================================================

@st.cache_data
def load_data():
    """Load all CSV data files"""
    data = {}
    
    # Define paths
    table_path = Path("outputs/tables")
    
    try:
        data['district_summary'] = pd.read_csv(table_path / "afi_summary_by_district.csv")
        data['state_summary'] = pd.read_csv(table_path / "afi_summary_by_state.csv")
        data['friction_signals'] = pd.read_csv(table_path / "friction_signal_summary.csv")
        data['hidden_risk'] = pd.read_csv(table_path / "hidden_risk_table.csv")
        data['lifecycle'] = pd.read_csv(table_path / "lifecycle_imbalance_table.csv")
        data['monthly_trends'] = pd.read_csv(table_path / "monthly_afi_trends.csv")
        data['top_100'] = pd.read_csv(table_path / "top_100_high_friction_records.csv")
        data['friction_typology'] = pd.read_csv(table_path / "district_friction_typology.csv")
        
        return data
    except FileNotFoundError as e:
        st.error(f"Error loading data: {e}")
        st.info("Make sure CSV files are in `outputs/tables/` directory")
        return None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def classify_friction(afi):
    """Classify AFI score into friction levels"""
    if afi >= 70:
        return "🔴 High Friction"
    elif afi >= 40:
        return "🟡 Medium Friction"
    else:
        return "🟢 Low Friction"

def get_afi_color(afi):
    """Return color based on AFI value"""
    if afi >= 70:
        return "#ef4444"
    elif afi >= 40:
        return "#f59e0b"
    else:
        return "#10b981"

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.markdown("# 📊 AFI Dashboard Navigation")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select Page:",
    [
        "📈 Dashboard Overview",
        "🔥 High-Risk Districts",
        "⚙️ Friction Signal Analysis",
        "⚠️ Hidden Risk Detection",
        "📋 State Comparison",
        "📅 Trends & Timeline",
        "📊 Detailed Tables",
        "ℹ️ About & Methodology"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filter Options")

# Load data
data = load_data()

if data is None:
    st.error("Failed to load data. Please check your file paths.")
    st.stop()

# Get unique values for filters
states_list = sorted(data['district_summary']['state'].unique())
selected_state = st.sidebar.selectbox(
    "Select State:",
    ["All States"] + states_list
)

# ============================================================================
# PAGE: DASHBOARD OVERVIEW
# ============================================================================

if page == "📈 Dashboard Overview":
    st.markdown('<div class="header-title">📊 Aadhaar Friction Index - Executive Dashboard</div>', 
                unsafe_allow_html=True)
    st.markdown("Real-time monitoring and actionable insights for friction management")
    st.markdown("---")
    
    # Calculate summary metrics
    all_afi = data['district_summary']['avg_afi']
    high_friction_count = len(data['friction_typology'][data['friction_typology']['AFI'] >= 70])
    medium_friction_count = len(data['friction_typology'][
        (data['friction_typology']['AFI'] >= 40) & (data['friction_typology']['AFI'] < 70)])
    
    # Display KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Avg AFI Score", f"{all_afi.mean():.2f}", 
                  delta=f"Median: {all_afi.median():.2f}")
    with col2:
        st.metric("High Friction Districts", high_friction_count, 
                  delta=f"(≥70)")
    with col3:
        st.metric("Medium Friction", medium_friction_count,
                  delta=f"(40-70)")
    with col4:
        st.metric("Total Districts", len(data['district_summary']),
                  delta=f"{len(data['state_summary'])} States")
    with col5:
        st.metric("Hidden Risk Cases", len(data['hidden_risk']),
                  delta="Low updates, High AFI")
    
    st.markdown("---")
    
    # Two-column layout for main visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 AFI Distribution")
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=all_afi,
            nbinsx=50,
            name='AFI Scores',
            marker=dict(color='#3b82f6', opacity=0.7)
        ))
        fig.add_vline(x=all_afi.mean(), line_dash="dash", line_color="red",
                     annotation_text="Mean", annotation_position="top right")
        fig.update_layout(title="Distribution of AFI Across Districts",
                         xaxis_title="AFI Score", yaxis_title="Count",
                         height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🔴 Friction Classification")
        friction_dist = data['friction_typology']['AFI'].apply(classify_friction).value_counts()
        fig = go.Figure(data=[go.Pie(
            labels=friction_dist.index,
            values=friction_dist.values,
            marker=dict(colors=['#ef4444', '#f59e0b', '#10b981'])
        )])
        fig.update_layout(title="Districts by Friction Level", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Top districts
    st.subheader("🏆 Top 15 High-Risk Districts")
    top_15 = data['district_summary'].nlargest(15, 'avg_afi')[['state', 'district', 'avg_afi', 'max_afi', 'months_observed']]
    top_15.columns = ['State', 'District', 'Avg AFI', 'Max AFI', 'Months Observed']
    
    fig = go.Figure(data=[
        go.Bar(x=top_15['Avg AFI'], y=top_15['District'] + ', ' + top_15['State'],
               orientation='h', marker=dict(color=top_15['Avg AFI'], colorscale='Reds'))
    ])
    fig.update_layout(title="Top 15 Districts by Average AFI",
                     xaxis_title="Average AFI Score",
                     height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📋 View Top 15 as Table"):
        st.dataframe(top_15, use_container_width=True, hide_index=True)

# ============================================================================
# PAGE: HIGH-RISK DISTRICTS
# ============================================================================

elif page == "🔥 High-Risk Districts":
    st.markdown('<div class="header-title">🔥 Identifying High-Risk Districts</div>', 
                unsafe_allow_html=True)
    st.markdown("Focus areas for immediate intervention")
    st.markdown("---")
    
    # Filter by state
    if selected_state != "All States":
        filtered_df = data['district_summary'][data['district_summary']['state'] == selected_state]
    else:
        filtered_df = data['district_summary']
    
    # Risk level selector
    risk_level = st.radio("Filter by Risk Level:", 
                          ["All Districts", "High Friction (≥70)", "Medium Friction (40-70)", "Low Friction (<40)"],
                          horizontal=True)
    
    if risk_level == "High Friction (≥70)":
        filtered_df = filtered_df[filtered_df['avg_afi'] >= 70]
    elif risk_level == "Medium Friction (40-70)":
        filtered_df = filtered_df[(filtered_df['avg_afi'] >= 40) & (filtered_df['avg_afi'] < 70)]
    elif risk_level == "Low Friction (<40)":
        filtered_df = filtered_df[filtered_df['avg_afi'] < 40]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.metric(f"Districts in This Category", len(filtered_df))
    with col2:
        st.metric("Avg AFI", f"{filtered_df['avg_afi'].mean():.2f}")
    
    st.markdown("---")
    
    # Interactive scatter plot
    fig = px.scatter(filtered_df, x='avg_afi', y='max_afi', 
                    size='months_observed', 
                    hover_data=['state', 'district', 'min_afi'],
                    color='avg_afi', color_continuous_scale='Reds',
                    title="Average AFI vs Maximum AFI (bubble size = observation period)",
                    labels={'avg_afi': 'Average AFI', 'max_afi': 'Maximum AFI'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("📊 District Details")
    display_cols = ['state', 'district', 'avg_afi', 'max_afi', 'min_afi', 'months_observed']
    display_df = filtered_df[display_cols].sort_values('avg_afi', ascending=False)
    display_df.columns = ['State', 'District', 'Avg AFI', 'Max AFI', 'Min AFI', 'Months']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Download option
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"high_risk_districts_{selected_state}.csv",
        mime="text/csv"
    )

# ============================================================================
# PAGE: FRICTION SIGNAL ANALYSIS
# ============================================================================

elif page == "⚙️ Friction Signal Analysis":
    st.markdown("""<div class="header-title">⚙️ What's Causing the Friction?</div>""", unsafe_allow_html=True)
    st.markdown("Analyzing UIS, RIS, BSS, TSD signals to explain AFI")
    st.markdown("---")
    
    # Filter by state
    if selected_state != "All States":
        filtered_signals = data['friction_signals'][data['friction_signals']['state'] == selected_state]
    else:
        filtered_signals = data['friction_signals']
    
    # Signal explanation
    st.info("""
    **Signal Definitions:**
    - **UIS** (Unresolved Issues Score): Issues not yet resolved
    - **RIS** (Resolution Issues Score): Problems in resolution process
    - **BSS** (Biometric Signal Score): Biometric-related friction
    - **TSD** (Technical Delays Score): System/technical delays
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg UIS", f"{filtered_signals['avg_UIS'].mean():.2f}")
    with col2:
        st.metric("Avg RIS", f"{filtered_signals['avg_RIS'].mean():.2f}")
    with col3:
        st.metric("Avg BSS", f"{filtered_signals['avg_BSS'].mean():.2f}")
    with col4:
        st.metric("Avg TSD", f"{filtered_signals['avg_TSD'].mean():.2f}")
    
    st.markdown("---")
    
    # Parallel coordinates plot
    fig = go.Figure(data=
        go.Parcoords(
            line = dict(color = filtered_signals['avg_UIS'],
                       colorscale = 'Reds'),
            dimensions = list([
                dict(range = [filtered_signals['avg_UIS'].min(), filtered_signals['avg_UIS'].max()],
                    label = 'UIS', values = filtered_signals['avg_UIS']),
                dict(range = [filtered_signals['avg_RIS'].min(), filtered_signals['avg_RIS'].max()],
                    label = 'RIS', values = filtered_signals['avg_RIS']),
                dict(range = [filtered_signals['avg_BSS'].min(), filtered_signals['avg_BSS'].max()],
                    label = 'BSS', values = filtered_signals['avg_BSS']),
                dict(range = [filtered_signals['avg_TSD'].min(), filtered_signals['avg_TSD'].max()],
                    label = 'TSD', values = filtered_signals['avg_TSD'])
            ])
        )
    )
    fig.update_layout(title="Signal Patterns Across Districts", height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top signal drivers
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 Top UIS Districts (Unresolved Issues)")
        top_uis = filtered_signals.nlargest(10, 'avg_UIS')[['state', 'district', 'avg_UIS']]
        fig = go.Figure(data=[go.Bar(y=top_uis['district'], x=top_uis['avg_UIS'], orientation='h', marker=dict(color='#ef4444'))])
        fig.update_layout(title="", height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🟡 Top BSS Districts (Biometric Issues)")
        top_bss = filtered_signals.nlargest(10, 'avg_BSS')[['state', 'district', 'avg_BSS']]
        fig = go.Figure(data=[go.Bar(y=top_bss['district'], x=top_bss['avg_BSS'], orientation='h', marker=dict(color='#f59e0b'))])
        fig.update_layout(title="", height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE: HIDDEN RISK DETECTION
# ============================================================================

elif page == "⚠️ Hidden Risk Detection":
    st.markdown('<div class="header-title">⚠️ Hidden Risk: Low Updates ≠ Low Friction</div>', 
                unsafe_allow_html=True)
    st.markdown("Identifying overlooked problem areas with few updates but high friction")
    st.markdown("---")
    
    st.metric("Hidden Risk Cases Found", len(data['hidden_risk']))
    
    # Scatter plot: Updates vs AFI
    fig = go.Figure(data=[
        go.Scatter(
            x=data['hidden_risk']['total_updates'],
            y=data['hidden_risk']['AFI'],
            mode='markers',
            marker=dict(
                size=8,
                color=data['hidden_risk']['AFI'],
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="AFI")
            ),
            text=data['hidden_risk']['district'] + ', ' + data['hidden_risk']['state'],
            hovertemplate='<b>%{text}</b><br>Updates: %{x}<br>AFI: %{y:.2f}<extra></extra>'
        )
    ])
    fig.update_layout(
        title="Hidden Risk: Update Volume vs Friction Level",
        xaxis_title="Total Updates",
        yaxis_title="AFI Score",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📉 Update Distribution in Hidden Risk Cases")
        fig = go.Figure(data=[
            go.Histogram(x=data['hidden_risk']['total_updates'], nbinsx=30, marker=dict(color='#3b82f6'))
        ])
        fig.update_layout(title="", xaxis_title="Total Updates", yaxis_title="Count", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🔴 AFI Distribution in Hidden Risk")
        fig = go.Figure(data=[
            go.Histogram(x=data['hidden_risk']['AFI'], nbinsx=30, marker=dict(color='#ef4444'))
        ])
        fig.update_layout(title="", xaxis_title="AFI Score", yaxis_title="Count", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Top hidden risk cases
    st.subheader("🔴 Top 20 Hidden Risk Cases")
    top_hidden = data['hidden_risk'].nlargest(20, 'AFI')[['state', 'district', 'period', 'total_updates', 'AFI']]
    top_hidden.columns = ['State', 'District', 'Period', 'Total Updates', 'AFI']
    st.dataframe(top_hidden, use_container_width=True, hide_index=True)

# ============================================================================
# PAGE: STATE COMPARISON
# ============================================================================

elif page == "📋 State Comparison":
    st.markdown('<div class="header-title">📋 State-Level Analysis</div>', 
                unsafe_allow_html=True)
    st.markdown("Comparative insights for policy and resource allocation")
    st.markdown("---")
    
    st.subheader("📊 States by Average AFI")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        sort_by = st.radio("Sort by:", ["Average AFI", "Maximum AFI", "Number of Districts"], horizontal=True)
    
    if sort_by == "Average AFI":
        state_data = data['state_summary'].sort_values('avg_afi', ascending=False)
    elif sort_by == "Maximum AFI":
        state_data = data['state_summary'].sort_values('max_afi', ascending=False)
    else:
        state_data = data['state_summary'].sort_values('districts', ascending=False)
    
    # Bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=state_data['state'],
            y=state_data['avg_afi'],
            marker=dict(color=state_data['avg_afi'], colorscale='Reds'),
            text=state_data['avg_afi'].round(2),
            textposition='outside'
        )
    ])
    fig.update_layout(
        title="Average AFI by State",
        xaxis_title="State",
        yaxis_title="Average AFI",
        height=500,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Scatter: Avg vs Max
    st.subheader("📈 Average AFI vs Maximum AFI")
    fig = px.scatter(
        data['state_summary'],
        x='avg_afi',
        y='max_afi',
        size='districts',
        hover_data=['state', 'districts'],
        color='avg_afi',
        color_continuous_scale='Reds',
        title="State Performance (bubble size = # districts)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("📊 State Summary Table")
    state_display = data['state_summary'].sort_values('avg_afi', ascending=False)
    state_display.columns = ['State', 'Avg AFI', 'Max AFI', 'Districts']
    st.dataframe(state_display, use_container_width=True, hide_index=True)

# ============================================================================
# PAGE: TRENDS & TIMELINE
# ============================================================================

elif page == "📅 Trends & Timeline":
    st.markdown('<div class="header-title">📅 Temporal Trends Analysis</div>', 
                unsafe_allow_html=True)
    st.markdown("Monitoring changes over time")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Monthly AFI Trends")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['monthly_trends']['period'],
            y=data['monthly_trends']['avg_afi'],
            mode='lines+markers',
            name='Average AFI',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=data['monthly_trends']['period'],
            y=data['monthly_trends']['median_afi'],
            mode='lines+markers',
            name='Median AFI',
            line=dict(color='#10b981', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        fig.update_layout(title="", xaxis_title="Period", yaxis_title="AFI Score", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Districts Reporting Over Time")
        fig = go.Figure(data=[
            go.Bar(x=data['monthly_trends']['period'], 
                  y=data['monthly_trends']['districts_reporting'],
                  marker=dict(color='#8b5cf6'))
        ])
        fig.update_layout(title="", xaxis_title="Period", yaxis_title="Number of Districts", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Lifecycle imbalance
    st.subheader("📋 Lifecycle Imbalance: Enrolment vs Updates")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['lifecycle']['period'],
            y=data['lifecycle']['total_enrolments'],
            mode='lines+markers',
            name='Enrolments',
            line=dict(color='#3b82f6', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=data['lifecycle']['period'],
            y=data['lifecycle']['total_updates'],
            mode='lines+markers',
            name='Total Updates',
            line=dict(color='#ef4444', width=2)
        ))
        fig.update_layout(title="Enrolments vs Updates", xaxis_title="Period", yaxis_title="Count", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(data=[
            go.Scatter(
                x=data['lifecycle']['period'],
                y=data['lifecycle']['update_to_enrolment_ratio'],
                mode='lines+markers',
                fill='tozeroy',
                marker=dict(color='#f59e0b', size=8)
            )
        ])
        fig.update_layout(
            title="Update to Enrolment Ratio",
            xaxis_title="Period",
            yaxis_title="Ratio",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE: DETAILED TABLES
# ============================================================================

elif page == "📊 Detailed Tables":
    st.markdown('<div class="header-title">📊 Detailed Data Tables</div>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    table_view = st.selectbox(
        "Select Table to View:",
        [
            "Top 100 High Friction Records",
            "District Friction Typology",
            "All Districts Summary",
            "All States Summary",
            "Friction Signals by District",
            "Monthly Trends",
            "Lifecycle Imbalance"
        ]
    )
    
    if table_view == "Top 100 High Friction Records":
        st.subheader("🔴 Top 100 Highest Friction Records")
        display_df = data['top_100'].head(100)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        csv = display_df.to_csv(index=False)
        st.download_button("📥 Download Top 100", csv, "top_100_records.csv", "text/csv")
    
    elif table_view == "District Friction Typology":
        st.subheader("⚙️ District Friction Classification")
        display_df = data['friction_typology'].head(100)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        csv = display_df.to_csv(index=False)
        st.download_button("📥 Download Friction Typology", csv, "friction_typology.csv", "text/csv")
    
    elif table_view == "All Districts Summary":
        st.subheader("📋 AFI Summary by District")
        display_df = data['district_summary'].sort_values('avg_afi', ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        csv = display_df.to_csv(index=False)
        st.download_button("📥 Download District Summary", csv, "district_summary.csv", "text/csv")
    
    elif table_view == "All States Summary":
        st.subheader("📋 AFI Summary by State")
        display_df = data['state_summary'].sort_values('avg_afi', ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        csv = display_df.to_csv(index=False)
        st.download_button("📥 Download State Summary", csv, "state_summary.csv", "text/csv")
    
    elif table_view == "Friction Signals by District":
        st.subheader("⚙️ Friction Signals Summary")
        display_df = data['friction_signals'].sort_values('avg_UIS', ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        csv = display_df.to_csv(index=False)
        st.download_button("📥 Download Friction Signals", csv, "friction_signals.csv", "text/csv")
    
    elif table_view == "Monthly Trends":
        st.subheader("📅 Monthly AFI Trends")
        display_df = data['monthly_trends']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        csv = display_df.to_csv(index=False)
        st.download_button("📥 Download Monthly Trends", csv, "monthly_trends.csv", "text/csv")
    
    elif table_view == "Lifecycle Imbalance":
        st.subheader("📋 Lifecycle Imbalance Table")
        display_df = data['lifecycle']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        csv = display_df.to_csv(index=False)
        st.download_button("📥 Download Lifecycle Data", csv, "lifecycle_imbalance.csv", "text/csv")

# ============================================================================
# PAGE: ABOUT & METHODOLOGY
# ============================================================================

elif page == "ℹ️ About & Methodology":
    st.markdown('<div class="header-title">ℹ️ About This Dashboard</div>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📖 Overview")
        st.markdown("""
        The **Aadhaar Friction Index (AFI) Dashboard** provides comprehensive analysis of 
        enrollment and update processes across India's districts and states.
        
        ### Key Metrics Explained
        
        **AFI (Aadhaar Friction Index)**
        - Score from 0-100 indicating operational friction
        - Higher = More problems
        - Combines multiple friction signals
        
        **Friction Levels**
        - 🔴 **High Friction (≥70)**: Immediate action required
        - 🟡 **Medium Friction (40-70)**: Monitor and improve
        - 🟢 **Low Friction (<40)**: Good performance
        
        ### Signal Components
        
        | Signal | Meaning |
        |--------|---------|
        | **UIS** | Unresolved Issues Score - problems awaiting resolution |
        | **RIS** | Resolution Issues Score - problems in resolution process |
        | **BSS** | Biometric Signal Score - biometric-related friction |
        | **TSD** | Technical Delays Score - System latency and technical failures |
        """)

        st.subheader("⚠️ Hidden Risk Methodology")
        st.markdown("""
        **"Hidden Risk"** districts are those that might fly under the radar because their absolute volume of updates is low. 
        However, when updates *do* occur, they face high friction.
        
        * **Detection Logic:** Low `total_updates` percentile + High `AFI` (>70).
        * **Implication:** Citizens in these areas may have given up on trying to update their details due to systemic barriers (service denial), rather than a lack of demand.
        """)

    with col2:
        st.markdown("### 💾 Data Sources")
        st.info("""
        **Primary Source:**
        District-level friction logs, enrolment counters, and update request logs.
        
        **Update Frequency:** Monthly aggregation.
        
        **Data Path:**
        `/outputs/tables/`
        """)

        st.markdown("### 🛠 Version Info")
        st.code("""
        Dashboard: v1.0.2
        Model: AFI-Beta-4
        Streamlit: v1.38+
        """)

        # st.markdown("### 📞 Contact")
        # st.write("For specific inquiries regarding district-level data discrepancies, please contact the Data Science Team.")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding-bottom: 20px;'>
        <p><strong>Aadhaar Friction Index (AFI) Analysis Dashboard</strong></p>
        <p style='font-size: 0.8rem;'>
            Developed for Performance Monitoring & Optimization | © 2026 Yogesh and Sojwal
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)