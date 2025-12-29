import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { logoutUser } from '../../features/auth/reducers/authSlice';

export default function AppShell() {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  async function logout() {
    await dispatch(logoutUser());
    navigate('/login', { replace: true });
  }

  return (
    <div style={{minHeight:'100vh', fontFamily:'system-ui, sans-serif'}}>
      <nav style={{padding:12, borderBottom:'1px solid #eee', display:'flex', gap:12, alignItems:'center', flexWrap:'wrap'}}>
        <strong>Legal Doc System</strong>
        <Link to="/login">Login</Link>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/documents">Documents</Link>
        <Link to="/profile">Profile</Link>
        <Link to="/admin">Admin</Link>
        <Link to="/admin/sheriff">Sheriff</Link>
        <Link to="/admin/analytics">Analytics</Link>
        <div style={{marginLeft:'auto'}}>
          <button onClick={logout} style={{padding:'6px 10px', border:'1px solid #ccc', borderRadius:6, cursor:'pointer'}}>
            Logout
          </button>
        </div>
      </nav>
      <main style={{padding:16}}>
        <Outlet />
      </main>
    </div>
  );
}
