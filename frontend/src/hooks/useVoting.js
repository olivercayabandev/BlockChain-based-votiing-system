import { useState, useCallback } from 'react';

async function safeJson(response) {
  try {
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    return { detail: `Unexpected response: ${response.status}` };
  } catch {
    return { detail: 'Invalid server response' };
  }
}

export function useVoting(token, residentId) {
  const [positions, setPositions] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [gasBalance, setGasBalance] = useState(0);
  const [votedPositions, setVotedPositions] = useState([]);
  const [voteDetails, setVoteDetails] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const [posRes, candRes, gasRes, votedRes, statusRes] = await Promise.all([
        fetch(`/api/positions`),
        fetch(`/api/candidates`),
        fetch(`/api/gas/${residentId}?token=${token}`),
        fetch(`/api/voted-positions/${residentId}?token=${token}`),
        fetch(`/api/vote-status/${residentId}?token=${token}`)
      ]);

      const gasData = await safeJson(gasRes);
      const votedData = await safeJson(votedRes);
      const statusData = await safeJson(statusRes);

      if (!gasRes.ok) {
        throw new Error(gasData.detail || 'Failed to fetch voter data');
      }

      if (!votedRes.ok) {
        throw new Error(votedData.detail || 'Failed to fetch voting status');
      }

      const posData = await posRes.json();
      const candData = await candRes.json();

      setPositions(Array.isArray(posData) ? posData : []);
      setCandidates(Array.isArray(candData) ? candData : []);
      setGasBalance(gasData.gas_balance ?? 0);
      setVotedPositions(votedData.voted_position_ids || []);
      setVoteDetails(statusData.votes || []);
    } catch (err) {
      setError(err.message || 'Failed to load voting data');
    } finally {
      setLoading(false);
    }
  }, [token, residentId]);

  const vote = useCallback(async (candidateId, positionId) => {
    if (!token) throw new Error('Not authenticated');
    
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch(`/api/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resident_id: residentId,
          candidate_id: candidateId,
          position_id: positionId,
          token
        })
      });

      const data = await safeJson(res);
      
      if (!res.ok) {
        throw new Error(data.detail || data.message || 'Vote failed');
      }

      await fetchData();
      return data;
    } catch (err) {
      const errorMsg = err.message || 'Failed to cast vote';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [token, residentId, fetchData]);

  const getCandidatesByPosition = useCallback((posId) => {
    return candidates.filter(c => c.position_id === posId);
  }, [candidates]);

  const getPositionName = useCallback((posId) => {
    return positions.find(p => p.id === posId)?.title || 'Unknown';
  }, [positions]);

  return {
    positions,
    candidates,
    gasBalance,
    votedPositions,
    voteDetails,
    loading,
    error,
    fetchData,
    vote,
    getCandidatesByPosition,
    getPositionName,
  };
}
