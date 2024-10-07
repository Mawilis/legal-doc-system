import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const SidebarContainer = styled.div`
    width: 250px;
    background-color: #2c3e50;
    height: 100vh;
    padding-top: 20px;
    position: fixed;
    left: 0;
`;

const SidebarLink = styled(Link)`
    display: block;
    color: white;
    padding: 10px 15px;
    text-decoration: none;
    &:hover {
        background-color: #34495e;
    }
`;

const Sidebar = () => {
    return (
        <SidebarContainer>
            <SidebarLink to="/">Dashboard</SidebarLink>
            <SidebarLink to="/admin">Admin Panel</SidebarLink>
            <SidebarLink to="/documents">Documents</SidebarLink>
        </SidebarContainer>
    );
};

export default Sidebar;
