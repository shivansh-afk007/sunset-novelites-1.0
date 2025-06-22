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