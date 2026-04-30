import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import { API_URL } from '../../utils/validation';

const ID_TYPES = ['resident_id', 'national_id', 'student_id', 'passport', 'drivers_license', 'senior_citizen', 'pwd', 'barangay_id'];

const SAMPLE_CSV = `resident_id,name,id_type,id_number
2026-0002,Juan dela Cruz,resident_id,2026-0002
2026-0003,Maria Santos,student_id,2023-12345
2026-0004,Pedro Garcia,philsys,123456789012
2026-0005,Ana Reyes,drivers_license,A1234567
2026-0006,Lisa Cruz,passport,P87654321`;

export function BulkImport({ token, onImportComplete }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleFileChange = useCallback((e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    if (!selectedFile.name.endsWith('.csv')) {
      setError('Please upload a CSV file');
      return;
    }

    setFile(selectedFile);
    setError('');
    setSuccess('');

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const text = event.target.result;
        const lines = text.split('\n').filter(line => line.trim());
        
        if (lines.length < 2) {
          setError('CSV file is empty or invalid');
          return;
        }

        const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
        const requiredHeaders = ['resident_id', 'name', 'id_type', 'id_number'];
        const missingHeaders = requiredHeaders.filter(h => !headers.includes(h));
        
        if (missingHeaders.length > 0) {
          setError(`Missing required columns: ${missingHeaders.join(', ')}`);
          return;
        }

        const data = lines.slice(1).map((line, index) => {
          const values = line.split(',').map(v => v.trim());
          const row = {};
          headers.forEach((header, i) => {
            row[header] = values[i] || '';
          });
          row._line = index + 2;
          return row;
        }).filter(row => row.resident_id && row.name);

        setPreview(data.slice(0, 10));
        setError('');
      } catch (err) {
        setError('Failed to parse CSV file');
      }
    };
    reader.readAsText(selectedFile);
  }, []);

  const handleImport = useCallback(async () => {
    if (!file) return;

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const reader = new FileReader();
      reader.onload = async (event) => {
        try {
          const text = event.target.result;
          const lines = text.split('\n').filter(line => line.trim());
          const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
          
          const voters = lines.slice(1).map(line => {
            const values = line.split(',').map(v => v.trim());
            const row = {};
            headers.forEach((header, i) => {
              row[header] = values[i] || '';
            });
            return row;
          }).filter(row => row.resident_id && row.name);

          const res = await fetch(`${API_URL}/api/admin/import-voters-batch?token=${token}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ voters })
          });

          const data = await res.json();
          
          if (!res.ok) {
            throw new Error(data.detail || data.message || 'Import failed');
          }

          setSuccess(`Successfully imported ${data.imported || voters.length} voters`);
          setFile(null);
          setPreview([]);
          onImportComplete?.();
        } catch (err) {
          setError(err.message);
        } finally {
          setLoading(false);
        }
      };
      reader.readAsText(file);
    } catch (err) {
      setError('Failed to read file');
      setLoading(false);
    }
  }, [file, token, onImportComplete]);

  const downloadSample = useCallback(() => {
    const blob = new Blob([SAMPLE_CSV], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_voters.csv';
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  const styles = {
    container: { marginBottom: '16px' },
    dropzone: { 
      border: '2px dashed #d1d5db', 
      borderRadius: '8px', 
      padding: '24px', 
      textAlign: 'center',
      cursor: 'pointer',
      transition: 'all 0.2s',
    },
    dropzoneActive: { borderColor: '#0d9488', backgroundColor: '#f0fdfa' },
    input: { display: 'none' },
    button: { padding: '10px 20px', borderRadius: '6px', border: 'none', fontSize: '14px', fontWeight: '500', cursor: 'pointer' },
    buttonPrimary: { backgroundColor: '#0d9488', color: '#fff' },
    buttonSecondary: { backgroundColor: '#f3f4f6', color: '#374151' },
    alert: { padding: '12px 16px', borderRadius: '6px', marginBottom: '12px', fontSize: '14px' },
    alertRed: { backgroundColor: '#fef2f2', color: '#991b1b' },
    alertGreen: { backgroundColor: '#dcfce7', color: '#166534' },
    previewTable: { width: '100%', borderCollapse: 'collapse', marginTop: '16px', fontSize: '13px' },
    th: { textAlign: 'left', padding: '8px', borderBottom: '2px solid #e5e7eb', backgroundColor: '#f9fafb' },
    td: { padding: '8px', borderBottom: '1px solid #e5e7eb' },
    infoBox: { backgroundColor: '#eff6ff', border: '1px solid #dbeafe', borderRadius: '6px', padding: '12px', marginBottom: '16px', fontSize: '13px', color: '#1e40af' },
  };

  return (
    <div style={styles.container}>
      <div style={styles.infoBox}>
        <strong>CSV Format:</strong> resident_id, name, id_type, id_number<br/>
        <strong>ID Types:</strong> {ID_TYPES.join(', ')}<br/>
        <strong>Note:</strong> Imported voters will be automatically approved (pre-verified)
      </div>

      <div style={styles.dropzone} onClick={() => document.getElementById('csv-input').click()}>
        <input
          id="csv-input"
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          style={styles.input}
        />
        <p style={{ margin: '0 0 8px 0', color: '#374151' }}>
          {file ? file.name : 'Click or drag CSV file here'}
        </p>
        <p style={{ margin: 0, fontSize: '12px', color: '#6b7280' }}>
          Required columns: resident_id, name, id_type, id_number
        </p>
      </div>

      <div style={{ marginTop: '12px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        <button
          style={{ ...styles.button, ...styles.buttonSecondary, backgroundColor: '#e0f2fe', color: '#0369a1' }}
          onClick={downloadSample}
        >
          Download Sample CSV
        </button>
      </div>

      {error && <div style={{ ...styles.alert, ...styles.alertRed }}>{error}</div>}
      {success && <div style={{ ...styles.alert, ...styles.alertGreen }}>{success}</div>}

      {preview.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <p style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
            Preview ({preview.length} shown of file):
          </p>
          <div style={{ overflowX: 'auto' }}>
            <table style={styles.previewTable}>
              <thead>
                <tr>
                  <th style={styles.th}>Line</th>
                  <th style={styles.th}>Resident ID</th>
                  <th style={styles.th}>Name</th>
                  <th style={styles.th}>ID Type</th>
                  <th style={styles.th}>ID Number</th>
                </tr>
              </thead>
              <tbody>
                {preview.map((row, i) => (
                  <tr key={i}>
                    <td style={styles.td}>{row._line}</td>
                    <td style={styles.td}>{row.resident_id}</td>
                    <td style={styles.td}>{row.name}</td>
                    <td style={styles.td}>{row.id_type}</td>
                    <td style={styles.td}>{row.id_number}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div style={{ display: 'flex', gap: '8px', marginTop: '16px', flexWrap: 'wrap' }}>
            <button
              style={{ ...styles.button, ...styles.buttonPrimary }}
              onClick={handleImport}
              disabled={loading}
            >
              {loading ? 'Importing...' : 'Import All Voters'}
            </button>
            <button
              style={{ ...styles.button, ...styles.buttonSecondary }}
              onClick={() => { setFile(null); setPreview([]); }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

BulkImport.propTypes = {
  token: PropTypes.string,
  onImportComplete: PropTypes.func,
};

BulkImport.defaultProps = {
  token: '',
  onImportComplete: null,
};