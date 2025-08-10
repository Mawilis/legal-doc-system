// ~/legal-doc-system/client/src/components/organisms/Footer.jsx

import React from 'react';
import styled from 'styled-components';
import { FaFacebook, FaTwitter, FaLinkedin } from 'react-icons/fa';

/**
 * A styled container for the footer.
 * It uses flexbox for a responsive layout and pulls colors from the theme.
 */
const FooterContainer = styled.footer`
  background-color: ${({ theme }) => theme.colors.footer || '#ffffff'};
  color: ${({ theme }) => theme.colors.textMuted || '#6c757d'};
  padding: 1.5rem 2rem;
  border-top: 1px solid ${({ theme }) => theme.colors.border || '#e0e0e0'};
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap; // Allows items to wrap on smaller screens
  gap: 1rem;

  @media (max-width: 768px) {
    flex-direction: column; // Stack items vertically on mobile
    padding: 1rem;
  }
`;

/**
 * A container for the footer links (e.g., Privacy, Terms).
 */
const FooterLinks = styled.div`
  display: flex;
  gap: 1.5rem;

  a {
    color: ${({ theme }) => theme.colors.textMuted || '#6c757d'};
    text-decoration: none;
    font-size: 0.9rem;
    transition: color 0.2s ease-in-out;

    &:hover {
      color: ${({ theme }) => theme.colors.primary || '#007bff'};
      text-decoration: underline;
    }
  }
`;

/**
 * A container for the social media icons.
 */
const SocialLinks = styled.div`
  display: flex;
  gap: 1rem;

  a {
    color: ${({ theme }) => theme.colors.textMuted || '#6c757d'};
    font-size: 1.2rem;
    transition: color 0.2s ease-in-out;

    &:hover {
      color: ${({ theme }) => theme.colors.primary || '#007bff'};
    }
  }
`;

/**
 * The main application footer component.
 * Provides copyright information, navigation links, and social media icons.
 */
const Footer = () => {
    return (
        <FooterContainer>
            {/* Copyright Notice */}
            <span>
                &copy; {new Date().getFullYear()} LegalDocSys. All rights reserved.
            </span>

            {/* Navigation Links */}
            <FooterLinks>
                <a href="/privacy-policy">Privacy Policy</a>
                <a href="/terms-of-service">Terms of Service</a>
                <a href="/contact">Contact</a>
            </FooterLinks>

            {/* Social Media Links */}
            <SocialLinks>
                <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
                    <FaFacebook />
                </a>
                <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
                    <FaTwitter />
                </a>
                <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
                    <FaLinkedin />
                </a>
            </SocialLinks>
        </FooterContainer>
    );
};

export default Footer;
