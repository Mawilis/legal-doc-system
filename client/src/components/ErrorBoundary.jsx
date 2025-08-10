// ~/legal-doc-system/client/src/components/ErrorBoundary.jsx

import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import Button from './atoms/Button'; // Use our masterpiece Button for consistency

// --- Styled Components for the Fallback UI ---

const FallbackContainer = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 2rem;
  text-align: center;
  background-color: ${({ theme }) => theme.colors.background || '#f9f9f9'};
`;

const ErrorHeader = styled.h2`
  font-size: 2rem;
  margin-bottom: 1rem;
  color: ${({ theme }) => theme.colors.danger || '#dc3545'};
`;

const ErrorMessage = styled.p`
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  color: ${({ theme }) => theme.colors.textSecondary || '#555'};
  max-width: 600px;
`;

const DetailsWrapper = styled.details`
  white-space: pre-wrap;
  margin-bottom: 1.5rem;
  text-align: left;
  max-width: 80%;
  background-color: #fff;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid ${({ theme }) => theme.colors.border || '#e0e0e0'};
  cursor: pointer;

  summary {
    font-weight: 500;
  }
`;

const ErrorDetails = styled.div`
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid ${({ theme }) => theme.colors.border || '#e0e0e0'};
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.textMuted || '#6c757d'};
  max-height: 200px;
  overflow-y: auto;
`;

/**
 * ErrorBoundary is a React component that catches JavaScript errors
 * anywhere in its child component tree, logs those errors, and displays
 * a polished fallback UI to prevent the entire app from crashing.
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
     * This lifecycle method is used to update the state so the next render
     * will show the fallback UI.
     */
    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    /**
     * This lifecycle method is invoked after an error has been thrown.
     * It's used for side effects, like logging the error.
     */
    componentDidCatch(error, errorInfo) {
        this.setState({ error, errorInfo });

        // Log the error details to the console for debugging
        console.error("ErrorBoundary caught an error:", error, errorInfo);

        // In a production environment, you would send this to a logging service
        // For example: logErrorToMyService(error, errorInfo);
    }

    /**
     * Resets the error state, allowing the user to try rendering the content again.
     */
    handleResetError = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    };

    render() {
        const { hasError, error, errorInfo } = this.state;

        // If an error was caught, display the fallback UI.
        if (hasError) {
            return (
                <FallbackContainer>
                    <ErrorHeader>Oops, Something Went Wrong</ErrorHeader>
                    <ErrorMessage>
                        We're sorry for the inconvenience. Please try refreshing the page or click the button below to attempt recovery.
                    </ErrorMessage>
                    <DetailsWrapper>
                        <summary>Error Details</summary>
                        <ErrorDetails>
                            {error && error.toString()}
                            <br />
                            {errorInfo && errorInfo.componentStack}
                        </ErrorDetails>
                    </DetailsWrapper>
                    <Button variant="primary" onClick={this.handleResetError}>
                        Try Again
                    </Button>
                </FallbackContainer>
            );
        }

        // Otherwise, render the children components as normal.
        return this.props.children;
    }
}

// Prop type validation for the component's children.
ErrorBoundary.propTypes = {
    children: PropTypes.node.isRequired,
};

export default ErrorBoundary;
