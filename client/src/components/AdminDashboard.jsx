import React, { useEffect, useState, useCallback } from 'react';
import { getAllUsers, deleteUser } from '../services/adminService';
import styled from 'styled-components';
import { FaTrashAlt } from 'react-icons/fa'; // Import a delete icon
import { toast } from 'react-toastify'; // For user feedback (install react-toastify)

const AdminDashboard = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // useCallback for fetching users
    const fetchUsers = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getAllUsers();
            setUsers(data);
        } catch (error) {
            console.error('Failed to fetch users', error);
            setError('Failed to fetch users');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchUsers();
    }, [fetchUsers]);

    // useCallback for handling delete
    const handleDelete = useCallback(async (userId) => {
        const confirmDelete = window.confirm('Are you sure you want to delete this user?');
        if (!confirmDelete) return;

        try {
            await deleteUser(userId);
            setUsers(users.filter(user => user._id !== userId));
            toast.success('User deleted successfully!'); // User feedback
        } catch (error) {
            console.error('Failed to delete user', error);
            // More specific error handling
            if (error.response && error.response.status === 404) {
                setError('User not found.');
            } else if (error.response && error.response.status === 403) {
                setError('You do not have permission to delete this user.');
            } else {
                setError('Failed to delete user.');
            }
        }
    }, [users]);

    if (loading) return <Loading>Loading users...</Loading>;
    if (error) return <ErrorText>{error}</ErrorText>;

    return (
        <AdminDashboardContainer>
            <DashboardTitle>Admin Dashboard</DashboardTitle>
            <UserList>
                {users.map((user) => (
                    <UserItem key={user._id}>
                        <UserInfo>
                            {user.name} - {user.email}
                        </UserInfo>
                        <DeleteButton onClick={() => handleDelete(user._id)} aria-label="Delete User">
                            <FaTrashAlt />
                        </DeleteButton>
                    </UserItem>
                ))}
            </UserList>
        </AdminDashboardContainer>
    );
};

// Styled Components
const AdminDashboardContainer = styled.div`
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
`;

const DashboardTitle = styled.h1`
    text-align: center; 
    margin-bottom: 20px; 
`;

const UserList = styled.ul`
    list-style: none;
    padding: 0;
`;

const UserItem = styled.li`
    display: flex;
    justify-content: space-between;
    align-items: center; 
    padding: 15px;
    border-bottom: 1px solid #eee; 

    &:hover {
        background-color: #f9f9f9; 
    }
`;

const UserInfo = styled.span`
    font-weight: 500; 
`;

const DeleteButton = styled.button`
    background-color: #dc3545; 
    color: white;
    border: none;
    padding: 8px 12px; 
    cursor: pointer;
    border-radius: 5px;
    display: flex;
    align-items: center; 
    transition: background-color 0.2s ease; 

    &:hover {
        background-color: #c82333; 
    }

    svg { 
        font-size: 1.1em; 
    }
`;

const Loading = styled.p`
  text-align: center;
  font-style: italic;
  color: #777;
`;

const ErrorText = styled.p`
  color: #dc3545;
  text-align: center;
  font-weight: bold;
`;

export default AdminDashboard;