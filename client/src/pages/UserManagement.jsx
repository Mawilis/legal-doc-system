// UserManagement.jsx
import React, { useEffect, useState } from 'react';
import { getAllUsers, deleteUser } from '../services/adminService';
import styled from 'styled-components';

const UserManagementContainer = styled.div`
    padding: 20px;
`;

const UserItem = styled.div`
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
`;

const DeleteButton = styled.button`
    background-color: red;
    color: white;
    padding: 5px 10px;
    border: none;
    cursor: pointer;
    border-radius: 5px;
`;

const UserManagement = () => {
    const [users, setUsers] = useState([]);

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const data = await getAllUsers();
                setUsers(data);
            } catch (err) {
                console.error('Error fetching users', err);
            }
        };

        fetchUsers();
    }, []);

    const handleDelete = async (userId) => {
        try {
            await deleteUser(userId);
            setUsers(users.filter(user => user._id !== userId));
        } catch (err) {
            console.error('Error deleting user', err);
        }
    };

    return (
        <UserManagementContainer>
            <h1>User Management</h1>
            <ul>
                {users.map((user) => (
                    <UserItem key={user._id}>
                        {user.name} - {user.email}
                        <DeleteButton onClick={() => handleDelete(user._id)}>Delete</DeleteButton>
                    </UserItem>
                ))}
            </ul>
        </UserManagementContainer>
    );
};

export default UserManagement;
