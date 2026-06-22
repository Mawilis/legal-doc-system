/* eslint-disable */
import React from 'react';

const BASE = Object.freeze({
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 10,
  borderRadius: 14,
  borderWidth: 1,
  borderStyle: 'solid',
  cursor: 'pointer',
  fontFamily: 'inherit',
  fontWeight: 900,
  letterSpacing: 1.1,
  textTransform: 'uppercase',
  transition: 'transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease, background 160ms ease',
  userSelect: 'none',
  whiteSpace: 'nowrap'
});

const SIZES = Object.freeze({
  sm: { minHeight: 38, padding: '8px 12px', fontSize: 11 },
  md: { minHeight: 46, padding: '11px 16px', fontSize: 12 },
  lg: { minHeight: 54, padding: '14px 20px', fontSize: 13 }
});

const VARIANTS = Object.freeze({
  sovereign: {
    background: 'linear-gradient(135deg, #fff3a3 0%, #d4af37 58%, #b8871f 100%)',
    color: '#050505',
    borderColor: 'rgba(212,175,55,0.95)',
    boxShadow: '0 14px 34px rgba(212,175,55,0.18)'
  },
  ghost: {
    background: 'rgba(255,255,255,0.025)',
    color: '#f4efe4',
    borderColor: 'rgba(212,175,55,0.34)',
    boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.04)'
  },
  command: {
    background: 'rgba(7,16,13,0.92)',
    color: '#d4af37',
    borderColor: 'rgba(212,175,55,0.42)',
    boxShadow: '0 0 0 1px rgba(212,175,55,0.08)'
  },
  danger: {
    background: 'rgba(120,30,30,0.18)',
    color: '#ffd8d8',
    borderColor: 'rgba(255,120,120,0.45)',
    boxShadow: 'none'
  }
});

/**
 * @function WilsyButton
 * @description Renders the unified Wilsy OS button standard for command, modal, artifact and workflow surfaces.
 * @param {object} props - Button props.
 * @returns {JSX.Element} Unified Wilsy OS button.
 * @collaboration Enforces one production-grade button language across Wilsy OS instead of scattered component-specific buttons.
 */
function WilsyButton({
  children,
  variant = 'sovereign',
  size = 'md',
  disabled = false,
  style = {},
  type = 'button',
  ...props
}) {
  const variantStyle = VARIANTS[variant] || VARIANTS.sovereign;
  const sizeStyle = SIZES[size] || SIZES.md;

  return (
    <button
      type={type}
      disabled={disabled}
      style={{
        ...BASE,
        ...sizeStyle,
        ...variantStyle,
        opacity: disabled ? 0.55 : 1,
        cursor: disabled ? 'not-allowed' : 'pointer',
        ...style
      }}
      {...props}
    >
      {children}
    </button>
  );
}

export default WilsyButton;
export { VARIANTS as WILSY_BUTTON_VARIANTS, SIZES as WILSY_BUTTON_SIZES };
