import React, { useState, useEffect } from 'react';
import XLSXViewer from './XLSXViewer';

const DocumentPreview = ({ files }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileUrl, setFileUrl] = useState(null);

  useEffect(() => {
    if (files && files.length > 0) {
      setSelectedFile(files[0]);
    }
  }, [files]);

  useEffect(() => {
    if (selectedFile) {
      const url = URL.createObjectURL(selectedFile);
      setFileUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [selectedFile]);

  if (!files || files.length === 0) {
    return <div className="p-4 bg-gray-100 rounded-lg h-full flex items-center justify-center text-gray-500">No documents uploaded</div>;
  }

  return (
    <div className="flex flex-col h-full">
      <div className="mb-4 flex space-x-2 overflow-x-auto p-2 bg-white shadow rounded">
        {files.map((file, index) => (
          <button
            key={index}
            onClick={() => setSelectedFile(file)}
            className={`px-3 py-1 rounded text-sm whitespace-nowrap ${
              selectedFile === file ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {file.name}
          </button>
        ))}
      </div>
      <div className="flex-1 bg-gray-100 border rounded-lg overflow-hidden relative">
        {selectedFile && fileUrl && (
          selectedFile.type === 'application/pdf' ? (
            <iframe src={fileUrl} className="w-full h-full" title="Document Preview" />
          ) : selectedFile.name.endsWith('.xlsx') || selectedFile.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ? (
            <div className="w-full h-full overflow-auto p-4">
              <XLSXViewer file={selectedFile} />
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
              <p>Preview not available for this file type.</p>
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default DocumentPreview;
