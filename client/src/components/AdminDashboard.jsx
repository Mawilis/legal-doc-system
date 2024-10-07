import React, { useEffect, useState } from 'react';
import { getAllUsers, deleteUser } from '../services/adminService';
import styled from 'styled-components'; // Import styled-components

const AdminDashboard = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                setLoading(true); // Set loading to true
                const data = await getAllUsers();
                setUsers(data);
            } catch (error) {
                console.error('Failed to fetch users', error);
                setError('Failed to fetch users'); // Set error message
            } finally {
                setLoading(false); // Set loading to false once the data is fetched
            }
        };

        fetchUsers();
    }, []);

    const handleDelete = async (userId) => {
        const confirmDelete = window.confirm('Are you sure you want to delete this user?');
        if (!confirmDelete) return;

        try {
            await deleteUser(userId);
            setUsers(users.filter(user => user._id !== userId));
        } catch (error) {
            console.error('Failed to delete user', error);
            setError('Failed to delete user'); // Set error message for delete failure
        }
    };

    if (loading) return <p>Loading users...</p>;
    if (error) return <p>{error}</p>;

    return (
        <AdminDashboardContainer>
            <h1>Admin Dashboard</h1>
            <UserList>
                {users.map((user) => (
                    <UserItem key={user._id}>
                        <UserInfo>
                            {user.name} - {user.email}
                        </UserInfo>
                        <DeleteButton onClick={() => handleDelete(user._id)}>Delete</DeleteButton>
                    </UserItem>
                ))}
            </UserList>
        </AdminDashboardContainer>
    );
};

// Styled Components Definitions
const AdminDashboardContainer = styled.div`
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
`;

const UserList = styled.ul`
    list-style: none;
    padding: 0;
`;

const UserItem = styled.li`
    display: flex;
    justify-content: space-between;
    padding: 10px;
    border-bottom: 1px solid #ddd;
`;

const UserInfo = styled.span`
    font-weight: bold;
`;

const DeleteButton = styled.button`
    background-color: #ff4d4f;
    color: white;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
    border-radius: 5px;

    &:hover {
        background-color: #ff7875;
    }
`;

export default AdminDashboard;
