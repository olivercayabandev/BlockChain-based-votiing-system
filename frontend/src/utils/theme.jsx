export const theme = {
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
    text: '#1e293b',
    textMuted: '#64748b',
    border: '#e2e8f0',
  },
  fonts: {
    primary: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
    mono: 'JetBrains Mono, monospace',
  },
  borderRadius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  },
};

export const getButtonStyles = (variant = 'primary') => {
  const base = {
    padding: '10px 20px',
    borderRadius: theme.borderRadius.md,
    border: 'none',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  };
  
  const variants = {
    primary: {
      backgroundColor: theme.colors.primary,
      color: '#ffffff',
    },
    secondary: {
      backgroundColor: '#f1f5f9',
      color: theme.colors.text,
    },
    accent: {
      backgroundColor: theme.colors.accent,
      color: '#ffffff',
    },
    danger: {
      backgroundColor: theme.colors.error,
      color: '#ffffff',
    },
    outline: {
      backgroundColor: 'transparent',
      color: theme.colors.primary,
      border: `2px solid ${theme.colors.primary}`,
    },
  };
  
  return { ...base, ...variants[variant] };
};

export const getCardStyles = () => {
  return {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    border: `1px solid ${theme.colors.border}`,
    padding: '20px',
    boxShadow: theme.shadows.sm,
  };
};

export const getInputStyles = () => {
  return {
    width: '100%',
    padding: '12px',
    borderRadius: theme.borderRadius.md,
    border: `1px solid ${theme.colors.border}`,
    fontSize: '16px',
    backgroundColor: theme.colors.surface,
    outline: 'none',
    transition: 'border-color 0.2s ease',
  };
};

export default theme;