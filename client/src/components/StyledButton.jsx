import styled, { css } from 'styled-components';
import PropTypes from 'prop-types';

// --- Variant and Size Maps for clean, scalable styling ---
const VARIANTS = {
  primary: { bg: '#007bff', color: '#ffffff', hoverBg: '#0056b3', border: '1px solid #007bff' },
  secondary: { bg: '#6c757d', color: '#ffffff', hoverBg: '#5a6268', border: '1px solid #6c757d' },
  danger: { bg: '#dc3545', color: '#ffffff', hoverBg: '#c82333', border: '1px solid #dc3545' },
  success: { bg: '#28a745', color: '#ffffff', hoverBg: '#218838', border: '1px solid #28a745' },
};

const SIZES = {
  small: { fontSize: '0.9rem', padding: '8px 12px' },
  medium: { fontSize: '1rem', padding: '10px 16px' },
  large: { fontSize: '1.1rem', padding: '12px 20px' },
};

/**
 * A versatile, theme-aware button component with multiple variants and sizes.
 */
const Button = styled.button`
  /* --- Base Styles --- */
  font-family: ${({ theme }) => theme.typography?.fontFamily || 'sans-serif'};
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s ease-in-out;
  white-space: nowrap;

  /* --- Size Styles --- */
  padding: ${({ size = 'medium' }) => SIZES[size]?.padding || SIZES.medium.padding};
  font-size: ${({ size = 'medium' }) => SIZES[size]?.fontSize || SIZES.medium.fontSize};
  
  /* --- Variant Styles --- */
  ${({ variant = 'primary', outline, ghost }) => {
    const themeVariant = VARIANTS[variant] || VARIANTS.primary;

    if (ghost) {
      return css`
        background-color: transparent;
        border: 1px solid transparent;
        color: ${themeVariant.bg};
        &:hover:not(:disabled) {
          background-color: ${themeVariant.bg};
          color: ${themeVariant.color};
        }
      `;
    }

    if (outline) {
      return css`
        background-color: transparent;
        border: ${themeVariant.border};
        color: ${themeVariant.bg};
        &:hover:not(:disabled) {
          background-color: ${themeVariant.bg};
          color: ${themeVariant.color};
        }
      `;
    }

    return css`
      background-color: ${themeVariant.bg};
      color: ${themeVariant.color};
      border: ${themeVariant.border};
      &:hover:not(:disabled) {
        background-color: ${themeVariant.hoverBg};
      }
    `;
  }}

  /* --- Icon-Only Styles --- */
  ${({ iconOnly }) => iconOnly && css`
      padding: 8px;
      width: 36px;
      height: 36px;
      & > svg {
          margin: 0;
      }
  `}

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

Button.propTypes = {
  variant: PropTypes.oneOf(['primary', 'secondary', 'danger', 'success']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  outline: PropTypes.bool,
  ghost: PropTypes.bool,
  iconOnly: PropTypes.bool,
  disabled: PropTypes.bool,
  children: PropTypes.node.isRequired,
};

export default Button;
