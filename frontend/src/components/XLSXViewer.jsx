import React, { useEffect, useState } from 'react';
import * as XLSX from 'xlsx';

/**
 * XLSXViewer renders a preview of an uploaded .xlsx file.
 * It parses the first worksheet into JSON rows and displays them in a simple table.
 * Props:
 *   file: File object representing the uploaded .xlsx document.
 */
const XLSXViewer = ({ file }) => {
  const [columns, setColumns] = useState([]);
  const [rows, setRows] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = e.target.result;
        // Read workbook as binary string
        const workbook = XLSX.read(data, { type: 'binary' });
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
        if (jsonData.length === 0) {
          setError('Empty sheet');
          return;
        }
        const [header, ...body] = jsonData;
        setColumns(header);
        setRows(body);
      } catch (err) {
        console.error(err);
        setError('Failed to parse XLSX file');
      }
    };
    // Read as binary string for SheetJS
    reader.readAsBinaryString(file);
  }, [file]);

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  if (rows.length === 0) {
    return <p className="text-gray-500">Loading preview...</p>;
  }

  return (
    <div className="overflow-auto border rounded">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((col, idx) => (
              <th
                key={idx}
                className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {rows.map((row, rowIdx) => (
            <tr key={rowIdx}>
              {row.map((cell, cellIdx) => (
                <td key={cellIdx} className="px-3 py-2 text-sm text-gray-700">
                  {cell?.toString()}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default XLSXViewer;
