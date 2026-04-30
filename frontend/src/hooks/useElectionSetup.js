import { useState, useCallback } from 'react';
import { API_URL, validatePosition, validateCandidate } from '../utils/validation';

export function useElectionSetup(token, onUpdate) {
  const [newPosition, setNewPosition] = useState({ title: '', max_votes: 1 });
  const [newCandidate, setNewCandidate] = useState({ 
    candidate_id: '', 
    name: '', 
    party: '', 
    description: '', 
    position_id: '' 
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [localPositions, setLocalPositions] = useState([]);
  const [localCandidates, setLocalCandidates] = useState([]);

  const fetchPositions = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/positions`);
      const data = await res.json();
      setLocalPositions(data);
      return data;
    } catch {
      setError('Failed to fetch positions');
      return [];
    }
  }, []);

  const fetchCandidates = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/candidates`);
      const data = await res.json();
      setLocalCandidates(data);
      return data;
    } catch {
      setError('Failed to fetch candidates');
      return [];
    }
  }, []);

  const addPosition = useCallback(async () => {
    const errors = validatePosition(newPosition);
    if (errors.length > 0) {
      setError(errors.join(', '));
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/api/positions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          title: newPosition.title, 
          max_votes: newPosition.max_votes || 1 
        })
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to add position');
      }

      setNewPosition({ title: '', max_votes: 1 });
      await fetchPositions();
      onUpdate?.();
      return true;
    } catch (err) {
      setError(err.message || 'Failed to add position');
      return false;
    } finally {
      setLoading(false);
    }
  }, [newPosition, onUpdate, fetchPositions]);

  const deletePosition = useCallback(async (id) => {
    setLoading(true);
    try {
      await fetch(`${API_URL}/api/positions/${id}`, { method: 'DELETE' });
      await fetchPositions();
      await fetchCandidates();
      onUpdate?.();
    } catch {
      setError('Failed to delete position');
    } finally {
      setLoading(false);
    }
  }, [onUpdate, fetchPositions, fetchCandidates]);

  const addCandidate = useCallback(async () => {
    const errors = validateCandidate(newCandidate);
    if (errors.length > 0) {
      setError(errors.join(', '));
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      const payload = {
        ...newCandidate,
        position_id: parseInt(newCandidate.position_id, 10)
      };

      const res = await fetch(`${API_URL}/api/candidates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to create candidate');
      }

      setNewCandidate({ candidate_id: '', name: '', party: '', description: '', position_id: '' });
      await fetchCandidates();
      onUpdate?.();
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  }, [newCandidate, onUpdate, fetchCandidates]);

  const getCandidatesByPosition = useCallback((posId) => {
    return (localCandidates || []).filter(c => c.position_id === posId);
  }, [localCandidates]);

  const positionOptions = localPositions.map(p => ({ value: String(p.id), label: p.title }));

  return {
    newPosition,
    newCandidate,
    loading,
    error,
    localPositions,
    localCandidates,
    positionOptions,
    setNewPosition,
    setNewCandidate,
    addPosition,
    deletePosition,
    addCandidate,
    fetchPositions,
    fetchCandidates,
    getCandidatesByPosition,
  };
}