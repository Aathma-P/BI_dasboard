import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Marketing Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #b3d9e6;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load all processed datasets"""
    try:
        marketing_df = pd.read_csv('processed_marketing_data.csv')
        business_df = pd.read_csv('processed_business_data.csv')
        combined_df = pd.read_csv('combined_daily_data.csv')
        platform_summary = pd.read_csv('platform_summary.csv')
        tactic_summary = pd.read_csv('tactic_summary.csv')
        
        # Convert dates
        marketing_df['date'] = pd.to_datetime(marketing_df['date'])
        business_df['date'] = pd.to_datetime(business_df['date'])
        combined_df['date'] = pd.to_datetime(combined_df['date'])
        
        # Load insights
        with open('insights.json', 'r') as f:
            insights = json.load(f)
            
        return marketing_df, business_df, combined_df, platform_summary, tactic_summary, insights
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

def create_kpi_cards(insights):
    """Create KPI cards for overview"""
    overview = insights['overview']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Marketing Spend",
            value=f"${overview['total_spend']:,.0f}",
            help="Total spend across all platforms and campaigns"
        )
    
    with col2:
        st.metric(
            label="Attributed Revenue",
            value=f"${overview['total_attributed_revenue']:,.0f}",
            help="Revenue directly attributed to marketing campaigns"
        )
    
    with col3:
        st.metric(
            label="Overall ROAS",
            value=f"{overview['overall_roas']:.2f}x",
            delta=f"{(overview['overall_roas'] - 1)*100:.1f}% ROI",
            help="Return on Ad Spend across all campaigns"
        )
    
    with col4:
        st.metric(
            label="Marketing Attribution Rate",
            value=f"{overview['marketing_attribution_rate']:.1f}%",
            help="Percentage of total business revenue attributed to marketing"
        )

def create_overview_page(marketing_df, business_df, combined_df, insights):
    """Create the main overview page"""
    st.markdown('<h1 class="main-header">📊 Marketing Intelligence Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Executive Summary
    st.subheader("🎯 Executive Summary")
    create_kpi_cards(insights)
    
    # Key insights box
    st.markdown("""
    <div class="insight-box">
        <h4>🔍 Key Insights</h4>
        <ul>
            <li><strong>Performance Period:</strong> 120 days of marketing and business data (May 16 - Sep 12, 2025)</li>
            <li><strong>Multi-Platform Strategy:</strong> Active campaigns across Facebook, Google, and TikTok</li>
            <li><strong>Diverse Tactics:</strong> ASC, Prospecting, Non-Branded Search, Display, Retargeting, and Spark Ads</li>
            <li><strong>Geographic Focus:</strong> Primary markets in New York and California</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Daily Performance Trends
    st.subheader("📈 Daily Performance Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue trends
        fig_revenue = go.Figure()
        fig_revenue.add_trace(go.Scatter(
            x=combined_df['date'],
            y=combined_df['total revenue'],
            mode='lines',
            name='Total Business Revenue',
            line=dict(color='#1f77b4', width=3)
        ))
        fig_revenue.add_trace(go.Scatter(
            x=combined_df['date'],
            y=combined_df['attributed revenue'],
            mode='lines',
            name='Attributed Revenue',
            line=dict(color='#ff7f0e', width=2)
        ))
        fig_revenue.update_layout(
            title="Revenue Performance Over Time",
            xaxis_title="Date",
            yaxis_title="Revenue ($)",
            hovermode='x unified',
            showlegend=True
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        # ROAS trend
        fig_roas = px.line(
            combined_df, 
            x='date', 
            y='roas',
            title="Return on Ad Spend (ROAS) Trend",
            color_discrete_sequence=['#2ca02c']
        )
        fig_roas.add_hline(
            y=combined_df['roas'].mean(), 
            line_dash="dash", 
            line_color="red",
            annotation_text=f"Avg ROAS: {combined_df['roas'].mean():.2f}"
        )
        fig_roas.update_layout(
            xaxis_title="Date",
            yaxis_title="ROAS",
            hovermode='x unified'
        )
        st.plotly_chart(fig_roas, use_container_width=True)
    
    # Marketing vs Business Performance
    st.subheader("🔗 Marketing Impact on Business Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Correlation between marketing spend and business revenue
        fig_correlation = px.scatter(
            combined_df,
            x='spend',
            y='total revenue',
            size='# of orders',
            color='roas',
            title="Marketing Spend vs Business Revenue",
            color_continuous_scale='RdYlGn',
            hover_data=['date', 'clicks', 'new customers']
        )
        fig_correlation.update_layout(
            xaxis_title="Daily Marketing Spend ($)",
            yaxis_title="Total Business Revenue ($)"
        )
        st.plotly_chart(fig_correlation, use_container_width=True)
    
    with col2:
        # Customer acquisition cost trends
        fig_cac = px.line(
            combined_df,
            x='date',
            y='customer_acquisition_cost',
            title="Customer Acquisition Cost Trend",
            color_discrete_sequence=['#d62728']
        )
        fig_cac.add_hline(
            y=combined_df['customer_acquisition_cost'].mean(),
            line_dash="dash",
            line_color="blue",
            annotation_text=f"Avg CAC: ${combined_df['customer_acquisition_cost'].mean():.2f}"
        )
        fig_cac.update_layout(
            xaxis_title="Date",
            yaxis_title="Customer Acquisition Cost ($)"
        )
        st.plotly_chart(fig_cac, use_container_width=True)

def create_platform_analysis_page(marketing_df, platform_summary, insights):
    """Create platform performance analysis page"""
    st.markdown('<h1 class="main-header">🚀 Platform Performance Analysis</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Platform overview metrics
    st.subheader("📊 Platform Performance Overview")
    
    col1, col2, col3 = st.columns(3)
    
    for i, platform in enumerate(['Facebook', 'Google', 'TikTok']):
        platform_data = platform_summary[platform_summary['platform'] == platform].iloc[0]
        
        with [col1, col2, col3][i]:
            st.metric(
                label=f"{platform} ROAS",
                value=f"{platform_data['roas']:.2f}x",
                help=f"Return on Ad Spend for {platform}"
            )
            st.metric(
                label=f"{platform} Spend",
                value=f"${platform_data['spend']:,.0f}",
                help=f"Total spend on {platform}"
            )
            st.metric(
                label=f"{platform} Revenue",
                value=f"${platform_data['attributed revenue']:,.0f}",
                help=f"Attributed revenue from {platform}"
            )
    
    # Platform comparison charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Spend distribution
        fig_spend = px.pie(
            platform_summary,
            values='spend',
            names='platform',
            title="Marketing Spend Distribution by Platform",
            color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
        )
        fig_spend.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_spend, use_container_width=True)
    
    with col2:
        # Revenue distribution
        fig_revenue = px.pie(
            platform_summary,
            values='attributed revenue',
            names='platform',
            title="Attributed Revenue Distribution by Platform",
            color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
        )
        fig_revenue.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Platform performance metrics comparison
    st.subheader("🔍 Detailed Platform Metrics Comparison")
    
    metrics = ['impression', 'clicks', 'spend', 'attributed revenue', 'ctr', 'cpc', 'roas']
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_metric = st.selectbox("Select Metric to Compare", metrics, index=6)
        
        fig_comparison = px.bar(
            platform_summary,
            x='platform',
            y=selected_metric,
            title=f"{selected_metric.title()} Comparison by Platform",
            color='platform',
            color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
        )
        fig_comparison.update_layout(showlegend=False)
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    with col2:
        # Daily platform performance
        daily_platform = marketing_df.groupby(['date', 'platform']).agg({
            'spend': 'sum',
            'attributed revenue': 'sum',
            'roas': 'mean'
        }).reset_index()
        
        fig_daily = px.line(
            daily_platform,
            x='date',
            y='roas',
            color='platform',
            title="Daily ROAS by Platform",
            color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
        )
        fig_daily.update_layout(
            xaxis_title="Date",
            yaxis_title="ROAS",
            hovermode='x unified'
        )
        st.plotly_chart(fig_daily, use_container_width=True)
    
    # Platform insights
    st.markdown("""
    <div class="insight-box">
        <h4>💡 Platform Insights</h4>
        <ul>
            <li><strong>Top Performer:</strong> Identify which platform delivers the highest ROAS</li>
            <li><strong>Efficiency Analysis:</strong> Compare cost per click and conversion rates across platforms</li>
            <li><strong>Scale Opportunities:</strong> Platforms with good performance but lower spend share</li>
            <li><strong>Optimization Focus:</strong> Platforms showing declining performance trends</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def create_campaign_analysis_page(marketing_df, tactic_summary):
    """Create campaign and tactic analysis page"""
    st.markdown('<h1 class="main-header">🎯 Campaign & Tactic Analysis</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Tactic performance overview
    st.subheader("📈 Tactic Performance Overview")
    
    # Sort tactics by ROAS for better visualization
    tactic_summary_sorted = tactic_summary.sort_values('roas', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_tactic_roas = px.bar(
            tactic_summary_sorted,
            x='tactic',
            y='roas',
            title="ROAS by Marketing Tactic",
            color='roas',
            color_continuous_scale='RdYlGn'
        )
        fig_tactic_roas.update_layout(
            xaxis_title="Marketing Tactic",
            yaxis_title="ROAS",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_tactic_roas, use_container_width=True)
    
    with col2:
        fig_tactic_spend = px.bar(
            tactic_summary_sorted,
            x='tactic',
            y='spend',
            title="Total Spend by Marketing Tactic",
            color='spend',
            color_continuous_scale='Blues'
        )
        fig_tactic_spend.update_layout(
            xaxis_title="Marketing Tactic",
            yaxis_title="Total Spend ($)",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_tactic_spend, use_container_width=True)
    
    # Campaign-level analysis
    st.subheader("🔍 Campaign-Level Performance")
    
    # Campaign performance by platform and tactic
    campaign_performance = marketing_df.groupby(['platform', 'tactic', 'campaign']).agg({
        'impression': 'sum',
        'clicks': 'sum',
        'spend': 'sum',
        'attributed revenue': 'sum',
        'roas': 'mean',
        'ctr': 'mean',
        'cpc': 'mean'
    }).reset_index()
    
    # Top performing campaigns
    top_campaigns = campaign_performance.nlargest(10, 'roas')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top 10 Campaigns by ROAS")
        
        fig_top_campaigns = px.bar(
            top_campaigns,
            x='roas',
            y='campaign',
            orientation='h',
            color='platform',
            title="Top Performing Campaigns",
            color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
        )
        fig_top_campaigns.update_layout(
            xaxis_title="ROAS",
            yaxis_title="Campaign",
            height=600
        )
        st.plotly_chart(fig_top_campaigns, use_container_width=True)
    
    with col2:
        # Campaign performance scatter plot
        fig_scatter = px.scatter(
            campaign_performance,
            x='spend',
            y='attributed revenue',
            size='clicks',
            color='platform',
            hover_data=['campaign', 'roas', 'ctr'],
            title="Campaign Performance: Spend vs Revenue",
            color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
        )
        fig_scatter.update_layout(
            xaxis_title="Total Spend ($)",
            yaxis_title="Attributed Revenue ($)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Tactic performance by platform
    st.subheader("🔄 Tactic Performance by Platform")
    
    tactic_platform = marketing_df.groupby(['platform', 'tactic']).agg({
        'spend': 'sum',
        'attributed revenue': 'sum',
        'roas': 'mean'
    }).reset_index()
    
    fig_heatmap = px.density_heatmap(
        tactic_platform,
        x='platform',
        y='tactic',
        z='roas',
        title="ROAS Heatmap: Platform vs Tactic",
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Insights section
    st.markdown("""
    <div class="insight-box">
        <h4>🎯 Campaign Optimization Insights</h4>
        <ul>
            <li><strong>Top Tactics:</strong> Focus budget on highest-performing tactics</li>
            <li><strong>Platform-Tactic Synergy:</strong> Identify best platform-tactic combinations</li>
            <li><strong>Underperformers:</strong> Campaigns/tactics requiring optimization or budget reallocation</li>
            <li><strong>Scaling Opportunities:</strong> High-ROAS campaigns with room for budget increase</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def create_business_impact_page(combined_df, business_df):
    """Create business impact analysis page"""
    st.markdown('<h1 class="main-header">💼 Business Impact Analysis</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Business metrics overview
    st.subheader("📊 Business Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_aov = combined_df['avg_order_value'].mean()
        st.metric(
            label="Average Order Value",
            value=f"${avg_aov:.2f}",
            help="Average value per order"
        )
    
    with col2:
        total_orders = combined_df['# of orders'].sum()
        st.metric(
            label="Total Orders",
            value=f"{total_orders:,}",
            help="Total number of orders in the period"
        )
    
    with col3:
        total_customers = combined_df['new customers'].sum()
        st.metric(
            label="New Customers Acquired",
            value=f"{total_customers:,}",
            help="Total new customers acquired"
        )
    
    with col4:
        avg_margin = combined_df['gross_margin'].mean()
        st.metric(
            label="Average Gross Margin",
            value=f"{avg_margin:.1f}%",
            help="Average gross profit margin"
        )
    
    # Business trends analysis
    st.subheader("📈 Business Performance Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Orders and customers trend
        fig_orders = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Daily Orders", "New Customers Acquired"),
            vertical_spacing=0.1
        )
        
        fig_orders.add_trace(
            go.Scatter(x=combined_df['date'], y=combined_df['# of orders'], 
                      mode='lines', name='Total Orders', line=dict(color='blue')),
            row=1, col=1
        )
        
        fig_orders.add_trace(
            go.Scatter(x=combined_df['date'], y=combined_df['new customers'], 
                      mode='lines', name='New Customers', line=dict(color='green')),
            row=2, col=1
        )
        
        fig_orders.update_layout(
            title="Orders and Customer Acquisition Trends",
            height=600,
            showlegend=True
        )
        st.plotly_chart(fig_orders, use_container_width=True)
    
    with col2:
        # Revenue and profitability
        fig_profit = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Revenue Trends", "Profitability Metrics"),
            vertical_spacing=0.1
        )
        
        fig_profit.add_trace(
            go.Scatter(x=combined_df['date'], y=combined_df['total revenue'], 
                      mode='lines', name='Total Revenue', line=dict(color='purple')),
            row=1, col=1
        )
        
        fig_profit.add_trace(
            go.Scatter(x=combined_df['date'], y=combined_df['gross profit'], 
                      mode='lines', name='Gross Profit', line=dict(color='orange')),
            row=1, col=1
        )
        
        fig_profit.add_trace(
            go.Scatter(x=combined_df['date'], y=combined_df['gross_margin'], 
                      mode='lines', name='Gross Margin %', line=dict(color='red')),
            row=2, col=1
        )
        
        fig_profit.update_layout(
            title="Revenue and Profitability Analysis",
            height=600,
            showlegend=True
        )
        st.plotly_chart(fig_profit, use_container_width=True)
    
    # Marketing impact on business metrics
    st.subheader("🎯 Marketing Impact on Business Outcomes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Marketing spend vs new customers
        fig_marketing_customers = px.scatter(
            combined_df,
            x='spend',
            y='new customers',
            size='attributed revenue',
            color='customer_acquisition_cost',
            title="Marketing Spend vs New Customer Acquisition",
            color_continuous_scale='RdYlGn_r',
            hover_data=['date', 'roas']
        )
        fig_marketing_customers.update_layout(
            xaxis_title="Daily Marketing Spend ($)",
            yaxis_title="New Customers Acquired"
        )
        st.plotly_chart(fig_marketing_customers, use_container_width=True)
    
    with col2:
        # Marketing efficiency vs business performance
        fig_efficiency = px.scatter(
            combined_df,
            x='marketing_efficiency',
            y='gross_margin',
            size='total revenue',
            color='avg_order_value',
            title="Marketing Efficiency vs Business Profitability",
            color_continuous_scale='Viridis',
            hover_data=['date', '# of orders']
        )
        fig_efficiency.update_layout(
            xaxis_title="Marketing Efficiency (Revenue/Spend)",
            yaxis_title="Gross Margin (%)"
        )
        st.plotly_chart(fig_efficiency, use_container_width=True)
    
    # Weekly performance analysis
    st.subheader("📅 Weekly Performance Analysis")
    
    # Add week columns
    combined_df['week'] = combined_df['date'].dt.isocalendar().week
    combined_df['weekday'] = combined_df['date'].dt.day_name()
    
    weekly_performance = combined_df.groupby('week').agg({
        'total revenue': 'sum',
        'attributed revenue': 'sum',
        'spend': 'sum',
        '# of orders': 'sum',
        'new customers': 'sum',
        'roas': 'mean',
        'gross_margin': 'mean'
    }).reset_index()
    
    fig_weekly = px.line(
        weekly_performance,
        x='week',
        y=['total revenue', 'attributed revenue'],
        title="Weekly Revenue Performance",
        labels={'value': 'Revenue ($)', 'variable': 'Revenue Type'}
    )
    st.plotly_chart(fig_weekly, use_container_width=True)
    
    # Day of week analysis
    weekday_performance = combined_df.groupby('weekday').agg({
        'total revenue': 'mean',
        '# of orders': 'mean',
        'spend': 'mean',
        'roas': 'mean'
    }).reset_index()
    
    # Reorder weekdays
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_performance['weekday'] = pd.Categorical(weekday_performance['weekday'], categories=weekday_order, ordered=True)
    weekday_performance = weekday_performance.sort_values('weekday')
    
    fig_weekday = px.bar(
        weekday_performance,
        x='weekday',
        y='total revenue',
        title="Average Daily Revenue by Day of Week",
        color='roas',
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig_weekday, use_container_width=True)
    
    # Business insights
    st.markdown("""
    <div class="insight-box">
        <h4>💡 Business Impact Insights</h4>
        <ul>
            <li><strong>Customer Acquisition:</strong> Track the relationship between marketing spend and new customer acquisition</li>
            <li><strong>Revenue Attribution:</strong> Understand how much of total business revenue is driven by marketing</li>
            <li><strong>Profitability Impact:</strong> Analyze how marketing efficiency affects overall business margins</li>
            <li><strong>Seasonal Patterns:</strong> Identify weekly and daily patterns in business performance</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def create_recommendations_page(insights, combined_df, platform_summary, tactic_summary):
    """Create strategic recommendations page"""
    st.markdown('<h1 class="main-header">🎯 Strategic Recommendations</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Performance summary
    st.subheader("📊 Performance Summary")
    
    # Calculate key metrics for recommendations
    best_platform = platform_summary.loc[platform_summary['roas'].idxmax(), 'platform']
    worst_platform = platform_summary.loc[platform_summary['roas'].idxmin(), 'platform']
    best_tactic = tactic_summary.loc[tactic_summary['roas'].idxmax(), 'tactic']
    worst_tactic = tactic_summary.loc[tactic_summary['roas'].idxmin(), 'tactic']
    
    avg_cac = combined_df['customer_acquisition_cost'].mean()
    avg_aov = combined_df['avg_order_value'].mean()
    avg_roas = combined_df['roas'].mean()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        **🏆 Top Performers**
        - Best Platform: {best_platform}
        - Best Tactic: {best_tactic}
        - Average ROAS: {avg_roas:.2f}x
        """)
    
    with col2:
        st.markdown(f"""
        **📈 Growth Opportunities**
        - Focus Platform: {best_platform}
        - Scale Tactic: {best_tactic}
        - Target ROAS: >{avg_roas:.2f}x
        """)
    
    with col3:
        st.markdown(f"""
        **⚠️ Areas for Improvement**
        - Review Platform: {worst_platform}
        - Optimize Tactic: {worst_tactic}
        - Current CAC: ${avg_cac:.2f}
        """)
    
    # Strategic recommendations
    st.subheader("🎯 Strategic Recommendations")
    
    recommendations = [
        {
            "title": "🚀 Budget Reallocation Strategy",
            "priority": "High",
            "description": f"Increase budget allocation to {best_platform} platform (highest ROAS performer)",
            "actions": [
                f"Shift 20-30% of budget from {worst_platform} to {best_platform}",
                f"Scale up {best_tactic} campaigns on {best_platform}",
                "Monitor performance closely during transition"
            ],
            "expected_impact": "15-25% improvement in overall ROAS"
        },
        {
            "title": "🎯 Campaign Optimization",
            "priority": "High",
            "description": f"Optimize underperforming {worst_tactic} campaigns",
            "actions": [
                "Conduct creative refresh for low-performing ad sets",
                "A/B test new targeting audiences",
                "Implement bid strategy optimization"
            ],
            "expected_impact": "10-20% improvement in campaign efficiency"
        },
        {
            "title": "📊 Attribution Enhancement",
            "priority": "Medium",
            "description": f"Improve marketing attribution (currently {insights['overview']['marketing_attribution_rate']:.1f}% of total revenue)",
            "actions": [
                "Implement advanced attribution modeling",
                "Set up proper UTM tracking for all campaigns",
                "Consider marketing mix modeling for cross-channel attribution"
            ],
            "expected_impact": "Better insights and 5-10% ROAS improvement"
        },
        {
            "title": "💰 Customer Acquisition Cost Optimization",
            "priority": "Medium",
            "description": f"Reduce customer acquisition cost (current average: ${avg_cac:.2f})",
            "actions": [
                "Focus on high-converting audience segments",
                "Optimize landing pages for better conversion rates",
                "Implement retargeting campaigns for warm audiences"
            ],
            "expected_impact": "10-15% reduction in CAC"
        },
        {
            "title": "📈 Scaling Strategy",
            "priority": "Medium",
            "description": "Scale high-performing campaigns while maintaining efficiency",
            "actions": [
                "Gradually increase budgets for top-performing campaigns",
                "Expand successful campaigns to new markets/audiences",
                "Implement automated bid management"
            ],
            "expected_impact": "20-30% increase in attributed revenue"
        }
    ]
    
    # Display recommendations
    for i, rec in enumerate(recommendations):
        priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
        
        with st.expander(f"{priority_color[rec['priority']]} {rec['title']} - {rec['priority']} Priority"):
            st.markdown(f"**Description:** {rec['description']}")
            
            st.markdown("**Action Items:**")
            for action in rec['actions']:
                st.markdown(f"- {action}")
            
            st.markdown(f"**Expected Impact:** {rec['expected_impact']}")
    
    # Performance tracking KPIs
    st.subheader("📊 Key Performance Indicators to Monitor")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎯 Marketing Efficiency KPIs**
        - Overall ROAS (Target: >3.0x)
        - Cost Per Acquisition (Target: <$50)
        - Click-Through Rate by Platform
        - Conversion Rate by Campaign
        - Marketing Attribution Rate (Target: >60%)
        """)
    
    with col2:
        st.markdown("""
        **💼 Business Impact KPIs**
        - Customer Lifetime Value
        - Average Order Value
        - New Customer Acquisition Rate
        - Revenue Growth Rate
        - Gross Margin Percentage
        """)
    
    # Implementation timeline
    st.subheader("📅 Implementation Timeline")
    
    timeline_data = {
        "Week": ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5-8"],
        "Action": [
            "Budget reallocation analysis",
            "Implement budget shifts (25%)",
            "Campaign optimization launch",
            "Attribution tracking setup",
            "Monitor and scale successful changes"
        ],
        "Owner": [
            "Marketing Manager",
            "Campaign Manager",
            "Creative Team",
            "Analytics Team",
            "Full Marketing Team"
        ]
    }
    
    timeline_df = pd.DataFrame(timeline_data)
    st.table(timeline_df)
    
    # ROI projection
    st.subheader("💰 Projected ROI Impact")
    
    current_spend = insights['overview']['total_spend']
    current_revenue = insights['overview']['total_attributed_revenue']
    current_roas = insights['overview']['overall_roas']
    
    # Conservative estimates
    projected_roas_improvement = 0.15  # 15% improvement
    new_roas = current_roas * (1 + projected_roas_improvement)
    projected_additional_revenue = current_spend * new_roas - current_revenue
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Current ROAS",
            value=f"{current_roas:.2f}x",
            help="Current return on ad spend"
        )
    
    with col2:
        st.metric(
            label="Projected ROAS",
            value=f"{new_roas:.2f}x",
            delta=f"+{projected_roas_improvement*100:.0f}%",
            help="Projected ROAS after implementing recommendations"
        )
    
    with col3:
        st.metric(
            label="Additional Revenue",
            value=f"${projected_additional_revenue:,.0f}",
            help="Projected additional revenue from improvements"
        )
    
    # Final insights
    st.markdown("""
    <div class="insight-box">
        <h4>🎯 Executive Summary</h4>
        <p>Based on the comprehensive analysis of 120 days of marketing and business data, the key opportunities for optimization focus on:</p>
        <ul>
            <li><strong>Platform Optimization:</strong> Reallocate budget to higher-performing platforms</li>
            <li><strong>Campaign Efficiency:</strong> Focus on tactics and campaigns with proven ROAS</li>
            <li><strong>Attribution Enhancement:</strong> Improve tracking for better decision-making</li>
            <li><strong>Customer Acquisition:</strong> Optimize for lower CAC while maintaining quality</li>
        </ul>
        <p><strong>Implementation of these recommendations could result in a 15-25% improvement in overall marketing ROI.</strong></p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main dashboard application"""
    # Load data
    marketing_df, business_df, combined_df, platform_summary, tactic_summary, insights = load_data()
    
    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
    st.sidebar.markdown("---")
    
    pages = {
        "🏠 Executive Overview": "overview",
        "🚀 Platform Analysis": "platforms",
        "🎯 Campaign Analysis": "campaigns",
        "💼 Business Impact": "business",
        "📋 Recommendations": "recommendations"
    }
    
    selected_page = st.sidebar.selectbox("Select Page", list(pages.keys()))
    
    # Data filters
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Data Filters")
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=[combined_df['date'].min().date(), combined_df['date'].max().date()],
        min_value=combined_df['date'].min().date(),
        max_value=combined_df['date'].max().date()
    )
    
    # Apply date filter if range is selected
    if len(date_range) == 2:
        start_date, end_date = date_range
        combined_df = combined_df[
            (combined_df['date'].dt.date >= start_date) & 
            (combined_df['date'].dt.date <= end_date)
        ]
        marketing_df = marketing_df[
            (marketing_df['date'].dt.date >= start_date) & 
            (marketing_df['date'].dt.date <= end_date)
        ]
        business_df = business_df[
            (business_df['date'].dt.date >= start_date) & 
            (business_df['date'].dt.date <= end_date)
        ]
    
    # Platform filter
    selected_platforms = st.sidebar.multiselect(
        "Select Platforms",
        options=marketing_df['platform'].unique(),
        default=marketing_df['platform'].unique()
    )
    
    if selected_platforms:
        marketing_df = marketing_df[marketing_df['platform'].isin(selected_platforms)]
        # Recalculate platform summary for filtered data
        platform_summary = marketing_df.groupby('platform').agg({
            'impression': 'sum',
            'clicks': 'sum',
            'spend': 'sum',
            'attributed revenue': 'sum',
            'ctr': 'mean',
            'cpc': 'mean',
            'roas': 'mean'
        }).reset_index()
    
    # Display selected page
    page_key = pages[selected_page]
    
    if page_key == "overview":
        create_overview_page(marketing_df, business_df, combined_df, insights)
    elif page_key == "platforms":
        create_platform_analysis_page(marketing_df, platform_summary, insights)
    elif page_key == "campaigns":
        create_campaign_analysis_page(marketing_df, tactic_summary)
    elif page_key == "business":
        create_business_impact_page(combined_df, business_df)
    elif page_key == "recommendations":
        create_recommendations_page(insights, combined_df, platform_summary, tactic_summary)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 1rem; color: #666;'>
        <p>📊 Marketing Intelligence Dashboard</p>
        <p>Built with Streamlit & Plotly</p>
        <p>Data Period: May 16 - Sep 12, 2025</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()