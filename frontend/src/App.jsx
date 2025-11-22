import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ExtractionForm from './components/ExtractionForm';
import DocumentPreview from './components/DocumentPreview';

function App() {
  const [extractedData, setExtractedData] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const handleUploadSuccess = (data, files) => {
    setExtractedData(data);
    setUploadedFiles(files);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-sans text-gray-900">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-blue-900">Shipment Document Processor</h1>
        <p className="text-gray-600">Upload Bill of Lading and Invoice to extract data</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[calc(100vh-200px)]">
        <div className="lg:col-span-1 flex flex-col space-y-8">
          <FileUpload onUploadSuccess={handleUploadSuccess} />
          {extractedData && <ExtractionForm data={extractedData} />}
        </div>
        <div className="lg:col-span-2 h-full">
          <DocumentPreview files={uploadedFiles} />
        </div>
      </div>
    </div>
  );
}

export default App;
