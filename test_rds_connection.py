import mysql.connector
import pandas as pd
import time

def test_rds_connection():
    """Test connection to AWS RDS MySQL instance"""
    print("🔍 Testing AWS RDS Connection")
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
        print("Step 1: Testing RDS connection...")
        connection = mysql.connector.connect(**rds_config)
        print("✅ RDS connection successful!")
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("\nStep 2: Testing database list...")
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print(f"✅ Found {len(databases)} databases:")
            for db in databases:
                print(f"   - {db[0]}")
            
            print("\nStep 3: Testing acumatica_data tables...")
            cursor.execute("USE acumatica_data")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✅ Found {len(tables)} tables in acumatica_data:")
            
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
            
            print(f"\n   Lightspeed tables ({len(lightspeed_tables)}):")
            for table in lightspeed_tables[:10]:  # Show first 10
                print(f"     - {table}")
            if len(lightspeed_tables) > 10:
                print(f"     ... and {len(lightspeed_tables) - 10} more")
            
            print(f"\n   Acumatica tables ({len(acumatica_tables)}):")
            for table in acumatica_tables:
                print(f"     - {table}")
            
            if other_tables:
                print(f"\n   Other tables ({len(other_tables)}):")
                for table in other_tables[:5]:
                    print(f"     - {table}")
            
            print("\nStep 4: Testing sample queries...")
            
            # Test Lightspeed tables
            if lightspeed_tables:
                print("\n   Testing Lightspeed data:")
                # Find item table
                item_table = None
                for table in lightspeed_tables:
                    if 'item' in table.lower():
                        item_table = table
                        break
                
                if item_table:
                    print(f"     Testing {item_table}...")
                    cursor.execute(f"SELECT COUNT(*) FROM {item_table}")
                    count = cursor.fetchone()[0]
                    print(f"     ✅ {item_table}: {count:,} records")
                    
                    # Show sample data
                    cursor.execute(f"SELECT * FROM {item_table} LIMIT 3")
                    sample_data = cursor.fetchall()
                    if sample_data:
                        print(f"     Sample data structure:")
                        for i, row in enumerate(sample_data):
                            print(f"       Row {i+1}: {row[:3]}...")  # Show first 3 columns
            
            # Test Acumatica tables
            if 'InventoryItem' in acumatica_tables:
                print("\n   Testing Acumatica data:")
                cursor.execute("SELECT COUNT(*) FROM InventoryItem")
                count = cursor.fetchone()[0]
                print(f"     ✅ InventoryItem: {count:,} records")
                
                cursor.execute("SELECT * FROM InventoryItem LIMIT 3")
                sample_data = cursor.fetchall()
                if sample_data:
                    print(f"     Sample data structure:")
                    for i, row in enumerate(sample_data):
                        print(f"       Row {i+1}: {row[:3]}...")
            
            print("\nStep 5: Testing performance...")
            start_time = time.time()
            
            # Test a simple aggregation query
            if lightspeed_tables and item_table:
                cursor.execute(f"SELECT COUNT(*) FROM {item_table}")
                cursor.fetchone()
            
            if 'InventoryItem' in acumatica_tables:
                cursor.execute("SELECT COUNT(*) FROM InventoryItem")
                cursor.fetchone()
            
            end_time = time.time()
            print(f"✅ Query performance test completed in {end_time - start_time:.2f}s")
            
            connection.close()
            print("\n🎉 All RDS tests completed successfully!")
            
        else:
            print("❌ Connection not established")
            
    except mysql.connector.Error as e:
        print(f"❌ MySQL Error: {e}")
    except Exception as e:
        print(f"❌ General Error: {e}")

if __name__ == "__main__":
    test_rds_connection() 