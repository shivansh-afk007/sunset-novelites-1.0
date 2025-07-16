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

class FlaskSalesDashboard:
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
            'total_products': len(self.df),
            'avg_profit_margin': float(self.df['Margin'].mean()),
            'top_product': str(self.df.loc[self.df['Total'].idxmax(), 'Description']),
            'top_product_revenue': float(self.df['Total'].max()),
            'negative_margin_products': len(self.df[self.df['Margin'] < 0]),
            'high_margin_products': len(self.df[self.df['Margin'] > 50]),
            'top_category': str(self.df.groupby('Category')['Total'].sum().idxmax()),
            'top_category_revenue': float(self.df.groupby('Category')['Total'].sum().max())
        }
    
    def create_revenue_chart(self):
        """Create revenue distribution chart"""
        category_revenue = self.df.groupby('Category')['Total'].sum().sort_values(ascending=False)
        fig = px.pie(
            values=category_revenue.values,
            names=category_revenue.index,
            title="Revenue Distribution by Category"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_top_products_chart(self):
        """Create top products chart"""
        top_products = self.df.nlargest(10, 'Total')
        fig = px.bar(
            top_products,
            x='Total',
            y='Description',
            orientation='h',
            title="Top 10 Products by Revenue"
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_margin_distribution_chart(self):
        """Create margin distribution chart"""
        fig = px.histogram(
            self.df,
            x='Margin',
            nbins=30,
            title="Profit Margin Distribution",
            labels={'Margin': 'Profit Margin (%)', 'count': 'Number of Products'}
        )
        fig.add_vline(x=self.df['Margin'].mean(), line_dash="dash", line_color="red",
                     annotation_text=f"Mean: {self.df['Margin'].mean():.1f}%")
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_revenue_vs_units_chart(self):
        """Create revenue vs units sold chart"""
        fig = px.scatter(
            self.df,
            x='Sold',
            y='Total',
            color='Category',
            size='Margin',
            hover_data=['Description'],
            title="Revenue vs Units Sold (Size = Profit Margin)"
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_category_performance_chart(self):
        """Create category performance chart"""
        category_metrics = self.df.groupby('Category').agg({
            'Total': 'sum',
            'Sold': 'sum',
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
            title="Category Performance",
            yaxis=dict(title="Revenue ($)"),
            yaxis2=dict(title="Units Sold", overlaying="y", side="right"),
            barmode='group'
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_pareto_chart(self):
        """Create Pareto analysis chart"""
        sorted_df = self.df.sort_values('Total', ascending=False)
        cumulative_revenue = sorted_df['Total'].cumsum()
        cumulative_percentage = (np.arange(len(cumulative_revenue)) + 1) / len(cumulative_revenue) * 100
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cumulative_percentage,
            y=cumulative_revenue,
            mode='lines+markers',
            name='Cumulative Revenue'
        ))
        fig.add_hline(y=cumulative_revenue.max() * 0.8, line_dash="dash", line_color="red",
                     annotation_text="80% of Revenue")
        
        fig.update_layout(
            title="Revenue Concentration (Pareto Analysis)",
            xaxis_title="Percentage of Products (%)",
            yaxis_title="Cumulative Revenue ($)"
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def get_top_products_data(self):
        """Get top products data for table"""
        return self.df.nlargest(20, 'Total')[['Description', 'Category', 'Sold', 'Total', 'Margin', 'Profit']].round(2)
    
    def get_negative_margin_data(self):
        """Get negative margin products data"""
        return self.df[self.df['Margin'] < 0][['Description', 'Category', 'Sold', 'Total', 'Margin', 'Cost']].round(2)
    
    def get_category_summary(self):
        """Get category summary data"""
        category_summary = self.df.groupby('Category').agg({
            'Total': ['sum', 'count'],
            'Margin': 'mean',
            'Sold': 'sum',
            'Cost': 'sum',
            'Profit': 'sum'
        }).round(2)
        
        # Flatten column names
        category_summary.columns = ['_'.join(col).strip() for col in category_summary.columns]
        return category_summary

# Initialize dashboard
dashboard = FlaskSalesDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard_pro.html')

@app.route('/api/metrics')
def get_metrics():
    """API endpoint for key metrics"""
    return jsonify(dashboard.insights)

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

@app.route('/api/charts/revenue-vs-units')
def get_revenue_vs_units_chart():
    """API endpoint for revenue vs units chart"""
    return dashboard.create_revenue_vs_units_chart()

@app.route('/api/charts/category-performance')
def get_category_performance_chart():
    """API endpoint for category performance chart"""
    return dashboard.create_category_performance_chart()

@app.route('/api/charts/pareto')
def get_pareto_chart():
    """API endpoint for Pareto chart"""
    return dashboard.create_pareto_chart()

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 