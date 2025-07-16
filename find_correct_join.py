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

def find_correct_join():
    """Find the correct join condition between InventoryItem and SalesOrderDetail"""
    try:
        conn = mysql.connector.connect(**RDS_CONFIG)
        cursor = conn.cursor()
        
        print("🔍 FINDING CORRECT JOIN CONDITION")
        print("=" * 50)
        
        # Check different possible join conditions
        join_tests = [
            ("InventoryCD = InventoryID", "i.InventoryCD = sod.InventoryID"),
            ("InventoryID = InventoryID", "i.InventoryID = sod.InventoryID"),
            ("RemoteID = InventoryID", "i.RemoteID = sod.InventoryID"),
            ("InventoryCD = InventoryID (TRIM)", "TRIM(i.InventoryCD) = sod.InventoryID"),
            ("InventoryCD = InventoryID (RTRIM)", "RTRIM(i.InventoryCD) = sod.InventoryID"),
        ]
        
        for test_name, join_condition in join_tests:
            print(f"\n🧪 Testing: {test_name}")
            print("-" * 30)
            
            query = f"""
            SELECT COUNT(*) as match_count
            FROM InventoryItem i
            INNER JOIN SalesOrderDetail sod ON {join_condition}
            """
            
            try:
                cursor.execute(query)
                match_count = cursor.fetchone()[0]
                print(f"Matches: {match_count}")
                
                if match_count > 0:
                    # Get sample matches
                    sample_query = f"""
                    SELECT i.InventoryCD, i.Descr, sod.InventoryID, sod.LineDescription, COUNT(*) as occurrences
                    FROM InventoryItem i
                    INNER JOIN SalesOrderDetail sod ON {join_condition}
                    GROUP BY i.InventoryCD, i.Descr, sod.InventoryID, sod.LineDescription
                    LIMIT 5
                    """
                    cursor.execute(sample_query)
                    matches = cursor.fetchall()
                    print("Sample matches:")
                    for inv_cd, descr, inv_id, line_desc, count in matches:
                        print(f"  InventoryCD: '{inv_cd}' -> InventoryID: '{inv_id}' ({count} times)")
                        print(f"    Descr: {descr}")
                        print(f"    LineDesc: {line_desc}")
                        print()
                        
            except Exception as e:
                print(f"Error: {e}")
        
        # Check for any other potential join columns
        print("\n🔍 CHECKING FOR OTHER JOIN POSSIBILITIES")
        print("=" * 50)
        
        # Check if there are any common patterns
        cursor.execute("""
        SELECT i.InventoryCD, sod.InventoryID, COUNT(*) as occurrences
        FROM InventoryItem i
        CROSS JOIN SalesOrderDetail sod
        WHERE i.InventoryCD = sod.InventoryID
        GROUP BY i.InventoryCD, sod.InventoryID
        LIMIT 10
        """)
        
        exact_matches = cursor.fetchall()
        print(f"Exact string matches: {len(exact_matches)}")
        
        # Check for partial matches
        cursor.execute("""
        SELECT i.InventoryCD, sod.InventoryID, COUNT(*) as occurrences
        FROM InventoryItem i
        CROSS JOIN SalesOrderDetail sod
        WHERE i.InventoryCD LIKE CONCAT('%', sod.InventoryID, '%')
           OR sod.InventoryID LIKE CONCAT('%', i.InventoryCD, '%')
        GROUP BY i.InventoryCD, sod.InventoryID
        LIMIT 10
        """)
        
        partial_matches = cursor.fetchall()
        print(f"Partial matches: {len(partial_matches)}")
        
        # Check if there's a mapping table or other relationship
        cursor.execute("SHOW TABLES LIKE '%mapping%'")
        mapping_tables = cursor.fetchall()
        if mapping_tables:
            print(f"Found mapping tables: {mapping_tables}")
        
        conn.close()
        
    except Error as e:
        print(f"Error: {e}")

def check_inventory_codes():
    """Check the format of inventory codes in both tables"""
    try:
        conn = mysql.connector.connect(**RDS_CONFIG)
        cursor = conn.cursor()
        
        print("\n🔍 INVENTORY CODE ANALYSIS")
        print("=" * 50)
        
        # Check InventoryItem.InventoryCD format
        cursor.execute("""
        SELECT InventoryCD, LENGTH(InventoryCD) as length, COUNT(*) as count
        FROM InventoryItem
        GROUP BY InventoryCD, LENGTH(InventoryCD)
        ORDER BY count DESC
        LIMIT 10
        """)
        
        inv_codes = cursor.fetchall()
        print("Top 10 InventoryItem.InventoryCD values:")
        for code, length, count in inv_codes:
            print(f"  '{code}' (length: {length}, count: {count})")
        
        # Check SalesOrderDetail.InventoryID format
        cursor.execute("""
        SELECT InventoryID, LENGTH(InventoryID) as length, COUNT(*) as count
        FROM SalesOrderDetail
        GROUP BY InventoryID, LENGTH(InventoryID)
        ORDER BY count DESC
        LIMIT 10
        """)
        
        sod_codes = cursor.fetchall()
        print("\nTop 10 SalesOrderDetail.InventoryID values:")
        for code, length, count in sod_codes:
            print(f"  '{code}' (length: {length}, count: {count})")
        
        conn.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_correct_join()
    check_inventory_codes() 