// ~/legal-doc-system/client/src/components/layout/AppLayout.jsx

import React, { useState } from 'react';
import { useLocation, Outlet } from 'react-router-dom';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from './Sidebar'; // Assuming a Sidebar component exists
import Header from './Header';   // Assuming a Header component exists
import Footer from './Footer';   // Assuming a Footer component exists

/**
 * A styled container for the entire application layout.
 * Uses flexbox to arrange the sidebar and main content.
 */
const LayoutContainer = styled.div`
  display: flex;
  height: 100vh;
  overflow: hidden;
  background-color: ${({ theme }) => theme.colors.background || '#f4f6f8'};
`;

/**
 * A wrapper for the sidebar that handles its responsive behavior.
 * On desktop, it's a fixed width. On mobile, it becomes a fixed-position drawer.
 */
const SidebarWrapper = styled.aside`
  width: 250px;
  flex-shrink: 0;
  background-color: ${({ theme }) => theme.colors.sidebar || '#ffffff'};
  border-right: 1px solid ${({ theme }) => theme.colors.border || '#e0e0e0'};
  transition: all 0.3s ease;

  @media (max-width: 768px) {
    position: fixed;
    top: 0;
    left: ${({ $isOpen }) => ($isOpen ? '0' : '-250px')};
    height: 100%;
    z-index: 1001;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  }
`;

/**
 * A wrapper for the main content area, including the header and footer.
 */
const ContentWrapper = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

/**
 * The main content area where the page components will be rendered.
 * It is scrollable and includes page transition animations.
 */
const MainContent = styled(motion.main)`
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background-color: ${({ theme }) => theme.colors.background || '#f4f6f8'};

  @media (max-width: 768px) {
    padding: 16px;
  }
`;

/**
 * The main application layout component.
 * It orchestrates the header, sidebar, and main content area,
 * providing a consistent structure for all pages.
 */
const AppLayout = () => {
  // State to manage the visibility of the sidebar on mobile devices.
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  // Toggles the sidebar's visibility.
  const toggleSidebar = () => setSidebarOpen((prev) => !prev);
  // Closes the sidebar, typically used by navigation links inside the sidebar.
  const closeSidebar = () => setSidebarOpen(false);

  return (
    <LayoutContainer>
      {/* The sidebar is rendered here, its visibility controlled by state. */}
      <SidebarWrapper $isOpen={isSidebarOpen}>
        <Sidebar onClose={closeSidebar} />
      </SidebarWrapper>

      <ContentWrapper>
        {/* The header receives the toggle function to control the mobile menu. */}
        <Header onMenuClick={toggleSidebar} />

        {/* AnimatePresence handles the exit/enter animations for page transitions. */}
        <AnimatePresence mode="wait">
          <MainContent
            key={location.pathname} // The key ensures the animation re-runs on route changes.
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
          >
            {/* The Outlet component from React Router renders the current route's component. */}
            <Outlet />
          </MainContent>
        </AnimatePresence>

        <Footer />
      </ContentWrapper>
    </LayoutContainer>
  );
};

export default AppLayout;
