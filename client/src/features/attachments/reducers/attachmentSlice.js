// ~/legal-doc-system/client/src/features/attachments/reducers/attachmentSlice.js

import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    attachments: [],
    loading: false,
    error: null,
};

const attachmentSlice = createSlice({
    name: "attachments",
    initialState,
    reducers: {
        addAttachment: (state, action) => {
            state.attachments.push(action.payload);
        },
        removeAttachment: (state, action) => {
            state.attachments = state.attachments.filter(
                (attachment) => attachment.id !== action.payload
            );
        },
        setLoading: (state, action) => {
            state.loading = action.payload;
        },
        setError: (state, action) => {
            state.error = action.payload;
        },
    },
});

export const {
    addAttachment,
    removeAttachment,
    setLoading,
    setError,
} = attachmentSlice.actions;
export default attachmentSlice.reducer;