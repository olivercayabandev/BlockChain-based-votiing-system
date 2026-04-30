import React, { useState, useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';
import { useAuth } from '../../context/AuthContext';
import { useVoting } from '../../hooks/useVoting';
import { useToast } from '../../hooks/useToast';
import { useBreakpoint } from '../../hooks/useBreakpoint';

const GAS_FEE = 0.05;

export function VoterDashboard() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('voter-dark-mode');
    return saved === 'true';
  });
  
  React.useEffect(() => {
    localStorage.setItem('voter-dark-mode', darkMode);
  }, [darkMode]);
  
  const { isMobile, isTablet } = useBreakpoint();
  const { user, logout, token } = useAuth();
  const { toasts, removeToast, success, error: showError } = useToast();
  const {
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
  } = useVoting(token, user?.resident_id);

  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [confirmModal, setConfirmModal] = useState(false);
  const [voteResult, setVoteResult] = useState(null);
  const [voting, setVoting] = useState(false);

  React.useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleVote = useCallback(async () => {
    if (!selectedCandidate || !selectedPosition) return;
    
    setVoting(true);
    try {
      const data = await vote(selectedCandidate, selectedPosition);
      setVoteResult(data);
      success('Vote recorded successfully!');
      setConfirmModal(false);
    } catch (err) {
      showError(err.message);
    } finally {
      setVoting(false);
    }
  }, [selectedCandidate, selectedPosition, vote, success, showError]);

  const selectedCandidateName = useMemo(() => {
    return candidates.find(c => c.candidate_id === selectedCandidate)?.name || '';
  }, [candidates, selectedCandidate]);

  const canVote = useMemo(() => {
    return selectedCandidate && selectedPosition && !votedPositions.includes(selectedPosition);
  }, [selectedCandidate, selectedPosition, votedPositions]);

  const theme = darkMode ? {
    colors: {
      primary: '#3b82f6',
      primaryLight: '#60a5fa',
      primaryDark: '#2563eb',
      accent: '#14b8a6',
      accentLight: '#5eead4',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      background: '#0f172a',
      surface: '#1e293b',
      surfaceHover: '#334155',
      text: '#f1f5f9',
      textMuted: '#94a3b8',
      border: '#334155',
    },
  } : {
    colors: {
      primary: '#1e40af',
      primaryLight: '#3b82f6',
      primaryDark: '#1e3a8a',
      accent: '#0d9488',
      accentLight: '#14b8a6',
      success: '#16a34a',
      warning: '#d97706',
      error: '#dc2626',
      background: '#f8fafc',
      surface: '#ffffff',
      surfaceHover: '#f1f5f9',
      text: '#0f172a',
      textMuted: '#64748b',
      border: '#e2e8f0',
    },
  };

  const styles = {
    container: { maxWidth: '1200px', margin: '0 auto', padding: isMobile ? '12px' : '24px', fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif', backgroundColor: theme.colors.background, minHeight: '100vh', color: theme.colors.text, transition: 'background-color 0.3s, color 0.3s' },
    header: { background: darkMode ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)', borderRadius: '16px', padding: '24px', marginBottom: '24px', color: darkMode ? '#fff' : '#0f172a', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)', flexWrap: 'wrap', gap: '12px', transition: 'all 0.3s' },
    headerLeft: { flex: 1 },
    headerTitle: { fontSize: isMobile ? '20px' : '24px', fontWeight: '700', margin: 0, color: darkMode ? '#fff' : '#0f172a', textShadow: darkMode ? '0 2px 4px rgba(0,0,0,0.3)' : '0 2px 4px rgba(0,0,0,0.1)' },
    headerSubtitle: { opacity: 0.9, margin: '4px 0 0 0', fontSize: '14px', color: darkMode ? 'rgba(255,255,255,0.9)' : 'rgba(15,23,42,0.9)' },
    headerRight: { display: 'flex', gap: '12px', alignItems: 'center' },
    darkModeToggle: { backgroundColor: 'rgba(255,255,255,0.2)', border: 'none', borderRadius: '50%', width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', fontSize: '18px', backdropFilter: 'blur(10px)', transition: 'all 0.2s', ':hover': { backgroundColor: 'rgba(255,255,255,0.3)' } },
    gasBadge: { backgroundColor: 'rgba(255,255,255,0.2)', padding: '8px 16px', borderRadius: '9999px', backdropFilter: 'blur(10px)', fontSize: '14px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '6px' },
    logoutBtn: { backgroundColor: 'rgba(255,255,255,0.2)', border: 'none', borderRadius: '8px', padding: '10px 20px', color: '#fff', fontSize: '14px', fontWeight: '600', cursor: 'pointer', backdropFilter: 'blur(10px)', transition: 'all 0.2s', ':hover': { backgroundColor: 'rgba(255,255,255,0.3)' } },
    progressCard: { backgroundColor: theme.colors.surface, borderRadius: '12px', padding: '20px', marginBottom: '20px', border: `1px solid ${theme.colors.border}`, boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)', transition: 'all 0.3s' },
    progressHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' },
    progressLabel: { fontSize: '14px', fontWeight: '600', color: theme.colors.textMuted, textTransform: 'uppercase', letterSpacing: '0.5px' },
    progressCount: { fontSize: '14px', fontWeight: '700', color: theme.colors.primary },
    progressBarBg: { width: '100%', height: '10px', backgroundColor: theme.colors.background, borderRadius: '9999px', overflow: 'hidden', border: `1px solid ${theme.colors.border}` },
    progressBarFill: { height: '100%', background: `linear-gradient(90deg, ${theme.colors.primary}, ${theme.colors.accent})`, borderRadius: '9999px', transition: 'width 0.5s ease', boxShadow: `0 0 10px ${theme.colors.primary}50` },
    card: { backgroundColor: theme.colors.surface, borderRadius: '16px', border: `1px solid ${theme.colors.border}`, padding: isMobile ? '16px' : '24px', marginBottom: '20px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)', transition: 'all 0.3s', overflow: 'hidden' },
    cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' },
    positionLabel: { fontSize: '12px', fontWeight: '600', color: theme.colors.textMuted, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' },
    positionTitle: { fontSize: isMobile ? '16px' : '20px', fontWeight: '700', margin: 0, color: theme.colors.text },
    badge: { display: 'inline-flex', padding: '6px 12px', borderRadius: '9999px', fontSize: '12px', fontWeight: '600' },
    badgeSuccess: { backgroundColor: darkMode ? '#064e3b' : '#d1fae5', color: darkMode ? '#6ee7b7' : '#065f46' },
    badgePending: { backgroundColor: darkMode ? '#78350f' : '#fef3c7', color: darkMode ? '#fcd34d' : '#92400e' },
    candidateGrid: { display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginTop: '16px' },
    candidateCard: { backgroundColor: theme.colors.surface, borderRadius: '12px', border: `2px solid ${theme.colors.border}`, padding: '20px', cursor: 'pointer', transition: 'all 0.2s ease', ':hover': { borderColor: theme.colors.primaryLight, transform: 'translateY(-4px)', boxShadow: `0 12px 24px -8px ${theme.colors.primary}26` } },
    candidateCardSelected: { borderColor: theme.colors.primary, backgroundColor: darkMode ? '#1e3a8a20' : '#eff6ff', boxShadow: `0 0 0 3px ${theme.colors.primary}33` },
    candidateCardDisabled: { opacity: 0.5, cursor: 'not-allowed', ':hover': {} },
    candidateAvatar: { width: '48px', height: '48px', borderRadius: '50%', backgroundColor: theme.colors.primary, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '20px', fontWeight: '700', marginBottom: '12px' },
    candidateName: { fontWeight: '600', fontSize: '16px', color: theme.colors.text, marginBottom: '4px' },
    candidateParty: { fontSize: '14px', color: theme.colors.textMuted },
    modal: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '16px', backdropFilter: 'blur(4px)' },
    modalContent: { backgroundColor: theme.colors.surface, borderRadius: '16px', padding: isMobile ? '20px' : '28px', maxWidth: '480px', width: '100%', maxHeight: '90vh', overflow: 'auto', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)', animation: 'slideUp 0.3s ease' },
    modalTitle: { fontSize: isMobile ? '18px' : '20px', fontWeight: '600', marginBottom: '12px', marginTop: 0, color: theme.colors.text },
    modalText: { fontSize: '14px', marginBottom: '12px', color: theme.colors.text },
    alert: { padding: '14px 18px', borderRadius: '8px', marginBottom: '12px', fontSize: '14px', transition: 'all 0.3s' },
    alertGreen: { backgroundColor: darkMode ? '#064e3b' : '#f0fdf4', color: theme.colors.success },
    alertRed: { backgroundColor: darkMode ? '#7f1d1d' : '#fef2f2', color: theme.colors.error },
    alertYellow: { backgroundColor: darkMode ? '#78350f' : '#fef9c3', color: darkMode ? '#fcd34d' : '#854d0e' },
    alertPrimary: { backgroundColor: darkMode ? '#1e3a8a' : '#eff6ff', color: theme.colors.primary },
    flexBetween: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' },
    flexGap: { display: 'flex', gap: '12px', flexWrap: 'wrap' },
    textMuted: { color: theme.colors.textMuted, fontSize: '14px' },
    title: { fontSize: isMobile ? '20px' : '28px', fontWeight: '800', marginBottom: '4px', color: theme.colors.text },
    button: { paddingTop: '12px', paddingBottom: '12px', paddingLeft: '20px', paddingRight: '20px', borderRadius: '8px', border: 'none', fontSize: '14px', fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s' },
    buttonSecondary: { backgroundColor: theme.colors.surfaceHover, color: theme.colors.text },
    buttonPrimary: { backgroundColor: theme.colors.primary, color: '#fff' },
    buttonDisabled: { opacity: 0.5, cursor: 'not-allowed' },
    voteStatusBadges: { display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' },
    confirmedBadge: { backgroundColor: darkMode ? '#064e3b' : '#dcfce7', color: darkMode ? '#6ee7b7' : '#166534', padding: '4px 12px', borderRadius: '9999px', fontSize: '12px', fontWeight: '600', display: 'inline-flex', alignItems: 'center', gap: '4px' },
    pendingBadge: { backgroundColor: darkMode ? '#78350f' : '#fef3c7', color: darkMode ? '#fcd34d' : '#92400e', padding: '4px 12px', borderRadius: '9999px', fontSize: '12px', fontWeight: '600', display: 'inline-flex', alignItems: 'center', gap: '4px' },
  };

  if (loading && positions.length === 0) {
    return (
      <div style={{ ...styles.container, textAlign: 'center', paddingTop: '100px' }}>
        Loading...
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Header with Gradient */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <h1 style={styles.headerTitle}>
            Welcome, {user?.name}
          </h1>
          <p style={styles.headerSubtitle}>Secure Blockchain Voting System</p>
        </div>
        <div style={styles.headerRight}>
          {voteDetails.length > 0 && (
            <div style={styles.voteStatusBadges}>
              {voteDetails.filter(v => v.confirmed).length > 0 && (
                <span style={styles.confirmedBadge}>
                  ✓ {voteDetails.filter(v => v.confirmed).length} Confirmed
                </span>
              )}
              {voteDetails.filter(v => !v.confirmed).length > 0 && (
                <span style={styles.pendingBadge}>
                  ○ {voteDetails.filter(v => !v.confirmed).length} Pending
                </span>
              )}
            </div>
          )}
          <span style={styles.gasBadge}>
            ⛽ Gas: {gasBalance.toFixed(2)}
          </span>
          <button
            style={styles.darkModeToggle}
            onClick={() => setDarkMode(!darkMode)}
            aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
          <button
            style={styles.logoutBtn}
            onClick={() => logout()}
            aria-label="Logout"
          >
            {isMobile ? 'Logout' : 'Logout'}
          </button>
        </div>
      </div>

      {/* Toast Notifications */}
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
            animation: 'slideIn 0.3s ease',
          }}
          onClick={() => removeToast(toast.id)}
          role="status"
        >
          {toast.message}
        </div>
      ))}

      {/* Error Alert */}
      {error && (
        <div style={{ ...styles.alert, ...styles.alertRed }} role="alert">
          {error}
        </div>
      )}

      {/* Progress Bar */}
      {positions.length > 0 && (
        <div style={styles.progressCard}>
          <div style={styles.progressHeader}>
            <span style={styles.progressLabel}>Voting Progress</span>
            <span style={styles.progressCount}>{votedPositions.length}/{positions.length}</span>
          </div>
          <div style={styles.progressBarBg}>
            <div 
              style={{
                ...styles.progressBarFill,
                width: `${positions.length > 0 ? (votedPositions.length / positions.length) * 100 : 0}%`
              }}
            />
          </div>
        </div>
      )}

      {/* Confirmed Votes Alert */}
      {voteDetails.filter(v => v.confirmed).length > 0 && (
        <div style={{ ...styles.alert, ...styles.alertGreen, marginBottom: '16px' }}>
          <strong>✓ Your votes have been confirmed!</strong> All {voteDetails.filter(v => v.confirmed).length} vote(s) recorded in the blockchain.
        </div>
      )}

      {/* Position Cards */}
      {error && (
        <div style={{ ...styles.alert, ...styles.alertRed }} role="alert">
          {error}
        </div>
      )}

      {positions.length === 0 ? (
        <div style={{ ...styles.card, textAlign: 'center' }}>
          <p style={styles.textMuted}>No election positions configured yet. Please contact admin.</p>
        </div>
      ) : (
        positions.map(pos => (
          <div key={pos.id} style={styles.card}>
            {/* Gradient Top Bar */}
            <div style={{
              height: '4px',
              background: votedPositions.includes(pos.id) 
                ? 'linear-gradient(90deg, #10b981, #34d399)'
                : `linear-gradient(90deg, ${theme.colors.primary}, ${theme.colors.primaryLight})`,
              margin: isMobile ? '-16px -16px 16px -16px' : '-24px -24px 16px -24px',
              borderRadius: '16px 16px 0 0'
            }} />
            
            <div style={styles.cardHeader}>
              <div>
                <p style={styles.positionLabel}>Vote for</p>
                <h2 style={styles.positionTitle}>{pos.title}</h2>
              </div>
              {votedPositions.includes(pos.id) ? (
                <span style={{ ...styles.badge, ...styles.badgeSuccess }}>
                  ✓ Voted
                </span>
              ) : (
                <span style={{ ...styles.badge, ...styles.badgePending }}>
                  ○ Pending
                </span>
              )}
            </div>
            
            <div style={styles.candidateGrid}>
              {getCandidatesByPosition(pos.id).map(cand => (
                <div
                  key={cand.candidate_id}
                  style={{
                    ...styles.candidateCard,
                    ...(selectedCandidate === cand.candidate_id && selectedPosition === pos.id ? styles.candidateCardSelected : {}),
                    ...(votedPositions.includes(pos.id) ? styles.candidateCardDisabled : {})
                  }}
                  onClick={() => {
                    if (!votedPositions.includes(pos.id)) {
                      setSelectedCandidate(cand.candidate_id);
                      setSelectedPosition(pos.id);
                      setConfirmModal(true);
                    }
                  }}
                  role="button"
                  tabIndex={votedPositions.includes(pos.id) ? -1 : 0}
                  aria-pressed={selectedCandidate === cand.candidate_id && selectedPosition === pos.id}
                  aria-disabled={votedPositions.includes(pos.id)}
                >
                  <div style={styles.candidateAvatar}>
                    {cand.name.charAt(0)}
                  </div>
                  <div style={styles.candidateName}>{cand.name}</div>
                  <div style={styles.candidateParty}>{cand.party}</div>
                </div>
              ))}
            </div>
          </div>
        ))
      )}

      {/* Confirmation Modal */}
      {confirmModal && (
        <div style={styles.modal} role="dialog" aria-modal="true" aria-labelledby="modal-title">
          <div style={styles.modalContent}>
            <h2 id="modal-title" style={styles.modalTitle}>
              Confirm Your Vote
            </h2>
            <p style={styles.modalText}>
              You are voting for <strong>{selectedCandidateName}</strong> for{' '}
              <strong>{getPositionName(selectedPosition)}</strong>.
            </p>
            <div style={{ ...styles.alert, ...styles.alertYellow, marginBottom: '12px' }}>
              Transaction fee: <strong>{GAS_FEE.toFixed(2)} Gas</strong>. Balance:{' '}
              {gasBalance.toFixed(2)} Gas
            </div>
            {voteResult && (
              <div style={{ ...styles.alert, ...styles.alertGreen, marginBottom: '12px' }}>
                <p style={{ fontWeight: '700', marginTop: 0 }}>Vote Recorded!</p>
                <p style={{ fontSize: '12px', wordBreak: 'break-all', marginBottom: 0 }}>
                  Hash: {voteResult.transaction_hash}
                </p>
              </div>
            )}
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end', flexWrap: 'wrap' }}>
              <button
                style={{ ...styles.button, ...styles.buttonSecondary }}
                onClick={() => setConfirmModal(false)}
              >
                Cancel
              </button>
              <button
                style={{
                  ...styles.button,
                  ...styles.buttonPrimary,
                  ...(!(voting || !canVote) ? {} : styles.buttonDisabled)
                }}
                onClick={handleVote}
                disabled={voting || !canVote}
                aria-busy={voting}
              >
                {voting ? 'Processing...' : 'Confirm Vote'}
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Add CSS animations */}
      <style>{`
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
}

VoterDashboard.propTypes = {
  onNavigate: PropTypes.func.isRequired,
};

VoterDashboard.defaultProps = {
  onNavigate: () => {},
};
