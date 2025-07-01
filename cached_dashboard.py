from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json
import numpy as np
from datetime import datetime, timedelta
import warnings
import mysql.connector
from sqlalchemy import create_engine, text
import threading
import time
warnings.filterwarnings('ignore')

app = Flask(__name__)

class CachedSalesDashboard:
    def __init__(self):
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_duration = 300  # 5 minutes
        self.lock = threading.Lock()
        
        # Initialize cache with key metrics
        self.refresh_cache()
        
        # Start background cache refresh
        self.start_cache_refresh_thread()
    
    def get_cache_key(self, data_type, **kwargs):
        """Generate cache key for data type and parameters"""
        key_parts = [data_type]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}_{v}")
        return "_".join(key_parts)
    
    def is_cache_valid(self, cache_key):
        """Check if cache is still valid"""
        if cache_key not in self.cache_timestamps:
            return False
        
        age = time.time() - self.cache_timestamps[cache_key]
        return age < self.cache_duration
    
    def get_cached_data(self, cache_key):
        """Get data from cache if valid"""
        with self.lock:
            if self.is_cache_valid(cache_key):
                return self.cache.get(cache_key)
        return None
    
    def set_cached_data(self, cache_key, data):
        """Store data in cache"""
        with self.lock:
            self.cache[cache_key] = data
            self.cache_timestamps[cache_key] = time.time()
    
    def get_mysql_connection(self, database):
        """Get MySQL connection for specified database"""
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database=database,
                connect_timeout=5
            )
            return connection
        except Exception as e:
            print(f"Error connecting to MySQL database {database}: {e}")
            return None
    
    def refresh_cache(self):
        """Refresh all cached data"""
        print("🔄 Refreshing dashboard cache...")
        
        # Cache key metrics
        self.cache_key_metrics()
        
        # Cache top products
        self.cache_top_products()
        
        # Cache category summary
        self.cache_category_summary()
        
        # Cache warehouse data
        self.cache_warehouse_data()
        
        print("✅ Cache refresh complete")
    
    def cache_key_metrics(self):
        """Cache key performance metrics"""
        try:
            total_revenue = 0
            total_units_sold = 0
            total_stock = 0
            total_products = 0
            
            # Synchub metrics
            synchub_conn = self.get_mysql_connection('synchub_data')
            if synchub_conn:
                cursor = synchub_conn.cursor()
                
                cursor.execute("SELECT SUM(Total) FROM sale WHERE Total IS NOT NULL")
                synchub_revenue = cursor.fetchone()[0] or 0
                total_revenue += synchub_revenue
                
                cursor.execute("SELECT SUM(Quantity) FROM orderline WHERE Quantity IS NOT NULL")
                synchub_units = cursor.fetchone()[0] or 0
                total_units_sold += synchub_units
                
                cursor.execute("SELECT SUM(Qoh) FROM itemshop WHERE Qoh IS NOT NULL")
                synchub_stock = cursor.fetchone()[0] or 0
                total_stock += synchub_stock
                
                cursor.execute("SELECT COUNT(*) FROM item WHERE Description IS NOT NULL")
                synchub_products = cursor.fetchone()[0] or 0
                total_products += synchub_products
                
                synchub_conn.close()
            
            # Acumatica metrics
            acumatica_conn = self.get_mysql_connection('acumatica_data')
            if acumatica_conn:
                cursor = acumatica_conn.cursor()
                
                cursor.execute("SELECT SUM(ExtendedPrice) FROM salesorderdetail WHERE ExtendedPrice IS NOT NULL")
                acumatica_revenue = cursor.fetchone()[0] or 0
                total_revenue += acumatica_revenue
                
                cursor.execute("SELECT SUM(OrderQty) FROM salesorderdetail WHERE OrderQty IS NOT NULL")
                acumatica_units = cursor.fetchone()[0] or 0
                total_units_sold += acumatica_units
                
                cursor.execute("SELECT COUNT(*) FROM inventoryitem WHERE Descr IS NOT NULL")
                acumatica_products = cursor.fetchone()[0] or 0
                total_products += acumatica_products
                
                acumatica_conn.close()
            
            metrics = {
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
            
            self.set_cached_data('key_metrics', metrics)
            
        except Exception as e:
            print(f"Error caching key metrics: {e}")
    
    def cache_top_products(self, limit=100):
        """Cache top products data"""
        try:
            all_products = []
            
            # Synchub top products
            synchub_conn = self.get_mysql_connection('synchub_data')
            if synchub_conn:
                synchub_query = f"""
                SELECT 
                    i.Description,
                    'Lightspeed' as Source,
                    COALESCE(SUM(ol.Quantity), 0) as Sold,
                    COALESCE(SUM(ol.Total), 0) as Total,
                    COALESCE(MAX(is1.Qoh), 0) as Stock,
                    100 as Margin
                FROM item i
                LEFT JOIN orderline ol ON i.RemoteID = ol.ItemID
                LEFT JOIN itemshop is1 ON i.RemoteID = is1.ItemID
                WHERE i.Description IS NOT NULL
                GROUP BY i.RemoteID, i.Description
                ORDER BY Total DESC
                LIMIT {limit}
                """
                
                synchub_df = pd.read_sql(synchub_query, synchub_conn)
                synchub_conn.close()
                
                if not synchub_df.empty:
                    synchub_df['Category'] = self.categorize_products(synchub_df['Description'])
                    all_products.extend(synchub_df.to_dict('records'))
            
            # Acumatica top products
            acumatica_conn = self.get_mysql_connection('acumatica_data')
            if acumatica_conn:
                acumatica_query = f"""
                SELECT 
                    i.Descr as Description,
                    'Acumatica' as Source,
                    COALESCE(SUM(sod.OrderQty), 0) as Sold,
                    COALESCE(SUM(sod.ExtendedPrice), 0) as Total,
                    0 as Stock,
                    100 as Margin
                FROM inventoryitem i
                LEFT JOIN salesorderdetail sod ON i.InventoryID = sod.InventoryID
                WHERE i.Descr IS NOT NULL
                GROUP BY i.InventoryID, i.Descr
                ORDER BY Total DESC
                LIMIT {limit}
                """
                
                acumatica_df = pd.read_sql(acumatica_query, acumatica_conn)
                acumatica_conn.close()
                
                if not acumatica_df.empty:
                    acumatica_df['Category'] = self.categorize_products(acumatica_df['Description'])
                    all_products.extend(acumatica_df.to_dict('records'))
            
            # Sort and store
            if all_products:
                df = pd.DataFrame(all_products)
                df = df.sort_values('Total', ascending=False).head(limit)
                self.set_cached_data('top_products', df.to_dict('records'))
            
        except Exception as e:
            print(f"Error caching top products: {e}")
    
    def cache_category_summary(self):
        """Cache category summary data"""
        try:
            # Get cached top products
            top_products = self.get_cached_data('top_products')
            if top_products:
                df = pd.DataFrame(top_products)
                category_summary = df.groupby('Category').agg({
                    'Total': ['sum', 'count'],
                    'Margin': 'mean',
                    'Sold': 'sum',
                    'Stock': 'sum'
                }).round(2)
                
                # Flatten column names
                category_summary.columns = ['_'.join(col).strip() for col in category_summary.columns]
                self.set_cached_data('category_summary', category_summary.to_dict('index'))
            
        except Exception as e:
            print(f"Error caching category summary: {e}")
    
    def cache_warehouse_data(self):
        """Cache warehouse data"""
        try:
            warehouse_data = []
            
            # Synchub warehouse data
            synchub_conn = self.get_mysql_connection('synchub_data')
            if synchub_conn:
                warehouse_query = """
                SELECT 
                    i.RemoteID as Product_ID,
                    i.Description as Product_Name,
                    COALESCE(MAX(is1.Qoh), 0) as Current_Stock,
                    COALESCE(MAX(is1.ReorderPoint), 0) as Reorder_Point,
                    0 as Lead_Time_Days
                FROM item i
                LEFT JOIN itemshop is1 ON i.RemoteID = is1.ItemID
                WHERE i.Description IS NOT NULL
                GROUP BY i.RemoteID, i.Description
                ORDER BY Current_Stock ASC
                LIMIT 100
                """
                
                synchub_warehouse = pd.read_sql(warehouse_query, synchub_conn)
                synchub_conn.close()
                
                for _, row in synchub_warehouse.iterrows():
                    warehouse_data.append({
                        'Product_ID': row['Product_ID'],
                        'Product_Name': row['Product_Name'],
                        'Category': 'Unknown',
                        'Current_Stock': row['Current_Stock'],
                        'Reorder_Point': row['Reorder_Point'],
                        'Lead_Time_Days': row['Lead_Time_Days'],
                        'Safety_Stock': 0,
                        'Max_Stock': row['Reorder_Point'] * 3,
                        'Warehouse_Location': 'Main',
                        'Supplier': 'Unknown',
                        'Last_Updated': datetime.now().strftime('%Y-%m-%d'),
                        'Stock_Status': 'Low' if row['Current_Stock'] <= row['Reorder_Point'] else 'Adequate',
                        'Restock_Needed': row['Current_Stock'] <= row['Reorder_Point'],
                        'Days_Until_Stockout': 999,
                        'Monthly_Demand': 0,
                        'Annual_Demand': 0,
                        'Stock_Turnover': 0
                    })
            
            self.set_cached_data('warehouse_data', warehouse_data)
            
        except Exception as e:
            print(f"Error caching warehouse data: {e}")
    
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
    
    def start_cache_refresh_thread(self):
        """Start background thread to refresh cache periodically"""
        def refresh_loop():
            while True:
                time.sleep(self.cache_duration)
                self.refresh_cache()
        
        refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        refresh_thread.start()
        print(f"🔄 Cache refresh thread started (every {self.cache_duration} seconds)")

# Initialize dashboard
dashboard = CachedSalesDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard_pro.html')

@app.route('/api/metrics')
def get_metrics():
    """API endpoint for key metrics"""
    metrics = dashboard.get_cached_data('key_metrics')
    if metrics is None:
        dashboard.cache_key_metrics()
        metrics = dashboard.get_cached_data('key_metrics')
    return jsonify(metrics)

@app.route('/api/data/top-products')
def get_top_products():
    """API endpoint for top products"""
    products = dashboard.get_cached_data('top_products')
    if products is None:
        dashboard.cache_top_products()
        products = dashboard.get_cached_data('top_products')
    return jsonify(products)

@app.route('/api/data/category-summary')
def get_category_summary():
    """API endpoint for category summary"""
    summary = dashboard.get_cached_data('category_summary')
    if summary is None:
        dashboard.cache_category_summary()
        summary = dashboard.get_cached_data('category_summary')
    return jsonify(summary)

@app.route('/api/data/warehouse-data')
def get_warehouse_data():
    """API endpoint for warehouse data"""
    warehouse_data = dashboard.get_cached_data('warehouse_data')
    if warehouse_data is None:
        dashboard.cache_warehouse_data()
        warehouse_data = dashboard.get_cached_data('warehouse_data')
    return jsonify(warehouse_data)

@app.route('/api/refresh-cache')
def refresh_cache():
    """API endpoint to manually refresh cache"""
    dashboard.refresh_cache()
    return jsonify({'status': 'Cache refreshed successfully'})

if __name__ == '__main__':
    print("Starting Cached Sales Analytics Dashboard...")
    print("Access the dashboard at: http://127.0.0.1:8080")
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    ) 