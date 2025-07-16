
import React from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, Star } from 'lucide-react';

export const InsightsTab = () => {
  const insights = [
    {
      type: 'success',
      icon: <TrendingUp className="w-6 h-6" />,
      title: 'Revenue Growth',
      description: 'Total revenue increased by 15% compared to last period, driven primarily by strong performance in the "Other" category.',
      recommendation: 'Continue focusing on high-performing products in the "Other" category while exploring expansion opportunities.',
    },
    {
      type: 'warning',
      icon: <AlertTriangle className="w-6 h-6" />,
      title: 'Negative Margin Products',
      description: '22 products are showing negative margins, requiring immediate attention to avoid losses.',
      recommendation: 'Review pricing strategy for these products or consider discontinuing low-performing items.',
    },
    {
      type: 'info',
      icon: <Star className="w-6 h-6" />,
      title: 'High Margin Opportunities',
      description: '589 products have margins above 50%, representing excellent profit opportunities.',
      recommendation: 'Increase marketing focus on these high-margin products to maximize profitability.',
    },
    {
      type: 'warning',
      icon: <TrendingDown className="w-6 h-6" />,
      title: 'Stock Management',
      description: 'Only 10 items remaining in total inventory across all categories.',
      recommendation: 'Implement urgent restocking for popular items to avoid stockouts and lost sales.',
    },
  ];

  const getInsightStyle = (type: string) => {
    switch (type) {
      case 'success':
        return 'border-green-200 bg-green-50 text-green-800';
      case 'warning':
        return 'border-yellow-200 bg-yellow-50 text-yellow-800';
      case 'info':
        return 'border-blue-200 bg-blue-50 text-blue-800';
      default:
        return 'border-gray-200 bg-gray-50 text-gray-800';
    }
  };

  const getIconStyle = (type: string) => {
    switch (type) {
      case 'success':
        return 'text-green-600';
      case 'warning':
        return 'text-yellow-600';
      case 'info':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center">
          <span className="mr-2">💡</span>
          Chart Insights
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">📊 Revenue Distribution</h3>
            <p className="text-sm text-blue-700">Shows which categories contribute most to your revenue and helps identify growth opportunities.</p>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-semibold text-green-900 mb-2">📈 Margin Analysis</h3>
            <p className="text-sm text-green-700">Identifies high and low margin products to optimize pricing and profitability strategies.</p>
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="font-semibold text-yellow-900 mb-2">📦 Stock Management</h3>
            <p className="text-sm text-yellow-700">Helps identify products that need restocking or have excess inventory.</p>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {insights.map((insight, index) => (
          <div
            key={index}
            className={`rounded-lg border p-6 ${getInsightStyle(insight.type)} animate-fade-in`}
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className="flex items-start space-x-4">
              <div className={`${getIconStyle(insight.type)} mt-1`}>
                {insight.icon}
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold mb-2">{insight.title}</h3>
                <p className="mb-3">{insight.description}</p>
                <div className="bg-white bg-opacity-50 rounded-md p-3">
                  <p className="text-sm font-medium">💡 Recommendation:</p>
                  <p className="text-sm">{insight.recommendation}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
