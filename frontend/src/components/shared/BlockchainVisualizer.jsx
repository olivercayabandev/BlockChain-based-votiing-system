import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import { useBlockchain } from '../../hooks/useBlockchain';

const styles = {
  container: { maxWidth: '1200px', margin: '0 auto', padding: '20px', fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', paddingBottom: '16px', borderBottomWidth: '1px', borderBottomStyle: 'solid', borderBottomColor: '#e5e7eb' },
  button: { padding: '10px 20px', borderRadius: '6px', border: 'none', fontSize: '14px', fontWeight: '500', cursor: 'pointer' },
  buttonSecondary: { backgroundColor: '#f3f4f6', color: '#374151' },
  blockCard: { backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e5e7eb', padding: '20px', marginBottom: '16px' },
  hash: { wordBreak: 'break-all', fontSize: '12px', fontFamily: 'monospace', color: '#6b7280' },
  alert: { padding: '12px 16px', borderRadius: '6px', marginBottom: '12px' },
  alertRed: { backgroundColor: '#fef2f2', color: '#991b1b' },
  badge: { display: 'inline-flex', padding: '2px 8px', borderRadius: '9999px', fontSize: '12px', fontWeight: '500' },
  badgeTeal: { backgroundColor: '#ccfbf1', color: '#0f766e' },
  flexBetween: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  textMuted: { color: '#6b7280', fontSize: '14px' },
};

export function BlockchainVisualizer({ onSwitchPage }) {
  const { chainData, pendingTxns, loading, error, fetchChain } = useBlockchain();

  useEffect(() => {
    fetchChain();
  }, [fetchChain]);

  if (loading && chainData.length === 0) {
    return (
      <div style={{ ...styles.container, textAlign: 'center', paddingTop: '100px' }}>
        Loading blockchain data...
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '4px' }}>
            Blockchain Ledger
          </h1>
          <p style={styles.textMuted}>Immutable voting record</p>
        </div>
        <button
          style={{ ...styles.button, ...styles.buttonSecondary }}
          onClick={() => onSwitchPage('home')}
          aria-label="Go back"
        >
          Back
        </button>
      </div>

      {error && (
        <div style={{ ...styles.alert, ...styles.alertRed }} role="alert">
          {error}
        </div>
      )}

      {pendingTxns.length > 0 && (
        <div style={{ ...styles.blockCard, borderColor: '#fbbf24', marginBottom: '24px' }}>
          <div style={{ ...styles.flexBetween, marginBottom: '12px' }}>
            <span style={{ ...styles.badge, backgroundColor: '#fef3c7', color: '#92400e', fontSize: '14px' }}>
              Pending Transactions ({pendingTxns.length})
            </span>
          </div>
          {pendingTxns.map((tx, i) => (
            <div
              key={i}
              style={{ ...styles.alert, backgroundColor: '#fef3c7', marginBottom: '4px' }}
            >
              <p style={{ fontSize: '12px', fontWeight: '600' }}>
                Pending Tx #{i + 1}: {tx.type}
              </p>
              {tx.resident_id && (
                <p style={{ fontSize: '12px' }}>Voter: {tx.resident_id}</p>
              )}
              {tx.candidate_id && (
                <p style={{ fontSize: '12px' }}>Candidate: {tx.candidate_id}</p>
              )}
              {tx.position_id && (
                <p style={{ fontSize: '12px' }}>Position ID: {tx.position_id}</p>
              )}
              {tx.timestamp && (
                <p style={{ fontSize: '12px', color: '#6b7280' }}>
                  Time: {new Date(tx.timestamp * 1000).toLocaleString()}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      <div style={{ maxHeight: '70vh', overflow: 'auto' }}>
        {chainData.length === 0 ? (
          <div style={{ ...styles.blockCard, textAlign: 'center' }}>
            <p style={styles.textMuted}>No blocks in the blockchain yet.</p>
          </div>
        ) : (
          chainData.map((block, idx) => (
            <React.Fragment key={block.index}>
              <div style={styles.blockCard}>
                <div style={{ ...styles.flexBetween, marginBottom: '12px' }}>
                  <span style={{ ...styles.badge, ...styles.badgeTeal, fontSize: '14px' }}>
                    Block #{block.index}
                  </span>
                  <span style={{ fontSize: '12px', color: '#9ca3af' }}>
                    {block.timestamp_readable || new Date(block.timestamp * 1000).toLocaleString()}
                  </span>
                </div>
                <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '12px' }}>
                  <p style={{ fontSize: '12px', color: '#6b7280' }}>Hash</p>
                  <p style={styles.hash}>{block.hash}</p>
                </div>
                {block.previous_hash && (
                  <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '12px' }}>
                    <p style={{ fontSize: '12px', color: '#6b7280' }}>Previous Hash</p>
                    <p style={styles.hash}>{block.previous_hash}</p>
                  </div>
                )}
                <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '12px' }}>
                  <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
                    Transactions ({block.transactions?.length || 0})
                  </p>
                  {block.transactions?.length > 0 ? (
                    block.transactions.map((tx, i) => (
                      <div
                        key={i}
                        style={{ ...styles.alert, backgroundColor: '#f3f4f6', marginBottom: '4px' }}
                      >
                        <p style={{ fontSize: '12px', fontWeight: '600' }}>
                          Tx #{i + 1}: {tx.type}
                        </p>
                        {tx.resident_id && (
                          <p style={{ fontSize: '12px' }}>Voter: {tx.resident_id}</p>
                        )}
                        {tx.candidate_id && (
                          <p style={{ fontSize: '12px' }}>Candidate: {tx.candidate_id}</p>
                        )}
                        {tx.position_id && (
                          <p style={{ fontSize: '12px' }}>Position ID: {tx.position_id}</p>
                        )}
                        {tx.transaction_hash && (
                          <p style={{ fontSize: '10px', wordBreak: 'break-all', color: '#6b7280' }}>
                            Hash: {tx.transaction_hash}
                          </p>
                        )}
                      </div>
                    ))
                  ) : (
                    <p style={{ fontSize: '12px', color: '#6b7280' }}>No transactions in this block</p>
                  )}
                </div>
              </div>
              {idx < chainData.length - 1 && (
                <div style={{ display: 'flex', justifyContent: 'center', margin: '-10px 0' }}>
                  <div style={{
                    width: 0,
                    height: 0,
                    borderLeft: '15px solid transparent',
                    borderRight: '15px solid transparent',
                    borderTop: '15px solid #0d9488'
                  }} />
                </div>
              )}
            </React.Fragment>
          ))
        )}
      </div>
    </div>
  );
}

BlockchainVisualizer.propTypes = {
  onSwitchPage: PropTypes.func.isRequired,
};