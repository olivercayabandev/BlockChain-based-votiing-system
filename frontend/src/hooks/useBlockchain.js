import { useState, useCallback } from 'react';

export function useBlockchain() {
  const [chainData, setChainData] = useState([]);
  const [pendingTxns, setPendingTxns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchChain = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`/api/blockchain`, { timeout: 10000 });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || `Server error: ${res.status}`);
      }
      const data = await res.json();
      setChainData(data.chain || []);
      setPendingTxns(data.pending_transactions || []);
    } catch (err) {
      if (err.name === 'AbortError' || err.message.includes('timeout')) {
        setError('Request timed out. Please try again.');
      } else {
        setError(err.message || 'Failed to load blockchain');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const verifyTransaction = useCallback(async (hash) => {
    if (!hash) throw new Error('Transaction hash is required');

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`/api/verify/${encodeURIComponent(hash)}`);
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || data.message || 'Transaction not found');
      }
      return await res.json();
    } catch (err) {
      setError(err.message || 'Failed to verify transaction');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    chainData,
    pendingTxns,
    loading,
    error,
    fetchChain,
    verifyTransaction,
  };
}
