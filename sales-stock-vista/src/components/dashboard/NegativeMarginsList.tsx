
import React from 'react';
import { AlertTriangle } from 'lucide-react';

export const NegativeMarginsList = () => {
  const negativeProducts = [
    { name: 'ROYAL FLUSH...', margin: '-32.0%' },
    { name: 'PLEASURE SLEEVE TRIO...', margin: '-108.7%' },
    { name: 'TIDAL WAVE...', margin: '-59.9%' },
    { name: 'FIRST RABBIT...', margin: '-9.1%' },
    { name: 'PERSONAL SILICONE LUBE', margin: '-2.1%' },
    { name: 'SUNSET PURE AND CLEAN', margin: '-73.3%' },
    { name: 'CUMULUS...', margin: '-63.3%' },
    { name: 'TURN...', margin: '-7.4%' },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
        Products with Negative Margins
      </h3>
      <div className="space-y-3 max-h-80 overflow-y-auto">
        {negativeProducts.map((product, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors"
          >
            <span className="text-sm font-medium text-gray-900 truncate flex-1">
              {product.name}
            </span>
            <span className="text-sm font-bold text-red-600 ml-2">
              {product.margin}
            </span>
          </div>
        ))}
      </div>
      <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-xs text-yellow-800">
          💡 <strong>Recommendation:</strong> Review pricing strategies for these products or consider discontinuation to improve overall profitability.
        </p>
      </div>
    </div>
  );
};
