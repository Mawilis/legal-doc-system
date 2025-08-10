// ~/client/src/index.js

import React from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { store, persistor } from './store';
import { ThemeProvider } from './context/ThemeContext';
import { NotificationProvider } from './context/NotificationContext'; // ✅ Import our custom provider
import GlobalStyle from './GlobalStyle';
import LoadingSpinner from './components/LoadingSpinner'; // Assuming a custom spinner

/**
 * A simple loading component displayed while the persisted Redux state is rehydrated.
 */
const Loading = () => (
    <div
        style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
        }}
        aria-label="Loading application"
        role="alert"
    >
        <LoadingSpinner />
    </div>
);

/**
 * A root-level error boundary to catch rendering errors anywhere in the app
 * and display a safe fallback UI instead of a blank page.
 */
class RootErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }
    static getDerivedStateFromError() {
        return { hasError: true };
    }
    componentDidCatch(error, errorInfo) {
        // In a real application, you would log this error to a service like Sentry or LogRocket
        console.error('RootErrorBoundary caught an error:', error, errorInfo);
    }
    render() {
        if (this.state.hasError) {
            return (
                <div
                    style={{
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center',
                        alignItems: 'center',
                        height: '100vh',
                        textAlign: 'center',
                        padding: '1rem',
                    }}
                >
                    <h1>Something went wrong</h1>
                    <p>Please refresh the page or try again later.</p>
                </div>
            );
        }
        return this.props.children;
    }
}

const container = document.getElementById('root');
const root = createRoot(container);

// --- Render the Application ---
// The component tree is wrapped in all necessary providers for state management,
// routing, theming, and notifications.
root.render(
    <Provider store={store}>
        <PersistGate loading={<Loading />} persistor={persistor}>
            <BrowserRouter>
                <ThemeProvider>
                    {/* ✅ Our custom NotificationProvider now wraps the entire app */}
                    <NotificationProvider>
                        <GlobalStyle />
                        <RootErrorBoundary>
                            <App />
                        </RootErrorBoundary>
                    </NotificationProvider>
                </ThemeProvider>
            </BrowserRouter>
        </PersistGate>
    </Provider>
);

// Optional: for measuring performance
reportWebVitals();
