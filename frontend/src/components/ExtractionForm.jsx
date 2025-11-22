import React, { useState, useEffect } from 'react';

const ExtractionForm = ({ data }) => {
  const [textExtraction, setTextExtraction] = useState({});
  const [visionExtraction, setVisionExtraction] = useState(null);
  const [activeTab, setActiveTab] = useState('text');
  const [discrepancies, setDiscrepancies] = useState([]);
  const [dismissedFields, setDismissedFields] = useState(new Set());
  const [acceptedValues, setAcceptedValues] = useState({});

  useEffect(() => {
    if (data) {
      try {
        const parsedData = typeof data === 'string' ? JSON.parse(data) : data;
        
        if (parsedData.text_extraction) {
          setTextExtraction(parsedData.text_extraction);
          if (parsedData.vision_extraction) {
            setVisionExtraction(parsedData.vision_extraction);
            calculateDiscrepancies(parsedData.text_extraction, parsedData.vision_extraction);
          }
        } else {
          setTextExtraction(parsedData);
          setVisionExtraction(null);
          setDiscrepancies([]);
        }
        setDismissedFields(new Set());
        setAcceptedValues({});
      } catch (e) {
        console.error("Failed to parse data", e);
        setTextExtraction({ raw_text: data });
        setVisionExtraction(null);
        setDiscrepancies([]);
        setDismissedFields(new Set());
        setAcceptedValues({});
      }
    }
  }, [data]);

  const normalizeValue = (value) => {
    if (value === null || value === undefined) return '';
    
    return String(value)
      .trim()
      .toLowerCase()
      .replace(/\$|usd|dollars?/gi, '')
      .replace(/\s*(kg|kilograms?|lbs?|pounds?)\s*/gi, ' ')
      .replace(/\s+/g, ' ')
      .replace(/[,;.]+\s*$/g, '')
      .replace(/\s*[,;.]\s*/g, ', ')
      .replace(/[\u2018\u2019]/g, "'")
      .replace(/[\u201C\u201D]/g, '"')
      .replace(/\u2013|\u2014/g, '-')
      .replace(/[^\w\s,.-]/g, '')
      .trim();
  };

  const levenshteinDistance = (str1, str2) => {
    const len1 = str1.length;
    const len2 = str2.length;
    const matrix = Array(len2 + 1).fill(null).map(() => Array(len1 + 1).fill(null));

    for (let i = 0; i <= len1; i++) matrix[0][i] = i;
    for (let j = 0; j <= len2; j++) matrix[j][0] = j;

    for (let j = 1; j <= len2; j++) {
      for (let i = 1; i <= len1; i++) {
        const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
        matrix[j][i] = Math.min(
          matrix[j][i - 1] + 1,
          matrix[j - 1][i] + 1,
          matrix[j - 1][i - 1] + cost
        );
      }
    }

    return matrix[len2][len1];
  };

  const valuesMatch = (val1, val2) => {
    const isNull1 = val1 === null || val1 === undefined || String(val1).trim() === '';
    const isNull2 = val2 === null || val2 === undefined || String(val2).trim() === '';
    
    if (isNull1 && isNull2) return true;
    
    if (isNull1 || isNull2) return false;
    
    const norm1 = normalizeValue(val1);
    const norm2 = normalizeValue(val2);
    
    if (norm1 === norm2) return true;
    
    const maxLen = Math.max(norm1.length, norm2.length);
    if (maxLen === 0) return true;
    
    const distance = levenshteinDistance(norm1, norm2);
    const similarity = 1 - distance / maxLen;
    
    return similarity >= 0.95;
  };

  const calculateDiscrepancies = (textData, visionData) => {
    const allKeys = new Set([
      ...Object.keys(textData),
      ...Object.keys(visionData)
    ]);
    
    const diffs = [];
    allKeys.forEach(key => {
      const textVal = textData[key];
      const visionVal = visionData[key];
      if (!valuesMatch(textVal, visionVal)) {
        diffs.push(key);
      }
    });
    
    setDiscrepancies(diffs);
  };

  const hasDiscrepancy = (key) => {
    return discrepancies.includes(key) && !dismissedFields.has(key);
  };

  const dismissDiscrepancy = (key) => {
    setDismissedFields(prev => new Set([...prev, key]));
  };

  const acceptValue = (key, source, newValue) => {
    setAcceptedValues(prev => ({
      ...prev,
      [key]: { source, value: newValue }
    }));
    setDismissedFields(prev => new Set([...prev, key]));
  };

  const getDisplayValue = (key, source, originalValue) => {
    if (acceptedValues[key] && acceptedValues[key].source === source) {
      return acceptedValues[key].value;
    }
    return originalValue;
  };

  const activeDiscrepancies = discrepancies.filter(key => !dismissedFields.has(key));

  const renderFields = (formData, source) => {
    return Object.entries(formData).map(([key, value]) => {
      const hasDiff = visionExtraction && hasDiscrepancy(key);
      const otherValue = source === 'text' ? visionExtraction?.[key] : textExtraction[key];
      const displayValue = getDisplayValue(key, source, value);
      const wasAccepted = acceptedValues[key]?.source === source;
      
      return (
        <div key={key} className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2 capitalize flex items-center justify-between">
            <span>{key.replace(/_/g, ' ')}</span>
            {hasDiff && (
              <div className="flex items-center gap-2">
                <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full font-normal">
                  ⚠ Mismatch
                </span>
                <button
                  onClick={() => dismissDiscrepancy(key)}
                  className="text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 px-2 py-1 rounded whitespace-nowrap"
                >
                  Dismiss
                </button>
                <button
                  onClick={() => acceptValue(key, source, otherValue)}
                  className="text-xs bg-green-500 hover:bg-green-600 text-white px-2 py-1 rounded whitespace-nowrap"
                >
                  Accept Other
                </button>
              </div>
            )}
          </label>
          <input
            type="text"
            value={displayValue || ''}
            readOnly
            className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight ${
              wasAccepted ? 'bg-green-50 border-green-400 border-2' : hasDiff ? 'bg-gray-50 border-red-400 border-2' : 'bg-gray-50'
            }`}
          />
          {hasDiff && (
            <p className="text-xs text-red-600 mt-1">
              {source === 'text' ? 'Vision API' : 'OCR/Text'} extracted: "{otherValue || 'null'}"
            </p>
          )}
          {wasAccepted && (
            <p className="text-xs text-green-600 mt-1">
              ✓ Accepted value from {source === 'text' ? 'Vision API' : 'OCR/Text'}
            </p>
          )}
        </div>
      );
    });
  };

  const renderComparison = () => {
    const allKeys = new Set([
      ...Object.keys(textExtraction),
      ...(visionExtraction ? Object.keys(visionExtraction) : [])
    ]);

    return Array.from(allKeys).map(key => {
      const textValue = textExtraction[key];
      const visionValue = visionExtraction?.[key];
      const hasDiff = hasDiscrepancy(key);
      const textAccepted = acceptedValues[key]?.source === 'text';
      const visionAccepted = acceptedValues[key]?.source === 'vision';
      const textDisplayValue = getDisplayValue(key, 'text', textValue);
      const visionDisplayValue = getDisplayValue(key, 'vision', visionValue);

      return (
        <div key={key} className="mb-4 border-b pb-3">
          <label className="block text-gray-700 text-sm font-bold mb-2 capitalize flex items-center justify-between">
            <span>{key.replace(/_/g, ' ')}</span>
            {hasDiff && (
              <div className="flex items-center gap-2">
                <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full font-normal">
                  ⚠ Mismatch
                </span>
                <button
                  onClick={() => dismissDiscrepancy(key)}
                  className="text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 px-2 py-1 rounded whitespace-nowrap"
                >
                  Dismiss
                </button>
              </div>
            )}
          </label>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-500">OCR/Text</span>
                {hasDiff && (
                  <button
                    onClick={() => acceptValue(key, 'text', visionValue)}
                    className="text-xs bg-green-500 hover:bg-green-600 text-white px-2 py-0.5 rounded"
                  >
                    Accept Vision
                  </button>
                )}
              </div>
              <input
                type="text"
                value={textDisplayValue || ''}
                readOnly
                className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight ${
                  textAccepted ? 'bg-green-50 border-green-400 border-2' : hasDiff ? 'bg-gray-50 border-red-400 border-2' : 'bg-gray-50'
                }`}
              />
              {textAccepted && (
                <p className="text-xs text-green-600 mt-1">✓ Accepted from Vision API</p>
              )}
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-500">Vision API</span>
                {hasDiff && (
                  <button
                    onClick={() => acceptValue(key, 'vision', textValue)}
                    className="text-xs bg-green-500 hover:bg-green-600 text-white px-2 py-0.5 rounded"
                  >
                    Accept Text
                  </button>
                )}
              </div>
              <input
                type="text"
                value={visionDisplayValue || ''}
                readOnly
                className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight ${
                  visionAccepted ? 'bg-green-50 border-green-400 border-2' : hasDiff ? 'bg-gray-50 border-red-400 border-2' : 'bg-gray-50'
                }`}
              />
              {visionAccepted && (
                <p className="text-xs text-green-600 mt-1">✓ Accepted from OCR/Text</p>
              )}
            </div>
          </div>
        </div>
      );
    });
  };

  return (
    <div className="p-4 bg-white shadow rounded-lg h-full overflow-auto">
      <h2 className="text-xl font-bold mb-4">Extracted Data</h2>
      
      {visionExtraction && activeDiscrepancies.length > 0 && (
        <div className="mb-4 p-3 bg-red-50 border-l-4 border-red-500 rounded">
          <div className="flex items-center">
            <span className="text-red-700 font-semibold">
              ⚠ {activeDiscrepancies.length} field{activeDiscrepancies.length !== 1 ? 's' : ''} differ between OCR and Vision API
            </span>
          </div>
          <p className="text-xs text-red-600 mt-1">
            Review the highlighted fields below for discrepancies
          </p>
        </div>
      )}

      {visionExtraction && discrepancies.length > 0 && activeDiscrepancies.length === 0 && (
        <div className="mb-4 p-3 bg-blue-50 border-l-4 border-blue-500 rounded">
          <div className="flex items-center">
            <span className="text-blue-700 font-semibold">
              ℹ All mismatches dismissed ({dismissedFields.size} field{dismissedFields.size !== 1 ? 's' : ''})
            </span>
          </div>
        </div>
      )}

      {visionExtraction && discrepancies.length === 0 && (
        <div className="mb-4 p-3 bg-green-50 border-l-4 border-green-500 rounded">
          <div className="flex items-center">
            <span className="text-green-700 font-semibold">
              ✓ All fields match between OCR and Vision API
            </span>
          </div>
        </div>
      )}
      
      {visionExtraction && (
        <div className="flex space-x-2 mb-4 border-b">
          <button
            onClick={() => setActiveTab('text')}
            className={`px-4 py-2 font-medium relative ${activeTab === 'text' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500'}`}
          >
            Text/OCR
            {activeDiscrepancies.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                {activeDiscrepancies.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('vision')}
            className={`px-4 py-2 font-medium relative ${activeTab === 'vision' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500'}`}
          >
            Vision API
            {activeDiscrepancies.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                {activeDiscrepancies.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('comparison')}
            className={`px-4 py-2 font-medium ${activeTab === 'comparison' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500'}`}
          >
            Comparison
          </button>
        </div>
      )}

      <form>
        {!visionExtraction && renderFields(textExtraction, 'text')}
        {visionExtraction && activeTab === 'text' && renderFields(textExtraction, 'text')}
        {visionExtraction && activeTab === 'vision' && renderFields(visionExtraction, 'vision')}
        {visionExtraction && activeTab === 'comparison' && renderComparison()}
      </form>
    </div>
  );
};

export default ExtractionForm;
