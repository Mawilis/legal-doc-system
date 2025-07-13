// /src/index.js
import React from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { BrowserRouter } from 'react-router-dom';
import { SnackbarProvider } from 'notistack';
import { ThemeProvider as MUIThemeProvider, createTheme } from '@mui/material/styles';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { store, persistor } from './store';
import CircularProgress from '@mui/material/CircularProgress';

// Create a unified theme for both providers
const theme = createTheme({
    palette: {
        primary: { main: '#0d47a1' },
        secondary: { main: '#9e9e9e' },
        background: { default: '#f5f5f5', paper: '#ffffff' },
        text: { primary: '#212121', secondary: '#757575' },
        error: { main: '#d32f2f' },
    },
    typography: {
        fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    },
    components: {
        MuiButton: { styleOverrides: { root: { textTransform: 'none' } } },
        MuiPaper: { styleOverrides: { root: { padding: '20px', boxShadow: '0px 2px 4px rgba(0,0,0,0.1)' } } },
    },
});

// Fallback loading component used by PersistGate
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
        <CircularProgress color="primary" />
    </div>
);

// A simple error boundary to catch errors in the component tree
class RootErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }
    static getDerivedStateFromError() {
        return { hasError: true };
    }
    componentDidCatch(error, errorInfo) {
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

root.render(
    <Provider store={store}>
        <PersistGate loading={<Loading />} persistor={persistor}>
            <BrowserRouter>
                <SnackbarProvider
                    maxSnack={3}
                    anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
                    autoHideDuration={4000}
                >
                    {/* Wrap the entire app with both providers */}
                    <StyledThemeProvider theme={theme}>
                        <MUIThemeProvider theme={theme}>
                            <RootErrorBoundary>
                                <App />
                            </RootErrorBoundary>
                        </MUIThemeProvider>
                    </StyledThemeProvider>
                </SnackbarProvider>
            </BrowserRouter>
        </PersistGate>
    </Provider>
);

reportWebVitals(console.log);
