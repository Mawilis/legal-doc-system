// ~/client/src/features/instructions/reducers/instructionSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { toast } from 'react-toastify';
// import instructionService from '../services/instructionService'; // In a real app, you'd have a service file for API calls

// --- Mock API Service (for demonstration) ---
// Replace these with your actual API calls
const mockApiService = {
    fetchAll: async () => [{ _id: '1', title: 'Sample Instruction', content: 'This is the content.', creator: 'Admin', createdAt: new Date().toISOString() }],
    update: async (id, data) => ({ _id: id, ...data, creator: 'Admin', createdAt: new Date().toISOString() }),
    delete: async (id) => id,
};

// --- Initial State ---
const initialState = {
    instructions: [],
    loading: false,
    error: null,
};

// --- Async Thunks ---

/**
 * Fetches all instructions from the backend.
 */
export const fetchInstructions = createAsyncThunk(
    'instructions/fetchInstructions',
    async (_, { rejectWithValue }) => {
        try {
            const data = await mockApiService.fetchAll();
            return data;
        } catch (err) {
            const message = err.response?.data?.message || 'Failed to fetch instructions';
            toast.error(message);
            return rejectWithValue(message);
        }
    }
);

/**
 * Updates an existing instruction.
 */
export const updateInstruction = createAsyncThunk(
    'instructions/updateInstruction',
    async ({ instructionId, ...updateData }, { rejectWithValue }) => {
        try {
            const data = await mockApiService.update(instructionId, updateData);
            toast.success('Instruction updated successfully!');
            return data;
        } catch (err) {
            const message = err.response?.data?.message || 'Failed to update instruction';
            toast.error(message);
            return rejectWithValue(message);
        }
    }
);

/**
 * Deletes an instruction by its ID.
 */
export const deleteInstruction = createAsyncThunk(
    'instructions/deleteInstruction',
    async (instructionId, { rejectWithValue }) => {
        try {
            await mockApiService.delete(instructionId);
            toast.success('Instruction deleted successfully!');
            return instructionId;
        } catch (err) {
            const message = err.response?.data?.message || 'Delete failed';
            toast.error(message);
            return rejectWithValue(message);
        }
    }
);

// --- Redux Slice Definition ---
const instructionSlice = createSlice({
    name: 'instructions',
    initialState,
    reducers: {},
    extraReducers: (builder) => {
        builder
            // Fetch Instructions
            .addCase(fetchInstructions.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchInstructions.fulfilled, (state, action) => {
                state.loading = false;
                state.instructions = action.payload;
            })
            .addCase(fetchInstructions.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })
            // Update Instruction
            .addCase(updateInstruction.fulfilled, (state, action) => {
                const index = state.instructions.findIndex(i => i._id === action.payload._id);
                if (index !== -1) {
                    state.instructions[index] = action.payload;
                }
            })
            // Delete Instruction
            .addCase(deleteInstruction.fulfilled, (state, action) => {
                state.instructions = state.instructions.filter(i => i._id !== action.payload);
            });
    },
});

export default instructionSlice.reducer;
