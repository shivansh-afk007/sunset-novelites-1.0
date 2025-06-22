import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for better looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class SalesAnalytics:
    def __init__(self, csv_file):
        """Initialize the analytics with CSV data"""
        self.df = self.load_and_clean_data(csv_file)
        self.generate_insights()
    
    def load_and_clean_data(self, csv_file):
        """Load and clean the CSV data"""
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Clean column names
        df.columns = df.columns.str.strip().str.replace('"', '')
        
        # Clean data types
        # Remove $ and % symbols and convert to numeric
        numeric_columns = ['Stock', 'Sold', 'Subtotal', 'Discounts', 'Subtotal w/ Discounts', 
                          'Total', 'Cost', 'Profit', 'Margin']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('$', '').str.replace('%', '').str.replace(',', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Create product categories based on description
        df['Category'] = self.categorize_products(df['Description'])
        
        return df
    
    def categorize_products(self, descriptions):
        """Categorize products based on description keywords"""
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
            'total_revenue': self.df['Total'].sum(),
            'total_units_sold': self.df['Sold'].sum(),
            'total_products': len(self.df),
            'avg_profit_margin': self.df['Margin'].mean(),
            'top_product': self.df.loc[self.df['Total'].idxmax(), 'Description'],
            'top_product_revenue': self.df['Total'].max(),
            'negative_margin_products': len(self.df[self.df['Margin'] < 0]),
            'high_margin_products': len(self.df[self.df['Margin'] > 50])
        }
    
    def create_revenue_analysis(self):
        """Create revenue analysis charts"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Revenue Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Revenue by Category
        category_revenue = self.df.groupby('Category')['Total'].sum().sort_values(ascending=False)
        axes[0, 0].pie(category_revenue.values, labels=category_revenue.index, autopct='%1.1f%%')
        axes[0, 0].set_title('Revenue Distribution by Category')
        
        # 2. Top 10 Products by Revenue
        top_products = self.df.nlargest(10, 'Total')
        axes[0, 1].barh(range(len(top_products)), top_products['Total'])
        axes[0, 1].set_yticks(range(len(top_products)))
        axes[0, 1].set_yticklabels([desc[:20] + '...' if len(desc) > 20 else desc 
                                   for desc in top_products['Description']])
        axes[0, 1].set_title('Top 10 Products by Revenue')
        axes[0, 1].set_xlabel('Revenue ($)')
        
        # 3. Profit Margin Distribution
        axes[1, 0].hist(self.df['Margin'].dropna(), bins=30, alpha=0.7, edgecolor='black')
        axes[1, 0].axvline(self.df['Margin'].mean(), color='red', linestyle='--', 
                          label=f'Mean: {self.df["Margin"].mean():.1f}%')
        axes[1, 0].set_title('Profit Margin Distribution')
        axes[1, 0].set_xlabel('Profit Margin (%)')
        axes[1, 0].set_ylabel('Number of Products')
        axes[1, 0].legend()
        
        # 4. Units Sold vs Revenue
        axes[1, 1].scatter(self.df['Sold'], self.df['Total'], alpha=0.6)
        axes[1, 1].set_xlabel('Units Sold')
        axes[1, 1].set_ylabel('Revenue ($)')
        axes[1, 1].set_title('Units Sold vs Revenue')
        
        plt.tight_layout()
        plt.savefig('revenue_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_performance_metrics(self):
        """Create performance metrics dashboard"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Performance Metrics Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Category Performance
        category_metrics = self.df.groupby('Category').agg({
            'Total': 'sum',
            'Sold': 'sum',
            'Margin': 'mean'
        }).round(2)
        
        x = np.arange(len(category_metrics))
        width = 0.35
        
        axes[0, 0].bar(x - width/2, category_metrics['Total'], width, label='Revenue ($)')
        axes[0, 0].bar(x + width/2, category_metrics['Sold'], width, label='Units Sold')
        axes[0, 0].set_xlabel('Category')
        axes[0, 0].set_ylabel('Amount')
        axes[0, 0].set_title('Category Performance')
        axes[0, 0].set_xticks(x)
        axes[0, 0].set_xticklabels(category_metrics.index, rotation=45)
        axes[0, 0].legend()
        
        # 2. Margin Analysis by Category
        axes[0, 1].bar(category_metrics.index, category_metrics['Margin'])
        axes[0, 1].set_title('Average Profit Margin by Category')
        axes[0, 1].set_xlabel('Category')
        axes[0, 1].set_ylabel('Average Margin (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Revenue vs Cost Analysis
        axes[1, 0].scatter(self.df['Cost'], self.df['Total'], alpha=0.6)
        axes[1, 0].plot([self.df['Cost'].min(), self.df['Cost'].max()], 
                       [self.df['Cost'].min(), self.df['Cost'].max()], 'r--', alpha=0.8)
        axes[1, 0].set_xlabel('Cost ($)')
        axes[1, 0].set_ylabel('Revenue ($)')
        axes[1, 0].set_title('Revenue vs Cost')
        
        # 4. Discount Impact
        discount_impact = self.df[self.df['Discounts'] > 0]
        if len(discount_impact) > 0:
            axes[1, 1].scatter(discount_impact['Discounts'], discount_impact['Sold'], alpha=0.6)
            axes[1, 1].set_xlabel('Discount Amount ($)')
            axes[1, 1].set_ylabel('Units Sold')
            axes[1, 1].set_title('Discount Impact on Sales')
        else:
            axes[1, 1].text(0.5, 0.5, 'No discount data available', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Discount Impact on Sales')
        
        plt.tight_layout()
        plt.savefig('performance_metrics.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_predictive_insights(self):
        """Create predictive analytics insights"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Predictive Analytics & Insights', fontsize=16, fontweight='bold')
        
        # 1. Price Elasticity Analysis
        price_elasticity = self.df.groupby('Category').apply(
            lambda x: np.corrcoef(x['Total']/x['Sold'], x['Sold'])[0,1] if len(x) > 1 else 0
        ).fillna(0)
        
        axes[0, 0].bar(price_elasticity.index, price_elasticity.values)
        axes[0, 0].set_title('Price Elasticity by Category')
        axes[0, 0].set_xlabel('Category')
        axes[0, 0].set_ylabel('Price Elasticity')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Profitability vs Volume
        axes[0, 1].scatter(self.df['Sold'], self.df['Margin'], alpha=0.6)
        axes[0, 1].set_xlabel('Units Sold')
        axes[0, 1].set_ylabel('Profit Margin (%)')
        axes[0, 1].set_title('Profitability vs Sales Volume')
        
        # 3. Revenue Forecast (Simple trend)
        sorted_df = self.df.sort_values('Total', ascending=False)
        cumulative_revenue = sorted_df['Total'].cumsum()
        axes[1, 0].plot(range(len(cumulative_revenue)), cumulative_revenue, marker='o')
        axes[1, 0].set_xlabel('Product Rank')
        axes[1, 0].set_ylabel('Cumulative Revenue ($)')
        axes[1, 0].set_title('Revenue Concentration (Pareto Analysis)')
        
        # 4. Margin Distribution by Category
        margin_data = [self.df[self.df['Category'] == cat]['Margin'].dropna() 
                      for cat in self.df['Category'].unique()]
        axes[1, 1].boxplot(margin_data, labels=self.df['Category'].unique())
        axes[1, 1].set_title('Margin Distribution by Category')
        axes[1, 1].set_xlabel('Category')
        axes[1, 1].set_ylabel('Profit Margin (%)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('predictive_insights.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def print_summary_report(self):
        """Print a comprehensive summary report"""
        print("=" * 80)
        print("SUNSET NOVELTIES - SALES ANALYTICS REPORT")
        print("=" * 80)
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        print("📊 KEY METRICS:")
        print(f"   • Total Revenue: ${self.insights['total_revenue']:,.2f}")
        print(f"   • Total Units Sold: {self.insights['total_units_sold']:,}")
        print(f"   • Total Products: {self.insights['total_products']}")
        print(f"   • Average Profit Margin: {self.insights['avg_profit_margin']:.1f}%")
        print()
        
        print("🏆 TOP PERFORMERS:")
        print(f"   • Best Selling Product: {self.insights['top_product'][:50]}...")
        print(f"   • Top Product Revenue: ${self.insights['top_product_revenue']:,.2f}")
        print()
        
        print("⚠️  AREAS OF CONCERN:")
        print(f"   • Products with Negative Margins: {self.insights['negative_margin_products']}")
        print(f"   • High Margin Products (>50%): {self.insights['high_margin_products']}")
        print()
        
        print("📈 CATEGORY PERFORMANCE:")
        category_summary = self.df.groupby('Category').agg({
            'Total': ['sum', 'count'],
            'Margin': 'mean',
            'Sold': 'sum'
        }).round(2)
        
        for category in category_summary.index:
            revenue = category_summary.loc[category, ('Total', 'sum')]
            count = category_summary.loc[category, ('Total', 'count')]
            margin = category_summary.loc[category, ('Margin', 'mean')]
            units = category_summary.loc[category, ('Sold', 'sum')]
            print(f"   • {category}: ${revenue:,.0f} revenue, {count} products, {margin:.1f}% avg margin, {units:,} units")
        
        print()
        print("🎯 RECOMMENDATIONS:")
        print("   1. Focus on high-margin products for better profitability")
        print("   2. Review pricing strategy for products with negative margins")
        print("   3. Consider expanding successful product categories")
        print("   4. Implement targeted marketing for underperforming categories")
        print("   5. Optimize inventory based on sales volume and margin analysis")
        print("=" * 80)
    
    def generate_excel_report(self, filename='sales_analytics_report.xlsx'):
        """Generate a comprehensive Excel report"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': ['Total Revenue', 'Total Units Sold', 'Total Products', 
                          'Average Profit Margin', 'Negative Margin Products', 'High Margin Products'],
                'Value': [self.insights['total_revenue'], self.insights['total_units_sold'],
                         self.insights['total_products'], self.insights['avg_profit_margin'],
                         self.insights['negative_margin_products'], self.insights['high_margin_products']]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Category analysis
            category_analysis = self.df.groupby('Category').agg({
                'Total': ['sum', 'count'],
                'Margin': 'mean',
                'Sold': 'sum',
                'Cost': 'sum',
                'Profit': 'sum'
            }).round(2)
            category_analysis.to_excel(writer, sheet_name='Category Analysis')
            
            # Top products
            top_products = self.df.nlargest(20, 'Total')[['Description', 'Category', 'Sold', 'Total', 'Margin', 'Profit']]
            top_products.to_excel(writer, sheet_name='Top Products', index=False)
            
            # Products with negative margins
            negative_margin = self.df[self.df['Margin'] < 0][['Description', 'Category', 'Sold', 'Total', 'Margin', 'Cost']]
            negative_margin.to_excel(writer, sheet_name='Negative Margin Products', index=False)
            
            # Raw data
            self.df.to_excel(writer, sheet_name='Raw Data', index=False)
        
        print(f"📄 Excel report generated: {filename}")

def main():
    """Main function to run the analytics"""
    try:
        # Initialize analytics
        print("🔍 Loading sales data...")
        analytics = SalesAnalytics('reports_sales_listings_item.csv')
        
        # Generate reports
        print("📊 Generating revenue analysis...")
        analytics.create_revenue_analysis()
        
        print("📈 Creating performance metrics...")
        analytics.create_performance_metrics()
        
        print("🔮 Generating predictive insights...")
        analytics.create_predictive_insights()
        
        print("📋 Printing summary report...")
        analytics.print_summary_report()
        
        print("📄 Generating Excel report...")
        analytics.generate_excel_report()
        
        print("\n✅ Analytics complete! Check the generated files:")
        print("   • revenue_analysis.png")
        print("   • performance_metrics.png")
        print("   • predictive_insights.png")
        print("   • sales_analytics_report.xlsx")
        
    except FileNotFoundError:
        print("❌ Error: CSV file 'reports_sales_listings_item.csv' not found!")
        print("   Please ensure the file is in the same directory as this script.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 