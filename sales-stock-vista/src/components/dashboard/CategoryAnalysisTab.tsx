
import React from 'react';
import { CategorySummaryTable } from './CategorySummaryTable';
import { CategoryChart } from './CategoryChart';

export const CategoryAnalysisTab = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center">
          <span className="mr-2">📊</span>
          Category Summary
        </h2>
        <CategorySummaryTable />
      </div>
      
      <div>
        <CategoryChart />
      </div>
    </div>
  );
};
