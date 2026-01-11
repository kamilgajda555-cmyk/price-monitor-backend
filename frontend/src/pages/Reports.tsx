import React, { useState } from 'react';
import { reportsAPI } from '../services/api';

const Reports: React.FC = () => {
  const [reportType, setReportType] = useState('products');
  const [format, setFormat] = useState('excel');
  const [loading, setLoading] = useState(false);

  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const response = await reportsAPI.generate({
        report_type: reportType,
        format: format,
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const extension = format === 'excel' ? 'xlsx' : format;
      link.setAttribute('download', `${reportType}_report_${new Date().toISOString().split('T')[0]}.${extension}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Error generating report. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Reports</h1>
        <p className="page-subtitle">Generate and download various reports</p>
      </div>

      <div className="card">
        <h2 className="card-title" style={{ marginBottom: '20px' }}>Generate Report</h2>
        
        <div className="form-group">
          <label className="form-label">Report Type</label>
          <select
            className="form-control"
            value={reportType}
            onChange={(e) => setReportType(e.target.value)}
          >
            <option value="products">Products Report</option>
            <option value="price_changes">Price Changes Report</option>
            <option value="sources">Sources Report</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Format</label>
          <select
            className="form-control"
            value={format}
            onChange={(e) => setFormat(e.target.value)}
          >
            <option value="excel">Excel (.xlsx)</option>
            <option value="csv">CSV (.csv)</option>
            <option value="pdf">PDF (.pdf)</option>
          </select>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleGenerateReport}
          disabled={loading}
          style={{ marginTop: '20px' }}
        >
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
      </div>

      <div className="card" style={{ marginTop: '30px' }}>
        <h2 className="card-title" style={{ marginBottom: '15px' }}>Available Reports</h2>
        
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '18px', marginBottom: '10px' }}>📊 Products Report</h3>
          <p style={{ color: '#666', marginBottom: '10px' }}>
            Complete list of all products with their details, SKU, EAN, categories, and current prices.
          </p>
          <ul style={{ color: '#666', marginLeft: '20px' }}>
            <li>Product name, SKU, EAN</li>
            <li>Category and brand information</li>
            <li>Base price and current prices</li>
            <li>Active/inactive status</li>
          </ul>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '18px', marginBottom: '10px' }}>📈 Price Changes Report</h3>
          <p style={{ color: '#666', marginBottom: '10px' }}>
            Historical price changes across all products and sources.
          </p>
          <ul style={{ color: '#666', marginLeft: '20px' }}>
            <li>Product and source information</li>
            <li>Price history with timestamps</li>
            <li>Availability status</li>
            <li>Customizable date range</li>
          </ul>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '18px', marginBottom: '10px' }}>🔗 Sources Report</h3>
          <p style={{ color: '#666', marginBottom: '10px' }}>
            Overview of all configured price monitoring sources.
          </p>
          <ul style={{ color: '#666', marginLeft: '20px' }}>
            <li>Source name and type</li>
            <li>Base URL and configuration</li>
            <li>Number of monitored products</li>
            <li>Active/inactive status</li>
          </ul>
        </div>
      </div>

      <div className="card" style={{ marginTop: '30px' }}>
        <h2 className="card-title" style={{ marginBottom: '15px' }}>ℹ️ Report Information</h2>
        <ul style={{ color: '#666', marginLeft: '20px' }}>
          <li><strong>Excel Format:</strong> Best for data analysis, filtering, and pivot tables</li>
          <li><strong>CSV Format:</strong> Compatible with most spreadsheet applications and databases</li>
          <li><strong>PDF Format:</strong> Professional format for sharing and printing</li>
        </ul>
        <p style={{ color: '#666', marginTop: '15px' }}>
          Reports are generated in real-time based on current data in the system.
        </p>
      </div>
    </div>
  );
};

export default Reports;
