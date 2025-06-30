# Azure SQL to MySQL Migration Tool

This tool migrates all tables from an Azure SQL database to a local MySQL database with precise data type mapping.

## Prerequisites

### 1. Install Required Software

#### Windows:
- **ODBC Driver 17 for SQL Server**: Download from Microsoft
- **MySQL Server**: Install MySQL Community Server
- **Python 3.8+**: Install Python from python.org

#### macOS:
```bash
# Install ODBC Driver
brew install microsoft/mssql-release/mssql-tools

# Install MySQL
brew install mysql

# Install Python dependencies
pip install -r migration_requirements.txt
```

#### Linux (Ubuntu/Debian):
```bash
# Install ODBC Driver
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Install MySQL
sudo apt-get install mysql-server

# Install Python dependencies
pip install -r migration_requirements.txt
```

### 2. Install Python Dependencies

```bash
pip install -r migration_requirements.txt
```

## Configuration

### 1. Update MySQL Credentials

Edit `azure_to_mysql_migration.py` and update these variables:

```python
# MySQL connection details (update as needed)
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'your_mysql_password'  # Update this
mysql_database = 'your_local_db'  # Update this
```

### 2. Create MySQL Database

```sql
CREATE DATABASE your_local_db;
```

## Usage

### 1. Test Connections

The script will automatically test both Azure SQL and MySQL connections before starting the migration.

### 2. Run Migration

```bash
python azure_to_mysql_migration.py
```

### 3. Follow Prompts

The script will:
1. Test connections to both databases
2. List all tables found in the Azure SQL schema
3. Ask for confirmation before proceeding
4. Migrate each table with progress updates
5. Provide a summary of the migration

## Features

### Data Type Mapping

The script includes comprehensive data type mapping from Azure SQL to MySQL:

- **Numeric Types**: INT, BIGINT, DECIMAL, FLOAT, etc.
- **String Types**: VARCHAR, TEXT, CHAR, etc.
- **Date/Time Types**: DATETIME, DATE, TIME, etc.
- **Binary Types**: BLOB, LONGBLOB, etc.
- **Special Types**: UNIQUEIDENTIFIER, XML, etc.

### Performance Optimizations

- **Batch Processing**: Inserts data in batches of 1000 rows
- **Connection Pooling**: Efficient database connections
- **Error Handling**: Continues migration even if individual tables fail
- **Progress Tracking**: Real-time progress updates

### Safety Features

- **Connection Testing**: Validates both database connections before starting
- **User Confirmation**: Requires explicit confirmation before migration
- **Error Recovery**: Rolls back failed table migrations
- **Detailed Logging**: Comprehensive error reporting

## Migration Process

1. **Discovery**: Lists all tables in the Azure SQL schema
2. **Schema Creation**: Creates MySQL tables with mapped data types
3. **Data Transfer**: Migrates all data in batches
4. **Verification**: Provides migration statistics

## Troubleshooting

### Common Issues

#### 1. ODBC Driver Not Found
```
Error: ('01000', "[01000] unixODBC cannot open and/or load the system DSN and/or user DSN (0) (SQLDriverConnect)")
```
**Solution**: Install ODBC Driver 17 for SQL Server

#### 2. MySQL Connection Failed
```
Error: 2003 (HY000): Can't connect to MySQL server
```
**Solution**: 
- Ensure MySQL server is running
- Check credentials in the script
- Verify database exists

#### 3. Azure SQL Connection Failed
```
Error: Login failed for user 'synchub_reader'
```
**Solution**: 
- Verify Azure SQL credentials
- Check firewall settings
- Ensure user has proper permissions

### Performance Tips

1. **Increase Batch Size**: For large tables, increase `batch_size` in the script
2. **Network Optimization**: Run the script close to the Azure SQL server
3. **MySQL Configuration**: Optimize MySQL settings for bulk inserts

## Data Type Mapping Details

| Azure SQL Type | MySQL Type | Notes |
|----------------|------------|-------|
| int | INT | 32-bit integer |
| bigint | BIGINT | 64-bit integer |
| varchar(n) | VARCHAR(n) | Variable-length string |
| nvarchar(n) | VARCHAR(n) | Unicode string |
| text | TEXT | Long text |
| datetime | DATETIME | Date and time |
| decimal(p,s) | DECIMAL(p,s) | Exact numeric |
| float | FLOAT/DOUBLE | Approximate numeric |
| uniqueidentifier | CHAR(36) | UUID |
| binary | BLOB | Binary data |

## Security Considerations

1. **Credentials**: Never commit database credentials to version control
2. **Network**: Use secure connections when possible
3. **Permissions**: Use read-only accounts for source database
4. **Backup**: Always backup target database before migration

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all prerequisites are installed
3. Review error messages for specific guidance
4. Ensure database permissions are correct

## License

This tool is provided as-is for educational and development purposes. 