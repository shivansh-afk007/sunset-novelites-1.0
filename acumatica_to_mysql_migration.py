# -*- coding: utf-8 -*-
import pyodbc
import mysql.connector
import pandas as pd
import sys
import os

# Azure SQL connection details (Acumatica)
azure_server = 'synchub-io.database.windows.net'
azure_database = 'warehouse_0006588'
azure_username = 'synchub_reader'
azure_password = 'ab914bb2-b28f-493d-89f7-d0bb371e1f6a'
azure_driver = '{ODBC Driver 11 for SQL Server}'  # Updated to installed driver
azure_schema = 'acumatica_crestwoodlive_12373_4'  # Acumatica schema

# MySQL connection details (XAMPP installation)
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = ''  # No password for XAMPP default installation
mysql_database = 'acumatica_data'  # New database for Acumatica data

# Data type mapping from Azure SQL to MySQL
type_mapping = {
    'int': 'INT',
    'bigint': 'BIGINT',
    'smallint': 'SMALLINT',
    'tinyint': 'TINYINT',
    'bit': 'BOOLEAN',
    'decimal': 'DECIMAL(18,4)',
    'numeric': 'DECIMAL(18,4)',
    'float': 'FLOAT',
    'real': 'FLOAT',
    'money': 'DECIMAL(19,4)',
    'smallmoney': 'DECIMAL(10,4)',
    'varchar': 'VARCHAR(255)',
    'nvarchar': 'VARCHAR(255)',
    'char': 'CHAR(1)',
    'nchar': 'CHAR(1)',
    'text': 'TEXT',
    'ntext': 'TEXT',
    'datetime': 'DATETIME',
    'datetime2': 'DATETIME',
    'smalldatetime': 'DATETIME',
    'date': 'DATE',
    'time': 'TIME',
    'uniqueidentifier': 'CHAR(36)',
    'binary': 'BLOB',
    'varbinary': 'BLOB',
    'image': 'LONGBLOB',
    'xml': 'TEXT',
    'sql_variant': 'TEXT',
    'timestamp': 'TIMESTAMP',
    'rowversion': 'BINARY(8)',
    'hierarchyid': 'TEXT',
    'geometry': 'TEXT',
    'geography': 'TEXT',
    'table': 'TEXT',
    'cursor': 'TEXT',
    'sysname': 'VARCHAR(128)',
    'datetimeoffset': 'VARCHAR(34)',
    'year': 'YEAR',
    'tinyblob': 'TINYBLOB',
    'blob': 'BLOB',
    'mediumblob': 'MEDIUMBLOB',
    'longblob': 'LONGBLOB',
    'tinytext': 'TINYTEXT',
    'mediumtext': 'MEDIUMTEXT',
    'longtext': 'LONGTEXT',
    'enum': 'ENUM',
    'set': 'SET',
    'json': 'JSON'
}

def map_data_type(sql_type, char_max_length, numeric_precision=None, numeric_scale=None):
    """
    Map Azure SQL data types to MySQL data types with precision handling
    """
    sql_type = sql_type.lower()
    
    # Handle VARCHAR/NVARCHAR with specific lengths
    if sql_type in ['varchar', 'nvarchar', 'char', 'nchar']:
        if char_max_length and char_max_length > 0:
            if char_max_length <= 255:
                return f"VARCHAR({char_max_length})"
            elif char_max_length <= 65535:
                return "TEXT"
            elif char_max_length <= 16777215:
                return "MEDIUMTEXT"
            else:
                return "LONGTEXT"
        else:
            return "TEXT"
    
    # Handle DECIMAL/NUMERIC with precision and scale
    if sql_type in ['decimal', 'numeric']:
        if numeric_precision and numeric_scale is not None:
            return f"DECIMAL({numeric_precision},{numeric_scale})"
        else:
            return "DECIMAL(18,4)"
    
    # Handle FLOAT with precision
    if sql_type == 'float' and numeric_precision:
        if numeric_precision <= 23:
            return "FLOAT"
        else:
            return "DOUBLE"
    
    # Handle INT types with precision
    if sql_type == 'int' and numeric_precision:
        if numeric_precision <= 3:
            return "TINYINT"
        elif numeric_precision <= 5:
            return "SMALLINT"
        elif numeric_precision <= 10:
            return "INT"
        else:
            return "BIGINT"
    
    return type_mapping.get(sql_type, "TEXT")

def create_mysql_database():
    """Create the MySQL database if it doesn't exist"""
    try:
        # Connect to MySQL without specifying a database
        mysql_conn = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password
        )
        mysql_cursor = mysql_conn.cursor()
        
        # Create database if it doesn't exist
        mysql_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{mysql_database}`")
        print(f"✓ MySQL database '{mysql_database}' created/verified")
        
        mysql_cursor.close()
        mysql_conn.close()
        return True
    except Exception as e:
        print(f"✗ Error creating MySQL database: {e}")
        return False

def test_connections():
    """Test both Azure SQL and MySQL connections"""
    print("Testing connections...")
    
    # Test Azure SQL connection
    try:
        azure_conn_str = (
            f'DRIVER={azure_driver};'
            f'SERVER={azure_server};'
            f'DATABASE={azure_database};'
            f'UID={azure_username};'
            f'PWD={azure_password}'
        )
        azure_conn = pyodbc.connect(azure_conn_str)
        print("✓ Azure SQL connection successful")
        azure_conn.close()
    except Exception as e:
        print(f"✗ Azure SQL connection failed: {e}")
        return False
    
    # Test MySQL connection
    try:
        mysql_conn = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database
        )
        print("✓ MySQL connection successful")
        mysql_conn.close()
    except Exception as e:
        print(f"✗ MySQL connection failed: {e}")
        return False
    
    return True

def migrate_all_tables():
    """Migrate all tables from Azure SQL to MySQL"""
    
    # Connect to Azure SQL
    azure_conn_str = (
        f'DRIVER={azure_driver};'
        f'SERVER={azure_server};'
        f'DATABASE={azure_database};'
        f'UID={azure_username};'
        f'PWD={azure_password}'
    )
    azure_conn = pyodbc.connect(azure_conn_str)
    azure_cursor = azure_conn.cursor()
    print("Connected to Azure SQL.")

    # Get all table names in the schema
    azure_cursor.execute(f"""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = '{azure_schema}' AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)
    tables = [row[0] for row in azure_cursor.fetchall()]
    print(f"Found {len(tables)} tables: {tables}")

    # Connect to MySQL
    mysql_conn = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    mysql_cursor = mysql_conn.cursor()
    print("Connected to MySQL.")

    # Track migration statistics
    migration_stats = {
        'total_tables': len(tables),
        'successful_tables': 0,
        'failed_tables': [],
        'total_rows_migrated': 0
    }

    for i, table in enumerate(tables, 1):
        try:
            print(f"\n[{i}/{len(tables)}] Transferring table: {table}")

            # Get column info from Azure SQL
            azure_cursor.execute(f"""
                SELECT 
                    COLUMN_NAME, 
                    DATA_TYPE, 
                    CHARACTER_MAXIMUM_LENGTH,
                    NUMERIC_PRECISION,
                    NUMERIC_SCALE,
                    IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = '{azure_schema}' AND TABLE_NAME = '{table}'
                ORDER BY ORDINAL_POSITION
            """)
            columns_info = azure_cursor.fetchall()

            # Build CREATE TABLE statement with mapped types
            columns_ddl = []
            for col_name, data_type, char_max_length, numeric_precision, numeric_scale, is_nullable in columns_info:
                mysql_type = map_data_type(data_type, char_max_length, numeric_precision, numeric_scale)
                nullable = "" if is_nullable == 'YES' else " NOT NULL"
                columns_ddl.append(f"`{col_name}` {mysql_type}{nullable}")
            
            create_table_sql = f"CREATE TABLE IF NOT EXISTS `{table}` ({', '.join(columns_ddl)})"
            mysql_cursor.execute(create_table_sql)
            print(f"  ✓ Table structure created")

            # Clear table before inserting (optional - comment out if you want to append)
            mysql_cursor.execute(f"DELETE FROM `{table}`")
            print(f"  ✓ Table cleared")

            # Fetch data from Azure SQL - handle reserved keywords
            try:
                df = pd.read_sql(f"SELECT * FROM [{azure_schema}].[{table}]", azure_conn)
            except:
                # Fallback to regular query if brackets don't work
                df = pd.read_sql(f"SELECT * FROM {azure_schema}.{table}", azure_conn)
            
            print(f"  ✓ {len(df)} rows fetched from Azure SQL")

            # Insert data into MySQL
            if not df.empty:
                # Handle NaN values
                df = df.fillna('')
                
                # Batch insert for better performance
                batch_size = 200
                for start_idx in range(0, len(df), batch_size):
                    end_idx = min(start_idx + batch_size, len(df))
                    batch_df = df.iloc[start_idx:end_idx]
                    
                    placeholders = ', '.join(['%s'] * len(batch_df.columns))
                    insert_sql = f"INSERT INTO `{table}` VALUES ({placeholders})"
                    
                    # Convert DataFrame to list of tuples
                    values = [tuple(row) for row in batch_df.values]
                    mysql_cursor.executemany(insert_sql, values)
                
                mysql_conn.commit()
                print(f"  ✓ {len(df)} rows inserted into MySQL")
                migration_stats['total_rows_migrated'] += len(df)
            else:
                print(f"  ✓ No data to insert (empty table)")

            migration_stats['successful_tables'] += 1

        except Exception as e:
            print(f"  ✗ Error migrating table {table}: {e}")
            migration_stats['failed_tables'].append((table, str(e)))
            mysql_conn.rollback()

    # Close connections
    mysql_cursor.close()
    mysql_conn.close()
    azure_cursor.close()
    azure_conn.close()
    
    # Print migration summary
    print(f"\n{'='*50}")
    print("MIGRATION SUMMARY")
    print(f"{'='*50}")
    print(f"Total tables: {migration_stats['total_tables']}")
    print(f"Successful migrations: {migration_stats['successful_tables']}")
    print(f"Failed migrations: {len(migration_stats['failed_tables'])}")
    print(f"Total rows migrated: {migration_stats['total_rows_migrated']}")
    
    if migration_stats['failed_tables']:
        print(f"\nFailed tables:")
        for table, error in migration_stats['failed_tables']:
            print(f"  - {table}: {error}")
    
    print(f"\nMigration completed!")

def main():
    """Main function"""
    print("Acumatica Azure SQL to MySQL Migration Tool")
    print("="*50)
    
    # Create MySQL database first
    if not create_mysql_database():
        print("Failed to create MySQL database. Exiting.")
        return
    
    # Test connections first
    if not test_connections():
        print("Connection test failed. Please check your credentials and try again.")
        return
    
    # Confirm before proceeding
    print(f"\nThis will migrate ALL tables from Azure SQL schema '{azure_schema}' to MySQL database '{mysql_database}'.")
    response = input("Do you want to proceed? (y/N): ")
    
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    # Start migration
    try:
        migrate_all_tables()
    except KeyboardInterrupt:
        print("\nMigration interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main() 