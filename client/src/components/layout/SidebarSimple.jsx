import React from 'react';
import { NavLink } from 'react-router-dom';
import styled from 'styled-components';

const Wrap = styled.nav`
  border-right:1px solid #eee; padding:12px; height:100%;
`;
const Item = styled(NavLink)`
  display:flex; align-items:center; gap:10px; padding:10px 12px; border-radius:8px;
  text-decoration:none; color:#222;
  &.active { background:#f3f4f6; font-weight:600; }
  &:hover { background:#f8fafc; }
`;

export default function SidebarSimple(){
  const links = [
    { to:'/dashboard', label:'Dashboard' },
    { to:'/documents', label:'Documents' },
    { to:'/profile', label:'Profile' },
    { to:'/chat', label:'Chat' },
    { to:'/search', label:'Search' },
    { to:'/settings', label:'Settings' },
    { to:'/admin', label:'Admin Panel' },
    { to:'/admin/users', label:'User Management' },
    { to:'/admin/geofencing', label:'Geofencing' },
    { to:'/admin/analytics', label:'Admin Analytics' },
    { to:'/sheriff/dashboard', label:'Sheriff Dashboard' },
    { to:'/sheriff/tracking', label:'Sheriff Tracking' },
    { to:'/sheriff/analytics', label:'Sheriff Analytics' },
  ];
  return (
    <Wrap>
      {links.map((l)=>(
        <Item key={l.to} to={l.to}>{l.label}</Item>
      ))}
    </Wrap>
  );
}
