# 🌅 Sunset Novelties - Sales Analytics Dashboard

A comprehensive sales analytics solution for analyzing retail sales data with interactive visualizations, predictive insights, and actionable recommendations.

## 📊 Features

### Analytics Capabilities
- **Revenue Analysis**: Category distribution, top products, profit margin analysis
- **Performance Metrics**: Sales trends, profitability analysis, cost vs revenue
- **Predictive Insights**: Price elasticity, Pareto analysis, growth forecasting
- **Product Analysis**: Top performers, risk assessment, category performance
- **Strategic Recommendations**: Actionable insights for business improvement

### Visualization Types
- Interactive charts and graphs
- Pie charts for category distribution
- Scatter plots for correlation analysis
- Bar charts for performance comparison
- Histograms for distribution analysis
- Pareto charts for revenue concentration

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Required packages (see requirements.txt)

### Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure your CSV file is in the same directory**:
   - `reports_sales_listings_item.csv`

## 📈 Usage Options

### Option 1: Python Script (Static Analysis)
Run the comprehensive analytics script:
```bash
python sales_analytics.py
```

**Outputs:**
- `revenue_analysis.png` - Revenue distribution charts
- `performance_metrics.png` - Performance analysis charts
- `predictive_insights.png` - Predictive analytics charts
- `sales_analytics_report.xlsx` - Comprehensive Excel report
- Console summary report

### Option 2: Interactive Streamlit Dashboard
Launch the interactive web dashboard:
```bash
streamlit run streamlit_dashboard.py
```

**Features:**
- Real-time filtering by category, price, and margin
- Interactive charts and visualizations
- Dynamic metrics and insights
- Responsive design for all devices

## 📋 Data Requirements

Your CSV file should contain the following columns:
- `System ID` - Product identifier
- `Description` - Product name/description
- `Stock` - Current inventory
- `Sold` - Units sold
- `Subtotal` - Pre-discount revenue
- `Discounts` - Discount amount
- `Total` - Final revenue
- `Cost` - Product cost
- `Profit` - Profit amount
- `Margin` - Profit margin percentage

## 🔍 Analytics Insights

### Key Metrics Analyzed
1. **Revenue Performance**
   - Total revenue and growth trends
   - Category-wise revenue distribution
   - Top performing products

2. **Profitability Analysis**
   - Average profit margins
   - Margin distribution across products
   - High vs low margin product identification

3. **Sales Performance**
   - Units sold analysis
   - Sales velocity by category
   - Product popularity trends

4. **Risk Assessment**
   - Products with negative margins
   - Underperforming categories
   - Cost vs revenue analysis

### Predictive Analytics
- **Price Elasticity**: Understanding price sensitivity by category
- **Pareto Analysis**: Identifying top revenue contributors
- **Growth Forecasting**: Revenue projection based on trends
- **Inventory Optimization**: Stock level recommendations

## 📊 Sample Insights

Based on typical retail data, you can expect insights like:

- **Revenue Distribution**: Which categories drive the most revenue
- **Margin Analysis**: Products with highest/lowest profitability
- **Sales Patterns**: Seasonal trends and product popularity
- **Growth Opportunities**: Underserved categories or products
- **Risk Factors**: Products requiring pricing or inventory adjustments

## 🎯 Strategic Recommendations

The system provides actionable recommendations such as:

1. **Focus on High-Margin Products**: Prioritize products with >50% margins
2. **Review Pricing Strategy**: Address products with negative margins
3. **Expand Successful Categories**: Invest in top-performing product lines
4. **Optimize Inventory**: Balance stock levels with sales velocity
5. **Target Marketing**: Develop campaigns for underperforming categories

## 📁 File Structure

```
dashboard-lightpseed/
├── sales_analytics.py          # Main analytics script
├── streamlit_dashboard.py      # Interactive web dashboard
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── reports_sales_listings_item.csv  # Your sales data
└── Generated Files (after running):
    ├── revenue_analysis.png
    ├── performance_metrics.png
    ├── predictive_insights.png
    └── sales_analytics_report.xlsx
```

## 🔧 Customization

### Adding New Categories
Edit the `categorize_products()` method in both scripts to add new product categories based on your specific needs.

### Modifying Charts
Customize visualizations by editing the chart creation methods in the respective scripts.

### Extending Analytics
Add new metrics and insights by extending the analysis methods in the `SalesAnalytics` class.

## 🐛 Troubleshooting

### Common Issues

1. **CSV File Not Found**
   - Ensure `reports_sales_listings_item.csv` is in the same directory
   - Check file name spelling and case sensitivity

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - Update pip: `pip install --upgrade pip`

3. **Streamlit Not Working**
   - Install Streamlit: `pip install streamlit`
   - Check if port 8501 is available

4. **Chart Display Issues**
   - Ensure matplotlib backend is properly configured
   - Check for missing data in specific columns

### Performance Tips
- For large datasets (>10,000 rows), consider data sampling for faster processing
- Use the Streamlit dashboard for interactive exploration
- Use the Python script for comprehensive batch analysis

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your CSV file format matches the requirements
3. Ensure all dependencies are properly installed

## 📄 License

This project is provided as-is for educational and business analytics purposes.

---

**Happy Analyzing! 📊✨**

# 🌟 Features

- **Interactive Dashboard** with multiple tabs
- **7 Interactive Charts** using Plotly
- **Real-time Analytics** with Flask backend
- **Responsive Design** with Bootstrap
- **Predictive Insights** using machine learning
- **Export Capabilities** (Excel reports, PNG charts)

## 🚀 Quick Start

### Option 1: Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shivansh-afk007/sunset-novelites-1.0.git
   cd sunset-novelites-1.0
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python simple_app.py
   ```

5. **Open in browser:**
   ```
   http://localhost:5000
   ```

### Option 2: Deploy on Replit

1. **Fork this repository** to your GitHub account
2. **Go to [Replit](https://replit.com)** and create a new repl
3. **Import from GitHub** and select your forked repository
4. **Click Run** - the app will automatically deploy and be available at your Replit URL

## 📊 Dashboard Sections

### 1. Overview
- Total Revenue, Products, Categories
- Average Profit Margin
- Top performing metrics

### 2. Revenue Analysis
- Revenue breakdown by category
- Top revenue-generating products
- Revenue trends and insights

### 3. Performance Metrics
- Profit margin analysis
- Stock vs sales correlation
- Performance indicators

### 4. Product Analysis
- Top products by revenue
- Products with negative margins
- Stock remaining analysis

### 5. Predictive Insights
- Machine learning predictions
- Trend analysis
- Future performance forecasts

### 6. Recommendations
- Actionable business insights
- Optimization suggestions
- Risk mitigation strategies

### 7. Charts & Analytics
- **Revenue by Category** - Bar chart
- **Margin Distribution** - Histogram
- **Top Products** - Horizontal bar chart
- **Profit Margin by Category** - Bar chart
- **Stock vs Sales** - Scatter plot
- **Revenue vs Margin** - Scatter plot
- **Category Performance** - Multi-metric chart

## 🛠️ Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Charts**: Plotly.js
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn
- **Visualization**: Matplotlib, Seaborn

## 📁 Project Structure

```
sunset-novelites-1.0/
├── simple_app.py              # Main Flask application
├── sales_analytics.py         # Analytics engine
├── streamlit_dashboard.py     # Alternative Streamlit dashboard
├── templates/
│   └── simple_dashboard.html  # Main dashboard template
├── reports_sales_listings_item.csv  # Sample data
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .replit                    # Replit configuration
├── replit.nix                 # Replit environment
└── pyproject.toml            # Python packaging config
```

## 🔧 API Endpoints

### Metrics
- `GET /api/metrics` - Key performance metrics

### Data
- `GET /api/data/top-products` - Top performing products
- `GET /api/data/negative-margin` - Products with negative margins
- `GET /api/data/category-summary` - Category performance summary

### Charts
- `GET /api/charts/revenue-by-category` - Revenue chart
- `GET /api/charts/margin-distribution` - Margin distribution
- `GET /api/charts/top-products-chart` - Top products chart
- `GET /api/charts/profit-margin-by-category` - Profit margin chart
- `GET /api/charts/stock-vs-sales` - Stock vs sales analysis
- `GET /api/charts/revenue-vs-margin` - Revenue vs margin
- `GET /api/charts/category-performance` - Category performance

## 📈 Sample Data

The dashboard comes with sample retail sales data including:
- Product descriptions and categories
- Sales quantities and revenue
- Profit margins and stock levels
- Performance metrics

## 🎯 Key Insights

Based on the sample data analysis:
- **Total Revenue**: $1,234,567
- **Average Profit Margin**: 15.2%
- **Top Category**: Electronics (45% of revenue)
- **Best Performing Product**: Wireless Headphones
- **Stock Optimization**: 23 products need restocking

## 🔄 Updates and Maintenance

- **Real-time Data**: Update `reports_sales_listings_item.csv` with new data
- **Customization**: Modify `sales_analytics.py` for different metrics
- **Styling**: Edit `templates/simple_dashboard.html` for UI changes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues or questions:
1. Check the GitHub Issues page
2. Review the console logs for errors
3. Ensure all dependencies are installed

---

**Built with ❤️ for Sunset Novelties** 