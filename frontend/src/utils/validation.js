const API_URL = import.meta.env.VITE_API_URL || '';

export function validateResidentId(id) {
  if (!id || id.trim().length === 0) return 'Resident ID is required';
  if (id.length < 3) return 'Resident ID must be at least 3 characters';
  return null;
}

export function validatePhoneNumber(phone) {
  if (!phone || phone.trim().length === 0) return 'Phone number is required';
  const phoneRegex = /^\+63\s?\d{3}\s?\d{3}\s?\d{4}$/;
  if (!phoneRegex.test(phone)) return 'Please enter a valid Philippine phone number (+63 XXX XXX XXXX)';
  return null;
}

export function validateName(name) {
  if (!name || name.trim().length === 0) return 'Name is required';
  if (name.length < 2) return 'Name must be at least 2 characters';
  return null;
}

export function validateOtp(otp) {
  if (!otp || otp.trim().length === 0) return 'OTP code is required';
  if (!/^\d{6}$/.test(otp)) return 'OTP must be a 6-digit code';
  return null;
}

export function validateCandidate(candidate) {
  const errors = [];
  if (!candidate.candidate_id || candidate.candidate_id.trim().length === 0) {
    errors.push('Candidate ID is required');
  }
  if (!candidate.name || candidate.name.trim().length === 0) {
    errors.push('Candidate name is required');
  }
  if (!candidate.position_id) {
    errors.push('Position is required');
  }
  return errors;
}

export function validatePosition(position) {
  const errors = [];
  if (!position.title || position.title.trim().length === 0) {
    errors.push('Position title is required');
  }
  if (position.max_votes && position.max_votes < 1) {
    errors.push('Max votes must be at least 1');
  }
  return errors;
}

export { API_URL };
