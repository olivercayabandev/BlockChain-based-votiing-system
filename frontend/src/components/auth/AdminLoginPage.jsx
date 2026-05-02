import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import { useBreakpoint } from '../../hooks/useBreakpoint';

const API_URL = '';

const theme = {
  colors: {
    primary: '#1e40af',
    primaryLight: '#3b82f6',
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

export function AdminLoginPage({ onSwitchPage }) {
  const { isMobile } = useBreakpoint();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const styles = {
    container: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: theme.colors.background, padding: '20px', fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif' },
    card: { backgroundColor: theme.colors.surface, borderRadius: '12px', border: `1px solid ${theme.colors.border}`, padding: isMobile ? '24px' : '32px', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)', maxWidth: '420px', width: '100%' },
    logo: { width: '72px', height: '72px', backgroundColor: theme.colors.primary, borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px', color: '#fff', fontSize: '28px', fontWeight: 'bold' },
    header: { textAlign: 'center', marginBottom: '28px' },
    title: { fontSize: '26px', fontWeight: '700', color: theme.colors.text, marginBottom: '8px' },
    subtitle: { fontSize: '14px', color: theme.colors.textMuted },
    input: { width: '100%', padding: '14px 16px', borderRadius: '8px', border: `1px solid ${theme.colors.border}`, fontSize: '16px', outline: 'none', boxSizing: 'border-box', backgroundColor: theme.colors.surface, transition: 'border-color 0.2s', focus: { borderColor: theme.colors.primary, boxShadow: '0 0 0 3px rgba(30, 64, 175, 0.1)' } },
    button: { padding: '14px 24px', borderRadius: '8px', border: 'none', fontSize: '16px', fontWeight: '600', cursor: 'pointer', width: '100%', transition: 'all 0.2s' },
    buttonPrimary: { backgroundColor: theme.colors.primary, color: '#fff' },
    buttonSecondary: { backgroundColor: '#f1f5f9', color: theme.colors.text },
    alert: { padding: '14px 18px', borderRadius: '8px', marginBottom: '16px', fontSize: '14px' },
    alertRed: { backgroundColor: '#fef2f2', color: theme.colors.error },
    label: { display: 'block', fontSize: '14px', fontWeight: '600', color: theme.colors.text, marginBottom: '8px' },
    footerLink: { textAlign: 'center', marginTop: '20px', paddingTop: '20px', borderTop: `1px solid ${theme.colors.border}` },
    link: { color: theme.colors.primary, cursor: 'pointer', textDecoration: 'none', fontSize: '14px', fontWeight: '500' },
    passwordWrapper: { position: 'relative' },
    showPassword: { position: 'absolute', right: '14px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: theme.colors.textMuted, fontSize: '14px', padding: '4px 8px' },
  };

  const handleLogin = useCallback(async () => {
    if (!username.trim()) {
      setError('Username is required');
      return;
    }
    if (!password) {
      setError('Password is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await fetch(`/api/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim(), password })
      });
      
      let data;
      const contentType = res.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await res.json();
      } else {
        data = { detail: `Server error: ${res.status}` };
      }
      
      if (!res.ok) {
        throw new Error(data.detail || `Login failed (${res.status})`);
      }
      
      localStorage.setItem('admin-token', data.token);
      localStorage.setItem('admin-user', JSON.stringify({
        username: data.username,
        role: data.role
      }));
      window.location.href = '/admin';
    } catch (err) {
      if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
        setError('Cannot connect to server. Please check your connection.');
      } else {
        setError(err.message || 'Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [username, password]);

  return (
    <div style={styles.container}>
      <div style={styles.loginBox}>
        <div style={styles.pageTitle}>
          <h1 style={styles.title}>Election Administration</h1>
          <p style={styles.textMuted}>Administrator Access</p>
        </div>
        <div style={styles.card}>
          <div style={styles.infoBox}>
            <strong>Administrator Portal</strong>
            <br />
            This area is restricted to authorized administrators only.
            <br /><br />
            For election officials, use the <span style={styles.link} onClick={() => onSwitchPage('officials-login')}>Officials Portal</span>.
          </div>

          <label style={styles.label}>Username</label>
          <input
            style={styles.input}
            type="text"
            placeholder="Enter username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
            autoComplete="username"
          />

          <div style={styles.passwordBox}>
            <label style={styles.label}>Password</label>
            <input
              type={showPassword ? 'text' : 'password'}
              style={styles.input}
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
              autoComplete="current-password"
            />
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px', marginTop: '8px' }}>
              <input
                type="checkbox"
                checked={showPassword}
                onChange={(e) => setShowPassword(e.target.checked)}
              />
              Show password
            </label>
          </div>
          
          {error && <div style={{ ...styles.alert, ...styles.alertRed }} role="alert">{error}</div>}
          
          <button
            style={{ ...styles.button, ...styles.buttonPrimary, marginTop: '8px' }}
            onClick={handleLogin}
            disabled={loading}
            aria-busy={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </div>

        <div style={styles.divider}>
          <div style={styles.dividerLine}></div>
          <span style={styles.dividerText}>OR</span>
          <div style={styles.dividerLine}></div>
        </div>

        <div style={{ textAlign: 'center' }}>
          <button
            style={{ ...styles.button, ...styles.buttonSecondary, marginTop: '8px', fontSize: '13px', padding: '8px 16px' }}
            onClick={() => window.location.href = '/officials-login'}
          >
            Go to Officials Portal
          </button>
        </div>

        <div style={{ textAlign: 'center', marginTop: '20px', display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button
            style={{ background: 'transparent', color: '#6b7280', border: 'none', fontSize: '12px', cursor: 'pointer', padding: '4px' }}
            onClick={() => window.location.href = '/officials-login'}
          >
            Officials
          </button>
          <span style={{ color: '#d1d5db' }}>|</span>
          <button
            style={{ background: 'transparent', color: '#6b7280', border: 'none', fontSize: '12px', cursor: 'pointer', padding: '4px' }}
            onClick={() => window.location.href = '/'}
          >
            Voter Login
          </button>
        </div>
      </div>
    </div>
  );
}

AdminLoginPage.propTypes = {
  onSwitchPage: PropTypes.func.isRequired,
};