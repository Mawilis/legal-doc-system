// /Users/wilsonkhanyezi/legal-doc-system/client/src/components/atoms/Logo.jsx

import React from "react";
import styled from "styled-components";
import { Link } from "react-router-dom";

const LogoWrapper = styled.div`
  font-size: 1.8rem; // Slightly smaller font size
  font-weight: bold;
  margin-bottom: 20px; // Add margin for spacing

  a {
    color: ${({ theme }) => theme.colors.text};
    text-decoration: none;
    transition: color 0.2s ease; // Add smooth transition

    &:hover {
      color: ${({ theme }) => theme.colors.primary};
    }
  }
`;

const Logo = () => (
  <LogoWrapper>
    <Link to="/">Legal Document System</Link>
  </LogoWrapper>
);

export default Logo;