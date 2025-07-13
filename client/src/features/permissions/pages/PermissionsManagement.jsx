// ~/legal-doc-system/client/src/features/permissions/pages/PermissionsManagement.jsx

import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { updatePermissions } from '../reducers/permissionSlice';
import { Button } from '@mui/material';

const PermissionsManagement = () => {
    const dispatch = useDispatch();
    const { roles, permissions } = useSelector((state) => state.permissions);

    const handleUpdatePermissions = (role) => {
        const newPermissions = ['addFees', 'editDocuments', 'deleteDocuments'];
        dispatch(updatePermissions({ role, permissions: newPermissions }));
    };

    return (
        <div>
            <h1>Permissions Management</h1>
            {roles.map((role) => (
                <div key={role}>
                    <h2>{role}</h2>
                    <p>Permissions: {permissions[role]?.join(', ') || 'None'}</p>
                    <Button variant="contained" onClick={() => handleUpdatePermissions(role)}>
                        Update Permissions
                    </Button>
                </div>
            ))}
        </div>
    );
};

export default PermissionsManagement;
