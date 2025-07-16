import mysql.connector
import pandas as pd

def debug_restock_calculation():
    """Debug the restock calculation logic"""
    
    rds_config = {
        'host': 'acumatica-rdspy.cda28gcg8vir.eu-north-1.rds.amazonaws.com',
        'user': 'admin',
        'password': 'Acumaticaadmin',
        'database': 'acumatica_data',
        'port': 3306,
        'connect_timeout': 30
    }
    
    try:
        print("🔍 Debugging Restock Calculation...")
        conn = mysql.connector.connect(**rds_config)
        
        # Get warehouse data
        query = """
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
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        print(f"\n📊 Warehouse Data Analysis:")
        print(f"   - Total items: {len(df)}")
        print(f"   - Items with stock > 0: {len(df[df['Current_Stock'] > 0])}")
        print(f"   - Items with reorder point > 0: {len(df[df['Reorder_Point'] > 0])}")
        
        # Show sample data
        print(f"\n📋 Sample Items (Stock vs Reorder Point):")
        for idx, row in df.head(10).iterrows():
            stock = row['Current_Stock']
            reorder = row['Reorder_Point']
            needs_restock = stock <= reorder
            status = "⚠️ NEEDS RESTOCK" if needs_restock else "✅ OK"
            print(f"   - {row['Product_Name'][:50]:50} | Stock: {stock:6} | Reorder: {reorder:6} | {status}")
        
        # Analyze restock candidates
        restock_candidates = df[df['Current_Stock'] <= df['Reorder_Point']]
        print(f"\n🔍 Restock Analysis:")
        print(f"   - Items needing restock: {len(restock_candidates)}")
        
        if not restock_candidates.empty:
            print(f"   - Items that need restocking:")
            for idx, row in restock_candidates.head(5).iterrows():
                print(f"     * {row['Product_Name'][:40]:40} | Stock: {row['Current_Stock']:4} | Reorder: {row['Reorder_Point']:4}")
        else:
            print(f"   - No items currently need restocking")
        
        # Show distribution of stock vs reorder points
        print(f"\n📈 Stock vs Reorder Point Distribution:")
        print(f"   - Items with stock > reorder point: {len(df[df['Current_Stock'] > df['Reorder_Point']])}")
        print(f"   - Items with stock = reorder point: {len(df[df['Current_Stock'] == df['Reorder_Point']])}")
        print(f"   - Items with stock < reorder point: {len(df[df['Current_Stock'] < df['Reorder_Point']])}")
        
        # Show reorder point distribution
        print(f"\n📊 Reorder Point Analysis:")
        reorder_stats = df['Reorder_Point'].describe()
        print(f"   - Reorder point stats:")
        print(f"     * Min: {reorder_stats['min']}")
        print(f"     * Max: {reorder_stats['max']}")
        print(f"     * Mean: {reorder_stats['mean']:.2f}")
        print(f"     * Items with reorder point = 0: {len(df[df['Reorder_Point'] == 0])}")
        
        # Alternative restock logic suggestions
        print(f"\n💡 Alternative Restock Logic Suggestions:")
        print(f"   1. Current: Stock <= Reorder Point")
        print(f"   2. Alternative: Stock <= (Reorder Point + Safety Stock)")
        print(f"   3. Alternative: Stock <= 5 (Critical threshold)")
        print(f"   4. Alternative: Stock <= (Reorder Point * 0.5) (50% of reorder point)")
        
        # Test alternative thresholds
        critical_threshold = len(df[df['Current_Stock'] <= 5])
        half_reorder = len(df[df['Current_Stock'] <= (df['Reorder_Point'] * 0.5)])
        
        print(f"\n🔢 Alternative Restock Counts:")
        print(f"   - Current logic (Stock <= Reorder): {len(restock_candidates)}")
        print(f"   - Critical threshold (Stock <= 5): {critical_threshold}")
        print(f"   - Half reorder point (Stock <= Reorder*0.5): {half_reorder}")
        
    except Exception as e:
        print(f"Error debugging restock calculation: {e}")

if __name__ == "__main__":
    debug_restock_calculation() 