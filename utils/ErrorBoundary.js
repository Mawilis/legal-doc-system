// ~/legal-doc-system/utils/ErrorBoundary.js

import React from 'react';
import PropTypes from 'prop-types';

/**
 * ErrorBoundary is a React component that catches JavaScript errors anywhere
 * in its child component tree, logs those errors, and displays a fallback UI.
 *
 * This helps prevent the entire app from crashing due to uncaught errors.
 */
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        // Initialize state to track error status and details.
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
        };
    }

    /**
     * getDerivedStateFromError is a lifecycle method that updates the state
     * so the next render shows the fallback UI.
     *
     * @param {Error} error - The error thrown by a descendant component.
     * @returns {Object} Updated state with hasError set to true.
     */
    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    /**
     * componentDidCatch is invoked after an error has been thrown by a descendant.
     * Here, you can log error information and update the state with details.
     *
     * @param {Error} error - The error thrown.
     * @param {Object} errorInfo - An object with a componentStack key containing information about which component threw the error.
     */
    componentDidCatch(error, errorInfo) {
        // Update state with error details.
        this.setState({ error, errorInfo });

        // Log the error details to the console.
        console.error("ErrorBoundary caught an error", error, errorInfo);

        // Example: Send error details to an error reporting endpoint.
        // Adjust the URL and payload as needed for your logging service.
        if (typeof window !== "undefined" && window.navigator && window.navigator.sendBeacon) {
            try {
                window.navigator.sendBeacon(
                    "/api/logError",
                    JSON.stringify({
                        message: error.message,
                        stack: error.stack,
                        componentStack: errorInfo.componentStack,
                    })
                );
            } catch (loggingError) {
                console.error("Failed to send error log beacon", loggingError);
            }
        }
    }

    /**
     * handleResetError resets the error state.
     *
     * You can choose to either reload the page or attempt to recover
     * by resetting the error state.
     */
    handleResetError = () => {
        // Option 1: Reload the page to try a full recovery:
        // window.location.reload();

        // Option 2: Reset the error state so that child components re-render.
        this.setState({ hasError: false, error: null, errorInfo: null });
    };

    render() {
        const { hasError, error, errorInfo } = this.state;

        // If an error was caught, display the fallback UI.
        if (hasError) {
            return (
                <div style={styles.fallbackContainer}>
                    <h2 style={styles.header}>Oops, something went wrong.</h2>
                    <p style={styles.message}>
                        We're sorry for the inconvenience. Please try refreshing the page or click the button below to attempt recovery.
                    </p>
                    <details style={styles.details}>
                        <summary>Error Details</summary>
                        <div style={styles.errorDetails}>
                            {error && error.toString()}
                            <br />
                            {errorInfo && errorInfo.componentStack}
                        </div>
                    </details>
                    <button style={styles.resetButton} onClick={this.handleResetError}>
                        Try Again
                    </button>
                </div>
            );
        }

        // If no error occurred, render the child components as usual.
        return this.props.children;
    }
}

// Inline styles for the fallback UI.
const styles = {
    fallbackContainer: {
        padding: '20px',
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#f5f5f5',
    },
    header: {
        fontSize: '1.8rem',
        marginBottom: '10px',
        color: '#d32f2f',
    },
    message: {
        fontSize: '1rem',
        marginBottom: '20px',
        color: '#333',
    },
    details: {
        whiteSpace: 'pre-wrap',
        marginBottom: '20px',
        textAlign: 'left',
        maxWidth: '80%',
        backgroundColor: '#fff',
        padding: '10px',
        borderRadius: '4px',
        border: '1px solid #ccc',
    },
    errorDetails: {
        fontSize: '0.9rem',
        color: '#555',
    },
    resetButton: {
        marginTop: '20px',
        padding: '10px 20px',
        fontSize: '1rem',
        borderRadius: '4px',
        border: 'none',
        cursor: 'pointer',
        backgroundColor: '#0d47a1',
        color: '#fff',
    },
};

// Prop type validation for the component's children.
ErrorBoundary.propTypes = {
    children: PropTypes.node.isRequired,
};

export default ErrorBoundary;
