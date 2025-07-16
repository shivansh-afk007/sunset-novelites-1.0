import mysql.connector
import pandas as pd

def check_database_schema():
    """Check the database schema to identify correct column names"""
    
    rds_config = {
        'host': 'acumatica-rdspy.cda28gcg8vir.eu-north-1.rds.amazonaws.com',
        'user': 'admin',
        'password': 'Acumaticaadmin',
        'database': 'acumatica_data',
        'port': 3306,
        'connect_timeout': 30
    }
    
    try:
        print("🔍 Checking database schema...")
        conn = mysql.connector.connect(**rds_config)
        
        # Check Lightspeed tables
        print("\n📊 LIGHTSPEED TABLES:")
        lightspeed_tables = ['lightspeed_Item', 'lightspeed_OrderLine', 'lightspeed_ItemShop']
        
        for table in lightspeed_tables:
            try:
                cursor = conn.cursor()
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                print(f"\n{table}:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")
                cursor.close()
            except Exception as e:
                print(f"  Error checking {table}: {e}")
        
        # Check Acumatica tables
        print("\n📊 ACUMATICA TABLES:")
        acumatica_tables = ['InventoryItem', 'SalesOrderDetail']
        
        for table in acumatica_tables:
            try:
                cursor = conn.cursor()
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                print(f"\n{table}:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")
                cursor.close()
            except Exception as e:
                print(f"  Error checking {table}: {e}")
        
        # Sample data from key tables
        print("\n📊 SAMPLE DATA:")
        
        # Lightspeed Item sample
        try:
            df = pd.read_sql("SELECT * FROM lightspeed_Item LIMIT 3", conn)
            print("\nlightspeed_Item sample:")
            print(df.columns.tolist())
            print(df.head())
        except Exception as e:
            print(f"Error reading lightspeed_Item: {e}")
        
        # Lightspeed OrderLine sample
        try:
            df = pd.read_sql("SELECT * FROM lightspeed_OrderLine LIMIT 3", conn)
            print("\nlightspeed_OrderLine sample:")
            print(df.columns.tolist())
            print(df.head())
        except Exception as e:
            print(f"Error reading lightspeed_OrderLine: {e}")
        
        # InventoryItem sample
        try:
            df = pd.read_sql("SELECT * FROM InventoryItem LIMIT 3", conn)
            print("\nInventoryItem sample:")
            print(df.columns.tolist())
            print(df.head())
        except Exception as e:
            print(f"Error reading InventoryItem: {e}")
        
        # SalesOrderDetail sample
        try:
            df = pd.read_sql("SELECT * FROM SalesOrderDetail LIMIT 3", conn)
            print("\nSalesOrderDetail sample:")
            print(df.columns.tolist())
            print(df.head())
        except Exception as e:
            print(f"Error reading SalesOrderDetail: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    check_database_schema() 