import React, { useEffect } from 'react';
import styled from 'styled-components';
import { useDispatch, useSelector } from 'react-redux';
import { fetchAllUsers, deleteUser, createUser } from '../reducers/adminSlice';
import { FaEdit, FaTrash, FaPlus } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import { Button, TableContainer, Table, TableHead, TableRow, TableCell, Paper, TableBody, Box, Typography, Modal, TextField, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { Formik, ErrorMessage } from 'formik';
import { toast } from 'react-toastify';
import * as Yup from 'yup';

// Styled Components
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
    border-radius: var(--border-radius);
    &:hover {
      background-color: var(--secondary-color);
    }
  }
`;

const Loading = styled.div`
  text-align: center;
  font-size: 1.5rem;
  color: var(--primary-color);
`;

const ErrorText = styled.p`
  color: var(--error-color);
  text-align: center;
  font-size: 1.2rem;
`;

const modalStyle = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 400,
    bgcolor: 'background.paper',
    boxShadow: 24,
    p: 4,
};

const UserManagement = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const { users, loading, error } = useSelector((state) => state.admin);
    const [openAddModal, setOpenAddModal] = React.useState(false);

    useEffect(() => {
        dispatch(fetchAllUsers());
    }, [dispatch]);

    const handleEdit = (user) => {
        navigate(`/admin/users/edit/${user.id}`, { state: { user } });
    };

    const handleDelete = async (userId) => {
        if (window.confirm('Are you sure you want to delete this user?')) {
            try {
                await dispatch(deleteUser(userId)).unwrap();
                toast.success('User deleted successfully!');
            } catch (err) {
                toast.error('Failed to delete user.');
            }
        }
    };

    const handleAddUser = () => {
        setOpenAddModal(true);
    };

    const handleCloseAddModal = () => {
        setOpenAddModal(false);
    };

    if (loading) {
        return <Loading>Loading Users...</Loading>;
    }

    if (error) {
        return <ErrorText>{error}</ErrorText>;
    }

    const validationSchema = Yup.object().shape({
        name: Yup.string().required('Name is required'),
        email: Yup.string().email('Invalid email').required('Email is required'),
        role: Yup.string().required('Role is required'),
    });

    return (
        <AdminContainer>
            <AdminHeader>
                <AdminTitle>User Management</AdminTitle>
                <AddUserButton variant="contained" onClick={handleAddUser} startIcon={<FaPlus />}>
                    Add User
                </AddUserButton>
            </AdminHeader>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>ID</TableCell>
                            <TableCell>Name</TableCell>
                            <TableCell>Email</TableCell>
                            <TableCell>Role</TableCell>
                            <TableCell>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {users.map((user) => (
                            <TableRow key={user.id}>
                                <TableCell>{user.id}</TableCell>
                                <TableCell>{user.name}</TableCell>
                                <TableCell>{user.email}</TableCell>
                                <TableCell>{user.role}</TableCell>
                                <TableCell>
                                    <Button
                                        variant="outlined"
                                        color="primary"
                                        onClick={() => handleEdit(user)}
                                        startIcon={<FaEdit />}
                                    >
                                        Edit
                                    </Button>
                                    <Button
                                        variant="outlined"
                                        color="error"
                                        onClick={() => handleDelete(user.id)}
                                        startIcon={<FaTrash />}
                                    >
                                        Delete
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            {/* Add User Modal */}
            <Modal open={openAddModal} onClose={handleCloseAddModal}>
                <Box sx={modalStyle}>
                    <Typography variant="h6" component="h2">Add New User</Typography>
                    <Formik
                        initialValues={{
                            name: '',
                            email: '',
                            role: '',
                        }}
                        validationSchema={validationSchema}
                        onSubmit={async (values, { resetForm }) => {
                            try {
                                await dispatch(createUser(values)).unwrap();
                                toast.success('User added successfully!');
                                resetForm();
                                handleCloseAddModal();
                            } catch (err) {
                                toast.error('Failed to add user.');
                            }
                        }}
                    >
                        {({ values, handleChange, handleSubmit, errors, touched }) => (
                            <form onSubmit={handleSubmit}>
                                <TextField
                                    label="Name"
                                    name="name"
                                    value={values.name}
                                    onChange={handleChange}
                                    fullWidth
                                    margin="normal"
                                    error={touched.name && !!errors.name}
                                    helperText={touched.name && errors.name}
                                />
                                <TextField
                                    label="Email"
                                    name="email"
                                    value={values.email}
                                    onChange={handleChange}
                                    fullWidth
                                    margin="normal"
                                    error={touched.email && !!errors.email}
                                    helperText={touched.email && errors.email}
                                />
                                <FormControl fullWidth margin="normal">
                                    <InputLabel id="role-label">Role</InputLabel>
                                    <Select
                                        labelId="role-label"
                                        id="role"
                                        name="role"
                                        value={values.role}
                                        onChange={handleChange}
                                        error={touched.role && !!errors.role}
                                    >
                                        <MenuItem value="sheriff">Sheriff</MenuItem>
                                        <MenuItem value="attorney">Attorney</MenuItem>
                                        <MenuItem value="admin">Admin</MenuItem>
                                    </Select>
                                    <ErrorMessage name="role" component={ErrorText} />
                                </FormControl>
                                <Button type="submit" variant="contained" color="primary">Add User</Button>
                                <Button onClick={handleCloseAddModal} variant="outlined" color="secondary">Cancel</Button>
                            </form>
                        )}
                    </Formik>
                </Box>
            </Modal>
        </AdminContainer>
    );
};

export default UserManagement;
