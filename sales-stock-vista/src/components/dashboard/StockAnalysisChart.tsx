
import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const StockAnalysisChart = () => {
  const data = [
    { stock: 0, sales: 3803, revenue: 99.84, category: 'Other' },
    { stock: 3, sales: 386, revenue: 25.98, category: 'Vibrators' },
    { stock: 0, sales: 1119, revenue: 12.07, category: 'Supplements' },
    { stock: 0, sales: 286, revenue: 9.56, category: 'Clothing & Accessories' },
    { stock: 1, sales: 277, revenue: 8.14, category: 'Adult Toys' },
    { stock: 0, sales: 261, revenue: 2.87, category: 'Lubricants' },
    { stock: 0, sales: 85, revenue: 1.09, category: 'Accessories' },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <span className="mr-2">📦</span>
        Stock vs Sales Analysis
      </h3>
      <p className="text-sm text-gray-600 mb-4">Size = Revenue</p>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="sales" name="Units Sold" />
            <YAxis dataKey="stock" name="Stock Remaining" />
            <Tooltip 
              cursor={{ strokeDasharray: '3 3' }}
              formatter={(value, name) => [value, name]}
              labelFormatter={(label) => `Category: ${label}`}
            />
            <Scatter 
              data={data} 
              fill="#8884d8"
              r={8}
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
