import { createSlice, nanoid } from '@reduxjs/toolkit';

const initialState = {
  messages: [],   // {id, from, text, ts}
  sending: false,
  error: null,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    receiveMessage(state, action) {
      const msg = action.payload;
      if (!msg?.id) msg.id = nanoid();
      state.messages.push(msg);
    },
    sendMessageStart(state) {
      state.sending = true;
      state.error = null;
    },
    sendMessageSuccess(state, action) {
      state.sending = false;
      const msg = action.payload;
      if (!msg?.id) msg.id = nanoid();
      state.messages.push(msg);
    },
    sendMessageError(state, action) {
      state.sending = false;
      state.error = action.payload || 'Failed to send';
    },
    clearChat(state) {
      state.messages = [];
      state.error = null;
    }
  }
});

export const {
  receiveMessage,
  sendMessageStart,
  sendMessageSuccess,
  sendMessageError,
  clearChat
} = chatSlice.actions;

export default chatSlice.reducer;
