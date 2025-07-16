
import React from 'react';
import { RevenueDistributionChart } from './RevenueDistributionChart';
import { ProfitMarginChart } from './ProfitMarginChart';
import { CategoryPerformanceChart } from './CategoryPerformanceChart';
import { StockAnalysisChart } from './StockAnalysisChart';

export const ChartsAnalyticsTab = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <RevenueDistributionChart />
        <ProfitMarginChart />
      </div>
      
      <div className="mb-8">
        <CategoryPerformanceChart />
      </div>
      
      <div>
        <StockAnalysisChart />
      </div>
    </div>
  );
};
