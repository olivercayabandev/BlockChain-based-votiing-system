import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import { useBlockchain } from '../../hooks/useBlockchain';

const styles = {
  container: { 
    maxWidth: '1200px', 
    margin: '0 auto', 
    padding: '20px', 
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
    backgroundColor: '#f8fafc',
    minHeight: '100vh'
  },
  header: { 
    display: 'flex', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    marginBottom: '24px', 
    paddingBottom: '16px', 
    borderBottomWidth: '2px', 
    borderBottomStyle: 'solid', 
    borderBottomColor: '#0d9488'
  },
  title: {
    fontSize: '28px',
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: '4px'
  },
  subtitle: {
    fontSize: '14px',
    color: '#64748b'
  },
  genesisCard: { 
    backgroundColor: '#fff', 
    borderRadius: '12px', 
    border: '2px solid #0d9488',
    padding: '24px', 
    marginBottom: '20px',
    boxShadow: '0 4px 6px -1px rgba(13, 148, 136, 0.1), 0 2px 4px -1px rgba(13, 148, 136, 0.06)'
  },
  blockCard: { 
    backgroundColor: '#fff', 
    borderRadius: '12px', 
    border: '1px solid #e2e8f0', 
    padding: '24px', 
    marginBottom: '16px',
    transition: 'transform 0.2s ease, box-shadow 0.2s ease'
  },
  blockHeader: { 
    display: 'flex', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    marginBottom: '16px',
    paddingBottom: '12px',
    borderBottom: '1px solid #e2e8f0'
  },
  blockNumber: {
    fontSize: '18px',
    fontWeight: '700',
    color: '#0f172a'
  },
  blockTime: { 
    fontSize: '13px', 
    color: '#94a3b8' 
  },
  hashLabel: { 
    fontSize: '11px', 
    fontWeight: '600',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    marginBottom: '4px'
  },
  hash: { 
    wordBreak: 'break-all', 
    fontSize: '12px', 
    fontFamily: 'monospace', 
    color: '#475569',
    backgroundColor: '#f8fafc',
    padding: '8px 12px',
    borderRadius: '6px',
    border: '1px solid #e2e8f0'
  },
  arrow: { 
    display: 'flex', 
    justifyContent: 'center', 
    margin: '-8px 0',
    color: '#0d9488'
  },
  transactionCard: {
    backgroundColor: '#f8fafc',
    borderRadius: '8px',
    padding: '12px',
    marginBottom: '8px',
    border: '1px solid #e2e8f0'
  },
  txLabel: {
    fontSize: '11px',
    fontWeight: '600',
    color: '#94a3b8',
    marginBottom: '2px'
  },
  txValue: {
    fontSize: '13px',
    color: '#475569'
  },
  alert: { 
    padding: '12px 16px', 
    borderRadius: '8px', 
    marginBottom: '16px',
    border: '1px solid'
  },
  alertRed: { 
    backgroundColor: '#fef2f2', 
    color: '#991b1b',
    borderColor: '#fecaca'
  },
  emptyState: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#94a3b8'
  },
  chainValidBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    padding: '6px 12px',
    borderRadius: '9999px',
    fontSize: '13px',
    fontWeight: '500',
    backgroundColor: '#dcfce7',
    color: '#166534'
  }
};

export function BlockchainVisualizer({ onSwitchPage }) {
  const { chainData, loading, error, fetchChain } = useBlockchain();

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
          <h1 style={styles.title}>
            Blockchain Ledger
          </h1>
          <p style={styles.subtitle}>Immutable voting record</p>
        </div>
      </div>

      {error && (
        <div style={{ ...styles.alert, ...styles.alertRed }} role="alert">
          {error}
        </div>
      )}

      <div style={{ maxHeight: '70vh', overflow: 'auto' }}>
        {chainData.length === 0 ? (
          <div style={{ ...styles.genesisCard, textAlign: 'center' }}>
            <p style={styles.subtitle}>No blocks in the blockchain yet.</p>
          </div>
        ) : (
          chainData.map((block, idx) => (
            <React.Fragment key={block.index}>
              <div style={block.index === 0 ? styles.genesisCard : styles.blockCard}>
                <div style={styles.blockHeader}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={styles.blockNumber}>
                      Block #{block.index}
                    </span>
                    {block.index === 0 && (
                      <span style={styles.chainValidBadge}>
                        Genesis
                      </span>
                    )}
                  </div>
                  <span style={styles.blockTime}>
                    {block.timestamp_readable || new Date(block.timestamp * 1000).toLocaleString()}
                  </span>
                </div>
                
                <div style={{ marginBottom: '12px' }}>
                  <p style={styles.hashLabel}>Hash</p>
                  <p style={styles.hash}>{block.hash}</p>
                </div>
                
                {block.previous_hash && block.previous_hash !== '0' && (
                  <div style={{ marginBottom: '12px' }}>
                    <p style={styles.hashLabel}>Previous Hash</p>
                    <p style={styles.hash}>{block.previous_hash}</p>
                  </div>
                )}
                
                <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '12px' }}>
                  <p style={{ fontSize: '14px', color: '#64748b', marginBottom: '8px', fontWeight: '600' }}>
                    Transactions ({block.transactions?.length || 0})
                  </p>
                  {block.transactions?.length > 0 ? (
                    block.transactions.map((tx, i) => (
                      <div
                        key={i}
                        style={styles.transactionCard}
                      >
                        <p style={{ fontSize: '12px', fontWeight: '600', marginBottom: '6px' }}>
                          Tx #{i + 1}: {tx.type}
                        </p>
                        {tx.resident_id && (
                          <p style={styles.txValue}><span style={styles.txLabel}>Voter: </span>{tx.resident_id}</p>
                        )}
                        {tx.candidate_id && (
                          <p style={styles.txValue}><span style={styles.txLabel}>Candidate: </span>{tx.candidate_id}</p>
                        )}
                        {tx.position_id && (
                          <p style={styles.txValue}><span style={styles.txLabel}>Position ID: </span>{tx.position_id}</p>
                        )}
                        {tx.transaction_hash && (
                          <p style={{ fontSize: '10px', wordBreak: 'break-all', color: '#94a3b8', marginTop: '6px' }}>
                            Hash: {tx.transaction_hash}
                          </p>
                        )}
                      </div>
                    ))
                  ) : (
                    <p style={{ fontSize: '12px', color: '#94a3b8' }}>No transactions in this block</p>
                  )}
                </div>
              </div>
              {idx < chainData.length - 1 && (
                <div style={styles.arrow}>
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
