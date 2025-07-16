
import React from 'react';

interface MetricCardProps {
  title: string;
  value: string;
  change: string;
  changeType: 'positive' | 'negative' | 'neutral';
  icon: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  changeType,
  icon,
}) => {
  const getChangeColor = () => {
    switch (changeType) {
      case 'positive':
        return 'text-emerald-600 bg-emerald-50';
      case 'negative':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-slate-600 bg-slate-50';
    }
  };

  const getIconBackground = () => {
    switch (changeType) {
      case 'positive':
        return 'gradient-accent';
      case 'negative':
        return 'bg-gradient-to-br from-red-500 to-pink-500';
      default:
        return 'gradient-secondary';
    }
  };

  return (
    <div className="card-premium hover-lift group cursor-pointer">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className={`w-12 h-12 ${getIconBackground()} rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}>
            <span className="text-white text-xl font-bold">{icon}</span>
          </div>
          <div className={`px-3 py-1 rounded-full text-xs font-semibold ${getChangeColor()}`}>
            {change}
          </div>
        </div>
        
        <div className="mb-2">
          <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wide mb-1">{title}</h3>
          <span className="text-3xl font-bold text-slate-800 group-hover:text-gradient-primary transition-all duration-300">{value}</span>
        </div>
        
        <div className="h-1 bg-slate-100 rounded-full overflow-hidden">
          <div className={`h-full ${getIconBackground()} rounded-full transition-all duration-1000 group-hover:w-full`} style={{width: '60%'}}></div>
        </div>
      </div>
    </div>
  );
};
