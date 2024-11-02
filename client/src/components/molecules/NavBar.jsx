import React from 'react';
import { Link } from 'react-router-dom';
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

const StyledLink = styled(Link)`
  color: ${({ theme }) => theme.colors.text};
  text-decoration: none;
  font-size: ${({ theme }) => theme.typography.fontSize};
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
  border-radius: 5px;

  &:hover {
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
                <NavItem><StyledLink as="button" onClick={onLogout}>Logout</StyledLink></NavItem>
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
