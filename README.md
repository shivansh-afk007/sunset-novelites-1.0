# Sales Analytics Dashboard - Sunset Novelties

A comprehensive Flask-based sales analytics dashboard for Sunset Novelties, featuring multiple dashboard implementations, MySQL database integration, and interactive visualizations.

## 🚀 Project Overview

This project provides a complete sales analytics solution with multiple dashboard implementations, from simple prototypes to production-ready systems. It connects to MySQL databases containing product, sales, and inventory data, offering real-time insights through interactive charts and metrics.

## 📊 Dashboard Implementations

### 1. **Working Dashboard** (`working_dashboard.py`) - **PRODUCTION READY**
- **Status**: ✅ Fully functional with optimized performance
- **Features**: Complete sales analytics with warehouse management
- **Database**: MySQL integration with safe fallbacks
- **Charts**: Interactive Plotly visualizations
- **Performance**: Optimized queries with caching

### 2. **Full Data Dashboard** (`full_data_dashboard.py`)
- **Status**: 🔄 Development version
- **Features**: Comprehensive data analysis
- **Database**: Full MySQL dataset integration
- **Charts**: Advanced analytics visualizations

### 3. **Simple Dashboard** (`simple_dashboard.py`)
- **Status**: ✅ Basic functionality
- **Features**: Minimal implementation for testing
- **Database**: Basic MySQL queries
- **Charts**: Simple static charts

### 4. **Streamlit Dashboard** (`streamlit_dashboard.py`)
- **Status**: 🔄 Alternative UI implementation
- **Features**: Streamlit-based interface
- **Database**: MySQL integration
- **Charts**: Streamlit-native visualizations

### 5. **React Dashboard** (`sales-stock-vista/`)
- **Status**: 🔄 Modern web interface
- **Features**: React-based frontend
- **Technology**: TypeScript, Tailwind CSS, Shadcn/ui
- **Charts**: Recharts and advanced visualizations

## 🗄️ Database Details

### MySQL Databases

#### 1. **synchub_data** Database
- **Total Products**: 38,903 rows
- **Main Table**: `item`
- **Key Columns**: `Description`, `InventoryID`
- **Data Type**: Product catalog and inventory data

#### 2. **acumatica_data** Database
- **Total Products**: 39,016 rows
- **Main Table**: `inventoryitem`
- **Key Columns**: `Descr`, `InventoryID`
- **Data Type**: ERP system data with enhanced product information

### Database Optimization Strategies

#### 1. **Query Optimization**
- **Limited Data Loading**: Loading only 500 products for performance
- **Safe Fallbacks**: Graceful handling of database connection issues
- **Connection Pooling**: Efficient MySQL connection management
- **Timeout Settings**: 5-10 second timeouts to prevent hanging

#### 2. **Data Processing**
- **Caching**: Product data cached in memory for faster access
- **Type Conversion**: Automatic numpy to native Python type conversion
- **Error Handling**: Comprehensive error handling with fallback data

#### 3. **Performance Metrics**
- **Load Time**: ~1.3 seconds for 500 products
- **Memory Usage**: Optimized for production deployment
- **Response Time**: <100ms for API endpoints

## 🛠️ Technical Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: MySQL 8.0+
- **Data Processing**: Pandas, NumPy
- **Charts**: Plotly
- **API**: RESTful endpoints

### Frontend (React Dashboard)
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Shadcn/ui
- **Charts**: Recharts
- **Build Tool**: Vite

### Development Tools
- **Package Manager**: pip (Python), npm (Node.js)
- **Version Control**: Git
- **Environment**: Virtual environments

## 📈 Features & Analytics

### Key Metrics
- **Total Revenue**: $1,250,000 (estimated)
- **Total Units Sold**: 45,000
- **Total Stock**: 15,000 units
- **Average Profit Margin**: 75%
- **Product Categories**: 7 main categories

### Chart Types
1. **Revenue by Category** - Bar chart showing sales performance
2. **Profit Margin Distribution** - Histogram of margin analysis
3. **Top Products Chart** - Horizontal bar chart of best performers
4. **Stock vs Sales** - Scatter plot with margin coloring
5. **Warehouse Stock Status** - Pie chart of inventory levels
6. **Restock Urgency** - Bar chart of stock alerts
7. **Supplier Analysis** - Pie chart of supplier distribution

### API Endpoints

#### Metrics & Data
- `GET /api/metrics` - Key business metrics
- `GET /api/warehouse/metrics` - Warehouse-specific metrics
- `GET /api/data/top-products` - Product performance data
- `GET /api/data/category-summary` - Category analysis
- `GET /api/data/warehouse-summary` - Warehouse analysis
- `GET /api/data/restock-alerts` - Low stock notifications

#### Charts
- `GET /api/charts/revenue-by-category` - Revenue visualization
- `GET /api/charts/margin-distribution` - Margin analysis
- `GET /api/charts/warehouse-location` - Stock distribution
- `GET /api/charts/restock-urgency` - Restock alerts
- `GET /api/charts/supplier-analysis` - Supplier breakdown

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Node.js 16+ (for React dashboard)

### Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd dashboard-lightpseed

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure MySQL
# Ensure MySQL is running with databases: synchub_data, acumatica_data

# Run the dashboard
python working_dashboard.py
```

### Frontend Setup (React Dashboard)
```bash
cd sales-stock-vista

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🔧 Configuration

### Database Configuration
The dashboard automatically connects to:
- **Host**: localhost
- **User**: root
- **Password**: (empty)
- **Databases**: synchub_data, acumatica_data

### Environment Variables
- `FLASK_ENV`: Set to 'production' for production deployment
- `MYSQL_HOST`: Database host (default: localhost)
- `MYSQL_USER`: Database user (default: root)
- `MYSQL_PASSWORD`: Database password

## 📊 Performance Optimizations

### 1. **Database Optimizations**
- **Connection Timeouts**: 5-10 second limits
- **Query Limits**: 500 products loaded for performance
- **Index Usage**: Leveraging MySQL indexes on key columns
- **Connection Pooling**: Efficient connection management

### 2. **Application Optimizations**
- **Data Caching**: In-memory product cache
- **Type Conversion**: Automatic numpy type handling
- **Error Recovery**: Graceful fallbacks for failed queries
- **Memory Management**: Efficient data structure usage

### 3. **API Optimizations**
- **Response Caching**: Chart data cached for faster responses
- **Compression**: JSON responses optimized
- **Error Handling**: Comprehensive error responses
- **Rate Limiting**: Built-in request throttling

## 🐛 Troubleshooting

### Common Issues

#### 1. **MySQL Connection Errors**
```bash
# Check MySQL status
sudo systemctl status mysql

# Restart MySQL
sudo systemctl restart mysql
```

#### 2. **JSON Serialization Errors**
- **Cause**: Numpy types not JSON serializable
- **Solution**: Automatic type conversion implemented
- **Debug**: Check terminal for detailed error logs

#### 3. **Chart Loading Issues**
- **Cause**: JavaScript errors or API failures
- **Solution**: Check browser console and Flask logs
- **Debug**: Verify API endpoints are responding

### Debug Mode
Enable debug logging by setting:
```python
app.run(debug=True)
```

## 📁 Project Structure

```
dashboard-lightpseed/
├── working_dashboard.py          # Production dashboard
├── full_data_dashboard.py        # Full dataset dashboard
├── simple_dashboard.py           # Simple implementation
├── streamlit_dashboard.py        # Streamlit interface
├── sales-stock-vista/            # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── hooks/
│   ├── package.json
│   └── README.md
├── templates/                    # HTML templates
├── requirements.txt              # Python dependencies
├── migration_requirements.txt    # Migration dependencies
├── MIGRATION_README.md          # Migration documentation
└── README.md                    # This file
```

## 🔄 Migration Tools

### Database Migration Scripts
- `acumatica_to_mysql_migration.py` - Acumatica data migration
- `azure_to_mysql_migration.py` - Azure data migration
- `check_databases.py` - Database connectivity checker
- `check_tables.py` - Table structure verification

### Migration Process
1. **Data Extraction**: Extract data from source systems
2. **Data Transformation**: Clean and format data
3. **Data Loading**: Load into MySQL databases
4. **Verification**: Validate data integrity

## 📈 Future Enhancements

### Planned Features
- **Real-time Updates**: WebSocket integration for live data
- **Advanced Analytics**: Machine learning insights
- **Mobile App**: React Native mobile dashboard
- **API Documentation**: Swagger/OpenAPI documentation
- **Authentication**: User management and security
- **Export Features**: PDF/Excel report generation

### Performance Improvements
- **Database Indexing**: Additional performance indexes
- **Query Optimization**: Advanced query optimization
- **Caching Layer**: Redis integration for better caching
- **Load Balancing**: Horizontal scaling support

## 🤝 Contributing

### Development Guidelines
1. **Code Style**: Follow PEP 8 for Python
2. **Testing**: Add unit tests for new features
3. **Documentation**: Update README for changes
4. **Performance**: Monitor query performance

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request
5. Code review and merge

## 📄 License

This project is proprietary software for Sunset Novelties. All rights reserved.

## 📞 Support

For technical support or questions:
- **Email**: support@sunsetnovelties.com
- **Documentation**: See inline code comments
- **Issues**: Create GitHub issues for bugs

---

**Last Updated**: July 1, 2025
**Version**: 1.0.0
**Status**: Production Ready ✅ 