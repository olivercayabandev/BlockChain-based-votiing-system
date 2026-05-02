import React, { useState, useEffect, useCallback, useRef } from 'react';
import PropTypes from 'prop-types';
import { useBreakpoint } from '../../hooks/useBreakpoint';

const API_URL = '';

export function OfficialDashboard({ onNavigate }) {
  const { isMobile } = useBreakpoint();
  const [voters, setVoters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [toasts, setToasts] = useState([]);
  const [selectedVoter, setSelectedVoter] = useState(null);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const previousVotersRef = useRef(new Set());
  const pollingIntervalRef = useRef(null);

  const officialUser = JSON.parse(localStorage.getItem('official-user') || '{}');
  const officialToken = localStorage.getItem('official-token');

  const styles = {
    container: { maxWidth: '1400px', margin: '0 auto', padding: isMobile ? '12px' : '20px', fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', paddingBottom: '16px', borderBottomWidth: '1px', borderBottomStyle: 'solid', borderBottomColor: '#e5e7eb', flexWrap: 'wrap', gap: '12px' },
    card: { backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e5e7eb', padding: isMobile ? '16px' : '20px', marginBottom: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' },
    button: { padding: '10px 16px', borderRadius: '6px', border: 'none', fontSize: '14px', fontWeight: '500', cursor: 'pointer' },
    buttonPrimary: { backgroundColor: '#0d9488', color: '#fff' },
    buttonSecondary: { backgroundColor: '#f3f4f6', color: '#374151' },
    buttonSuccess: { backgroundColor: '#22c55e', color: '#fff' },
    buttonDanger: { backgroundColor: '#dc2626', color: '#fff' },
    buttonWarning: { backgroundColor: '#f59e0b', color: '#fff' },
    badge: { display: 'inline-flex', alignItems: 'center', paddingTop: '4px', paddingBottom: '4px', paddingLeft: '10px', paddingRight: '10px', borderRadius: '9999px', fontSize: '12px', fontWeight: '500', gap: '6px' },
    badgeYellow: { backgroundColor: '#fef3c7', color: '#92400e' },
    badgeGreen: { backgroundColor: '#dcfce7', color: '#166534' },
    badgeBlue: { backgroundColor: '#dbeafe', color: '#1e40af' },
    title: { fontSize: isMobile ? '18px' : '24px', fontWeight: '700', color: '#111827', marginBottom: '4px' },
    subtitle: { fontSize: '14px', color: '#6b7280' },
    statValue: { fontSize: '32px', fontWeight: '700', color: '#0d9488' },
    textMuted: { color: '#6b7280', fontSize: '14px' },
    idPhoto: { width: '100%', maxHeight: '200px', objectFit: 'contain', borderRadius: '8px', border: '1px solid #e5e7eb', marginTop: '8px' },
    modal: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 },
    modalContent: { backgroundColor: '#fff', borderRadius: '12px', padding: '24px', maxWidth: '500px', width: '95%', maxHeight: '90vh', overflow: 'auto' },
    select: { width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', backgroundColor: '#fff', marginBottom: '12px' },
    input: { width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', marginBottom: '12px', outline: 'none' },
    label: { display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' },
  };

  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const fetchVoters = useCallback(async (isInitial = false) => {
    if (!officialToken) return;
    
    if (isInitial) setLoading(true);
    
    try {
      const res = await fetch(`/api/official/pending-voters?token=${officialToken}`);
      if (!res.ok) throw new Error('Failed to fetch voters');
      
      const data = await res.json();
      const newVoters = data.voters || [];
      
      if (!isInitial) {
        const previousIds = previousVotersRef.current;
        for (const voter of newVoters) {
          if (!previousIds.has(voter.resident_id)) {
            if (voter.verification_status === 'approved') {
              addToast(`Voter ${voter.name} was just approved by another official`, 'success');
            } else if (voter.verification_status === 'rejected') {
              addToast(`Voter ${voter.name} was just rejected`, 'warning');
            }
          }
        }
      }
      
      previousVotersRef.current = new Set(newVoters.map(v => v.resident_id));
      setVoters(newVoters);
      setError('');
    } catch (err) {
      if (isInitial) setError(err.message);
    } finally {
      if (isInitial) setLoading(false);
    }
  }, [officialToken, addToast]);

  useEffect(() => {
    fetchVoters(true);
    
    pollingIntervalRef.current = setInterval(() => {
      fetchVoters(false);
    }, 3000);
    
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [fetchVoters]);

  const handleStartReview = useCallback(async (residentId) => {
    try {
      const res = await fetch(`/api/official/start-review/${residentId}?token=${officialToken}`, {
        method: 'POST'
      });
      const data = await res.json();
      
      if (!res.ok) {
        if (res.status === 409) {
          addToast(`${data.reviewed_by_name} is currently reviewing this voter`, 'warning');
        } else {
          throw new Error(data.detail || 'Failed to start review');
        }
      }
    } catch (err) {
      addToast(err.message, 'error');
    }
  }, [officialToken, addToast]);

  const handleEndReview = useCallback(async (residentId) => {
    try {
      await fetch(`/api/official/end-review/${residentId}?token=${officialToken}`, {
        method: 'POST'
      });
    } catch (err) {
      console.error('Failed to end review:', err);
    }
  }, [officialToken]);

  const handleApprove = useCallback(async (voter) => {
    const officialId = officialUser.official_id;
    const action = 'approve';
    
    try {
      const res = await fetch(`/api/official/verify-voter/${voter.resident_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ official_id: officialId, action })
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to approve');
      
      addToast(`${voter.name} has been approved`, 'success');
      await handleEndReview(voter.resident_id);
      fetchVoters(false);
    } catch (err) {
      addToast(err.message, 'error');
    }
  }, [officialUser.official_id, addToast, handleEndReview, fetchVoters]);

  const handleReject = useCallback(async () => {
    if (!selectedVoter || !rejectReason) return;
    
    const officialId = officialUser.official_id;
    const action = 'reject';
    
    try {
      const res = await fetch(`/api/official/verify-voter/${selectedVoter.resident_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ official_id: officialId, action, reason: rejectReason })
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to reject');
      
      addToast(`${selectedVoter.name} has been rejected`, 'warning');
      setShowRejectModal(false);
      setSelectedVoter(null);
      setRejectReason('');
      await handleEndReview(selectedVoter.resident_id);
      fetchVoters(false);
    } catch (err) {
      addToast(err.message, 'error');
    }
  }, [selectedVoter, rejectReason, officialUser.official_id, addToast, handleEndReview, fetchVoters]);

  const openRejectModal = useCallback((voter) => {
    setSelectedVoter(voter);
    setShowRejectModal(true);
  }, []);

  const handleLogout = useCallback(() => {
    localStorage.removeItem('official-token');
    localStorage.removeItem('official-user');
    window.location.href = '/';
  }, []);

  const handleRefresh = useCallback(() => {
    fetchVoters(true);
  }, [fetchVoters]);

  const REJECTION_REASONS = [
    'ID is unclear/unreadable',
    'Duplicate registration',
    'Invalid ID number',
    'Suspected fraudulent ID',
    'Name does not match ID',
    'ID expired',
    'Other (see notes)',
  ];

  return (
    <div style={styles.container}>
      {toasts.map(toast => (
        <div
          key={toast.id}
          style={{
            ...styles.card,
            position: 'fixed',
            top: '20px',
            right: '20px',
            zIndex: 2000,
            cursor: 'pointer',
            ...(toast.type === 'success' 
              ? { backgroundColor: '#dcfce7', color: '#166534' }
              : toast.type === 'warning'
              ? { backgroundColor: '#fef3c7', color: '#92400e' }
              : { backgroundColor: '#dbeafe', color: '#1e40af' }
            ),
            minWidth: '300px',
            maxWidth: '400px',
          }}
          onClick={() => removeToast(toast.id)}
          role="status"
        >
          {toast.message}
        </div>
      ))}

      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Election Official Portal</h1>
          <p style={styles.subtitle}>Welcome, {officialUser.name || 'Official'}</p>
        </div>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button style={{ ...styles.button, ...styles.buttonSecondary }} onClick={handleRefresh}>
            Refresh
          </button>
          <button style={{ ...styles.button, ...styles.buttonDanger }} onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>

      <div style={styles.card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div>
            <p style={styles.textMuted}>Pending Verifications</p>
            <p style={styles.statValue}>{voters.length}</p>
          </div>
          <div style={{ marginLeft: 'auto', ...styles.badge, ...styles.badgeYellow }}>
            Auto-refresh: 3s
          </div>
        </div>
      </div>

      {loading ? (
        <div style={{ ...styles.card, textAlign: 'center', padding: '40px' }}>
          Loading...
        </div>
      ) : error ? (
        <div style={{ ...styles.card, textAlign: 'center', padding: '40px', color: '#dc2626' }}>
          {error}
          <button style={{ ...styles.button, ...styles.buttonPrimary, marginTop: '12px' }} onClick={handleRefresh}>
            Retry
          </button>
        </div>
      ) : voters.length === 0 ? (
        <div style={{ ...styles.card, textAlign: 'center', padding: '40px' }}>
          <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>No pending verifications</p>
          <p style={styles.textMuted}>All voters have been reviewed</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {voters.map(voter => (
            <div key={voter.resident_id} style={styles.card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                <div style={{ flex: 1, minWidth: '200px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px', flexWrap: 'wrap' }}>
                    <h3 style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>{voter.name}</h3>
                    {voter.is_under_review && (
                      <span style={{ ...styles.badge, ...styles.badgeYellow }}>
                        <span>👁</span>
                        Being reviewed by {voter.reviewed_by}
                      </span>
                    )}
                  </div>
                  <p style={{ ...styles.textMuted, marginBottom: '4px' }}>
                    <strong>Resident ID:</strong> {voter.resident_id}
                  </p>
                  {voter.id_type && (
                    <p style={{ ...styles.textMuted, marginBottom: '4px' }}>
                      <strong>{voter.id_type}:</strong> {voter.id_number}
                    </p>
                  )}
                  {voter.phone_number && (
                    <p style={{ ...styles.textMuted, marginBottom: '4px' }}>
                      <strong>Phone:</strong> {voter.phone_number}
                    </p>
                  )}
                  
                  {voter.id_photo_front && (
                    <div style={{ marginTop: '12px' }}>
                      <p style={{ fontSize: '12px', fontWeight: '500', marginBottom: '4px' }}>ID Photo:</p>
                      <img 
                        src={`data:image/jpeg;base64,${voter.id_photo_front}`} 
                        alt="ID Front" 
                        style={styles.idPhoto}
                      />
                    </div>
                  )}
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', minWidth: '140px' }}>
                  <button
                    style={{ ...styles.button, ...styles.buttonSuccess }}
                    onClick={() => handleApprove(voter)}
                    onMouseEnter={() => handleStartReview(voter.resident_id)}
                    onMouseLeave={() => handleEndReview(voter.resident_id)}
                  >
                    ✓ Approve
                  </button>
                  <button
                    style={{ ...styles.button, ...styles.buttonDanger }}
                    onClick={() => openRejectModal(voter)}
                    onMouseEnter={() => handleStartReview(voter.resident_id)}
                    onMouseLeave={() => handleEndReview(voter.resident_id)}
                  >
                    ✕ Reject
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showRejectModal && selectedVoter && (
        <div style={styles.modal} onClick={() => setShowRejectModal(false)}>
          <div style={styles.modalContent} onClick={e => e.stopPropagation()}>
            <h3 style={{ marginTop: 0 }}>Reject Voter</h3>
            <p style={{ fontWeight: '600' }}>{selectedVoter.name} ({selectedVoter.resident_id})</p>
            
            <label style={styles.label}>Reason for Rejection</label>
            <select
              style={styles.select}
              value={rejectReason}
              onChange={e => setRejectReason(e.target.value)}
            >
              <option value="">Select a reason...</option>
              {REJECTION_REASONS.map(reason => (
                <option key={reason} value={reason}>{reason}</option>
              ))}
            </select>

            <label style={styles.label}>Additional Notes (Optional)</label>
            <textarea
              style={{ ...styles.input, height: '80px', resize: 'vertical' }}
              placeholder="Add any additional notes..."
            />

            <p style={{ fontSize: '12px', color: '#6b7280', marginBottom: '16px' }}>
              Note: The ID number will be flagged and cannot be used for re-registration.
            </p>

            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
              <button
                style={{ ...styles.button, ...styles.buttonSecondary }}
                onClick={() => setShowRejectModal(false)}
              >
                Cancel
              </button>
              <button
                style={{ ...styles.button, ...styles.buttonDanger }}
                onClick={handleReject}
                disabled={!rejectReason}
              >
                Confirm Reject
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

OfficialDashboard.propTypes = {
  onNavigate: PropTypes.func,
};