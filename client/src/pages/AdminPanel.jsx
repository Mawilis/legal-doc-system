import React, { useState, useEffect } from 'react';
import { getAllUsers, deleteUser } from '../services/adminService';
import styled from 'styled-components';
import io from 'socket.io-client';

// Socket.io initialization
const socket = io('http://localhost:3001');

const AdminPanelContainer = styled.div`
  padding: 20px;
  background-color: #f4f4f9;
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

const AdminPanel = () => {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await getAllUsers();
        setUsers(data);
      } catch (error) {
        console.error('Failed to fetch users', error);
      }
    };

    fetchUsers();

    // Listen for real-time user events
    socket.on('user-created', (newUser) => {
      setUsers(prevUsers => [...prevUsers, newUser]);
    });

    socket.on('user-updated', (updatedUser) => {
      setUsers(prevUsers =>
        prevUsers.map(user => user._id === updatedUser._id ? updatedUser : user)
      );
    });

    socket.on('user-deleted', (deletedUser) => {
      setUsers(prevUsers => prevUsers.filter(user => user._id !== deletedUser._id));
    });

    return () => {
      socket.off('user-created');
      socket.off('user-updated');
      socket.off('user-deleted');
    };
  }, []);

  const handleDelete = async (userId) => {
    try {
      await deleteUser(userId);
      setUsers(users.filter(user => user._id !== userId));
    } catch (error) {
      console.error('Failed to delete user', error);
    }
  };

  return (
    <AdminPanelContainer>
      <h1>Admin Panel</h1>
      <ul>
        {users.map((user) => (
          <UserItem key={user._id}>
            {user.name} - {user.email}
            <DeleteButton onClick={() => handleDelete(user._id)}>Delete</DeleteButton>
          </UserItem>
        ))}
      </ul>
    </AdminPanelContainer>
  );
};

export default AdminPanel;
