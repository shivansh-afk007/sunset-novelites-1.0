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

def test_rtrim_join():
    """Test the RTRIM join condition"""
    try:
        conn = mysql.connector.connect(**RDS_CONFIG)
        cursor = conn.cursor()
        
        print("🔍 TESTING RTRIM JOIN CONDITION")
        print("=" * 50)
        
        # Test the RTRIM join query
        query = """
        SELECT 
            i.Descr as Description,
            i.InventoryCD as `System ID`,
            COALESCE(SUM(sod.OrderQty), 0) as Sold,
            COALESCE(SUM(sod.UnitPrice * sod.OrderQty), 0) as Subtotal,
            COALESCE(SUM(sod.ExtendedPrice), 0) as Total
        FROM InventoryItem i
        INNER JOIN SalesOrderDetail sod ON RTRIM(i.InventoryCD) = sod.InventoryID
        WHERE i.Descr IS NOT NULL
        GROUP BY i.InventoryCD, i.Descr
        HAVING Total > 0
        ORDER BY Total DESC
        """
        
        df = pd.read_sql(query, conn)
        print(f"✅ RTRIM Join Result: {len(df)} Acumatica records")
        
        if len(df) > 0:
            print("\nTop 5 Acumatica records:")
            print(df.head().to_string())
        
        # Compare with old join
        old_query = """
        SELECT 
            i.Descr as Description,
            i.InventoryCD as `System ID`,
            COALESCE(SUM(sod.OrderQty), 0) as Sold,
            COALESCE(SUM(sod.UnitPrice * sod.OrderQty), 0) as Subtotal,
            COALESCE(SUM(sod.ExtendedPrice), 0) as Total
        FROM InventoryItem i
        INNER JOIN SalesOrderDetail sod ON i.InventoryCD = sod.InventoryID
        WHERE i.Descr IS NOT NULL
        GROUP BY i.InventoryCD, i.Descr
        HAVING Total > 0
        ORDER BY Total DESC
        """
        
        old_df = pd.read_sql(old_query, conn)
        print(f"\n📊 COMPARISON:")
        print(f"Old join (without RTRIM): {len(old_df)} records")
        print(f"New join (with RTRIM): {len(df)} records")
        print(f"Improvement: +{len(df) - len(old_df)} records")
        
        conn.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_rtrim_join() 