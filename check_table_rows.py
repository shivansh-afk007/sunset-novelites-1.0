import mysql.connector
import pandas as pd
from sqlalchemy import create_engine, text
import sys

def count_all_table_rows():
    """Count total rows in all tables across databases"""
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
            
            print(f"\n📊 Analyzing {len(databases)} databases for row counts...")
            print("=" * 80)
            
            total_rows_all_dbs = 0
            database_summary = []
            
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
                        
                        # Get all tables in the database
                        db_cursor.execute("SHOW TABLES")
                        tables = db_cursor.fetchall()
                        
                        db_total_rows = 0
                        table_details = []
                        
                        print(f"\n📁 Database: {db_name}")
                        print(f"   Tables found: {len(tables)}")
                        print("-" * 60)
                        
                        for table in tables:
                            table_name = table[0]
                            try:
                                # Count rows in table
                                db_cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                                row_count = db_cursor.fetchone()[0]
                                
                                # Get table size info
                                db_cursor.execute(f"""
                                    SELECT 
                                        ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size_MB'
                                    FROM information_schema.tables 
                                    WHERE table_schema = '{db_name}' AND table_name = '{table_name}'
                                """)
                                size_result = db_cursor.fetchone()
                                size_mb = size_result[0] if size_result and size_result[0] else 0
                                
                                table_details.append({
                                    'Table': table_name,
                                    'Rows': row_count,
                                    'Size_MB': size_mb
                                })
                                
                                db_total_rows += row_count
                                
                                # Print table info (only if rows > 0 or it's a key table)
                                if row_count > 0 or table_name in ['item', 'inventoryitem', 'orderline', 'salesorderdetail', 'itemshop']:
                                    print(f"   📋 {table_name:<25} | Rows: {row_count:>8,} | Size: {size_mb:>6.2f} MB")
                                
                            except Exception as e:
                                print(f"   ❌ Error counting rows in {table_name}: {e}")
                        
                        # Sort table details by row count (descending)
                        table_details.sort(key=lambda x: x['Rows'], reverse=True)
                        
                        print(f"\n   📈 Database Summary:")
                        print(f"      Total Rows: {db_total_rows:,}")
                        print(f"      Total Tables: {len(tables)}")
                        
                        # Show top 5 tables by row count
                        if table_details:
                            print(f"      Top 5 Tables by Row Count:")
                            for i, table in enumerate(table_details[:5]):
                                print(f"        {i+1}. {table['Table']:<20} | {table['Rows']:,} rows")
                        
                        database_summary.append({
                            'Database': db_name,
                            'Total_Rows': db_total_rows,
                            'Total_Tables': len(tables),
                            'Top_Table': table_details[0]['Table'] if table_details else 'N/A',
                            'Top_Table_Rows': table_details[0]['Rows'] if table_details else 0
                        })
                        
                        total_rows_all_dbs += db_total_rows
                        db_connection.close()
                        
                except Exception as e:
                    print(f"❌ Error accessing database {db_name}: {e}")
            
            print("\n" + "=" * 80)
            print(f"🎯 FINAL SUMMARY")
            print("=" * 80)
            print(f"📊 Total Rows Across All Databases: {total_rows_all_dbs:,}")
            print(f"📁 Total Databases Analyzed: {len(database_summary)}")
            
            # Create summary DataFrame
            if database_summary:
                df = pd.DataFrame(database_summary)
                print(f"\n📋 Database Summary:")
                print(df.to_string(index=False))
                
                # Check for our specific databases
                synchub_data = next((db for db in database_summary if db['Database'] == 'synchub_data'), None)
                acumatica_data = next((db for db in database_summary if db['Database'] == 'acumatica_data'), None)
                
                print(f"\n🎯 Target Databases Analysis:")
                if synchub_data:
                    print(f"   synchub_data:")
                    print(f"     - Total Rows: {synchub_data['Total_Rows']:,}")
                    print(f"     - Tables: {synchub_data['Total_Tables']}")
                    print(f"     - Largest Table: {synchub_data['Top_Table']} ({synchub_data['Top_Table_Rows']:,} rows)")
                
                if acumatica_data:
                    print(f"   acumatica_data:")
                    print(f"     - Total Rows: {acumatica_data['Total_Rows']:,}")
                    print(f"     - Tables: {acumatica_data['Total_Tables']}")
                    print(f"     - Largest Table: {acumatica_data['Top_Table']} ({acumatica_data['Top_Table_Rows']:,} rows)")
                
                # Calculate percentages
                if total_rows_all_dbs > 0:
                    if synchub_data:
                        synchub_pct = (synchub_data['Total_Rows'] / total_rows_all_dbs) * 100
                        print(f"     - Percentage of total: {synchub_pct:.1f}%")
                    
                    if acumatica_data:
                        acumatica_pct = (acumatica_data['Total_Rows'] / total_rows_all_dbs) * 100
                        print(f"     - Percentage of total: {acumatica_pct:.1f}%")
            
            connection.close()
            
        else:
            print("❌ Could not connect to MySQL")
            
    except mysql.connector.Error as e:
        print(f"❌ MySQL Error: {e}")
        print("\n💡 Possible solutions:")
        print("1. Make sure MySQL is installed and running")
        print("2. Check if MySQL service is started")
        print("3. Verify connection credentials")
        
    except Exception as e:
        print(f"❌ General Error: {e}")

if __name__ == "__main__":
    print("🔍 Counting Total Rows in All Tables...")
    print("=" * 80)
    count_all_table_rows() 