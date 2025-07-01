import mysql.connector

def check_table_structure():
    # Check synchub_data database
    print("=== SYNCHUB_DATA DATABASE ===")
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='synchub_data'
        )
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tables in synchub_data:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check Item table structure
        print(f"\nStructure of item table:")
        cursor.execute("DESCRIBE item")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        # Check orderline table structure
        print(f"\nStructure of orderline table:")
        cursor.execute("DESCRIBE orderline")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        # Check itemshop table structure
        print(f"\nStructure of itemshop table:")
        cursor.execute("DESCRIBE itemshop")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        conn.close()
    except Exception as e:
        print(f"Error with synchub_data: {e}")
    
    print("\n=== ACUMATICA_DATA DATABASE ===")
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='acumatica_data'
        )
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tables in acumatica_data:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check salesorderdetail table structure
        print(f"\nStructure of salesorderdetail table:")
        cursor.execute("DESCRIBE salesorderdetail")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        conn.close()
    except Exception as e:
        print(f"Error with acumatica_data: {e}")

if __name__ == "__main__":
    check_table_structure() 