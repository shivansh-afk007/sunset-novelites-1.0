
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const CategoryPerformanceChart = () => {
  const data = [
    { category: 'Accessories', revenue: 1.09, units: 85 },
    { category: 'Adult Toys', revenue: 8.14, units: 277 },
    { category: 'Clothing & Accessories', revenue: 9.56, units: 286 },
    { category: 'Lubricants', revenue: 2.87, units: 261 },
    { category: 'Other', revenue: 99.84, units: 3803 },
    { category: 'Supplements', revenue: 12.07, units: 1119 },
    { category: 'Vibrators', revenue: 25.98, units: 386 },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <span className="mr-2">📈</span>
        Category Performance Comparison
      </h3>
      <div className="h-96">
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
            <YAxis yAxisId="revenue" orientation="left" />
            <YAxis yAxisId="units" orientation="right" />
            <Tooltip />
            <Bar yAxisId="revenue" dataKey="revenue" fill="#3B82F6" name="Revenue ($K)" />
            <Bar yAxisId="units" dataKey="units" fill="#EF4444" name="Units Sold" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
