from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

class InstantSalesDashboard:
    def __init__(self):
        print("🚀 Initializing Instant Dashboard...")
        self.insights = {}
        self.warehouse_insights = {}
        self.products = []
        self.generate_instant_data()
        print("✅ Instant Dashboard ready!")
    
    def generate_instant_data(self):
        """Generate instant sample data"""
        print("📊 Generating instant data...")
        
        # Generate sample products
        sample_products = [
            "Premium Vibrator Deluxe", "Rhino Male Enhancement", "Silky Lube Gel", 
            "Lace Lingerie Set", "Adult Toy Collection", "Battery Charger Kit",
            "Wand Massager Pro", "Mood Enhancement Pills", "Leather Restraints",
            "Silicone Dildo Set", "Lubricant Oil", "Stockings & Garters",
            "Adult Game Kit", "Cleaner Solution", "Remote Control Toy",
            "Vibrating Ring", "Female Enhancement", "Massage Oil", "Corset Set",
            "Anal Plug Set", "Charging Station", "Heating Lube", "Fishnet Stockings"
        ]
        
        categories = ['Vibrators', 'Supplements', 'Lubricants', 'Clothing & Accessories', 
                     'Adult Toys', 'Accessories', 'Other']
        
        np.random.seed(42)
        
        # Generate products
        for i, product in enumerate(sample_products):
            category = categories[i % len(categories)]
            sold = np.random.randint(10, 500)
            stock = np.random.randint(0, 200)
            total = np.random.uniform(1000, 25000)
            margin = np.random.uniform(60, 90)
            
            self.products.append({
                'Description': product,
                'System ID': f"PROD{i+1:03d}",
                'Sold': sold,
                'Stock': stock,
                'Total': total,
                'Margin': margin,
                'Source': 'Sample Data',
                'Category': category
            })
        
        # Generate insights
        total_revenue = sum(p['Total'] for p in self.products)
        total_units_sold = sum(p['Sold'] for p in self.products)
        total_stock = sum(p['Stock'] for p in self.products)
        
        self.insights = {
            'total_revenue': float(total_revenue),
            'total_units_sold': int(total_units_sold),
            'total_stock_remaining': int(total_stock),
            'total_products': len(self.products),
            'avg_profit_margin': float(np.mean([p['Margin'] for p in self.products])),
            'top_product': max(self.products, key=lambda x: x['Total'])['Description'],
            'top_product_revenue': float(max(self.products, key=lambda x: x['Total'])['Total']),
            'negative_margin_products': 0,
            'high_margin_products': len([p for p in self.products if p['Margin'] > 50])
        }
        
        self.warehouse_insights = {
            'total_products': len(self.products),
            'total_current_stock': int(total_stock),
            'products_needing_restock': len([p for p in self.products if p['Stock'] < 10]),
            'low_stock_products': len([p for p in self.products if p['Stock'] < 20]),
            'overstocked_products': len([p for p in self.products if p['Stock'] > 100]),
            'avg_lead_time': 7.5,
            'total_safety_stock': int(total_stock * 0.2),
            'avg_stock_turnover': 4.2,
            'warehouse_locations': 3,
            'suppliers': 25,
            'critical_stock_products': len([p for p in self.products if p['Stock'] < 5])
        }
        
        print(f"✅ Generated {len(self.products)} products, ${total_revenue:,.0f} revenue")

# Initialize dashboard
print("🎯 Creating Instant Dashboard instance...")
dashboard = InstantSalesDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    print("📄 Serving main dashboard page")
    return render_template('dashboard_pro.html')

@app.route('/api/metrics')
def get_metrics():
    """API endpoint for key metrics"""
    print("📊 Serving metrics API")
    return jsonify(dashboard.insights)

@app.route('/api/warehouse/metrics')
def get_warehouse_metrics():
    """API endpoint for warehouse metrics"""
    print("🏭 Serving warehouse metrics API")
    return jsonify(dashboard.warehouse_insights)

@app.route('/api/data/top-products')
def get_top_products():
    """API endpoint for top products"""
    print("📦 Serving top products API")
    limit = int(request.args.get('limit', 50))
    sorted_products = sorted(dashboard.products, key=lambda x: x['Total'], reverse=True)
    return jsonify(sorted_products[:limit])

@app.route('/api/data/negative-margin')
def get_negative_margin():
    """API endpoint for negative margin products"""
    print("📉 Serving negative margin API")
    negative_products = [p for p in dashboard.products if p['Margin'] < 0]
    return jsonify(negative_products)

@app.route('/api/data/category-summary')
def get_category_summary():
    """API endpoint for category summary"""
    print("📋 Serving category summary API")
    df = pd.DataFrame(dashboard.products)
    if not df.empty:
        category_summary = df.groupby('Category').agg({
            'Total': ['sum', 'count'],
            'Margin': 'mean',
            'Sold': 'sum',
            'Stock': 'sum'
        }).round(2)
        category_summary.columns = ['_'.join(col).strip() for col in category_summary.columns]
        return jsonify(category_summary.to_dict('index'))
    return jsonify({})

@app.route('/api/data/warehouse-summary')
def get_warehouse_summary():
    """API endpoint for warehouse summary"""
    print("🏭 Serving warehouse summary API")
    df = pd.DataFrame(dashboard.products)
    if not df.empty:
        warehouse_summary = df.groupby('Category').agg({
            'Stock': ['sum', 'mean'],
            'Sold': 'sum'
        }).round(2)
        warehouse_summary.columns = ['_'.join(col).strip() for col in warehouse_summary.columns]
        return jsonify(warehouse_summary.to_dict('index'))
    return jsonify({})

@app.route('/api/data/restock-alerts')
def get_restock_alerts():
    """API endpoint for restock alerts"""
    print("⚠️ Serving restock alerts API")
    restock_alerts = [p for p in dashboard.products if p['Stock'] < 10]
    restock_alerts = sorted(restock_alerts, key=lambda x: x['Stock'])[:15]
    return jsonify(restock_alerts)

@app.route('/api/data/warehouse-locations')
def get_warehouse_locations():
    """API endpoint for warehouse locations"""
    print("📍 Serving warehouse locations API")
    return jsonify({
        'Main Warehouse': {
            'Total_Stock': sum(p['Stock'] for p in dashboard.products),
            'Product_Count': len(dashboard.products),
            'Restock_Needed': len([p for p in dashboard.products if p['Stock'] < 10])
        }
    })

@app.route('/api/charts/margin-distribution')
def get_margin_distribution_chart():
    """API endpoint for margin distribution chart"""
    print("📈 Serving margin distribution chart")
    try:
        df = pd.DataFrame(dashboard.products)
        fig = px.histogram(
            df,
            x='Margin',
            nbins=20,
            title="Profit Margin Distribution",
            labels={'Margin': 'Profit Margin (%)', 'count': 'Number of Products'},
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(title_x=0.5, title_font_size=16, showlegend=False)
        return jsonify(json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)))
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/charts/revenue-by-category')
def get_revenue_by_category_chart():
    """API endpoint for revenue by category chart"""
    print("📈 Serving revenue by category chart")
    try:
        df = pd.DataFrame(dashboard.products)
        category_revenue = df.groupby('Category')['Total'].sum().sort_values(ascending=False)
        fig = px.pie(
            values=category_revenue.values,
            names=category_revenue.index,
            title="Revenue Distribution by Category"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(title_x=0.5, title_font_size=16)
        return jsonify(json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)))
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/charts/top-products-chart')
def get_top_products_chart():
    """API endpoint for top products chart"""
    print("📈 Serving top products chart")
    try:
        top_products = sorted(dashboard.products, key=lambda x: x['Total'], reverse=True)[:10]
        df = pd.DataFrame(top_products)
        fig = px.bar(
            df,
            x='Total',
            y='Description',
            orientation='h',
            title="Top 10 Products by Revenue",
            color='Category',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(title_x=0.5, title_font_size=16, yaxis={'categoryorder':'total ascending'})
        return jsonify(json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)))
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/charts/warehouse-stock-status')
def get_warehouse_stock_status_chart():
    """API endpoint for warehouse stock status chart"""
    print("📈 Serving warehouse stock status chart")
    try:
        df = pd.DataFrame(dashboard.products)
        df['Stock_Status'] = df['Stock'].apply(lambda x: 'Low' if x < 20 else 'Adequate' if x < 100 else 'Overstocked')
        stock_status = df['Stock_Status'].value_counts()
        fig = px.pie(
            values=stock_status.values,
            names=stock_status.index,
            title="Warehouse Stock Status Distribution",
            color_discrete_sequence=['#ef4444', '#10b981', '#f59e0b']
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(title_x=0.5, title_font_size=16)
        return jsonify(json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)))
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/status')
def get_status():
    """API endpoint for status"""
    print("🔍 Serving status API")
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'products_loaded': len(dashboard.products),
        'total_revenue': dashboard.insights['total_revenue'],
        'message': 'Instant dashboard running with sample data'
    })

if __name__ == '__main__':
    print("🚀 Starting Instant Sales Analytics Dashboard...")
    print("Access the dashboard at: http://127.0.0.1:8080")
    print("Status at: http://127.0.0.1:8080/api/status")
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    ) 