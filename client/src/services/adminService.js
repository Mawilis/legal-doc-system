// ~/client/src/services/adminService.js
import http from './http';
import { toast } from 'react-toastify';

// Base API path for Admin Routes
const API_BASE = '/admin';

// --- Helper: Standardized Error Handler ---
const handleError = (err) => {
  const msg = err?.response?.data?.message || err?.message || 'Unknown administrative error';
  console.error(`[AdminService Error] ${msg}`, err);
  // Prevent duplicate toasts if the global interceptor already handled it
  if (!toast.isActive(msg)) {
    toast.error(msg);
  }
  throw new Error(msg);
};

/**
 * Fetch All System Users
 * Returns raw array or .users property depending on backend structure.
 * @returns {Promise<Array>}
 */
export const getAllUsers = async () => {
  try {
    const { data } = await http.get(`${API_BASE}/users`);
    return Array.isArray(data) ? data : (data?.users || []);
  } catch (e) {
    return handleError(e);
  }
};

/**
 * Create New User (Admin Override)
 * @param {Object} payload - { name, email, role, password }
 */
export const createUser = async (payload) => {
  try {
    const { data } = await http.post(`${API_BASE}/users`, payload);
    return data;
  } catch (e) {
    return handleError(e);
  }
};

/**
 * Update User Details
 * @param {string} userId 
 * @param {Object} updates 
 */
export const updateUser = async (userId, updates) => {
  try {
    const { data } = await http.put(`${API_BASE}/users/${userId}`, updates);
    return data;
  } catch (e) {
    return handleError(e);
  }
};

/**
 * Delete User
 * @param {string} userId 
 */
export const deleteUser = async (userId) => {
  try {
    const { data } = await http.delete(`${API_BASE}/users/${userId}`);
    return data;
  } catch (e) {
    return handleError(e);
  }
};

/**
 * Assign User to Team
 * @param {string} userId 
 * @param {string} teamId 
 */
export const assignUserToTeam = async (userId, teamId) => {
  try {
    const { data } = await http.put(`${API_BASE}/users/${userId}/team`, { teamId });
    return data;
  } catch (e) {
    return handleError(e);
  }
};

/**
 * Toggle Single Permission
 * @param {string} userId 
 * @param {string} module 
 * @param {boolean} value 
 */
export const togglePermission = async (userId, module, value) => {
  try {
    const { data } = await http.patch(`${API_BASE}/users/${userId}/permissions`, { module, value });
    return data;
  } catch (e) {
    return handleError(e);
  }
};

/**
 * Bulk Update Permissions
 * @param {string} userId 
 * @param {Object} permissions - { documents: true, billing: false }
 */
export const updatePermissions = async (userId, permissions) => {
  try {
    const { data } = await http.patch(`${API_BASE}/users/${userId}/permissions`, { permissions });
    return data;
  } catch (e) {
    return handleError(e);
  }
};

/**
 * Get System Audit Logs
 * Critical for legal compliance tracking.
 */
export const getAuditLogs = async () => {
  try {
    const { data } = await http.get(`${API_BASE}/logs`);
    return data;
  } catch (e) {
    return handleError(e);
  }
};

// ✅ FIX: Assign object to variable before export (Fixes ESLint warning)
const adminService = {
  getAllUsers,
  createUser,
  updateUser,
  deleteUser,
  assignUserToTeam,
  togglePermission,
  updatePermissions,
  getAuditLogs,
};

export default adminService;