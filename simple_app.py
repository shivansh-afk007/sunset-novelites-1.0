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
        self.insights = {}
        self.load_data()
    
    def load_data(self):
        """Load and prepare the data"""
        try:
            # Load CSV data
            self.df = pd.read_csv('reports_sales_listings_item.csv')
            
            # Clean column names
            self.df.columns = self.df.columns.str.strip().str.replace('"', '')
            
            # Clean numeric data
            numeric_columns = ['Stock', 'Sold', 'Subtotal', 'Discounts', 'Subtotal w/ Discounts', 
                              'Total', 'Cost', 'Profit', 'Margin']
            
            for col in numeric_columns:
                if col in self.df.columns:
                    self.df[col] = self.df[col].astype(str).str.replace('$', '').str.replace('%', '').str.replace(',', '')
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            # Create categories
            self.df['Category'] = self.categorize_products(self.df['Description'])
            self.generate_insights()
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
    
    def categorize_products(self, descriptions):
        """Categorize products based on description"""
        categories = []
        for desc in descriptions:
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
    
    def generate_insights(self):
        """Generate key insights from the data"""
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
    
    def get_top_products_data(self):
        """Get top products data for table"""
        return self.df.nlargest(20, 'Total')[['Description', 'Category', 'Sold', 'Stock', 'Total', 'Margin', 'Profit']].round(2)
    
    def get_negative_margin_data(self):
        """Get negative margin products data"""
        return self.df[self.df['Margin'] < 0][['Description', 'Category', 'Sold', 'Stock', 'Total', 'Margin', 'Cost']].round(2)
    
    def get_category_summary(self):
        """Get category summary data"""
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
    
    def create_margin_distribution_chart(self):
        """Create margin distribution histogram"""
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

# Initialize dashboard
dashboard = SimpleSalesDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('simple_dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    """API endpoint for key metrics"""
    return jsonify(dashboard.insights)

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

@app.route('/api/charts/margin-distribution')
def get_margin_distribution_chart():
    """API endpoint for margin distribution chart"""
    try:
        return dashboard.create_margin_distribution_chart()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/revenue-by-category')
def get_revenue_by_category_chart():
    """API endpoint for revenue by category chart"""
    try:
        return dashboard.create_revenue_by_category_chart()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/top-products-chart')
def get_top_products_chart():
    """API endpoint for top products chart"""
    try:
        return dashboard.create_top_products_chart()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/stock-vs-sales')
def get_stock_vs_sales_chart():
    """API endpoint for stock vs sales chart"""
    try:
        return dashboard.create_stock_vs_sales_chart()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/profit-margin-by-category')
def get_profit_margin_by_category_chart():
    """API endpoint for profit margin by category chart"""
    try:
        return dashboard.create_profit_margin_by_category_chart()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/revenue-vs-margin')
def get_revenue_vs_margin_chart():
    """API endpoint for revenue vs margin chart"""
    try:
        return dashboard.create_revenue_vs_margin_chart()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/category-performance')
def get_category_performance_chart():
    """API endpoint for category performance chart"""
    try:
        return dashboard.create_category_performance_chart()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # For Replit deployment
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False  # Set to False for production
    ) 