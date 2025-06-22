import React from 'react';
import { Tag, X } from 'lucide-react';

interface CustomTagsInputProps {
  customTags: Record<string, string>;
  onChange: (tags: Record<string, string>) => void;
  selectedTypes: string[];
  className?: string;
}

const DEFAULT_TAGS: Record<string, string> = {
  name: '[REDACTED_NAME]',
  email: '[REDACTED_EMAIL]',
  phone: '[REDACTED_PHONE]',
  address: '[REDACTED_ADDRESS]',
  ssn: '[REDACTED_SSN]',
  credit_card: '[REDACTED_CREDIT_CARD]',
  date: '[REDACTED_DATE]',
  drivers_license: '[REDACTED_DRIVERS_LICENSE]',
  passport: '[REDACTED_PASSPORT]',
  bank_account: '[REDACTED_BANK_ACCOUNT]',
  ip_address: '[REDACTED_IP_ADDRESS]',
  medical_record: '[REDACTED_MEDICAL_RECORD]',
  employee_id: '[REDACTED_EMPLOYEE_ID]',
  license_plate: '[REDACTED_LICENSE_PLATE]',
  vin: '[REDACTED_VIN]',
  insurance_policy: '[REDACTED_INSURANCE_POLICY]',
  tax_id: '[REDACTED_TAX_ID]',
  credit_score: '[REDACTED_CREDIT_SCORE]',
  biometric: '[REDACTED_BIOMETRIC]',
  personal_url: '[REDACTED_PERSONAL_URL]',
  mac_address: '[REDACTED_MAC_ADDRESS]',
  guid: '[REDACTED_GUID]'
};

const TYPE_LABELS: Record<string, string> = {
  name: 'Names',
  email: 'Email Addresses',
  phone: 'Phone Numbers',
  address: 'Physical Addresses',
  ssn: 'Social Security Numbers',
  credit_card: 'Credit Card Numbers',
  date: 'Dates',
  drivers_license: 'Driver\'s Licenses',
  passport: 'Passport Numbers',
  bank_account: 'Bank Accounts',
  ip_address: 'IP Addresses',
  medical_record: 'Medical Records',
  employee_id: 'Employee IDs',
  license_plate: 'License Plates',
  vin: 'Vehicle IDs (VIN)',
  insurance_policy: 'Insurance Policies',
  tax_id: 'Tax IDs / EINs',
  credit_score: 'Credit Scores',
  biometric: 'Biometric IDs',
  personal_url: 'Personal URLs',
  mac_address: 'MAC Addresses',
  guid: 'GUIDs/UUIDs'
};

export default function CustomTagsInput({ customTags, onChange, selectedTypes, className = '' }: CustomTagsInputProps) {
  const handleTagChange = (type: string, value: string) => {
    onChange({
      ...customTags,
      [type]: value,
    });
  };

  const handleRemoveTag = (type: string) => {
    const newTags = { ...customTags };
    delete newTags[type];
    onChange(newTags);
  };

  const handleResetToDefault = (type: string) => {
    onChange({
      ...customTags,
      [type]: DEFAULT_TAGS[type],
    });
  };

  if (selectedTypes.length === 0) {
    return (
      <div className={`text-center py-8 text-gray-500 dark:text-gray-400 ${className}`}>
        <Tag className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">Select PII types to configure custom replacement tags</p>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex items-center space-x-2">
        <Tag className="w-4 h-4 text-gray-500 dark:text-gray-400" />
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Custom Replacement Tags (Optional)
        </label>
      </div>
      
      <div className="space-y-3">
        {selectedTypes.map((type) => (
          <div key={type} className="flex items-center space-x-3">
            <div className="flex-shrink-0 w-24 text-sm text-gray-600 dark:text-gray-400">
              {TYPE_LABELS[type]}
            </div>
            <div className="flex-1">
              <input
                type="text"
                value={customTags[type] || ''}
                onChange={(e) => handleTagChange(type, e.target.value)}
                placeholder={DEFAULT_TAGS[type]}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-colors duration-300"
              />
            </div>
            <div className="flex items-center space-x-1">
              {customTags[type] && (
                <>
                  <button
                    type="button"
                    onClick={() => handleResetToDefault(type)}
                    className="p-1 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                    title="Reset to default"
                  >
                    <Tag className="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(type)}
                    className="p-1 text-gray-400 dark:text-gray-500 hover:text-red-500 transition-colors"
                    title="Remove custom tag"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
      
      <div className="text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 p-3 rounded-md transition-colors duration-300">
        <p className="font-medium mb-1">Tip:</p>
        <p>Leave empty to use default tags. Custom tags will replace the detected PII with your specified text.</p>
      </div>
    </div>
  );
}