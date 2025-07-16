
import React, { useState } from 'react';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { OverviewTab } from '@/components/dashboard/OverviewTab';
import { ProductAnalysisTab } from '@/components/dashboard/ProductAnalysisTab';
import { CategoryAnalysisTab } from '@/components/dashboard/CategoryAnalysisTab';
import { ChartsAnalyticsTab } from '@/components/dashboard/ChartsAnalyticsTab';
import { InsightsTab } from '@/components/dashboard/InsightsTab';

const Index = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewTab />;
      case 'product-analysis':
        return <ProductAnalysisTab />;
      case 'category-analysis':
        return <CategoryAnalysisTab />;
      case 'charts-analytics':
        return <ChartsAnalyticsTab />;
      case 'insights':
        return <InsightsTab />;
      default:
        return <OverviewTab />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      <DashboardHeader activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="animate-fade-in-up">
        {renderActiveTab()}
      </div>
    </div>
  );
};

export default Index;
