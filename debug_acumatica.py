import mysql.connector
import pandas as pd

def debug_acumatica_data():
    """Debug Acumatica data loading issues"""
    print("🔍 Debugging Acumatica Data Loading")
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
        
        print("Step 1: Check Acumatica tables...")
        cursor.execute("SHOW TABLES LIKE '%InventoryItem%'")
        inventory_tables = cursor.fetchall()
        print(f"Found {len(inventory_tables)} inventory tables: {inventory_tables}")
        
        cursor.execute("SHOW TABLES LIKE '%SalesOrder%'")
        sales_tables = cursor.fetchall()
        print(f"Found {len(sales_tables)} sales tables: {sales_tables}")
        
        print("\nStep 2: Check InventoryItem data...")
        cursor.execute("SELECT COUNT(*) FROM InventoryItem")
        inventory_count = cursor.fetchone()[0]
        print(f"InventoryItem records: {inventory_count:,}")
        
        cursor.execute("SELECT COUNT(*) FROM InventoryItem WHERE Descr IS NOT NULL")
        inventory_with_desc = cursor.fetchone()[0]
        print(f"InventoryItem with descriptions: {inventory_with_desc:,}")
        
        print("\nStep 3: Check SalesOrderDetail data...")
        cursor.execute("SELECT COUNT(*) FROM SalesOrderDetail")
        sales_count = cursor.fetchone()[0]
        print(f"SalesOrderDetail records: {sales_count:,}")
        
        cursor.execute("SELECT COUNT(*) FROM SalesOrderDetail WHERE InventoryID IS NOT NULL")
        sales_with_inventory = cursor.fetchone()[0]
        print(f"SalesOrderDetail with InventoryID: {sales_with_inventory:,}")
        
        print("\nStep 4: Check for matching data...")
        cursor.execute("""
        SELECT COUNT(DISTINCT i.InventoryID) 
        FROM InventoryItem i 
        INNER JOIN SalesOrderDetail sod ON i.InventoryID = sod.InventoryID
        WHERE i.Descr IS NOT NULL
        """)
        matching_count = cursor.fetchone()[0]
        print(f"Matching InventoryItem-SalesOrderDetail: {matching_count:,}")
        
        print("\nStep 5: Test sample query...")
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
        LEFT JOIN SalesOrderDetail sod ON i.InventoryID = sod.InventoryID
        WHERE i.Descr IS NOT NULL
        GROUP BY i.InventoryID, i.Descr
        HAVING Total > 0
        ORDER BY Total DESC
        LIMIT 5
        """)
        
        results = cursor.fetchall()
        print(f"Sample query results: {len(results)} records")
        if results:
            print("Sample data:")
            for i, row in enumerate(results):
                print(f"  Row {i+1}: {row[:3]}...")
        else:
            print("No results found!")
        
        print("\nStep 6: Check data types...")
        cursor.execute("DESCRIBE InventoryItem")
        inventory_columns = cursor.fetchall()
        print("InventoryItem columns:")
        for col in inventory_columns:
            print(f"  {col[0]}: {col[1]}")
        
        cursor.execute("DESCRIBE SalesOrderDetail")
        sales_columns = cursor.fetchall()
        print("SalesOrderDetail columns:")
        for col in sales_columns[:5]:  # Show first 5
            print(f"  {col[0]}: {col[1]}")
        
        print("\nStep 7: Check for any sales data...")
        cursor.execute("SELECT SUM(ExtendedPrice) FROM SalesOrderDetail WHERE ExtendedPrice IS NOT NULL")
        total_sales = cursor.fetchone()[0]
        print(f"Total sales value: ${total_sales:,.2f}" if total_sales else "No sales data")
        
        cursor.execute("SELECT SUM(OrderQty) FROM SalesOrderDetail WHERE OrderQty IS NOT NULL")
        total_qty = cursor.fetchone()[0]
        print(f"Total quantity sold: {total_qty:,.0f}" if total_qty else "No quantity data")
        
        connection.close()
        print("\n🎉 Debug completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_acumatica_data() 