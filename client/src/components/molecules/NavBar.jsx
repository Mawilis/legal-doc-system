// ~/legal-doc-system/client/src/components/molecules/NavBar.jsx

import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import PropTypes from 'prop-types';
import { useSelector, useDispatch } from 'react-redux';
import { logoutUser } from '../../features/auth/reducers/authSlice';
import { FaUserCircle, FaSignOutAlt, FaUserShield } from 'react-icons/fa';

const NavList = styled.ul`
  display: flex;
  align-items: center;
  list-style: none;
  margin: 0;
  padding: 0;
`;

const NavItem = styled.li`
  margin-right: ${({ theme }) => theme.spacing.md};
`;

const StyledLink = styled(NavLink)`
  color: ${({ theme }) => theme.colors.text};
  text-decoration: none;
  font-size: ${({ theme }) => theme.typography.fontSize};
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
  border-radius: 5px;
  transition: background-color 0.2s ease, color 0.2s ease;

  &:hover {
    background-color: ${({ theme }) => theme.colors.primaryLight};
    color: ${({ theme }) => theme.colors.primary};
  }

  &.active {
    background-color: ${({ theme }) => theme.colors.primary};
    color: ${({ theme }) => theme.colors.background};
  }
`;

const IconLink = styled.button`
  background: none;
  border: none;
  color: ${({ theme }) => theme.colors.text};
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: ${({ theme }) => theme.spacing.sm};
  transition: color 0.2s ease;

  &:hover {
    color: ${({ theme }) => theme.colors.primary};
  }
`;

const NavBar = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { user, token } = useSelector((state) => state.auth);
  const isAuthenticated = Boolean(token);

  const handleLogout = () => {
    dispatch(logoutUser());
    navigate('/login');
  };

  return (
    <NavList>
      <NavItem>
        <StyledLink to="/">Dashboard</StyledLink>
      </NavItem>
      {isAuthenticated ? (
        <>
          {user?.role === 'admin' && (
            <NavItem>
              <StyledLink to="/admin"><FaUserShield /> Admin</StyledLink>
            </NavItem>
          )}
          <NavItem>
            <StyledLink to="/profile"><FaUserCircle /> Profile</StyledLink>
          </NavItem>
          <NavItem>
            <IconLink onClick={handleLogout} title="Logout">
              <FaSignOutAlt />
            </IconLink>
          </NavItem>
        </>
      ) : (
        <NavItem>
          <StyledLink to="/login">Login</StyledLink>
        </NavItem>
      )}
    </NavList>
  );
};

NavBar.propTypes = {
  isAuthenticated: PropTypes.bool,
  userRole: PropTypes.string,
  onLogout: PropTypes.func,
};

export default NavBar;
