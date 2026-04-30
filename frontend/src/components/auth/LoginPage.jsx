import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import { useAuth } from '../../context/AuthContext';
import { useBreakpoint } from '../../hooks/useBreakpoint';

const API_URL = import.meta.env.VITE_API_URL || '';

export function LoginPage({ onSwitchPage }) {
  const { isMobile } = useBreakpoint();
  const [idType, setIdType] = useState('resident_id');
  const [idNumber, setIdNumber] = useState('');
  const [pin, setPin] = useState('');
  const [showPin, setShowPin] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [needsPinSetup, setNeedsPinSetup] = useState(false);
  const [pinSetupToken, setPinSetupToken] = useState('');
  const [voterName, setVoterName] = useState('');
  const [confirmPin, setConfirmPin] = useState('');
  const { login } = useAuth();

  const styles = {
    container: { maxWidth: '1200px', margin: '0 auto', padding: isMobile ? '12px' : '20px', fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif' },
    card: { backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e5e7eb', padding: isMobile ? '16px' : '24px', marginBottom: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' },
    input: { width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '16px', outline: 'none', boxSizing: 'border-box' },
    button: { padding: '12px 20px', borderRadius: '6px', border: 'none', fontSize: '16px', fontWeight: '500', cursor: 'pointer', width: '100%' },
    buttonPrimary: { backgroundColor: '#0d9488', color: '#fff' },
    buttonSecondary: { backgroundColor: '#f3f4f6', color: '#374151' },
    alert: { padding: '12px 16px', borderRadius: '6px', marginBottom: '12px', fontSize: '14px' },
    alertRed: { backgroundColor: '#fef2f2', color: '#991b1b' },
    label: { display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' },
    pageTitle: { textAlign: 'center', marginBottom: '24px' },
    title: { fontSize: isMobile ? '20px' : '24px', fontWeight: '700', color: '#111827', marginBottom: '8px' },
    textMuted: { color: '#6b7280', fontSize: '14px' },
    loginBox: { maxWidth: '400px', margin: '0 auto', paddingTop: isMobile ? '20px' : '40px' },
    select: { width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '16px', backgroundColor: '#fff', marginBottom: '12px', boxSizing: 'border-box' },
    infoBox: { backgroundColor: '#f0fdfa', border: '1px solid #ccfbf1', borderRadius: '6px', padding: '12px', marginBottom: '16px', fontSize: '13px', color: '#134e4a' },
    pinBox: { backgroundColor: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '12px', marginBottom: '12px' },
  };

  const ID_TYPE_LABELS = {
    resident_id: 'Resident ID',
    national_id: 'National ID Number',
    philsys: 'PhilSys ID',
    student_id: 'Student ID Number',
    passport: 'Passport Number',
    drivers_license: "Driver's License Number",
  };

  const ID_TYPE_PLACEHOLDERS = {
    resident_id: '2026-0001',
    national_id: 'Enter your 12-digit National ID',
    philsys: 'Enter your 12-digit PhilSys ID',
    student_id: 'Enter your student ID',
    passport: 'Enter passport number',
    drivers_license: 'e.g., A1234567',
  };

  const handleLogin = useCallback(async () => {
    console.log('Login button clicked', { idNumber: idNumber.trim(), idType, pin: pin ? '****' : 'empty' });
    if (!idNumber.trim()) {
      setError('Please enter your ID number');
      return;
    }
    if (!pin) {
      setError('Please enter your PIN');
      return;
    }
    if (!/^\d{6}$/.test(pin)) {
      setError('PIN must be exactly 6 digits');
      return;
    }

    setLoading(true);
    setError('');

    try {
      console.log('Sending login request...');
      const res = await fetch(`/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_type: idType, id_number: idNumber.trim(), pin })
      });
      console.log('Response status:', res.status);
      
      let data;
      const contentType = res.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await res.json();
        console.log('Response data:', data);
      } else {
        data = { detail: `Server error: ${res.status}` };
      }
      
      if (!res.ok) {
        if (data.needs_pin_setup) {
          setNeedsPinSetup(true);
          setPinSetupToken(data.token_required);
          setVoterName(data.name || '');
          setError('');
          return;
        }
        throw new Error(data.detail || data.message || `Login failed (${res.status})`);
      }
      
      console.log('Login successful, storing token...');
      login(data.token, { resident_id: data.resident_id, name: data.name, id_type: idType });
      window.location.href = '/voter';
    } catch (err) {
      console.error('Login error:', err);
      if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
        setError('Cannot connect to server. Please check your connection.');
      } else {
        setError(err.message || 'Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [idType, idNumber, pin, login]);

  const handlePinSetup = useCallback(async () => {
    if (!pin) {
      setError('Please enter a PIN');
      return;
    }
    if (!confirmPin) {
      setError('Please confirm your PIN');
      return;
    }
    if (!/^\d{6}$/.test(pin)) {
      setError('PIN must be exactly 6 digits');
      return;
    }
    if (pin !== confirmPin) {
      setError('PINs do not match');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await fetch(`${API_URL}/api/voter/setup-pin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: pinSetupToken,
          id_type: idType,
          id_number: idNumber.trim(),
          new_pin: pin
        })
      });
      
      let data;
      const contentType = res.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await res.json();
      } else {
        data = { detail: `Server error: ${res.status}` };
      }
      
      if (!res.ok) {
        throw new Error(data.detail || data.message || `PIN setup failed (${res.status})`);
      }
      
      login(data.token, { resident_id: data.resident_id, name: data.name, id_type: idType });
    } catch (err) {
      if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
        setError('Cannot connect to server. Please check your connection.');
      } else {
        setError(err.message || 'PIN setup failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [idType, idNumber, pin, confirmPin, pinSetupToken, login]);

  return (
    <div style={styles.container}>
      <div style={styles.loginBox}>
        <div style={styles.pageTitle}>
          <h1 style={styles.title}>Blockchain Voting System</h1>
          <p style={styles.textMuted}>Secure ID-Based Verification</p>
        </div>
        <div style={styles.card}>
          <div style={styles.infoBox}>
            Enter your registered ID and PIN to cast your vote.
          </div>

          <label style={styles.label}>ID Type</label>
          <select
            style={styles.select}
            value={idType}
            onChange={(e) => setIdType(e.target.value)}
            aria-label="ID Type"
          >
            <option value="resident_id">Resident ID</option>
            <option value="national_id">National ID</option>
            <option value="philsys">PhilSys ID</option>
            <option value="student_id">Student ID</option>
            <option value="passport">Passport</option>
            <option value="drivers_license">Driver's License</option>
          </select>

          <label style={styles.label}>
            {ID_TYPE_LABELS[idType] || 'ID Number'}
          </label>
          <input
            style={styles.input}
            placeholder={ID_TYPE_PLACEHOLDERS[idType] || 'Enter ID number'}
            value={idNumber}
            onChange={(e) => setIdNumber(e.target.value)}
            aria-label="ID Number"
          />

          <div style={styles.pinBox}>
            <label style={styles.label}>6-digit PIN</label>
            <input
              type={showPin ? 'text' : 'password'}
              style={styles.input}
              placeholder="Enter your PIN"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 6))}
              maxLength={6}
              onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
              aria-label="PIN"
            />
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px', marginTop: '8px' }}>
              <input
                type="checkbox"
                checked={showPin}
                onChange={(e) => setShowPin(e.target.checked)}
              />
              Show PIN
            </label>
          </div>
          
          {error && <div style={{ ...styles.alert, ...styles.alertRed }} role="alert">{error}</div>}
          
          <button
            type="button"
            style={{ ...styles.button, ...styles.buttonPrimary, marginTop: '8px' }}
            onClick={handleLogin}
            disabled={loading}
            aria-busy={loading}
          >
            {loading ? 'Signing in...' : 'Sign In to Vote'}
          </button>
          
          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <p style={{ color: '#6b7280', fontSize: '13px', marginBottom: '12px' }}>
              Not registered yet?
            </p>
            <button
              style={{ ...styles.button, ...styles.buttonSecondary }}
              onClick={() => window.location.href = '/register'}
            >
              Register to Vote
            </button>
          </div>
        </div>

        {needsPinSetup && (
          <div style={styles.card}>
            <div style={styles.pageTitle}>
              <h2 style={styles.title}>Set Your PIN</h2>
              <p style={styles.textMuted}>
                Welcome, {voterName}! Set your 6-digit PIN to complete registration.
              </p>
            </div>
            
            <div style={{ ...styles.alert, backgroundColor: '#f0fdfa', color: '#134e4a', marginBottom: '16px' }}>
              This is your first login. Please set your desired 6-digit PIN.
            </div>

            <div style={styles.pinBox}>
              <label style={styles.label}>6-digit PIN</label>
              <input
                type={showPin ? 'text' : 'password'}
                style={styles.input}
                placeholder="Enter your desired PIN"
                value={pin}
                onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 6))}
                maxLength={6}
                aria-label="New PIN"
              />
            </div>

            <div style={styles.pinBox}>
              <label style={styles.label}>Confirm PIN</label>
              <input
                type={showPin ? 'text' : 'password'}
                style={styles.input}
                placeholder="Confirm your PIN"
                value={confirmPin}
                onChange={(e) => setConfirmPin(e.target.value.replace(/\D/g, '').slice(0, 6))}
                maxLength={6}
                onKeyDown={(e) => e.key === 'Enter' && handlePinSetup()}
                aria-label="Confirm PIN"
              />
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px', marginTop: '8px' }}>
                <input
                  type="checkbox"
                  checked={showPin}
                  onChange={(e) => setShowPin(e.target.checked)}
                />
                Show PIN
              </label>
            </div>

            {error && <div style={{ ...styles.alert, ...styles.alertRed }} role="alert">{error}</div>}

            <button
              style={{ ...styles.button, ...styles.buttonPrimary, marginTop: '8px' }}
              onClick={handlePinSetup}
              disabled={loading}
              aria-busy={loading}
            >
              {loading ? 'Setting PIN...' : 'Set PIN'}
            </button>

            <div style={{ textAlign: 'center', marginTop: '16px' }}>
              <button
                style={{ background: 'transparent', color: '#6b7280', border: 'none', fontSize: '13px', cursor: 'pointer' }}
                onClick={() => {
                  setNeedsPinSetup(false);
                  setPin('');
                  setConfirmPin('');
                  setError('');
                }}
              >
                ← Back to Login
              </button>
            </div>
          </div>
        )}

        <div style={{ textAlign: 'center', marginTop: '20px' }}>
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              style={{ background: 'transparent', color: '#dc2626', border: 'none', fontSize: '13px', cursor: 'pointer', padding: '8px', fontWeight: '500' }}
              onClick={() => window.location.href = '/admin-login'}
            >
              Admin
            </button>
            <button
              style={{ background: 'transparent', color: '#0d9488', border: 'none', fontSize: '13px', cursor: 'pointer', padding: '8px', fontWeight: '500' }}
              onClick={() => window.location.href = '/officials-login'}
            >
              Officials
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

LoginPage.propTypes = {
  onSwitchPage: PropTypes.func.isRequired,
};