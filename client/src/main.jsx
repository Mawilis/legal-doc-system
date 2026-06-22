/* eslint-disable */
/**
 * @file /Users/wilsonkhanyezi/legal-doc-system/client/src/main.jsx
 * @version 1.0.1
 * @epitome Sovereign Root Initialization - Wilsy OS
 * @description Entry point for the Citadel UI. Enforces StrictMode and global theme injection.
 * * BIBLICAL STANDARDS:
 * - Worth: Billions.
 * - Integrity: StrictMode enabled for forensic debugging.
 * - Future-proof: No child's place.
 * * @collaboration Wilson Khanyezi (Founder), Gemini (Architect)
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import WilsyForensicMerkleShowroom from './components/chrome/WilsyForensicMerkleShowroom.jsx';
import './index.css';

// Billion-dollar infrastructure requires StrictMode to catch side-effects early
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {import.meta.env.DEV && window.location.pathname === '/wilsy-lab/forensic-merkle' ? (
      <WilsyForensicMerkleShowroom />
    ) : (
      <App />
    )}
  </React.StrictMode>,
);
