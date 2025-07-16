
import React from 'react';
import { RevenueDistributionChart } from './RevenueDistributionChart';
import { ProfitMarginChart } from './ProfitMarginChart';

export const CategoryChart = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <RevenueDistributionChart />
      <ProfitMarginChart />
    </div>
  );
};
