
import React, { useState } from 'react';
import { ProductTable } from './ProductTable';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export const ProductAnalysisTab = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <Input
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full"
            />
          </div>
          <div className="w-48">
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="vibrators">Vibrators</SelectItem>
                <SelectItem value="other">Other</SelectItem>
                <SelectItem value="supplements">Supplements</SelectItem>
                <SelectItem value="clothing">Clothing & Accessories</SelectItem>
                <SelectItem value="lubricants">Lubricants</SelectItem>
                <SelectItem value="adult-toys">Adult Toys</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        
        <ProductTable searchTerm={searchTerm} categoryFilter={categoryFilter} />
      </div>
    </div>
  );
};
