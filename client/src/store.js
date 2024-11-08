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
import storage from 'redux-persist/lib/storage'; // Defaults to localStorage for web
import logger from 'redux-logger';

// Import slice reducers
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

// Combine all reducers
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
});

// Configure persist settings
const persistConfig = {
    key: 'root',
    storage,
    whitelist: ['auth', 'profile', 'settings'],
};

// Create a persisted reducer
const persistedReducer = persistReducer(persistConfig, rootReducer);

// Configure the store
const store = configureStore({
    reducer: persistedReducer,
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: {
                ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
            },
        }).concat(logger),
});

// Create a persistor
const persistor = persistStore(store);

// Export both store and persistor
export { store, persistor };
export default store;
