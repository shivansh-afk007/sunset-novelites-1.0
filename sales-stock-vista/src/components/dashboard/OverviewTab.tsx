
import React from 'react';
import { MetricCard } from './MetricCard';
import { TopProductsChart } from './TopProductsChart';
import { NegativeMarginsList } from './NegativeMarginsList';

export const OverviewTab = () => {
  const metrics = [
    {
      title: 'Total Revenue',
      value: '$1,59,556.75',
      change: '+15% vs last period',
      changeType: 'positive' as const,
      icon: '$',
    },
    {
      title: 'Units Sold',
      value: '6,217',
      change: '+8% vs last period',
      changeType: 'positive' as const,
      icon: '📦',
    },
    {
      title: 'Stock Remaining',
      value: '10',
      change: 'Total inventory',
      changeType: 'neutral' as const,
      icon: '📊',
    },
    {
      title: 'Avg Profit Margin',
      value: '58.1%',
      change: '+2% vs last period',
      changeType: 'positive' as const,
      icon: '%',
    },
    {
      title: 'Top Product',
      value: '$18,010.06',
      change: 'HERQUAKE THRUSTING RABBIT - TE...',
      changeType: 'neutral' as const,
      icon: '🏆',
    },
  ];

  const alertMetrics = [
    {
      title: 'Negative Margins',
      value: '22',
      change: 'Products need attention',
      changeType: 'negative' as const,
      icon: '⚠️',
    },
    {
      title: 'High Margin Products',
      value: '589',
      change: '>50% margin',
      changeType: 'positive' as const,
      icon: '⭐',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Section */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Welcome back, Analytics Team 👋</h2>
        <p className="text-slate-600">Here's what's happening with your business today.</p>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        {metrics.map((metric, index) => (
          <div key={index} className="animate-fade-in-up" style={{ animationDelay: `${index * 100}ms` }}>
            <MetricCard {...metric} />
          </div>
        ))}
      </div>

      {/* Alert Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {alertMetrics.map((metric, index) => (
          <div key={index} className="animate-slide-in-right" style={{ animationDelay: `${index * 200}ms` }}>
            <MetricCard {...metric} />
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="animate-fade-in-up" style={{ animationDelay: '600ms' }}>
          <TopProductsChart />
        </div>
        <div className="animate-fade-in-up" style={{ animationDelay: '700ms' }}>
          <NegativeMarginsList />
        </div>
      </div>
    </div>
  );
};
