// ~/legal-doc-system/client/src/features/chat/reducers/chatSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios'; // Assuming an authenticated axios instance is configured
import { toast } from 'react-toastify';

// --- Initial State ---
const initialState = {
    messages: [],
    loading: false,
    error: null,
};

// --- Helper function to handle API errors ---
const handleApiError = (err, defaultMessage) => {
    const message = err.response?.data?.message || err.message || defaultMessage;
    toast.error(message);
    return message;
};

// --- Async Thunks ---

/**
 * Fetches the initial message history for a specific chat room.
 */
export const fetchChatMessages = createAsyncThunk(
    'chat/fetchChatMessages',
    async (roomId, { rejectWithValue }) => {
        try {
            const response = await axios.get(`/api/chat/messages/${roomId}`);
            return response.data;
        } catch (err) {
            return rejectWithValue(handleApiError(err, 'Failed to fetch chat history'));
        }
    }
);

/**
 * Sends a new message to the backend API.
 * The backend is responsible for saving it and broadcasting it via sockets.
 */
export const sendMessage = createAsyncThunk(
    'chat/sendMessage',
    async (messageData, { rejectWithValue }) => {
        try {
            // This API call just posts the message; it doesn't need to return it,
            // as the real-time update will come via a socket event.
            await axios.post('/api/chat/messages', messageData);
            return null; // No state change needed here
        } catch (err) {
            return rejectWithValue(handleApiError(err, 'Failed to send message'));
        }
    }
);

// --- Redux Slice Definition ---
const chatSlice = createSlice({
    name: 'chat',
    initialState,
    reducers: {
        /**
         * Adds a new message to the state in real-time.
         * This action should be dispatched by your socketMiddleware when a 'newMessage' event is received.
         * @param {object} state - The current Redux state.
         * @param {object} action - The action containing the new message payload.
         */
        addMessage: (state, action) => {
            // Avoid adding duplicate messages
            if (!state.messages.find(msg => msg._id === action.payload._id)) {
                state.messages.push(action.payload);
            }
        },
        /**
         * Clears all chat messages from the state, for example, when leaving a room.
         */
        clearChat: (state) => {
            state.messages = [];
            state.error = null;
        },
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
                state.error = action.payload;
            })

            // Send Message (only handles error state, success is handled by socket)
            .addCase(sendMessage.rejected, (state, action) => {
                state.error = action.payload;
                // Optionally add the failed message to the UI with a "failed to send" indicator
            });
    },
});

export const { addMessage, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
