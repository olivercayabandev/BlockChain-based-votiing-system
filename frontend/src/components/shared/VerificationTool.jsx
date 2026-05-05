import React, { useState } from 'react';
import PropTypes from 'prop-types';

const styles = {
  container: { 
    maxWidth: '700px', 
    margin: '0 auto', 
    padding: '20px', 
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
    backgroundColor: '#f8fafc',
    minHeight: '100vh'
  },
  pageTitle: { 
    textAlign: 'center', 
    marginBottom: '32px' 
  },
  title: { 
    fontSize: '28px', 
    fontWeight: '700', 
    color: '#0f172a', 
    marginBottom: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px'
  },
  subtitle: { 
    fontSize: '14px', 
    color: '#64748b' 
  },
  card: { 
    backgroundColor: '#fff', 
    borderRadius: '16px', 
    padding: '32px', 
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    border: '1px solid #e2e8f0'
  },
  inputGroup: { 
    marginBottom: '20px' 
  },
  label: { 
    display: 'block', 
    fontSize: '14px', 
    fontWeight: '600', 
    color: '#374151', 
    marginBottom: '8px' 
  },
  input: { 
    width: '100%', 
    padding: '12px 16px', 
    fontSize: '14px', 
    border: '2px solid #e5e7eb', 
    borderRadius: '8px', 
    outline: 'none', 
    transition: 'border-color 0.2s ease',
    fontFamily: 'monospace',
    color: '#111827'
  },
  button: { 
    width: '100%', 
    padding: '14px', 
    fontSize: '16px', 
    fontWeight: '600', 
    border: 'none', 
    borderRadius: '8px', 
    cursor: 'pointer', 
    transition: 'all 0.2s ease', 
    display: 'flex', 
    alignItems: 'center', 
    justifyContent: 'center', 
    gap: '8px' 
  },
  buttonPrimary: { 
    backgroundColor: '#0d9488', 
    color: '#fff',
    ':hover': { backgroundColor: '#0f766e' }
  },
  resultCard: { 
    marginTop: '24px', 
    padding: '20px', 
    borderRadius: '8px', 
    border: '1px solid' 
  },
  resultTitle: { 
    fontSize: '16px', 
    fontWeight: '600', 
    marginBottom: '12px', 
    display: 'flex', 
    alignItems: 'center', 
    gap: '8px' 
  },
  resultRow: { 
    display: 'flex', 
    justifyContent: 'space-between', 
    padding: '8px 0', 
    borderBottom: '1px solid #f1f5f9',
    fontSize: '14px'
  },
  resultLabel: { 
    color: '#64748b', 
    fontWeight: '500' 
  },
  resultValue: { 
    color: '#0f172a', 
    fontWeight: '600' 
  },
  alert: { 
    padding: '12px 16px', 
    borderRadius: '8px', 
    marginBottom: '16px', 
    border: '1px solid',
    display: 'flex',
    alignItems: 'center',
    gap: '12px'
  },
  alertRed: { 
    backgroundColor: '#fef2f2', 
    color: '#991b1b', 
    borderColor: '#fecaca' 
  },
  alertGreen: { 
    backgroundColor: '#f0fdf4', 
    color: '#166534', 
    borderColor: '#bbf7d0'
  },
  alertYellow: { 
    backgroundColor: '#fefce8', 
    color: '#92400e', 
    borderColor: '#fde68a' 
  },
  icon: {
    fontSize: '32px',
    color: '#0d9488'
  }
};

export function VerificationTool({ onSwitchPage }) {
  const [searchHash, setSearchHash] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toasts, setToasts] = useState([]);

  const showToast = (message, type = 'error') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);
  };

  const handleSearch = async () => {
    if (!searchHash.trim()) {
      showToast('Please enter a transaction hash', 'error');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`/api/verify/${searchHash.trim()}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();

      if (response.ok && data.verified) {
        setResult(data);
        showToast('Transaction verified successfully!', 'success');
      } else {
        showToast(data.message || 'Transaction not found', 'error');
      }
    } catch (error) {
      showToast('Verification failed. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.pageTitle}>
        <h1 style={styles.title}>
          <span style={styles.icon}>🔍</span>
          Verify Transaction
        </h1>
        <p style={styles.subtitle}>Enter a transaction hash to verify its authenticity on the blockchain</p>
      </div>

      <div style={styles.card}>
        <div style={styles.inputGroup}>
          <label htmlFor="searchHash" style={styles.label}>
            Transaction Hash
          </label>
          <input
            id="searchHash"
            type="text"
            style={styles.input}
            placeholder="Enter transaction hash (e.g., a1b2c3d4...)"
            value={searchHash}
            onChange={(e) => setSearchHash(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
        </div>

        <button
          style={{ ...styles.button, ...styles.buttonPrimary }}
          onClick={handleSearch}
          disabled={loading}
          aria-busy={loading}
        >
          {loading ? 'Verifying...' : 'Verify Transaction'}
        </button>

        {toasts.map(toast => (
          <div
            key={toast.id}
            style={{
              ...styles.alert,
              ...(toast.type === 'success' ? styles.alertGreen : styles.alertRed)
            }}
            role="status"
          >
            <span style={{ fontSize: '20px' }}>
              {toast.type === 'success' ? '✓' : '⚠'}
            </span>
            <span>{toast.message}</span>
          </div>
        ))}
      </div>

      {result && (
        <div style={{ ...styles.resultCard, borderColor: '#bbf7d0', backgroundColor: '#f0fdf4' }}>
          <h3 style={{ ...styles.resultTitle, color: '#166534' }}>
            <span>✓</span>
            Transaction Verified
          </h3>
          
          <div style={styles.resultRow}>
            <span style={styles.resultLabel}>Status</span>
            <span style={{ ...styles.resultValue, color: '#166534' }}>Confirmed</span>
          </div>
          
          <div style={styles.resultRow}>
            <span style={styles.resultLabel}>Transaction Hash</span>
            <span style={{ ...styles.resultValue, fontFamily: 'monospace', fontSize: '12px' }}>
              {result.transaction_hash}
            </span>
          </div>
          
          <div style={styles.resultRow}>
            <span style={styles.resultLabel}>Block Index</span>
            <span style={styles.resultValue}>#{result.block_index}</span>
          </div>
          
          <div style={styles.resultRow}>
            <span style={styles.resultLabel}>Block Hash</span>
            <span style={{ ...styles.resultValue, fontFamily: 'monospace', fontSize: '12px' }}>
              {result.block_hash}
            </span>
          </div>
          
          {result.type && (
            <div style={styles.resultRow}>
              <span style={styles.resultLabel}>Type</span>
              <span style={styles.resultValue}>{result.type}</span>
            </div>
          )}
          
          {result.resident_id && (
            <div style={styles.resultRow}>
              <span style={styles.resultLabel}>Voter ID</span>
              <span style={styles.resultValue}>{result.resident_id}</span>
            </div>
          )}
          
          {result.candidate_id && (
            <div style={styles.resultRow}>
              <span style={styles.resultLabel}>Candidate</span>
              <span style={styles.resultValue}>{result.candidate_id}</span>
            </div>
          )}
          
          {result.timestamp && (
            <div style={styles.resultRow}>
              <span style={styles.resultLabel}>Timestamp</span>
              <span style={styles.resultValue}>
                {new Date(result.timestamp * 1000).toLocaleString()}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

VerificationTool.propTypes = {
  onSwitchPage: PropTypes.func.isRequired,
};
