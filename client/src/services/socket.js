// ~/legal-doc-system/client/src/store.js

import { configureStore, combineReducers } from '@reduxjs/toolkit';
import {
    persistStore,
    persistReducer,
    FLUSH,
    REHYDRATE,
    PAUSE,
    PERSIST,
    PURGE,
    REGISTER,
} from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import logger from 'redux-logger';

// --- Import Middleware ---
import socketMiddleware from './middleware/socketMiddleware'; // ✅ Import the socket middleware

// --- Import Slice Reducers ---
import authReducer from './features/auth/reducers/authSlice';
import profileReducer from './features/profile/reducers/profileSlice';
import adminReducer from './features/admin/reducers/adminSlice';
// ... import other reducers as needed

// --- Combine All Reducers ---
const rootReducer = combineReducers({
    auth: authReducer,
    profile: profileReducer,
    admin: adminReducer,
    // ... other reducers
});

// --- Persist Configuration ---
// This configuration determines which parts of your Redux state will be saved
// to local storage and rehydrated on page refresh.
const persistConfig = {
    key: 'root',
    storage,
    // Only persist slices that are safe and necessary to store locally.
    // Avoid persisting transient or sensitive data.
    whitelist: ['auth', 'profile', 'settings'],
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

/**
 * Configures the Redux store for the application.
 *
 * It includes:
 * - The persisted root reducer.
 * - A middleware chain with Redux Toolkit's defaults, redux-logger for development,
 * and our custom socketMiddleware for real-time event handling.
 * - Configuration to ignore actions from redux-persist for the serializability check.
 */
const store = configureStore({
    reducer: persistedReducer,
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: {
                // Ignore these action types from redux-persist
                ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
            },
        }).concat(logger, socketMiddleware), // ✅ Wire the socket middleware into the store
    devTools: process.env.NODE_ENV !== 'production',
});

const persistor = persistStore(store);

export { store, persistor };
export default store;
