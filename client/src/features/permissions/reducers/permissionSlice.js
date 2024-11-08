// ~/legal-doc-system/client/src/features/permissions/reducers/permissionSlice.js

import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    roles: ['User', 'Admin', 'Manager'],
    permissions: {
        User: [],
        Admin: ['addFees', 'editDocuments', 'viewReports'],
        Manager: ['viewReports'],
    },
};

const permissionSlice = createSlice({
    name: 'permissions',
    initialState,
    reducers: {
        addRole: (state, action) => {
            state.roles.push(action.payload);
        },
        updatePermissions: (state, action) => {
            const { role, permissions } = action.payload;
            state.permissions[role] = permissions;
        },
    },
});

export const { addRole, updatePermissions } = permissionSlice.actions;
export default permissionSlice.reducer;
