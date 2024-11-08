// ~/legal-doc-system/client/src/components/organisms/Footer.jsx

import React from 'react';
import styled from 'styled-components';

const FooterContainer = styled.footer`
  background-color: ${({ theme }) => theme.colors.primary};
  color: white;
  text-align: center;
  padding: ${({ theme }) => theme.spacing.md};
  position: fixed;
  bottom: 0;
  width: 100%;
`;

const Footer = () => {
    return (
        <FooterContainer>
            &copy; {new Date().getFullYear()} Your Company Name. All rights reserved.
        </FooterContainer>
    );
};

export default Footer;
