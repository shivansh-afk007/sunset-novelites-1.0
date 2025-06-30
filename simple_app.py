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
        self.load_data()
        self.load_warehouse_data()
    
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
    
    def load_warehouse_data(self):
        """Load and prepare warehouse data from CSV"""
        try:
            # Try to load the warehouse CSV file
            try:
                self.warehouse_df = pd.read_csv('_Inventory Planning Settings 20250627.csv')
                print("Successfully loaded warehouse CSV file")
                
                # Map the actual CSV columns to expected column names
                column_mapping = {
                    'Inventory ID': 'Product_ID',
                    'Description': 'Product_Name',
                    'Class ID': 'Category',
                    'Warehouse ID': 'Warehouse_Location',
                    'Qty. On Hand': 'Current_Stock',
                    'Qty. Available': 'Available_Stock',
                    'Reorder Point': 'Reorder_Point',
                    'Max Qty.': 'Max_Stock',
                    'Vendor': 'Supplier',
                    'Vendor Name': 'Supplier_Name',
                    'Vendor Lead Time (Days)': 'Lead_Time_Days',
                    'Total Lead Time': 'Total_Lead_Time',
                    'Item Status': 'Item_Status'
                }
                
                # Rename columns that exist in the CSV
                for old_col, new_col in column_mapping.items():
                    if old_col in self.warehouse_df.columns:
                        self.warehouse_df.rename(columns={old_col: new_col}, inplace=True)
                
                # Convert numeric columns to proper data types
                numeric_columns = ['Current_Stock', 'Available_Stock', 'Reorder_Point', 'Max_Stock', 'Lead_Time_Days', 'Total_Lead_Time']
                for col in numeric_columns:
                    if col in self.warehouse_df.columns:
                        # Clean the data first
                        self.warehouse_df[col] = self.warehouse_df[col].astype(str).str.replace(',', '').str.replace('$', '').str.replace('%', '')
                        # Convert to numeric, filling errors with 0
                        self.warehouse_df[col] = pd.to_numeric(self.warehouse_df[col], errors='coerce').fillna(0)
                
                # Handle text columns that might contain NaN values
                text_columns = ['Product_Name', 'Category', 'Warehouse_Location', 'Supplier', 'Supplier_Name', 'Item_Status']
                for col in text_columns:
                    if col in self.warehouse_df.columns:
                        self.warehouse_df[col] = self.warehouse_df[col].fillna('Unknown')
                
                # Map warehouse categories to match sales categories
                self.warehouse_df['Category'] = self.warehouse_df['Category'].apply(self.map_warehouse_category)
                
                # Add missing columns with default values
                if 'Safety_Stock' not in self.warehouse_df.columns:
                    self.warehouse_df['Safety_Stock'] = self.warehouse_df['Reorder_Point'] * 0.5
                
                if 'Last_Updated' not in self.warehouse_df.columns:
                    self.warehouse_df['Last_Updated'] = datetime.now().strftime('%Y-%m-%d')
                
                # Calculate derived columns with proper error handling
                def calculate_stock_status(row):
                    try:
                        current = float(row['Current_Stock'])
                        reorder = float(row['Reorder_Point'])
                        max_stock = float(row.get('Max_Stock', current + 1))
                        
                        if current <= reorder:
                            return 'Low'
                        elif current <= max_stock:
                            return 'Adequate'
                        else:
                            return 'Overstocked'
                    except:
                        return 'Unknown'
                
                self.warehouse_df['Stock_Status'] = self.warehouse_df.apply(calculate_stock_status, axis=1)
                
                def calculate_restock_needed(row):
                    try:
                        return float(row['Current_Stock']) <= float(row['Reorder_Point'])
                    except:
                        return False
                
                self.warehouse_df['Restock_Needed'] = self.warehouse_df.apply(calculate_restock_needed, axis=1)
                
                # Calculate days until stockout (simplified calculation)
                def calculate_days_until_stockout(row):
                    try:
                        current = float(row['Current_Stock'])
                        reorder = float(row['Reorder_Point'])
                        if current == 0:
                            return 999
                        return int(current / max(1, reorder / 30))
                    except:
                        return 999
                
                self.warehouse_df['Days_Until_Stockout'] = self.warehouse_df.apply(calculate_days_until_stockout, axis=1)
                
                # Add monthly and annual demand estimates
                self.warehouse_df['Monthly_Demand'] = self.warehouse_df['Reorder_Point'] * 2  # Estimate
                self.warehouse_df['Annual_Demand'] = self.warehouse_df['Monthly_Demand'] * 12
                
                # Calculate stock turnover
                def calculate_stock_turnover(row):
                    try:
                        monthly_demand = float(row['Monthly_Demand'])
                        current_stock = float(row['Current_Stock'])
                        return monthly_demand / max(1, current_stock)
                    except:
                        return 0
                
                self.warehouse_df['Stock_Turnover'] = self.warehouse_df.apply(calculate_stock_turnover, axis=1)
                
                print(f"Successfully processed warehouse data with {len(self.warehouse_df)} products")
                
            except Exception as e:
                print(f"Could not load warehouse CSV file: {e}")
                # Create sample warehouse data based on sales data
                self.create_sample_warehouse_data()
            
            self.generate_warehouse_insights()
        except Exception as e:
            print(f"Error loading warehouse data: {str(e)}")
            self.create_sample_warehouse_data()
            self.generate_warehouse_insights()
    
    def create_sample_warehouse_data(self):
        """Create sample warehouse data based on sales data"""
        print("Creating sample warehouse data...")
        
        # Create warehouse data based on existing sales data
        warehouse_data = []
        
        for _, row in self.df.iterrows():
            # Calculate warehouse metrics based on sales data
            current_stock = max(0, row['Stock'])
            reorder_point = max(1, int(row['Sold'] * 0.2))  # 20% of sales as reorder point
            lead_time_days = np.random.randint(7, 30)  # Random lead time 7-30 days
            safety_stock = max(1, int(row['Sold'] * 0.1))  # 10% of sales as safety stock
            max_stock = reorder_point + safety_stock + int(row['Sold'] * 0.5)  # Max stock level
            
            warehouse_data.append({
                'Product_ID': row.get('System ID', f'PROD_{len(warehouse_data)}'),
                'Product_Name': row['Description'],
                'Category': row['Category'],
                'Current_Stock': current_stock,
                'Reorder_Point': reorder_point,
                'Lead_Time_Days': lead_time_days,
                'Safety_Stock': safety_stock,
                'Max_Stock': max_stock,
                'Warehouse_Location': np.random.choice(['A1', 'A2', 'B1', 'B2', 'C1', 'C2']),
                'Supplier': np.random.choice(['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D']),
                'Last_Updated': datetime.now().strftime('%Y-%m-%d'),
                'Stock_Status': 'Low' if current_stock <= reorder_point else 'Adequate' if current_stock <= max_stock else 'Overstocked',
                'Restock_Needed': current_stock <= reorder_point,
                'Days_Until_Stockout': int(current_stock / (row['Sold'] / 365)) if row['Sold'] > 0 else 999,
                'Monthly_Demand': row['Sold'],
                'Annual_Demand': row['Sold'] * 12,
                'Stock_Turnover': row['Sold'] / current_stock if current_stock > 0 else 0
            })
        
        self.warehouse_df = pd.DataFrame(warehouse_data)
        print(f"Created sample warehouse data with {len(warehouse_data)} products")
    
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
    
    def map_warehouse_category(self, warehouse_category):
        """Map warehouse category names to match sales categories"""
        if pd.isna(warehouse_category):
            return 'Other'
        
        category_str = str(warehouse_category).upper()
        
        # Map warehouse categories to sales categories
        if 'CLOTHING' in category_str or 'PANTY' in category_str or 'HOSIERY' in category_str or 'SHOES' in category_str or 'TEDDY' in category_str:
            return 'Clothing & Accessories'
        elif 'ADULT TOYS' in category_str or 'DILDO' in category_str or 'BULLET' in category_str or 'C RING' in category_str or 'RABBIT' in category_str:
            return 'Adult Toys'
        elif 'VIBRATOR' in category_str or 'WAND' in category_str:
            return 'Vibrators'
        elif 'SUPPLEMENT' in category_str or 'RHINO' in category_str or 'MOOD' in category_str:
            return 'Supplements'
        elif 'LUBE' in category_str or 'LUBRICANT' in category_str or 'GEL' in category_str or 'OIL' in category_str:
            return 'Lubricants'
        elif 'CLEANER' in category_str or 'CLEAN' in category_str or 'CHARGER' in category_str or 'BATTERY' in category_str:
            return 'Accessories'
        else:
            return 'Other'
    
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
    
    def generate_warehouse_insights(self):
        """Generate warehouse-specific insights"""
        if self.warehouse_df is not None and len(self.warehouse_df) > 0:
            try:
                # Ensure numeric columns are properly converted
                numeric_cols = ['Current_Stock', 'Lead_Time_Days', 'Safety_Stock', 'Stock_Turnover']
                for col in numeric_cols:
                    if col in self.warehouse_df.columns:
                        self.warehouse_df[col] = pd.to_numeric(self.warehouse_df[col], errors='coerce').fillna(0)
                
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
            except Exception as e:
                print(f"Error generating warehouse insights: {e}")
                # Fallback to basic insights
                self.warehouse_insights = {
                    'total_products': int(len(self.warehouse_df)),
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
        else:
            self.warehouse_insights = {}
    
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
    
    def get_warehouse_summary(self):
        """Get warehouse summary data - limited to top categories by revenue"""
        if self.warehouse_df is not None:
            # Get top categories by revenue (limit to top 10)
            top_categories = self.df.groupby('Category')['Total'].sum().nlargest(10).index.tolist()
            
            # Filter warehouse data to only include top revenue categories
            filtered_warehouse = self.warehouse_df[self.warehouse_df['Category'].isin(top_categories)]
            
            warehouse_summary = filtered_warehouse.groupby('Category').agg({
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
        """Get top 15 products that need restocking - prioritized by revenue and urgency"""
        if self.warehouse_df is not None:
            # Get top revenue products from sales data
            top_revenue_products = self.df.nlargest(100, 'Total')['Description'].tolist()
            
            # Filter warehouse data to include only top revenue products
            filtered_warehouse = self.warehouse_df[
                self.warehouse_df['Product_Name'].isin(top_revenue_products)
            ]
            
            # Get products that need restocking, sorted by urgency and revenue
            restock_alerts = filtered_warehouse[filtered_warehouse['Restock_Needed'] == True].copy()
            
            # Add revenue information from sales data
            restock_alerts = restock_alerts.merge(
                self.df[['Description', 'Total']].rename(columns={'Description': 'Product_Name'}),
                on='Product_Name',
                how='left'
            ).fillna(0)
            
            # Sort by urgency (days until stockout) and revenue, then take top 15
            restock_alerts = restock_alerts.sort_values(['Days_Until_Stockout', 'Total'], ascending=[True, False])
            restock_alerts = restock_alerts.head(15)[
                ['Product_Name', 'Category', 'Current_Stock', 'Reorder_Point', 'Lead_Time_Days', 'Days_Until_Stockout', 'Supplier', 'Total']
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
        """Get warehouse location summary - limited to top locations"""
        if self.warehouse_df is not None:
            # Get top revenue products
            top_revenue_products = self.df.nlargest(100, 'Total')['Description'].tolist()
            
            # Filter warehouse data to include only top revenue products
            filtered_warehouse = self.warehouse_df[
                self.warehouse_df['Product_Name'].isin(top_revenue_products)
            ]
            
            location_summary = filtered_warehouse.groupby('Warehouse_Location').agg({
                'Current_Stock': 'sum',
                'Product_Name': 'count',
                'Restock_Needed': 'sum'
            }).round(2)
            location_summary.columns = ['Total_Stock', 'Product_Count', 'Restock_Needed']
            
            # Sort by total stock and take top 10 locations
            location_summary = location_summary.sort_values('Total_Stock', ascending=False).head(10)
            
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
    
    # Warehouse-specific charts
    def create_warehouse_stock_status_chart(self):
        """Create warehouse stock status chart"""
        if self.warehouse_df is not None:
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
        """Create warehouse location chart - focused on top locations"""
        if self.warehouse_df is not None:
            # Get top revenue products
            top_revenue_products = self.df.nlargest(100, 'Total')['Description'].tolist()
            
            # Filter warehouse data to include only top revenue products
            filtered_warehouse = self.warehouse_df[
                self.warehouse_df['Product_Name'].isin(top_revenue_products)
            ]
            
            location_data = filtered_warehouse.groupby('Warehouse_Location').agg({
                'Current_Stock': 'sum',
                'Product_Name': 'count'
            }).reset_index()
            
            # Sort by total stock and take top 10 locations
            location_data = location_data.sort_values('Current_Stock', ascending=False).head(10)
            
            fig = px.bar(
                location_data,
                x='Warehouse_Location',
                y='Current_Stock',
                title="Top 10 Warehouse Locations by Stock",
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
        """Create restock urgency chart - top 15 products by urgency and revenue"""
        if self.warehouse_df is not None:
            # Get top revenue products from sales data
            top_revenue_products = self.df.nlargest(100, 'Total')['Description'].tolist()
            
            # Filter warehouse data to include only top revenue products
            filtered_warehouse = self.warehouse_df[
                self.warehouse_df['Product_Name'].isin(top_revenue_products)
            ]
            
            # Filter products that need restocking
            restock_data = filtered_warehouse[filtered_warehouse['Restock_Needed'] == True].copy()
            
            # Add revenue information
            restock_data = restock_data.merge(
                self.df[['Description', 'Total']].rename(columns={'Description': 'Product_Name'}),
                on='Product_Name',
                how='left'
            ).fillna(0)
            
            # Sort by urgency and revenue, take top 15
            restock_data = restock_data.sort_values(['Days_Until_Stockout', 'Total'], ascending=[True, False]).head(15)
            
            # Truncate product names for better display
            restock_data['Product_Name_Short'] = restock_data['Product_Name'].str[:30] + '...'
            
            fig = px.bar(
                restock_data,
                x='Days_Until_Stockout',
                y='Product_Name_Short',
                orientation='h',
                title="Top 15 Restock Alerts - High Revenue Products",
                labels={'Days_Until_Stockout': 'Days Until Stockout', 'Product_Name_Short': 'Product'},
                color='Total',
                color_continuous_scale='Reds',
                hover_data=['Product_Name', 'Category', 'Current_Stock', 'Total']
            )
            fig.update_layout(
                title_x=0.5,
                title_font_size=16,
                yaxis={'categoryorder':'total ascending'},
                height=600  # Increase height for better visibility
            )
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return json.dumps({})
    
    def create_supplier_analysis_chart(self):
        """Create supplier analysis chart - focused on top suppliers"""
        if self.warehouse_df is not None:
            # Get top revenue products
            top_revenue_products = self.df.nlargest(100, 'Total')['Description'].tolist()
            
            # Filter warehouse data to include only top revenue products
            filtered_warehouse = self.warehouse_df[
                self.warehouse_df['Product_Name'].isin(top_revenue_products)
            ]
            
            supplier_data = filtered_warehouse.groupby('Supplier').agg({
                'Current_Stock': 'sum',
                'Product_Name': 'count',
                'Lead_Time_Days': 'mean',
                'Restock_Needed': 'sum'
            }).round(2)
            
            # Sort by total stock and take top 10 suppliers
            supplier_data = supplier_data.sort_values('Current_Stock', ascending=False).head(10)
            
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
                title="Top 10 Suppliers Analysis",
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
    # For Replit deployment
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False  # Set to False for production
    ) 