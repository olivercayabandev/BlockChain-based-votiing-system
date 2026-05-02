import { useState, useCallback } from 'react';

export function useAdmin(token) {
  const [voters, setVoters] = useState([]);
  const [stats, setStats] = useState({});
  const [positions, setPositions] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [chainValid, setChainValid] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    if (!token) {
      setError('Not authenticated');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const votersRes = await fetch(`/api/admin/voters?token=${token}`);

      if (!votersRes.ok) {
        throw new Error(`Admin API failed: ${votersRes.status}`);
      }

      const votersData = await votersRes.json();
      const [statsData, chainData, posData, candData] = await Promise.all([
        fetch(`/api/stats`).then(r => r.json()),
        fetch(`/api/blockchain`).then(r => r.json()),
        fetch(`/api/positions`).then(r => r.json()),
        fetch(`/api/candidates`).then(r => r.json())
      ]);

      setVoters(votersData || []);
      setStats(statsData);
      setChainValid(chainData.is_valid);
      setPositions(posData);
      setCandidates(candData);
    } catch (err) {
      setError(err.message || 'Failed to load admin data');
    } finally {
      setLoading(false);
    }
  }, [token]);

  const approveVoter = useCallback(async (residentId, approved) => {
    if (!token) throw new Error('Not authenticated');

    setLoading(true);
    try {
      const res = await fetch(`/api/admin/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resident_id: residentId, approved, token })
      });

      if (!res.ok) {
        throw new Error('Failed to update voter status');
      }

      await fetchData();
    } catch (err) {
      setError(err.message || 'Failed to update voter');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token, fetchData]);

  const resetElection = useCallback(async () => {
    if (!token) throw new Error('Not authenticated');

    setLoading(true);
    try {
      const res = await fetch(`/api/admin/reset-election`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      });

      if (!res.ok) {
        throw new Error('Failed to reset election');
      }

      await fetchData();
    } catch (err) {
      setError(err.message || 'Failed to reset election');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token, fetchData]);

  const deleteVoter = useCallback(async (residentId) => {
    if (!token) throw new Error('Not authenticated');

    setLoading(true);
    try {
      const res = await fetch(`/api/admin/voters/${residentId}/delete?token=${token}`, {
        method: 'POST',
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to delete voter');
      }

      await fetchData();
    } catch (err) {
      setError(err.message || 'Failed to delete voter');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token, fetchData]);

  return {
    voters,
    stats,
    positions,
    candidates,
    chainValid,
    loading,
    error,
    fetchData,
    approveVoter,
    resetElection,
    deleteVoter,
  };
}
