import mysql.connector
import pandas as pd

def fix_acumatica_join():
    """Fix the JOIN issue between InventoryItem and SalesOrderDetail"""
    print("🔧 Fixing Acumatica JOIN Issue")
    print("=" * 50)
    
    # RDS Connection Details
    rds_config = {
        'host': 'acumatica-rdspy.cda28gcg8vir.eu-north-1.rds.amazonaws.com',
        'user': 'admin',
        'password': 'Acumaticaadmin',
        'database': 'acumatica_data',
        'port': 3306,
        'connect_timeout': 30
    }
    
    try:
        connection = mysql.connector.connect(**rds_config)
        cursor = connection.cursor()
        
        print("Step 1: Check data types and sample values...")
        
        # Check InventoryItem InventoryID
        cursor.execute("SELECT InventoryID, Descr FROM InventoryItem LIMIT 5")
        inventory_samples = cursor.fetchall()
        print("InventoryItem samples:")
        for row in inventory_samples:
            print(f"  InventoryID: {row[0]} (type: {type(row[0])}), Descr: {row[1][:50]}...")
        
        # Check SalesOrderDetail InventoryID
        cursor.execute("SELECT InventoryID, LineNbr FROM SalesOrderDetail LIMIT 5")
        sales_samples = cursor.fetchall()
        print("SalesOrderDetail samples:")
        for row in sales_samples:
            print(f"  InventoryID: {row[0]} (type: {type(row[0])}), LineNbr: {row[1]}")
        
        print("\nStep 2: Check for NULL values...")
        cursor.execute("SELECT COUNT(*) FROM InventoryItem WHERE InventoryID IS NULL")
        null_inventory = cursor.fetchone()[0]
        print(f"InventoryItem with NULL InventoryID: {null_inventory}")
        
        cursor.execute("SELECT COUNT(*) FROM SalesOrderDetail WHERE InventoryID IS NULL")
        null_sales = cursor.fetchone()[0]
        print(f"SalesOrderDetail with NULL InventoryID: {null_sales}")
        
        print("\nStep 3: Check for string vs integer mismatch...")
        cursor.execute("""
        SELECT COUNT(*) 
        FROM InventoryItem i 
        INNER JOIN SalesOrderDetail sod ON CAST(i.InventoryID AS CHAR) = CAST(sod.InventoryID AS CHAR)
        WHERE i.Descr IS NOT NULL
        """)
        string_join_count = cursor.fetchone()[0]
        print(f"String JOIN matches: {string_join_count:,}")
        
        print("\nStep 4: Check for different column names...")
        cursor.execute("DESCRIBE SalesOrderDetail")
        sales_columns = cursor.fetchall()
        print("SalesOrderDetail columns:")
        for col in sales_columns:
            print(f"  {col[0]}: {col[1]}")
        
        print("\nStep 5: Try alternative JOIN approaches...")
        
        # Try with string conversion
        cursor.execute("""
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
            100 as Margin
        FROM InventoryItem i
        INNER JOIN SalesOrderDetail sod ON CAST(i.InventoryID AS CHAR) = CAST(sod.InventoryID AS CHAR)
        WHERE i.Descr IS NOT NULL
        GROUP BY i.InventoryID, i.Descr
        HAVING Total > 0
        ORDER BY Total DESC
        LIMIT 5
        """)
        
        results = cursor.fetchall()
        print(f"String JOIN results: {len(results)} records")
        if results:
            print("Sample data:")
            for i, row in enumerate(results):
                print(f"  Row {i+1}: {row[:3]}...")
        
        print("\nStep 6: Check if there are any sales without inventory items...")
        cursor.execute("""
        SELECT COUNT(DISTINCT sod.InventoryID) 
        FROM SalesOrderDetail sod 
        LEFT JOIN InventoryItem i ON CAST(sod.InventoryID AS CHAR) = CAST(i.InventoryID AS CHAR)
        WHERE i.InventoryID IS NULL
        """)
        orphaned_sales = cursor.fetchone()[0]
        print(f"Sales with no matching inventory items: {orphaned_sales:,}")
        
        print("\nStep 7: Check for any successful matches...")
        cursor.execute("""
        SELECT 
            i.Descr as Description,
            i.InventoryID as `System ID`,
            COUNT(sod.InventoryID) as Sales_Count,
            SUM(sod.OrderQty) as Total_Qty,
            SUM(sod.ExtendedPrice) as Total_Revenue
        FROM InventoryItem i
        LEFT JOIN SalesOrderDetail sod ON CAST(i.InventoryID AS CHAR) = CAST(sod.InventoryID AS CHAR)
        WHERE i.Descr IS NOT NULL
        GROUP BY i.InventoryID, i.Descr
        HAVING Sales_Count > 0
        ORDER BY Total_Revenue DESC
        LIMIT 10
        """)
        
        matches = cursor.fetchall()
        print(f"Successful matches: {len(matches)} records")
        if matches:
            print("Top matches:")
            for i, row in enumerate(matches[:3]):
                print(f"  {i+1}. {row[0][:50]}... - ${row[4]:,.2f}")
        
        connection.close()
        print("\n🎉 JOIN investigation completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_acumatica_join() 