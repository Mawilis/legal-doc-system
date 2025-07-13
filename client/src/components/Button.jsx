// /Users/wilsonkhanyezi/legal-doc-system/client/src/components/atoms/Button.jsx

import styled, { css } from 'styled-components';

const Button = styled.button`
  /* Basic Button Styles */
  background-color: ${({ theme, variant }) => {
    switch (variant) {
      case 'primary':
        return theme.colors.primary;
      case 'secondary':
        return theme.colors.secondary;
      case 'danger':
        return theme.colors.danger;
      // ... more variants
      default:
        return theme.colors.primary;
    }
  }};
  color: ${({ theme, color }) => color || theme.colors.background}; // Allow custom color
  padding: ${({ theme, padding }) => padding || `${theme.spacing.sm} ${theme.spacing.md}`}; // Allow custom padding
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: ${({ theme }) => theme.typography.fontSize};
  font-weight: 500;
  transition:
    background-color 0.2s ease,
    transform 0.1s ease,
    box-shadow 0.2s ease;

  &:hover {
    background-color: ${({ theme, variant }) => {
    switch (variant) {
      case 'primary':
        return theme.colors.primaryDark;
      case 'secondary':
        return theme.colors.secondaryDark;
      case 'danger':
        return theme.colors.dangerDark;
      // ... more variants
      default:
        return theme.colors.primaryDark;
    }
  }};
    transform: translateY(-1px);
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  }

  &:active {
    transform: translateY(1px);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  /* Size Variations */
  ${({ size }) =>
    size === 'large' &&
    css`
      font-size: 1.2rem;
      padding: ${({ theme }) => theme.spacing.md} ${({ theme }) => theme.spacing.lg};
    `}

  ${({ size }) =>
    size === 'small' &&
    css`
      font-size: 0.8rem;
      padding: ${({ theme }) => theme.spacing.xs} ${({ theme }) => theme.spacing.sm};
    `}

  /* ... more size variations or custom styles */
`;

export default Button;