import { useState, useEffect } from 'react';
import { Shield, Check, Info, AlertCircle, Zap } from 'lucide-react';
import { apiService } from '../services/api';
import type { PIITypeCategory, SupportedTypesResponse } from '../types/api';

interface PIITypeSelectorProps {
  selectedTypes: string[];
  onChange: (types: string[]) => void;
  className?: string;
}

export default function PIITypeSelector({ selectedTypes, onChange, className = '' }: PIITypeSelectorProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [supportedTypes, setSupportedTypes] = useState<SupportedTypesResponse | null>(null);
  const [categories, setCategories] = useState<PIITypeCategory[]>([]);
  const [mode, setMode] = useState<'auto' | 'manual'>('auto');

  // Fetch supported PII types from API
  useEffect(() => {
    const fetchSupportedTypes = async () => {
      try {
        setLoading(true);
        const data = await apiService.getSupportedTypes();
        setSupportedTypes(data);
        
        // Transform categories into a format easy to render
        const categoryList: PIITypeCategory[] = [];
        
        if (data.categories) {
          Object.entries(data.categories).forEach(([categoryId, typeIds]) => {
            const categoryLabel = getCategoryLabel(categoryId);
            const types = typeIds.map(id => ({
              id,
              label: getTypeLabel(id),
              description: getTypeDescription(id),
              category: categoryId,
              critical: data.critical_types.includes(id)
            }));
            
            categoryList.push({
              id: categoryId,
              label: categoryLabel,
              types
            });
          });
        }
        
        setCategories(categoryList);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load supported PII types');
        // Fallback to basic types if API fails
        setCategories(getBasicCategories());
      } finally {
        setLoading(false);
      }
    };
    
    fetchSupportedTypes();
  }, []);

  const toggleType = (type: string) => {
    if (selectedTypes.includes(type)) {
      onChange(selectedTypes.filter(t => t !== type));
    } else {
      onChange([...selectedTypes, type]);
    }
  };

  const toggleCategory = (categoryTypes: string[]) => {
    const allSelected = categoryTypes.every(type => selectedTypes.includes(type));
    
    if (allSelected) {
      // Remove all types in this category
      onChange(selectedTypes.filter(type => !categoryTypes.includes(type)));
    } else {
      // Add all types in this category that aren't already selected
      const newTypes = categoryTypes.filter(type => !selectedTypes.includes(type));
      onChange([...selectedTypes, ...newTypes]);
    }
  };

  const selectCommonTypes = () => {
    if (supportedTypes?.common_types) {
      onChange(supportedTypes.common_types);
    } else {
      onChange(['name', 'email', 'phone', 'address', 'ssn', 'credit_card']);
    }
  };

  const selectAllTypes = () => {
    if (supportedTypes?.all_supported) {
      onChange(supportedTypes.all_supported);
    } else {
      const allTypes = categories.flatMap(category => category.types.map(type => type.id));
      onChange(allTypes);
    }
  };

  const selectCriticalTypes = () => {
    if (supportedTypes?.critical_types) {
      onChange(supportedTypes.critical_types);
    } else {
      onChange(['ssn', 'credit_card', 'bank_account', 'passport', 'drivers_license']);
    }
  };

  const clearSelection = () => {
    onChange([]);
    setMode('auto');
  };

  const handleModeChange = (newMode: 'auto' | 'manual') => {
    setMode(newMode);
    if (newMode === 'auto') {
      clearSelection();
    } else {
      // In manual mode, select common types as a starting point
      selectCommonTypes();
    }
  };

  // Helper function to get category labels
  const getCategoryLabel = (categoryId: string): string => {
    const labels: Record<string, string> = {
      'identity': 'Identity Information',
      'financial': 'Financial Information',
      'contact': 'Contact Information',
      'medical': 'Medical Information',
      'employment': 'Employment Information',
      'technical': 'Technical Identifiers',
      'vehicle': 'Vehicle Information',
      'temporal': 'Temporal Information'
    };
    return labels[categoryId] || categoryId.charAt(0).toUpperCase() + categoryId.slice(1);
  };

  // Helper function to get type labels
  const getTypeLabel = (typeId: string): string => {
    const labels: Record<string, string> = {
      'name': 'Names',
      'email': 'Email Addresses',
      'phone': 'Phone Numbers',
      'address': 'Physical Addresses',
      'ssn': 'Social Security Numbers',
      'credit_card': 'Credit Card Numbers',
      'date': 'Dates',
      'drivers_license': 'Driver\'s Licenses',
      'passport': 'Passport Numbers',
      'bank_account': 'Bank Accounts',
      'ip_address': 'IP Addresses',
      'medical_record': 'Medical Records',
      'employee_id': 'Employee IDs',
      'license_plate': 'License Plates',
      'vin': 'Vehicle IDs (VIN)',
      'insurance_policy': 'Insurance Policies',
      'tax_id': 'Tax IDs / EINs',
      'credit_score': 'Credit Scores',
      'biometric': 'Biometric IDs',
      'personal_url': 'Personal URLs',
      'mac_address': 'MAC Addresses',
      'guid': 'GUIDs/UUIDs'
    };
    return labels[typeId] || typeId.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  // Helper function to get type descriptions
  const getTypeDescription = (typeId: string): string => {
    const descriptions: Record<string, string> = {
      'name': 'Personal names, full names, first and last names',
      'email': 'Email addresses in any format',
      'phone': 'Phone numbers in various formats',
      'address': 'Physical addresses including street, city, state, zip',
      'ssn': 'Social Security Numbers in any format',
      'credit_card': 'Credit and debit card numbers',
      'date': 'Personal dates including birth dates',
      'drivers_license': 'Driver\'s license numbers',
      'passport': 'Passport numbers',
      'bank_account': 'Bank account numbers',
      'ip_address': 'IP addresses (IPv4 and IPv6)',
      'medical_record': 'Medical record numbers and patient IDs',
      'employee_id': 'Employee identification numbers',
      'license_plate': 'Vehicle license plate numbers',
      'vin': 'Vehicle Identification Numbers',
      'insurance_policy': 'Insurance policy numbers',
      'tax_id': 'Tax Identification Numbers, EINs',
      'credit_score': 'Credit scores (FICO, etc.)',
      'biometric': 'Biometric identifiers, fingerprint IDs',
      'personal_url': 'Personal social media URLs',
      'mac_address': 'Media Access Control addresses',
      'guid': 'Globally Unique Identifiers'
    };
    return descriptions[typeId] || '';
  };

  // Fallback categories if API fails
  const getBasicCategories = (): PIITypeCategory[] => {
    return [
      {
        id: 'identity',
        label: 'Identity Information',
        types: [
          { id: 'name', label: 'Names', description: 'Personal names, full names, first and last names', critical: false },
          { id: 'ssn', label: 'Social Security Numbers', description: 'Social Security Numbers in any format', critical: true },
          { id: 'drivers_license', label: 'Driver\'s Licenses', description: 'Driver\'s license numbers', critical: true },
          { id: 'passport', label: 'Passport Numbers', description: 'Passport numbers', critical: true }
        ]
      },
      {
        id: 'contact',
        label: 'Contact Information',
        types: [
          { id: 'email', label: 'Email Addresses', description: 'Email addresses in any format', critical: false },
          { id: 'phone', label: 'Phone Numbers', description: 'Phone numbers in various formats', critical: false },
          { id: 'address', label: 'Physical Addresses', description: 'Physical addresses including street, city, state, zip', critical: false }
        ]
      },
      {
        id: 'financial',
        label: 'Financial Information',
        types: [
          { id: 'credit_card', label: 'Credit Card Numbers', description: 'Credit and debit card numbers', critical: true },
          { id: 'bank_account', label: 'Bank Accounts', description: 'Bank account numbers', critical: true }
        ]
      },
      {
        id: 'other',
        label: 'Other Information',
        types: [
          { id: 'date', label: 'Dates', description: 'Personal dates including birth dates', critical: false },
          { id: 'ip_address', label: 'IP Addresses', description: 'IP addresses (IPv4 and IPv6)', critical: false }
        ]
      }
    ];
  };

  if (loading) {
    return (
      <div className={`flex justify-center items-center py-8 ${className}`}>
        <Zap className="w-5 h-5 text-blue-500 animate-spin mr-2" />
        <span className="text-sm text-gray-600 dark:text-gray-400">Loading PII types...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 ${className}`}>
        <div className="flex items-start">
          <AlertCircle className="w-5 h-5 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
            <p className="text-xs text-red-600 dark:text-red-300 mt-1">Using basic PII types instead.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex items-center space-x-2">
        <Shield className="w-4 h-4 text-gray-500 dark:text-gray-400" />
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          PII Detection Mode
        </label>
      </div>

      {/* Detection Mode Selection */}
      <div className="flex items-center space-x-4 mb-4">
        <div className="flex items-center">
          <input
            type="radio"
            id="auto-detect"
            name="detection-mode"
            checked={mode === 'auto'}
            onChange={() => handleModeChange('auto')}
            className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 focus:ring-blue-500 dark:bg-gray-700"
          />
          <label htmlFor="auto-detect" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
            Auto-detect all PII types
          </label>
        </div>

        <div className="flex items-center">
          <input
            type="radio"
            id="manual-select"
            name="detection-mode"
            checked={mode === 'manual'}
            onChange={() => handleModeChange('manual')}
            className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 focus:ring-blue-500 dark:bg-gray-700"
          />
          <label htmlFor="manual-select" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
            Select specific PII types
          </label>
        </div>
      </div>

      {/* Auto-detect Info Box */}
      {mode === 'auto' && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 transition-colors duration-300">
          <div className="flex items-start">
            <Info className="w-5 h-5 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm text-blue-700 dark:text-blue-300 font-medium">Automatic PII Detection</p>
              <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                The system will automatically detect all {supportedTypes?.total_types || 'supported'} types of PII in your content, including names, 
                contact information, financial data, identification numbers, and more.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Manual Type Selection */}
      {mode === 'manual' && (
        <>
          {/* Quick Selection Buttons */}
          <div className="flex flex-wrap gap-2 mb-4">
            <button
              onClick={selectCommonTypes}
              className="px-3 py-1.5 text-xs bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded-md hover:bg-blue-200 dark:hover:bg-blue-900/40 transition-colors"
            >
              Common Types
            </button>
            <button
              onClick={selectCriticalTypes}
              className="px-3 py-1.5 text-xs bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 rounded-md hover:bg-amber-200 dark:hover:bg-amber-900/40 transition-colors"
            >
              Critical Types
            </button>
            <button
              onClick={selectAllTypes}
              className="px-3 py-1.5 text-xs bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-400 rounded-md hover:bg-purple-200 dark:hover:bg-purple-900/40 transition-colors"
            >
              All Types
            </button>
            <button
              onClick={clearSelection}
              className="px-3 py-1.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              Clear
            </button>
          </div>

          <div className="space-y-4">
            {categories.map((category) => (
              <div key={category.id} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden transition-colors duration-300">
                {/* Category Header */}
                <div 
                  className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 p-3 cursor-pointer transition-colors duration-300"
                  onClick={() => toggleCategory(category.types.map(type => type.id))}
                >
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{category.label}</span>
                    <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                      ({category.types.filter(type => selectedTypes.includes(type.id)).length}/{category.types.length})
                    </span>
                  </div>
                  <div className="flex items-center space-x-1">
                    {category.types.some(type => type.critical) && (
                      <span className="px-2 py-0.5 text-xs bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 rounded">
                        Contains Critical PII
                      </span>
                    )}
                  </div>
                </div>

                {/* Category Types */}
                <div className="p-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                  {category.types.map((type) => (
                    <div key={type.id} className="flex items-center">
                      <input
                        type="checkbox"
                        id={`pii-type-${type.id}`}
                        checked={selectedTypes.includes(type.id)}
                        onChange={() => toggleType(type.id)}
                        className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500 dark:bg-gray-700"
                      />
                      <label 
                        htmlFor={`pii-type-${type.id}`} 
                        className="ml-2 text-sm text-gray-700 dark:text-gray-300 flex items-center"
                        title={type.description}
                      >
                        {type.label}
                        {type.critical && (
                          <span className="ml-1 inline-flex items-center">
                            <AlertCircle className="w-3 h-3 text-amber-500" />
                          </span>
                        )}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Selected Types Summary */}
          <div className="mt-4 px-4 py-3 bg-gray-50 dark:bg-gray-800 rounded-lg transition-colors duration-300">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {selectedTypes.length === 0 
                  ? 'No types selected (will use auto-detection)' 
                  : `${selectedTypes.length} ${selectedTypes.length === 1 ? 'type' : 'types'} selected`}
              </span>
              {selectedTypes.length > 0 && (
                <button
                  onClick={clearSelection}
                  className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                >
                  Clear
                </button>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}