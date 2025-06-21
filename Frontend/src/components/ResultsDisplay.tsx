import React, { useState } from 'react';
import { Eye, EyeOff, BarChart3, Copy, Check } from 'lucide-react';

interface ResultsDisplayProps {
  original: string;
  redacted: string;
  summary: Record<string, number>;
  redactTypesUsed: string[];
}

export default function ResultsDisplay({ original, redacted, summary, redactTypesUsed }: ResultsDisplayProps) {
  const [activeTab, setActiveTab] = useState<'redacted' | 'original' | 'comparison'>('redacted');
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const handleCopy = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedText(type);
      setTimeout(() => setCopiedText(null), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const getTotalEntities = () => {
    return Object.values(summary).reduce((sum, count) => sum + count, 0);
  };

  const TYPE_LABELS: Record<string, string> = {
    name: 'Names',
    email: 'Email Addresses',
    phone: 'Phone Numbers',
    address: 'Physical Addresses',
    ssn: 'Social Security Numbers',
    credit_card: 'Credit Card Numbers',
    ip_address: 'IP Addresses',
    url: 'URLs',
    date: 'Dates',
  };

  const getEntityColor = (type: string) => {
    const colors: Record<string, string> = {
      name: 'bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300',
      email: 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300',
      phone: 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300',
      address: 'bg-purple-100 dark:bg-purple-900/20 text-purple-800 dark:text-purple-300',
      ssn: 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300',
      credit_card: 'bg-orange-100 dark:bg-orange-900/20 text-orange-800 dark:text-orange-300',
      ip_address: 'bg-cyan-100 dark:bg-cyan-900/20 text-cyan-800 dark:text-cyan-300',
      url: 'bg-indigo-100 dark:bg-indigo-900/20 text-indigo-800 dark:text-indigo-300',
      date: 'bg-pink-100 dark:bg-pink-900/20 text-pink-800 dark:text-pink-300',
    };
    return colors[type] || 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300';
  };

  return (
    <div className="space-y-6">
      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 transition-colors duration-300">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-900 dark:text-blue-300 mb-1">
              {getTotalEntities()}
            </div>
            <p className="text-sm text-blue-700 dark:text-blue-400">Total PII Redacted</p>
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 transition-colors duration-300">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-900 dark:text-green-300 mb-1">
              {redactTypesUsed.length}
            </div>
            <p className="text-sm text-green-700 dark:text-green-400">PII Types Found</p>
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4 transition-colors duration-300">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-900 dark:text-purple-300 mb-1">
              {Math.round((redacted.length / original.length) * 100)}%
            </div>
            <p className="text-sm text-purple-700 dark:text-purple-400">Text Preserved</p>
          </div>
        </div>
      </div>

      {/* PII Breakdown */}
      <div>
        <h3 className="text-md font-medium text-gray-900 dark:text-white mb-3 flex items-center">
          <BarChart3 className="w-4 h-4 mr-2" />
          PII Detection Summary
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {Object.entries(summary).map(([type, count]) => (
            <div key={type} className={`px-3 py-2 rounded-lg transition-colors duration-300 ${getEntityColor(type)}`}>
              <div className="text-sm font-medium">
                {TYPE_LABELS[type] || type}
              </div>
              <div className="text-lg font-bold">
                {count}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'redacted', label: 'Redacted Text', icon: EyeOff },
            { id: 'original', label: 'Original Text', icon: Eye },
            { id: 'comparison', label: 'Side by Side', icon: BarChart3 },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {activeTab === 'redacted' && (
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-md font-medium text-gray-900 dark:text-white">Redacted Text</h3>
              <button
                onClick={() => handleCopy(redacted, 'redacted')}
                className="inline-flex items-center px-3 py-1.5 text-sm bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded-md hover:bg-blue-200 dark:hover:bg-blue-900/40 transition-colors"
              >
                {copiedText === 'redacted' ? (
                  <>
                    <Check className="w-4 h-4 mr-1" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4 mr-1" />
                    Copy
                  </>
                )}
              </button>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 max-h-96 overflow-y-auto transition-colors duration-300">
              <pre className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{redacted}</pre>
            </div>
          </div>
        )}

        {activeTab === 'original' && (
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-md font-medium text-gray-900 dark:text-white">Original Text</h3>
              <button
                onClick={() => handleCopy(original, 'original')}
                className="inline-flex items-center px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                {copiedText === 'original' ? (
                  <>
                    <Check className="w-4 h-4 mr-1" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4 mr-1" />
                    Copy
                  </>
                )}
              </button>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 max-h-96 overflow-y-auto transition-colors duration-300">
              <pre className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{original}</pre>
            </div>
          </div>
        )}

        {activeTab === 'comparison' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-md font-medium text-gray-900 dark:text-white">Original</h3>
                <button
                  onClick={() => handleCopy(original, 'original-comp')}
                  className="inline-flex items-center px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  {copiedText === 'original-comp' ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                </button>
              </div>
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 h-80 overflow-y-auto transition-colors duration-300">
                <pre className="text-xs text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{original}</pre>
              </div>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-md font-medium text-gray-900 dark:text-white">Redacted</h3>
                <button
                  onClick={() => handleCopy(redacted, 'redacted-comp')}
                  className="inline-flex items-center px-2 py-1 text-xs bg-green-100 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded hover:bg-green-200 dark:hover:bg-green-900/40 transition-colors"
                >
                  {copiedText === 'redacted-comp' ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                </button>
              </div>
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3 h-80 overflow-y-auto transition-colors duration-300">
                <pre className="text-xs text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{redacted}</pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}