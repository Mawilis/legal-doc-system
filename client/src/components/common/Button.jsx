// ~/client/src/components/atoms/Button.jsx

import styled, { css } from 'styled-components';
import PropTypes from 'prop-types';

// --- Variant and Size Maps for clean, scalable styling ---
// This pattern is more maintainable and readable than multiple switch statements.
const VARIANTS = {
  primary: {
    bg: (theme) => theme.colors?.primary || '#007bff',
    color: '#ffffff',
    hoverBg: (theme) => theme.colors?.primaryDark || '#0056b3',
    border: (theme) => `1px solid ${theme.colors?.primary || '#007bff'}`,
  },
  secondary: {
    bg: (theme) => theme.colors?.secondary || '#6c757d',
    color: '#ffffff',
    hoverBg: (theme) => theme.colors?.secondaryDark || '#5a6268',
    border: (theme) => `1px solid ${theme.colors?.secondary || '#6c757d'}`,
  },
  danger: {
    bg: (theme) => theme.colors?.danger || '#dc3545',
    color: '#ffffff',
    hoverBg: (theme) => theme.colors?.dangerDark || '#c82333',
    border: (theme) => `1px solid ${theme.colors?.danger || '#dc3545'}`,
  },
  success: {
    bg: (theme) => theme.colors?.success || '#28a745',
    color: '#ffffff',
    hoverBg: (theme) => theme.colors?.successDark || '#218838',
    border: (theme) => `1px solid ${theme.colors?.success || '#28a745'}`,
  },
};

const SIZES = {
  small: {
    fontSize: (theme) => theme.typography?.fontSizeSm || '0.9rem',
    padding: (theme) => theme.spacing?.xs || '8px 12px',
  },
  medium: {
    fontSize: (theme) => theme.typography?.fontSize || '1rem',
    padding: (theme) => theme.spacing?.sm || '10px 16px',
  },
  large: {
    fontSize: (theme) => theme.typography?.fontSizeLg || '1.1rem',
    padding: (theme) => theme.spacing?.md || '12px 20px',
  }
};

/**
 * A versatile, theme-aware button component with multiple variants and sizes.
 * It supports solid, outline, and ghost styles for maximum flexibility.
 *
 * @param {object} props
 * @param {('primary'|'secondary'|'danger'|'success')} [props.variant='primary'] - The button's style variant.
 * @param {('small'|'medium'|'large')} [props.size='medium'] - The button's size.
 * @param {boolean} [props.outline=false] - If true, renders with a transparent background and colored border.
 * @param {boolean} [props.ghost=false] - If true, renders with a transparent background and no border.
 * @param {boolean} [props.disabled=false] - If true, the button will be disabled.
 * @param {React.ReactNode} props.children - The content to display inside the button.
 */
const Button = styled.button`
  /* --- Base Styles --- */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-family: ${({ theme }) => theme.typography?.fontFamily || 'sans-serif'};
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease-in-out;
  white-space: nowrap;

  /* --- Size Styles --- */
  padding: ${({ theme, size = 'medium' }) => SIZES[size]?.padding(theme) || SIZES.medium.padding(theme)};
  font-size: ${({ theme, size = 'medium' }) => SIZES[size]?.fontSize(theme) || SIZES.medium.fontSize(theme)};
  
  /* --- Variant Styles --- */
  ${({ theme, variant = 'primary', outline, ghost }) => {
    const themeVariant = VARIANTS[variant] || VARIANTS.primary;

    if (ghost) {
      return css`
        background-color: transparent;
        border: 1px solid transparent;
        color: ${themeVariant.bg(theme)};
        &:hover:not(:disabled) {
          background-color: rgba(0, 0, 0, 0.05);
        }
      `;
    }

    if (outline) {
      return css`
        background-color: transparent;
        border: ${themeVariant.border(theme)};
        color: ${themeVariant.bg(theme)};
        &:hover:not(:disabled) {
          background-color: ${themeVariant.bg(theme)};
          color: ${themeVariant.color};
        }
      `;
    }

    // Solid (default) variant
    return css`
      background-color: ${themeVariant.bg(theme)};
      color: ${themeVariant.color};
      border: ${themeVariant.border(theme)};
      &:hover:not(:disabled) {
        background-color: ${themeVariant.hoverBg(theme)};
      }
    `;
  }}

  /* --- State Styles --- */
  &:active:not(:disabled) {
    transform: translateY(1px);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px ${({ theme }) => theme.colors?.focusRing || 'rgba(0, 123, 255, 0.25)'};
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

// --- PropTypes for Documentation and Type-Checking ---
Button.propTypes = {
  variant: PropTypes.oneOf(['primary', 'secondary', 'danger', 'success']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  outline: PropTypes.bool,
  ghost: PropTypes.bool,
  disabled: PropTypes.bool,
  children: PropTypes.node.isRequired,
};

export default Button;
