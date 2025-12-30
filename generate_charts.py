#!/usr/bin/env python3
"""
Unvan.az Business Analytics - Chart Generation
Generates business-focused visualizations for marketplace data analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for professional charts
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Configure matplotlib for better visualization
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

def load_data():
    """Load and combine all datasets"""
    print("Loading data...")
    df1 = pd.read_csv('listings.csv')
    df2 = pd.read_csv('18_08_2023.csv')
    df = pd.concat([df1, df2], ignore_index=True)

    # Data cleaning
    df['price_clean'] = pd.to_numeric(df['price'], errors='coerce')
    df['date_clean'] = pd.to_datetime(df['date'], format='%d.%m.%Y', errors='coerce')

    print(f"Loaded {len(df)} listings")
    return df

def chart_1_market_composition(df):
    """Market Composition: Top 15 Categories by Volume"""
    print("Generating Chart 1: Market Composition...")

    top_categories = df['category'].value_counts().head(15)

    fig, ax = plt.subplots(figsize=(14, 8))
    bars = ax.barh(range(len(top_categories)), top_categories.values, color='#2E86AB')
    ax.set_yticks(range(len(top_categories)))
    ax.set_yticklabels(top_categories.index)
    ax.set_xlabel('Number of Listings', fontweight='bold', fontsize=12)
    ax.set_title('Market Composition: Top 15 Categories by Listing Volume',
                 fontweight='bold', fontsize=14, pad=20)
    ax.invert_yaxis()

    # Add value labels
    for i, (idx, val) in enumerate(top_categories.items()):
        ax.text(val + 50, i, f'{val:,}', va='center', fontweight='bold')

    # Add percentage of total
    total = len(df)
    for i, (idx, val) in enumerate(top_categories.items()):
        pct = (val / total) * 100
        ax.text(val / 2, i, f'{pct:.1f}%', va='center', ha='center',
                color='white', fontweight='bold', fontsize=9)

    plt.tight_layout()
    plt.savefig('charts/01_market_composition.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: charts/01_market_composition.png")

def chart_2_pricing_by_category(df):
    """Average Pricing by Top Categories"""
    print("Generating Chart 2: Pricing Analysis...")

    # Get top 12 categories
    top_cats = df['category'].value_counts().head(12).index
    df_top = df[df['category'].isin(top_cats)].copy()

    # Calculate average prices
    avg_prices = df_top.groupby('category')['price_clean'].mean().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(14, 8))
    bars = ax.barh(range(len(avg_prices)), avg_prices.values, color='#A23B72')
    ax.set_yticks(range(len(avg_prices)))
    ax.set_yticklabels(avg_prices.index)
    ax.set_xlabel('Average Price (AZN)', fontweight='bold', fontsize=12)
    ax.set_title('Average Listing Prices by Top Categories',
                 fontweight='bold', fontsize=14, pad=20)
    ax.invert_yaxis()

    # Add value labels
    for i, (idx, val) in enumerate(avg_prices.items()):
        ax.text(val + 5, i, f'{val:.0f} AZN', va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig('charts/02_pricing_by_category.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: charts/02_pricing_by_category.png")

def chart_3_temporal_trends(df):
    """Listing Volume Trends Over Time"""
    print("Generating Chart 3: Temporal Trends...")

    df_dated = df[df['date_clean'].notna()].copy()
    df_dated['year_month'] = df_dated['date_clean'].dt.to_period('M')

    monthly_counts = df_dated.groupby('year_month').size()

    fig, ax = plt.subplots(figsize=(14, 6))
    x_values = range(len(monthly_counts))
    ax.plot(x_values, monthly_counts.values, marker='o', linewidth=3,
            markersize=8, color='#F18F01')
    ax.fill_between(x_values, monthly_counts.values, alpha=0.3, color='#F18F01')

    ax.set_xticks(x_values)
    ax.set_xticklabels([str(period) for period in monthly_counts.index], rotation=45)
    ax.set_ylabel('Number of Listings', fontweight='bold', fontsize=12)
    ax.set_xlabel('Month', fontweight='bold', fontsize=12)
    ax.set_title('Marketplace Activity: Monthly Listing Volume Trends',
                 fontweight='bold', fontsize=14, pad=20)
    ax.grid(True, alpha=0.3)

    # Add value labels
    for i, val in enumerate(monthly_counts.values):
        ax.text(i, val + 200, f'{val:,}', ha='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig('charts/03_temporal_trends.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: charts/03_temporal_trends.png")

def chart_4_market_concentration(df):
    """Market Concentration Analysis"""
    print("Generating Chart 4: Market Concentration...")

    category_counts = df['category'].value_counts()
    total = len(df)

    # Calculate cumulative percentage
    cumsum = category_counts.cumsum()
    cumsum_pct = (cumsum / total) * 100

    fig, ax = plt.subplots(figsize=(14, 6))
    x_values = range(len(cumsum_pct))
    ax.plot(x_values, cumsum_pct.values, linewidth=3, color='#C73E1D')
    ax.fill_between(x_values, cumsum_pct.values, alpha=0.3, color='#C73E1D')

    # Add horizontal reference lines
    ax.axhline(y=50, color='gray', linestyle='--', linewidth=2, alpha=0.7)
    ax.axhline(y=80, color='gray', linestyle='--', linewidth=2, alpha=0.7)

    ax.set_ylabel('Cumulative Market Share (%)', fontweight='bold', fontsize=12)
    ax.set_xlabel('Number of Categories (ranked by volume)', fontweight='bold', fontsize=12)
    ax.set_title('Market Concentration: Cumulative Category Distribution',
                 fontweight='bold', fontsize=14, pad=20)
    ax.grid(True, alpha=0.3)

    # Find key thresholds
    cats_for_50 = (cumsum_pct >= 50).argmax()
    cats_for_80 = (cumsum_pct >= 80).argmax()

    ax.text(cats_for_50, 50, f'  {cats_for_50} categories = 50%',
            va='center', fontweight='bold', fontsize=10)
    ax.text(cats_for_80, 80, f'  {cats_for_80} categories = 80%',
            va='center', fontweight='bold', fontsize=10)

    plt.tight_layout()
    plt.savefig('charts/04_market_concentration.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: charts/04_market_concentration.png")

def chart_5_price_segmentation(df):
    """Price Segmentation Analysis"""
    print("Generating Chart 5: Price Segmentation...")

    df_priced = df[df['price_clean'].notna()].copy()

    # Define price segments
    bins = [0, 50, 100, 200, 500, 1000]
    labels = ['Budget\n(1-50 AZN)', 'Economy\n(51-100 AZN)',
              'Mid-Range\n(101-200 AZN)', 'Premium\n(201-500 AZN)',
              'Luxury\n(500+ AZN)']

    df_priced['price_segment'] = pd.cut(df_priced['price_clean'], bins=bins, labels=labels)
    segment_counts = df_priced['price_segment'].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(14, 7))
    bars = ax.bar(range(len(segment_counts)), segment_counts.values, color='#06A77D')
    ax.set_xticks(range(len(segment_counts)))
    ax.set_xticklabels(segment_counts.index, fontweight='bold')
    ax.set_ylabel('Number of Listings', fontweight='bold', fontsize=12)
    ax.set_title('Price Segmentation: Distribution Across Price Tiers',
                 fontweight='bold', fontsize=14, pad=20)

    # Add value labels and percentages
    total_priced = len(df_priced)
    for i, (idx, val) in enumerate(segment_counts.items()):
        ax.text(i, val + 200, f'{val:,}', ha='center', fontweight='bold')
        pct = (val / total_priced) * 100
        ax.text(i, val / 2, f'{pct:.1f}%', ha='center', va='center',
                color='white', fontweight='bold', fontsize=11)

    plt.tight_layout()
    plt.savefig('charts/05_price_segmentation.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: charts/05_price_segmentation.png")

def chart_6_top_categories_comparison(df):
    """Top Categories: Volume vs Average Price Comparison"""
    print("Generating Chart 6: Category Comparison...")

    top_cats = df['category'].value_counts().head(10).index
    df_top = df[df['category'].isin(top_cats)].copy()

    cat_stats = df_top.groupby('category').agg({
        'id': 'count',
        'price_clean': 'mean'
    }).rename(columns={'id': 'count', 'price_clean': 'avg_price'})

    cat_stats = cat_stats.sort_values('count', ascending=False)

    fig, ax1 = plt.subplots(figsize=(14, 8))

    x = range(len(cat_stats))
    ax1.bar(x, cat_stats['count'].values, color='#2E86AB', alpha=0.7, label='Listing Volume')
    ax1.set_xlabel('Category', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Number of Listings', fontweight='bold', fontsize=12, color='#2E86AB')
    ax1.tick_params(axis='y', labelcolor='#2E86AB')
    ax1.set_xticks(x)
    ax1.set_xticklabels(cat_stats.index, rotation=45, ha='right')

    ax2 = ax1.twinx()
    ax2.plot(x, cat_stats['avg_price'].values, color='#C73E1D', marker='o',
             linewidth=3, markersize=8, label='Average Price')
    ax2.set_ylabel('Average Price (AZN)', fontweight='bold', fontsize=12, color='#C73E1D')
    ax2.tick_params(axis='y', labelcolor='#C73E1D')

    ax1.set_title('Top Categories: Market Volume vs Pricing Strategy',
                  fontweight='bold', fontsize=14, pad=20)

    # Add legends
    ax1.legend(loc='upper left', fontsize=10)
    ax2.legend(loc='upper right', fontsize=10)

    plt.tight_layout()
    plt.savefig('charts/06_category_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: charts/06_category_comparison.png")

def chart_7_weekly_patterns(df):
    """Weekly Posting Patterns"""
    print("Generating Chart 7: Weekly Patterns...")

    df_dated = df[df['date_clean'].notna()].copy()
    df_dated['weekday'] = df_dated['date_clean'].dt.day_name()

    # Define correct order
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_counts = df_dated['weekday'].value_counts().reindex(weekday_order)

    fig, ax = plt.subplots(figsize=(14, 6))
    bars = ax.bar(range(len(weekday_counts)), weekday_counts.values, color='#6A4C93')
    ax.set_xticks(range(len(weekday_counts)))
    ax.set_xticklabels(weekday_counts.index, fontweight='bold')
    ax.set_ylabel('Number of Listings Posted', fontweight='bold', fontsize=12)
    ax.set_title('Weekly Activity Patterns: Listing Posting Trends by Day of Week',
                 fontweight='bold', fontsize=14, pad=20)

    # Add value labels
    for i, val in enumerate(weekday_counts.values):
        ax.text(i, val + 50, f'{val:,}', ha='center', fontweight='bold')

    # Highlight weekend
    ax.axvspan(4.5, 6.5, alpha=0.2, color='gray')
    ax.text(5.5, max(weekday_counts) * 0.95, 'Weekend', ha='center',
            fontweight='bold', fontsize=11, style='italic')

    plt.tight_layout()
    plt.savefig('charts/07_weekly_patterns.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: charts/07_weekly_patterns.png")

def chart_8_seller_activity(df):
    """Seller Activity Distribution"""
    print("Generating Chart 8: Seller Activity...")

    df_named = df[df['name'].notna()].copy()
    seller_counts = df_named['name'].value_counts()

    # Distribution of seller activity
    activity_distribution = seller_counts.value_counts().sort_index()

    # Group for clarity
    bins = [0, 1, 5, 10, 20, 50, 1000]
    labels = ['1 listing', '2-5 listings', '6-10 listings',
              '11-20 listings', '21-50 listings', '50+ listings']

    seller_activity = pd.cut(seller_counts, bins=bins, labels=labels)
    activity_counts = seller_activity.value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(14, 7))
    bars = ax.bar(range(len(activity_counts)), activity_counts.values, color='#E07A5F')
    ax.set_xticks(range(len(activity_counts)))
    ax.set_xticklabels(activity_counts.index, fontweight='bold')
    ax.set_ylabel('Number of Sellers', fontweight='bold', fontsize=12)
    ax.set_title('Seller Activity Distribution: Number of Listings per Seller',
                 fontweight='bold', fontsize=14, pad=20)

    # Add value labels and percentages
    total_sellers = len(seller_counts)
    for i, (idx, val) in enumerate(activity_counts.items()):
        ax.text(i, val + 50, f'{val:,}', ha='center', fontweight='bold')
        pct = (val / total_sellers) * 100
        ax.text(i, val / 2, f'{pct:.1f}%', ha='center', va='center',
                color='white', fontweight='bold', fontsize=10)

    plt.tight_layout()
    plt.savefig('charts/08_seller_activity.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: charts/08_seller_activity.png")

def chart_9_category_growth(df):
    """Category Growth Comparison (if data spans multiple months)"""
    print("Generating Chart 9: Category Growth...")

    df_dated = df[df['date_clean'].notna()].copy()
    df_dated['year_month'] = df_dated['date_clean'].dt.to_period('M')

    # Get top 6 categories
    top_6_cats = df['category'].value_counts().head(6).index
    df_top = df_dated[df_dated['category'].isin(top_6_cats)].copy()

    # Monthly counts by category
    monthly_cat = df_top.groupby(['year_month', 'category']).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(14, 7))

    for category in monthly_cat.columns:
        ax.plot(range(len(monthly_cat)), monthly_cat[category].values,
                marker='o', linewidth=2, markersize=6, label=category)

    ax.set_xticks(range(len(monthly_cat)))
    ax.set_xticklabels([str(period) for period in monthly_cat.index], rotation=45)
    ax.set_ylabel('Number of Listings', fontweight='bold', fontsize=12)
    ax.set_xlabel('Month', fontweight='bold', fontsize=12)
    ax.set_title('Category Growth Trends: Top 6 Categories Over Time',
                 fontweight='bold', fontsize=14, pad=20)
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('charts/09_category_growth.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: charts/09_category_growth.png")

def chart_10_key_metrics_summary(df):
    """Key Business Metrics Summary Dashboard"""
    print("Generating Chart 10: Key Metrics Summary...")

    df_priced = df[df['price_clean'].notna()]

    fig = plt.figure(figsize=(14, 8))
    gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)

    # Metric 1: Total Listings
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.text(0.5, 0.5, f'{len(df):,}', ha='center', va='center',
             fontsize=32, fontweight='bold', color='#2E86AB')
    ax1.text(0.5, 0.2, 'Total Listings', ha='center', va='center',
             fontsize=12, fontweight='bold')
    ax1.axis('off')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)

    # Metric 2: Total Categories
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.text(0.5, 0.5, f'{df["category"].nunique()}', ha='center', va='center',
             fontsize=32, fontweight='bold', color='#A23B72')
    ax2.text(0.5, 0.2, 'Active Categories', ha='center', va='center',
             fontsize=12, fontweight='bold')
    ax2.axis('off')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)

    # Metric 3: Average Price
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.text(0.5, 0.5, f'{df_priced["price_clean"].mean():.0f} AZN',
             ha='center', va='center', fontsize=28, fontweight='bold', color='#F18F01')
    ax3.text(0.5, 0.2, 'Average Price', ha='center', va='center',
             fontsize=12, fontweight='bold')
    ax3.axis('off')
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)

    # Metric 4: Unique Sellers
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.text(0.5, 0.5, f'{df["name"].nunique():,}', ha='center', va='center',
             fontsize=32, fontweight='bold', color='#C73E1D')
    ax4.text(0.5, 0.2, 'Unique Sellers', ha='center', va='center',
             fontsize=12, fontweight='bold')
    ax4.axis('off')
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)

    # Metric 5: Median Price
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.text(0.5, 0.5, f'{df_priced["price_clean"].median():.0f} AZN',
             ha='center', va='center', fontsize=28, fontweight='bold', color='#06A77D')
    ax5.text(0.5, 0.2, 'Median Price', ha='center', va='center',
             fontsize=12, fontweight='bold')
    ax5.axis('off')
    ax5.set_xlim(0, 1)
    ax5.set_ylim(0, 1)

    # Metric 6: Top Category
    ax6 = fig.add_subplot(gs[1, 2])
    top_cat = df['category'].value_counts().index[0]
    top_cat_count = df['category'].value_counts().values[0]
    ax6.text(0.5, 0.6, top_cat, ha='center', va='center',
             fontsize=14, fontweight='bold', color='#6A4C93', wrap=True)
    ax6.text(0.5, 0.4, f'({top_cat_count:,} listings)', ha='center', va='center',
             fontsize=10, color='#666')
    ax6.text(0.5, 0.2, 'Top Category', ha='center', va='center',
             fontsize=12, fontweight='bold')
    ax6.axis('off')
    ax6.set_xlim(0, 1)
    ax6.set_ylim(0, 1)

    # Bottom row: Price distribution histogram
    ax7 = fig.add_subplot(gs[2, :])
    df_priced_filtered = df_priced[df_priced['price_clean'] <= 999]
    ax7.hist(df_priced_filtered['price_clean'], bins=50, color='#2E86AB', alpha=0.7, edgecolor='black')
    ax7.set_xlabel('Price (AZN)', fontweight='bold')
    ax7.set_ylabel('Frequency', fontweight='bold')
    ax7.set_title('Price Distribution Overview', fontweight='bold', fontsize=12)
    ax7.grid(True, alpha=0.3)

    fig.suptitle('Unvan.az Marketplace: Key Business Metrics Overview',
                 fontsize=16, fontweight='bold', y=0.98)

    plt.savefig('charts/10_key_metrics_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: charts/10_key_metrics_summary.png")

def main():
    """Main execution function"""
    print("=" * 60)
    print("UNVAN.AZ BUSINESS ANALYTICS - CHART GENERATION")
    print("=" * 60)
    print()

    # Load data
    df = load_data()
    print()

    # Generate all charts
    chart_1_market_composition(df)
    chart_2_pricing_by_category(df)
    chart_3_temporal_trends(df)
    chart_4_market_concentration(df)
    chart_5_price_segmentation(df)
    chart_6_top_categories_comparison(df)
    chart_7_weekly_patterns(df)
    chart_8_seller_activity(df)
    chart_9_category_growth(df)
    chart_10_key_metrics_summary(df)

    print()
    print("=" * 60)
    print("CHART GENERATION COMPLETE!")
    print("All visualizations saved to: charts/")
    print("=" * 60)

if __name__ == '__main__':
    main()
