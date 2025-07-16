
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const ProfitMarginChart = () => {
  const data = [
    { category: 'Lubricants', margin: 69.2 },
    { category: 'Supplements', margin: 64.7 },
    { category: 'Accessories', margin: 63.7 },
    { category: 'Vibrators', margin: 59.1 },
    { category: 'Clothing & Accessories', margin: 58.3 },
    { category: 'Other', margin: 57.6 },
    { category: 'Adult Toys', margin: 53.2 },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <span className="mr-2">📊</span>
        Average Profit Margin by Category
      </h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="category" 
              angle={-45}
              textAnchor="end"
              height={100}
              fontSize={12}
            />
            <YAxis />
            <Tooltip formatter={(value) => [`${value}%`, 'Profit Margin']} />
            <Bar dataKey="margin" fill="#4F46E5" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
