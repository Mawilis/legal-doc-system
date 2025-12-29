import { configureStore } from '@reduxjs/toolkit';
import authReducer from './features/auth/reducers/authSlice';
import adminReducer from './features/admin/reducers/adminSlice';
import settingsReducer from './features/settings/reducers/settingsSlice';
import searchReducer from './features/search/reducers/searchSlice';
import chatReducer from './features/chat/reducers/chatSlice';

const store = configureStore({
  reducer: {
    auth: authReducer,
    admin: adminReducer,
    settings: settingsReducer,
    search: searchReducer,
    chat: chatReducer,
  },
});

export default store;
