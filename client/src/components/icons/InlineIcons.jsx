import React from 'react';

function Svg({ size = 20, children, ...rest }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false" {...rest}>
      {children}
    </svg>
  );
}

export function IconPlus({ size = 20, stroke = 'currentColor', strokeWidth = 2, ...rest }) {
  return (
    <Svg size={size} {...rest}>
      <path d="M12 5v14M5 12h14" stroke={stroke} strokeWidth={strokeWidth} strokeLinecap="round"/>
    </Svg>
  );
}

export function IconShield({ size = 20, fill = 'currentColor', ...rest }) {
  return (
    <Svg size={size} {...rest} viewBox="0 0 512 512">
      <path fill={fill} d="M466.5 83.7 278 3.5c-14.2-6-29.8-6-44 0L45.5 83.7C31 90 22 104 22 119.8v120.9c0 72.4 32.1 140.7 87.6 186.1L234 507.8c13.7 11.1 33.3 11.1 47 0l124.4-81c55.6-45.5 87.6-113.7 87.6-186.1V119.8c0-15.8-9-29.8-23.5-36.1z"/>
    </Svg>
  );
}
