import mysql.connector
import pandas as pd

def explore_rds_schema():
    """Explore the RDS database schema to understand table structures"""
    print("🔍 Exploring RDS Database Schema")
    print("=" * 50)
    
    # RDS Connection Details
    rds_config = {
        'host': 'acumatica-rdspy.cda28gcg8vir.eu-north-1.rds.amazonaws.com',
        'user': 'admin',
        'password': 'Acumaticaadmin',
        'database': 'acumatica_data',
        'port': 3306,
        'connect_timeout': 10
    }
    
    try:
        connection = mysql.connector.connect(**rds_config)
        cursor = connection.cursor()
        
        print("Step 1: Getting all tables...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        # Categorize tables
        lightspeed_tables = []
        acumatica_tables = []
        other_tables = []
        
        for table in tables:
            table_name = table[0]
            if table_name.startswith('lightspeed_'):
                lightspeed_tables.append(table_name)
            elif table_name in ['Customer', 'InventoryItem', 'SalesOrder', 'SalesOrderDetail', 'Bill', 'BillDetail']:
                acumatica_tables.append(table_name)
            else:
                other_tables.append(table_name)
        
        print(f"\nFound {len(lightspeed_tables)} Lightspeed tables")
        print(f"Found {len(acumatica_tables)} Acumatica tables")
        print(f"Found {len(other_tables)} other tables")
        
        print("\nStep 2: Exploring key Lightspeed tables...")
        key_lightspeed_tables = [
            'lightspeed_Item', 'lightspeed_OrderLine', 'lightspeed_ItemShop', 
            'lightspeed_Sale', 'lightspeed_Customer', 'lightspeed_Category'
        ]
        
        for table_name in key_lightspeed_tables:
            if table_name in [t[0] for t in tables]:
                print(f"\n📋 {table_name}:")
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                print(f"   Columns ({len(columns)}):")
                for col in columns:
                    print(f"     - {col[0]} ({col[1]})")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"   Records: {count:,}")
                
                # Show sample data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
                sample = cursor.fetchall()
                if sample:
                    print(f"   Sample data:")
                    for i, row in enumerate(sample):
                        print(f"     Row {i+1}: {row[:3]}...")
        
        print("\nStep 3: Exploring Acumatica tables...")
        for table_name in acumatica_tables:
            print(f"\n📋 {table_name}:")
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            print(f"   Columns ({len(columns)}):")
            for col in columns:
                print(f"     - {col[0]} ({col[1]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   Records: {count:,}")
            
            # Show sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
            sample = cursor.fetchall()
            if sample:
                print(f"   Sample data:")
                for i, row in enumerate(sample):
                    print(f"     Row {i+1}: {row[:3]}...")
        
        print("\nStep 4: Testing sample queries for dashboard...")
        
        # Test Lightspeed sales data
        if 'lightspeed_Item' in [t[0] for t in tables] and 'lightspeed_OrderLine' in [t[0] for t in tables]:
            print("\n   Testing Lightspeed sales query:")
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
                0 as Cost,
                COALESCE(SUM(ol.Total), 0) as Profit,
                100 as Margin
            FROM lightspeed_Item i
            LEFT JOIN lightspeed_OrderLine ol ON i.RemoteID = ol.ItemID
            LEFT JOIN lightspeed_ItemShop is1 ON i.RemoteID = is1.ItemID
            WHERE i.Description IS NOT NULL
            GROUP BY i.RemoteID, i.Description
            LIMIT 5
            """
            
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                print(f"     ✅ Query successful, found {len(results)} records")
                if results:
                    print(f"     Sample result: {results[0]}")
            except Exception as e:
                print(f"     ❌ Query failed: {e}")
        
        # Test Acumatica sales data
        if 'InventoryItem' in acumatica_tables and 'SalesOrderDetail' in acumatica_tables:
            print("\n   Testing Acumatica sales query:")
            query = """
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
            LIMIT 5
            """
            
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                print(f"     ✅ Query successful, found {len(results)} records")
                if results:
                    print(f"     Sample result: {results[0]}")
            except Exception as e:
                print(f"     ❌ Query failed: {e}")
        
        connection.close()
        print("\n🎉 Schema exploration completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    explore_rds_schema() 