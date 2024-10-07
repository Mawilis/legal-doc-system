import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import PropTypes from 'prop-types'; // Import PropTypes for validation

const Header = ({ isAuthenticated, userRole, onLogout }) => {
    console.log('Header rendered with isAuthenticated:', isAuthenticated, 'userRole:', userRole);

    return (
        <HeaderContainer>
            <Logo>
                <Link to="/">Legal Document System</Link>
            </Logo>
            <Nav>
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
            </Nav>
        </HeaderContainer>
    );
};

// PropTypes for validation
Header.propTypes = {
    isAuthenticated: PropTypes.bool.isRequired,
    userRole: PropTypes.string,
    onLogout: PropTypes.func.isRequired,
};

// Default prop in case no role is passed
Header.defaultProps = {
    userRole: '',
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
  font-size: 24px;
  font-weight: bold;
  a {
    color: white;
    text-decoration: none;
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

const StyledLink = styled(Link)`
  color: white;
  text-decoration: none;
  font-size: 18px;
  padding: 8px 16px;
  border-radius: 5px;
  &:hover {
    background-color: #61dafb;
    color: #282c34;
  }
  &.active {
    background-color: #61dafb;
    color: #282c34;
  }
`;
