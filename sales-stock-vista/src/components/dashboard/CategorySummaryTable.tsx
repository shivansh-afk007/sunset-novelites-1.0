
import React from 'react';

interface CategoryData {
  category: string;
  totalRevenue: string;
  productCount: number;
  avgMargin: string;
  unitsSold: number;
  stockRemaining: number;
  totalCost: string;
  totalProfit: string;
}

export const CategorySummaryTable = () => {
  const categories: CategoryData[] = [
    {
      category: 'Accessories',
      totalRevenue: '$1,094.55',
      productCount: 16,
      avgMargin: '63.7%',
      unitsSold: 85,
      stockRemaining: 0,
      totalCost: '$314.9',
      totalProfit: '$712.95',
    },
    {
      category: 'Adult Toys',
      totalRevenue: '$8,140.91',
      productCount: 106,
      avgMargin: '53.2%',
      unitsSold: 277,
      stockRemaining: 1,
      totalCost: '$3,452.65',
      totalProfit: '$4,219.17',
    },
    {
      category: 'Clothing & Accessories',
      totalRevenue: '$9,559.99',
      productCount: 87,
      avgMargin: '58.3%',
      unitsSold: 286,
      stockRemaining: 0,
      totalCost: '$4,421.43',
      totalProfit: '$4,732.93',
    },
    {
      category: 'Lubricants',
      totalRevenue: '$2,872.97',
      productCount: 35,
      avgMargin: '69.2%',
      unitsSold: 261,
      stockRemaining: 0,
      totalCost: '$1,506.73',
      totalProfit: '$1,198.48',
    },
    {
      category: 'Other',
      totalRevenue: '$99,838.73',
      productCount: 462,
      avgMargin: '57.6%',
      unitsSold: 3803,
      stockRemaining: 6,
      totalCost: '$65,819.03',
      totalProfit: '$28,415.97',
    },
    {
      category: 'Supplements',
      totalRevenue: '$12,068.73',
      productCount: 30,
      avgMargin: '64.7%',
      unitsSold: 1119,
      stockRemaining: 0,
      totalCost: '$4,768.68',
      totalProfit: '$6,639.18',
    },
    {
      category: 'Vibrators',
      totalRevenue: '$25,980.87',
      productCount: 49,
      avgMargin: '59.1%',
      unitsSold: 386,
      stockRemaining: 3,
      totalCost: '$16,645.27',
      totalProfit: '$7,903.78',
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left py-4 px-4 font-medium text-gray-600">Category</th>
              <th className="text-right py-4 px-4 font-medium text-gray-600">Total Revenue</th>
              <th className="text-right py-4 px-4 font-medium text-gray-600">Product Count</th>
              <th className="text-right py-4 px-4 font-medium text-gray-600">Avg Margin</th>
              <th className="text-right py-4 px-4 font-medium text-gray-600">Units Sold</th>
              <th className="text-right py-4 px-4 font-medium text-gray-600">Stock Remaining</th>
              <th className="text-right py-4 px-4 font-medium text-gray-600">Total Cost</th>
              <th className="text-right py-4 px-4 font-medium text-gray-600">Total Profit</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((category, index) => (
              <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="py-4 px-4 font-medium text-gray-900">{category.category}</td>
                <td className="py-4 px-4 text-right font-medium text-gray-900">{category.totalRevenue}</td>
                <td className="py-4 px-4 text-right text-gray-900">{category.productCount}</td>
                <td className="py-4 px-4 text-right font-medium text-green-600">{category.avgMargin}</td>
                <td className="py-4 px-4 text-right text-gray-900">{category.unitsSold}</td>
                <td className="py-4 px-4 text-right text-gray-900">{category.stockRemaining}</td>
                <td className="py-4 px-4 text-right text-gray-900">{category.totalCost}</td>
                <td className="py-4 px-4 text-right font-medium text-green-600">{category.totalProfit}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
