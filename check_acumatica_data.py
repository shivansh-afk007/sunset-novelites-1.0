import mysql.connector
import pandas as pd
from mysql.connector import Error

# RDS connection details
RDS_CONFIG = {
    'host': 'acumatica-rdspy.cda28gcg8vir.eu-north-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'SunsetNovelties2024!',
    'database': 'acumatica_data'
}

def check_acumatica_tables():
    """Check all Acumatica tables and their data"""
    try:
        conn = mysql.connector.connect(**RDS_CONFIG)
        cursor = conn.cursor()
        
        print("🔍 CHECKING ACUMATICA TABLES AND DATA")
        print("=" * 50)
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        acumatica_tables = [t for t in tables if not t.startswith('lightspeed_')]
        print(f"Found {len(acumatica_tables)} Acumatica tables:")
        for table in acumatica_tables:
            print(f"  - {table}")
        
        print("\n" + "=" * 50)
        
        # Check each Acumatica table
        for table in acumatica_tables:
            print(f"\n📊 TABLE: {table}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  Total rows: {count}")
            
            if count > 0:
                # Get sample data
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                print(f"  Columns: {columns}")
                print("  Sample data:")
                for i, row in enumerate(rows, 1):
                    print(f"    Row {i}: {row}")
            
            print("-" * 30)
        
        conn.close()
        
    except Error as e:
        print(f"Error: {e}")

def check_inventory_item_data():
    """Specifically check InventoryItem table"""
    try:
        conn = mysql.connector.connect(**RDS_CONFIG)
        cursor = conn.cursor()
        
        print("\n🔍 DETAILED INVENTORY ITEM ANALYSIS")
        print("=" * 50)
        
        # Check InventoryItem table
        cursor.execute("SELECT COUNT(*) FROM InventoryItem")
        count = cursor.fetchone()[0]
        print(f"InventoryItem total rows: {count}")
        
        if count > 0:
            # Get column info
            cursor.execute("DESCRIBE InventoryItem")
            columns = cursor.fetchall()
            print("\nInventoryItem columns:")
            for col in columns:
                print(f"  {col[0]} - {col[1]} - {col[2]}")
            
            # Get sample data
            cursor.execute("SELECT * FROM InventoryItem LIMIT 5")
            sample_data = cursor.fetchall()
            print("\nSample InventoryItem data:")
            for i, row in enumerate(sample_data, 1):
                print(f"  Row {i}: {row}")
            
            # Check for InventoryCD values
            cursor.execute("SELECT InventoryCD, COUNT(*) FROM InventoryItem GROUP BY InventoryCD LIMIT 10")
            inventory_codes = cursor.fetchall()
            print(f"\nSample InventoryCD values (first 10):")
            for code, count in inventory_codes:
                print(f"  {code}: {count} occurrences")
        
        conn.close()
        
    except Error as e:
        print(f"Error: {e}")

def check_sales_order_detail_data():
    """Specifically check SalesOrderDetail table"""
    try:
        conn = mysql.connector.connect(**RDS_CONFIG)
        cursor = conn.cursor()
        
        print("\n🔍 DETAILED SALES ORDER DETAIL ANALYSIS")
        print("=" * 50)
        
        # Check SalesOrderDetail table
        cursor.execute("SELECT COUNT(*) FROM SalesOrderDetail")
        count = cursor.fetchone()[0]
        print(f"SalesOrderDetail total rows: {count}")
        
        if count > 0:
            # Get column info
            cursor.execute("DESCRIBE SalesOrderDetail")
            columns = cursor.fetchall()
            print("\nSalesOrderDetail columns:")
            for col in columns:
                print(f"  {col[0]} - {col[1]} - {col[2]}")
            
            # Get sample data
            cursor.execute("SELECT * FROM SalesOrderDetail LIMIT 5")
            sample_data = cursor.fetchall()
            print("\nSample SalesOrderDetail data:")
            for i, row in enumerate(sample_data, 1):
                print(f"  Row {i}: {row}")
            
            # Check for InventoryID values
            cursor.execute("SELECT InventoryID, COUNT(*) FROM SalesOrderDetail GROUP BY InventoryID LIMIT 10")
            inventory_ids = cursor.fetchall()
            print(f"\nSample InventoryID values (first 10):")
            for inv_id, count in inventory_ids:
                print(f"  {inv_id}: {count} occurrences")
        
        conn.close()
        
    except Error as e:
        print(f"Error: {e}")

def test_join_conditions():
    """Test different join conditions to see what matches"""
    try:
        conn = mysql.connector.connect(**RDS_CONFIG)
        cursor = conn.cursor()
        
        print("\n🔍 TESTING JOIN CONDITIONS")
        print("=" * 50)
        
        # Test 1: Join on InventoryCD = InventoryID
        query1 = """
        SELECT COUNT(*) as match_count
        FROM InventoryItem i
        INNER JOIN SalesOrderDetail s ON i.InventoryCD = s.InventoryID
        """
        cursor.execute(query1)
        match_count1 = cursor.fetchone()[0]
        print(f"Join InventoryCD = InventoryID: {match_count1} matches")
        
        # Test 2: Check for exact string matches
        query2 = """
        SELECT i.InventoryCD, s.InventoryID, COUNT(*) as occurrences
        FROM InventoryItem i
        INNER JOIN SalesOrderDetail s ON i.InventoryCD = s.InventoryID
        GROUP BY i.InventoryCD, s.InventoryID
        LIMIT 10
        """
        cursor.execute(query2)
        matches = cursor.fetchall()
        print(f"\nSample matches (first 10):")
        for inv_cd, inv_id, count in matches:
            print(f"  InventoryCD: {inv_cd} = InventoryID: {inv_id} ({count} times)")
        
        # Test 3: Check data types and lengths
        query3 = """
        SELECT 
            'InventoryItem.InventoryCD' as column_name,
            COUNT(*) as total_rows,
            COUNT(DISTINCT InventoryCD) as unique_values,
            MIN(LENGTH(InventoryCD)) as min_length,
            MAX(LENGTH(InventoryCD)) as max_length
        FROM InventoryItem
        UNION ALL
        SELECT 
            'SalesOrderDetail.InventoryID' as column_name,
            COUNT(*) as total_rows,
            COUNT(DISTINCT InventoryID) as unique_values,
            MIN(LENGTH(InventoryID)) as min_length,
            MAX(LENGTH(InventoryID)) as max_length
        FROM SalesOrderDetail
        """
        cursor.execute(query3)
        stats = cursor.fetchall()
        print(f"\nColumn statistics:")
        for col_name, total, unique, min_len, max_len in stats:
            print(f"  {col_name}: {total} rows, {unique} unique, length {min_len}-{max_len}")
        
        conn.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_acumatica_tables()
    check_inventory_item_data()
    check_sales_order_detail_data()
    test_join_conditions() 