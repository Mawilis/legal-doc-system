// /Users/wilsonkhanyezi/legal-doc-system/client/src/components/molecules/NavBar.jsx

import React from 'react';
import { NavLink } from 'react-router-dom'; // Use NavLink for active link styling
import styled from 'styled-components';
import PropTypes from 'prop-types';

const NavList = styled.ul`
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
`;

const NavItem = styled.li`
  margin-right: ${({ theme }) => theme.spacing.md};
`;

const StyledLink = styled(NavLink)` // Use NavLink
  color: ${({ theme }) => theme.colors.text};
  text-decoration: none;
  font-size: ${({ theme }) => theme.typography.fontSize};
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
  border-radius: 5px;
  transition: background-color 0.2s ease, color 0.2s ease; // Add transitions

  &:hover {
    background-color: ${({ theme }) => theme.colors.primaryLight}; // Use a lighter shade on hover
    color: ${({ theme }) => theme.colors.primary};
  }

  &.active { // Style the active link
    background-color: ${({ theme }) => theme.colors.primary};
    color: ${({ theme }) => theme.colors.background};
  }
`;

const NavBar = ({ isAuthenticated, userRole, onLogout }) => (
  <NavList>
    <NavItem><StyledLink to="/">Dashboard</StyledLink></NavItem>
    {isAuthenticated ? (
      <>
        {userRole === 'admin' && (
          <NavItem><StyledLink to="/admin">Admin Panel</StyledLink></NavItem>
        )}
        <NavItem><StyledLink to="/profile">Profile</StyledLink></NavItem>
        <NavItem>
          <StyledLink as="button" onClick={onLogout}>
            Logout
          </StyledLink>
        </NavItem>
      </>
    ) : (
      <NavItem><StyledLink to="/login">Login</StyledLink></NavItem>
    )}
  </NavList>
);

NavBar.propTypes = {
  isAuthenticated: PropTypes.bool.isRequired,
  userRole: PropTypes.string,
  onLogout: PropTypes.func.isRequired,
};

NavBar.defaultProps = {
  userRole: '',
};

export default NavBar;