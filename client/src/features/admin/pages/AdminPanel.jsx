import React from 'react';
import { useSelector } from 'react-redux';
import AdminDashboard from '../../../components/AdminDashboard';

export default function AdminPanel() {
  const { user } = useSelector((s) => s?.auth || {});
  if (!user) return <div style={{padding:24}}>Loading user…</div>;
  if (user.role !== 'admin') return <div style={{padding:24}}>You do not have permission to view this page.</div>;
  return <AdminDashboard />;
}
