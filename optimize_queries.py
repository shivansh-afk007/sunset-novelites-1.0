import mysql.connector
import pandas as pd
from sqlalchemy import create_engine, text
import time

def optimize_database_queries():
    """Optimize database queries and add indexes for better performance"""
    
    def get_connection(database):
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database=database,
            connect_timeout=10
        )
    
    print("🔧 Database Query Optimization")
    print("=" * 60)
    
    # Synchub optimizations
    print("\n📊 Optimizing synchub_data database...")
    synchub_conn = get_connection('synchub_data')
    if synchub_conn:
        cursor = synchub_conn.cursor()
        
        # Add indexes for better performance
        indexes_to_add = [
            "CREATE INDEX IF NOT EXISTS idx_item_remotepid ON item(RemoteID)",
            "CREATE INDEX IF NOT EXISTS idx_orderline_itemid ON orderline(ItemID)",
            "CREATE INDEX IF NOT EXISTS idx_orderline_quantity ON orderline(Quantity)",
            "CREATE INDEX IF NOT EXISTS idx_orderline_total ON orderline(Total)",
            "CREATE INDEX IF NOT EXISTS idx_itemshop_itemid ON itemshop(ItemID)",
            "CREATE INDEX IF NOT EXISTS idx_itemshop_qoh ON itemshop(Qoh)",
            "CREATE INDEX IF NOT EXISTS idx_sale_total ON sale(Total)",
            "CREATE INDEX IF NOT EXISTS idx_salepayment_saleid ON salepayment(SaleID)"
        ]
        
        for index_sql in indexes_to_add:
            try:
                cursor.execute(index_sql)
                print(f"✅ Added index: {index_sql.split('idx_')[1].split(' ON')[0]}")
            except Exception as e:
                print(f"⚠️  Index already exists or error: {e}")
        
        # Test query performance
        print("\n⏱️  Testing query performance...")
        
        # Test 1: Simple count
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM item WHERE Description IS NOT NULL")
        count = cursor.fetchone()[0]
        end_time = time.time()
        print(f"   Count items: {count:,} rows in {end_time - start_time:.3f}s")
        
        # Test 2: Aggregated sales
        start_time = time.time()
        cursor.execute("""
            SELECT 
                i.Description,
                SUM(ol.Quantity) as Total_Sold,
                SUM(ol.Total) as Total_Revenue
            FROM item i
            LEFT JOIN orderline ol ON i.RemoteID = ol.ItemID
            WHERE i.Description IS NOT NULL
            GROUP BY i.RemoteID, i.Description
            ORDER BY Total_Revenue DESC
            LIMIT 10
        """)
        results = cursor.fetchall()
        end_time = time.time()
        print(f"   Top 10 products query: {end_time - start_time:.3f}s")
        
        synchub_conn.close()
    
    # Acumatica optimizations
    print("\n📊 Optimizing acumatica_data database...")
    acumatica_conn = get_connection('acumatica_data')
    if acumatica_conn:
        cursor = acumatica_conn.cursor()
        
        # Add indexes for better performance
        indexes_to_add = [
            "CREATE INDEX IF NOT EXISTS idx_inventoryitem_inventoryid ON inventoryitem(InventoryID)",
            "CREATE INDEX IF NOT EXISTS idx_salesorderdetail_inventoryid ON salesorderdetail(InventoryID)",
            "CREATE INDEX IF NOT EXISTS idx_salesorderdetail_orderqty ON salesorderdetail(OrderQty)",
            "CREATE INDEX IF NOT EXISTS idx_salesorderdetail_extendedprice ON salesorderdetail(ExtendedPrice)",
            "CREATE INDEX IF NOT EXISTS idx_billdetail_billid ON billdetail(BillID)",
            "CREATE INDEX IF NOT EXISTS idx_invoicedetail_invoiceid ON invoicedetail(InvoiceID)"
        ]
        
        for index_sql in indexes_to_add:
            try:
                cursor.execute(index_sql)
                print(f"✅ Added index: {index_sql.split('idx_')[1].split(' ON')[0]}")
            except Exception as e:
                print(f"⚠️  Index already exists or error: {e}")
        
        # Test query performance
        print("\n⏱️  Testing query performance...")
        
        # Test 1: Simple count
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM inventoryitem WHERE Descr IS NOT NULL")
        count = cursor.fetchone()[0]
        end_time = time.time()
        print(f"   Count inventory items: {count:,} rows in {end_time - start_time:.3f}s")
        
        # Test 2: Aggregated sales
        start_time = time.time()
        cursor.execute("""
            SELECT 
                i.Descr as Description,
                SUM(sod.OrderQty) as Total_Sold,
                SUM(sod.ExtendedPrice) as Total_Revenue
            FROM inventoryitem i
            LEFT JOIN salesorderdetail sod ON i.InventoryID = sod.InventoryID
            WHERE i.Descr IS NOT NULL
            GROUP BY i.InventoryID, i.Descr
            ORDER BY Total_Revenue DESC
            LIMIT 10
        """)
        results = cursor.fetchall()
        end_time = time.time()
        print(f"   Top 10 products query: {end_time - start_time:.3f}s")
        
        acumatica_conn.close()
    
    print("\n✅ Database optimization complete!")

def create_materialized_views():
    """Create materialized views for frequently accessed data"""
    print("\n📋 Creating Materialized Views for Performance")
    print("=" * 60)
    
    synchub_conn = get_connection('synchub_data')
    if synchub_conn:
        cursor = synchub_conn.cursor()
        
        # Create summary tables for faster access
        views_to_create = [
            """
            CREATE TABLE IF NOT EXISTS product_summary AS
            SELECT 
                i.RemoteID,
                i.Description,
                COALESCE(SUM(ol.Quantity), 0) as Total_Sold,
                COALESCE(SUM(ol.Total), 0) as Total_Revenue,
                COALESCE(MAX(is1.Qoh), 0) as Current_Stock,
                COUNT(DISTINCT ol.SaleID) as Sale_Count
            FROM item i
            LEFT JOIN orderline ol ON i.RemoteID = ol.ItemID
            LEFT JOIN itemshop is1 ON i.RemoteID = is1.ItemID
            WHERE i.Description IS NOT NULL
            GROUP BY i.RemoteID, i.Description
            """,
            """
            CREATE TABLE IF NOT EXISTS daily_sales_summary AS
            SELECT 
                DATE(s.SaleTime) as Sale_Date,
                COUNT(DISTINCT s.SaleID) as Daily_Sales,
                SUM(s.Total) as Daily_Revenue,
                COUNT(DISTINCT ol.ItemID) as Products_Sold
            FROM sale s
            LEFT JOIN orderline ol ON s.SaleID = ol.SaleID
            WHERE s.SaleTime IS NOT NULL
            GROUP BY DATE(s.SaleTime)
            ORDER BY Sale_Date DESC
            LIMIT 365
            """
        ]
        
        for view_sql in views_to_create:
            try:
                cursor.execute(view_sql)
                print(f"✅ Created summary table")
            except Exception as e:
                print(f"⚠️  Error creating summary table: {e}")
        
        synchub_conn.close()

if __name__ == "__main__":
    optimize_database_queries()
    create_materialized_views() 