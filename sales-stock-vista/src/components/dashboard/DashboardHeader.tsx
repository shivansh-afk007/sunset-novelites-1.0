
import React from 'react';
import { Settings, Bell, User } from 'lucide-react';

interface DashboardHeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'product-analysis', label: 'Product Analysis', icon: '📦' },
    { id: 'category-analysis', label: 'Category Analysis', icon: '🏷️' },
    { id: 'charts-analytics', label: 'Charts & Analytics', icon: '📈' },
    { id: 'insights', label: 'Insights & Recommendations', icon: '💡' },
  ];

  return (
    <div className="bg-gradient-to-r from-slate-50 via-white to-slate-50 border-b border-slate-200/60 shadow-elegant">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-6">
          {/* Company Header */}
          <div className="text-center flex-1">
            <div className="flex items-center justify-center mb-3">
              <div className="w-10 h-10 gradient-primary rounded-2xl flex items-center justify-center mr-4 shadow-lg hover-glow">
                <span className="text-white font-bold text-xl">🌅</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gradient-primary">Sunset Novelties</h1>
                <p className="text-sm text-slate-600 font-medium">Advanced Sales Intelligence Platform</p>
              </div>
            </div>
            <div className="flex items-center justify-center space-x-4 text-xs text-slate-500">
              <span className="flex items-center">
                <div className="w-2 h-2 bg-emerald-400 rounded-full mr-2 animate-pulse"></div>
                Live Analytics
              </span>
              <span>•</span>
              <span>Report Generated: June 22, 2025 at 02:24 PM</span>
            </div>
          </div>
          
          {/* Action Icons */}
          <div className="flex items-center space-x-3">
            <button className="p-3 hover:bg-slate-100 rounded-xl transition-all duration-200 relative hover-lift">
              <Bell className="w-5 h-5 text-slate-600" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
            </button>
            <button className="p-3 hover:bg-slate-100 rounded-xl transition-all duration-200 hover-lift">
              <Settings className="w-5 h-5 text-slate-600" />
            </button>
            <button className="p-3 hover:bg-slate-100 rounded-xl transition-all duration-200 hover-lift">
              <User className="w-5 h-5 text-slate-600" />
            </button>
          </div>
        </div>
        
        {/* Navigation Tabs */}
        <div className="flex space-x-2 overflow-x-auto pb-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center px-6 py-4 text-sm font-semibold rounded-xl whitespace-nowrap transition-all duration-300 hover-lift ${
                activeTab === tab.id
                  ? 'gradient-primary text-white shadow-lg shadow-indigo-500/25'
                  : 'text-slate-600 hover:text-slate-800 hover:bg-white hover:shadow-md bg-slate-50/50'
              }`}
            >
              <span className="mr-3 text-lg">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
