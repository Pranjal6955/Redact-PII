import React, { useState } from 'react';
import { FileText, Zap, Copy, Download, AlertCircle } from 'lucide-react';
import PIITypeSelector from './PIITypeSelector';
import CustomTagsInput from './CustomTagsInput';
import ResultsDisplay from './ResultsDisplay';
import { apiService } from '../services/api';
import type { RedactionResponse } from '../types/api';

export default function TextRedaction() {
  const [text, setText] = useState('');
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [customTags, setCustomTags] = useState<Record<string, string>>({});
  const [results, setResults] = useState<RedactionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  const handleRedact = async () => {
    if (!text.trim()) {
      setError('Please enter some text to redact');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiService.redactText({
        text: text.trim(),
        redact_types: selectedTypes,
        custom_tags: Object.keys(customTags).length > 0 ? customTags : undefined,
        auto_detect_all: selectedTypes.length === 0, // Auto-detect all if no types are selected
      });
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to redact text');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async (textToCopy: string) => {
    try {
      await navigator.clipboard.writeText(textToCopy);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const handleDownload = (textToDownload: string, filename: string) => {
    const blob = new Blob([textToDownload], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadPdf = async () => {
    if (!results) return;
    
    setDownloadingPdf(true);
    try {
      const timestamp = new Date().toISOString().slice(0, 19).replace(/[:\-T]/g, '_');
      const filename = `redacted_text_${timestamp}.pdf`;
      
      // Create PDF on server
      const pdfInfo = await apiService.createPdfFromText(results.redacted, filename);
      
      // Download the created PDF
      const blob = await apiService.downloadFile(pdfInfo.filename);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = pdfInfo.filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download PDF');
    } finally {
      setDownloadingPdf(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-300">
        <div className="flex items-center space-x-2 mb-4">
          <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Text Input</h2>
        </div>
        
        <div className="space-y-4">
          <div>
            <label htmlFor="text-input" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Enter text containing PII to redact
            </label>
            <textarea
              id="text-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste your text here... For example: 'My name is John Doe, email: john.doe@example.com, phone: (555) 123-4567'"
              className="w-full h-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-colors duration-300"
            />
            <div className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {text.length} characters
            </div>
          </div>
        </div>
      </div>

      {/* Configuration Section */}
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
          onClick={handleRedact}
          disabled={loading || !text.trim() || selectedTypes.length === 0}
          className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-lg shadow-sm hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          {loading ? (
            <>
              <Zap className="w-5 h-5 mr-2 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Zap className="w-5 h-5 mr-2" />
              Redact Text
            </>
          )}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 transition-colors duration-300">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
            <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
          </div>
        </div>
      )}

      {/* Results Section */}
      {results && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-300">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Redaction Results</h2>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handleCopy(results.redacted)}
                className="inline-flex items-center px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                <Copy className="w-4 h-4 mr-1" />
                Copy
              </button>
              <button
                onClick={() => handleDownload(results.redacted, 'redacted-text.txt')}
                className="inline-flex items-center px-3 py-1.5 text-sm bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded-md hover:bg-blue-200 dark:hover:bg-blue-900/40 transition-colors"
              >
                <Download className="w-4 h-4 mr-1" />
                TXT
              </button>
              <button
                onClick={handleDownloadPdf}
                disabled={downloadingPdf}
                className="inline-flex items-center px-3 py-1.5 text-sm bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md hover:bg-red-200 dark:hover:bg-red-900/40 transition-colors disabled:opacity-50"
              >
                {downloadingPdf ? (
                  <>
                    <Download className="w-4 h-4 mr-1 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-1" />
                    PDF
                  </>
                )}
              </button>
            </div>
          </div>
          
          <ResultsDisplay
            original={results.original}
            redacted={results.redacted}
            summary={results.summary}
            redactTypesUsed={results.redact_types_used}
          />
        </div>
      )}
    </div>
  );
}