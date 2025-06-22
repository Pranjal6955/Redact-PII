import React from 'react';
import { Check } from 'lucide-react';

const PII_TYPES = [
  { id: 'name', label: 'Names', description: 'Personal names and identities' },
  { id: 'email', label: 'Email Addresses', description: 'Email contact information' },
  { id: 'phone', label: 'Phone Numbers', description: 'Telephone and mobile numbers' },
  { id: 'address', label: 'Physical Addresses', description: 'Home and business addresses' },
  { id: 'credit_card', label: 'Credit Card Numbers', description: 'Payment card information' },
  { id: 'date', label: 'Dates of Birth', description: 'Birth dates and sensitive dates' },
];

interface PIITypeSelectorProps {
  selectedTypes: string[];
  onChange: (types: string[]) => void;
  className?: string;
}

export default function PIITypeSelector({ selectedTypes, onChange, className = '' }: PIITypeSelectorProps) {
  const handleToggle = (typeId: string) => {
    if (selectedTypes.includes(typeId)) {
      onChange(selectedTypes.filter(id => id !== typeId));
    } else {
      onChange([...selectedTypes, typeId]);
    }
  };

  const handleSelectAll = () => {
    if (selectedTypes.length === PII_TYPES.length) {
      onChange([]);
    } else {
      onChange(PII_TYPES.map(type => type.id));
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex justify-between items-center">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          PII Types to Redact
        </label>
        <button
          type="button"
          onClick={handleSelectAll}
          className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
        >
          {selectedTypes.length === PII_TYPES.length ? 'Deselect All' : 'Select All'}
        </button>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {PII_TYPES.map((type) => {
          const isSelected = selectedTypes.includes(type.id);
          return (
            <div
              key={type.id}
              onClick={() => handleToggle(type.id)}
              className={`relative p-3 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
                isSelected
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 ring-1 ring-blue-500'
                  : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 hover:border-gray-300 dark:hover:border-gray-500 hover:bg-gray-50 dark:hover:bg-gray-600'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center mt-0.5 ${
                  isSelected
                    ? 'bg-blue-500 border-blue-500'
                    : 'border-gray-300 dark:border-gray-500'
                }`}>
                  {isSelected && <Check className="w-3 h-3 text-white" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium ${
                    isSelected ? 'text-blue-900 dark:text-blue-300' : 'text-gray-900 dark:text-white'
                  }`}>
                    {type.label}
                  </p>
                  <p className={`text-xs mt-1 ${
                    isSelected ? 'text-blue-700 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400'
                  }`}>
                    {type.description}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="text-sm text-gray-600 dark:text-gray-400">
        {selectedTypes.length} of {PII_TYPES.length} types selected
      </div>
    </div>
  );
}