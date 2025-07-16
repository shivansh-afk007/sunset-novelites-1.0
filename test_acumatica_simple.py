import mysql.connector
import pandas as pd
from mysql.connector import Error

# RDS connection details
RDS_CONFIG = {
    'host': 'acumatica-rdspy.cda28gcg8vir.eu-north-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'Acumaticaadmin',
    'database': 'acumatica_data'
}

def test_acumatica_connection():
    """Test basic connection to Acumatica tables"""
    try:
        conn = mysql.connector.connect(**RDS_CONFIG)
        cursor = conn.cursor()
        
        print("🔍 TESTING ACUMATICA CONNECTION")
        print("=" * 50)
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        acumatica_tables = [t for t in tables if not t.startswith('lightspeed_')]
        print(f"Found {len(acumatica_tables)} Acumatica tables:")
        for table in acumatica_tables:
            print(f"  - {table}")
        
        print("\n" + "=" * 50)
        
        # Test InventoryItem table
        if 'InventoryItem' in acumatica_tables:
            print("\n📊 INVENTORY ITEM TABLE")
            cursor.execute("SELECT COUNT(*) FROM InventoryItem")
            count = cursor.fetchone()[0]
            print(f"Total rows: {count}")
            
            if count > 0:
                cursor.execute("SELECT * FROM InventoryItem LIMIT 3")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                print(f"Columns: {columns}")
                print("Sample data:")
                for i, row in enumerate(rows, 1):
                    print(f"  Row {i}: {row}")
        
        # Test SalesOrderDetail table
        if 'SalesOrderDetail' in acumatica_tables:
            print("\n📊 SALES ORDER DETAIL TABLE")
            cursor.execute("SELECT COUNT(*) FROM SalesOrderDetail")
            count = cursor.fetchone()[0]
            print(f"Total rows: {count}")
            
            if count > 0:
                cursor.execute("SELECT * FROM SalesOrderDetail LIMIT 3")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                print(f"Columns: {columns}")
                print("Sample data:")
                for i, row in enumerate(rows, 1):
                    print(f"  Row {i}: {row}")
        
        # Test the join that's being used
        print("\n🔍 TESTING THE JOIN")
        print("=" * 50)
        
        # Test the exact query from the dashboard
        query = """
        SELECT 
            i.Descr as Description,
            i.InventoryCD as `System ID`,
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
        INNER JOIN SalesOrderDetail sod ON i.InventoryCD = sod.InventoryID
        WHERE i.Descr IS NOT NULL
        GROUP BY i.InventoryCD, i.Descr
        HAVING Total > 0
        ORDER BY Total DESC
        """
        
        try:
            df = pd.read_sql(query, conn)
            print(f"Join query result: {len(df)} records")
            if len(df) > 0:
                print("Sample joined data:")
                print(df.head(3))
        except Exception as e:
            print(f"Error in join query: {e}")
        
        # Test individual table counts
        print("\n📊 INDIVIDUAL TABLE COUNTS")
        print("=" * 50)
        
        for table in ['InventoryItem', 'SalesOrderDetail']:
            if table in acumatica_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count} rows")
        
        conn.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_acumatica_connection() 