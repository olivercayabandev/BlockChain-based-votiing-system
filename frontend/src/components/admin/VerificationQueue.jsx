import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { useBreakpoint } from '../../hooks/useBreakpoint';
import { useToast } from '../../hooks/useToast';
import { API_URL } from '../../utils/validation';

const styles = {
  container: { maxWidth: '1200px', margin: '0 auto', padding: '20px', fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' },
  title: { fontSize: '20px', fontWeight: '700', color: '#111827', margin: 0 },
  card: { backgroundColor: '#fff', borderRadius: '8px', borderWidth: '1px', borderStyle: 'solid', borderColor: '#e5e7eb', paddingTop: '20px', paddingBottom: '20px', paddingLeft: '20px', paddingRight: '20px', marginBottom: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' },
  badge: { display: 'inline-flex', paddingTop: '2px', paddingBottom: '2px', paddingLeft: '8px', paddingRight: '8px', borderRadius: '9999px', fontSize: '12px', fontWeight: '500' },
  badgeYellow: { backgroundColor: '#fef3c7', color: '#92400e' },
  textMuted: { color: '#6b7280', fontSize: '14px' },
  grid: { display: 'grid', gap: '16px', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' },
  idPhoto: { width: '100%', maxHeight: '200px', objectFit: 'contain', borderRadius: '8px', border: '1px solid #e5e7eb' },
  emptyState: { textAlign: 'center', paddingTop: '40px', paddingBottom: '40px', color: '#6b7280' },
  viewOnlyNotice: { backgroundColor: '#f0fdfa', border: '1px solid #ccfbf1', borderRadius: '6px', padding: '12px', fontSize: '13px', color: '#134e4a', marginBottom: '16px' },
};

export function VerificationQueue({ token }) {
  const { isMobile, isTablet } = useBreakpoint();
  const { toasts, removeToast, success, error: showError } = useToast();
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchQueue = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/admin/verification-queue?token=${token}`);
      if (!res.ok) throw new Error('Failed to fetch verification queue');
      const data = await res.json();
      setQueue(data);
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  }, [token, showError]);

  useEffect(() => {
    fetchQueue();
  }, [fetchQueue]);

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
            ...(toast.type === 'success' ? { backgroundColor: '#dcfce7', color: '#166534' } : { backgroundColor: '#fee2e2', color: '#991b1b' }),
          }}
          onClick={() => removeToast(toast.id)}
          role="status"
        >
          {toast.message}
        </div>
      ))}

      <div style={styles.header}>
        <h2 style={styles.title}>Pending Verifications ({queue.length})</h2>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button
            style={{ backgroundColor: '#f3f4f6', color: '#374151', padding: '8px 16px', borderRadius: '6px', border: 'none', fontSize: '14px', cursor: 'pointer' }}
            onClick={fetchQueue}
            disabled={loading}
          >
            Refresh
          </button>
        </div>
      </div>

      <div style={styles.viewOnlyNotice}>
        <strong>View Only:</strong> Voter verification is handled by Election Officials only. This page shows pending voters for monitoring purposes.
      </div>

      {loading ? (
        <div style={{ ...styles.card, textAlign: 'center' }}>Loading...</div>
      ) : queue.length === 0 ? (
        <div style={{ ...styles.card, ...styles.emptyState }}>
          <p>No pending verifications</p>
          <p style={{ fontSize: '12px' }}>All voters have been reviewed by election officials</p>
        </div>
      ) : (
        <div style={isMobile ? { display: 'flex', flexDirection: 'column', gap: '12px' } : styles.grid}>
          {queue.map(voter => (
            <div key={voter.resident_id} style={styles.card}>
              <div style={{ marginBottom: '12px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: '600', margin: '0 0 4px 0' }}>{voter.name}</h3>
                <p style={{ ...styles.textMuted, margin: '0 0 8px 0' }}>ID: {voter.resident_id}</p>
                <span style={{ ...styles.badge, ...styles.badgeYellow }}>
                  {voter.verification_status}
                </span>
              </div>
              
              <div style={{ marginTop: '12px', fontSize: '14px' }}>
                <p style={{ margin: '0 0 4px 0' }}><strong>ID Type:</strong> {voter.id_type || 'Not provided'}</p>
                <p style={{ margin: '0 0 4px 0' }}><strong>ID Number:</strong> {voter.id_number || 'Not provided'}</p>
                {voter.phone_number && (
                  <p style={{ margin: '0 0 4px 0' }}><strong>Phone:</strong> {voter.phone_number}</p>
                )}
              </div>

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
          ))}
        </div>
      )}
    </div>
  );
}

VerificationQueue.propTypes = {
  token: PropTypes.string,
};

VerificationQueue.defaultProps = {
  token: '',
};