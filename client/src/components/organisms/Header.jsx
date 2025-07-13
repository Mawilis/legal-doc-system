// ~/legal-doc-system/client/src/components/organisms/Header.jsx

import React from 'react';
import { NavLink } from 'react-router-dom'; // Import NavLink for active styling
import styled from 'styled-components';
import { useSelector, useDispatch } from 'react-redux';
import { logout } from '../../reducers/authSlice';

const Header = () => {
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
  const dispatch = useDispatch();

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <HeaderContainer>
      <Logo>
        <NavLink to="/">Legal Document System</NavLink> {/* Use NavLink for logo */}
      </Logo>
      <Nav>
        <NavList>
          {isAuthenticated && (
            <NavItem>
              <StyledLink to="/">Dashboard</StyledLink>
            </NavItem>
          )}
          {isAuthenticated ? (
            <NavItem>
              <StyledButton onClick={handleLogout}>Logout</StyledButton>
            </NavItem>
          ) : (
            <NavItem>
              <StyledLink to="/login">Login</StyledLink>
            </NavItem>
          )}
        </NavList>
      </Nav>
    </HeaderContainer>
  );
};

export default Header;

// Styled Components
const HeaderContainer = styled.header`
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    background-color: #282c34;
    color: white;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const Logo = styled.div`
    font-size: 1.8rem; // Slightly smaller font size
    font-weight: bold;
    a {
        color: white;
        text-decoration: none;
        transition: color 0.2s ease; // Add smooth transition
        &:hover {
            color: #61dafb;
        }
    }
`;

const Nav = styled.nav``;

const NavList = styled.ul`
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
`;

const NavItem = styled.li`
    margin-right: 20px;
`;

const StyledLink = styled(NavLink)` // Use NavLink for active link styling
    color: white;
    text-decoration: none;
    font-size: 1rem; // Adjust font size as needed
    padding: 8px 16px;
    border-radius: 5px;
    transition: background-color 0.2s ease, color 0.2s ease; // Add smooth transitions

    &:hover {
        background-color: #61dafb;
        color: #282c34;
    }

    &.active { // Style the active link
        background-color: #61dafb;
        color: #282c34;
    }
`;

const StyledButton = styled.button`
    color: white;
    background: none;
    border: none;
    font-size: 1rem; // Adjust font size as needed
    padding: 8px 16px;
    cursor: pointer;
    transition: background-color 0.2s ease, color 0.2s ease; // Add smooth transitions

    &:hover {
        background-color: #61dafb;
        color: #282c34;
    }
`;