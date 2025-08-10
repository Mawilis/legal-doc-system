// ~/legal-doc-system/client/src/components/atoms/Button.jsx

import styled, { css } from 'styled-components';
import PropTypes from 'prop-types';
import React from 'react';

/**
 * Base Styled Button Component
 */
const StyledButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: ${({ iconPosition }) => (iconPosition === 'right' ? '8px' : '4px')};
  padding: ${({ theme, size }) =>
    size === 'large'
      ? `${theme.spacing.md} ${theme.spacing.lg}`
      : size === 'small'
        ? `${theme.spacing.xs} ${theme.spacing.sm}`
        : `${theme.spacing.sm} ${theme.spacing.md}`};
  font-size: ${({ size }) =>
    size === 'large' ? '1.2rem' : size === 'small' ? '0.85rem' : '1rem'};
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    transform 0.1s ease,
    box-shadow 0.2s ease;
  user-select: none;

  ${({ theme, variant }) => {
    const base = {
      primary: {
        bg: theme.colors.primary,
        hover: theme.colors.primaryDark,
        text: '#fff',
      },
      secondary: {
        bg: theme.colors.secondary,
        hover: theme.colors.secondaryDark,
        text: '#fff',
      },
      danger: {
        bg: theme.colors.danger,
        hover: theme.colors.dangerDark,
        text: '#fff',
      },
      outline: {
        bg: 'transparent',
        hover: theme.colors.primaryLight,
        text: theme.colors.primary,
        border: `1px solid ${theme.colors.primary}`,
      },
    }[variant || 'primary'];

    return css`
      background-color: ${base.bg};
      color: ${base.text};
      ${base.border ? base.border : ''}

      &:hover {
        background-color: ${base.hover};
      }
    `;
  }}

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
  }

  &:active {
    transform: translateY(1px);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  }

  &:focus-visible {
    outline: none;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.4);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
  }
`;

/**
 * Reusable Button Component with optional icon and positioning
 */
const Button = ({ children, icon, iconPosition = 'left', ...rest }) => {
  return (
    <StyledButton iconPosition={iconPosition} {...rest}>
      {iconPosition === 'left' && icon}
      {children}
      {iconPosition === 'right' && icon}
    </StyledButton>
  );
};

Button.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['primary', 'secondary', 'danger', 'outline']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  icon: PropTypes.node,
  iconPosition: PropTypes.oneOf(['left', 'right']),
};

export default Button;
