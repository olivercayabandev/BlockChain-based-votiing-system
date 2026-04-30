import { useState, useCallback } from 'react';
import { API_URL } from '../utils/validation';

export function useBlockchain() {
  const [chainData, setChainData] = useState([]);
  const [pendingTxns, setPendingTxns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchChain = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/api/blockchain`);
      if (!res.ok) {
        throw new Error('Failed to fetch blockchain data');
      }
      const data = await res.json();
      setChainData(data.chain || []);
      setPendingTxns(data.pending_transactions || []);
    } catch (err) {
      setError(err.message || 'Failed to load blockchain');
    } finally {
      setLoading(false);
    }
  }, []);

  const verifyTransaction = useCallback(async (hash) => {
    if (!hash) throw new Error('Transaction hash is required');

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/api/verify/${encodeURIComponent(hash)}`);
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
