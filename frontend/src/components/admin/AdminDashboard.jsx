import React, { useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';
import { useAdmin } from '../../hooks/useAdmin';
import { useToast } from '../../hooks/useToast';
import { useBreakpoint } from '../../hooks/useBreakpoint';
import { ElectionSetup } from './ElectionSetup';
import { VerificationQueue } from './VerificationQueue';
import { BulkImport } from './BulkImport';
import { BlockchainVisualizer } from '../shared/BlockchainVisualizer';
import { VerificationTool } from '../shared/VerificationTool';
import { SystemReset } from './SystemReset';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function AdminDashboard() {
  const { isMobile, isTablet } = useBreakpoint();
  const adminToken = localStorage.getItem('admin-token');
  const { toasts, removeToast, success, error: showError } = useToast();
  const {
    voters,
    stats,
    candidates,
    chainValid,
    loading,
    error,
    fetchData,
    approveVoter,
    deleteVoter,
  } = useAdmin(adminToken);

  const [activeTab, setActiveTab] = React.useState('voters');

  React.useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleApprove = useCallback(async (residentId, approved) => {
    try {
      await approveVoter(residentId, approved);
      success(`Voter ${approved ? 'approved' : 'rejected'} successfully`);
    } catch (err) {
      showError(err.message);
    }
  }, [approveVoter, success, showError]);

  const handleDelete = useCallback(async (residentId) => {
    if (!window.confirm(`Are you sure you want to delete voter ${residentId}? This action cannot be undone.`)) {
      return;
    }
    try {
      await deleteVoter(residentId);
      success(`Voter ${residentId} deleted successfully`);
    } catch (err) {
      showError(err.message);
    }
  }, [deleteVoter, success, showError]);

  const filteredVoters = useMemo(() => {
    return voters.filter(v => v.resident_id !== 'ADMIN001');
  }, [voters]);

  const pendingCount = useMemo(() => {
    return filteredVoters.filter(v => !v.is_approved && v.verification_status === 'pending').length;
  }, [filteredVoters]);

  const approvedCount = useMemo(() => {
    return filteredVoters.filter(v => v.is_approved).length;
  }, [filteredVoters]);

  const tabs = ['voters', 'verification', 'import', 'setup', 'blockchain', 'verify', 'reset'];

  const theme = {
  colors: {
    primary: '#1e40af',
    primaryLight: '#3b82f6',
    primaryDark: '#1e3a8a',
    accent: '#0d9488',
    accentLight: '#14b8a6',
    success: '#16a34a',
    warning: '#d97706',
    error: '#dc2626',
    background: '#f1f5f9',
    surface: '#ffffff',
    text: '#1e293b',
    textMuted: '#64748b',
    border: '#e2e8f0',
  },
};

const styles = {
  container: { maxWidth: '1200px', margin: '0 auto', padding: isMobile ? '12px' : '24px', fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif', backgroundColor: theme.colors.background, minHeight: '100vh' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', paddingBottom: '20px', borderBottomWidth: '2px', borderBottomStyle: 'solid', borderBottomColor: theme.colors.primary, flexWrap: 'wrap', gap: '12px' },
  card: { backgroundColor: theme.colors.surface, borderRadius: '12px', borderWidth: '1px', borderStyle: 'solid', borderColor: theme.colors.border, padding: isMobile ? '16px' : '24px', marginBottom: '20px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' },
  cardTitle: { fontSize: '18px', fontWeight: '700', color: theme.colors.primary, marginBottom: '16px', paddingBottom: '8px', borderBottomWidth: '1px', borderBottomStyle: 'solid', borderBottomColor: theme.colors.border },
  button: { padding: '10px 20px', borderRadius: '8px', border: 'none', fontSize: '14px', fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s' },
  buttonSecondary: { backgroundColor: '#f1f5f9', color: theme.colors.text },
  buttonPrimary: { backgroundColor: theme.colors.primary, color: '#fff' },
  buttonDanger: { backgroundColor: theme.colors.error, color: '#fff' },
  badge: { display: 'inline-flex', padding: '4px 12px', borderRadius: '9999px', fontSize: '12px', fontWeight: '600' },
  badgeTeal: { backgroundColor: '#ccfbf1', color: '#0f766e' },
  badgeYellow: { backgroundColor: '#fef3c7', color: '#92400e' },
  badgeRed: { backgroundColor: '#fee2e2', color: '#991b1b' },
  badgeGreen: { backgroundColor: '#dcfce7', color: '#166534' },
  badgePrimary: { backgroundColor: '#dbeafe', color: theme.colors.primary },
  title: { fontSize: isMobile ? '20px' : '28px', fontWeight: '800', color: theme.colors.text },
  subtitle: { fontSize: '14px', color: theme.colors.textMuted },
  grid: { display: 'grid', gridTemplateColumns: isMobile ? 'repeat(2, 1fr)' : isTablet ? 'repeat(2, 1fr)' : 'repeat(4, 1fr)', gap: isMobile ? '12px' : '20px' },
  flexBetween: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' },
  flexGap: { display: 'flex', gap: '12px', flexWrap: 'wrap' },
  table: { width: '100%', borderCollapse: 'collapse', minWidth: '400px' },
  th: { textAlign: 'left', padding: '12px', borderBottomWidth: '2px', borderBottomStyle: 'solid', borderBottomColor: theme.colors.border, fontWeight: '600', color: theme.colors.textMuted, fontSize: '13px', whiteSpace: 'nowrap' },
  td: { padding: '12px', borderBottomWidth: '1px', borderBottomStyle: 'solid', borderBottomColor: theme.colors.border, fontSize: '14px' },
  statValue: { fontSize: isMobile ? '28px' : '36px', fontWeight: '800', color: theme.colors.primary },
  statLabel: { fontSize: '13px', color: theme.colors.textMuted, textTransform: 'uppercase', letterSpacing: '0.5px' },
  tabs: { display: 'flex', gap: isMobile ? '4px' : '8px', borderBottomWidth: '2px', borderBottomStyle: 'solid', borderBottomColor: theme.colors.border, marginBottom: '20px', overflowX: 'auto', paddingBottom: '2px' },
  tab: { padding: isMobile ? '10px 14px' : '12px 20px', cursor: 'pointer', borderBottomWidth: '2px', borderBottomStyle: 'solid', borderBottomColor: 'transparent', fontSize: isMobile ? '13px' : '14px', whiteSpace: 'nowrap', fontWeight: '500', color: theme.colors.textMuted },
  tabActive: { borderBottomColor: theme.colors.primary, color: theme.colors.primary },
  alert: { padding: '14px 18px', borderRadius: '8px', marginBottom: '12px', fontSize: '14px' },
  alertRed: { backgroundColor: '#fef2f2', color: theme.colors.error },
  alertGreen: { backgroundColor: '#dcfce7', color: theme.colors.success },
  alertPrimary: { backgroundColor: '#eff6ff', color: theme.colors.primary },
};

  if (loading && voters.length === 0) {
    return (
      <div style={{ ...styles.container, textAlign: 'center', paddingTop: '100px' }}>
        Loading...
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Admin Dashboard</h1>
          <p style={styles.textMuted}>Manage election</p>
        </div>
        <div style={styles.flexGap}>
          <span style={{ ...styles.badge, ...(chainValid ? styles.badgeGreen : styles.badgeRed) }}>
            Chain: {chainValid ? 'Valid' : 'Invalid'}
          </span>
          <button
            style={{ ...styles.button, ...styles.buttonSecondary }}
            onClick={() => {
              localStorage.removeItem('admin-token');
              localStorage.removeItem('admin-user');
              window.location.href = '/admin-login';
            }}
            aria-label="Logout"
          >
            Logout
          </button>
        </div>
      </div>

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

      {error && (
        <div style={{ ...styles.alert, ...styles.alertRed }} role="alert">
          {error}
        </div>
      )}

      <div style={styles.tabs} role="tablist">
        {tabs.map(tab => (
          <div
            key={tab}
            role="tab"
            aria-selected={activeTab === tab}
            tabIndex={activeTab === tab ? 0 : -1}
            style={{ ...styles.tab, ...(activeTab === tab ? styles.tabActive : {}) }}
            onClick={() => setActiveTab(tab)}
            onKeyPress={(e) => e.key === 'Enter' && setActiveTab(tab)}
          >
            {tab === 'verification' && pendingCount > 0 ? (
              <span style={{ position: 'relative' }}>
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
                <span style={{ position: 'absolute', top: '-6px', right: '-8px', background: '#dc2626', color: 'white', borderRadius: '50%', width: '18px', height: '18px', fontSize: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {pendingCount}
                </span>
              </span>
            ) : (
              tab.charAt(0).toUpperCase() + tab.slice(1)
            )}
          </div>
        ))}
      </div>

      {activeTab === 'voters' && (
        <>
          <div style={styles.grid}>
            <div style={styles.card}>
              <p style={{ ...styles.textMuted, fontSize: '12px' }}>Total</p>
              <p style={styles.statValue}>{stats.total_voters || 0}</p>
            </div>
            <div style={styles.card}>
              <p style={{ ...styles.textMuted, fontSize: '12px' }}>Pending</p>
              <p style={{ ...styles.statValue, color: '#f59e0b' }}>{pendingCount}</p>
            </div>
            <div style={styles.card}>
              <p style={{ ...styles.textMuted, fontSize: '12px' }}>Approved</p>
              <p style={styles.statValue}>{approvedCount}</p>
            </div>
            <div style={styles.card}>
              <p style={{ ...styles.textMuted, fontSize: '12px' }}>Votes</p>
              <p style={styles.statValue}>{stats.confirmed_votes || 0}</p>
            </div>
          </div>
          <div style={styles.card}>
            <div style={{ ...styles.flexBetween, marginBottom: '12px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: '600' }}>Voter Status</h3>
              <span style={{ ...styles.badge, ...styles.badgeYellow, fontSize: '11px' }}>View Only - Approval handled by Officials</span>
            </div>
            <div style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch' }}>
              <table style={styles.table} role="grid">
                <thead>
                  <tr>
                    <th style={styles.th} scope="col">ID</th>
                    <th style={styles.th} scope="col">Name</th>
                    <th style={styles.th} scope="col">Status</th>
                    <th style={styles.th} scope="col">Approved By</th>
                    <th style={styles.th} scope="col">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredVoters.map(v => (
                    <tr key={v.resident_id}>
                      <td style={styles.td}>{v.resident_id}</td>
                      <td style={styles.td}>{v.name}</td>
                      <td style={styles.td}>
                        <span style={{ ...styles.badge, ...(v.verification_status === 'approved' ? styles.badgeGreen : v.verification_status === 'rejected' ? styles.badgeRed : styles.badgeYellow) }}>
                          {v.verification_status || 'pending'}
                        </span>
                      </td>
                      <td style={styles.td}>
                        <span style={{ fontSize: '12px', color: v.verified_by ? '#374151' : '#9ca3af' }}>
                          {v.verified_by || '-'}
                        </span>
                      </td>
                      <td style={styles.td}>
                        <button
                          onClick={() => handleDelete(v.resident_id)}
                          style={{
                            paddingTop: '4px',
                            paddingBottom: '4px',
                            paddingLeft: '8px',
                            paddingRight: '8px',
                            fontSize: '12px',
                            backgroundColor: '#dc2626',
                            color: '#fff',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                          }}
                          title="Delete voter"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {activeTab === 'verification' && (
        <VerificationQueue token={adminToken} />
      )}

      {activeTab === 'import' && (
        <div style={styles.card}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', marginTop: 0, marginBottom: '16px' }}>
            Bulk Import Pre-Verified Voters
          </h3>
          <BulkImport token={adminToken} onImportComplete={fetchData} />
        </div>
      )}

      {activeTab === 'setup' && (
        <ElectionSetup onUpdate={fetchData} />
      )}

      {activeTab === 'blockchain' && <BlockchainVisualizer onSwitchPage={() => {}} />}
      {activeTab === 'verify' && <VerificationTool onSwitchPage={() => {}} />}
      {activeTab === 'reset' && <SystemReset token={adminToken} />}
    </div>
  );
}

AdminDashboard.propTypes = {};