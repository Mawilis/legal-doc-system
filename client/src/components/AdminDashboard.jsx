// ~/client/src/components/AdminDashboard.jsx
import React, { useEffect, useState, useCallback, useMemo } from 'react';
import styled from 'styled-components';
import { getAllUsers, deleteUser, updateUser as updateUserApi } from '../services/adminService';
import { toast } from 'react-toastify';

const USERS_PER_PAGE = 5;

// Minimal trash icon (no external deps)
const TrashIcon = (props) => (
  <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false" {...props}>
    <path d="M9 3h6l1 2h4v2H4V5h4l1-2zm1 6h2v9h-2V9zm4 0h2v9h-2V9zM7 9h2v9H7V9z" fill="currentColor"/>
  </svg>
);

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isConfirmOpen, setConfirmOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('[AdminDashboard] fetching users…');
      const list = await getAllUsers();
      console.log('[AdminDashboard] users result:', list);
      setUsers(Array.isArray(list) ? list : []);
    } catch (err) {
      const msg = err?.message || 'Failed to fetch users';
      console.error('[AdminDashboard] fetch error:', msg);
      setError(msg);
      try { toast.error(msg); } catch {}
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const filteredUsers = useMemo(() => {
    const s = search.toLowerCase();
    return (users || []).filter(u =>
      `${u.name||''}`.toLowerCase().includes(s) ||
      `${u.email||''}`.toLowerCase().includes(s)
    );
  }, [users, search]);

  const paginated = useMemo(() => {
    const start = (currentPage - 1) * USERS_PER_PAGE;
    return filteredUsers.slice(start, start + USERS_PER_PAGE);
  }, [filteredUsers, currentPage]);

  const promptDelete = (user) => { setUserToDelete(user); setConfirmOpen(true); };

  const handleDelete = async () => {
    if (!userToDelete) return;
    try {
      await deleteUser(userToDelete._id || userToDelete.id);
      setUsers(prev => prev.filter(u => (u._id||u.id) !== (userToDelete._id||userToDelete.id)));
      try { toast.success('User deleted'); } catch {}
    } catch (err) {
      const msg = err?.message || 'Delete failed';
      console.error('[AdminDashboard] delete error:', msg);
      try { toast.error(msg); } catch {}
    } finally {
      setConfirmOpen(false);
      setUserToDelete(null);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await updateUserApi(userId, { role: newRole });
      setUsers(prev => prev.map(u => (u._id===userId||u.id===userId) ? { ...u, role: newRole } : u));
      try { toast.success('Role updated'); } catch {}
    } catch (err) {
      const msg = err?.message || 'Role update failed';
      console.error('[AdminDashboard] role update error:', msg);
      try { toast.error(msg); } catch {}
    }
  };

  if (loading) return <Placeholder>Loading users…</Placeholder>;
  if (error) return <Placeholder>Error: {error}</Placeholder>;

  const totalPages = Math.max(1, Math.ceil(filteredUsers.length / USERS_PER_PAGE));

  return (
    <Wrapper>
      <Header>
        <Title>Admin Dashboard</Title>
        <Right>
          <SearchInput
            placeholder="Search by name or email…"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setCurrentPage(1); }}
          />
        </Right>
      </Header>

      {users.length === 0 ? (
        <Placeholder>No users yet or you are not authorized.</Placeholder>
      ) : (
        <>
          <UserTable>
            <thead>
              <tr><th>Name</th><th>Email</th><th>Role</th><th>Action</th></tr>
            </thead>
            <tbody>
              {paginated.map(u => (
                <tr key={u._id || u.id}>
                  <td>{u.name}</td>
                  <td>{u.email}</td>
                  <td>
                    <RoleSelect
                      value={u.role || 'user'}
                      onChange={(e) => handleRoleChange(u._id || u.id, e.target.value)}
                    >
                      <option value="user">User</option>
                      <option value="admin">Admin</option>
                    </RoleSelect>
                  </td>
                  <td>
                    <ActionButton onClick={() => promptDelete(u)} title="Delete">
                      <TrashIcon />
                    </ActionButton>
                  </td>
                </tr>
              ))}
            </tbody>
          </UserTable>

          <Pagination>
            {Array.from({ length: totalPages }, (_, i) => (
              <PageBtn
                key={i}
                $active={i + 1 === currentPage}
                onClick={() => setCurrentPage(i + 1)}
              >
                {i + 1}
              </PageBtn>
            ))}
          </Pagination>
        </>
      )}

      {isConfirmOpen && (
        <ModalOverlay onClick={() => setConfirmOpen(false)}>
          <ModalBox onClick={(e) => e.stopPropagation()}>
            <h3>Confirm Deletion</h3>
            <p>Delete user “{userToDelete?.name}”?</p>
            <Row>
              <ActionButton onClick={() => setConfirmOpen(false)}>Cancel</ActionButton>
              <ActionButton danger onClick={handleDelete}>Confirm</ActionButton>
            </Row>
          </ModalBox>
        </ModalOverlay>
      )}
    </Wrapper>
  );
};

const Wrapper = styled.div`padding:2rem;`;
const Header = styled.div`display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;`;
const Right = styled.div`display:flex;gap:.5rem;align-items:center;`;
const Title = styled.h2`margin:0;`;
const SearchInput = styled.input`padding:.5rem .75rem;border:1px solid #ccc;border-radius:6px;min-width:260px;`;
const Placeholder = styled.div`padding:24px;text-align:center;color:#666;`;

const UserTable = styled.table`
  width:100%; border-collapse:collapse; background:#fff; border:1px solid #eee;
  th, td { padding:12px; border-bottom:1px solid #eee; text-align:left; }
  th { background:#fafafa; }
`;

const RoleSelect = styled.select`padding:.4rem .6rem;`;
const Pagination = styled.div`display:flex; gap:.5rem; justify-content:center; margin-top:1rem;`;
const PageBtn = styled.button`
  padding:6px 10px; border:1px solid ${({$active}) => $active ? '#007bff' : '#ccc'};
  background:${({$active}) => $active ? '#007bff' : '#fff'};
  color:${({$active}) => $active ? '#fff' : '#333'};
  border-radius:6px; cursor:pointer;
`;

const ActionButton = styled.button`
  display:inline-flex; align-items:center; gap:.4rem; padding:8px 12px;
  border:1px solid ${p => p.danger ? '#dc3545' : '#007bff'};
  background:${p => p.danger ? '#dc3545' : '#007bff'};
  color:#fff; border-radius:6px; cursor:pointer;
`;

const ModalOverlay = styled.div`
  position:fixed; inset:0; background:rgba(0,0,0,.5);
  display:flex; align-items:center; justify-content:center; z-index:1000;
`;
const ModalBox = styled.div`background:#fff; padding:20px; border-radius:10px; min-width:320px;`;
const Row = styled.div`display:flex; gap:.5rem; justify-content:flex-end; margin-top:1rem;`;

export default AdminDashboard;
