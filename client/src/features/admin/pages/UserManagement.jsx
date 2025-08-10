// ~/legal-doc-system/client/src/features/admin/pages/UserManagement.jsx

import React, { useEffect, useState, useCallback, useMemo } from 'react';
import styled from 'styled-components';
import { useDispatch, useSelector } from 'react-redux';
import {
    fetchAllUsers,
    deleteUser,
    createUser,
    updateUser,
    updateUserPermissions,
    addUserFromSocket,
    removeUserFromSocket,
    updateUserFromSocket
} from '../reducers/adminSlice';
import { FaTrash, FaEdit, FaPlus, FaShieldAlt } from 'react-icons/fa';
import Button from '../../../components/StyledButton';
import LoadingSpinner from '../../../components/LoadingSpinner';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import io from 'socket.io-client';
//import { toast } from 'react-toastify';

// --- Constants ---
const USERS_PER_PAGE = 5;
const SOCKET_URL = process.env.REACT_APP_SERVER_URL || 'http://localhost:5000';
const PERMISSION_MODULES = ['documents', 'billing', 'settings', 'users'];
const PERMISSION_ACTIONS = ['create', 'read', 'update', 'delete'];

// --- Validation Schema for the User Form ---
const UserValidationSchema = Yup.object({
    name: Yup.string().min(2, 'Too Short!').required('Name is required'),
    email: Yup.string().email('Invalid email address').required('Email is required'),
    role: Yup.string().oneOf(['admin', 'sheriff', 'attorney', 'user'], 'Invalid role').required('Role is required'),
});

// --- Reusable UI Components ---

/**
 * A generic, reusable Modal component.
 */
const Modal = ({ open, onClose, children, width }) => {
    if (!open) return null;
    return (
        <ModalOverlay onClick={onClose}>
            <ModalBox width={width} onClick={(e) => e.stopPropagation()}>{children}</ModalBox>
        </ModalOverlay>
    );
};

/**
 * A reusable confirmation dialog for dangerous actions.
 */
const ConfirmationDialog = ({ open, onClose, onConfirm, title, message }) => (
    <Modal open={open} onClose={onClose}>
        <Typography as="h3">{title}</Typography>
        <p>{message}</p>
        <ActionRow>
            <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
            <Button type="button" variant="danger" onClick={onConfirm}>Confirm</Button>
        </ActionRow>
    </Modal>
);

/**
 * A reusable form for creating or editing a user.
 */
const UserForm = ({ initialValues, validationSchema, onSubmit, onCancel, isEditMode }) => (
    <Formik initialValues={initialValues} validationSchema={validationSchema} onSubmit={onSubmit} enableReinitialize>
        {() => (
            <StyledForm>
                <Field as={StyledInput} name="name" placeholder="Full Name" />
                <StyledErrorMessage name="name" component="div" />
                <Field as={StyledInput} name="email" type="email" placeholder="Email Address" />
                <StyledErrorMessage name="email" component="div" />
                <Field as={StyledSelect} name="role">
                    <option value="" disabled>Select a role</option>
                    <option value="admin">Admin</option>
                    <option value="sheriff">Sheriff</option>
                    <option value="attorney">Attorney</option>
                    <option value="user">User</option>
                </Field>
                <StyledErrorMessage name="role" component="div" />
                <ActionRow>
                    <Button type="button" variant="secondary" onClick={onCancel}>Cancel</Button>
                    <Button type="submit" variant="success">{isEditMode ? 'Save Changes' : 'Create User'}</Button>
                </ActionRow>
            </StyledForm>
        )}
    </Formik>
);

/**
 * A dedicated modal for editing a user's granular permissions.
 */
const PermissionsModal = ({ user, open, onClose }) => {
    const dispatch = useDispatch();
    const [localPermissions, setLocalPermissions] = useState(user?.permissions || {});

    useEffect(() => {
        setLocalPermissions(user?.permissions || {});
    }, [user]);

    const handleToggle = (module, action) => {
        setLocalPermissions(prev => {
            const moduleActions = prev[module] || [];
            const hasAction = moduleActions.includes(action);
            const newModuleActions = hasAction ? moduleActions.filter(a => a !== action) : [...moduleActions, action];
            return { ...prev, [module]: newModuleActions };
        });
    };

    const handleSave = async () => {
        try {
            await dispatch(updateUserPermissions({ userId: user.id, permissions: localPermissions })).unwrap();
            onClose();
        } catch (err) {
            // Error toast is handled by the slice
        }
    };

    return (
        <Modal open={open} onClose={onClose} width="600px">
            <Typography as="h3">Edit Permissions for {user?.name}</Typography>
            <PermissionsTable>
                <thead>
                    <tr>
                        <th>Module</th>
                        {PERMISSION_ACTIONS.map(action => <th key={action}>{action}</th>)}
                    </tr>
                </thead>
                <tbody>
                    {PERMISSION_MODULES.map(module => (
                        <tr key={module}>
                            <td>{module}</td>
                            {PERMISSION_ACTIONS.map(action => (
                                <td key={action}>
                                    <input
                                        type="checkbox"
                                        checked={localPermissions[module]?.includes(action) || false}
                                        onChange={() => handleToggle(module, action)}
                                    />
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </PermissionsTable>
            <ActionRow>
                <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
                <Button type="button" variant="success" onClick={handleSave}>Save Permissions</Button>
            </ActionRow>
        </Modal>
    );
};

/**
 * UserManagement Component: A comprehensive, real-time interface for managing users and permissions.
 */
const UserManagement = () => {
    // --- Hooks ---
    const dispatch = useDispatch();
    const { users, loading, error } = useSelector((state) => state.admin);

    // --- Component State ---
    const [isAddEditModalOpen, setAddEditModalOpen] = useState(false);
    const [isConfirmOpen, setConfirmOpen] = useState(false);
    const [isPermissionsModalOpen, setPermissionsModalOpen] = useState(false);
    const [selectedUser, setSelectedUser] = useState(null);
    const [search, setSearch] = useState('');
    const [currentPage, setCurrentPage] = useState(1);

    // --- Data Fetching & Real-time Sync ---
    const fetchUsers = useCallback(() => { dispatch(fetchAllUsers()); }, [dispatch]);

    useEffect(() => {
        fetchUsers();
    }, [fetchUsers]);

    useEffect(() => {
        const socket = io(SOCKET_URL);

        // Listen for real-time updates from the server
        socket.on('user-created', (user) => dispatch(addUserFromSocket(user)));
        socket.on('user-updated', (user) => dispatch(updateUserFromSocket(user)));
        socket.on('user-deleted', (userId) => dispatch(removeUserFromSocket(userId)));

        return () => socket.disconnect();
    }, [dispatch]);

    // --- Memoized Data for Performance ---
    const filteredUsers = useMemo(() =>
        users.filter((u) => u.name.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase())),
        [search, users]
    );

    const paginatedUsers = useMemo(() => {
        const start = (currentPage - 1) * USERS_PER_PAGE;
        return filteredUsers.slice(start, start + USERS_PER_PAGE);
    }, [filteredUsers, currentPage]);

    // --- Event Handlers ---
    const handleOpenAddEditModal = (user = null) => {
        setSelectedUser(user);
        setAddEditModalOpen(true);
    };

    const handleCloseAddEditModal = () => {
        setAddEditModalOpen(false);
        setSelectedUser(null);
    };

    const handleFormSubmit = async (values, { resetForm }) => {
        const isEditMode = !!values.id;
        try {
            if (isEditMode) {
                await dispatch(updateUser({ userId: values.id, userData: values })).unwrap();
            } else {
                await dispatch(createUser(values)).unwrap();
            }
            resetForm();
            handleCloseAddEditModal();
        } catch (err) {
            // Error is handled by the slice
        }
    };

    const promptDelete = (user) => {
        setSelectedUser(user);
        setConfirmOpen(true);
    };

    const confirmDelete = async () => {
        if (!selectedUser) return;
        try {
            await dispatch(deleteUser(selectedUser.id || selectedUser._id)).unwrap();
        } catch (err) {
            // Error is handled by the slice
        } finally {
            setConfirmOpen(false);
            setSelectedUser(null);
        }
    };

    const openPermissionsModal = (user) => {
        setSelectedUser(user);
        setPermissionsModalOpen(true);
    };

    // --- Render Logic ---
    if (loading && users.length === 0) return <LoadingSpinner />;
    if (error) return <ErrorMessageText>Error: {error}</ErrorMessageText>;

    return (
        <Container>
            <Header>
                <Title>User Management</Title>
                <Button size="small" variant="success" onClick={() => handleOpenAddEditModal()}>
                    <FaPlus /> Add User
                </Button>
            </Header>

            <SearchBar
                type="text"
                placeholder="Search by name or email..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setCurrentPage(1); }}
            />

            <UsersTable>
                <thead>
                    <tr>
                        <th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {paginatedUsers.length > 0 ? paginatedUsers.map((user) => (
                        <tr key={user.id || user._id}>
                            <td>{user.id || user._id}</td>
                            <td>{user.name}</td>
                            <td>{user.email}</td>
                            <td><RoleTag role={user.role}>{user.role}</RoleTag></td>
                            <td>
                                <ActionGroup>
                                    <Button size="small" ghost onClick={() => handleOpenAddEditModal(user)} title="Edit User Details"><FaEdit /></Button>
                                    <Button size="small" ghost onClick={() => openPermissionsModal(user)} title="Edit Permissions"><FaShieldAlt /></Button>
                                    <Button size="small" ghost variant="danger" onClick={() => promptDelete(user)} title="Delete User"><FaTrash /></Button>
                                </ActionGroup>
                            </td>
                        </tr>
                    )) : (
                        <tr><td colSpan="5" style={{ textAlign: 'center' }}>No users found.</td></tr>
                    )}
                </tbody>
            </UsersTable>

            <Pagination>
                {[...Array(Math.ceil(filteredUsers.length / USERS_PER_PAGE))].map((_, i) => (
                    <Button key={i + 1} size="small" outline={i + 1 !== currentPage} onClick={() => setCurrentPage(i + 1)}>
                        {i + 1}
                    </Button>
                ))}
            </Pagination>

            {/* --- Modals --- */}
            <Modal open={isAddEditModalOpen} onClose={handleCloseAddEditModal}>
                <Typography as="h3">{selectedUser?.id ? 'Edit User' : 'Add New User'}</Typography>
                <UserForm
                    initialValues={selectedUser || { name: '', email: '', role: 'user' }}
                    validationSchema={UserValidationSchema}
                    onSubmit={handleFormSubmit}
                    onCancel={handleCloseAddEditModal}
                    isEditMode={!!selectedUser?.id}
                />
            </Modal>

            <ConfirmationDialog
                open={isConfirmOpen}
                onClose={() => setConfirmOpen(false)}
                onConfirm={confirmDelete}
                title="Confirm Deletion"
                message={`Are you sure you want to delete ${selectedUser?.name}? This action cannot be undone.`}
            />

            <PermissionsModal
                user={selectedUser}
                open={isPermissionsModalOpen}
                onClose={() => { setPermissionsModalOpen(false); setSelectedUser(null); }}
            />
        </Container>
    );
};

// --- Styled Components ---
const Container = styled.div` padding: 2rem; background-color: #f9f9f9; `;
const Header = styled.div` display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; `;
const Title = styled.h2` font-size: 2rem; color: #333; margin: 0; `;
const SearchBar = styled.input` padding: 0.75rem; width: 100%; max-width: 400px; margin-bottom: 1.5rem; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; `;
const UsersTable = styled.table`
  width: 100%; border-collapse: collapse; background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  th, td { padding: 1rem; border-bottom: 1px solid #ddd; text-align: left; vertical-align: middle; }
  th { background-color: #f8f9fa; font-weight: 600; }
  tr:hover { background-color: #f1f1f1; }
`;
const RoleTag = styled.span`
  background-color: ${({ role }) => {
        if (role === 'admin') return '#007bff';
        if (role === 'sheriff') return '#17a2b8';
        if (role === 'attorney') return '#ffc107';
        return '#6c757d';
    }};
  color: #fff; padding: 0.25rem 0.6rem; border-radius: 12px; font-size: 0.8rem; text-transform: capitalize;
`;
const Pagination = styled.div` display: flex; gap: 0.5rem; justify-content: center; margin-top: 1.5rem; `;
const ActionGroup = styled.div` display: flex; gap: 0.5rem; `;
const ErrorMessageText = styled.p` color: #dc3545; text-align: center; font-weight: bold; font-size: 1.2rem; `;
const Typography = styled.h3` font-size: 1.5rem; color: #333; margin-top: 0; margin-bottom: 1rem; text-align: center; `;
const ModalOverlay = styled.div`
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex; justify-content: center; align-items: center; z-index: 1000;
`;
const ModalBox = styled.div`
  background: #fff; padding: 2rem; width: 100%; max-width: ${({ width }) => width || '450px'};
  border-radius: 8px; box-shadow: 0 5px 15px rgba(0,0,0,0.3);
`;
const StyledForm = styled(Form)` display: flex; flex-direction: column; gap: 1rem; `;
const StyledInput = styled(Field)` width: 100%; padding: 0.75rem; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; `;
const StyledSelect = styled(Field)` width: 100%; padding: 0.75rem; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; background-color: white; `;
const StyledErrorMessage = styled(ErrorMessage)` color: #dc3545; font-size: 0.875rem; margin-top: -0.75rem; `;
const ActionRow = styled.div` display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1rem; `;
const PermissionsTable = styled.table`
    width: 100%;
    margin-top: 1rem;
    border-collapse: collapse;
    td, th {
        padding: 0.75rem;
        text-align: center;
        border: 1px solid #dee2e6;
    }
    th {
        background-color: #f8f9fa;
        text-transform: capitalize;
    }
    td:first-child {
        text-align: left;
        font-weight: 500;
        text-transform: capitalize;
    }
    input[type="checkbox"] {
        width: 16px;
        height: 16px;
        cursor: pointer;
    }
`;

export default UserManagement;
