// ~/legal-doc-system/client/src/features/chat/reducers/chatSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async thunk to fetch chat messages
export const fetchChatMessages = createAsyncThunk(
    'chat/fetchChatMessages',
    async (_, { rejectWithValue }) => {
        try {
            const response = await axios.get('/api/chat/messages');
            return response.data; // Assuming it returns an array of messages
        } catch (error) {
            if (error.response && error.response.data && error.response.data.message) {
                return rejectWithValue(error.response.data.message);
            } else {
                return rejectWithValue(error.message);
            }
        }
    }
);

// Async thunk to send a new message
export const sendMessage = createAsyncThunk(
    'chat/sendMessage',
    async (messageData, { rejectWithValue }) => {
        try {
            const response = await axios.post('/api/chat/messages', messageData);
            return response.data; // Assuming it returns the created message
        } catch (error) {
            if (error.response && error.response.data && error.response.data.message) {
                return rejectWithValue(error.response.data.message);
            } else {
                return rejectWithValue(error.message);
            }
        }
    }
);

const chatSlice = createSlice({
    name: 'chat',
    initialState: {
        messages: [],
        loading: false,
        error: null,
    },
    reducers: {
        // Define synchronous reducers if needed
    },
    extraReducers: (builder) => {
        builder
            // Fetch Chat Messages
            .addCase(fetchChatMessages.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchChatMessages.fulfilled, (state, action) => {
                state.loading = false;
                state.messages = action.payload;
            })
            .addCase(fetchChatMessages.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || 'Failed to fetch chat messages';
            })

            // Send Message
            .addCase(sendMessage.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(sendMessage.fulfilled, (state, action) => {
                state.loading = false;
                state.messages.push(action.payload);
            })
            .addCase(sendMessage.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || 'Failed to send message';
            });
    },
});

export default chatSlice.reducer;
