// src/index.js

import React from 'react';
import { createRoot } from 'react-dom/client'; // Updated for React 18+
import './index.css';
import App from './App';
import { BrowserRouter as Router } from 'react-router-dom';
import { io } from 'socket.io-client';
import ErrorBoundary from './utils/ErrorBoundary'; // Corrected import path for ErrorBoundary
import * as serviceWorkerRegistration from './serviceWorkerRegistration'; // Import for service worker registration

// Register the service worker for Progressive Web App capabilities
serviceWorkerRegistration.register();

// Socket.io setup for real-time notifications
const socket = io('http://localhost:3001');

socket.on('new-notification', (notification) => {
    console.log('New Notification:', notification);
    // Handle the notification as needed, e.g., update state or UI
});

// Using `createRoot` for React 18+
const container = document.getElementById('root');
const root = createRoot(container); // Create root for React 18+
root.render(
    <ErrorBoundary>
        <Router>
            <App />
        </Router>
    </ErrorBoundary>
);
