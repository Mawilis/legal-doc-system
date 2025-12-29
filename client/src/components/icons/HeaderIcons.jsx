import React from 'react';

function Svg({ size = 18, stroke = 'currentColor', fill = 'none', strokeWidth = 1.8, children, ...rest }) {
  return (
    <svg
      width={size} height={size} viewBox="0 0 24 24"
      fill={fill} stroke={stroke} strokeWidth={strokeWidth}
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...rest}
    >
      {children}
    </svg>
  );
}

export const BellIcon = (props) => (
  <Svg {...props}>
    <path d="M18 8a6 6 0 10-12 0c0 7-3 8-3 8h18s-3-1-3-8" />
    <path d="M13.73 21a2 2 0 01-3.46 0" />
  </Svg>
);

export const SunIcon = (props) => (
  <Svg {...props}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
  </Svg>
);

export const MoonIcon = (props) => (
  <Svg {...props}>
    <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
  </Svg>
);

export const CogIcon = (props) => (
  <Svg {...props}>
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.7 1.7 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06A1.7 1.7 0 0015 19.4a1.7 1.7 0 00-1 .6 1.7 1.7 0 00-.4 1v.12a2 2 0 11-4 0V21a1.7 1.7 0 00-.4-1 1.7 1.7 0 00-1-.6 1.7 1.7 0 00-1.82-.33l-.06.06a2 2 0 11-2.83-2.83l.06-.06A1.7 1.7 0 004.6 15 1.7 1.7 0 004 14a1.7 1.7 0 00-.6-1 1.7 1.7 0 00-1-.4H2.28a2 2 0 110-4H2.4a1.7 1.7 0 001-.4 1.7 1.7 0 00.6-1 1.7 1.7 0 00.33-1.82l-.06-.06A2 2 0 117.07 2.4l.06.06A1.7 1.7 0 009 4.6c.24-.38.62-.71 1-.6h.12a2 2 0 114 0V4c.38-.11.76.22 1 .6a1.7 1.7 0 001 .4 1.7 1.7 0 001.82-.33l.06-.06a2 2 0 112.83 2.83l-.06.06A1.7 1.7 0 0019.4 9c.25.38.4.78.4 1v.12a2 2 0 110 4V14c-.25.38-.4.78-.4 1z" />
  </Svg>
);

export const UserCircleIcon = (props) => (
  <Svg {...props}>
    <circle cx="12" cy="8" r="4" />
    <path d="M4 20a8 8 0 0116 0" />
  </Svg>
);

export const BarsIcon = (props) => (
  <Svg {...props}><path d="M3 6h18M3 12h18M3 18h18" /></Svg>
);

export const SignOutIcon = (props) => (
  <Svg {...props}>
    <path d="M10 17l5-5-5-5" />
    <path d="M15 12H3" />
    <path d="M21 19V5a2 2 0 00-2-2h-7" />
  </Svg>
);
