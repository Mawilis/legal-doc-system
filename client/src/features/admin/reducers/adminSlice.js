// ~/legal-doc-system/client/src/features/admin/reducers/adminSlice.js

import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import {
    createUser as createUserService,
    deleteUser as deleteUserService,
    getAllUsers,
    updateUser as updateUserService,
    // Assume a new service function for toggling a single permission exists
    togglePermission as togglePermissionService,
} from "../services/adminService";
import { toast } from "react-toastify";

// --- Initial State ---
const initialState = {
    users: [],
    loading: false,
    error: null,
};

// --- Helper function to handle API errors ---
const handleApiError = (err, defaultMessage) => {
    const message = err.response?.data?.message || err.message || defaultMessage;
    toast.error(message);
    return message;
};

// --- Async Thunks for API Operations ---

/**
 * Fetches all users from the backend.
 */
export const fetchAllUsers = createAsyncThunk(
    "admin/fetchAllUsers",
    async (_, { rejectWithValue }) => {
        try {
            const response = await getAllUsers();
            // Ensure compatibility by mapping _id to id if it exists
            return response.data.map(user => ({ ...user, id: user._id || user.id }));
        } catch (err) {
            return rejectWithValue(handleApiError(err, "Failed to fetch users"));
        }
    }
);

/**
 * Deletes a user by their ID.
 */
export const deleteUser = createAsyncThunk(
    "admin/deleteUser",
    async (userId, { rejectWithValue }) => {
        try {
            await deleteUserService(userId);
            // The socket middleware will handle the success toast and state update
            return userId;
        } catch (err) {
            return rejectWithValue(handleApiError(err, "Failed to delete user"));
        }
    }
);

/**
 * Creates a new user.
 */
export const createUser = createAsyncThunk(
    "admin/createUser",
    async (userData, { rejectWithValue }) => {
        try {
            const response = await createUserService(userData);
            // The socket middleware will handle the success toast and state update
            const newUser = response.data;
            return { ...newUser, id: newUser._id || newUser.id };
        } catch (err) {
            return rejectWithValue(handleApiError(err, "Failed to create user"));
        }
    }
);

/**
 * Updates a user's core details.
 */
export const updateUser = createAsyncThunk(
    "admin/updateUser",
    async ({ userId, userData }, { rejectWithValue }) => {
        try {
            const response = await updateUserService(userId, userData);
            // The socket middleware will handle the success toast and state update
            const updatedUser = response.data;
            return { ...updatedUser, id: updatedUser._id || updatedUser.id };
        } catch (err) {
            return rejectWithValue(handleApiError(err, "Failed to update user"));
        }
    }
);

/**
 * Updates the entire permissions object for a specific user.
 */
export const updateUserPermissions = createAsyncThunk(
    "admin/updateUserPermissions",
    async ({ userId, permissions }, { rejectWithValue }) => {
        try {
            const response = await updateUserService(userId, { permissions });
            // The socket middleware will handle the success toast and state update
            const updatedUser = response.data;
            return { ...updatedUser, id: updatedUser._id || updatedUser.id };
        } catch (err) {
            return rejectWithValue(handleApiError(err, "Failed to update permissions"));
        }
    }
);

/**
 * Toggles a single permission for a user.
 */
export const toggleUserPermission = createAsyncThunk(
    "admin/toggleUserPermission",
    async ({ userId, module, permission }, { rejectWithValue }) => {
        try {
            const response = await togglePermissionService(userId, module, permission);
            // The socket middleware will handle the success toast and state update
            const updatedUser = response.data;
            return { ...updatedUser, id: updatedUser._id || updatedUser.id };
        } catch (err) {
            return rejectWithValue(handleApiError(err, "Failed to toggle permission"));
        }
    }
);

/**
 * Assigns a user to a specific team.
 */
export const assignUserToTeam = createAsyncThunk(
    "admin/assignUserToTeam",
    async ({ userId, teamId }, { rejectWithValue }) => {
        try {
            const response = await updateUserService(userId, { team: teamId });
            // The socket middleware will handle the success toast and state update
            const updatedUser = response.data;
            return { ...updatedUser, id: updatedUser._id || updatedUser.id };
        } catch (err) {
            return rejectWithValue(handleApiError(err, "Failed to assign team"));
        }
    }
);

// --- Redux Slice Definition ---
const adminSlice = createSlice({
    name: "admin",
    initialState,
    reducers: {
        /**
         * Adds a new user to the state. Called by socket middleware.
         * @param {object} state - The current Redux state.
         * @param {object} action - The action containing the new user object.
         */
        addUserFromSocket: (state, action) => {
            const newUser = { ...action.payload, id: action.payload._id || action.payload.id };
            // Avoid duplicates
            if (!state.users.find(user => user.id === newUser.id)) {
                state.users.push(newUser);
            }
        },
        /**
         * Removes a user from the state. Called by socket middleware.
         * @param {object} state - The current Redux state.
         * @param {object} action - The action containing the ID of the user to remove.
         */
        removeUserFromSocket: (state, action) => {
            const userId = action.payload;
            state.users = state.users.filter(user => user.id !== userId && user._id !== userId);
        },
        /**
         * Updates an existing user in the state. Called by socket middleware.
         * @param {object} state - The current Redux state.
         * @param {object} action - The action containing the updated user object.
         */
        updateUserFromSocket: (state, action) => {
            const updatedUser = { ...action.payload, id: action.payload._id || action.payload.id };
            const index = state.users.findIndex(user => user.id === updatedUser.id);
            if (index !== -1) {
                state.users[index] = updatedUser;
            }
        },
    },
    extraReducers: (builder) => {
        // --- Generic Pending State Handler ---
        const handlePending = (state) => {
            state.loading = true;
            state.error = null;
        };

        // --- Generic Rejected State Handler ---
        const handleRejected = (state, action) => {
            state.loading = false;
            state.error = action.payload;
        };

        builder
            // Fetch All Users
            .addCase(fetchAllUsers.pending, handlePending)
            .addCase(fetchAllUsers.fulfilled, (state, action) => {
                state.loading = false;
                state.users = action.payload;
            })
            .addCase(fetchAllUsers.rejected, handleRejected)

            // --- Matchers for cleaner state management ---

            // This matcher handles the pending state for all thunks in this slice
            .addMatcher(
                (action) => action.type.startsWith('admin/') && action.type.endsWith('/pending'),
                handlePending
            )
            // This matcher handles the rejected state for all thunks that don't have a specific rejected case
            .addMatcher(
                (action) => action.type.startsWith('admin/') && action.type.endsWith('/rejected'),
                handleRejected
            )
            // This matcher handles the fulfilled state for all actions that don't need a specific state update,
            // as the socket middleware will handle it. It just sets loading to false.
            .addMatcher(
                (action) => action.type.startsWith('admin/') && action.type.endsWith('/fulfilled') && action.type !== fetchAllUsers.fulfilled.type,
                (state) => {
                    state.loading = false;
                }
            );
    },
});

// --- Export Actions and Reducer ---
export const { addUserFromSocket, removeUserFromSocket, updateUserFromSocket } = adminSlice.actions;
export default adminSlice.reducer;
