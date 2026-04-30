import React from 'react';
import PropTypes from 'prop-types';

const styles = {
  container: {
    position: 'fixed',
    top: '20px',
    right: '20px',
    zIndex: 9999,
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    maxWidth: '400px',
  },
  toast: {
    padding: '12px 16px',
    borderRadius: '6px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    cursor: 'pointer',
    animation: 'slideIn 0.3s ease-out',
    fontSize: '14px',
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
  },
  success: {
    backgroundColor: '#dcfce7',
    color: '#166534',
    borderLeft: '4px solid #22c55e',
  },
  error: {
    backgroundColor: '#fee2e2',
    color: '#991b1b',
    borderLeft: '4px solid #ef4444',
  },
  warning: {
    backgroundColor: '#fef3c7',
    color: '#92400e',
    borderLeft: '4px solid #f59e0b',
  },
  info: {
    backgroundColor: '#e0f2fe',
    color: '#075985',
    borderLeft: '4px solid #3b82f6',
  },
  closeButton: {
    position: 'absolute',
    right: '8px',
    top: '8px',
    background: 'transparent',
    border: 'none',
    fontSize: '18px',
    cursor: 'pointer',
    opacity: 0.6,
    lineHeight: 1,
  },
};

const toastStyles = {
  success: styles.success,
  error: styles.error,
  warning: styles.warning,
  info: styles.info,
};

export function ToastContainer({ toasts, onRemove }) {
  if (toasts.length === 0) return null;

  return (
    <div style={styles.container} role="region" aria-label="Notifications">
      <style>
        {`
          @keyframes slideIn {
            from {
              transform: translateX(100%);
              opacity: 0;
            }
            to {
              transform: translateX(0);
              opacity: 1;
            }
          }
        `}
      </style>
      {toasts.map(toast => (
        <div
          key={toast.id}
          style={{
            ...styles.toast,
            ...toastStyles[toast.type] || toastStyles.info,
            position: 'relative',
          }}
          onClick={() => onRemove(toast.id)}
          role="alert"
          aria-live="polite"
        >
          {toast.message}
          <button
            style={styles.closeButton}
            onClick={(e) => {
              e.stopPropagation();
              onRemove(toast.id);
            }}
            aria-label="Dismiss notification"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}

ToastContainer.propTypes = {
  toasts: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      message: PropTypes.string.isRequired,
      type: PropTypes.oneOf(['success', 'error', 'warning', 'info']).isRequired,
    })
  ).isRequired,
  onRemove: PropTypes.func.isRequired,
};