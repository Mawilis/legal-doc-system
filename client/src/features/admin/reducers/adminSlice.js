import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import {
  createUser as createUserService,
  deleteUser as deleteUserService,
  getAllUsers,
  updateUser as updateUserService,
  togglePermission as togglePermissionService,
  updatePermissions as updatePermissionsService
} from "../services/adminService";
import { toast } from "react-toastify";

// --- Initial State ---
const initialState = {
  users: [],
  loading: false,
  error: null,
};

const apiError = (err, fallback) =>
  err?.response?.data?.message || err?.message || fallback;

// Thunks
export const fetchAllUsers = createAsyncThunk("admin/fetchAllUsers", async (_, { rejectWithValue }) => {
  try {
    const data = await getAllUsers();
    return (Array.isArray(data) ? data : data?.data || []).map(u => ({ ...u, id: u._id || u.id }));
  } catch (err) {
    return rejectWithValue(apiError(err, "Failed to fetch users"));
  }
});

export const createUser = createAsyncThunk("admin/createUser", async (payload, { rejectWithValue }) => {
  try {
    const data = await createUserService(payload);
    const u = data?.data || data;
    return { ...u, id: u._id || u.id };
  } catch (err) {
    return rejectWithValue(apiError(err, "Failed to create user"));
  }
});

export const updateUser = createAsyncThunk("admin/updateUser", async ({ userId, userData }, { rejectWithValue }) => {
  try {
    const data = await updateUserService(userId, userData);
    const u = data?.data || data;
    return { ...u, id: u._id || u.id };
  } catch (err) {
    return rejectWithValue(apiError(err, "Failed to update user"));
  }
});

export const deleteUser = createAsyncThunk("admin/deleteUser", async (userId, { rejectWithValue }) => {
  try {
    await deleteUserService(userId);
    return userId;
  } catch (err) {
    return rejectWithValue(apiError(err, "Failed to delete user"));
  }
});

export const updateUserPermissions = createAsyncThunk(
  "admin/updateUserPermissions",
  async ({ userId, permissions }, { rejectWithValue }) => {
    try {
      const data = await updatePermissionsService(userId, permissions);
      const u = data?.data || data;
      return { ...u, id: u._id || u.id };
    } catch (err) {
      return rejectWithValue(apiError(err, "Failed to update permissions"));
    }
  }
);

export const toggleUserPermission = createAsyncThunk(
  "admin/toggleUserPermission",
  async ({ userId, module, permission }, { rejectWithValue }) => {
    try {
      const data = await togglePermissionService(userId, module, permission);
      const u = data?.data || data;
      return { ...u, id: u._id || u.id };
    } catch (err) {
      return rejectWithValue(apiError(err, "Failed to toggle permission"));
    }
  }
);

// Slice
const adminSlice = createSlice({
  name: "admin",
  initialState,
  reducers: {
    addUserFromSocket: (state, action) => {
      const nu = { ...action.payload, id: action.payload._id || action.payload.id };
      if (!state.users.find(u => u.id === nu.id)) state.users.push(nu);
    },
    updateUserFromSocket: (state, action) => {
      const uu = { ...action.payload, id: action.payload._id || action.payload.id };
      const i = state.users.findIndex(u => u.id === uu.id);
      if (i > -1) state.users[i] = uu;
    },
    removeUserFromSocket: (state, action) => {
      const id = action.payload;
      state.users = state.users.filter(u => (u.id || u._id) !== id);
    },
  },
  extraReducers: (builder) => {
    const pending = (s) => { s.loading = true; s.error = null; };
    const rejected = (s, a) => { s.loading = false; s.error = a.payload; toast.error(a.payload); };

    builder
      .addCase(fetchAllUsers.pending, pending)
      .addCase(fetchAllUsers.fulfilled, (s, a) => { s.loading = false; s.users = a.payload; })
      .addCase(fetchAllUsers.rejected, rejected)
      .addCase(createUser.pending, pending)
      .addCase(createUser.fulfilled, (s, a) => { s.loading = false; /* socket will inject; fallback: */ s.users.unshift(a.payload); })
      .addCase(createUser.rejected, rejected)
      .addCase(updateUser.pending, pending)
      .addCase(updateUser.fulfilled, (s, a) => { s.loading = false; /* socket will update; fallback: */ 
        const i = s.users.findIndex(u => u.id === a.payload.id); if (i>-1) s.users[i] = a.payload;
      })
      .addCase(updateUser.rejected, rejected)
      .addCase(deleteUser.pending, pending)
      .addCase(deleteUser.fulfilled, (s, a) => { s.loading = false; s.users = s.users.filter(u => (u.id || u._id) !== a.payload); })
      .addCase(deleteUser.rejected, rejected)
      .addCase(updateUserPermissions.pending, pending)
      .addCase(updateUserPermissions.fulfilled, (s, a) => { s.loading = false; 
        const i = s.users.findIndex(u => u.id === a.payload.id); if (i>-1) s.users[i] = a.payload;
      })
      .addCase(updateUserPermissions.rejected, rejected);
  }
});

export const {
  addUserFromSocket,
  updateUserFromSocket,
  removeUserFromSocket
} = adminSlice.actions;

export default adminSlice.reducer;

// Backwards-compat names (to silence previous import errors if any code still uses them)
export const fetchUsers = fetchAllUsers;
export const setRoles = () => ({ type: 'admin/setRoles' });
export const clearError = () => ({ type: 'admin/clearError' });
