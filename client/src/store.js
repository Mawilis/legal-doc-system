// ~/client/src/store.js

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
import storage from 'redux-persist/lib/storage'; // Defaults to localStorage for web
import logger from 'redux-logger';

// --- Import Middleware ---
import socketMiddleware from './middleware/socketMiddleware';

// --- Import All Slice Reducers ---
import authReducer from './features/auth/reducers/authSlice';
import profileReducer from './features/profile/reducers/profileSlice';
import adminReducer from './features/admin/reducers/adminSlice';
import documentReducer from './features/documents/reducers/documentSlice';
import chatReducer from './features/chat/reducers/chatSlice';
import dashboardReducer from './features/dashboard/reducers/dashboardSlice';
import notificationsReducer from './features/notifications/reducers/notificationsSlice';
import settingsReducer from './features/settings/reducers/settingsSlice';
import analyticsReducer from './features/analytics/reducers/analyticsSlice';
import billingReducer from './features/billing/reducers/billingSlice';
import serviceQueueReducer from './features/serviceQueue/reducers/serviceQueueSlice';
import movementTrackingReducer from './features/movementTracking/reducers/movementTrackingSlice';
import communicationReducer from './features/communication/reducers/communicationSlice';
import sheriffReducer from './features/sheriff/reducers/sheriffSlice'; // Import the new sheriff slice

// --- Combine All Reducers into a Single Root Reducer ---
const rootReducer = combineReducers({
    auth: authReducer,
    profile: profileReducer,
    admin: adminReducer,
    documents: documentReducer,
    chat: chatReducer,
    dashboard: dashboardReducer,
    notifications: notificationsReducer,
    settings: settingsReducer,
    analytics: analyticsReducer,
    billing: billingReducer,
    serviceQueue: serviceQueueReducer,
    movementTracking: movementTrackingReducer,
    communication: communicationReducer,
    sheriff: sheriffReducer, // ✅ Add the sheriff slice to the store
});

// --- Redux Persist Configuration ---
// This configuration determines which parts of your Redux state will be saved
// to local storage and rehydrated on page refresh.
const persistConfig = {
    key: 'root',
    storage,
    // Only persist slices that are safe and necessary to store locally.
    // Avoid persisting transient or sensitive data.
    whitelist: ['auth', 'profile', 'settings', 'billing'],
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
        }).concat(logger, socketMiddleware), // Wire the socket middleware into the store
    devTools: process.env.NODE_ENV !== 'production', // Enable devTools in non-production environments
});

const persistor = persistStore(store);

export { store, persistor };
export default store;
