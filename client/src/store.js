/**
 * File: client/src/store.js
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | Enterprise State Management
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - CENTRAL NERVOUS SYSTEM: Manages global state integrity.
 * - PERSISTENCE: Uses Redux Persist to survive browser refreshes.
 * - COMPLIANCE: Integrates Audit logs for forensic tracking.
 * - SCALABILITY: Modular slice architecture for easy expansion.
 * -----------------------------------------------------------------------------
 */

import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { persistStore, persistReducer, FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER } from 'redux-persist';
import storage from 'redux-persist/lib/storage'; // Defaults to localStorage for web

// --- FEATURE SLICES (The Lobes) ---
import authReducer from './features/auth/reducers/authSlice';
import adminReducer from './features/admin/reducers/adminSlice';
import settingsReducer from './features/settings/reducers/settingsSlice';
import searchReducer from './features/search/reducers/searchSlice';
import chatReducer from './features/chat/reducers/chatSlice';
import auditReducer from './features/audits/auditSlice'; // ✅ Compliance Engine

// --- ROOT REDUCER (The Cortex) ---
const rootReducer = combineReducers({
  auth: authReducer,       // Identity State
  admin: adminReducer,     // System Administration
  settings: settingsReducer, // User Preferences
  search: searchReducer,   // Legal Discovery
  chat: chatReducer,       // Communication
  audits: auditReducer,    // Forensic Logging
});

// --- PERSISTENCE CONFIGURATION ---
// We whitelist only what is necessary to maintain UX across reloads.
// Sensitive data (like active chats) might be excluded depending on policy.
const persistConfig = {
  key: 'wilsy_os_root',
  version: 1,
  storage,
  whitelist: ['auth', 'settings'], // Only persist Identity and Preferences
  blacklist: ['search', 'chat'],   // Clear ephemeral data on reload for security
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

// --- STORE CONFIGURATION ---
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore redux-persist actions to prevent console warnings
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production', // Disable DevTools in Prod for security
});

// --- PERSISTOR EXPORT ---
export const persistor = persistStore(store);