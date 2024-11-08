// ~/legal-doc-system/client/src/features/admin/pages/AdminPanel.jsx

import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useDispatch, useSelector } from 'react-redux';
import { fetchAllUsers, updateUser, deleteUser } from '../reducers/adminSlice';
import { FaEdit, FaTrash, FaPlus } from 'react-icons/fa';
import { Modal, Box, Button, TextField } from '@mui/material';

const AdminContainer = styled.div`
  padding: var(--spacing-lg);
  background-color: var(--background-color);
  min-height: 100vh;
`;

const AdminHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
`;

const AdminTitle = styled.h1`
  font-size: 2.5rem;
  color: var(--primary-color);
`;

const AddUserButton = styled(Button)`
  && {
    background-color: var(--primary-color);
    color: #fff;
    &:hover {
      background-color: var(--secondary-color);
    }
  }
`;

const UsersTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-top: var(--spacing-md);
`;

const TableHeader = styled.th`
  padding: var(--spacing-sm);
  border: 1px solid var(--accent-color);
  background-color: var(--secondary-color);
  color: var(--light-color);
  text-align: left;
`;

const TableData = styled.td`
  padding: var(--spacing-sm);
  border: 1px solid var(--accent-color);
  color: var (--text-color);
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  margin-right: var(--spacing-sm);
  font-size: 1.2rem;

  &:hover {
    color: var(--secondary-color);
  }

  &:last-child {
    margin-right: 0;
  }
`;

const Loading = styled.div`
  text-align: center;
  font-size: 1.5rem;
  color: var(--primary-color);
`;

const ErrorMessage = styled.p`
  color: var(--error-color);
  text-align: center;
  font-size: 1.2rem;
`;

const AdminPanel = () => {
  const dispatch = useDispatch();
  const { users, loading, error } = useSelector((state) => state.admin);
  const [openModal, setOpenModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  useEffect(() => {
    dispatch(fetchAllUsers());
  }, [dispatch]);

  const handleEdit = (user) => {
    console.log('Edit user:', user); // Log the user to be edited
    setSelectedUser(user);
    setOpenModal(true);
  };

  const handleCloseModal = () => {
    console.log('Close modal'); // Log when the modal is closed
    setOpenModal(false);
    setSelectedUser(null);
  };

  const handleSave = () => {
    console.log('Save user:', selectedUser); // Log the user to be saved
    dispatch(updateUser(selectedUser));
    handleCloseModal();
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    console.log('Change input:', name, value); // Log input changes
    setSelectedUser((prev) => ({ ...prev, [name]: value }));
  };

  const handleDelete = (userId) => {
    console.log('Delete user ID:', userId); // Log the user ID to be deleted
    if (window.confirm('Are you sure you want to delete this user?')) {
      dispatch(deleteUser(userId));
    }
  };

  if (loading) {
    return <Loading>Loading Users...</Loading>;
  }

  if (error) {
    console.error('Error:', error); // Log any errors
    return <ErrorMessage>{error}</ErrorMessage>;
  }

  return (
    <AdminContainer>
      <AdminHeader>
        <AdminTitle>Admin Panel</AdminTitle>
        <AddUserButton startIcon={<FaPlus />}>Add User</AddUserButton>
      </AdminHeader>
      <UsersTable>
        <thead>
          <tr>
            <TableHeader>ID</TableHeader>
            <TableHeader>Name</TableHeader>
            <TableHeader>Email</TableHeader>
            <TableHeader>Role</TableHeader>
            <TableHeader>Actions</TableHeader>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <TableData>{user.id}</TableData>
              <TableData>{user.name}</TableData>
              <TableData>{user.email}</TableData>
              <TableData>{user.role}</TableData>
              <TableData>
                <ActionButton onClick={() => handleEdit(user)} aria-label="Edit User">
                  <FaEdit />
                </ActionButton>
                <ActionButton onClick={() => handleDelete(user.id)} aria-label="Delete User">
                  <FaTrash />
                </ActionButton>
              </TableData>
            </tr>
          ))}
        </tbody>
      </UsersTable>

      <Modal open={openModal} onClose={handleCloseModal}>
        <Box sx={{ p: 4, bgcolor: 'background.paper', borderRadius: 1 }}>
          <h2>Edit User</h2>
          {selectedUser && (
            <>
              <TextField
                label="Name"
                name="name"
                value={selectedUser.name}
                onChange={handleChange}
                fullWidth
                margin="normal"
              />
              <TextField
                label="Email"
                name="email"
                value={selectedUser.email}
                onChange={handleChange}
                fullWidth
                margin="normal"
              />
              <TextField
                label="Role"
                name="role"
                value={selectedUser.role}
                onChange={handleChange}
                fullWidth
                margin="normal"
              />
              <Button variant="contained" color="primary" onClick={handleSave}>
                Save
              </Button>
              <Button variant="outlined" color="secondary" onClick={handleCloseModal}>
                Cancel
              </Button>
            </>
          )}
        </Box>
      </Modal>
    </AdminContainer>
  );
};

export default AdminPanel;
