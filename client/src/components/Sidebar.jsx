import React from 'react';
import { NavLink } from 'react-router-dom'; // Import NavLink for active styling
import styled from 'styled-components';

const SidebarContainer = styled.div`
    width: 250px;
    background-color: #2c3e50; // Dark background color
    height: 100vh;
    padding-top: 20px;
    position: fixed;
    left: 0;
    top: 0; // Ensure it starts from the top
    overflow-y: auto; // Add vertical scroll if needed
`;

const SidebarLink = styled(NavLink)` // Use NavLink for active styling
    display: block;
    color: white;
    padding: 12px 15px; // Add more padding
    text-decoration: none;
    transition: background-color 0.2s ease; // Add smooth transition

    &:hover {
        background-color: #34495e;
    }

    &.active { // Style the active link
        background-color: #1abc9c; // Example active color
        font-weight: bold;
    }
`;

const Sidebar = () => {
    return (
        <SidebarContainer>
            <SidebarLink to="/">Dashboard</SidebarLink>
            <SidebarLink to="/admin">Admin Panel</SidebarLink>
            <SidebarLink to="/documents">Documents</SidebarLink>
            {/* Add more links as needed */}
        </SidebarContainer>
    );
};

export default Sidebar;