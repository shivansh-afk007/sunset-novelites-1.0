from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json
import numpy as np
from datetime import datetime
import warnings
import mysql.connector
import time
import os
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Import the dashboard class and initialize it
from rds_dashboard_fixed import RDSRTRIMDashboard

# Initialize dashboard
dashboard = RDSRTRIMDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard_pro.html')

@app.route('/api/metrics')
def get_metrics():
    """API endpoint for key metrics"""
    try:
        if not dashboard.insights:
            dashboard.generate_insights()
        return jsonify(dashboard.insights)
    except Exception as e:
        print(f"Error in metrics endpoint: {e}")
        return jsonify({
            'total_revenue': 0,
            'total_units_sold': 0,
            'total_products': 0,
            'avg_profit_margin': 0,
            'top_product': "No products",
            'top_product_revenue': 0,
            'negative_margin_products': 0,
            'high_margin_products': 0,
            'total_stock_remaining': 0
        })

@app.route('/api/warehouse/metrics')
def get_warehouse_metrics():
    """API endpoint for warehouse metrics"""
    try:
        return jsonify(dashboard.get_warehouse_metrics())
    except Exception as e:
        print(f"Error in warehouse metrics endpoint: {e}")
        return jsonify({
            'total_products': 0,
            'total_current_stock': 0,
            'products_needing_restock': 0,
            'avg_lead_time': 0.0,
            'critical_stock_products': 0
        })

@app.route('/api/charts/revenue')
def get_revenue_chart():
    """API endpoint for revenue chart"""
    return dashboard.create_revenue_chart()

@app.route('/api/charts/top-products')
def get_top_products_chart():
    """API endpoint for top products chart"""
    return dashboard.create_top_products_chart()

@app.route('/api/charts/margin-distribution')
def get_margin_distribution_chart():
    """API endpoint for margin distribution chart"""
    return dashboard.create_margin_distribution_chart()

@app.route('/api/charts/source-comparison')
def get_source_comparison_chart():
    """API endpoint for source comparison chart"""
    return dashboard.create_source_comparison_chart()

@app.route('/api/charts/warehouse-stock-status')
def get_warehouse_stock_chart():
    """API endpoint for warehouse stock chart"""
    return dashboard.create_warehouse_stock_chart()

@app.route('/api/data/top-products')
def get_top_products_data():
    """API endpoint for top products data"""
    return jsonify(dashboard.get_top_products_data().to_dict('records'))

@app.route('/api/data/negative-margin')
def get_negative_margin_data():
    """API endpoint for negative margin data"""
    return jsonify(dashboard.get_negative_margin_data().to_dict('records'))

@app.route('/api/data/category-summary')
def get_category_summary_data():
    """API endpoint for category summary data"""
    return jsonify(dashboard.get_category_summary().to_dict('index'))

@app.route('/api/charts/revenue-by-category')
def get_revenue_by_category_chart():
    """API endpoint for revenue by category chart"""
    chart_data = dashboard.create_revenue_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/top-products-chart')
def get_top_products_chart_alt():
    """API endpoint for top products chart (alternative)"""
    chart_data = dashboard.create_top_products_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/profit-margin-by-category')
def get_profit_margin_by_category_chart():
    """API endpoint for profit margin by category chart"""
    chart_data = dashboard.create_margin_distribution_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/stock-vs-sales')
def get_stock_vs_sales_chart():
    """API endpoint for stock vs sales chart"""
    chart_data = dashboard.create_source_comparison_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/revenue-vs-margin')
def get_revenue_vs_margin_chart():
    """API endpoint for revenue vs margin chart"""
    chart_data = dashboard.create_source_comparison_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/category-performance')
def get_category_performance_chart():
    """API endpoint for category performance chart"""
    chart_data = dashboard.create_revenue_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/warehouse-location')
def get_warehouse_location_chart():
    """API endpoint for warehouse location chart"""
    chart_data = dashboard.create_warehouse_stock_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/restock-urgency')
def get_restock_urgency_chart():
    """API endpoint for restock urgency chart"""
    chart_data = dashboard.create_warehouse_stock_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/supplier-analysis')
def get_supplier_analysis_chart():
    """API endpoint for supplier analysis chart"""
    chart_data = dashboard.create_source_comparison_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/data/warehouse-summary')
def get_warehouse_summary_data():
    """API endpoint for warehouse summary data"""
    try:
        # Create warehouse summary data structure
        lightspeed_df = pd.DataFrame(dashboard.warehouse_data.get('lightspeed', []))
        acumatica_df = pd.DataFrame(dashboard.warehouse_data.get('acumatica', []))
        
        if not lightspeed_df.empty:
            warehouse_summary = {
                'Lightspeed': {
                    'Current_Stock_sum': int(lightspeed_df['Current_Stock'].sum()),
                    'Current_Stock_mean': float(lightspeed_df['Current_Stock'].mean()),
                    'Reorder_Point_sum': int(lightspeed_df['Reorder_Point'].sum()),
                    'Safety_Stock_sum': int(lightspeed_df['Safety_Stock'].sum()),
                    'Restock_Needed_sum': int(len(lightspeed_df[lightspeed_df['Current_Stock'] <= lightspeed_df['Reorder_Point']]))
                }
            }
        else:
            warehouse_summary = {
                'Lightspeed': {
                    'Current_Stock_sum': 0,
                    'Current_Stock_mean': 0,
                    'Reorder_Point_sum': 0,
                    'Safety_Stock_sum': 0,
                    'Restock_Needed_sum': 0
                }
            }
        
        return jsonify(warehouse_summary)
    except Exception as e:
        print(f"Error getting warehouse summary data: {e}")
        return jsonify({})

@app.route('/api/data/restock-alerts')
def get_restock_alerts_data():
    """API endpoint for restock alerts data with ADVANCED purchase rate logic"""
    try:
        lightspeed_df = pd.DataFrame(dashboard.warehouse_data.get('lightspeed', []))
        
        if not lightspeed_df.empty:
            # Use enhanced warehouse data if available, otherwise calculate
            if 'lightspeed_enhanced' in dashboard.warehouse_data:
                enhanced_df = pd.DataFrame(dashboard.warehouse_data['lightspeed_enhanced'])
                restock_items = enhanced_df[enhanced_df['Needs_Restock']].copy()
            else:
                # Fallback to basic calculation
                purchase_rates = dashboard.calculate_purchase_rates()
                
                # Merge purchase rates with warehouse data
                lightspeed_df_with_rates = lightspeed_df.copy()
                lightspeed_df_with_rates['Purchase_Rate'] = lightspeed_df_with_rates['Product_ID'].map(purchase_rates)
                lightspeed_df_with_rates['Purchase_Rate'] = lightspeed_df_with_rates['Purchase_Rate'].fillna(0)
                
                # Calculate days until stockout
                lightspeed_df_with_rates['Days_Until_Stockout'] = lightspeed_df_with_rates.apply(
                    lambda row: dashboard.calculate_days_until_stockout(row['Current_Stock'], row['Purchase_Rate']), axis=1
                )
                
                # Filter items that need restocking (stock will last less than 30 days)
                restock_items = lightspeed_df_with_rates[lightspeed_df_with_rates['Days_Until_Stockout'] <= 30].copy()
            
            print(f"🔍 ADVANCED Restock Analysis:")
            print(f"   - Total warehouse items: {len(lightspeed_df)}")
            print(f"   - Items needing restock (30-day rule): {len(restock_items)}")
            print(f"   - Items with stock > 0: {len(lightspeed_df[lightspeed_df['Current_Stock'] > 0])}")
            
            if not restock_items.empty:
                # Add urgency level based on days until stockout
                restock_items['Urgency_Level'] = restock_items['Days_Until_Stockout'].apply(
                    lambda days: 'Critical' if days <= 7 else 'High' if days <= 14 else 'Medium' if days <= 30 else 'Low'
                )
                
                # Add category based on product name
                restock_items['Category'] = restock_items['Product_Name'].apply(
                    lambda name: dashboard.categorize_products([name])[0] if pd.notna(name) else 'Other'
                )
                
                # Add restock recommendation
                restock_items['Restock_Recommendation'] = restock_items.apply(
                    lambda row: f"Order {max(10, int(row['Purchase_Rate'] * 30))} units" if row['Purchase_Rate'] > 0 else "Review demand",
                    axis=1
                )
                
                # Convert to records format
                restock_alerts = restock_items.to_dict('records')
                
                print(f"   - Sample restock items:")
                for idx, row in restock_items.head(3).iterrows():
                    print(f"     * {row['Product_Name'][:40]:40} | Stock: {row['Current_Stock']:4} | Rate: {row['Purchase_Rate']:.1f}/day | Days: {row['Days_Until_Stockout']:.1f} | {row['Urgency_Level']}")
            else:
                restock_alerts = []
                print(f"   - No items need restocking (all have >30 days stock)")
        else:
            restock_alerts = []
            print(f"   - No warehouse data available")
        
        return jsonify(restock_alerts)
    except Exception as e:
        print(f"Error getting restock alerts data: {e}")
        return jsonify([])

if __name__ == '__main__':
    # Use environment variable for port, default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 