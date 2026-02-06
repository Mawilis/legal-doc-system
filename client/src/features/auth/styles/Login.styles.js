/**
 * File: client/src/features/auth/styles/Login.styles.js
 * STATUS: EPITOME | VISUAL LANGUAGE
 * PURPOSE: Styled components preserving the Wilsy OS Brand Identity.
 */

import styled, { keyframes, css, createGlobalStyle } from 'styled-components';

export const THEME = {
    colors: {
        primary: '#0F172A',
        primaryHover: '#1E293B',
        accent: '#2563EB',
        accentHover: '#1D4ED8',
        surface: '#FFFFFF',
        background: '#F8FAFC',
        text: '#1E293B',
        muted: '#64748B',
        border: '#E2E8F0',
        error: '#EF4444',
        success: '#10B981',
        warning: '#F59E0B'
    },
    typography: {
        fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    },
    transitions: {
        default: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
    }
};

export const GlobalReset = createGlobalStyle`
  :root {
    --wilsy-primary: ${THEME.colors.primary};
    --wilsy-accent: ${THEME.colors.accent};
    --wilsy-bg: ${THEME.colors.background};
  }
  * { box-sizing: border-box; }
`;

export const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

export const spin = keyframes`
  to { transform: rotate(360deg); }
`;

export const shake = keyframes`
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
`;

export const Wrapper = styled.div`
  display: flex;
  min-height: 100vh;
  width: 100vw;
  font-family: ${THEME.typography.fontFamily};
  background: ${THEME.colors.surface};
  overflow: hidden;
`;

export const BrandSection = styled.section`
  flex: 1;
  background: linear-gradient(135deg, #020617 0%, #0F172A 50%, #1E3A8A 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 6vw;
  color: white;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(37,99,235,0.1) 0%, transparent 60%);
    pointer-events: none;
  }

  @media (max-width: 1024px) {
    display: none;
  }
`;

export const BrandLogo = styled.div`
  margin-bottom: 48px;
  img { height: 48px; width: auto; }
  .fallback { font-size: 2rem; font-weight: 800; color: white; letter-spacing: -1px; }
`;

export const HeroText = styled.h1`
  font-size: 4rem;
  font-weight: 900;
  line-height: 1.1;
  margin-bottom: 24px;
  letter-spacing: -1px;
  color: white;

  span {
    background: linear-gradient(to right, #60A5FA, #3B82F6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
`;

export const SubText = styled.p`
  font-size: 1.5rem;
  color: #94A3B8;
  line-height: 1.6;
  max-width: 580px;
  margin-bottom: 64px;
  font-weight: 300;
  border-left: 4px solid #3B82F6;
  padding-left: 24px;
`;

export const FeatureList = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
`;

export const Feature = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 16px;

  .icon-box {
    background: rgba(37,99,235,0.2);
    padding: 8px;
    border-radius: 8px;
    color: #60A5FA;
  }

  h4 { margin: 0 0 4px 0; font-size: 1rem; font-weight: 600; }
  p { margin: 0; font-size: 0.875rem; color: #94A3B8; }
`;

export const SecurityBadge = styled.div`
  position: absolute;
  bottom: 24px;
  left: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255,255,255,0.1);
  border-radius: 99px;
  font-size: 0.75rem;
  color: rgba(255,255,255,0.7);
  border: 1px solid rgba(255,255,255,0.2);
`;

export const FormSection = styled.section`
  flex: 1;
  max-width: 720px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
  background: ${THEME.colors.surface};
  position: relative;
`;

export const AuthCard = styled.div`
  width: 100%;
  max-width: 440px;
  animation: ${fadeIn} 0.6s ease-out;
  ${props => props.$shake && css`animation: ${shake} 0.82s cubic-bezier(.36,.07,.19,.97) both;`}
`;

export const Header = styled.div`
  text-align: center;
  margin-bottom: 40px;

  h2 {
    font-size: 1.875rem;
    font-weight: 700;
    color: ${THEME.colors.text};
    margin: 0 0 12px 0;
    letter-spacing: -0.5px;
  }

  p { color: ${THEME.colors.muted}; font-size: 0.95rem; line-height: 1.5; }
`;

export const InputGroup = styled.div`
  margin-bottom: 20px;
  position: relative;
`;

export const Label = styled.label`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: ${THEME.colors.text};
  margin-bottom: 8px;

  a {
    color: ${THEME.colors.accent};
    text-decoration: none;
    font-size: 0.8rem;
    &:hover { text-decoration: underline; }
  }
`;

export const InputWrapper = styled.div`
  position: relative;

  svg {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: ${THEME.colors.muted};
    transition: ${THEME.transitions.default};
  }

  .toggle-pw {
    left: auto;
    right: 14px;
    cursor: pointer;
    &:hover { color: ${THEME.colors.text}; }
  }
`;

export const Input = styled.input`
  width: 100%;
  padding: 12px 12px 12px 44px;
  font-size: 1rem;
  border: 1px solid ${props => props.$error ? THEME.colors.error : THEME.colors.border};
  border-radius: 12px;
  background: ${THEME.colors.background};
  color: ${THEME.colors.text};
  outline: none;
  transition: ${THEME.transitions.default};

  &:focus {
    border-color: ${THEME.colors.accent};
    background: ${THEME.colors.surface};
    box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
  }

  &:disabled { background: #F1F5F9; cursor: not-allowed; }
`;

export const ErrorMsg = styled.div`
  color: ${THEME.colors.error};
  font-size: 0.8rem;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  animation: ${fadeIn} 0.2s ease;
`;

export const Button = styled.button`
  width: 100%;
  padding: 14px;
  margin-top: 12px;
  background: ${props => props.$variant === 'secondary' ? 'transparent' : THEME.colors.primary};
  color: ${props => props.$variant === 'secondary' ? THEME.colors.text : 'white'};
  border: ${props => props.$variant === 'secondary' ? `1px solid ${THEME.colors.border}` : 'none'};
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: ${THEME.transitions.default};

  &:hover {
    background: ${props => props.$variant === 'secondary' ? THEME.colors.background : THEME.colors.primaryHover};
    transform: translateY(-1px);
  }

  &:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }

  .loader {
    width: 18px;
    height: 18px;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: ${spin} 0.8s linear infinite;
  }
`;

export const Divider = styled.div`
  display: flex;
  align-items: center;
  margin: 32px 0;
  color: ${THEME.colors.muted};
  font-size: 0.85rem;

  &::before, &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: ${THEME.colors.border};
  }

  span {
    padding: 0 16px;
    font-weight: 500;
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 1px;
  }
`;

export const LegalFooter = styled.footer`
  margin-top: 48px;
  text-align: center;
  font-size: 0.75rem;
  color: ${THEME.colors.muted};

  a {
    color: ${THEME.colors.text};
    text-decoration: none;
    font-weight: 600;
    &:hover { text-decoration: underline; }
  }
`;
