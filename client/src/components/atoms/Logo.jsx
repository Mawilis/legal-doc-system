// ~/client/src/components/atoms/Logo.jsx

import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import PropTypes from 'prop-types';

const LogoWrapper = styled.div`
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 1rem;
  padding-left: ${({ collapsed }) => (collapsed ? '0.5rem' : '1rem')};
  white-space: nowrap;
  text-align: ${({ collapsed }) => (collapsed ? 'center' : 'left')};

  a {
    color: ${({ theme }) => theme.colors.text};
    text-decoration: none;
    transition: color 0.3s ease-in-out;

    &:hover {
      color: ${({ theme }) => theme.colors.primary};
    }
  }

  span {
    display: ${({ collapsed }) => (collapsed ? 'none' : 'inline')};
  }
`;

const Logo = ({ collapsed }) => (
  <LogoWrapper collapsed={collapsed}>
    <Link to="/">
      <span>📄 LegalDocSys</span>
      {!collapsed && <span style={{ fontWeight: 300, marginLeft: 4 }}>Pro</span>}
    </Link>
  </LogoWrapper>
);

Logo.propTypes = {
  collapsed: PropTypes.bool,
};

Logo.defaultProps = {
  collapsed: false,
};

export default Logo;
