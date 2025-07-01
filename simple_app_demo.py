from flask import Flask, render_template, jsonify
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

class SimpleSalesDashboard:
    def __init__(self):
        self.df = None
        self.warehouse_df = None
        self.insights = {}
        self.warehouse_insights = {}
        self.create_sample_data()
        self.create_sample_warehouse_data()
        self.generate_insights()
        self.generate_warehouse_insights()
    
    def create_sample_data(self):
        """Create sample data for demonstration"""
        print("Creating sample sales data for demonstration...")
        
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
        
        np.random.seed(42)  # For reproducible results
        n_products = len(sample_products)
        
        sample_data = []
        for i, product in enumerate(sample_products):
            category = categories[i % len(categories)]
            sold = np.random.randint(10, 500)
            stock = np.random.randint(0, 200)
            price = np.random.uniform(20, 150)
            margin = np.random.uniform(20, 80)
            cost = price * (1 - margin/100)
            total = sold * price
            
            sample_data.append({
                'Description': product,
                'System ID': f"PROD{i+1:03d}",
                'Sold': sold,
                'Stock': stock,
                'Subtotal': total,
                'Discounts': total * 0.05,
                'Subtotal w/ Discounts': total * 0.95,
                'Total': total * 0.95,
                'Cost': cost * sold,
                'Profit': total * 0.95 - (cost * sold),
                'Margin': margin,
                'Category': category,
                'Source': 'Sample Data'
            })
        
        self.df = pd.DataFrame(sample_data)
        print(f"Created {len(self.df)} sample products")
    
    def create_sample_warehouse_data(self):
        """Create sample warehouse data"""
        print("Creating sample warehouse data...")
        
        warehouse_products = [
            "Premium Vibrator Deluxe", "Rhino Male Enhancement", "Silky Lube Gel", 
            "Lace Lingerie Set", "Adult Toy Collection", "Battery Charger Kit",
            "Wand Massager Pro", "Mood Enhancement Pills", "Leather Restraints",
            "Silicone Dildo Set", "Lubricant Oil", "Stockings & Garters"
        ]
        
        categories = ['Vibrators', 'Supplements', 'Lubricants', 'Clothing & Accessories', 
                     'Adult Toys', 'Accessories']
        
        np.random.seed(42)
        warehouse_data = []
        
        for i, product in enumerate(warehouse_products):
            category = categories[i % len(categories)]
            current_stock = np.random.randint(0, 100)
            reorder_point = np.random.randint(10, 30)
            lead_time = np.random.randint(3, 14)
            
            warehouse_data.append({
                'Product_ID': f"PROD{i+1:03d}",
                'Product_Name': product,
                'Category': category,
                'Current_Stock': current_stock,
                'Reorder_Point': reorder_point,
                'Lead_Time_Days': lead_time,
                'Safety_Stock': reorder_point * 0.5,
                'Max_Stock': reorder_point * 3,
                'Warehouse_Location': f"Zone {chr(65 + (i % 5))}",
                'Supplier': f"Supplier {i % 4 + 1}",
                'Last_Updated': datetime.now().strftime('%Y-%m-%d'),
                'Stock_Status': 'Low' if current_stock <= reorder_point else 'Adequate',
                'Restock_Needed': current_stock <= reorder_point,
                'Days_Until_Stockout': max(1, np.random.randint(1, 30)),
                'Monthly_Demand': np.random.randint(50, 200),
                'Annual_Demand': np.random.randint(500, 2000),
                'Stock_Turnover': np.random.uniform(2, 8)
            })
        
        self.warehouse_df = pd.DataFrame(warehouse_data)
        print(f"Created {len(self.warehouse_df)} warehouse products")
    
    def generate_insights(self):
        """Generate key insights from the data"""
        if self.df is None or self.df.empty:
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
            return
        
        self.insights = {
            'total_revenue': float(self.df['Total'].sum()),
            'total_units_sold': int(self.df['Sold'].sum()),
            'total_stock_remaining': int(self.df['Stock'].sum()),
            'total_products': int(len(self.df)),
            'avg_profit_margin': float(self.df['Margin'].mean()),
            'top_product': str(self.df.loc[self.df['Total'].idxmax(), 'Description']),
            'top_product_revenue': float(self.df['Total'].max()),
            'negative_margin_products': int(len(self.df[self.df['Margin'] < 0])),
            'high_margin_products': int(len(self.df[self.df['Margin'] > 50]))
        }
    
    def generate_warehouse_insights(self):
        """Generate warehouse-specific insights"""
        if self.warehouse_df is None or len(self.warehouse_df) == 0:
            self.warehouse_insights = {
                'total_products': 0,
                'total_current_stock': 0,
                'products_needing_restock': 0,
                'low_stock_products': 0,
                'overstocked_products': 0,
                'avg_lead_time': 0.0,
                'total_safety_stock': 0,
                'avg_stock_turnover': 0.0,
                'warehouse_locations': 0,
                'suppliers': 0,
                'critical_stock_products': 0
            }
            return
        
        self.warehouse_insights = {
            'total_products': int(len(self.warehouse_df)),
            'total_current_stock': int(self.warehouse_df['Current_Stock'].sum()),
            'products_needing_restock': int(len(self.warehouse_df[self.warehouse_df['Restock_Needed'] == True])),
            'low_stock_products': int(len(self.warehouse_df[self.warehouse_df['Stock_Status'] == 'Low'])),
            'overstocked_products': int(len(self.warehouse_df[self.warehouse_df['Stock_Status'] == 'Overstocked'])),
            'avg_lead_time': float(self.warehouse_df['Lead_Time_Days'].mean()),
            'total_safety_stock': int(self.warehouse_df['Safety_Stock'].sum()),
            'avg_stock_turnover': float(self.warehouse_df['Stock_Turnover'].mean()),
            'warehouse_locations': int(self.warehouse_df['Warehouse_Location'].nunique()),
            'suppliers': int(self.warehouse_df['Supplier'].nunique()),
            'critical_stock_products': int(len(self.warehouse_df[self.warehouse_df['Days_Until_Stockout'] <= 7]))
        }
    
    def get_top_products_data(self):
        """Get top products data for table"""
        if self.df.empty:
            return pd.DataFrame()
        return self.df.nlargest(20, 'Total')[['Description', 'Category', 'Sold', 'Stock', 'Total', 'Margin', 'Profit', 'Source']].round(2)
    
    def get_negative_margin_data(self):
        """Get negative margin products data"""
        if self.df.empty:
            return pd.DataFrame()
        return self.df[self.df['Margin'] < 0][['Description', 'Category', 'Sold', 'Stock', 'Total', 'Margin', 'Cost', 'Source']].round(2)
    
    def get_category_summary(self):
        """Get category summary data"""
        if self.df.empty:
            return pd.DataFrame()
            
        category_summary = self.df.groupby('Category').agg({
            'Total': ['sum', 'count'],
            'Margin': 'mean',
            'Sold': 'sum',
            'Stock': 'sum',
            'Cost': 'sum',
            'Profit': 'sum'
        }).round(2)
        
        # Flatten column names
        category_summary.columns = ['_'.join(col).strip() for col in category_summary.columns]
        return category_summary
    
    def get_warehouse_summary(self):
        """Get warehouse summary data"""
        if self.warehouse_df is not None and len(self.warehouse_df) > 0:
            warehouse_summary = self.warehouse_df.groupby('Category').agg({
                'Current_Stock': ['sum', 'mean'],
                'Reorder_Point': 'sum',
                'Safety_Stock': 'sum',
                'Lead_Time_Days': 'mean',
                'Restock_Needed': 'sum',
                'Stock_Turnover': 'mean'
            }).round(2)
            
            # Flatten column names
            warehouse_summary.columns = ['_'.join(col).strip() for col in warehouse_summary.columns]
            
            # Convert to dictionary and handle NaN values
            summary_dict = warehouse_summary.to_dict('index')
            for category in summary_dict:
                for key, value in summary_dict[category].items():
                    if pd.isna(value):
                        summary_dict[category][key] = 0
                    elif isinstance(value, (int, float)):
                        summary_dict[category][key] = float(value)
            
            return summary_dict
        return {}
    
    def get_restock_alerts(self):
        """Get top 15 products that need restocking"""
        if self.warehouse_df is not None and len(self.warehouse_df) > 0:
            restock_alerts = self.warehouse_df[self.warehouse_df['Restock_Needed'] == True].copy()
            
            # Sort by urgency and take top 15
            restock_alerts = restock_alerts.sort_values('Days_Until_Stockout', ascending=True)
            restock_alerts = restock_alerts.head(15)[
                ['Product_Name', 'Category', 'Current_Stock', 'Reorder_Point', 'Lead_Time_Days', 'Days_Until_Stockout', 'Supplier']
            ].round(2)
            
            # Convert to records and handle NaN values
            records = restock_alerts.to_dict('records')
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        if isinstance(value, str):
                            record[key] = ""
                        else:
                            record[key] = 0
                    elif isinstance(value, (int, float)):
                        record[key] = float(value)
            
            return records
        return []
    
    def get_warehouse_locations(self):
        """Get warehouse location summary"""
        if self.warehouse_df is not None and len(self.warehouse_df) > 0:
            location_summary = self.warehouse_df.groupby('Warehouse_Location').agg({
                'Current_Stock': 'sum',
                'Product_Name': 'count',
                'Restock_Needed': 'sum'
            }).round(2)
            location_summary.columns = ['Total_Stock', 'Product_Count', 'Restock_Needed']
            
            # Convert to dictionary and handle NaN values
            location_dict = location_summary.to_dict('index')
            for location in location_dict:
                for key, value in location_dict[location].items():
                    if pd.isna(value):
                        location_dict[location][key] = 0
                    elif isinstance(value, (int, float)):
                        location_dict[location][key] = float(value)
            
            return location_dict
        return {}
    
    # Chart creation methods (same as original)
    def create_margin_distribution_chart(self):
        """Create margin distribution histogram"""
        if self.df.empty:
            return json.dumps({})
            
        fig = px.histogram(
            self.df,
            x='Margin',
            nbins=30,
            title="Profit Margin Distribution",
            labels={'Margin': 'Profit Margin (%)', 'count': 'Number of Products'},
            color_discrete_sequence=['#667eea']
        )
        fig.add_vline(x=self.df['Margin'].mean(), line_dash="dash", line_color="red",
                     annotation_text=f"Mean: {self.df['Margin'].mean():.1f}%")
        fig.update_layout(
            title_x=0.5,
            title_font_size=16,
            showlegend=False
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_revenue_by_category_chart(self):
        """Create revenue distribution by category"""
        if self.df.empty:
            return json.dumps({})
            
        category_revenue = self.df.groupby('Category')['Total'].sum().sort_values(ascending=False)
        fig = px.pie(
            values=category_revenue.values,
            names=category_revenue.index,
            title="Revenue Distribution by Category"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            title_x=0.5,
            title_font_size=16
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_top_products_chart(self):
        """Create top products by revenue chart"""
        if self.df.empty:
            return json.dumps({})
            
        top_products = self.df.nlargest(10, 'Total')
        fig = px.bar(
            top_products,
            x='Total',
            y='Description',
            orientation='h',
            title="Top 10 Products by Revenue",
            color='Category',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            title_x=0.5,
            title_font_size=16,
            yaxis={'categoryorder':'total ascending'}
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_stock_vs_sales_chart(self):
        """Create stock vs sales scatter plot"""
        if self.df.empty:
            return json.dumps({})
            
        # Filter out negative values and use absolute values for size
        df_filtered = self.df.copy()
        df_filtered['Total_abs'] = df_filtered['Total'].abs()
        
        fig = px.scatter(
            df_filtered,
            x='Sold',
            y='Stock',
            color='Category',
            size='Total_abs',
            hover_data=['Description'],
            title="Stock vs Sales Analysis (Size = Revenue)",
            labels={'Sold': 'Units Sold', 'Stock': 'Stock Remaining', 'Total_abs': 'Revenue ($)'}
        )
        fig.update_layout(
            title_x=0.5,
            title_font_size=16
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_profit_margin_by_category_chart(self):
        """Create average profit margin by category"""
        if self.df.empty:
            return json.dumps({})
            
        category_margins = self.df.groupby('Category')['Margin'].mean().sort_values(ascending=False)
        fig = px.bar(
            x=category_margins.index,
            y=category_margins.values,
            title="Average Profit Margin by Category",
            labels={'x': 'Category', 'y': 'Average Profit Margin (%)'},
            color=category_margins.values,
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(
            title_x=0.5,
            title_font_size=16,
            showlegend=False
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_revenue_vs_margin_chart(self):
        """Create revenue vs margin scatter plot"""
        if self.df.empty:
            return json.dumps({})
            
        # Filter out negative values and use absolute values for size
        df_filtered = self.df.copy()
        df_filtered['Sold_abs'] = df_filtered['Sold'].abs()
        
        fig = px.scatter(
            df_filtered,
            x='Margin',
            y='Total',
            color='Category',
            size='Sold_abs',
            hover_data=['Description'],
            title="Revenue vs Profit Margin (Size = Units Sold)",
            labels={'Margin': 'Profit Margin (%)', 'Total': 'Revenue ($)', 'Sold_abs': 'Units Sold'}
        )
        fig.update_layout(
            title_x=0.5,
            title_font_size=16
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_category_performance_chart(self):
        """Create category performance comparison"""
        if self.df.empty:
            return json.dumps({})
            
        category_metrics = self.df.groupby('Category').agg({
            'Total': 'sum',
            'Sold': 'sum',
            'Stock': 'sum',
            'Margin': 'mean'
        }).round(2)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=category_metrics.index,
            y=category_metrics['Total'],
            name='Revenue',
            yaxis='y'
        ))
        fig.add_trace(go.Bar(
            x=category_metrics.index,
            y=category_metrics['Sold'],
            name='Units Sold',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Category Performance Comparison",
            title_x=0.5,
            title_font_size=16,
            yaxis=dict(title="Revenue ($)"),
            yaxis2=dict(title="Units Sold", overlaying="y", side="right"),
            barmode='group'
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Warehouse-specific charts
    def create_warehouse_stock_status_chart(self):
        """Create warehouse stock status chart"""
        if self.warehouse_df is not None and len(self.warehouse_df) > 0:
            stock_status = self.warehouse_df['Stock_Status'].value_counts()
            fig = px.pie(
                values=stock_status.values,
                names=stock_status.index,
                title="Warehouse Stock Status Distribution",
                color_discrete_sequence=['#ef4444', '#10b981', '#f59e0b']
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                title_x=0.5,
                title_font_size=16
            )
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return json.dumps({})
    
    def create_warehouse_location_chart(self):
        """Create warehouse location chart"""
        if self.warehouse_df is not None and len(self.warehouse_df) > 0:
            location_data = self.warehouse_df.groupby('Warehouse_Location').agg({
                'Current_Stock': 'sum',
                'Product_Name': 'count'
            }).reset_index()
            
            fig = px.bar(
                location_data,
                x='Warehouse_Location',
                y='Current_Stock',
                title="Warehouse Locations by Stock",
                labels={'Current_Stock': 'Total Stock', 'Warehouse_Location': 'Location'},
                color='Product_Name',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                title_x=0.5,
                title_font_size=16,
                height=500
            )
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return json.dumps({})
    
    def create_restock_urgency_chart(self):
        """Create restock urgency chart"""
        if self.warehouse_df is not None and len(self.warehouse_df) > 0:
            restock_data = self.warehouse_df[self.warehouse_df['Restock_Needed'] == True].copy()
            
            # Sort by urgency and take top 15
            restock_data = restock_data.sort_values('Days_Until_Stockout', ascending=True).head(15)
            
            # Truncate product names for better display
            restock_data['Product_Name_Short'] = restock_data['Product_Name'].str[:30] + '...'
            
            fig = px.bar(
                restock_data,
                x='Days_Until_Stockout',
                y='Product_Name_Short',
                orientation='h',
                title="Top 15 Restock Alerts",
                labels={'Days_Until_Stockout': 'Days Until Stockout', 'Product_Name_Short': 'Product'},
                color='Current_Stock',
                color_continuous_scale='Reds',
                hover_data=['Product_Name', 'Category', 'Current_Stock']
            )
            fig.update_layout(
                title_x=0.5,
                title_font_size=16,
                yaxis={'categoryorder':'total ascending'},
                height=600
            )
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return json.dumps({})
    
    def create_supplier_analysis_chart(self):
        """Create supplier analysis chart"""
        if self.warehouse_df is not None and len(self.warehouse_df) > 0:
            supplier_data = self.warehouse_df.groupby('Supplier').agg({
                'Current_Stock': 'sum',
                'Product_Name': 'count',
                'Lead_Time_Days': 'mean',
                'Restock_Needed': 'sum'
            }).round(2)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=supplier_data.index,
                y=supplier_data['Current_Stock'],
                name='Total Stock',
                yaxis='y'
            ))
            fig.add_trace(go.Bar(
                x=supplier_data.index,
                y=supplier_data['Restock_Needed'],
                name='Products Needing Restock',
                yaxis='y'
            ))
            
            fig.update_layout(
                title="Supplier Analysis",
                title_x=0.5,
                title_font_size=16,
                yaxis=dict(title="Count"),
                barmode='group',
                height=500
            )
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return json.dumps({})

# Initialize dashboard
dashboard = SimpleSalesDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard_pro.html')

@app.route('/api/metrics')
def get_metrics():
    """API endpoint for key metrics"""
    return jsonify(dashboard.insights)

@app.route('/api/warehouse/metrics')
def get_warehouse_metrics():
    """API endpoint for warehouse metrics"""
    return jsonify(dashboard.warehouse_insights)

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

@app.route('/api/data/warehouse-summary')
def get_warehouse_summary_data():
    """API endpoint for warehouse summary data"""
    return jsonify(dashboard.get_warehouse_summary())

@app.route('/api/data/restock-alerts')
def get_restock_alerts_data():
    """API endpoint for restock alerts data"""
    return jsonify(dashboard.get_restock_alerts())

@app.route('/api/data/warehouse-locations')
def get_warehouse_locations_data():
    """API endpoint for warehouse locations data"""
    return jsonify(dashboard.get_warehouse_locations())

@app.route('/api/charts/margin-distribution')
def get_margin_distribution_chart():
    """API endpoint for margin distribution chart"""
    try:
        chart_data = dashboard.create_margin_distribution_chart()
        return jsonify(json.loads(chart_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/revenue-by-category')
def get_revenue_by_category_chart():
    """API endpoint for revenue by category chart"""
    try:
        chart_data = dashboard.create_revenue_by_category_chart()
        return jsonify(json.loads(chart_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/top-products-chart')
def get_top_products_chart():
    """API endpoint for top products chart"""
    try:
        chart_data = dashboard.create_top_products_chart()
        return jsonify(json.loads(chart_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/stock-vs-sales')
def get_stock_vs_sales_chart():
    """API endpoint for stock vs sales chart"""
    try:
        chart_data = dashboard.create_stock_vs_sales_chart()
        return jsonify(json.loads(chart_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/profit-margin-by-category')
def get_profit_margin_by_category_chart():
    """API endpoint for profit margin by category chart"""
    try:
        chart_data = dashboard.create_profit_margin_by_category_chart()
        return jsonify(json.loads(chart_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/revenue-vs-margin')
def get_revenue_vs_margin_chart():
    """API endpoint for revenue vs margin chart"""
    try:
        chart_data = dashboard.create_revenue_vs_margin_chart()
        return jsonify(json.loads(chart_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/category-performance')
def get_category_performance_chart():
    """API endpoint for category performance chart"""
    try:
        chart_data = dashboard.create_category_performance_chart()
        return jsonify(json.loads(chart_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Warehouse chart endpoints
@app.route('/api/charts/warehouse-stock-status')
def get_warehouse_stock_status_chart():
    """API endpoint for warehouse stock status chart"""
    try:
        chart_data = dashboard.create_warehouse_stock_status_chart()
        return jsonify(json.loads(chart_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/warehouse-location')
def get_warehouse_location_chart():
    """API endpoint for warehouse location chart"""
    try:
        chart_data = dashboard.create_warehouse_location_chart()
        return jsonify(json.loads(chart_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/restock-urgency')
def get_restock_urgency_chart():
    """API endpoint for restock urgency chart"""
    try:
        chart_data = dashboard.create_restock_urgency_chart()
        return jsonify(json.loads(chart_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/supplier-analysis')
def get_supplier_analysis_chart():
    """API endpoint for supplier analysis chart"""
    try:
        chart_data = dashboard.create_supplier_analysis_chart()
        return jsonify(json.loads(chart_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Sales Analytics Dashboard with sample data...")
    print("Access the dashboard at: http://127.0.0.1:8080")
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    ) 