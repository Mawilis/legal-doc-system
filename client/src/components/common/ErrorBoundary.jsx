import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ error, errorInfo });
    console.error("🔥 [ErrorBoundary] Caught crash:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          backgroundColor: '#f8f9fa',
          color: '#333',
          fontFamily: 'Segoe UI, sans-serif',
          textAlign: 'center',
          padding: '2rem'
        }}>
          <h1 style={{ color: '#d32f2f', marginBottom: '1rem' }}>Something went wrong.</h1>
          <p style={{ maxWidth: '600px', marginBottom: '2rem', color: '#555' }}>
            The application encountered an unexpected error. We have logged this issue.
          </p>
          <button 
            onClick={() => window.location.href = '/dashboard'}
            style={{
              padding: '12px 24px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '1rem'
            }}
          >
            Return to Dashboard
          </button>
          
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details style={{ marginTop: '2rem', textAlign: 'left', background: '#eee', padding: '1rem', borderRadius: '8px', maxWidth: '800px', overflow: 'auto' }}>
              <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>View Error Details</summary>
              <pre style={{ marginTop: '10px', fontSize: '0.85rem' }}>
                {this.state.error.toString()}
                <br />
                {this.state.errorInfo?.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
