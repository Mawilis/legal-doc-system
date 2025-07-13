// ~/legal-doc-system/client/src/features/admin/pages/AdminPanel.jsx

import React, { useEffect, useState, useCallback } from "react";
import styled from "styled-components";
import { useDispatch, useSelector } from "react-redux";
import {
  fetchAllUsers,
  updateUser,
  deleteUser,
} from "../reducers/adminSlice";
import { FaEdit, FaTrash, FaPlus } from "react-icons/fa";
import {
  Modal,
  Box,
  Button,
  TextField,
  Typography,
} from "@mui/material";

const AdminContainer = styled.div`
  padding: 20px;
  background-color: #f9f9f9; // Light background color
  min-height: 100vh;
`;

const AdminHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const AdminTitle = styled.h1`
  font-size: 2.5rem;
  color: #333; // Dark text color
`;

const AddUserButton = styled(Button)`
  && {
    background-color: #007bff; // Primary button color
    color: #fff;

    &:hover {
      background-color: #0062cc; // Darker shade on hover
    }
  }
`;

const UsersTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
`;

const TableHeader = styled.th`
  padding: 10px;
  border: 1px solid #ddd; // Subtle border
  background-color: #f5f5f5; // Light background for header
  color: #333;
  text-align: left;
  font-weight: 500; // Slightly bolder font
`;

const TableData = styled.td`
  padding: 10px;
  border: 1px solid #ddd;
  color: #555; // Slightly lighter text color
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  color: #007bff; // Primary color for icons
  cursor: pointer;
  margin-right: 10px;
  font-size: 1.2rem;
  transition: color 0.2s ease; // Add transition for hover effect

  &:hover {
    color: #0062cc; // Darker shade on hover
  }

  &:last-child {
    margin-right: 0;
  }
`;

const Loading = styled.div`
  text-align: center;
  font-size: 1.5rem;
  color: #007bff; // Primary color for loading message
`;

const ErrorMessage = styled.p`
  color: #dc3545; // Error color
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

  const handleEdit = useCallback((user) => {
    setSelectedUser(user);
    setOpenModal(true);
  }, []);

  const handleCloseModal = useCallback(() => {
    setOpenModal(false);
    setSelectedUser(null);
  }, []);

  const handleSave = useCallback(() => {
    dispatch(updateUser(selectedUser));
    handleCloseModal();
  }, [dispatch, selectedUser, handleCloseModal]);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setSelectedUser((prev) => ({ ...prev, [name]: value }));
  }, []);

  const handleDelete = useCallback(
    (userId) => {
      if (window.confirm("Are you sure you want to delete this user?")) {
        dispatch(deleteUser(userId));
      }
    },
    [dispatch]
  );

  if (loading) {
    return <Loading>Loading Users...</Loading>;
  }

  if (error) {
    return <ErrorMessage>{error}</ErrorMessage>;
  }

  return (
    <AdminContainer>
      <AdminHeader>
        <AdminTitle>Admin Panel</AdminTitle>
        <AddUserButton
          startIcon={<FaPlus />}
          onClick={() => {
            // Handle add user logic here
            // For example, you can open a modal to add a new user
            setOpenModal(true);
            setSelectedUser({ name: "", email: "", role: "" });
          }}
        >
          Add User
        </AddUserButton>
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
                <ActionButton
                  onClick={() => handleEdit(user)}
                  aria-label="Edit User"
                >
                  <FaEdit />
                </ActionButton>
                <ActionButton
                  onClick={() => handleDelete(user.id)}
                  aria-label="Delete User"
                >
                  <FaTrash />
                </ActionButton>
              </TableData>
            </tr>
          ))}
        </tbody>
      </UsersTable>

      <Modal open={openModal} onClose={handleCloseModal}>
        <Box
          sx={{
            p: 4,
            bgcolor: "background.paper",
            borderRadius: 1,
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: 400,
          }}
        >
          <Typography variant="h5" component="h2" gutterBottom>
            {selectedUser && selectedUser.id ? "Edit User" : "Add User"}
          </Typography>
          {selectedUser && (
            <form>
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
              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  marginTop: "20px",
                }}
              >
                <Button
                  variant="outlined"
                  color="secondary"
                  onClick={handleCloseModal}
                  sx={{ mr: 2 }}
                >
                  Cancel
                </Button>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleSave}
                >
                  Save
                </Button>
              </div>
            </form>
          )}
        </Box>
      </Modal>
    </AdminContainer>
  );
};

export default AdminPanel;