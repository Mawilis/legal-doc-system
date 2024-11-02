import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';

const LogoWrapper = styled.div`
  font-size: 24px;
  font-weight: bold;

  a {
    color: ${({ theme }) => theme.colors.text};
    text-decoration: none;

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
