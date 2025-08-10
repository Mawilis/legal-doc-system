// ~/legal-doc-system/client/src/components/layout/Header.jsx

import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { FaBell, FaSignOutAlt, FaCog, FaUser, FaMoon, FaSun, FaBars } from 'react-icons/fa';
import { logoutUser } from '../../features/auth/reducers/authSlice';
import { useThemeContext } from '../../context/ThemeContext'; // Assuming a ThemeContext

// --- Main Header Wrapper ---
const HeaderWrapper = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: ${({ theme }) => theme.colors.header || '#ffffff'};
  color: ${({ theme }) => theme.colors.headerText || '#333'};
  padding: 0 24px;
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 1000;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border || '#e0e0e0'};
`;

const Logo = styled.h1`
  font-size: 1.6rem;
  margin: 0;
  font-weight: 600;
  cursor: pointer;
  color: ${({ theme }) => theme.colors.primary || '#007bff'};
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

// --- Custom Dropdown Components ---
const DropdownMenu = styled.div`
  position: absolute;
  top: 55px;
  right: 0;
  background-color: ${({ theme }) => theme.colors.background || '#fff'};
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 1001;
  width: 220px;
  border: 1px solid ${({ theme }) => theme.colors.border || '#e0e0e0'};
`;

const MenuItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  font-size: 0.95rem;
  color: ${({ theme, disabled }) => (disabled ? theme.colors.textMuted : theme.colors.text) || '#555'};
  background-color: ${({ disabled }) => (disabled ? '#f8f9fa' : 'transparent')};
  pointer-events: ${({ disabled }) => (disabled ? 'none' : 'auto')};
  border-bottom: 1px solid ${({ theme }) => theme.colors.border || '#e0e0e0'};

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background-color: ${({ theme, disabled }) => !disabled && (theme.colors.backgroundLight || '#f1f1f1')};
  }
`;

// --- Icon and Avatar Components ---
const IconButton = styled.button`
  background: none;
  border: none;
  color: inherit;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  &:hover {
    background-color: ${({ theme }) => theme.colors.backgroundLight || 'rgba(0, 0, 0, 0.05)'};
  }
`;

const Badge = styled.span`
  position: absolute;
  top: 4px;
  right: 4px;
  background-color: ${({ theme }) => theme.colors.danger || '#dc3545'};
  color: white;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
`;

const Avatar = styled.div`
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: ${({ theme }) => theme.colors.primary || '#007bff'};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.9rem;
`;

const MenuIcon = styled(IconButton)`
  display: none;
  @media (max-width: 768px) {
    display: flex;
  }
`;

/**
 * The main application header.
 * Provides navigation, theme switching, and user account actions.
 */
const Header = ({ onMenuClick }) => {
    // --- Hooks ---
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const { user } = useSelector((state) => state.auth);
    const { darkMode, toggleTheme } = useThemeContext();
    const userMenuRef = useRef(null);
    const notifMenuRef = useRef(null);

    // --- State for custom dropdowns ---
    const [isUserMenuOpen, setUserMenuOpen] = useState(false);
    const [isNotifMenuOpen, setNotifMenuOpen] = useState(false);

    // --- Event Handlers ---
    const handleLogout = () => {
        dispatch(logoutUser());
        setUserMenuOpen(false);
        navigate('/login');
    };

    // Effect to handle clicks outside of the dropdown menus to close them
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
                setUserMenuOpen(false);
            }
            if (notifMenuRef.current && !notifMenuRef.current.contains(event.target)) {
                setNotifMenuOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // --- Helper Functions ---
    const getInitials = (name) => {
        if (!name) return '';
        return name.split(' ').map((n) => n[0]).join('').toUpperCase();
    };

    return (
        <HeaderWrapper>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <MenuIcon onClick={onMenuClick}><FaBars /></MenuIcon>
                <Logo onClick={() => navigate('/')}>LegalDocSys</Logo>
            </div>

            <RightSection>
                {/* 🌙 Theme Toggle */}
                <IconButton onClick={toggleTheme} title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}>
                    {darkMode ? <FaSun /> : <FaMoon />}
                </IconButton>

                {/* 🔔 Notifications Dropdown */}
                <div style={{ position: 'relative' }} ref={notifMenuRef}>
                    <IconButton onClick={() => setNotifMenuOpen(prev => !prev)} title="Notifications">
                        <FaBell />
                        <Badge>3</Badge>
                    </IconButton>
                    {isNotifMenuOpen && (
                        <DropdownMenu>
                            <MenuItem>🔔 3 new system updates</MenuItem>
                            <MenuItem>📄 Document LS#123 served</MenuItem>
                            <MenuItem>📬 Deputy K filed a return</MenuItem>
                        </DropdownMenu>
                    )}
                </div>

                {/* 👤 User Avatar & Dropdown */}
                <div style={{ position: 'relative' }} ref={userMenuRef}>
                    <IconButton onClick={() => setUserMenuOpen(prev => !prev)} title="Account Settings">
                        <Avatar>{getInitials(user?.name)}</Avatar>
                    </IconButton>
                    {isUserMenuOpen && (
                        <DropdownMenu>
                            <MenuItem disabled>
                                <strong>{user?.name || 'User'}</strong> - {user?.role || 'guest'}
                            </MenuItem>
                            <MenuItem onClick={() => { setUserMenuOpen(false); navigate('/profile'); }}>
                                <FaUser /> Profile
                            </MenuItem>
                            <MenuItem onClick={() => { setUserMenuOpen(false); navigate('/settings'); }}>
                                <FaCog /> Settings
                            </MenuItem>
                            <MenuItem onClick={handleLogout}>
                                <FaSignOutAlt /> Logout
                            </MenuItem>
                        </DropdownMenu>
                    )}
                </div>
            </RightSection>
        </HeaderWrapper>
    );
};

export default Header;
