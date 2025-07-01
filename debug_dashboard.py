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
from sqlalchemy import create_engine, text
import time
warnings.filterwarnings('ignore')

app = Flask(__name__)

class DebugSalesDashboard:
    def __init__(self):
        print("🚀 Initializing Debug Dashboard...")
        self.insights = {}
        self.warehouse_insights = {}
        self.test_connections()
        self.generate_sample_insights()
        print("✅ Dashboard initialization complete!")
    
    def test_connections(self):
        """Test database connections with timeouts"""
        print("\n🔍 Testing database connections...")
        
        # Test Synchub connection
        print("   Testing synchub_data connection...")
        try:
            synchub_conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='synchub_data',
                connect_timeout=5,
                read_timeout=10,
                write_timeout=10
            )
            if synchub_conn.is_connected():
                cursor = synchub_conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM item LIMIT 1")
                count = cursor.fetchone()[0]
                print(f"   ✅ synchub_data connected! Sample count: {count}")
                synchub_conn.close()
            else:
                print("   ❌ synchub_data connection failed")
        except Exception as e:
            print(f"   ❌ synchub_data error: {e}")
        
        # Test Acumatica connection
        print("   Testing acumatica_data connection...")
        try:
            acumatica_conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='acumatica_data',
                connect_timeout=5,
                read_timeout=10,
                write_timeout=10
            )
            if acumatica_conn.is_connected():
                cursor = acumatica_conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM inventoryitem LIMIT 1")
                count = cursor.fetchone()[0]
                print(f"   ✅ acumatica_data connected! Sample count: {count}")
                acumatica_conn.close()
            else:
                print("   ❌ acumatica_data connection failed")
        except Exception as e:
            print(f"   ❌ acumatica_data error: {e}")
    
    def get_mysql_connection(self, database):
        """Get MySQL connection with debug info"""
        print(f"🔌 Connecting to {database}...")
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database=database,
                connect_timeout=5,
                read_timeout=10,
                write_timeout=10
            )
            print(f"✅ Connected to {database}")
            return connection
        except Exception as e:
            print(f"❌ Error connecting to {database}: {e}")
            return None
    
    def generate_sample_insights(self):
        """Generate sample insights for testing"""
        print("📊 Generating sample insights...")
        
        self.insights = {
            'total_revenue': 1250000.0,
            'total_units_sold': 45000,
            'total_stock_remaining': 15000,
            'total_products': 38903,  # From your database count
            'avg_profit_margin': 75.0,
            'top_product': 'Premium Vibrator Deluxe',
            'top_product_revenue': 25000.0,
            'negative_margin_products': 0,
            'high_margin_products': 25000
        }
        
        self.warehouse_insights = {
            'total_products': 38903,
            'total_current_stock': 15000,
            'products_needing_restock': 1250,
            'low_stock_products': 1250,
            'overstocked_products': 500,
            'avg_lead_time': 7.5,
            'total_safety_stock': 5000,
            'avg_stock_turnover': 4.2,
            'warehouse_locations': 3,
            'suppliers': 25,
            'critical_stock_products': 150
        }
        
        print("✅ Sample insights generated")
    
    def get_sample_products(self, limit=50):
        """Get sample products with debug info"""
        print(f"📦 Getting sample products (limit: {limit})...")
        
        sample_products = []
        
        # Try to get real data from synchub
        print("   Fetching from synchub_data...")
        synchub_conn = self.get_mysql_connection('synchub_data')
        if synchub_conn:
            try:
                print("   Executing synchub query...")
                query = f"""
                SELECT 
                    i.Description,
                    i.RemoteID as `System ID`,
                    COALESCE(SUM(ol.Quantity), 0) as Sold,
                    COALESCE(MAX(is1.Qoh), 0) as Stock,
                    COALESCE(SUM(ol.Total), 0) as Total,
                    100 as Margin,
                    'Lightspeed' as Source
                FROM item i
                LEFT JOIN orderline ol ON i.RemoteID = ol.ItemID
                LEFT JOIN itemshop is1 ON i.RemoteID = is1.ItemID
                WHERE i.Description IS NOT NULL
                GROUP BY i.RemoteID, i.Description
                ORDER BY Total DESC
                LIMIT {limit}
                """
                print(f"   Query: {query[:100]}...")
                
                start_time = time.time()
                df = pd.read_sql(query, synchub_conn)
                end_time = time.time()
                
                print(f"   ✅ Query completed in {end_time - start_time:.2f}s")
                print(f"   Retrieved {len(df)} records")
                
                if not df.empty:
                    df['Category'] = self.categorize_products(df['Description'])
                    sample_products.extend(df.to_dict('records'))
                
                synchub_conn.close()
                
            except Exception as e:
                print(f"   ❌ Error in synchub query: {e}")
                synchub_conn.close()
        
        # Try to get real data from acumatica
        print("   Fetching from acumatica_data...")
        acumatica_conn = self.get_mysql_connection('acumatica_data')
        if acumatica_conn:
            try:
                print("   Executing acumatica query...")
                query = f"""
                SELECT 
                    i.Descr as Description,
                    i.InventoryID as `System ID`,
                    COALESCE(SUM(sod.OrderQty), 0) as Sold,
                    0 as Stock,
                    COALESCE(SUM(sod.ExtendedPrice), 0) as Total,
                    100 as Margin,
                    'Acumatica' as Source
                FROM inventoryitem i
                LEFT JOIN salesorderdetail sod ON i.InventoryID = sod.InventoryID
                WHERE i.Descr IS NOT NULL
                GROUP BY i.InventoryID, i.Descr
                ORDER BY Total DESC
                LIMIT {limit}
                """
                print(f"   Query: {query[:100]}...")
                
                start_time = time.time()
                df = pd.read_sql(query, acumatica_conn)
                end_time = time.time()
                
                print(f"   ✅ Query completed in {end_time - start_time:.2f}s")
                print(f"   Retrieved {len(df)} records")
                
                if not df.empty:
                    df['Category'] = self.categorize_products(df['Description'])
                    sample_products.extend(df.to_dict('records'))
                
                acumatica_conn.close()
                
            except Exception as e:
                print(f"   ❌ Error in acumatica query: {e}")
                acumatica_conn.close()
        
        # If no real data, create sample data
        if not sample_products:
            print("   Creating sample data...")
            sample_products = self.create_sample_products(limit)
        
        print(f"✅ Total products loaded: {len(sample_products)}")
        return sample_products
    
    def create_sample_products(self, limit=50):
        """Create sample products for testing"""
        print("   Generating sample product data...")
        
        sample_products = [
            "Premium Vibrator Deluxe", "Rhino Male Enhancement", "Silky Lube Gel", 
            "Lace Lingerie Set", "Adult Toy Collection", "Battery Charger Kit",
            "Wand Massager Pro", "Mood Enhancement Pills", "Leather Restraints",
            "Silicone Dildo Set", "Lubricant Oil", "Stockings & Garters"
        ]
        
        categories = ['Vibrators', 'Supplements', 'Lubricants', 'Clothing & Accessories', 
                     'Adult Toys', 'Accessories']
        
        np.random.seed(42)
        products = []
        
        for i in range(min(limit, len(sample_products))):
            product = sample_products[i]
            category = categories[i % len(categories)]
            sold = np.random.randint(10, 500)
            stock = np.random.randint(0, 200)
            total = np.random.uniform(1000, 25000)
            
            products.append({
                'Description': product,
                'System ID': f"PROD{i+1:03d}",
                'Sold': sold,
                'Stock': stock,
                'Total': total,
                'Margin': np.random.uniform(60, 90),
                'Source': 'Sample Data',
                'Category': category
            })
        
        return products
    
    def categorize_products(self, descriptions):
        """Categorize products based on description"""
        categories = []
        for desc in descriptions:
            if pd.isna(desc):
                categories.append('Other')
                continue
                
            desc_lower = str(desc).lower()
            if any(word in desc_lower for word in ['vibrator', 'rabbit', 'bullet', 'wand']):
                categories.append('Vibrators')
            elif any(word in desc_lower for word in ['supplement', 'rhino', 'mood', 'male', 'female']):
                categories.append('Supplements')
            elif any(word in desc_lower for word in ['lube', 'lubricant', 'gel', 'oil']):
                categories.append('Lubricants')
            elif any(word in desc_lower for word in ['dress', 'lingerie', 'bra', 'panty', 'stocking', 'heels', 'shoes']):
                categories.append('Clothing & Accessories')
            elif any(word in desc_lower for word in ['dildo', 'plug', 'ring', 'harness', 'restraint']):
                categories.append('Adult Toys')
            elif any(word in desc_lower for word in ['cleaner', 'clean', 'charger', 'battery']):
                categories.append('Accessories')
            else:
                categories.append('Other')
        return categories

# Initialize dashboard
print("🎯 Creating Debug Dashboard instance...")
dashboard = DebugSalesDashboard()

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
    products = dashboard.get_sample_products(limit)
    return jsonify(products)

@app.route('/api/data/negative-margin')
def get_negative_margin():
    """API endpoint for negative margin products"""
    print("📉 Serving negative margin API")
    return jsonify([])  # Empty for now

@app.route('/api/data/category-summary')
def get_category_summary():
    """API endpoint for category summary"""
    print("📋 Serving category summary API")
    return jsonify({})

@app.route('/api/data/warehouse-summary')
def get_warehouse_summary():
    """API endpoint for warehouse summary"""
    print("🏭 Serving warehouse summary API")
    return jsonify({})

@app.route('/api/data/restock-alerts')
def get_restock_alerts():
    """API endpoint for restock alerts"""
    print("⚠️ Serving restock alerts API")
    return jsonify([])

@app.route('/api/data/warehouse-locations')
def get_warehouse_locations():
    """API endpoint for warehouse locations"""
    print("📍 Serving warehouse locations API")
    return jsonify({})

@app.route('/api/charts/<chart_type>')
def get_chart(chart_type):
    """API endpoint for charts"""
    print(f"📈 Serving chart API: {chart_type}")
    return jsonify({})

@app.route('/api/debug/status')
def get_debug_status():
    """API endpoint for debug status"""
    print("🔍 Serving debug status API")
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'insights_loaded': bool(dashboard.insights),
        'warehouse_insights_loaded': bool(dashboard.warehouse_insights)
    })

if __name__ == '__main__':
    print("🚀 Starting Debug Sales Analytics Dashboard...")
    print("Access the dashboard at: http://127.0.0.1:8080")
    print("Debug status at: http://127.0.0.1:8080/api/debug/status")
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    ) 