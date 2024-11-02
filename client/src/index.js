// ~/legal-doc-system/client/src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import store, { persistor } from './store';
import App from './App';
import { ThemeProvider } from 'styled-components';
import GlobalStyles from './theme/globalStyles';
import theme from './theme/theme';

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
    <React.StrictMode>
        <Provider store={store}>
            <PersistGate loading={null} persistor={persistor}>
                <ThemeProvider theme={theme}>
                    <GlobalStyles />
                    <App />
                </ThemeProvider>
            </PersistGate>
        </Provider>
    </React.StrictMode>
);
