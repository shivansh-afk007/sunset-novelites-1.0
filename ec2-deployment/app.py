from flask import Flask, render_template, jsonify
import mysql.connector
import pandas as pd
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Database configuration
RDS_CONFIG = {
    'host': 'acumatica-rdspy.cda28gcg8vir.eu-north-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Sunset2024!',
    'port': 3306,
    'charset': 'utf8mb4',
    'autocommit': True,
    'pool_name': 'mypool',
    'pool_size': 5
}

class DashboardData:
    def __init__(self):
        self.rds_config = RDS_CONFIG
        
    def get_mysql_connection(self, database):
        """Get MySQL connection for specified database"""
        try:
            connection = mysql.connector.connect(
                **self.rds_config,
                database=database
            )
            return connection
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL database {database}: {e}")
            return None

    def load_dashboard_data(self):
        """Load and prepare the data from MySQL databases"""
        try:
            # Load Lightspeed data
            synchub_conn = self.get_mysql_connection('synchub_data')
            if synchub_conn:
                synchub_query = """
                SELECT 
                    p.productID,
                    p.name as product_name,
                    p.sku,
                    p.qoh as stock_quantity,
                    p.cost as cost_price,
                    p.price as selling_price,
                    p.categoryID,
                    c.name as category_name
                FROM products p
                LEFT JOIN categories c ON p.categoryID = c.categoryID
                WHERE p.qoh > 0
                ORDER BY p.qoh ASC
                LIMIT 1000
                """
                synchub_df = pd.read_sql(synchub_query, synchub_conn)
                synchub_conn.close()
            else:
                synchub_df = pd.DataFrame()

            # Load Acumatica data
            acumatica_conn = self.get_mysql_connection('acumatica_data')
            if acumatica_conn:
                acumatica_query = """
                SELECT 
                    p.InventoryID,
                    p.Description as product_name,
                    p.InventoryCD as sku,
                    p.QtyOnHand as stock_quantity,
                    p.BasePrice as cost_price,
                    p.SalesPrice as selling_price,
                    p.ItemClass as category_name
                FROM InventoryItem p
                WHERE p.QtyOnHand > 0
                ORDER BY p.QtyOnHand ASC
                LIMIT 1000
                """
                acumatica_df = pd.read_sql(acumatica_query, acumatica_conn)
                acumatica_conn.close()
            else:
                acumatica_df = pd.DataFrame()

            return synchub_df, acumatica_df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame(), pd.DataFrame()

    def calculate_metrics(self, synchub_df, acumatica_df):
        """Calculate dashboard metrics"""
        try:
            # Combine data
            all_products = []
            
            if not synchub_df.empty:
                synchub_products = synchub_df.to_dict('records')
                for product in synchub_products:
                    product['source'] = 'Lightspeed'
                    all_products.append(product)
            
            if not acumatica_df.empty:
                acumatica_products = acumatica_df.to_dict('records')
                for product in acumatica_products:
                    product['source'] = 'Acumatica'
                    all_products.append(product)

            if not all_products:
                return {
                    'total_products': 0,
                    'total_stock': 0,
                    'total_value': 0,
                    'low_stock_count': 0,
                    'categories': [],
                    'top_products': [],
                    'stock_distribution': []
                }

            # Calculate metrics
            total_products = len(all_products)
            total_stock = sum(p.get('stock_quantity', 0) for p in all_products)
            total_value = sum(p.get('stock_quantity', 0) * p.get('cost_price', 0) for p in all_products)
            low_stock_count = len([p for p in all_products if p.get('stock_quantity', 0) < 10])

            # Category analysis
            categories = {}
            for product in all_products:
                category = product.get('category_name', 'Unknown')
                if category not in categories:
                    categories[category] = {'count': 0, 'stock': 0, 'value': 0}
                categories[category]['count'] += 1
                categories[category]['stock'] += product.get('stock_quantity', 0)
                categories[category]['value'] += product.get('stock_quantity', 0) * product.get('cost_price', 0)

            # Top products by stock
            top_products = sorted(all_products, key=lambda x: x.get('stock_quantity', 0), reverse=True)[:10]

            return {
                'total_products': total_products,
                'total_stock': total_stock,
                'total_value': round(total_value, 2),
                'low_stock_count': low_stock_count,
                'categories': [{'name': k, **v} for k, v in categories.items()],
                'top_products': top_products,
                'stock_distribution': [
                    {'range': '0-10', 'count': len([p for p in all_products if 0 <= p.get('stock_quantity', 0) <= 10])},
                    {'range': '11-50', 'count': len([p for p in all_products if 11 <= p.get('stock_quantity', 0) <= 50])},
                    {'range': '51-100', 'count': len([p for p in all_products if 51 <= p.get('stock_quantity', 0) <= 100])},
                    {'range': '100+', 'count': len([p for p in all_products if p.get('stock_quantity', 0) > 100])}
                ]
            }
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return {
                'total_products': 0,
                'total_stock': 0,
                'total_value': 0,
                'low_stock_count': 0,
                'categories': [],
                'top_products': [],
                'stock_distribution': []
            }

# Initialize dashboard
dashboard = DashboardData()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    """API endpoint for dashboard metrics"""
    try:
        synchub_df, acumatica_df = dashboard.load_dashboard_data()
        metrics = dashboard.calculate_metrics(synchub_df, acumatica_df)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 