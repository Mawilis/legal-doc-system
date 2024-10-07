import React from 'react';
import styled from 'styled-components';

const FooterContainer = styled.footer`
    background-color: #2c3e50;
    color: white;
    text-align: center;
    padding: 10px 0;
    position: fixed;
    width: 100%;
    bottom: 0;
`;

const Footer = () => {
    return (
        <FooterContainer>
            <p>&copy; {new Date().getFullYear()} Legal Document System</p>
        </FooterContainer>
    );
};

export default Footer;
