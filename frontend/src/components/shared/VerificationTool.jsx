import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import { useBlockchain } from '../../hooks/useBlockchain';
import { useToast } from '../../hooks/useToast';

const styles = {
  container: { maxWidth: '1200px', margin: '0 auto', padding: '20px', fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif' },
  loginBox: { maxWidth: '400px', margin: '0 auto', padding: '40px 0' },
  card: { backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e5e7eb', padding: '20px', marginBottom: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' },
  input: { width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', marginBottom: '12px', outline: 'none' },
  button: { padding: '10px 20px', borderRadius: '6px', border: 'none', fontSize: '14px', fontWeight: '500', cursor: 'pointer' },
  buttonPrimary: { backgroundColor: '#0d9488', color: '#fff' },
  buttonSecondary: { backgroundColor: '#f3f4f6', color: '#374151' },
  badge: { display: 'inline-flex', padding: '2px 8px', borderRadius: '9999px', fontSize: '12px', fontWeight: '500' },
  badgeGreen: { backgroundColor: '#dcfce7', color: '#166534' },
  badgeYellow: { backgroundColor: '#fef3c7', color: '#92400e' },
  alert: { padding: '12px 16px', borderRadius: '6px', marginBottom: '12px' },
  alertRed: { backgroundColor: '#fef2f2', color: '#991b1b' },
  alertGreen: { backgroundColor: '#f0fdf4', color: '#166534' },
  alertYellow: { backgroundColor: '#fefce8', color: '#92400e' },
  label: { display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' },
  pageTitle: { textAlign: 'center', marginBottom: '32px' },
  title: { fontSize: '24px', fontWeight: '700', color: '#111827', marginBottom: '8px' },
  textMuted: { color: '#6b7280', fontSize: '14px' },
  hash: { wordBreak: 'break-all', fontSize: '12px', fontFamily: 'monospace', color: '#6b7280' },
  flexBetween: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
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
          <h1 style={styles.title}>Vote Verification</h1>
          <p style={styles.textMuted}>Enter transaction hash</p>
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
          />
          <button
            style={{ ...styles.button, ...styles.buttonPrimary, width: '100%' }}
            onClick={handleSearch}
            disabled={loading}
            aria-busy={loading}
          >
            {loading ? 'Verifying...' : 'Verify'}
          </button>

          {toasts.map(toast => (
            <div
              key={toast.id}
              style={{
                ...styles.alert,
                ...(toast.type === 'success' ? styles.alertGreen : styles.alertRed),
                marginTop: '12px',
              }}
              role="status"
            >
              {toast.message}
            </div>
          ))}

          <button
            style={{ ...styles.button, background: 'transparent', color: '#6b7280', width: '100%', marginTop: '16px' }}
            onClick={() => onSwitchPage('home')}
          >
            Back
          </button>
        </div>
      </div>
    </div>
  );
}

VerificationTool.propTypes = {
  onSwitchPage: PropTypes.func.isRequired,
};