import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import { useBlockchain } from '../../hooks/useBlockchain';
import { useToast } from '../../hooks/useToast';

const styles = {
  container: { 
    maxWidth: '1200px', 
    margin: '0 auto', 
    padding: '20px', 
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
    backgroundColor: '#f8fafc',
    minHeight: '100vh'
  },
  loginBox: { 
    maxWidth: '480px', 
    margin: '40px auto', 
    padding: '0'
  },
  card: { 
    backgroundColor: '#fff', 
    borderRadius: '16px', 
    border: '1px solid #e2e8f0', 
    padding: '32px', 
    marginBottom: '16px', 
    boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)' 
  },
  input: { 
    width: '100%', 
    padding: '14px 16px', 
    borderRadius: '10px', 
    border: '2px solid #e2e8f0', 
    fontSize: '14px', 
    marginBottom: '16px', 
    outline: 'none',
    transition: 'border-color 0.2s ease',
    color: '#111827'
  },
  button: { 
    padding: '14px 24px', 
    borderRadius: '10px', 
    border: 'none', 
    fontSize: '15px', 
    fontWeight: '600', 
    cursor: 'pointer',
    transition: 'all 0.2s ease'
  },
  buttonPrimary: { 
    backgroundColor: '#0d9488', 
    color: '#fff',
    width: '100%',
    ':hover': {
      backgroundColor: '#0f766e'
    },
    ':disabled': {
      backgroundColor: '#94a3b8',
      cursor: 'not-allowed'
    }
  },
  buttonSecondary: { 
    backgroundColor: 'transparent', 
    color: '#64748b', 
    width: '100%', 
    marginTop: '16px',
    border: '1px solid #e2e8f0',
    ':hover': {
      backgroundColor: '#f8fafc'
    }
  },
  pageTitle: { 
    textAlign: 'center', 
    marginBottom: '32px' 
  },
  title: { 
    fontSize: '28px', 
    fontWeight: '700', 
    color: '#0f172a', 
    marginBottom: '8px' 
  },
  textMuted: { 
    color: '#64748b', 
    fontSize: '15px' 
  },
  hashIcon: {
    fontSize: '48px',
    marginBottom: '16px',
    display: 'block'
  },
  alert: { 
    padding: '16px', 
    borderRadius: '10px', 
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
  label: { 
    display: 'block', 
    fontSize: '14px', 
    fontWeight: '500', 
    color: '#374151', 
    marginBottom: '6px' 
  },
  flexCenter: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center'
  }
};

export function VerificationTool({ onSwitchPage }) {
  const [searchHash, setSearchHash] = useState('');
  const { loading, verifyTransaction } = useBlockchain();
  const { toasts, success, error: showError } = useToast();

  const handleSearch = useCallback(async () => {
    if (!searchHash.trim()) {
      showError('Please enter a transaction hash');
      return;
    }

    try {
      const result = await verifyTransaction(searchHash.trim());
      if (result.confirmed) {
        success('Vote confirmed! Transaction is in the blockchain.');
      } else {
        showError('Transaction found but not yet confirmed.');
      }
    } catch (err) {
      showError(err.message || 'Transaction not found');
    }
  }, [searchHash, verifyTransaction, success, showError]);

  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  }, [handleSearch]);

  return (
    <div style={styles.container}>
      <div style={styles.loginBox}>
        <div style={styles.pageTitle}>
          <div style={{...styles.flexCenter, marginBottom: '16px'}}>
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="#0d9488"/>
            </svg>
          </div>
          <h1 style={styles.title}>Vote Verification</h1>
          <p style={styles.textMuted}>Enter transaction hash to verify</p>
        </div>
        <div style={styles.card}>
          <label style={styles.label}>Transaction Hash</label>
          <input
            style={styles.input}
            placeholder="Enter transaction hash"
            value={searchHash}
            onChange={(e) => setSearchHash(e.target.value)}
            onKeyPress={handleKeyPress}
            aria-label="Transaction Hash"
            onFocus={(e) => e.target.style.borderColor = '#0d9488'}
            onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
          />
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
        </div>
      </div>
    );
  }

  VerificationTool.propTypes = {
    onSwitchPage: PropTypes.func.isRequired,
  };
