import React, { useState, useCallback } from 'react';
import { Upload, File, Download, AlertCircle, CheckCircle, FileText, Zap } from 'lucide-react';
import PIITypeSelector from './PIITypeSelector';
import CustomTagsInput from './CustomTagsInput';
import { apiService } from '../services/api';
import type { FileUploadResponse } from '../types/api';

export default function FileUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [customTags, setCustomTags] = useState<Record<string, string>>({});
  const [exportFormat, setExportFormat] = useState<string>('both');
  const [useOCR, setUseOCR] = useState(false);
  const [preservePdfFormat, setPreservePdfFormat] = useState(true);
  const [comprehensiveScan, setComprehensiveScan] = useState(true);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<FileUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      validateAndSetFile(files[0]);
    }
  }, []);

  const validateAndSetFile = (file: File) => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['application/pdf', 'text/plain'];

    if (file.size > maxSize) {
      setError('File size must be less than 10MB');
      return;
    }

    if (!allowedTypes.includes(file.type)) {
      setError('Only PDF and TXT files are supported');
      return;
    }

    setSelectedFile(file);
    setError(null);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      validateAndSetFile(files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const response = await apiService.uploadFile(
        selectedFile,
        selectedTypes,
        Object.keys(customTags).length > 0 ? customTags : undefined,
        exportFormat,
        useOCR,
        preservePdfFormat,
        comprehensiveScan
      );
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process file');
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadFile = async (filename: string) => {
    try {
      const blob = await apiService.downloadFile(filename);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download file');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* File Upload Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-300">
        <div className="flex items-center space-x-2 mb-4">
          <Upload className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">File Upload</h2>
        </div>

        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${
            dragActive
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
              : selectedFile
              ? 'border-green-300 bg-green-50 dark:bg-green-900/20'
              : 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 hover:border-gray-400 dark:hover:border-gray-500'
          }`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="file-upload"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            accept=".pdf,.txt"
            onChange={handleFileSelect}
          />

          {selectedFile ? (
            <div className="space-y-3">
              <CheckCircle className="w-12 h-12 text-green-500 mx-auto" />
              <div>
                <p className="text-lg font-medium text-gray-900 dark:text-white">{selectedFile.name}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {formatFileSize(selectedFile.size)} • {selectedFile.type.includes('pdf') ? 'PDF Document' : 'Text File'}
                </p>
              </div>
              <button
                onClick={() => setSelectedFile(null)}
                className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
              >
                Choose different file
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              <File className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto" />
              <div>
                <p className="text-lg font-medium text-gray-900 dark:text-white">
                  {dragActive ? 'Drop your file here' : 'Drag and drop your file here'}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">or click to browse</p>
              </div>
              <div className="text-xs text-gray-400 dark:text-gray-500">
                Supports PDF and TXT files up to 10MB
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Processing Options */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-300">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Processing Options</h2>
        
        <div className="space-y-6">
          {/* Export Format */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Export Format</label>
            <div className="flex space-x-4">
              {[
                { value: 'pdf', label: 'PDF Only' },
                { value: 'txt', label: 'Text Only' },
                { value: 'both', label: 'Both Formats' },
              ].map((option) => (
                <label key={option.value} className="flex items-center">
                  <input
                    type="radio"
                    name="export-format"
                    value={option.value}
                    checked={exportFormat === option.value}
                    onChange={(e) => setExportFormat(e.target.value)}
                    className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 focus:ring-blue-500 dark:bg-gray-700"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">{option.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Comprehensive Scan Option */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="comprehensive-scan"
              checked={comprehensiveScan}
              onChange={(e) => setComprehensiveScan(e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500 dark:bg-gray-700"
            />
            <label htmlFor="comprehensive-scan" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              Enable comprehensive PII detection
              <span className="text-gray-500 dark:text-gray-400 ml-1">(detects 20+ types of personal information)</span>
            </label>
          </div>

          {/* OCR Option */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="use-ocr"
              checked={useOCR}
              onChange={(e) => setUseOCR(e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500 dark:bg-gray-700"
            />
            <label htmlFor="use-ocr" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              Force OCR for scanned PDFs
              <span className="text-gray-500 dark:text-gray-400 ml-1">(skips normal text extraction, may take longer)</span>
            </label>
          </div>

          {/* OCR Info */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 transition-colors duration-300">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  <strong>Automatic OCR Fallback:</strong> If normal text extraction fails, the system will automatically try OCR to extract text from scanned PDFs or images.
                </p>
              </div>
            </div>
          </div>

          {/* Preserve PDF Format Option */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="preserve-pdf-format"
              checked={preservePdfFormat}
              onChange={(e) => setPreservePdfFormat(e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500 dark:bg-gray-700"
            />
            <label htmlFor="preserve-pdf-format" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              Preserve original PDF formatting
              <span className="text-gray-500 dark:text-gray-400 ml-1">(maintains layout, images, and structure)</span>
            </label>
          </div>
        </div>
      </div>

      {/* PII Configuration */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-300">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Redaction Configuration</h2>
        
        <div className="space-y-8">
          <PIITypeSelector
            selectedTypes={selectedTypes}
            onChange={setSelectedTypes}
          />
          
          <CustomTagsInput
            customTags={customTags}
            onChange={setCustomTags}
            selectedTypes={selectedTypes}
          />
        </div>
      </div>

      {/* Action Button */}
      <div className="flex justify-center">
        <button
          onClick={handleUpload}
          disabled={uploading || !selectedFile || selectedTypes.length === 0}
          className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-green-600 to-teal-600 text-white font-medium rounded-lg shadow-sm hover:from-green-700 hover:to-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          {uploading ? (
            <>
              <Zap className="w-5 h-5 mr-2 animate-spin" />
              Processing File...
            </>
          ) : (
            <>
              <Upload className="w-5 h-5 mr-2" />
              Process File
            </>
          )}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 transition-colors duration-300">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm text-red-700 dark:text-red-400 font-medium mb-2">{error}</p>
              {error.includes("Failed to extract text") && (
                <div className="text-xs text-red-600 dark:text-red-300 space-y-1">
                  <p><strong>Possible solutions:</strong></p>
                  <ul className="list-disc list-inside ml-2 space-y-1">
                    <li>Try enabling "Force OCR for scanned PDFs" option</li>
                    <li>Check if the PDF contains actual text (not just images)</li>
                    <li>Try a different PDF file</li>
                    <li>Ensure the PDF is not corrupted or password-protected</li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Results Section */}
      {results && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-300">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Processing Results</h2>
          
          <div className="space-y-6">
            {/* Summary */}
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 transition-colors duration-300">
              <div className="flex items-center mb-2">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                <p className="font-medium text-green-900 dark:text-green-400">File processed successfully!</p>
              </div>
              <div className="text-sm text-green-700 dark:text-green-400 space-y-1">
                {Object.entries(results.summary).map(([type, count]) => (
                  <p key={type}>
                    {count} {type.replace('_', ' ')} redacted
                  </p>
                ))}
              </div>
            </div>

            {/* Generated Files */}
            <div>
              <h3 className="text-md font-medium text-gray-900 dark:text-white mb-3">Generated Files</h3>
              <div className="space-y-2">
                {results.files_generated.map((filename) => (
                  <div
                    key={filename}
                    className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg transition-colors duration-300"
                  >
                    <div className="flex items-center space-x-3">
                      <FileText className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">{filename}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {formatFileSize(results.file_sizes[filename])}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDownloadFile(filename)}
                      className="inline-flex items-center px-3 py-1.5 text-sm bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded-md hover:bg-blue-200 dark:hover:bg-blue-900/40 transition-colors"
                    >
                      <Download className="w-4 h-4 mr-1" />
                      Download
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Text Preview */}
            {results.redacted_text && (
              <div>
                <h3 className="text-md font-medium text-gray-900 dark:text-white mb-3">Text Preview</h3>
                <div className="bg-gray-50 dark:bg-gray-700 border rounded-lg p-4 max-h-40 overflow-y-auto transition-colors duration-300">
                  <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                    {results.redacted_text.length > 500 
                      ? results.redacted_text.substring(0, 500) + '...'
                      : results.redacted_text
                    }
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}