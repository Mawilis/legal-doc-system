// ~/client/src/components/layout/Sidebar.jsx

import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import styled from 'styled-components';
import { useSelector, useDispatch } from 'react-redux';
import { logoutUser } from '../../features/auth/reducers/authSlice';
import {
    Drawer,
    IconButton,
    Menu,
    MenuItem,
    Avatar,
    useMediaQuery,
    Tooltip,
    Switch,
} from '@mui/material';
import { motion } from 'framer-motion';
import Logo from '../atoms/Logo';
import { useTheme } from '../../context/ThemeContext';

// ✅ All 24 icons
import dashboardIcon from '../../assets/icons/dashboard.svg';
import documentsIcon from '../../assets/icons/documents.svg';
import profileIcon from '../../assets/icons/profile.svg';
import chatIcon from '../../assets/icons/chat.svg';
import settingsIcon from '../../assets/icons/settings.svg';
import adminIcon from '../../assets/icons/admin.svg';
import usersIcon from '../../assets/icons/users.svg';
import logoutIcon from '../../assets/icons/logout.svg';
import loginIcon from '../../assets/icons/login.svg';
import bellIcon from '../../assets/icons/bell.svg';
import userIcon from '../../assets/icons/user.svg';
import gearIcon from '../../assets/icons/gear.svg';
import moonIcon from '../../assets/icons/moon.svg';
import sunIcon from '../../assets/icons/sun.svg';
import lockIcon from '../../assets/icons/lock.svg';
import folderIcon from '../../assets/icons/folder.svg';
import plusIcon from '../../assets/icons/plus.svg';
import pencilIcon from '../../assets/icons/pencil.svg';
import trashIcon from '../../assets/icons/trash.svg';
import homeIcon from '../../assets/icons/home.svg';
import shieldIcon from '../../assets/icons/shield.svg';
import tagIcon from '../../assets/icons/tag.svg';
import searchIcon from '../../assets/icons/search.svg';
import arrowIcon from '../../assets/icons/arrow.svg';
import menuIcon from '../../assets/icons/menu.svg';

const SidebarWrapper = styled.div`
  display: flex;
`;

const MobileMenuToggle = styled(IconButton)`
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 1201;
  color: white;

  @media (min-width: 769px) {
    display: none;
  }
`;

const SidebarContainer = styled(motion.div)`
  display: flex;
  flex-direction: column;
  width: ${({ collapsed }) => (collapsed ? '70px' : '250px')};
  background-color: ${({ theme }) => theme.colors.sidebarBg};
  height: 100vh;
  overflow-y: auto;
  padding-top: 20px;
  transition: width 0.3s ease;
`;

const SidebarLink = styled(NavLink)`
  display: flex;
  align-items: center;
  color: ${({ theme }) => theme.colors.text};
  padding: 12px 15px;
  text-decoration: none;
  transition: background-color 0.2s ease;

  img {
    margin-right: 10px;
    width: 20px;
    height: 20px;
  }

  &:hover {
    background-color: ${({ theme }) => theme.colors.hoverBg};
  }

  &.active {
    background-color: ${({ theme }) => theme.colors.activeBg};
    font-weight: bold;
  }
`;

const AvatarContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 16px 0;
`;

const CollapseButton = styled(IconButton)`
  color: ${({ theme }) => theme.colors.text};
  margin: 8px auto;
`;

const ToggleWrapper = styled.div`
  text-align: center;
  margin-top: auto;
  padding: 12px;
  color: ${({ theme }) => theme.colors.text};
`;

const Sidebar = ({ onClose }) => {
    const dispatch = useDispatch();
    const { user } = useSelector((state) => state.auth);
    const [mobileOpen, setMobileOpen] = useState(false);
    const [anchorEl, setAnchorEl] = useState(null);
    const [collapsed, setCollapsed] = useState(false);
    const isMobile = useMediaQuery('(max-width: 768px)');
    const { isDarkMode, toggleDarkMode } = useTheme();

    const handleToggle = () => setMobileOpen(!mobileOpen);
    const handleCollapseToggle = () => setCollapsed((prev) => !prev);
    const handleAvatarClick = (e) => setAnchorEl(e.currentTarget);
    const handleMenuClose = () => setAnchorEl(null);
    const handleLogout = () => {
        dispatch(logoutUser());
        handleMenuClose();
        if (isMobile && onClose) onClose();
    };

    const links = [
        { to: '/dashboard', label: 'Dashboard', icon: dashboardIcon },
        { to: '/documents', label: 'Documents', icon: documentsIcon },
        { to: '/profile', label: 'Profile', icon: profileIcon },
        { to: '/chat', label: 'Chat', icon: chatIcon },
        { to: '/settings', label: 'Settings', icon: settingsIcon },
        { to: '/search', label: 'Search', icon: searchIcon },
        { to: '/tags', label: 'Tags', icon: tagIcon },
        { to: '/home', label: 'Home', icon: homeIcon },
        { to: '/trash', label: 'Trash', icon: trashIcon },
        { to: '/pencil', label: 'Edit', icon: pencilIcon },
        { to: '/create', label: 'Create', icon: plusIcon },
        { to: '/folders', label: 'Folders', icon: folderIcon },
        { to: '/lock', label: 'Lock', icon: lockIcon },
        { to: '/gear', label: 'Gear', icon: gearIcon },
        { to: '/bell', label: 'Alerts', icon: bellIcon },
        { to: '/login', label: 'Login', icon: loginIcon },
        { to: '/shield', label: 'Security', icon: shieldIcon },
        ...(user?.role === 'admin'
            ? [
                { to: '/admin', label: 'Admin', icon: adminIcon },
                { to: '/admin/users', label: 'Users', icon: usersIcon },
            ]
            : []),
    ];

    const renderLinks = () => (
        <SidebarContainer
            collapsed={collapsed}
            initial={{ x: -250 }}
            animate={{ x: 0 }}
            transition={{ duration: 0.3 }}
        >
            <Logo collapsed={collapsed} />

            <AvatarContainer>
                <Tooltip title={user?.name || 'User'}>
                    <IconButton onClick={handleAvatarClick}>
                        <Avatar alt={user?.name || 'User'}>
                            <img src={userIcon} alt="user" width={24} height={24} />
                        </Avatar>
                    </IconButton>
                </Tooltip>
                <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
                    <MenuItem onClick={handleLogout}>
                        <img src={logoutIcon} alt="logout" width={20} style={{ marginRight: 8 }} />
                        Logout
                    </MenuItem>
                </Menu>
            </AvatarContainer>

            {links.map((link) => (
                <Tooltip key={link.to} title={collapsed ? link.label : ''} placement="right">
                    <SidebarLink
                        to={link.to}
                        onClick={() => {
                            if (isMobile && onClose) onClose();
                        }}
                    >
                        <img src={link.icon} alt={link.label} />
                        {!collapsed && link.label}
                    </SidebarLink>
                </Tooltip>
            ))}

            {!isMobile && (
                <CollapseButton onClick={handleCollapseToggle} aria-label="Toggle sidebar">
                    <img src={arrowIcon} alt="Toggle" width={20} />
                </CollapseButton>
            )}

            <ToggleWrapper>
                <img
                    src={isDarkMode ? moonIcon : sunIcon}
                    alt="Theme toggle"
                    width={20}
                    style={{ verticalAlign: 'middle', marginRight: 8 }}
                />
                <Switch
                    checked={isDarkMode}
                    onChange={toggleDarkMode}
                    inputProps={{ 'aria-label': 'toggle dark mode' }}
                />
            </ToggleWrapper>
        </SidebarContainer>
    );

    return (
        <SidebarWrapper>
            {isMobile && (
                <MobileMenuToggle onClick={handleToggle}>
                    <img src={menuIcon} alt="menu" width={24} />
                </MobileMenuToggle>
            )}
            {isMobile ? (
                <Drawer anchor="left" open={mobileOpen} onClose={handleToggle}>
                    {renderLinks()}
                </Drawer>
            ) : (
                renderLinks()
            )}
        </SidebarWrapper>
    );
};

export default Sidebar;
