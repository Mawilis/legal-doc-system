// src/components/ErrorBoundary.jsx (or src/ErrorBoundary.js, depending on where you place it)

import React, { Component } from 'react';

class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        // Log the error to an error reporting service if needed
        console.error('Error occurred:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            // Render fallback UI
            return <h1>Something went wrong. Please try again later.</h1>;
        }

        // If no error, render children
        return this.props.children;
    }
}

export default ErrorBoundary;
