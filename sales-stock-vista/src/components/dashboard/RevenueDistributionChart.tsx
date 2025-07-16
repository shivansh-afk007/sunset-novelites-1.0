
import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

export const RevenueDistributionChart = () => {
  const data = [
    { name: 'Other', value: 62.6, color: '#FF6B6B' },
    { name: 'Vibrators', value: 16.3, color: '#4ECDC4' },
    { name: 'Adult Toys', value: 5.1, color: '#45B7D1' },
    { name: 'Supplements', value: 7.6, color: '#96CEB4' },
    { name: 'Clothing & Accessories', value: 6.0, color: '#FFEAA7' },
    { name: 'Lubricants', value: 1.8, color: '#DDA0DD' },
    { name: 'Accessories', value: 0.7, color: '#98D8C8' },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <span className="mr-2">🍰</span>
        Revenue Distribution by Category
      </h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={120}
              paddingAngle={2}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => [`${value}%`, 'Revenue Share']} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
