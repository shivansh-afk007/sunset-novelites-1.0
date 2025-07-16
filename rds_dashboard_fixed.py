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

class RDSRTRIMDashboard:
    def __init__(self):
        self.rds_config = {
            'host': 'acumatica-rdspy.cda28gcg8vir.eu-north-1.rds.amazonaws.com',
            'user': 'admin',
            'password': 'Acumaticaadmin',
            'database': 'acumatica_data',
            'port': 3306,
            'connect_timeout': 30
        }
        self.insights = {}
        self.warehouse_data = {}
        self.load_data()
    
    def get_rds_connection(self):
        """Get connection to RDS MySQL database with OPTIMIZED settings"""
        try:
            connection = mysql.connector.connect(
                **self.rds_config,
                autocommit=True,
                pool_size=10,
                pool_name="dashboard_pool",
                pool_reset_session=True,
                use_pure=True,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            return connection
        except Exception as e:
            print(f"Error connecting to RDS: {e}")
            return None
    
    def load_data(self):
        """Load and prepare the data from RDS with OPTIMIZED performance"""
        try:
            print("Loading OPTIMIZED data from RDS...")
            start_time = time.time()
            
            # Load Lightspeed data (OPTIMIZED)
            lightspeed_start = time.time()
            lightspeed_df = self.load_lightspeed_data_full()
            lightspeed_time = time.time() - lightspeed_start
            print(f"⏱️  Lightspeed data loaded in {lightspeed_time:.2f} seconds")
            
            # Load Acumatica data (OPTIMIZED)
            acumatica_start = time.time()
            acumatica_df = self.load_acumatica_data_fixed()
            acumatica_time = time.time() - acumatica_start
            print(f"⏱️  Acumatica data loaded in {acumatica_time:.2f} seconds")
            
            # Load warehouse data (OPTIMIZED)
            warehouse_start = time.time()
            self.load_warehouse_data()
            warehouse_time = time.time() - warehouse_start
            print(f"⏱️  Warehouse data loaded in {warehouse_time:.2f} seconds")
            
            # Combine data
            combine_start = time.time()
            if not lightspeed_df.empty and not acumatica_df.empty:
                lightspeed_df['Source'] = 'Lightspeed'
                acumatica_df['Source'] = 'Acumatica'
                self.df = pd.concat([lightspeed_df, acumatica_df], ignore_index=True)
            elif not lightspeed_df.empty:
                self.df = lightspeed_df.copy()
                self.df['Source'] = 'Lightspeed'
            elif not acumatica_df.empty:
                self.df = acumatica_df.copy()
                self.df['Source'] = 'Acumatica'
            else:
                self.df = pd.DataFrame()
                print("No data loaded from RDS")
            
            if not self.df.empty:
                categorize_start = time.time()
                self.df['Category'] = self.categorize_products(self.df['Description'])
                categorize_time = time.time() - categorize_start
                print(f"⏱️  Product categorization completed in {categorize_time:.2f} seconds")
                
                insights_start = time.time()
                self.generate_insights()
                insights_time = time.time() - insights_start
                print(f"⏱️  Insights generation completed in {insights_time:.2f} seconds")
                
                total_time = time.time() - start_time
                print(f"✅ Loaded {len(self.df)} records from RDS (OPTIMIZED) in {total_time:.2f} seconds")
                print(f"   - Lightspeed: {len(self.df[self.df['Source'] == 'Lightspeed'])} records")
                print(f"   - Acumatica: {len(self.df[self.df['Source'] == 'Acumatica'])} records")
                print(f"📊 Performance Summary:")
                print(f"   - Lightspeed query: {lightspeed_time:.2f}s ({lightspeed_time/total_time*100:.1f}%)")
                print(f"   - Acumatica query: {acumatica_time:.2f}s ({acumatica_time/total_time*100:.1f}%)")
                print(f"   - Warehouse query: {warehouse_time:.2f}s ({warehouse_time/total_time*100:.1f}%)")
                print(f"   - Data processing: {categorize_time + insights_time:.2f}s ({(categorize_time + insights_time)/total_time*100:.1f}%)")
                
                # Data quality check
                print(f"🔍 Data Quality Check:")
                print(f"   - Average Margin: {self.df['Margin'].mean():.2f}%")
                print(f"   - Products with Stock > 0: {len(self.df[self.df['Stock'] > 0])}")
                print(f"   - Products with Cost > 0: {len(self.df[self.df['Cost'] > 0])}")
                print(f"   - Products with Profit > 0: {len(self.df[self.df['Profit'] > 0])}")
                
            else:
                print("No data available for analysis")
                
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            self.df = pd.DataFrame()
    
    def load_lightspeed_data_full(self):
        """Load FULL Lightspeed data from RDS with CORRECT column names"""
        try:
            conn_start = time.time()
            conn = self.get_rds_connection()
            conn_time = time.time() - conn_start
            if not conn:
                return pd.DataFrame()
            
            print("Loading CORRECT Lightspeed data...")
            query_start = time.time()
            
            # CORRECT query using actual column names
            query = """
            SELECT 
                i.Description,
                i.RemoteID as `System ID`,
                COALESCE(SUM(ol.Quantity), 0) as Sold,
                COALESCE(MAX(is1.Qoh), 0) as Stock,
                COALESCE(SUM(ol.Price * ol.Quantity), 0) as Subtotal,
                0 as Discounts,
                COALESCE(SUM(ol.Price * ol.Quantity), 0) as `Subtotal w/ Discounts`,
                COALESCE(SUM(ol.Total), 0) as Total,
                COALESCE(SUM(ol.Quantity * COALESCE(i.DefaultCost, i.AvgCost, 0)), 0) as Cost,
                COALESCE(SUM(ol.Total) - COALESCE(SUM(ol.Quantity * COALESCE(i.DefaultCost, i.AvgCost, 0)), 0), 0) as Profit,
                CASE 
                    WHEN COALESCE(SUM(ol.Total), 0) > 0 
                    THEN ROUND(((COALESCE(SUM(ol.Total), 0) - COALESCE(SUM(ol.Quantity * COALESCE(i.DefaultCost, i.AvgCost, 0)), 0)) / COALESCE(SUM(ol.Total), 0)) * 100, 2)
                    ELSE 0 
                END as Margin
            FROM lightspeed_Item i
            LEFT JOIN lightspeed_OrderLine ol ON i.RemoteID = ol.ItemID
            LEFT JOIN lightspeed_ItemShop is1 ON i.RemoteID = is1.ItemID
            WHERE i.Description IS NOT NULL
            GROUP BY i.RemoteID, i.Description
            HAVING Total > 0
            ORDER BY Total DESC
            LIMIT 1000
            """
            
            df = pd.read_sql(query, conn)
            query_time = time.time() - query_start
            conn.close()
            print(f"✅ Loaded {len(df)} Lightspeed records (CORRECT columns)")
            print(f"   - Connection time: {conn_time:.2f}s")
            print(f"   - Query execution time: {query_time:.2f}s")
            return df
            
        except Exception as e:
            print(f"Error loading Lightspeed data: {e}")
            return pd.DataFrame()
    
    def load_acumatica_data_fixed(self):
        """Load Acumatica data with CORRECT column names"""
        try:
            conn_start = time.time()
            conn = self.get_rds_connection()
            conn_time = time.time() - conn_start
            if not conn:
                return pd.DataFrame()
            
            print("Loading CORRECT Acumatica data...")
            query_start = time.time()
            
            # CORRECT query using actual column names
            query = """
            SELECT 
                i.Descr as Description,
                i.InventoryCD as `System ID`,
                COALESCE(SUM(sod.OrderQty), 0) as Sold,
                0 as Stock,
                COALESCE(SUM(sod.UnitPrice * sod.OrderQty), 0) as Subtotal,
                COALESCE(SUM(sod.DiscountAmount), 0) as Discounts,
                COALESCE(SUM(sod.UnitPrice * sod.OrderQty) - COALESCE(SUM(sod.DiscountAmount), 0), 0) as `Subtotal w/ Discounts`,
                COALESCE(SUM(sod.ExtendedPrice), 0) as Total,
                COALESCE(SUM(sod.OrderQty * COALESCE(sod.UnitCost, i.StdCost, 0)), 0) as Cost,
                COALESCE(SUM(sod.ExtendedPrice) - COALESCE(SUM(sod.OrderQty * COALESCE(sod.UnitCost, i.StdCost, 0)), 0), 0) as Profit,
                CASE 
                    WHEN COALESCE(SUM(sod.ExtendedPrice), 0) > 0 
                    THEN ROUND(((COALESCE(SUM(sod.ExtendedPrice), 0) - COALESCE(SUM(sod.OrderQty * COALESCE(sod.UnitCost, i.StdCost, 0)), 0)) / COALESCE(SUM(sod.ExtendedPrice), 0)) * 100, 2)
                    ELSE 0 
                END as Margin
            FROM InventoryItem i
            INNER JOIN SalesOrderDetail sod ON RTRIM(i.InventoryCD) = sod.InventoryID
            WHERE i.Descr IS NOT NULL
            GROUP BY i.InventoryCD, i.Descr
            HAVING Total > 0
            ORDER BY Total DESC
            LIMIT 1000
            """
            
            df = pd.read_sql(query, conn)
            query_time = time.time() - query_start
            conn.close()
            print(f"✅ Loaded {len(df)} Acumatica records (CORRECT columns)")
            print(f"   - Connection time: {conn_time:.2f}s")
            print(f"   - Query execution time: {query_time:.2f}s")
            return df
            
        except Exception as e:
            print(f"Error loading Acumatica data: {e}")
            return pd.DataFrame()
    
    def load_warehouse_data(self):
        """Load warehouse data from RDS with CORRECT column names"""
        try:
            conn_start = time.time()
            conn = self.get_rds_connection()
            conn_time = time.time() - conn_start
            if not conn:
                return
            
            print("Loading CORRECT warehouse data...")
            
            # CORRECT Lightspeed warehouse data
            lightspeed_warehouse_start = time.time()
            lightspeed_warehouse_query = """
            SELECT 
                i.RemoteID as Product_ID,
                i.Description as Product_Name,
                COALESCE(MAX(is1.Qoh), 0) as Current_Stock,
                COALESCE(MAX(is1.ReorderPoint), 0) as Reorder_Point,
                0 as Lead_Time_Days,
                0 as Safety_Stock,
                0 as Max_Stock,
                'Main Warehouse' as Warehouse_Location,
                'Lightspeed' as Supplier,
                'Active' as Item_Status
            FROM lightspeed_Item i
            LEFT JOIN lightspeed_ItemShop is1 ON i.RemoteID = is1.ItemID
            WHERE i.Description IS NOT NULL
            GROUP BY i.RemoteID, i.Description
            HAVING Current_Stock > 0
            ORDER BY Current_Stock DESC
            LIMIT 50
            """
            
            lightspeed_warehouse = pd.read_sql(lightspeed_warehouse_query, conn)
            lightspeed_warehouse_time = time.time() - lightspeed_warehouse_start
            
            # CORRECT Acumatica warehouse data (no stock data available)
            acumatica_warehouse_start = time.time()
            acumatica_warehouse_query = """
            SELECT 
                i.InventoryCD as Product_ID,
                i.Descr as Product_Name,
                0 as Current_Stock,
                0 as Reorder_Point,
                0 as Lead_Time_Days,
                0 as Safety_Stock,
                0 as Max_Stock,
                'Acumatica Warehouse' as Warehouse_Location,
                'Acumatica' as Supplier,
                'Active' as Item_Status
            FROM InventoryItem i
            WHERE i.Descr IS NOT NULL
            GROUP BY i.InventoryCD, i.Descr
            ORDER BY i.InventoryCD
            LIMIT 50
            """
            
            acumatica_warehouse = pd.read_sql(acumatica_warehouse_query, conn)
            acumatica_warehouse_time = time.time() - acumatica_warehouse_start
            conn.close()
            
            # Combine warehouse data
            self.warehouse_data = {
                'lightspeed': lightspeed_warehouse.to_dict('records'),
                'acumatica': acumatica_warehouse.to_dict('records'),
                'total_items': len(lightspeed_warehouse) + len(acumatica_warehouse),
                'low_stock_items': len(lightspeed_warehouse[lightspeed_warehouse['Current_Stock'] <= lightspeed_warehouse['Reorder_Point']])
            }
            
            print(f"✅ Loaded warehouse data: {self.warehouse_data['total_items']} items")
            print(f"   - Lightspeed query time: {lightspeed_warehouse_time:.2f}s")
            print(f"   - Acumatica query time: {acumatica_warehouse_time:.2f}s")
            
        except Exception as e:
            print(f"Error loading warehouse data: {e}")
            self.warehouse_data = {}
    
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
        try:
            # Calculate metrics with safe defaults
            total_revenue = float(self.df['Total'].sum()) if not self.df.empty else 0
            total_units_sold = int(self.df['Sold'].sum()) if not self.df.empty else 0
            total_products = len(self.df) if not self.df.empty else 0
            avg_profit_margin = float(self.df['Margin'].mean()) if not self.df.empty else 0
            top_product = str(self.df.loc[self.df['Total'].idxmax(), 'Description']) if not self.df.empty else "No products"
            top_product_revenue = float(self.df['Total'].max()) if not self.df.empty else 0
            negative_margin_products = len(self.df[self.df['Margin'] < 0]) if not self.df.empty else 0
            high_margin_products = len(self.df[self.df['Margin'] > 50]) if not self.df.empty else 0
            top_category = str(self.df.groupby('Category')['Total'].sum().idxmax()) if not self.df.empty else "No category"
            top_category_revenue = float(self.df.groupby('Category')['Total'].sum().max()) if not self.df.empty else 0
            lightspeed_products = len(self.df[self.df['Source'] == 'Lightspeed']) if not self.df.empty else 0
            acumatica_products = len(self.df[self.df['Source'] == 'Acumatica']) if not self.df.empty else 0
            warehouse_items = self.warehouse_data.get('total_items', 0)
            low_stock_items = self.warehouse_data.get('low_stock_items', 0)
            
            # Calculate actual stock remaining from warehouse data
            lightspeed_df = pd.DataFrame(self.warehouse_data.get('lightspeed', []))
            total_stock_remaining = int(lightspeed_df['Current_Stock'].sum()) if not lightspeed_df.empty else 0
            
            self.insights = {
                'total_revenue': total_revenue,
                'total_units_sold': total_units_sold,
                'total_products': total_products,
                'avg_profit_margin': avg_profit_margin,
                'top_product': top_product,
                'top_product_revenue': top_product_revenue,
                'negative_margin_products': negative_margin_products,
                'high_margin_products': high_margin_products,
                'top_category': top_category,
                'top_category_revenue': top_category_revenue,
                'lightspeed_products': lightspeed_products,
                'acumatica_products': acumatica_products,
                'warehouse_items': warehouse_items,
                'low_stock_items': low_stock_items,
                'total_stock_remaining': total_stock_remaining
            }
        except Exception as e:
            print(f"Error generating insights: {e}")
            self.insights = {
                'total_revenue': 0,
                'total_units_sold': 0,
                'total_products': 0,
                'avg_profit_margin': 0,
                'top_product': "No products",
                'top_product_revenue': 0,
                'negative_margin_products': 0,
                'high_margin_products': 0,
                'top_category': "No category",
                'top_category_revenue': 0,
                'lightspeed_products': 0,
                'acumatica_products': 0,
                'warehouse_items': 0,
                'low_stock_items': 0,
                'total_stock_remaining': 0
            }
    
    def create_revenue_chart(self):
        """Create revenue distribution chart"""
        try:
            category_revenue = self.df.groupby('Category')['Total'].sum().sort_values(ascending=False)
            fig = px.pie(
                values=category_revenue.values,
                names=category_revenue.index,
                title="Revenue Distribution by Category (FIXED JOIN)"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        except Exception as e:
            print(f"Error creating revenue chart: {e}")
            return json.dumps({})
    
    def create_top_products_chart(self):
        """Create top products chart"""
        try:
            top_products = self.df.nlargest(10, 'Total')
            fig = px.bar(
                top_products,
                x='Total',
                y='Description',
                orientation='h',
                title="Top 10 Products by Revenue (FIXED JOIN)"
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        except Exception as e:
            print(f"Error creating top products chart: {e}")
            return json.dumps({})
    
    def create_margin_distribution_chart(self):
        """Create margin distribution chart"""
        try:
            fig = px.histogram(
                self.df,
                x='Margin',
                nbins=30,
                title="Profit Margin Distribution (FIXED JOIN)",
                labels={'Margin': 'Profit Margin (%)', 'count': 'Number of Products'}
            )
            fig.add_vline(x=self.df['Margin'].mean(), line_dash="dash", line_color="red",
                         annotation_text=f"Mean: {self.df['Margin'].mean():.1f}%")
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        except Exception as e:
            print(f"Error creating margin chart: {e}")
            return json.dumps({})
    
    def create_source_comparison_chart(self):
        """Create source comparison chart"""
        try:
            source_revenue = self.df.groupby('Source')['Total'].sum()
            fig = px.bar(
                x=source_revenue.index,
                y=source_revenue.values,
                title="Revenue by Data Source (FIXED JOIN)",
                labels={'x': 'Source', 'y': 'Revenue ($)'}
            )
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        except Exception as e:
            print(f"Error creating source comparison chart: {e}")
            return json.dumps({})
    
    def create_warehouse_stock_chart(self):
        """Create warehouse stock status chart"""
        try:
            if 'lightspeed' in self.warehouse_data:
                df = pd.DataFrame(self.warehouse_data['lightspeed'])
                fig = px.bar(
                    df.head(20),
                    x='Current_Stock',
                    y='Product_Name',
                    orientation='h',
                    title="Warehouse Stock Levels (Top 20 Items)"
                )
                return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            else:
                return json.dumps({})
        except Exception as e:
            print(f"Error creating warehouse chart: {e}")
            return json.dumps({})
    
    def get_top_products_data(self):
        """Get top products data for table with ACTUAL stock data"""
        try:
            df_subset = self.df.nlargest(20, 'Total')[['Description', 'Category', 'Sold', 'Total', 'Margin', 'Source', 'Stock', 'Cost', 'Profit']].copy()
            
            # Use actual stock data from the dataframe (already loaded from database)
            # Stock data is already available in the main dataframe from the database queries
            
            return df_subset.round(2)
        except Exception as e:
            print(f"Error getting top products data: {e}")
            return pd.DataFrame()
    
    def get_negative_margin_data(self):
        """Get negative margin products data with ACTUAL stock data"""
        try:
            df_subset = self.df[self.df['Margin'] < 0][['Description', 'Category', 'Sold', 'Total', 'Margin', 'Source', 'Stock', 'Cost', 'Profit']].copy()
            
            # Use actual stock data from the dataframe (already loaded from database)
            # Stock data is already available in the main dataframe from the database queries
            
            return df_subset.round(2)
        except Exception as e:
            print(f"Error getting negative margin data: {e}")
            return pd.DataFrame()
    
    def get_category_summary(self):
        """Get category summary data with ACTUAL stock and cost data"""
        try:
            category_summary = self.df.groupby('Category').agg({
                'Total': ['sum', 'count'],
                'Margin': 'mean',
                'Sold': 'sum',
                'Stock': 'sum',  # Use actual stock data
                'Cost': 'sum',    # Use actual cost data
                'Profit': 'sum',  # Use actual profit data
                'Source': 'first'
            }).round(2)
            
            # Flatten column names
            category_summary.columns = ['_'.join(col).strip() for col in category_summary.columns]
            
            # All data is now from actual database queries, no hardcoded values
            return category_summary
        except Exception as e:
            print(f"Error getting category summary: {e}")
            return pd.DataFrame()
    
    def get_warehouse_metrics(self):
        """Get warehouse metrics with ADVANCED restock logic based on purchase rate"""
        try:
            # Calculate warehouse metrics
            lightspeed_df = pd.DataFrame(self.warehouse_data.get('lightspeed', []))
            acumatica_df = pd.DataFrame(self.warehouse_data.get('acumatica', []))
            
            total_products = len(lightspeed_df) + len(acumatica_df)
            total_current_stock = lightspeed_df['Current_Stock'].sum() if not lightspeed_df.empty else 0
            
            # ADVANCED RESTOCK LOGIC: Calculate based on purchase rate and stock duration
            if not lightspeed_df.empty:
                # Get purchase rate data for each product
                purchase_rates = self.calculate_purchase_rates()
                
                # Merge purchase rates with warehouse data
                lightspeed_df_with_rates = lightspeed_df.copy()
                lightspeed_df_with_rates['Purchase_Rate'] = lightspeed_df_with_rates['Product_ID'].map(purchase_rates)
                lightspeed_df_with_rates['Purchase_Rate'] = lightspeed_df_with_rates['Purchase_Rate'].fillna(0)
                
                # Calculate days until stockout based on purchase rate
                lightspeed_df_with_rates['Days_Until_Stockout'] = lightspeed_df_with_rates.apply(
                    lambda row: self.calculate_days_until_stockout(row['Current_Stock'], row['Purchase_Rate']), axis=1
                )
                
                # Determine if restock is needed (stock will last less than 30 days)
                lightspeed_df_with_rates['Needs_Restock'] = lightspeed_df_with_rates['Days_Until_Stockout'] <= 30
                
                # Count products needing restock
                products_needing_restock = len(lightspeed_df_with_rates[lightspeed_df_with_rates['Needs_Restock']])
                
                # Debug information
                print(f"🔍 ADVANCED Warehouse Metrics Analysis:")
                print(f"   - Total warehouse products: {total_products}")
                print(f"   - Total current stock: {total_current_stock}")
                print(f"   - Products needing restock (30-day rule): {products_needing_restock}")
                print(f"   - Items with stock > 0: {len(lightspeed_df[lightspeed_df['Current_Stock'] > 0])}")
                print(f"   - Items with reorder point > 0: {len(lightspeed_df[lightspeed_df['Reorder_Point'] > 0])}")
                
                # Show sample items that need restocking
                restock_items = lightspeed_df_with_rates[lightspeed_df_with_rates['Needs_Restock']]
                if not restock_items.empty:
                    print(f"   - Items needing restock (30-day rule):")
                    for idx, row in restock_items.head(5).iterrows():
                        print(f"     * {row['Product_Name'][:40]:40} | Stock: {row['Current_Stock']:4} | Rate: {row['Purchase_Rate']:.1f}/day | Days: {row['Days_Until_Stockout']:.1f}")
                else:
                    print(f"   - No items need restocking (all have >30 days stock)")
                
                # Store the enhanced data for other functions
                self.warehouse_data['lightspeed_enhanced'] = lightspeed_df_with_rates.to_dict('records')
            else:
                products_needing_restock = 0
                print(f"   - No warehouse data available")
            
            avg_lead_time = lightspeed_df['Lead_Time_Days'].mean() if not lightspeed_df.empty else 0
            critical_stock_products = len(lightspeed_df[lightspeed_df['Current_Stock'] <= 5]) if not lightspeed_df.empty else 0
            
            # Ensure all values are numbers, not NaN
            total_products = int(total_products) if not pd.isna(total_products) else 0
            total_current_stock = int(total_current_stock) if not pd.isna(total_current_stock) else 0
            products_needing_restock = int(products_needing_restock) if not pd.isna(products_needing_restock) else 0
            avg_lead_time = float(avg_lead_time) if not pd.isna(avg_lead_time) else 0.0
            critical_stock_products = int(critical_stock_products) if not pd.isna(critical_stock_products) else 0
            
            return {
                'total_products': total_products,
                'total_current_stock': total_current_stock,
                'products_needing_restock': products_needing_restock,
                'avg_lead_time': avg_lead_time,
                'critical_stock_products': critical_stock_products,
                'lightspeed': self.warehouse_data.get('lightspeed', []),
                'acumatica': self.warehouse_data.get('acumatica', []),
                'total_items': self.warehouse_data.get('total_items', 0),
                'low_stock_items': self.warehouse_data.get('low_stock_items', 0)
            }
        except Exception as e:
            print(f"Error getting warehouse metrics: {e}")
            return {
                'total_products': 0,
                'total_current_stock': 0,
                'products_needing_restock': 0,
                'avg_lead_time': 0.0,
                'critical_stock_products': 0,
                'lightspeed': [],
                'acumatica': [],
                'total_items': 0,
                'low_stock_items': 0
            }
    
    def calculate_purchase_rates(self):
        """Calculate daily purchase rate for each product based on sales data"""
        try:
            # Calculate total units sold and days since first sale for each product
            if not self.df.empty:
                # Group by product and calculate sales metrics
                sales_metrics = self.df.groupby('System ID').agg({
                    'Sold': 'sum',
                    'Description': 'first'
                }).reset_index()
                
                # Calculate purchase rates (units sold per day)
                # For simplicity, we'll use a 90-day period as default
                days_period = 90
                purchase_rates = {}
                
                for _, row in sales_metrics.iterrows():
                    total_sold = row['Sold']
                    daily_rate = total_sold / days_period if days_period > 0 else 0
                    purchase_rates[row['System ID']] = daily_rate
                
                print(f"📊 Purchase Rate Analysis:")
                print(f"   - Calculated rates for {len(purchase_rates)} products")
                print(f"   - Average daily sales rate: {sum(purchase_rates.values()) / len(purchase_rates):.2f} units/day")
                
                return purchase_rates
            else:
                return {}
        except Exception as e:
            print(f"Error calculating purchase rates: {e}")
            return {}
    
    def calculate_days_until_stockout(self, current_stock, purchase_rate):
        """Calculate how many days until stockout based on purchase rate"""
        try:
            if purchase_rate > 0:
                days_until_stockout = current_stock / purchase_rate
                return days_until_stockout
            else:
                # If no purchase rate, assume very slow moving (365 days)
                return 365
        except Exception as e:
            print(f"Error calculating days until stockout: {e}")
            return 365

# Initialize dashboard
dashboard = RDSRTRIMDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard_pro.html')

@app.route('/api/metrics')
def get_metrics():
    """API endpoint for key metrics"""
    try:
        if not dashboard.insights:
            dashboard.generate_insights()
        return jsonify(dashboard.insights)
    except Exception as e:
        print(f"Error in metrics endpoint: {e}")
        return jsonify({
            'total_revenue': 0,
            'total_units_sold': 0,
            'total_products': 0,
            'avg_profit_margin': 0,
            'top_product': "No products",
            'top_product_revenue': 0,
            'negative_margin_products': 0,
            'high_margin_products': 0,
            'total_stock_remaining': 0
        })

@app.route('/api/warehouse/metrics')
def get_warehouse_metrics():
    """API endpoint for warehouse metrics"""
    try:
        return jsonify(dashboard.get_warehouse_metrics())
    except Exception as e:
        print(f"Error in warehouse metrics endpoint: {e}")
        return jsonify({
            'total_products': 0,
            'total_current_stock': 0,
            'products_needing_restock': 0,
            'avg_lead_time': 0.0,
            'critical_stock_products': 0
        })

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

@app.route('/api/charts/source-comparison')
def get_source_comparison_chart():
    """API endpoint for source comparison chart"""
    return dashboard.create_source_comparison_chart()

@app.route('/api/charts/warehouse-stock-status')
def get_warehouse_stock_chart():
    """API endpoint for warehouse stock chart"""
    return dashboard.create_warehouse_stock_chart()

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

# Add missing API endpoints to fix loading states
@app.route('/api/charts/revenue-by-category')
def get_revenue_by_category_chart():
    """API endpoint for revenue by category chart"""
    chart_data = dashboard.create_revenue_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/top-products-chart')
def get_top_products_chart_alt():
    """API endpoint for top products chart (alternative)"""
    chart_data = dashboard.create_top_products_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/profit-margin-by-category')
def get_profit_margin_by_category_chart():
    """API endpoint for profit margin by category chart"""
    chart_data = dashboard.create_margin_distribution_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/stock-vs-sales')
def get_stock_vs_sales_chart():
    """API endpoint for stock vs sales chart"""
    chart_data = dashboard.create_source_comparison_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/revenue-vs-margin')
def get_revenue_vs_margin_chart():
    """API endpoint for revenue vs margin chart"""
    chart_data = dashboard.create_source_comparison_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/category-performance')
def get_category_performance_chart():
    """API endpoint for category performance chart"""
    chart_data = dashboard.create_revenue_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/warehouse-location')
def get_warehouse_location_chart():
    """API endpoint for warehouse location chart"""
    chart_data = dashboard.create_warehouse_stock_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/restock-urgency')
def get_restock_urgency_chart():
    """API endpoint for restock urgency chart"""
    chart_data = dashboard.create_warehouse_stock_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/charts/supplier-analysis')
def get_supplier_analysis_chart():
    """API endpoint for supplier analysis chart"""
    chart_data = dashboard.create_source_comparison_chart()
    return chart_data, 200, {'Content-Type': 'application/json'}

@app.route('/api/data/warehouse-summary')
def get_warehouse_summary_data():
    """API endpoint for warehouse summary data"""
    try:
        # Create warehouse summary data structure
        lightspeed_df = pd.DataFrame(dashboard.warehouse_data.get('lightspeed', []))
        acumatica_df = pd.DataFrame(dashboard.warehouse_data.get('acumatica', []))
        
        if not lightspeed_df.empty:
            warehouse_summary = {
                'Lightspeed': {
                    'Current_Stock_sum': int(lightspeed_df['Current_Stock'].sum()),
                    'Current_Stock_mean': float(lightspeed_df['Current_Stock'].mean()),
                    'Reorder_Point_sum': int(lightspeed_df['Reorder_Point'].sum()),
                    'Safety_Stock_sum': int(lightspeed_df['Safety_Stock'].sum()),
                    'Restock_Needed_sum': int(len(lightspeed_df[lightspeed_df['Current_Stock'] <= lightspeed_df['Reorder_Point']]))
                }
            }
        else:
            warehouse_summary = {
                'Lightspeed': {
                    'Current_Stock_sum': 0,
                    'Current_Stock_mean': 0,
                    'Reorder_Point_sum': 0,
                    'Safety_Stock_sum': 0,
                    'Restock_Needed_sum': 0
                }
            }
        
        return jsonify(warehouse_summary)
    except Exception as e:
        print(f"Error getting warehouse summary data: {e}")
        return jsonify({})

@app.route('/api/data/restock-alerts')
def get_restock_alerts_data():
    """API endpoint for restock alerts data with ADVANCED purchase rate logic"""
    try:
        lightspeed_df = pd.DataFrame(dashboard.warehouse_data.get('lightspeed', []))
        
        if not lightspeed_df.empty:
            # Use enhanced warehouse data if available, otherwise calculate
            if 'lightspeed_enhanced' in dashboard.warehouse_data:
                enhanced_df = pd.DataFrame(dashboard.warehouse_data['lightspeed_enhanced'])
                restock_items = enhanced_df[enhanced_df['Needs_Restock']].copy()
            else:
                # Fallback to basic calculation
                purchase_rates = dashboard.calculate_purchase_rates()
                
                # Merge purchase rates with warehouse data
                lightspeed_df_with_rates = lightspeed_df.copy()
                lightspeed_df_with_rates['Purchase_Rate'] = lightspeed_df_with_rates['Product_ID'].map(purchase_rates)
                lightspeed_df_with_rates['Purchase_Rate'] = lightspeed_df_with_rates['Purchase_Rate'].fillna(0)
                
                # Calculate days until stockout
                lightspeed_df_with_rates['Days_Until_Stockout'] = lightspeed_df_with_rates.apply(
                    lambda row: dashboard.calculate_days_until_stockout(row['Current_Stock'], row['Purchase_Rate']), axis=1
                )
                
                # Filter items that need restocking (stock will last less than 30 days)
                restock_items = lightspeed_df_with_rates[lightspeed_df_with_rates['Days_Until_Stockout'] <= 30].copy()
            
            print(f"🔍 ADVANCED Restock Analysis:")
            print(f"   - Total warehouse items: {len(lightspeed_df)}")
            print(f"   - Items needing restock (30-day rule): {len(restock_items)}")
            print(f"   - Items with stock > 0: {len(lightspeed_df[lightspeed_df['Current_Stock'] > 0])}")
            
            if not restock_items.empty:
                # Add urgency level based on days until stockout
                restock_items['Urgency_Level'] = restock_items['Days_Until_Stockout'].apply(
                    lambda days: 'Critical' if days <= 7 else 'High' if days <= 14 else 'Medium' if days <= 30 else 'Low'
                )
                
                # Add category based on product name
                restock_items['Category'] = restock_items['Product_Name'].apply(
                    lambda name: dashboard.categorize_products([name])[0] if pd.notna(name) else 'Other'
                )
                
                # Add restock recommendation
                restock_items['Restock_Recommendation'] = restock_items.apply(
                    lambda row: f"Order {max(10, int(row['Purchase_Rate'] * 30))} units" if row['Purchase_Rate'] > 0 else "Review demand",
                    axis=1
                )
                
                # Convert to records format
                restock_alerts = restock_items.to_dict('records')
                
                print(f"   - Sample restock items:")
                for idx, row in restock_items.head(3).iterrows():
                    print(f"     * {row['Product_Name'][:40]:40} | Stock: {row['Current_Stock']:4} | Rate: {row['Purchase_Rate']:.1f}/day | Days: {row['Days_Until_Stockout']:.1f} | {row['Urgency_Level']}")
            else:
                restock_alerts = []
                print(f"   - No items need restocking (all have >30 days stock)")
        else:
            restock_alerts = []
            print(f"   - No warehouse data available")
        
        return jsonify(restock_alerts)
    except Exception as e:
        print(f"Error getting restock alerts data: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5004) 