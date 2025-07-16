
import React, { useMemo } from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';

interface Product {
  name: string;
  category: string;
  unitsSold: number;
  stockRemaining: number;
  revenue: string;
  margin: string;
  profit: string;
  cost?: string;
}

interface ProductTableProps {
  searchTerm: string;
  categoryFilter: string;
}

export const ProductTable: React.FC<ProductTableProps> = ({ searchTerm, categoryFilter }) => {
  const products: Product[] = [
    {
      name: 'HERQUAKE THRUSTING RABBIT - TE...',
      category: 'Vibrators',
      unitsSold: 199,
      stockRemaining: 0,
      revenue: '$18,010.06',
      margin: '31.9%',
      profit: '$5,433.48',
    },
    {
      name: 'FREIGHT CHARGES...',
      category: 'Other',
      unitsSold: 1485,
      stockRemaining: 0,
      revenue: '$8,993.45',
      margin: '0.0%',
      profit: '$0',
    },
    {
      name: 'STORM 2...',
      category: 'Other',
      unitsSold: 97,
      stockRemaining: 0,
      revenue: '$4,613.21',
      margin: '6.3%',
      profit: '$275.77',
    },
    {
      name: 'ROYAL FLUSH...',
      category: 'Other',
      unitsSold: 9,
      stockRemaining: 0,
      revenue: '$79.65',
      margin: '-32.0%',
      profit: '$98.99',
    },
    {
      name: 'PLEASURE SLEEVE TRIO...',
      category: 'Other',
      unitsSold: 44,
      stockRemaining: 0,
      revenue: '$599.49',
      margin: '-108.7%',
      profit: '$1,167.96',
    },
    {
      name: 'BLACK MAMBA 7K MALE SUPPLEMENT...',
      category: 'Supplements',
      unitsSold: 202,
      stockRemaining: 0,
      revenue: '$2,136.89',
      margin: '62.3%',
      profit: '$1,253.85',
    },
  ];

  const filteredProducts = useMemo(() => {
    return products.filter((product) => {
      const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           product.category.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = categoryFilter === 'all' || 
                             product.category.toLowerCase().includes(categoryFilter.toLowerCase());
      return matchesSearch && matchesCategory;
    });
  }, [searchTerm, categoryFilter]);

  const getMarginColor = (margin: string) => {
    const value = parseFloat(margin.replace('%', ''));
    if (value < 0) return 'text-red-600 bg-red-50';
    if (value > 50) return 'text-green-600 bg-green-50';
    return 'text-gray-600';
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-4 font-medium text-gray-600">Product</th>
            <th className="text-left py-3 px-4 font-medium text-gray-600">Category</th>
            <th className="text-right py-3 px-4 font-medium text-gray-600">Units Sold</th>
            <th className="text-right py-3 px-4 font-medium text-gray-600">Stock Remaining</th>
            <th className="text-right py-3 px-4 font-medium text-gray-600">Revenue</th>
            <th className="text-right py-3 px-4 font-medium text-gray-600">Margin</th>
            <th className="text-right py-3 px-4 font-medium text-gray-600">Profit</th>
          </tr>
        </thead>
        <tbody>
          {filteredProducts.map((product, index) => (
            <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
              <td className="py-3 px-4 font-medium text-gray-900">{product.name}</td>
              <td className="py-3 px-4 text-gray-600">
                <span className="inline-flex px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                  {product.category}
                </span>
              </td>
              <td className="py-3 px-4 text-right text-gray-900">{product.unitsSold}</td>
              <td className="py-3 px-4 text-right text-gray-900">{product.stockRemaining}</td>
              <td className="py-3 px-4 text-right font-medium text-gray-900">{product.revenue}</td>
              <td className={`py-3 px-4 text-right font-medium ${getMarginColor(product.margin)} rounded px-2`}>
                {product.margin}
              </td>
              <td className="py-3 px-4 text-right font-medium text-gray-900">{product.profit}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
