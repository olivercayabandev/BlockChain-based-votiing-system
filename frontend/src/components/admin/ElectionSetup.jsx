import React, { useCallback, useMemo, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useElectionSetup } from '../../hooks/useElectionSetup';
import { useToast } from '../../hooks/useToast';

const styles = {
  card: { backgroundColor: '#fff', borderRadius: '8px', borderWidth: '1px', borderStyle: 'solid', borderColor: '#e5e7eb', paddingTop: '20px', paddingBottom: '20px', paddingLeft: '20px', paddingRight: '20px', marginBottom: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' },
  input: { width: '100%', paddingTop: '10px', paddingBottom: '10px', paddingLeft: '12px', paddingRight: '12px', borderRadius: '6px', borderWidth: '1px', borderStyle: 'solid', borderColor: '#d1d5db', fontSize: '14px', marginBottom: '12px', outline: 'none' },
  button: { paddingTop: '10px', paddingBottom: '10px', paddingLeft: '20px', paddingRight: '20px', borderRadius: '6px', border: 'none', fontSize: '14px', fontWeight: '500', cursor: 'pointer' },
  buttonPrimary: { backgroundColor: '#0d9488', color: '#fff' },
  badge: { display: 'inline-flex', paddingTop: '2px', paddingBottom: '2px', paddingLeft: '8px', paddingRight: '8px', borderRadius: '9999px', fontSize: '12px', fontWeight: '500' },
  badgeTeal: { backgroundColor: '#ccfbf1', color: '#0f766e' },
  label: { display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' },
  textMuted: { color: '#6b7280', fontSize: '14px' },
  select: { width: '100%', paddingTop: '10px', paddingBottom: '10px', paddingLeft: '12px', paddingRight: '12px', borderRadius: '6px', borderWidth: '1px', borderStyle: 'solid', borderColor: '#d1d5db', fontSize: '14px', marginBottom: '12px', backgroundColor: '#fff' },
  alert: { paddingTop: '12px', paddingBottom: '12px', paddingLeft: '16px', paddingRight: '16px', borderRadius: '6px', marginBottom: '12px' },
  alertRed: { backgroundColor: '#fef2f2', color: '#991b1b' },
  alertGreen: { backgroundColor: '#f0fdf4', color: '#166534' },
};

export function ElectionSetup({ onUpdate }) {
  const { toasts, removeToast, success, error: showError } = useToast();
  const {
    newPosition,
    newCandidate,
    loading,
    error,
    localPositions,
    localCandidates,
    setNewPosition,
    setNewCandidate,
    addPosition,
    deletePosition,
    addCandidate,
    fetchPositions,
    fetchCandidates,
    getCandidatesByPosition,
  } = useElectionSetup(null, onUpdate);

  useEffect(() => {
    fetchPositions();
    fetchCandidates();
  }, [fetchPositions, fetchCandidates]);

  useEffect(() => {
    if (error) {
      showError(error);
    }
  }, [error, showError]);

  const handleAddPosition = useCallback(async () => {
    const result = await addPosition();
    if (result) {
      success('Position added successfully');
    }
  }, [addPosition, success]);

  const handleDeletePosition = useCallback(async (id) => {
    if (!window.confirm('Are you sure you want to delete this position? This will also delete all candidates under it.')) {
      return;
    }
    await deletePosition(id);
    success('Position deleted');
  }, [deletePosition, success]);

  const handleAddCandidate = useCallback(async () => {
    const result = await addCandidate();
    if (result) {
      success('Candidate added successfully');
    }
  }, [addCandidate, success]);

  const canAddCandidate = useMemo(() => {
    return newCandidate.candidate_id && newCandidate.name && newCandidate.position_id;
  }, [newCandidate]);

  return (
    <div>
      {toasts.map(toast => (
        <div
          key={toast.id}
          style={{
            ...styles.alert,
            ...(toast.type === 'success' ? styles.alertGreen : styles.alertRed),
            position: 'fixed',
            top: '20px',
            right: '20px',
            zIndex: 2000,
            cursor: 'pointer',
          }}
          onClick={() => removeToast(toast.id)}
          role="status"
        >
          {toast.message}
        </div>
      ))}

      <div style={styles.card}>
        <h3 style={{ marginBottom: '16px' }}>Add Position</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '12px', alignItems: 'end' }}>
          <div>
            <label style={styles.label}>Position Title</label>
            <input
              style={styles.input}
              placeholder="e.g., President"
              value={newPosition.title}
              onChange={(e) => setNewPosition(prev => ({ ...prev, title: e.target.value }))}
              aria-label="Position Title"
            />
          </div>
          <div>
            <label style={styles.label}>Max Votes</label>
            <input
              type="number"
              style={styles.input}
              value={newPosition.max_votes}
              onChange={(e) => setNewPosition(prev => ({ ...prev, max_votes: parseInt(e.target.value, 10) || 1 }))}
              min="1"
              aria-label="Max Votes"
            />
          </div>
          <button
            style={{ ...styles.button, ...styles.buttonPrimary }}
            onClick={handleAddPosition}
            disabled={loading || !newPosition.title.trim()}
            aria-busy={loading}
          >
            Add
          </button>
        </div>
      </div>

      <div style={styles.card}>
        <h3 style={{ marginBottom: '16px' }}>Positions ({localPositions.length})</h3>
        {localPositions.length === 0 ? (
          <p style={styles.textMuted}>No positions yet. Add one above.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {localPositions.map(p => (
              <div
                key={p.id}
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '12px', paddingBottom: '12px', paddingLeft: '12px', paddingRight: '12px', backgroundColor: '#f9fafb', borderRadius: '6px' }}
              >
                <div>
                  <strong>{p.title}</strong>
                  <span style={{ marginLeft: '8px', ...styles.textMuted }}>Max: {p.max_votes}</span>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <span style={{ ...styles.badge, ...styles.badgeTeal }}>
                    {getCandidatesByPosition(p.id).length} candidates
                  </span>
                  <button
                    style={{ ...styles.button, background: '#ef4444', color: '#fff', paddingTop: '4px', paddingBottom: '4px', paddingLeft: '12px', paddingRight: '12px' }}
                    onClick={() => handleDeletePosition(p.id)}
                    aria-label={`Delete ${p.title}`}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div style={styles.card}>
        <h3 style={{ marginBottom: '16px' }}>Add Candidate</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div>
            <label style={styles.label}>Candidate ID</label>
            <input
              style={styles.input}
              placeholder="e.g., CAND001"
              value={newCandidate.candidate_id}
              onChange={(e) => setNewCandidate(prev => ({ ...prev, candidate_id: e.target.value }))}
              aria-label="Candidate ID"
            />
          </div>
          <div>
            <label style={styles.label}>Name</label>
            <input
              style={styles.input}
              placeholder="Candidate Name"
              value={newCandidate.name}
              onChange={(e) => setNewCandidate(prev => ({ ...prev, name: e.target.value }))}
              aria-label="Candidate Name"
            />
          </div>
          <div>
            <label style={styles.label}>Party</label>
            <input
              style={styles.input}
              placeholder="Party/Organization"
              value={newCandidate.party}
              onChange={(e) => setNewCandidate(prev => ({ ...prev, party: e.target.value }))}
              aria-label="Party"
            />
          </div>
          <div>
            <label style={styles.label}>Position</label>
            {localPositions.length === 0 ? (
              <div style={{ ...styles.input, backgroundColor: '#f3f4f6', color: '#6b7280' }}>
                No positions available - create one first
              </div>
            ) : (
              <select
                style={styles.select}
                value={newCandidate.position_id}
                onChange={(e) => setNewCandidate(prev => ({ ...prev, position_id: e.target.value }))}
                aria-label="Select Position"
              >
                <option value="">Select Position</option>
                {localPositions.map(p => (
                  <option key={p.id} value={String(p.id)}>{p.title}</option>
                ))}
              </select>
            )}
          </div>
          <div style={{ gridColumn: 'span 2' }}>
            <label style={styles.label}>Description</label>
            <input
              style={styles.input}
              placeholder="Brief description"
              value={newCandidate.description}
              onChange={(e) => setNewCandidate(prev => ({ ...prev, description: e.target.value }))}
              aria-label="Description"
            />
          </div>
        </div>
        <button
          style={{
            ...styles.button,
            ...styles.buttonPrimary,
            marginTop: '12px',
            opacity: canAddCandidate && localPositions.length > 0 ? 1 : 0.5,
          }}
          onClick={handleAddCandidate}
          disabled={loading || !canAddCandidate || localPositions.length === 0}
          aria-busy={loading}
        >
          {localPositions.length === 0 ? 'Add positions first' : 'Add Candidate'}
        </button>
        {!canAddCandidate && localPositions.length > 0 && (
          <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
            Fill all required fields (Candidate ID, Name, Position)
          </p>
        )}
      </div>
    </div>
  );
}

ElectionSetup.propTypes = {
  onUpdate: PropTypes.func,
};

ElectionSetup.defaultProps = {
  onUpdate: () => {},
};