import React from 'react';
import PropTypes from 'prop-types';

const styles = {
  container: {
    maxWidth: '600px',
    margin: '0 auto',
    padding: '40px 20px',
    textAlign: 'center',
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    border: '1px solid #e5e7eb',
    padding: '40px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  title: {
    fontSize: '24px',
    fontWeight: '700',
    color: '#dc2626',
    marginBottom: '16px',
  },
  text: {
    fontSize: '14px',
    color: '#6b7280',
    marginBottom: '24px',
  },
  button: {
    padding: '10px 20px',
    borderRadius: '6px',
    border: 'none',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    backgroundColor: '#0d9488',
    color: '#fff',
  },
  errorDetails: {
    marginTop: '16px',
    padding: '12px',
    backgroundColor: '#fef2f2',
    borderRadius: '6px',
    textAlign: 'left',
    fontSize: '12px',
    fontFamily: 'monospace',
    color: '#991b1b',
    wordBreak: 'break-all',
  },
};

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }
  }

  handleReload = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  handleGoHome = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    localStorage.removeItem('voting-token');
    localStorage.removeItem('voting-user');
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={styles.container}>
          <div style={styles.card}>
            <h1 style={styles.title}>Something went wrong</h1>
            <p style={styles.text}>
              We're sorry, but something unexpected happened. Please try refreshing the page or contact support if the problem persists.
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button style={styles.button} onClick={this.handleReload}>
                Reload Page
              </button>
              <button
                style={{ ...styles.button, backgroundColor: '#6b7280' }}
                onClick={this.handleGoHome}
              >
                Go to Home
              </button>
            </div>
            {import.meta.env.DEV && this.state.error && (
              <div style={styles.errorDetails}>
                <strong>Error:</strong> {this.state.error.toString()}
                {this.state.errorInfo?.componentStack && (
                  <>
                    <br /><strong>Component Stack:</strong>
                    <pre style={{ margin: '8px 0 0 0', whiteSpace: 'pre-wrap' }}>
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,
};