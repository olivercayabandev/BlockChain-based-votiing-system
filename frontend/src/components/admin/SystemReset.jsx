import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';

const API_URL = import.meta.env.VITE_API_URL || '';

export function SystemReset({ token }) {
  const [confirmText, setConfirmText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const isConfirmed = confirmText === 'CONFIRM RESET';

  const handleReset = useCallback(async () => {
    if (!isConfirmed) return;
    
    if (!window.confirm('Are you absolutely sure?\n\nThis will:\n- Wipe the entire ledger\n- Reset ALL voter gas balances\n- Clear ALL vote records\n\nThis action CANNOT be undone!')) {
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/admin/hard-reset?token=${encodeURIComponent(token)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Reset failed');
      }

      setResult(data);
      setConfirmText('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [token, isConfirmed]);

  return (
    <div style={{ backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '24px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}>
      <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#1e40af', marginBottom: '16px', paddingBottom: '8px', borderBottom: '1px solid #e2e8f0' }}>
        System Hard Reset
      </h3>

      {/* Warning Box */}
      <div style={{ backgroundColor: '#fef2f2', border: '2px solid #dc2626', borderRadius: '8px', padding: '16px', marginBottom: '20px' }}>
        <h4 style={{ color: '#dc2626', fontSize: '16px', fontWeight: '700', margin: '0 0 8px 0' }}>
          WARNING: DESTRUCTIVE ACTION
        </h4>
        <p style={{ color: '#991b1b', fontSize: '14px', margin: '0 0 8px 0', lineHeight: '1.5' }}>
          This will <strong>permanently wipe</strong> the following:
        </p>
        <ul style={{ color: '#991b1b', fontSize: '14px', margin: '0', paddingLeft: '20px', lineHeight: '1.8' }}>
          <li>Entire blockchain ledger (all blocks deleted)</li>
          <li>All vote records from database</li>
          <li>Reset ALL voter gas balances to default (1.0)</li>
          <li>Recreate genesis block</li>
        </ul>
      </div>

      {/* Confirmation Input */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
          Type <strong>CONFIRM RESET</strong> to enable the reset button:
        </label>
        <input
          type="text"
          value={confirmText}
          onChange={(e) => setConfirmText(e.target.value)}
          placeholder="CONFIRM RESET"
          style={{
            width: '100%',
            padding: '10px 14px',
            border: `2px solid ${isConfirmed ? '#16a34a' : '#e2e8f0'}`,
            borderRadius: '8px',
            fontSize: '14px',
            backgroundColor: isConfirmed ? '#f0fdf4' : '#fff',
            outline: 'none',
            transition: 'all 0.2s'
          }}
          aria-label="Type CONFIRM RESET to proceed"
        />
      </div>

      {/* Reset Button */}
      <button
        onClick={handleReset}
        disabled={!isConfirmed || loading}
        style={{
          padding: '12px 24px',
          borderRadius: '8px',
          border: 'none',
          fontSize: '14px',
          fontWeight: '600',
          cursor: isConfirmed && !loading ? 'pointer' : 'not-allowed',
          backgroundColor: isConfirmed ? '#dc2626' : '#9ca3af',
          color: '#fff',
          transition: 'all 0.2s',
          opacity: loading ? 0.7 : 1
        }}
        aria-label="Execute hard reset"
      >
        {loading ? 'Resetting...' : 'Execute Hard Reset'}
      </button>

      {/* Success Message */}
      {result && (
        <div style={{ backgroundColor: '#dcfce7', color: '#166534', padding: '14px 18px', borderRadius: '8px', marginTop: '16px', fontSize: '14px' }}>
          <strong>Reset Complete!</strong>
          <p style={{ margin: '8px 0 0 0' }}>{result.message}</p>
          <div style={{ marginTop: '12px', fontSize: '13px' }}>
            <p>Ledger blocks: {result.ledger_blocks}</p>
            <p>Votes cleared: {result.votes_cleared ? 'Yes' : 'No'}</p>
            <p>Gas reset: {result.gas_reset ? 'Yes' : 'No'}</p>
            <p>Reset time: {new Date(result.reset_time).toLocaleString()}</p>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div style={{ backgroundColor: '#fee2e2', color: '#991b1b', padding: '14px 18px', borderRadius: '8px', marginTop: '16px', fontSize: '14px' }}>
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
}

SystemReset.propTypes = {
  token: PropTypes.string.isRequired,
};
