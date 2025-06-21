import React, { useEffect, useState } from 'react';
import { Shield, Activity, AlertCircle, CheckCircle, Moon, Sun } from 'lucide-react';
import { apiService } from '../services/api';
import type { HealthResponse } from '../types/api';

interface HeaderProps {
  darkMode: boolean;
  onToggleDarkMode: () => void;
}

export default function Header({ darkMode, onToggleDarkMode }: HeaderProps) {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const healthData = await apiService.getHealth();
        setHealth(healthData);
      } catch (error) {
        console.error('Health check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = () => {
    if (loading) return <Activity className="w-4 h-4 animate-spin" />;
    if (!health || health.status !== 'healthy') return <AlertCircle className="w-4 h-4 text-red-500" />;
    return <CheckCircle className="w-4 h-4 text-green-500" />;
  };

  const getStatusText = () => {
    if (loading) return 'Checking...';
    if (!health) return 'Offline';
    return health.status === 'healthy' ? 'Online' : 'Issues Detected';
  };

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">PII Redaction Suite</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">Secure data protection & privacy compliance</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-gray-50 dark:bg-gray-700 rounded-lg transition-colors duration-300">
              {getStatusIcon()}
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Service: {getStatusText()}
              </span>
            </div>
            {health && (
              <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 bg-blue-50 dark:bg-blue-900/20 rounded-lg transition-colors duration-300">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-sm text-blue-700 dark:text-blue-400">
                  Model: {health.model}
                </span>
              </div>
            )}
            <button
              onClick={onToggleDarkMode}
              className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
              title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {darkMode ? (
                <Sun className="w-5 h-5 text-yellow-500" />
              ) : (
                <Moon className="w-5 h-5 text-gray-600" />
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}