import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';

export default function ProtectedRoute({ children }) {
  const location = useLocation();
  const { isAuthenticated } = useSelector((s) => s.auth);

  // Fallback to localStorage in case Redux hasn't hydrated yet
  const token = localStorage.getItem('token');
  const allowed = isAuthenticated || !!token;

  if (!allowed) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return children;
}
