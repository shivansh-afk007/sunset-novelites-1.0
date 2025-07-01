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
warnings.filterwarnings('ignore')

app = Flask(__name__)

class PaginatedSalesDashboard:
    def __init__(self):
        self.insights = {}
        self.warehouse_insights = {}
        self.generate_summary_insights()
    
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
    
    def generate_summary_insights(self):
        """Generate summary insights from aggregated data (fast)"""
        try:
            # Get summary metrics from both databases
            synchub_conn = self.get_mysql_connection('synchub_data')
            acumatica_conn = self.get_mysql_connection('acumatica_data')
            
            total_revenue = 0
            total_units_sold = 0
            total_stock = 0
            total_products = 0
            
            # Synchub summary
            if synchub_conn:
                try:
                    # Fast aggregated queries
                    cursor = synchub_conn.cursor()
                    
                    # Total revenue from sales
                    cursor.execute("SELECT SUM(Total) FROM sale WHERE Total IS NOT NULL")
                    synchub_revenue = cursor.fetchone()[0] or 0
                    total_revenue += synchub_revenue
                    
                    # Total units sold from orderline
                    cursor.execute("SELECT SUM(Quantity) FROM orderline WHERE Quantity IS NOT NULL")
                    synchub_units = cursor.fetchone()[0] or 0
                    total_units_sold += synchub_units
                    
                    # Total stock from itemshop
                    cursor.execute("SELECT SUM(Qoh) FROM itemshop WHERE Qoh IS NOT NULL")
                    synchub_stock = cursor.fetchone()[0] or 0
                    total_stock += synchub_stock
                    
                    # Total products
                    cursor.execute("SELECT COUNT(*) FROM item WHERE Description IS NOT NULL")
                    synchub_products = cursor.fetchone()[0] or 0
                    total_products += synchub_products
                    
                    synchub_conn.close()
                    print(f"Synchub summary: ${synchub_revenue:,.2f} revenue, {synchub_units:,} units, {synchub_stock:,} stock")
                    
                except Exception as e:
                    print(f"Error getting Synchub summary: {e}")
            
            # Acumatica summary
            if acumatica_conn:
                try:
                    cursor = acumatica_conn.cursor()
                    
                    # Total revenue from sales
                    cursor.execute("SELECT SUM(ExtendedPrice) FROM salesorderdetail WHERE ExtendedPrice IS NOT NULL")
                    acumatica_revenue = cursor.fetchone()[0] or 0
                    total_revenue += acumatica_revenue
                    
                    # Total units sold
                    cursor.execute("SELECT SUM(OrderQty) FROM salesorderdetail WHERE OrderQty IS NOT NULL")
                    acumatica_units = cursor.fetchone()[0] or 0
                    total_units_sold += acumatica_units
                    
                    # Total products
                    cursor.execute("SELECT COUNT(*) FROM inventoryitem WHERE Descr IS NOT NULL")
                    acumatica_products = cursor.fetchone()[0] or 0
                    total_products += acumatica_products
                    
                    acumatica_conn.close()
                    print(f"Acumatica summary: ${acumatica_revenue:,.2f} revenue, {acumatica_units:,} units")
                    
                except Exception as e:
                    print(f"Error getting Acumatica summary: {e}")
            
            self.insights = {
                'total_revenue': float(total_revenue),
                'total_units_sold': int(total_units_sold),
                'total_stock_remaining': int(total_stock),
                'total_products': int(total_products),
                'avg_profit_margin': 75.0,  # Estimated
                'top_product': 'Loading...',
                'top_product_revenue': 0,
                'negative_margin_products': 0,
                'high_margin_products': int(total_products * 0.6)  # Estimated
            }
            
        except Exception as e:
            print(f"Error generating summary insights: {e}")
            self.insights = {
                'total_revenue': 0,
                'total_units_sold': 0,
                'total_stock_remaining': 0,
                'total_products': 0,
                'avg_profit_margin': 0,
                'top_product': '',
                'top_product_revenue': 0,
                'negative_margin_products': 0,
                'high_margin_products': 0
            }
    
    def get_paginated_products(self, page=1, page_size=50, source='all', category='all'):
        """Get paginated product data"""
        try:
            offset = (page - 1) * page_size
            
            # Build dynamic query based on filters
            where_conditions = []
            params = []
            
            if source != 'all':
                if source == 'synchub':
                    where_conditions.append("i.Description IS NOT NULL")
                elif source == 'acumatica':
                    where_conditions.append("i.Descr IS NOT NULL")
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Get data from both databases with pagination
            all_products = []
            
            # Synchub data
            if source in ['all', 'synchub']:
                synchub_conn = self.get_mysql_connection('synchub_data')
                if synchub_conn:
                    try:
                        synchub_query = f'''
                        SELECT 
                            i.Description,
                            i.RemoteID as `System ID`,
                            COALESCE(SUM(ol.Quantity), 0) as Sold,
                            COALESCE(MAX(is1.Qoh), 0) as Stock,
                            COALESCE(SUM(ol.Price * ol.Quantity), 0) as Subtotal,
                            0 as Discounts,
                            COALESCE(SUM(ol.Price * ol.Quantity), 0) as `Subtotal w/ Discounts`,
                            COALESCE(SUM(ol.Total), 0) as Total,
                            0 as Cost,
                            COALESCE(SUM(ol.Total), 0) as Profit,
                            100 as Margin,
                            'Lightspeed' as Source
                        FROM item i
                        LEFT JOIN orderline ol ON i.RemoteID = ol.ItemID
                        LEFT JOIN itemshop is1 ON i.RemoteID = is1.ItemID
                        WHERE {where_clause}
                        GROUP BY i.RemoteID, i.Description
                        ORDER BY Total DESC
                        LIMIT {page_size} OFFSET {offset}
                        '''
                        
                        synchub_df = pd.read_sql(synchub_query, synchub_conn)
                        synchub_conn.close()
                        
                        if not synchub_df.empty:
                            synchub_df['Category'] = self.categorize_products(synchub_df['Description'])
                            all_products.extend(synchub_df.to_dict('records'))
                            
                    except Exception as e:
                        print(f"Error loading Synchub paginated data: {e}")
            
            # Acumatica data
            if source in ['all', 'acumatica']:
                acumatica_conn = self.get_mysql_connection('acumatica_data')
                if acumatica_conn:
                    try:
                        acumatica_query = f'''
                        SELECT 
                            i.Descr as Description,
                            i.InventoryID as `System ID`,
                            COALESCE(SUM(sod.OrderQty), 0) as Sold,
                            0 as Stock,
                            COALESCE(SUM(sod.UnitPrice * sod.OrderQty), 0) as Subtotal,
                            COALESCE(SUM(sod.DiscountAmount), 0) as Discounts,
                            COALESCE(SUM(sod.UnitPrice * sod.OrderQty) - SUM(sod.DiscountAmount), 0) as `Subtotal w/ Discounts`,
                            COALESCE(SUM(sod.ExtendedPrice), 0) as Total,
                            0 as Cost,
                            COALESCE(SUM(sod.ExtendedPrice), 0) as Profit,
                            100 as Margin,
                            'Acumatica' as Source
                        FROM inventoryitem i
                        LEFT JOIN salesorderdetail sod ON i.InventoryID = sod.InventoryID
                        WHERE {where_clause}
                        GROUP BY i.InventoryID, i.Descr
                        ORDER BY Total DESC
                        LIMIT {page_size} OFFSET {offset}
                        '''
                        
                        acumatica_df = pd.read_sql(acumatica_query, acumatica_conn)
                        acumatica_conn.close()
                        
                        if not acumatica_df.empty:
                            acumatica_df['Category'] = self.categorize_products(acumatica_df['Description'])
                            all_products.extend(acumatica_df.to_dict('records'))
                            
                    except Exception as e:
                        print(f"Error loading Acumatica paginated data: {e}")
            
            return {
                'products': all_products,
                'page': page,
                'page_size': page_size,
                'total_loaded': len(all_products),
                'has_more': len(all_products) == page_size
            }
            
        except Exception as e:
            print(f"Error in paginated products: {e}")
            return {
                'products': [],
                'page': page,
                'page_size': page_size,
                'total_loaded': 0,
                'has_more': False
            }
    
    def get_top_products_summary(self, limit=20):
        """Get top products summary (fast query)"""
        try:
            all_products = []
            
            # Synchub top products
            synchub_conn = self.get_mysql_connection('synchub_data')
            if synchub_conn:
                try:
                    synchub_query = f'''
                    SELECT 
                        i.Description,
                        'Lightspeed' as Source,
                        COALESCE(SUM(ol.Quantity), 0) as Sold,
                        COALESCE(SUM(ol.Total), 0) as Total,
                        COALESCE(MAX(is1.Qoh), 0) as Stock
                    FROM item i
                    LEFT JOIN orderline ol ON i.RemoteID = ol.ItemID
                    LEFT JOIN itemshop is1 ON i.RemoteID = is1.ItemID
                    WHERE i.Description IS NOT NULL
                    GROUP BY i.RemoteID, i.Description
                    ORDER BY Total DESC
                    LIMIT {limit}
                    '''
                    
                    synchub_df = pd.read_sql(synchub_query, synchub_conn)
                    synchub_conn.close()
                    
                    if not synchub_df.empty:
                        synchub_df['Category'] = self.categorize_products(synchub_df['Description'])
                        all_products.extend(synchub_df.to_dict('records'))
                        
                except Exception as e:
                    print(f"Error loading Synchub top products: {e}")
            
            # Acumatica top products
            acumatica_conn = self.get_mysql_connection('acumatica_data')
            if acumatica_conn:
                try:
                    acumatica_query = f'''
                    SELECT 
                        i.Descr as Description,
                        'Acumatica' as Source,
                        COALESCE(SUM(sod.OrderQty), 0) as Sold,
                        COALESCE(SUM(sod.ExtendedPrice), 0) as Total,
                        0 as Stock
                    FROM inventoryitem i
                    LEFT JOIN salesorderdetail sod ON i.InventoryID = sod.InventoryID
                    WHERE i.Descr IS NOT NULL
                    GROUP BY i.InventoryID, i.Descr
                    ORDER BY Total DESC
                    LIMIT {limit}
                    '''
                    
                    acumatica_df = pd.read_sql(acumatica_query, acumatica_conn)
                    acumatica_conn.close()
                    
                    if not acumatica_df.empty:
                        acumatica_df['Category'] = self.categorize_products(acumatica_df['Description'])
                        all_products.extend(acumatica_df.to_dict('records'))
                        
                except Exception as e:
                    print(f"Error loading Acumatica top products: {e}")
            
            # Sort combined results and return top
            if all_products:
                df = pd.DataFrame(all_products)
                df = df.sort_values('Total', ascending=False).head(limit)
                return df.to_dict('records')
            
            return []
            
        except Exception as e:
            print(f"Error getting top products summary: {e}")
            return []
    
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
    
    def create_summary_chart(self, chart_type='revenue_by_category'):
        """Create summary charts using aggregated data"""
        try:
            if chart_type == 'revenue_by_category':
                # Get category revenue summary
                synchub_conn = self.get_mysql_connection('synchub_data')
                if synchub_conn:
                    cursor = synchub_conn.cursor()
                    cursor.execute("""
                        SELECT 
                            'Lightspeed' as Source,
                            COALESCE(SUM(ol.Total), 0) as Total_Revenue,
                            COUNT(DISTINCT i.RemoteID) as Product_Count
                        FROM item i
                        LEFT JOIN orderline ol ON i.RemoteID = ol.ItemID
                        WHERE i.Description IS NOT NULL
                    """)
                    synchub_summary = cursor.fetchone()
                    synchub_conn.close()
                    
                    # Create simple pie chart
                    fig = px.pie(
                        values=[synchub_summary[1] if synchub_summary else 0],
                        names=['Lightspeed Revenue'],
                        title="Revenue Distribution (Summary)"
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(title_x=0.5, title_font_size=16)
                    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
            return json.dumps({})
            
        except Exception as e:
            print(f"Error creating summary chart: {e}")
            return json.dumps({})

# Initialize dashboard
dashboard = PaginatedSalesDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard_pro.html')

@app.route('/api/metrics')
def get_metrics():
    """API endpoint for key metrics"""
    return jsonify(dashboard.insights)

@app.route('/api/data/products')
def get_paginated_products():
    """API endpoint for paginated products"""
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 50))
    source = request.args.get('source', 'all')
    category = request.args.get('category', 'all')
    
    return jsonify(dashboard.get_paginated_products(page, page_size, source, category))

@app.route('/api/data/top-products')
def get_top_products():
    """API endpoint for top products summary"""
    limit = int(request.args.get('limit', 20))
    return jsonify(dashboard.get_top_products_summary(limit))

@app.route('/api/charts/summary/<chart_type>')
def get_summary_chart(chart_type):
    """API endpoint for summary charts"""
    try:
        chart_data = dashboard.create_summary_chart(chart_type)
        return jsonify(json.loads(chart_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Paginated Sales Analytics Dashboard...")
    print("Access the dashboard at: http://127.0.0.1:8080")
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    ) 