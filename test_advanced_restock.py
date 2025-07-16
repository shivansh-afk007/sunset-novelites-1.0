import mysql.connector
import pandas as pd

def test_advanced_restock_logic():
    """Test the advanced restock logic with purchase rate calculations"""
    
    rds_config = {
        'host': 'acumatica-rdspy.cda28gcg8vir.eu-north-1.rds.amazonaws.com',
        'user': 'admin',
        'password': 'Acumaticaadmin',
        'database': 'acumatica_data',
        'port': 3306,
        'connect_timeout': 30
    }
    
    try:
        print("🧪 Testing Advanced Restock Logic...")
        conn = mysql.connector.connect(**rds_config)
        
        # Get sample sales data to calculate purchase rates
        sales_query = """
        SELECT 
            i.RemoteID as Product_ID,
            i.Description as Product_Name,
            COALESCE(SUM(ol.Quantity), 0) as Total_Sold,
            COALESCE(MAX(is1.Qoh), 0) as Current_Stock,
            COALESCE(MAX(is1.ReorderPoint), 0) as Reorder_Point
        FROM lightspeed_Item i
        LEFT JOIN lightspeed_OrderLine ol ON i.RemoteID = ol.ItemID
        LEFT JOIN lightspeed_ItemShop is1 ON i.RemoteID = is1.ItemID
        WHERE i.Description IS NOT NULL
        GROUP BY i.RemoteID, i.Description
        HAVING Current_Stock > 0
        ORDER BY Total_Sold DESC
        LIMIT 20
        """
        
        df = pd.read_sql(sales_query, conn)
        conn.close()
        
        print(f"\n📊 Sample Products Analysis:")
        print(f"   - Total products: {len(df)}")
        
        # Calculate purchase rates (assuming 90-day period)
        days_period = 90
        df['Daily_Purchase_Rate'] = df['Total_Sold'] / days_period
        df['Days_Until_Stockout'] = df.apply(
            lambda row: row['Current_Stock'] / row['Daily_Purchase_Rate'] if row['Daily_Purchase_Rate'] > 0 else 365, axis=1
        )
        df['Needs_Restock'] = df['Days_Until_Stockout'] <= 30
        
        # Show results
        print(f"\n📋 Sample Products (Advanced Restock Logic):")
        for idx, row in df.head(10).iterrows():
            stock = row['Current_Stock']
            sold = row['Total_Sold']
            rate = row['Daily_Purchase_Rate']
            days = row['Days_Until_Stockout']
            needs_restock = row['Needs_Restock']
            status = "⚠️ NEEDS RESTOCK" if needs_restock else "✅ OK"
            
            print(f"   - {row['Product_Name'][:40]:40} | Stock: {stock:6} | Sold: {sold:6} | Rate: {rate:.1f}/day | Days: {days:.1f} | {status}")
        
        # Summary statistics
        needs_restock_count = len(df[df['Needs_Restock']])
        avg_purchase_rate = df['Daily_Purchase_Rate'].mean()
        avg_days_until_stockout = df['Days_Until_Stockout'].mean()
        
        print(f"\n📈 Advanced Restock Summary:")
        print(f"   - Products needing restock (30-day rule): {needs_restock_count}")
        print(f"   - Average daily purchase rate: {avg_purchase_rate:.2f} units/day")
        print(f"   - Average days until stockout: {avg_days_until_stockout:.1f} days")
        
        # Show products that need restocking
        restock_items = df[df['Needs_Restock']]
        if not restock_items.empty:
            print(f"\n🔍 Products Needing Restock:")
            for idx, row in restock_items.head(5).iterrows():
                recommendation = f"Order {max(10, int(row['Daily_Purchase_Rate'] * 30))} units"
                print(f"   - {row['Product_Name'][:40]:40} | Stock: {row['Current_Stock']:4} | Rate: {row['Daily_Purchase_Rate']:.1f}/day | Days: {row['Days_Until_Stockout']:.1f} | {recommendation}")
        else:
            print(f"\n✅ No products need restocking (all have >30 days stock)")
        
        # Compare with old logic
        old_logic_count = len(df[df['Current_Stock'] <= df['Reorder_Point']])
        print(f"\n🔄 Logic Comparison:")
        print(f"   - Old logic (Stock <= Reorder Point): {old_logic_count} products")
        print(f"   - New logic (30-day rule): {needs_restock_count} products")
        print(f"   - Difference: {needs_restock_count - old_logic_count} products")
        
    except Exception as e:
        print(f"Error testing advanced restock logic: {e}")

if __name__ == "__main__":
    test_advanced_restock_logic() 