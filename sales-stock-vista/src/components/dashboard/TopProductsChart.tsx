
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const TopProductsChart = () => {
  const data = [
    { name: 'HERQUAKE THRUSTING RABBIT', revenue: 18.01 },
    { name: 'FREIGHT CHARGES', revenue: 8.99 },
    { name: 'GUSHER', revenue: 3.03 },
    { name: 'BEACH BUNNY MIFFY-T', revenue: 3.13 },
    { name: 'CUMULUS - PURPLE', revenue: 3.22 },
    { name: 'CUMULUS', revenue: 3.51 },
    { name: 'HEART THROB', revenue: 4.40 },
    { name: 'STORM 2', revenue: 4.61 },
    { name: 'HURRICANE', revenue: 2.24 },
    { name: 'CATEGORY 5', revenue: 2.55 },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <span className="mr-2">🏆</span>
        Top 20 Products by Revenue
      </h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="horizontal" margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" width={120} fontSize={10} />
            <Tooltip formatter={(value) => [`$${value}K`, 'Revenue']} />
            <Bar dataKey="revenue" fill="#F59E0B" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
