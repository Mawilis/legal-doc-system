import React from 'react';
import { Link } from 'react-router-dom';

export default function HeaderSimple() {
  return (
    <header style={{
      height:56, display:'flex', alignItems:'center', gap:16,
      padding:'0 16px', borderBottom:'1px solid #eee', background:'#fff'
    }}>
      <strong>Legal Doc System</strong>
      <nav style={{display:'flex', gap:12}}>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/documents">Documents</Link>
        <Link to="/profile">Profile</Link>
        <Link to="/admin">Admin</Link>
        <Link to="/admin/sheriff">Sheriff</Link>
        <Link to="/admin/analytics">Analytics</Link>
      </nav>
    </header>
  );
}
