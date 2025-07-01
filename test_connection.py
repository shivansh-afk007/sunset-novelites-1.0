import mysql.connector
import time

def test_mysql_connection():
    print("🔍 Testing MySQL Connection Step by Step")
    print("=" * 50)
    
    print("Step 1: Testing basic connection...")
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            connect_timeout=5
        )
        print("✅ Basic connection successful!")
        
        if connection.is_connected():
            cursor = connection.cursor()
            print("Step 2: Testing database list...")
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print(f"✅ Found {len(databases)} databases:")
            for db in databases:
                print(f"   - {db[0]}")
            
            print("\nStep 3: Testing synchub_data connection...")
            synchub_conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='synchub_data',
                connect_timeout=5
            )
            print("✅ synchub_data connection successful!")
            
            if synchub_conn.is_connected():
                synchub_cursor = synchub_conn.cursor()
                print("Step 4: Testing simple query...")
                start_time = time.time()
                synchub_cursor.execute("SELECT COUNT(*) FROM item")
                count = synchub_cursor.fetchone()[0]
                end_time = time.time()
                print(f"✅ Query completed in {end_time - start_time:.2f}s")
                print(f"   Item count: {count:,}")
                
                print("Step 5: Testing complex query...")
                start_time = time.time()
                synchub_cursor.execute("""
                    SELECT COUNT(*) 
                    FROM item i 
                    LEFT JOIN orderline ol ON i.RemoteID = ol.ItemID 
                    WHERE i.Description IS NOT NULL
                """)
                count = synchub_cursor.fetchone()[0]
                end_time = time.time()
                print(f"✅ Complex query completed in {end_time - start_time:.2f}s")
                print(f"   Result: {count:,}")
                
                synchub_conn.close()
            
            print("\nStep 6: Testing acumatica_data connection...")
            acumatica_conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='acumatica_data',
                connect_timeout=5
            )
            print("✅ acumatica_data connection successful!")
            
            if acumatica_conn.is_connected():
                acumatica_cursor = acumatica_conn.cursor()
                print("Step 7: Testing acumatica query...")
                start_time = time.time()
                acumatica_cursor.execute("SELECT COUNT(*) FROM inventoryitem")
                count = acumatica_cursor.fetchone()[0]
                end_time = time.time()
                print(f"✅ Query completed in {end_time - start_time:.2f}s")
                print(f"   Inventory item count: {count:,}")
                
                acumatica_conn.close()
            
            connection.close()
            print("\n🎉 All tests completed successfully!")
            
        else:
            print("❌ Connection not established")
            
    except mysql.connector.Error as e:
        print(f"❌ MySQL Error: {e}")
    except Exception as e:
        print(f"❌ General Error: {e}")

if __name__ == "__main__":
    test_mysql_connection() 