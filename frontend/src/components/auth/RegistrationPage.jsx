import React, { useState, useCallback, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

const API_URL = '';

export function RegistrationPage({ onSwitchPage }) {
  const [formData, setFormData] = useState({
    resident_id: '',
    name: '',
    id_type: '',
    id_number: '',
    id_photo_front: '',
    consent_given: false
  });
  const [pin, setPin] = useState('');
  const [confirmPin, setConfirmPin] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPin, setShowPin] = useState(false);
  const [pinDisplay, setPinDisplay] = useState('');
  const [idPhotoFront, setIdPhotoFront] = useState(null);
  const fileInputRef = useRef(null);

  const updateField = useCallback((field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (field === 'id_type') {
      setFormData(prev => ({ ...prev, id_number: '' }));
    }
  }, []);

  const handlePhotoUpload = useCallback((e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      setError('Image too large. Max 5MB.');
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64 = reader.result.split(',')[1];
      setFormData(prev => ({ ...prev, id_photo_front: base64 }));
      setIdPhotoFront(reader.result);
    };
    reader.readAsDataURL(file);
  }, []);

  const handleSubmit = useCallback(async () => {
    setError('');

    if (!formData.resident_id.trim()) {
      setError('Resident ID is required');
      return;
    }
    if (!formData.name.trim()) {
      setError('Full name is required');
      return;
    }
    if (!formData.id_type) {
      setError('Please select ID type');
      return;
    }
    if (!formData.id_number.trim()) {
      setError('ID number is required');
      return;
    }
    if (!pin) {
      setError('PIN is required');
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
    if (!formData.consent_given) {
      setError('You must agree to the Data Privacy Act consent');
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, pin })
      });
      
      let data;
      const contentType = res.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await res.json();
      } else {
        data = { detail: `Server error: ${res.status}` };
      }
      
      if (!res.ok) {
        throw new Error(data.detail || data.message || `Registration failed (${res.status})`);
      }
      
      setSuccess(data.message);
      setPinDisplay(pin);
      setTimeout(() => {
        onSwitchPage('login');
      }, 5000);
    } catch (err) {
      if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
        setError('Cannot connect to server. Please check your connection.');
      } else {
        setError(err.message || 'Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [formData, pin, confirmPin, onSwitchPage]);

  const styles = {
    container: { maxWidth: '100%', margin: '0 auto', padding: '16px', fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif' },
    loginBox: { maxWidth: '500px', margin: '0 auto', paddingTop: '20px', paddingBottom: '20px' },
    card: { backgroundColor: '#fff', borderRadius: '8px', borderWidth: '1px', borderStyle: 'solid', borderColor: '#e5e7eb', paddingTop: '20px', paddingBottom: '20px', paddingLeft: '16px', paddingRight: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' },
    input: { width: '100%', paddingTop: '10px', paddingBottom: '10px', paddingLeft: '12px', paddingRight: '12px', borderRadius: '6px', borderWidth: '1px', borderStyle: 'solid', borderColor: '#d1d5db', fontSize: '14px', marginBottom: '12px', outline: 'none', boxSizing: 'border-box' },
    button: { paddingTop: '10px', paddingBottom: '10px', paddingLeft: '20px', paddingRight: '20px', borderRadius: '6px', border: 'none', fontSize: '14px', fontWeight: '500', cursor: 'pointer', width: '100%' },
    buttonPrimary: { backgroundColor: '#0d9488', color: '#fff' },
    buttonSecondary: { backgroundColor: '#f3f4f6', color: '#374151' },
    alert: { paddingTop: '12px', paddingBottom: '12px', paddingLeft: '16px', paddingRight: '16px', borderRadius: '6px', marginBottom: '12px', fontSize: '14px' },
    alertRed: { backgroundColor: '#fef2f2', color: '#991b1b' },
    alertGreen: { backgroundColor: '#f0fdf4', color: '#166534' },
    alertTeal: { backgroundColor: '#f0fdfa', border: '1px solid #ccfbf1', color: '#134e4a' },
    label: { display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' },
    pageTitle: { textAlign: 'center', marginBottom: '24px' },
    title: { fontSize: '20px', fontWeight: '700', color: '#111827', marginBottom: '8px' },
    textMuted: { color: '#6b7280', fontSize: '14px' },
    select: { width: '100%', paddingTop: '10px', paddingBottom: '10px', paddingLeft: '12px', paddingRight: '12px', borderRadius: '6px', borderWidth: '1px', borderStyle: 'solid', borderColor: '#d1d5db', fontSize: '14px', marginBottom: '12px', backgroundColor: '#fff' },
    fileInput: { display: 'none' },
    photoPreview: { width: '100%', maxHeight: '150px', objectFit: 'contain', borderRadius: '8px', border: '1px solid #e5e7eb', marginBottom: '12px' },
    photoLabel: { display: 'block', paddingTop: '12px', paddingBottom: '12px', paddingLeft: '16px', paddingRight: '16px', borderRadius: '6px', borderWidth: '1px', borderStyle: 'dashed', borderColor: '#d1d5db', textAlign: 'center', cursor: 'pointer', fontSize: '14px', color: '#6b7280', marginBottom: '12px' },
    row: { display: 'flex', gap: '12px', flexWrap: 'wrap' },
    col: { flex: 1, minWidth: '200px' },
    pinBox: { backgroundColor: '#fef3c7', border: '1px solid #fcd34d', borderRadius: '8px', padding: '16px', marginBottom: '16px' },
    pinDisplay: { fontSize: '32px', fontWeight: '700', letterSpacing: '8px', textAlign: 'center', color: '#92400e', marginTop: '8px' },
    warning: { fontSize: '12px', color: '#92400e', marginTop: '12px', textAlign: 'center' },
  };

  const ID_TYPES = [
    { value: 'philsys', label: 'Philippine Identification Card (PhilSys)' },
    { value: 'student_id', label: 'Student ID' },
    { value: 'drivers_license', label: "Driver's License" },
    { value: 'passport', label: 'Passport' },
    { value: 'senior_citizen', label: 'Senior Citizen ID' },
    { value: 'pwd', label: 'PWD ID' },
    { value: 'barangay_id', label: 'Barangay ID' },
  ];

  const ID_HINTS = {
    philsys: '12 digits (e.g., 123456789012)',
    student_id: 'Your student ID number',
    drivers_license: 'Letters + 7-8 digits (e.g., A1234567)',
    passport: 'Letter + 8 digits (e.g., P12345678)',
    senior_citizen: 'Your ID number',
    pwd: 'Your ID number',
    barangay_id: 'Your ID number',
  };

  if (success && pinDisplay) {
    return (
      <div style={styles.container}>
        <div style={styles.loginBox}>
          <div style={styles.card}>
            <div style={styles.pageTitle}>
              <h1 style={styles.title}>Registration Complete!</h1>
            </div>
            
            <div style={styles.pinBox}>
              <p style={{ margin: '0 0 8px 0', textAlign: 'center', color: '#92400e' }}>
                Your 6-digit PIN is:
              </p>
              <div style={styles.pinDisplay}>{pinDisplay}</div>
              <p style={styles.warning}>
                Write this down! You will need this to vote.
                <br/>Keep it secret and safe.
              </p>
            </div>
            
            <div style={{ ...styles.alert, ...styles.alertTeal, textAlign: 'center' }}>
              <strong>Wait for official approval</strong>
              <br/>
              <span style={{ fontSize: '14px' }}>
                Your registration is pending verification by election officials.
                You will be able to vote once approved.
              </span>
            </div>
            
            <p style={{ textAlign: 'center', color: '#6b7280', fontSize: '13px' }}>
              Redirecting to login in 5 seconds...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.loginBox}>
        <div style={styles.pageTitle}>
          <h1 style={styles.title}>Voter Registration</h1>
          <p style={styles.textMuted}>Submit your ID for verification</p>
        </div>
        <div style={styles.card}>
          <div style={styles.row}>
            <div style={styles.col}>
              <label style={styles.label}>Resident ID *</label>
              <input
                style={styles.input}
                placeholder="e.g., 2026-0001"
                value={formData.resident_id}
                onChange={(e) => updateField('resident_id', e.target.value)}
                aria-label="Resident ID"
              />
            </div>
            <div style={styles.col}>
              <label style={styles.label}>Full Name *</label>
              <input
                style={styles.input}
                placeholder="Enter your full name"
                value={formData.name}
                onChange={(e) => updateField('name', e.target.value)}
                aria-label="Full Name"
              />
            </div>
          </div>

          <label style={styles.label}>ID Type *</label>
          <select
            style={styles.select}
            value={formData.id_type}
            onChange={(e) => updateField('id_type', e.target.value)}
            aria-label="ID Type"
          >
            <option value="">Select ID Type</option>
            {ID_TYPES.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>

          <label style={styles.label}>ID Number *</label>
          <input
            style={styles.input}
            placeholder={formData.id_type ? ID_HINTS[formData.id_type] : 'Select ID type first'}
            value={formData.id_number}
            onChange={(e) => updateField('id_number', e.target.value.toUpperCase())}
            aria-label="ID Number"
            disabled={!formData.id_type}
          />

          <div style={{ ...styles.pinBox, backgroundColor: '#f0fdfa', borderColor: '#0d9488' }}>
            <label style={styles.label}>Set Your 6-digit PIN *</label>
            <input
              type={showPin ? 'text' : 'password'}
              style={styles.input}
              placeholder="Enter 6-digit PIN"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 6))}
              maxLength={6}
              aria-label="PIN"
            />
            <input
              type={showPin ? 'text' : 'password'}
              style={styles.input}
              placeholder="Confirm PIN"
              value={confirmPin}
              onChange={(e) => setConfirmPin(e.target.value.replace(/\D/g, '').slice(0, 6))}
              maxLength={6}
              aria-label="Confirm PIN"
            />
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px' }}>
              <input
                type="checkbox"
                checked={showPin}
                onChange={(e) => setShowPin(e.target.checked)}
              />
              Show PIN
            </label>
            <p style={{ fontSize: '12px', color: '#0f766e', marginTop: '8px' }}>
              <strong>Important:</strong> You will need this PIN to vote. Write it down and keep it safe!
            </p>
          </div>

          <label style={styles.label}>ID Photo (Front) - Optional</label>
          <input
            type="file"
            accept="image/*"
            capture="environment"
            style={styles.fileInput}
            ref={fileInputRef}
            onChange={handlePhotoUpload}
          />
          {!idPhotoFront ? (
            <div style={styles.photoLabel} onClick={() => fileInputRef.current?.click()}>
              Tap to capture or upload ID photo
            </div>
          ) : (
            <div>
              <img src={idPhotoFront} alt="ID Preview" style={styles.photoPreview} />
              <button
                style={{ ...styles.button, ...styles.buttonSecondary, fontSize: '12px', padding: '6px 12px' }}
                onClick={() => {
                  setIdPhotoFront(null);
                  setFormData(prev => ({ ...prev, id_photo_front: '' }));
                }}
              >
                Remove Photo
              </button>
            </div>
          )}

          <label style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', cursor: 'pointer', marginTop: '12px', marginBottom: '12px' }}>
            <input
              type="checkbox"
              checked={formData.consent_given}
              onChange={(e) => updateField('consent_given', e.target.checked)}
              style={{ marginTop: '4px' }}
              aria-label="Data Privacy Act Consent"
            />
            <span style={{ fontSize: '14px', color: '#374151' }}>
              I agree to the Data Privacy Act (R.A. 10173) consent and confirm that all information provided is accurate.
            </span>
          </label>

          {error && <div style={{ ...styles.alert, ...styles.alertRed }} role="alert">{error}</div>}

          <button
            style={{ ...styles.button, ...styles.buttonPrimary }}
            onClick={handleSubmit}
            disabled={loading}
            aria-busy={loading}
          >
            {loading ? 'Registering...' : 'Register & Set PIN'}
          </button>

          <button
            style={{ ...styles.button, ...styles.buttonSecondary, marginTop: '12px' }}
            onClick={() => onSwitchPage('login')}
          >
            Back to Login
          </button>
        </div>
      </div>
    </div>
  );
}

RegistrationPage.propTypes = {
  onSwitchPage: PropTypes.func.isRequired,
};