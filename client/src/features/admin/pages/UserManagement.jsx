/**
 * File: client/src/features/admin/pages/UserManagement.jsx
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | Enterprise Identity Governance (Clean Build)
 * -----------------------------------------------------------------------------
 */

import React, { useEffect, useState, useCallback, useMemo } from 'react';
import styled from 'styled-components';
import { useDispatch, useSelector } from 'react-redux';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import io from 'socket.io-client';
import {
  FiUserPlus, FiShield, FiEdit3, FiTrash2, FiSearch, FiCheckCircle, FiXCircle, FiSave, FiX
} from 'react-icons/fi';

import {
  fetchAllUsers, createUser, updateUser, deleteUser,
  addUserFromSocket, updateUserFromSocket, removeUserFromSocket,
} from '../reducers/adminSlice';

import Button from '../../../components/StyledButton';
import LoadingSpinner from '../../../components/LoadingSpinner';

// --- CONFIGURATION ---
const USERS_PER_PAGE = 8;
const SOCKET_URL = process.env.REACT_APP_GATEWAY_URL || 'http://localhost:3001';

const UserSchema = Yup.object({
  name: Yup.string().min(2, 'Too Short').required('Full Name is required'),
  email: Yup.string().email('Invalid email').required('Email is required'),
  role: Yup.string().required('Role is required'),
});

const UserManagement = () => {
  const dispatch = useDispatch();
  const { users, loading, error } = useSelector((s) => s?.admin) || { users: [], loading: false, error: null };

  const [search, setSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [modal, setModal] = useState({ type: null, data: null }); // 'form' | 'delete' | 'perms'

  // --- ACTIONS ---
  const refreshUsers = useCallback(() => {
    dispatch(fetchAllUsers());
  }, [dispatch]);

  useEffect(() => {
    refreshUsers();
    const socket = io(SOCKET_URL);
    socket.on('user-created', (u) => dispatch(addUserFromSocket(u)));
    socket.on('user-updated', (u) => dispatch(updateUserFromSocket(u)));
    socket.on('user-deleted', (id) => dispatch(removeUserFromSocket(id)));
    return () => socket.disconnect();
  }, [refreshUsers]);

  // --- LOGIC ---
  const filteredUsers = useMemo(() => {
    const q = search.toLowerCase();
    return (users || []).filter(u =>
      u.name?.toLowerCase().includes(q) || u.email?.toLowerCase().includes(q)
    );
  }, [search, users]);

  const paginatedUsers = useMemo(() => {
    const start = (currentPage - 1) * USERS_PER_PAGE;
    return filteredUsers.slice(start, start + USERS_PER_PAGE);
  }, [filteredUsers, currentPage]);

  const handleFormSubmit = async (values) => {
    if (values._id || values.id) {
      await dispatch(updateUser({ userId: values._id || values.id, userData: values }));
    } else {
      await dispatch(createUser(values));
    }
    setModal({ type: null, data: null });
  };

  if (loading && users.length === 0) return <LoadingSpinner />;

  return (
    <Container>
      {error && <ErrorBanner>⚠️ {error}</ErrorBanner>}

      <Header>
        <div className="title-group">
          <h2>Registry Governance</h2>
          <p>Managing {users.length} identity records across the fleet.</p>
        </div>
        <Button variant="primary" onClick={() => setModal({ type: 'form', data: null })}>
          <FiUserPlus /> Add New Agent
        </Button>
      </Header>

      <ControlBar>
        <SearchWrapper>
          <FiSearch />
          <input
            placeholder="Search agents... (Cmd+K)"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setCurrentPage(1); }}
          />
        </SearchWrapper>
      </ControlBar>

      <RegistryTable>
        <thead>
          <tr>
            <th>Agent Identity</th>
            <th>Role</th>
            <th>Status</th>
            <th style={{ textAlign: 'right' }}>Management</th>
          </tr>
        </thead>
        <tbody>
          {paginatedUsers.map((user) => (
            <tr key={user._id || user.id}>
              <td>
                <div className="user-cell">
                  <Avatar>{user.name?.charAt(0)}</Avatar>
                  <div>
                    <div className="name">{user.name}</div>
                    <div className="email">{user.email}</div>
                  </div>
                </div>
              </td>
              <td><RoleTag $role={user.role}>{user.role}</RoleTag></td>
              <td>
                <Status $active={user.status === 'active'}>
                  {user.status === 'active' ? <FiCheckCircle /> : <FiXCircle />}
                  {user.status || 'Active'}
                </Status>
              </td>
              <td style={{ textAlign: 'right' }}>
                <ActionGroup>
                  <IconButton onClick={() => setModal({ type: 'form', data: user })}><FiEdit3 /></IconButton>
                  <IconButton onClick={() => setModal({ type: 'perms', data: user })}><FiShield /></IconButton>
                  <IconButton $danger onClick={() => {
                    if (window.confirm('Expunge record?')) dispatch(deleteUser(user._id || user.id));
                  }}><FiTrash2 /></IconButton>
                </ActionGroup>
              </td>
            </tr>
          ))}
        </tbody>
      </RegistryTable>

      {/* --- FORM MODAL --- */}
      {modal.type === 'form' && (
        <Overlay onClick={() => setModal({ type: null, data: null })}>
          <ModalContent onClick={e => e.stopPropagation()}>
            <h3>{modal.data ? 'Update Profile' : 'Provision Agent'}</h3>
            <Formik
              initialValues={modal.data || { name: '', email: '', role: 'associate' }}
              validationSchema={UserSchema}
              onSubmit={handleFormSubmit}
            >
              <Form>
                <div className="field">
                  <label>Full Name</label>
                  <Field name="name" placeholder="John Doe" />
                  <ErrorMessage name="name" component="small" />
                </div>
                <div className="field">
                  <label>Email Address</label>
                  <Field name="email" type="email" placeholder="john@wilsy.com" />
                  <ErrorMessage name="email" component="small" />
                </div>
                <div className="field">
                  <label>Role</label>
                  <Field as="select" name="role">
                    <option value="associate">Associate</option>
                    <option value="lawyer">Lawyer</option>
                    <option value="sheriff">Sheriff</option>
                    <option value="admin">Admin</option>
                  </Field>
                </div>
                <div className="actions">
                  <Button type="button" ghost onClick={() => setModal({ type: null, data: null })}>Cancel</Button>
                  <Button type="submit" variant="primary">Save Changes</Button>
                </div>
              </Form>
            </Formik>
          </ModalContent>
        </Overlay>
      )}
    </Container>
  );
};

// --- STYLED COMPONENTS (Investor-Ready) ---
const Container = styled.div` padding: 2rem; `;
const Header = styled.header` display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; h2 { font-weight: 800; color: #0F172A; margin: 0; } p { color: #64748B; font-size: 0.9rem; margin: 4px 0; } `;
const ControlBar = styled.div` background: white; padding: 1rem; border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid #E2E8F0; `;
const SearchWrapper = styled.div` position: relative; max-width: 400px; svg { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94A3B8; } input { width: 100%; padding: 10px 12px 10px 40px; border: 1px solid #E2E8F0; border-radius: 8px; } `;
const RegistryTable = styled.table` width: 100%; border-collapse: separate; border-spacing: 0; background: white; border-radius: 12px; border: 1px solid #E2E8F0; overflow: hidden; th { background: #F8FAFC; padding: 1rem 1.5rem; text-align: left; font-size: 0.75rem; text-transform: uppercase; color: #64748B; border-bottom: 1px solid #E2E8F0; } td { padding: 1rem 1.5rem; border-bottom: 1px solid #F1F5F9; } .user-cell { display: flex; align-items: center; gap: 12px; .name { font-weight: 700; color: #0F172A; } .email { color: #64748B; font-size: 0.85rem; } } `;
const Avatar = styled.div` width: 36px; height: 36px; background: #E2E8F0; border-radius: 50%; display: grid; place-items: center; font-weight: 800; color: #475569; `;
const RoleTag = styled.span` padding: 4px 10px; border-radius: 99px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; background: ${props => props.$role === 'admin' ? '#DBEAFE' : '#F1F5F9'}; color: ${props => props.$role === 'admin' ? '#1E40AF' : '#475569'}; `;
const Status = styled.span` display: flex; align-items: center; gap: 6px; font-size: 0.85rem; font-weight: 600; color: ${props => props.$active ? '#10B981' : '#EF4444'}; `;
const ActionGroup = styled.div` display: flex; gap: 8px; justify-content: flex-end; `;
const IconButton = styled.button` background: transparent; border: none; padding: 8px; border-radius: 6px; color: #64748B; cursor: pointer; transition: 0.2s; &:hover { background: #F1F5F9; color: ${props => props.$danger ? '#EF4444' : '#0F172A'}; } `;
const Overlay = styled.div` position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(4px); display: grid; place-items: center; z-index: 1000; `;
const ModalContent = styled.div` background: white; padding: 2rem; border-radius: 16px; width: 100%; max-width: 450px; h3 { margin-top: 0; font-weight: 800; } .field { margin-bottom: 1rem; label { display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 4px; } input, select { width: 100%; padding: 10px; border: 1px solid #E2E8F0; border-radius: 8px; } small { color: #EF4444; font-size: 0.75rem; } } .actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 2rem; } `;
const ErrorBanner = styled.div` background: #FEE2E2; color: #B91C1C; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; font-weight: 600; `;

export default UserManagement;