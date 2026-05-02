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

export function useAdminVerification(token) {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchQueue = useCallback(async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch(`/api/admin/verification-queue?token=${token}`);
      const data = await safeJson(res);
      
      if (!res.ok) {
        throw new Error(data.detail || `Failed to fetch queue: ${res.status}`);
      }
      
      setQueue(Array.isArray(data) ? data : []);
      return data;
    } catch (err) {
      const msg = err.message || 'Failed to fetch queue';
      setError(msg);
      return [];
    } finally {
      setLoading(false);
    }
  }, [token]);

  const verifyVoter = useCallback(async (residentId, action, reason, notes) => {
    if (!token) throw new Error('Not authenticated');
    
    setLoading(true);
    
    try {
      const res = await fetch(`/api/admin/verify-voter/${residentId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, reason, notes, token })
      });
      
      const data = await safeJson(res);
      
      if (!res.ok) {
        throw new Error(data.detail || data.message || 'Verification failed');
      }
      
      await fetchQueue();
      return data;
    } catch (err) {
      const msg = err.message || 'Verification failed';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  }, [token, fetchQueue]);

  const approveVoter = useCallback(async (residentId) => {
    return verifyVoter(residentId, 'approve', null, null);
  }, [verifyVoter]);

  const rejectVoter = useCallback(async (residentId, reason, notes) => {
    return verifyVoter(residentId, 'reject', reason, notes);
  }, [verifyVoter]);

  const approveAllPending = useCallback(async () => {
    if (!token) throw new Error('Not authenticated');
    
    setLoading(true);
    
    try {
      const res = await fetch(`/api/admin/approve-all-pending?token=${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm: true })
      });
      
      const data = await safeJson(res);
      
      if (!res.ok) {
        throw new Error(data.detail || data.message || 'Failed to approve all');
      }
      
      await fetchQueue();
      return data;
    } catch (err) {
      const msg = err.message || 'Failed to approve all';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  }, [token, fetchQueue]);

  const importVoters = useCallback(async (votersData) => {
    if (!token) throw new Error('Not authenticated');
    
    setLoading(true);
    
    try {
      const res = await fetch(`/api/admin/import-voters-batch?token=${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voters: votersData })
      });
      
      const data = await safeJson(res);
      
      if (!res.ok) {
        throw new Error(data.detail || data.message || 'Import failed');
      }
      
      await fetchQueue();
      return data;
    } catch (err) {
      const msg = err.message || 'Import failed';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  }, [token, fetchQueue]);

  return {
    queue,
    loading,
    error,
    fetchQueue,
    verifyVoter,
    approveVoter,
    rejectVoter,
    approveAllPending,
    importVoters,
  };
}