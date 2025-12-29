// ~/client/src/components/icons/SocialIcons.jsx
import React from 'react';

/**
 * Enterprise SVG Wrapper
 * Standardizes size, accessible attributes, and behaviors for all icons.
 * This fixes the "unused variable" warning by actively using it.
 */
function Svg({ size = 18, className = "", children, ...rest }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none" // Standardize base fill
      aria-hidden="true"
      className={className}
      {...rest}
    >
      {children}
    </svg>
  );
}

export const FacebookIcon = ({ size = 18, ...props }) => (
  <Svg size={size} {...props}>
    <path
      fill="currentColor"
      d="M22 12.06C22 6.48 17.52 2 11.94 2S2 6.48 2 12.06c0 5.02 3.66 9.18 8.44 9.94v-7.04H7.9v-2.9h2.54V9.41c0-2.5 1.49-3.89 3.77-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56v1.86h2.78l-.44 2.9h-2.34V22c4.78-.76 8.44-4.92 8.44-9.94Z"
    />
  </Svg>
);

export const TwitterIcon = ({ size = 18, ...props }) => (
  <Svg size={size} {...props}>
    <path
      fill="currentColor"
      d="M22 5.92c-.75.33-1.55.55-2.39.66a4.17 4.17 0 0 0 1.83-2.3 8.34 8.34 0 0 1-2.64 1.01 4.15 4.15 0 0 0-7.07 3.78 11.78 11.78 0 0 1-8.55-4.34 4.15 4.15 0 0 0 1.28 5.54c-.64-.02-1.24-.2-1.76-.49v.05c0 2.01 1.43 3.68 3.32 4.06-.35.1-.73.16-1.11.16-.27 0-.54-.03-.8-.08.54 1.7 2.12 2.94 3.99 2.97A8.33 8.33 0 0 1 2 19.54a11.75 11.75 0 0 0 6.36 1.86c7.63 0 11.8-6.32 11.8-11.8 0-.18 0-.36-.01-.54A8.34 8.34 0 0 0 22 5.92Z"
    />
  </Svg>
);

export const LinkedInIcon = ({ size = 18, ...props }) => (
  <Svg size={size} {...props}>
    <path
      fill="currentColor"
      d="M4.98 3.5a2.5 2.5 0 1 0 0 4.99 2.5 2.5 0 0 0 0-4.99ZM3.5 9h3v12h-3V9Zm7 0h2.87v1.64h.04c.4-.76 1.37-1.56 2.82-1.56 3.02 0 3.58 1.99 3.58 4.57V21h-3v-5.51c0-1.31-.02-3-1.83-3-1.83 0-2.11 1.43-2.11 2.9V21h-3V9Z"
    />
  </Svg>
);

// Optional: Export the helper in case you need custom icons elsewhere
export { Svg };