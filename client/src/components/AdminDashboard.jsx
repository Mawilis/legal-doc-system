// ~/client/src/components/AdminDashboard.jsx

import React, { useEffect, useState, useCallback, useMemo } from 'react';
import styled from 'styled-components';
import { getAllUsers, deleteUser, updateUserRole } from '../services/adminService';
import { FaTrashAlt } from 'react-icons/fa';
import { toast } from 'react-toastify';
import io from 'socket.io-client';
import LoadingSpinner from './LoadingSpinner'; // Assuming a generic spinner component exists

// --- Constants ---
const USERS_PER_PAGE = 5;
const SOCKET_URL = process.env.REACT_APP_SERVER_URL || 'http://localhost:5000';

// --- Reusable Modal Component for Confirmation ---
const ConfirmationDialog = ({ open, onClose, onConfirm, title, message }) => {
    if (!open) return null;
    return (
        <ModalOverlay onClick={onClose}>
            <ModalBox onClick={(e) => e.stopPropagation()}>
                <ModalTitle>{title}</ModalTitle>
                <p>{message}</p>
                <ActionRow>
                    <ActionButton variant="secondary" onClick={onClose}>Cancel</ActionButton>
                    <ActionButton variant="danger" onClick={onConfirm}>Confirm Delete</ActionButton>
                </ActionRow>
            </ModalBox>
        </ModalOverlay>
    );
};

/**
 * AdminDashboard Component: A real-time dashboard for managing user roles.
 * Features live updates via sockets, pagination, search, and role editing.
 */
const AdminDashboard = () => {
    // --- State Management ---
    const [users, setUsers] = useState([]);
    const [search, setSearch] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isConfirmOpen, setConfirmOpen] = useState(false);
    const [userToDelete, setUserToDelete] = useState(null);

    // --- Data Fetching ---
    const fetchUsers = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await getAllUsers();
            setUsers(data);
        } catch (err) {
            const errorMessage = err.response?.data?.message || 'Failed to fetch users';
            toast.error(errorMessage);
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    }, []);

    // Initial data fetch on component mount
    useEffect(() => {
        fetchUsers();
    }, [fetchUsers]);

    // Effect for handling real-time updates via Socket.IO
    useEffect(() => {
        const socket = io(SOCKET_URL);

        // Listener for when another admin updates a user's role
        socket.on('user_role_updated', ({ userId, newRole }) => {
            toast.info("A user's role has been updated in real-time.");
            // Update the local state to reflect the change without a full refetch
            setUsers((prevUsers) =>
                prevUsers.map((user) =>
                    user._id === userId ? { ...user, role: newRole } : user
                )
            );
        });

        // Cleanup on component unmount
        return () => socket.disconnect();
    }, []);

    // --- Memoized Data for Performance ---
    const filteredUsers = useMemo(() =>
        users.filter((u) =>
            u.name.toLowerCase().includes(search.toLowerCase()) ||
            u.email.toLowerCase().includes(search.toLowerCase())
        ), [search, users]
    );

    const paginatedUsers = useMemo(() => {
        const start = (currentPage - 1) * USERS_PER_PAGE;
        return filteredUsers.slice(start, start + USERS_PER_PAGE);
    }, [filteredUsers, currentPage]);

    // --- Event Handlers ---

    /**
     * Opens the confirmation modal before deleting a user.
     * @param {object} user - The user object to be deleted.
     */
    const promptDelete = (user) => {
        setUserToDelete(user);
        setConfirmOpen(true);
    };

    /**
     * Confirms and executes the user deletion.
     */
    const handleDelete = async () => {
        if (!userToDelete) return;
        try {
            await deleteUser(userToDelete._id);
            toast.success(`User "${userToDelete.name}" deleted successfully`);
            // Optimistically update the UI
            setUsers((prevUsers) => prevUsers.filter((u) => u._id !== userToDelete._id));
        } catch (err) {
            toast.error(err.response?.data?.message || 'Error deleting user');
        } finally {
            setConfirmOpen(false);
            setUserToDelete(null);
        }
    };

    /**
     * Handles updating a user's role.
     * @param {string} userId - The ID of the user to update.
     * @param {string} newRole - The new role to assign.
     */
    const handleRoleChange = async (userId, newRole) => {
        try {
            await updateUserRole(userId, newRole);
            toast.success('Role updated successfully');
            // Optimistically update the UI. The socket listener will handle updates from other clients.
            setUsers((prev) =>
                prev.map((u) => (u._id === userId ? { ...u, role: newRole } : u))
            );
            // In a real app, the backend would now emit the 'user_role_updated' event.
        } catch (err) {
            toast.error(err.response?.data?.message || 'Error updating role');
            // Optional: Re-fetch users to revert optimistic update on failure
            fetchUsers();
        }
    };

    // --- Render Logic ---

    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorText>{error}</ErrorText>;

    return (
        <Wrapper>
            <Header>
                <Title>Admin Dashboard</Title>
                <SearchInput
                    type="text"
                    placeholder="Search by name or email..."
                    value={search}
                    onChange={(e) => {
                        setSearch(e.target.value);
                        setCurrentPage(1); // Reset page on new search
                    }}
                />
            </Header>

            <UserTable>
                <thead>
                    <tr>
                        <th>Name</th><th>Email</th><th>Role</th><th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {paginatedUsers.length > 0 ? paginatedUsers.map((user) => (
                        <tr key={user._id}>
                            <td>{user.name}</td>
                            <td>{user.email}</td>
                            <td>
                                <RoleSelect
                                    value={user.role}
                                    onChange={(e) => handleRoleChange(user._id, e.target.value)}
                                >
                                    <option value="user">User</option>
                                    <option value="admin">Admin</option>
                                </RoleSelect>
                            </td>
                            <td>
                                <ActionButton variant="danger" ghost onClick={() => promptDelete(user)} title="Delete User">
                                    <FaTrashAlt />
                                </ActionButton>
                            </td>
                        </tr>
                    )) : (
                        <tr>
                            <td colSpan="4" style={{ textAlign: 'center' }}>No users found.</td>
                        </tr>
                    )}
                </tbody>
            </UserTable>

            <Pagination>
                {Array.from({ length: Math.ceil(filteredUsers.length / USERS_PER_PAGE) }, (_, i) => (
                    <PageButton key={i + 1} onClick={() => setCurrentPage(i + 1)} $active={i + 1 === currentPage}>
                        {i + 1}
                    </PageButton>
                ))}
            </Pagination>

            <ConfirmationDialog
                open={isConfirmOpen}
                onClose={() => setConfirmOpen(false)}
                onConfirm={handleDelete}
                title="Confirm Deletion"
                message={`Are you sure you want to delete the user "${userToDelete?.name}"? This action cannot be undone.`}
            />
        </Wrapper>
    );
};

// --- Styled Components ---

const Wrapper = styled.div`
  padding: 2rem;
  background-color: #f9f9f9;
`;
const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
`;
const Title = styled.h2`
  font-size: 2rem;
  color: #333;
  margin: 0;
`;
const SearchInput = styled.input`
  padding: 0.75rem;
  width: 100%;
  max-width: 300px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
`;
const UserTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  th, td {
    padding: 1rem;
    border-bottom: 1px solid #ddd;
    text-align: left;
    vertical-align: middle;
  }
  th {
    background-color: #f8f9fa;
    font-weight: 600;
  }
  tr:hover {
    background-color: #f1f1f1;
  }
`;
const RoleSelect = styled.select`
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ccc;
  background-color: white;
  font-size: 0.9rem;
`;
const Pagination = styled.div`
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 1.5rem;
`;
const PageButton = styled.button`
  padding: 8px 12px;
  border: 1px solid ${({ $active }) => ($active ? '#007bff' : '#ccc')};
  background-color: ${({ $active }) => ($active ? '#007bff' : '#fff')};
  color: ${({ $active }) => ($active ? '#fff' : '#333')};
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;

  &:hover {
    background-color: ${({ $active }) => ($active ? '#0056b3' : '#eee')};
    border-color: ${({ $active }) => ($active ? '#0056b3' : '#ccc')};
  }
`;
const ErrorText = styled.p`
  color: #dc3545;
  text-align: center;
  font-weight: bold;
  font-size: 1.2rem;
`;

// --- Modal Styled Components ---
const ModalOverlay = styled.div`
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex; justify-content: center; align-items: center; z-index: 1000;
`;
const ModalBox = styled.div`
  background: #fff; padding: 2rem; width: 100%; max-width: 450px;
  border-radius: 8px; box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  text-align: center;
`;
const ModalTitle = styled.h3`
  font-size: 1.5rem;
  color: #333;
  margin-top: 0;
  margin-bottom: 1rem;
`;
const ActionRow = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
`;
const ActionButton = styled.button`
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 10px 16px;
    font-size: 1rem;
    font-weight: 500;
    border-radius: 5px;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.2s ease-in-out;

    ${({ variant }) => {
        switch (variant) {
            case 'danger':
                return `background-color: #dc3545; color: white; border-color: #dc3545; &:hover { background-color: #c82333; }`;
            case 'secondary':
                return `background-color: #6c757d; color: white; border-color: #6c757d; &:hover { background-color: #5a6268; }`;
            default:
                return `background-color: #007bff; color: white; border-color: #007bff; &:hover { background-color: #0056b3; }`;
        }
    }}

    ${({ ghost }) => ghost && `
        background-color: transparent;
        color: #dc3545;
        &:hover {
            background-color: #dc3545;
            color: white;
        }
    `}
`;

export default AdminDashboard;
