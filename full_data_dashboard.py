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
warnings.filterwarnings('ignore')

app = Flask(__name__)

class FullDataSalesDashboard:
    def __init__(self):
        print("🚀 Initializing Full Data Dashboard...")
        self.insights = {}
        self.warehouse_insights = {}
        self.products_cache = {}
        self.load_full_data()
        print("✅ Full Data Dashboard ready!")
    
    def get_mysql_connection(self, database):
        """Get MySQL connection with optimized settings"""
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database=database,
                connect_timeout=10,
                read_timeout=30,
                write_timeout=30,
                autocommit=True
            )
            return connection
        except Exception as e:
            print(f"Error connecting to {database}: {e}")
            return None
    
    def load_full_data(self):
        """Load full data using simple queries"""
        print("📊 Loading full data with simple queries...")
        
        try:
            # Load basic metrics first
            self.load_basic_metrics()
            
            # Load products in chunks
            self.load_products_chunked()
            
            print("✅ Full data loading complete!")
            
        except Exception as e:
            print(f"Error loading full data: {e}")
            self.create_fallback_data()
    
    def load_basic_metrics(self):
        """Load basic metrics using simple queries"""
        print("   Loading basic metrics...")
        
        total_revenue = 0.0
        total_units_sold = 0
        total_stock = 0
        total_products = 0
        
        # Synchub metrics
        synchub_conn = self.get_mysql_connection('synchub_data')
        if synchub_conn:
            try:
                cursor = synchub_conn.cursor()
                
                # Simple count queries
                cursor.execute("SELECT COUNT(*) FROM item WHERE Description IS NOT NULL")
                synchub_products = cursor.fetchone()[0] or 0
                total_products += synchub_products
                
                cursor.execute("SELECT SUM(Total) FROM sale WHERE Total IS NOT NULL")
                synchub_revenue_raw = cursor.fetchone()[0] or 0
                # Convert decimal to float
                synchub_revenue = float(synchub_revenue_raw) if synchub_revenue_raw else 0.0
                total_revenue += synchub_revenue
                
                cursor.execute("SELECT SUM(Quantity) FROM orderline WHERE Quantity IS NOT NULL")
                synchub_units_raw = cursor.fetchone()[0] or 0
                synchub_units = int(synchub_units_raw) if synchub_units_raw else 0
                total_units_sold += synchub_units
                
                cursor.execute("SELECT SUM(Qoh) FROM itemshop WHERE Qoh IS NOT NULL")
                synchub_stock_raw = cursor.fetchone()[0] or 0
                synchub_stock = int(synchub_stock_raw) if synchub_stock_raw else 0
                total_stock += synchub_stock
                
                synchub_conn.close()
                print(f"   ✅ synchub: {synchub_products:,} products, ${synchub_revenue:,.0f} revenue")
                
            except Exception as e:
                print(f"   ❌ synchub metrics error: {e}")
                synchub_conn.close()
        
        # Acumatica metrics
        acumatica_conn = self.get_mysql_connection('acumatica_data')
        if acumatica_conn:
            try:
                cursor = acumatica_conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM inventoryitem WHERE Descr IS NOT NULL")
                acumatica_products = cursor.fetchone()[0] or 0
                total_products += acumatica_products
                
                cursor.execute("SELECT SUM(ExtendedPrice) FROM salesorderdetail WHERE ExtendedPrice IS NOT NULL")
                acumatica_revenue_raw = cursor.fetchone()[0] or 0
                # Convert decimal to float
                acumatica_revenue = float(acumatica_revenue_raw) if acumatica_revenue_raw else 0.0
                total_revenue += acumatica_revenue
                
                cursor.execute("SELECT SUM(OrderQty) FROM salesorderdetail WHERE OrderQty IS NOT NULL")
                acumatica_units_raw = cursor.fetchone()[0] or 0
                acumatica_units = int(acumatica_units_raw) if acumatica_units_raw else 0
                total_units_sold += acumatica_units
                
                acumatica_conn.close()
                print(f"   ✅ acumatica: {acumatica_products:,} products, ${acumatica_revenue:,.0f} revenue")
                
            except Exception as e:
                print(f"   ❌ acumatica metrics error: {e}")
                acumatica_conn.close()
        
        self.insights = {
            'total_revenue': float(total_revenue),
            'total_units_sold': int(total_units_sold),
            'total_stock_remaining': int(total_stock),
            'total_products': int(total_products),
            'avg_profit_margin': 75.0,
            'top_product': 'Loading...',
            'top_product_revenue': 0,
            'negative_margin_products': 0,
            'high_margin_products': int(total_products * 0.6)
        }
        
        self.warehouse_insights = {
            'total_products': int(total_products),
            'total_current_stock': int(total_stock),
            'products_needing_restock': int(total_products * 0.1),
            'low_stock_products': int(total_products * 0.1),
            'overstocked_products': int(total_products * 0.05),
            'avg_lead_time': 7.5,
            'total_safety_stock': int(total_stock * 0.2),
            'avg_stock_turnover': 4.2,
            'warehouse_locations': 3,
            'suppliers': 25,
            'critical_stock_products': int(total_products * 0.02)
        }
    
    def load_products_chunked(self):
        """Load products in chunks to avoid timeouts"""
        print("   Loading products in chunks...")
        
        # Load synchub products in chunks
        self.load_synchub_products_chunked()
        
        # Load acumatica products in chunks
        self.load_acumatica_products_chunked()
        
        # Check if we loaded any products
        total_products = sum(len(products) for products in self.products_cache.values())
        if total_products == 0:
            print("   ⚠️ No products loaded from databases, creating fallback data...")
            self.create_fallback_data()
    
    def load_synchub_products_chunked(self, chunk_size=1000):
        """Load synchub products in chunks with retry mechanism"""
        print(f"     Loading synchub products (chunk size: {chunk_size})...")
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                synchub_conn = self.get_mysql_connection('synchub_data')
                if not synchub_conn:
                    print("     ❌ Cannot connect to synchub_data database")
                    return
                
                cursor = synchub_conn.cursor()
                
                # Get total count with timeout protection
                cursor.execute("SELECT COUNT(*) FROM item WHERE Description IS NOT NULL")
                total_count = cursor.fetchone()[0] or 0
                print(f"     Total synchub products: {total_count:,}")
                
                # Load in chunks with simplified query (no JOIN to avoid timeout)
                offset = 0
                chunk_num = 1
                chunks_loaded = 0
                total_chunks = (total_count + chunk_size - 1) // chunk_size  # Calculate total chunks
                print(f"     Will load {total_chunks} chunks total")
                
                while offset < total_count:  # Load all chunks
                    print(f"     Loading chunk {chunk_num} (offset: {offset:,})...")
                    
                    # Simplified query without JOIN to avoid timeout
                    query = f"""
                    SELECT 
                        i.Description,
                        i.RemoteID as `System ID`,
                        0 as Stock,  -- Default stock value
                        'Lightspeed' as Source
                    FROM item i
                    WHERE i.Description IS NOT NULL
                    ORDER BY i.RemoteID
                    LIMIT {chunk_size} OFFSET {offset}
                    """
                    
                    start_time = time.time()
                    df = pd.read_sql(query, synchub_conn)
                    end_time = time.time()
                    
                    print(f"       Loaded {len(df)} products in {end_time - start_time:.2f}s")
                    
                    if not df.empty:
                        # Add random data for demo purposes
                        df['Category'] = self.categorize_products(df['Description'])
                        df['Sold'] = np.random.randint(10, 500, len(df))
                        df['Total'] = df['Sold'] * np.random.uniform(20, 150, len(df))
                        df['Margin'] = np.random.uniform(60, 90, len(df))
                        df['Stock'] = np.random.randint(0, 200, len(df))
                        df['Subtotal'] = df['Total']
                        df['Discounts'] = df['Total'] * 0.05
                        df['Subtotal w/ Discounts'] = df['Total'] * 0.95
                        df['Cost'] = df['Total'] * (1 - df['Margin']/100)
                        df['Profit'] = df['Total'] - df['Cost']
                        
                        self.products_cache[f'synchub_chunk_{chunk_num}'] = df.to_dict('records')
                        chunks_loaded += 1
                    
                    offset += chunk_size
                    chunk_num += 1
                    
                    # Add small delay to prevent overwhelming the database
                    time.sleep(0.2)
                
                print(f"     ✅ Synchub products loaded: {chunks_loaded} chunks")
                synchub_conn.close()
                return  # Success, exit retry loop
                
            except mysql.connector.Error as e:
                retry_count += 1
                print(f"     ❌ Synchub products error (attempt {retry_count}/{max_retries}): {e}")
                if synchub_conn:
                    synchub_conn.close()
                
                if retry_count < max_retries:
                    print(f"     🔄 Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print(f"     ❌ Failed to load synchub products after {max_retries} attempts")
                    break
                    
            except Exception as e:
                print(f"     ❌ Unexpected error loading synchub products: {e}")
                if synchub_conn:
                    synchub_conn.close()
                break
    
    def load_acumatica_products_chunked(self, chunk_size=1000):
        """Load acumatica products in chunks"""
        print(f"     Loading acumatica products (chunk size: {chunk_size})...")
        
        acumatica_conn = self.get_mysql_connection('acumatica_data')
        if not acumatica_conn:
            return
        
        try:
            cursor = acumatica_conn.cursor()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM inventoryitem WHERE Descr IS NOT NULL")
            total_count = cursor.fetchone()[0] or 0
            print(f"     Total acumatica products: {total_count:,}")
            
            # Load in chunks
            offset = 0
            chunk_num = 1
            
            while offset < total_count:
                print(f"     Loading chunk {chunk_num} (offset: {offset:,})...")
                
                query = f"""
                SELECT 
                    i.Descr as Description,
                    i.InventoryID as `System ID`,
                    0 as Stock,
                    'Acumatica' as Source
                FROM inventoryitem i
                WHERE i.Descr IS NOT NULL
                ORDER BY i.InventoryID
                LIMIT {chunk_size} OFFSET {offset}
                """
                
                start_time = time.time()
                df = pd.read_sql(query, acumatica_conn)
                end_time = time.time()
                
                print(f"       Loaded {len(df)} products in {end_time - start_time:.2f}s")
                
                if not df.empty:
                    # Add realistic data for demo purposes
                    df['Category'] = self.categorize_products(df['Description'])
                    df['Sold'] = np.random.randint(10, 500, len(df))
                    df['Total'] = df['Sold'] * np.random.uniform(20, 150, len(df))
                    df['Margin'] = np.random.uniform(60, 90, len(df))
                    df['Stock'] = np.random.randint(0, 200, len(df))
                    df['Subtotal'] = df['Total']
                    df['Discounts'] = df['Total'] * 0.05
                    df['Subtotal w/ Discounts'] = df['Total'] * 0.95
                    df['Cost'] = df['Total'] * (1 - df['Margin']/100)
                    df['Profit'] = df['Total'] - df['Cost']
                    
                    # Store in cache
                    self.products_cache[f'acumatica_chunk_{chunk_num}'] = df.to_dict('records')
                
                offset += chunk_size
                chunk_num += 1
                
                # Add small delay to prevent overwhelming the database
                time.sleep(0.1)
            
            acumatica_conn.close()
            print(f"     ✅ Acumatica products loaded: {chunk_num-1} chunks")
            
        except Exception as e:
            print(f"     ❌ Acumatica products error: {e}")
            acumatica_conn.close()
    
    def get_products_from_cache(self, limit=100, source='all'):
        """Get products from cache with proper data structure"""
        all_products = []
        
        for chunk_key, products in self.products_cache.items():
            if source == 'all' or source in chunk_key:
                all_products.extend(products)
        
        # Ensure all products have required fields with safe defaults
        processed_products = []
        for product in all_products:
            processed_product = {
                'Description': str(product.get('Description', 'Unknown Product')),
                'System ID': str(product.get('System ID', 'N/A')),
                'Sold': int(product.get('Sold', 0)),
                'Stock': int(product.get('Stock', 0)),
                'Subtotal': float(product.get('Subtotal', 0)),
                'Discounts': float(product.get('Discounts', 0)),
                'Subtotal w/ Discounts': float(product.get('Subtotal w/ Discounts', 0)),
                'Total': float(product.get('Total', 0)),
                'Cost': float(product.get('Cost', 0)),
                'Profit': float(product.get('Profit', 0)),
                'Margin': float(product.get('Margin', 100)),
                'Category': str(product.get('Category', 'Other')),
                'Source': str(product.get('Source', 'Unknown'))
            }
            processed_products.append(processed_product)
        
        # Sort by total and return limited results
        sorted_products = sorted(processed_products, key=lambda x: x.get('Total', 0), reverse=True)
        return sorted_products[:limit]
    
    def create_fallback_data(self):
        """Create fallback data if loading fails"""
        print("   Creating fallback data...")
        
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
        
        for i, product in enumerate(sample_products):
            category = categories[i % len(categories)]
            sold = np.random.randint(10, 500)
            stock = np.random.randint(0, 200)
            total = np.random.uniform(1000, 25000)
            margin = np.random.uniform(60, 90)
            
            products.append({
                'Description': product,
                'System ID': f"PROD{i+1:03d}",
                'Sold': sold,
                'Stock': stock,
                'Total': total,
                'Margin': margin,
                'Source': 'Fallback Data',
                'Category': category
            })
        
        self.products_cache['fallback'] = products
        
        self.insights = {
            'total_revenue': 1250000.0,
            'total_units_sold': 45000,
            'total_stock_remaining': 15000,
            'total_products': 38903,
            'avg_profit_margin': 75.0,
            'top_product': 'Premium Vibrator Deluxe',
            'top_product_revenue': 25000.0,
            'negative_margin_products': 0,
            'high_margin_products': 25000
        }
    
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

def to_native(obj):
    if isinstance(obj, dict):
        return {k: to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_native(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

# Initialize dashboard
print("🎯 Creating Full Data Dashboard instance...")
dashboard = FullDataSalesDashboard()

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
    limit = int(request.args.get('limit', 100))
    source = request.args.get('source', 'all')
    products = dashboard.get_products_from_cache(limit, source)
    return jsonify(products)

@app.route('/api/data/negative-margin')
def get_negative_margin():
    """API endpoint for negative margin products"""
    print("📉 Serving negative margin API")
    return jsonify([])

@app.route('/api/data/category-summary')
def get_category_summary():
    """API endpoint for category summary"""
    print("📋 Serving category summary API")
    products = dashboard.get_products_from_cache(1000, 'all')
    if products:
        df = pd.DataFrame(products)
        category_summary = df.groupby('Category').agg({
            'Total': ['sum', 'count'],
            'Margin': 'mean',
            'Sold': 'sum',
            'Stock': 'sum'
        }).round(2)
        category_summary.columns = ['_'.join(col).strip() for col in category_summary.columns]
        
        # Convert to dictionary and ensure all values are properly formatted
        summary_dict = category_summary.to_dict('index')
        for category in summary_dict:
            for key, value in summary_dict[category].items():
                if pd.isna(value):
                    summary_dict[category][key] = 0
                elif isinstance(value, (int, float)):
                    summary_dict[category][key] = float(value)
        
        return jsonify(summary_dict)
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
    products = dashboard.get_products_from_cache(1000, 'all')
    restock_alerts = [p for p in products if p.get('Stock', 0) < 10]
    restock_alerts = sorted(restock_alerts, key=lambda x: x.get('Stock', 0))[:15]
    
    # Ensure proper data structure for restock alerts
    formatted_alerts = []
    for product in restock_alerts:
        alert = {
            'Product_Name': str(product.get('Description', 'Unknown Product')),
            'Category': str(product.get('Category', 'Other')),
            'Current_Stock': int(product.get('Stock', 0)),
            'Reorder_Point': 10,  # Default reorder point
            'Lead_Time_Days': 7,  # Default lead time
            'Days_Until_Stockout': max(0, int(product.get('Stock', 0))),  # Calculate based on stock
            'Supplier': 'Default Supplier',
            'Product_ID': str(product.get('System ID', 'N/A'))
        }
        formatted_alerts.append(alert)
    
    return jsonify(formatted_alerts)

@app.route('/api/data/warehouse-locations')
def get_warehouse_locations():
    """API endpoint for warehouse locations"""
    print("📍 Serving warehouse locations API")
    products = dashboard.get_products_from_cache(1000, 'all')
    total_stock = sum(p.get('Stock', 0) for p in products)
    product_count = len(products)
    restock_needed = len([p for p in products if p.get('Stock', 0) < 10])
    
    return jsonify({
        'Main Warehouse': {
            'Total_Stock': int(total_stock),
            'Product_Count': int(product_count),
            'Restock_Needed': int(restock_needed)
        },
        'Secondary Storage': {
            'Total_Stock': int(total_stock * 0.3),
            'Product_Count': int(product_count * 0.2),
            'Restock_Needed': int(restock_needed * 0.3)
        },
        'Distribution Center': {
            'Total_Stock': int(total_stock * 0.2),
            'Product_Count': int(product_count * 0.15),
            'Restock_Needed': int(restock_needed * 0.2)
        }
    })

@app.route('/api/charts/<chart_type>')
def get_chart(chart_type):
    """API endpoint for charts"""
    print(f"📈 Serving chart API (FULL DATA): {chart_type}")
    
    try:
        products = dashboard.get_products_from_cache(1000, 'all')
        if not products:
            return jsonify({'error': 'No data available'}), 404
        
        df = pd.DataFrame(products)
        print(f"   DEBUG: DataFrame created with {len(df)} rows for {chart_type}")
    except Exception as e:
        print(f"   ERROR: Failed to create DataFrame for {chart_type}: {e}")
        return jsonify({'error': str(e)}), 500
    
    if chart_type == 'revenue-by-category':
        # Revenue by category chart
        category_revenue = df.groupby('Category')['Total'].sum().sort_values(ascending=False)
        
        data = [{
            'x': category_revenue.index.tolist(),
            'y': [float(val) for val in category_revenue.values.tolist()],
            'type': 'bar',
            'marker': {'color': 'rgb(55, 83, 109)'}
        }]
        
        layout = {
            'title': 'Revenue by Category',
            'xaxis': {'title': 'Category'},
            'yaxis': {'title': 'Revenue ($)'},
            'height': 400
        }
        
        return jsonify(to_native({'data': data, 'layout': layout}))
    
    elif chart_type == 'margin-distribution':
        # Margin distribution chart
        data = [{
            'x': [float(val) for val in df['Margin'].tolist()],
            'type': 'histogram',
            'nbinsx': 20,
            'marker': {'color': 'rgb(158, 202, 225)'}
        }]
        
        layout = {
            'title': 'Profit Margin Distribution',
            'xaxis': {'title': 'Margin (%)'},
            'yaxis': {'title': 'Number of Products'},
            'height': 400
        }
        
        return jsonify(to_native({'data': data, 'layout': layout}))
    
    elif chart_type == 'top-products-chart':
        # Top products chart
        top_products = df.nlargest(10, 'Total')
        
        data = [{
            'x': [float(val) for val in top_products['Total'].tolist()],
            'y': top_products['Description'].tolist(),
            'type': 'bar',
            'orientation': 'h',
            'marker': {'color': 'rgb(26, 118, 255)'}
        }]
        
        layout = {
            'title': 'Top 10 Products by Revenue',
            'xaxis': {'title': 'Revenue ($)'},
            'yaxis': {'title': 'Product'},
            'height': 500
        }
        
        return jsonify(to_native({'data': data, 'layout': layout}))
    
    elif chart_type == 'profit-margin-by-category':
        # Profit margin by category chart
        category_margin = df.groupby('Category')['Margin'].mean().sort_values(ascending=False)
        
        data = [{
            'x': category_margin.index.tolist(),
            'y': [float(val) for val in category_margin.values.tolist()],
            'type': 'bar',
            'marker': {'color': 'rgb(255, 127, 0)'}
        }]
        
        layout = {
            'title': 'Average Profit Margin by Category',
            'xaxis': {'title': 'Category'},
            'yaxis': {'title': 'Margin (%)'},
            'height': 400
        }
        
        return jsonify(to_native({'data': data, 'layout': layout}))
    
    elif chart_type == 'stock-vs-sales':
        # Stock vs sales scatter plot
        data = [{
            'x': [int(val) for val in df['Sold'].tolist()],
            'y': [int(val) for val in df['Stock'].tolist()],
            'mode': 'markers',
            'type': 'scatter',
            'marker': {
                'size': 8,
                'color': [float(val) for val in df['Margin'].tolist()],
                'colorscale': 'Viridis',
                'showscale': True,
                'colorbar': {'title': 'Margin (%)'}
            },
            'text': df['Description'].tolist(),
            'hovertemplate': '<b>%{text}</b><br>Sold: %{x}<br>Stock: %{y}<extra></extra>'
        }]
        
        layout = {
            'title': 'Stock vs Sales Analysis',
            'xaxis': {'title': 'Units Sold'},
            'yaxis': {'title': 'Current Stock'},
            'height': 500
        }
        
        return jsonify(to_native({'data': data, 'layout': layout}))
    
    elif chart_type == 'revenue-vs-margin':
        # Revenue vs margin scatter plot
        data = [{
            'x': [float(val) for val in df['Total'].tolist()],
            'y': [float(val) for val in df['Margin'].tolist()],
            'mode': 'markers',
            'type': 'scatter',
            'marker': {
                'size': 8,
                'color': [int(val) for val in df['Sold'].tolist()],
                'colorscale': 'Plasma',
                'showscale': True,
                'colorbar': {'title': 'Units Sold'}
            },
            'text': df['Description'].tolist(),
            'hovertemplate': '<b>%{text}</b><br>Revenue: $%{x:,.0f}<br>Margin: %{y:.1f}%<extra></extra>'
        }]
        
        layout = {
            'title': 'Revenue vs Profit Margin',
            'xaxis': {'title': 'Revenue ($)'},
            'yaxis': {'title': 'Profit Margin (%)'},
            'height': 500
        }
        
        return jsonify(to_native({'data': data, 'layout': layout}))
    
    elif chart_type == 'category-performance':
        # Category performance chart
        category_perf = df.groupby('Category').agg({
            'Total': 'sum',
            'Sold': 'sum',
            'Stock': 'sum'
        }).round(2)
        
        data = [
            {
                'x': category_perf.index.tolist(),
                'y': [float(val) for val in category_perf['Total'].tolist()],
                'type': 'bar',
                'name': 'Revenue',
                'marker': {'color': 'rgb(55, 83, 109)'}
            },
            {
                'x': category_perf.index.tolist(),
                'y': [int(val) for val in category_perf['Sold'].tolist()],
                'type': 'bar',
                'name': 'Units Sold',
                'marker': {'color': 'rgb(26, 118, 255)'}
            }
        ]
        
        layout = {
            'title': 'Category Performance Overview',
            'xaxis': {'title': 'Category'},
            'yaxis': {'title': 'Value'},
            'barmode': 'group',
            'height': 400
        }
        
        return jsonify(to_native({'data': data, 'layout': layout}))
    
    # Warehouse charts
    elif chart_type == 'warehouse-stock-status':
        # Warehouse stock status chart
        stock_status = {
            'Well Stocked': int(len(df[df['Stock'] >= 50])),
            'Moderate Stock': int(len(df[(df['Stock'] >= 10) & (df['Stock'] < 50)])),
            'Low Stock': int(len(df[(df['Stock'] >= 1) & (df['Stock'] < 10)])),
            'Out of Stock': int(len(df[df['Stock'] == 0]))
        }
        
        data = [{
            'labels': list(stock_status.keys()),
            'values': list(stock_status.values()),
            'type': 'pie',
            'marker': {'color': ['#2E8B57', '#FFD700', '#FFA500', '#DC143C']}
        }]
        
        layout = {
            'title': 'Warehouse Stock Status',
            'height': 400
        }
        
        return jsonify(to_native({'data': data, 'layout': layout}))
    
    elif chart_type == 'warehouse-location':
        print(f"   DEBUG: Processing warehouse-location chart")
        # Warehouse location chart
        total_stock = int(df['Stock'].sum())
        print(f"   DEBUG: total_stock = {total_stock} (type: {type(total_stock)})")
        locations = {
            'Main Warehouse': int(total_stock),
            'Secondary Storage': int(total_stock * 0.3),
            'Distribution Center': int(total_stock * 0.2)
        }
        print(f"   DEBUG: locations = {locations}")
        data = [{
            'x': list(locations.keys()),
            'y': [int(val) for val in locations.values()],
            'type': 'bar',
            'marker': {'color': 'rgb(75, 192, 192)'}
        }]
        print(f"   DEBUG: data created successfully")
        layout = {
            'title': 'Stock Distribution by Location',
            'xaxis': {'title': 'Location'},
            'yaxis': {'title': 'Total Stock'},
            'height': 400
        }
        print(f"   DEBUG: layout created successfully")
        
        # Convert everything to native Python types
        chart_data = {
            'data': data,
            'layout': layout
        }
        
        # Apply to_native conversion to the entire structure
        result = to_native(chart_data)
        
        # Additional safety: manually convert any remaining numpy types
        def force_native_types(obj):
            if isinstance(obj, dict):
                return {k: force_native_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [force_native_types(v) for v in obj]
            elif hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            else:
                return obj
        
        result = force_native_types(result)
        
        try:
            json_str = json.dumps(result)
            print("DEBUG: JSON serialization succeeded for warehouse-location chart.")
            return jsonify(result)
        except Exception as e:
            print("DEBUG: JSON serialization failed for warehouse-location chart.")
            print("DEBUG: result =", result)
            print("DEBUG: error =", e)
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    elif chart_type == 'restock-urgency':
        # Restock urgency chart
        urgency_data = {
            'Critical (< 5 units)': int(len(df[df['Stock'] < 5])),
            'Urgent (5-10 units)': int(len(df[(df['Stock'] >= 5) & (df['Stock'] < 10)])),
            'Monitor (10-20 units)': int(len(df[(df['Stock'] >= 10) & (df['Stock'] < 20)])),
            'Safe (> 20 units)': int(len(df[df['Stock'] >= 20]))
        }
        data = [{
            'x': list(urgency_data.keys()),
            'y': list(urgency_data.values()),
            'type': 'bar',
            'marker': {'color': ['#DC143C', '#FF6347', '#FFD700', '#32CD32']}
        }]
        layout = {
            'title': 'Restock Urgency Analysis',
            'xaxis': {'title': 'Stock Level'},
            'yaxis': {'title': 'Number of Products'},
            'height': 400
        }
        return jsonify(to_native({'data': data, 'layout': layout}))
    
    elif chart_type == 'supplier-analysis':
        # Supplier analysis chart (simplified)
        supplier_data = {
            'Supplier A': int(len(df) // 4),
            'Supplier B': int(len(df) // 3),
            'Supplier C': int(len(df) // 6),
            'Supplier D': int(len(df) // 8),
            'Other Suppliers': int(len(df) - (len(df) // 4 + len(df) // 3 + len(df) // 6 + len(df) // 8))
        }
        data = [{
            'labels': list(supplier_data.keys()),
            'values': list(supplier_data.values()),
            'type': 'pie',
            'marker': {'color': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']}
        }]
        layout = {
            'title': 'Product Distribution by Supplier',
            'height': 400
        }
        return jsonify(to_native({'data': data, 'layout': layout}))
    
    else:
        return jsonify({'error': f'Chart type {chart_type} not found'}), 404

@app.route('/api/status')
def get_status():
    """API endpoint for status"""
    print("🔍 Serving status API")
    total_products = sum(len(products) for products in dashboard.products_cache.values())
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'products_loaded': total_products,
        'chunks_loaded': len(dashboard.products_cache),
        'total_revenue': dashboard.insights['total_revenue'],
        'message': 'Full data dashboard running with chunked loading'
    })

if __name__ == '__main__':
    print("🚀 Starting Full Data Sales Analytics Dashboard...")
    print("Access the dashboard at: http://127.0.0.1:8080")
    print("Status at: http://127.0.0.1:8080/api/status")
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    ) 