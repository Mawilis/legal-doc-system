import React from 'react';
import styled from 'styled-components';
import { FacebookIcon, TwitterIcon, LinkedInIcon } from '../icons/SocialIcons';

const FooterContainer = styled.footer`
  background-color: ${({ theme }) => theme?.colors?.footer || '#ffffff'};
  color: ${({ theme }) => theme?.colors?.textMuted || '#6c757d'};
  padding: 1.5rem 2rem;
  border-top: 1px solid ${({ theme }) => theme?.colors?.border || '#e0e0e0'};
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;

  @media (max-width: 768px) {
    flex-direction: column;
    padding: 1rem;
  }
`;

const FooterLinks = styled.div`
  display: flex;
  gap: 1.5rem;

  a {
    color: ${({ theme }) => theme?.colors?.textMuted || '#6c757d'};
    text-decoration: none;
    font-size: 0.9rem;
    transition: color 0.2s ease-in-out;

    &:hover {
      color: ${({ theme }) => theme?.colors?.primary || '#007bff'};
      text-decoration: underline;
    }
  }
`;

const SocialLinks = styled.div`
  display: flex;
  gap: 1rem;

  a {
    color: ${({ theme }) => theme?.colors?.textMuted || '#6c757d'};
    display: inline-flex;
    transition: color 0.2s ease-in-out;

    &:hover {
      color: ${({ theme }) => theme?.colors?.primary || '#007bff'};
    }
  }
`;

export default function Footer() {
  return (
    <FooterContainer>
      <span>&copy; {new Date().getFullYear()} LegalDocSys. All rights reserved.</span>

      <FooterLinks>
        <a href="/privacy-policy">Privacy Policy</a>
        <a href="/terms-of-service">Terms of Service</a>
        <a href="/contact">Contact</a>
      </FooterLinks>

      <SocialLinks>
        <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
          <FacebookIcon size={18} />
        </a>
        <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" aria-label="Twitter / X">
          <TwitterIcon size={18} />
        </a>
        <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
          <LinkedInIcon size={18} />
        </a>
      </SocialLinks>
    </FooterContainer>
  );
}
