// ~/legal-doc-system/client/src/index.js
import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import ErrorBoundary from './components/ErrorBoundary';

// Check if the root container exists
const container = document.getElementById('root');
if (container) {
    const root = createRoot(container);

    root.render(
        <React.StrictMode>
            <ErrorBoundary>
                <BrowserRouter>
                    <App />
                </BrowserRouter>
            </ErrorBoundary>
        </React.StrictMode>
    );
} else {
    console.error('Root container not found!');
}
