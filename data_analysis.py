import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def load_and_explore_data():
    """Load all datasets and perform initial exploration"""
    print("Loading datasets...")
    
    # Load marketing datasets
    facebook_df = pd.read_csv('Facebook.csv')
    google_df = pd.read_csv('Google.csv')
    tiktok_df = pd.read_csv('TikTok.csv')
    business_df = pd.read_csv('business.csv')
    
    print("\n=== DATASET OVERVIEW ===")
    print(f"Facebook data: {facebook_df.shape}")
    print(f"Google data: {google_df.shape}")
    print(f"TikTok data: {tiktok_df.shape}")
    print(f"Business data: {business_df.shape}")
    
    # Check data types and missing values
    print("\n=== DATA QUALITY CHECK ===")
    
    for name, df in [("Facebook", facebook_df), ("Google", google_df), ("TikTok", tiktok_df), ("Business", business_df)]:
        print(f"\n{name} Dataset:")
        print(f"Columns: {list(df.columns)}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"Missing values: {df.isnull().sum().sum()}")
        
        if name != "Business":
            print(f"Unique campaigns: {df['campaign'].nunique()}")
            print(f"Unique tactics: {df['tactic'].nunique()}")
            print(f"Unique states: {df['state'].nunique()}")
    
    return facebook_df, google_df, tiktok_df, business_df

def clean_and_prepare_data(facebook_df, google_df, tiktok_df, business_df):
    """Clean and standardize the datasets"""
    print("\n=== DATA CLEANING AND PREPARATION ===")
    
    # Convert date columns to datetime
    for df in [facebook_df, google_df, tiktok_df, business_df]:
        df['date'] = pd.to_datetime(df['date'])
    
    # Add platform identifier to marketing datasets
    facebook_df['platform'] = 'Facebook'
    google_df['platform'] = 'Google'
    tiktok_df['platform'] = 'TikTok'
    
    # Combine all marketing data
    marketing_df = pd.concat([facebook_df, google_df, tiktok_df], ignore_index=True)
    
    print(f"Combined marketing data shape: {marketing_df.shape}")
    print(f"Date range: {marketing_df['date'].min()} to {marketing_df['date'].max()}")
    print(f"Platforms: {marketing_df['platform'].unique()}")
    print(f"Tactics: {marketing_df['tactic'].unique()}")
    print(f"States: {marketing_df['state'].unique()}")
    
    return marketing_df, business_df

def calculate_marketing_metrics(marketing_df):
    """Calculate key marketing performance metrics"""
    print("\n=== CALCULATING MARKETING METRICS ===")
    
    # Calculate basic metrics
    marketing_df['ctr'] = (marketing_df['clicks'] / marketing_df['impression']) * 100
    marketing_df['cpc'] = marketing_df['spend'] / marketing_df['clicks']
    marketing_df['cpm'] = (marketing_df['spend'] / marketing_df['impression']) * 1000
    marketing_df['roas'] = marketing_df['attributed revenue'] / marketing_df['spend']
    marketing_df['conversion_rate'] = (marketing_df['attributed revenue'] / marketing_df['clicks']) * 100
    
    # Handle division by zero
    marketing_df['ctr'] = marketing_df['ctr'].replace([np.inf, -np.inf], 0).fillna(0)
    marketing_df['cpc'] = marketing_df['cpc'].replace([np.inf, -np.inf], 0).fillna(0)
    marketing_df['cpm'] = marketing_df['cpm'].replace([np.inf, -np.inf], 0).fillna(0)
    marketing_df['roas'] = marketing_df['roas'].replace([np.inf, -np.inf], 0).fillna(0)
    marketing_df['conversion_rate'] = marketing_df['conversion_rate'].replace([np.inf, -np.inf], 0).fillna(0)
    
    print("Calculated metrics: CTR, CPC, CPM, ROAS, Conversion Rate")
    
    return marketing_df

def aggregate_data(marketing_df, business_df):
    """Create aggregated views for analysis"""
    print("\n=== CREATING AGGREGATED VIEWS ===")
    
    # Daily aggregated marketing data
    daily_marketing = marketing_df.groupby('date').agg({
        'impression': 'sum',
        'clicks': 'sum',
        'spend': 'sum',
        'attributed revenue': 'sum'
    }).reset_index()
    
    # Calculate aggregated metrics
    daily_marketing['ctr'] = (daily_marketing['clicks'] / daily_marketing['impression']) * 100
    daily_marketing['cpc'] = daily_marketing['spend'] / daily_marketing['clicks']
    daily_marketing['roas'] = daily_marketing['attributed revenue'] / daily_marketing['spend']
    
    # Platform-level aggregation
    platform_summary = marketing_df.groupby('platform').agg({
        'impression': 'sum',
        'clicks': 'sum',
        'spend': 'sum',
        'attributed revenue': 'sum',
        'ctr': 'mean',
        'cpc': 'mean',
        'roas': 'mean'
    }).reset_index()
    
    # Tactic-level aggregation
    tactic_summary = marketing_df.groupby('tactic').agg({
        'impression': 'sum',
        'clicks': 'sum',
        'spend': 'sum',
        'attributed revenue': 'sum',
        'ctr': 'mean',
        'cpc': 'mean',
        'roas': 'mean'
    }).reset_index()
    
    print("Created aggregations: Daily, Platform, and Tactic level")
    
    return daily_marketing, platform_summary, tactic_summary

def merge_marketing_business_data(daily_marketing, business_df):
    """Merge marketing and business data for comprehensive analysis"""
    print("\n=== MERGING MARKETING AND BUSINESS DATA ===")
    
    # Merge on date
    combined_df = pd.merge(daily_marketing, business_df, on='date', how='inner')
    
    print(f"Combined dataset shape: {combined_df.shape}")
    print(f"Date range: {combined_df['date'].min()} to {combined_df['date'].max()}")
    
    # Calculate additional business metrics
    combined_df['avg_order_value'] = combined_df['total revenue'] / combined_df['# of orders']
    combined_df['new_customer_ratio'] = combined_df['new customers'] / combined_df['# of orders']
    combined_df['gross_margin'] = (combined_df['gross profit'] / combined_df['total revenue']) * 100
    combined_df['marketing_efficiency'] = combined_df['attributed revenue'] / combined_df['spend']
    combined_df['customer_acquisition_cost'] = combined_df['spend'] / combined_df['new customers']
    
    # Handle division by zero
    for col in ['avg_order_value', 'new_customer_ratio', 'gross_margin', 'marketing_efficiency', 'customer_acquisition_cost']:
        combined_df[col] = combined_df[col].replace([np.inf, -np.inf], 0).fillna(0)
    
    print("Calculated additional metrics: AOV, New Customer Ratio, Gross Margin, Marketing Efficiency, CAC")
    
    return combined_df

def generate_insights(marketing_df, business_df, combined_df, platform_summary, tactic_summary):
    """Generate key insights for the dashboard"""
    print("\n=== GENERATING KEY INSIGHTS ===")
    
    insights = {}
    
    # Overall performance metrics
    total_spend = marketing_df['spend'].sum()
    total_revenue = marketing_df['attributed revenue'].sum()
    total_business_revenue = business_df['total revenue'].sum()
    overall_roas = total_revenue / total_spend if total_spend > 0 else 0
    
    insights['overview'] = {
        'total_spend': total_spend,
        'total_attributed_revenue': total_revenue,
        'total_business_revenue': total_business_revenue,
        'overall_roas': overall_roas,
        'marketing_attribution_rate': (total_revenue / total_business_revenue) * 100 if total_business_revenue > 0 else 0
    }
    
    # Platform performance
    insights['platforms'] = platform_summary.to_dict('records')
    
    # Tactic performance
    insights['tactics'] = tactic_summary.to_dict('records')
    
    # Best and worst performing days
    best_roas_day = combined_df.loc[combined_df['roas'].idxmax()]
    worst_roas_day = combined_df.loc[combined_df['roas'].idxmin()]
    
    insights['performance_days'] = {
        'best_roas': {
            'date': best_roas_day['date'],
            'roas': best_roas_day['roas'],
            'spend': best_roas_day['spend'],
            'revenue': best_roas_day['attributed revenue']
        },
        'worst_roas': {
            'date': worst_roas_day['date'],
            'roas': worst_roas_day['roas'],
            'spend': worst_roas_day['spend'],
            'revenue': worst_roas_day['attributed revenue']
        }
    }
    
    # Trends analysis
    combined_df['week'] = combined_df['date'].dt.isocalendar().week
    weekly_trends = combined_df.groupby('week').agg({
        'spend': 'mean',
        'attributed revenue': 'mean',
        'roas': 'mean',
        'total revenue': 'mean'
    }).reset_index()
    
    insights['weekly_trends'] = weekly_trends.to_dict('records')
    
    print("Generated insights for overview, platforms, tactics, performance days, and trends")
    
    return insights

def save_processed_data(marketing_df, business_df, combined_df, platform_summary, tactic_summary, insights):
    """Save processed data for dashboard use"""
    print("\n=== SAVING PROCESSED DATA ===")
    
    marketing_df.to_csv('processed_marketing_data.csv', index=False)
    business_df.to_csv('processed_business_data.csv', index=False)
    combined_df.to_csv('combined_daily_data.csv', index=False)
    platform_summary.to_csv('platform_summary.csv', index=False)
    tactic_summary.to_csv('tactic_summary.csv', index=False)
    
    # Save insights as JSON for easy loading in dashboard
    import json
    with open('insights.json', 'w') as f:
        json.dump(insights, f, default=str, indent=2)
    
    print("Saved processed datasets and insights")

def main():
    """Main execution function"""
    print("=== MARKETING INTELLIGENCE DASHBOARD - DATA PREPARATION ===")
    
    # Load and explore data
    facebook_df, google_df, tiktok_df, business_df = load_and_explore_data()
    
    # Clean and prepare data
    marketing_df, business_df = clean_and_prepare_data(facebook_df, google_df, tiktok_df, business_df)
    
    # Calculate marketing metrics
    marketing_df = calculate_marketing_metrics(marketing_df)
    
    # Create aggregated views
    daily_marketing, platform_summary, tactic_summary = aggregate_data(marketing_df, business_df)
    
    # Merge marketing and business data
    combined_df = merge_marketing_business_data(daily_marketing, business_df)
    
    # Generate insights
    insights = generate_insights(marketing_df, business_df, combined_df, platform_summary, tactic_summary)
    
    # Save processed data
    save_processed_data(marketing_df, business_df, combined_df, platform_summary, tactic_summary, insights)
    
    print("\n=== DATA PREPARATION COMPLETE ===")
    print("Ready to build the dashboard!")

if __name__ == "__main__":
    main()