import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import {
    createUser as createUserService,
    deleteUser as deleteUserService,
    getAllUsers,
    updateUser as updateUserService,
} from "../services/adminService";
import { toast } from "react-toastify";

// Define initial state
const initialState = {
    users: [],
    loading: false,
    error: null,
};

// Async thunk to fetch all users
export const fetchAllUsers = createAsyncThunk(
    "admin/fetchAllUsers",
    async (_, { rejectWithValue }) => {
        try {
            const response = await getAllUsers();
            return response.data; // Assuming your API returns data in response.data
        } catch (err) {
            return rejectWithValue(
                err.response?.data || "Failed to fetch users"
            );
        }
    }
);

// Async thunk to delete a user
export const deleteUser = createAsyncThunk(
    "admin/deleteUser",
    async (userId, { rejectWithValue }) => {
        try {
            await deleteUserService(userId);
            toast.success("User deleted successfully!");
            return userId;
        } catch (err) {
            toast.error("Failed to delete user.");
            return rejectWithValue(
                err.response?.data || "Failed to delete user"
            );
        }
    }
);

// Async thunk to create a new user
export const createUser = createAsyncThunk(
    "admin/createUser",
    async (userData, { rejectWithValue }) => {
        try {
            const response = await createUserService(userData);
            toast.success("User created successfully!");
            return response.data; // Assuming API returns new user data
        } catch (err) {
            toast.error("Failed to create user.");
            return rejectWithValue(
                err.response?.data || "Failed to create user"
            );
        }
    }
);

// Async thunk to update a user
export const updateUser = createAsyncThunk(
    "admin/updateUser",
    async (userData, { rejectWithValue }) => {
        try {
            const { id, ...updatedData } = userData; // Extract ID from userData
            const response = await updateUserService(id, updatedData);
            toast.success("User updated successfully!");
            return response.data; // Assuming API returns updated user data
        } catch (err) {
            toast.error("Failed to update user.");
            return rejectWithValue(
                err.response?.data || "Failed to update user"
            );
        }
    }
);

// Create admin slice
const adminSlice = createSlice({
    name: "admin",
    initialState,
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(fetchAllUsers.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchAllUsers.fulfilled, (state, action) => {
                state.loading = false;
                state.users = action.payload;
            })
            .addCase(fetchAllUsers.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })
            .addCase(deleteUser.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(deleteUser.fulfilled, (state, action) => {
                state.loading = false;
                state.users = state.users.filter(
                    (user) => user.id !== action.payload
                );
            })
            .addCase(deleteUser.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })
            .addCase(createUser.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(createUser.fulfilled, (state, action) => {
                state.loading = false;
                state.users.push(action.payload);
            })
            .addCase(createUser.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })
            .addCase(updateUser.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(updateUser.fulfilled, (state, action) => {
                state.loading = false;
                const index = state.users.findIndex(
                    (user) => user.id === action.payload.id
                );
                if (index !== -1) {
                    state.users[index] = action.payload;
                }
            })
            .addCase(updateUser.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            });
    },
});

// Export reducer
export default adminSlice.reducer;