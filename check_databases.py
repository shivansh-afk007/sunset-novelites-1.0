import mysql.connector
import pandas as pd
from sqlalchemy import create_engine, text
import sys

def check_mysql_databases():
    """Check MySQL databases and their sizes"""
    try:
        # Try to connect to MySQL
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            connect_timeout=5
        )
        
        if connection.is_connected():
            print("✅ Successfully connected to MySQL!")
            cursor = connection.cursor()
            
            # Get list of databases
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            
            print(f"\n📊 Found {len(databases)} databases:")
            print("-" * 50)
            
            total_size = 0
            database_info = []
            
            for db in databases:
                db_name = db[0]
                
                # Skip system databases
                if db_name in ['information_schema', 'mysql', 'performance_schema', 'sys']:
                    continue
                
                try:
                    # Connect to specific database
                    db_connection = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='',
                        database=db_name,
                        connect_timeout=5
                    )
                    
                    if db_connection.is_connected():
                        db_cursor = db_connection.cursor()
                        
                        # Get database size
                        db_cursor.execute("""
                            SELECT 
                                table_schema AS 'Database',
                                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)',
                                COUNT(*) AS 'Tables'
                            FROM information_schema.tables 
                            WHERE table_schema = %s
                            GROUP BY table_schema
                        """, (db_name,))
                        
                        size_result = db_cursor.fetchone()
                        
                        if size_result:
                            size_mb = size_result[1] if size_result[1] else 0
                            table_count = size_result[2] if size_result[2] else 0
                        else:
                            size_mb = 0
                            table_count = 0
                        
                        # Get table details
                        db_cursor.execute("SHOW TABLES")
                        tables = db_cursor.fetchall()
                        
                        print(f"📁 Database: {db_name}")
                        print(f"   Size: {size_mb} MB")
                        print(f"   Tables: {table_count}")
                        
                        if tables:
                            print(f"   Tables found:")
                            for table in tables[:5]:  # Show first 5 tables
                                print(f"     - {table[0]}")
                            if len(tables) > 5:
                                print(f"     ... and {len(tables) - 5} more")
                        
                        database_info.append({
                            'Database': db_name,
                            'Size_MB': size_mb,
                            'Tables': table_count
                        })
                        
                        total_size += size_mb
                        db_connection.close()
                        
                except Exception as e:
                    print(f"❌ Error accessing database {db_name}: {e}")
            
            print("-" * 50)
            print(f"📈 Total size of user databases: {total_size:.2f} MB")
            
            # Create summary DataFrame
            if database_info:
                df = pd.DataFrame(database_info)
                print(f"\n📋 Database Summary:")
                print(df.to_string(index=False))
                
                # Check for our specific databases
                synchub_exists = any(db['Database'] == 'synchub_data' for db in database_info)
                acumatica_exists = any(db['Database'] == 'acumatica_data' for db in database_info)
                
                print(f"\n🎯 Target Databases Status:")
                print(f"   synchub_data: {'✅ Found' if synchub_exists else '❌ Not found'}")
                print(f"   acumatica_data: {'✅ Found' if acumatica_exists else '❌ Not found'}")
            
            connection.close()
            
        else:
            print("❌ Could not connect to MySQL")
            
    except mysql.connector.Error as e:
        print(f"❌ MySQL Error: {e}")
        print("\n💡 Possible solutions:")
        print("1. Make sure MySQL is installed and running")
        print("2. Check if MySQL service is started")
        print("3. Verify connection credentials")
        print("4. Try using XAMPP or similar if MySQL is installed there")
        
    except Exception as e:
        print(f"❌ General Error: {e}")

if __name__ == "__main__":
    print("🔍 Checking MySQL Databases and Sizes...")
    print("=" * 50)
    check_mysql_databases() 