// ~/legal-doc-system/client/src/components/ErrorBoundary.jsx

import React from 'react';
import styled from 'styled-components';

const ErrorContainer = styled.div`
  padding: var(--spacing-lg);
  text-align: center;
  color: var(--error-color);
`;

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        // You can log the error to an error reporting service here
        console.error('ErrorBoundary caught an error', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return <ErrorContainer>Something went wrong.</ErrorContainer>;
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
