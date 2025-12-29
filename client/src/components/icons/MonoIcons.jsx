import React from 'react';

/** Base wrapper to keep icons consistent */
export function SvgIcon({ size = 18, stroke = 'currentColor', fill = 'none', strokeWidth = 1.8, children, ...rest }) {
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

/* Dashboard */
export const DashboardIcon = (props) => (
  <SvgIcon {...props}>
    <rect x="3" y="3" width="7" height="7" rx="1" />
    <rect x="14" y="3" width="7" height="7" rx="1" />
    <rect x="14" y="14" width="7" height="7" rx="1" />
    <rect x="3" y="14" width="7" height="7" rx="1" />
  </SvgIcon>
);

/* Files / Documents */
export const FilesIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
    <path d="M14 3v6h6" />
  </SvgIcon>
);

/* Profile / User */
export const UserIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M20 21a8 8 0 1 0-16 0" />
    <circle cx="12" cy="7" r="4" />
  </SvgIcon>
);

/* Chat */
export const ChatIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" />
  </SvgIcon>
);

/* Settings / Cog */
export const SettingsIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z" />
    <path d="M19.4 15a1.7 1.7 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0-.4 1v.12a2 2 0 1 1-4 0V21a1.7 1.7 0 0 0-.4-1 1.7 1.7 0 0 0-1-.6 1.7 1.7 0 0 0-1.82-.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15 1.7 1.7 0 0 0 4 14a1.7 1.7 0 0 0-.6-1 1.7 1.7 0 0 0-1-.4H2.28a2 2 0 1 1 0-4H2.4a1.7 1.7 0 0 0 1-.4 1.7 1.7 0 0 0 .6-1 1.7 1.7 0 0 0 .33-1.82l-.06-.06A2 2 0 1 1 7.07 2.4l.06.06A1.7 1.7 0 0 0 9 4.6 1.7 1.7 0 0 0 10 4c.38-.25.78-.4 1-.4h.12a2 2 0 1 1 4 0V4a1.7 1.7 0 0 0 1 .4 1.7 1.7 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9c.25.38.4.78.4 1v.12a2 2 0 1 1 0 4V14c-.25.38-.4.78-.4 1Z" />
  </SvgIcon>
);

/* Admin */
export const AdminIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M12 12l8-5-8-5-8 5 8 5z" />
    <path d="M4 10v6l8 5 8-5v-6" />
  </SvgIcon>
);

/* Users / People */
export const UsersIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
  </SvgIcon>
);

/* Tracking / Map pin */
export const TrackingIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M12 21s-6-5.33-6-10a6 6 0 0 1 12 0c0 4.67-6 10-6 10z" />
    <circle cx="12" cy="11" r="2.5" />
  </SvgIcon>
);

/* Analytics */
export const AnalyticsIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M3 3v18h18" />
    <path d="M7 15l4-4 3 3 5-6" />
  </SvgIcon>
);

/* Geofences */
export const GeofenceIcon = (props) => (
  <SvgIcon {...props}>
    <circle cx="12" cy="12" r="7" />
    <path d="M5 12h14M12 5v14" />
  </SvgIcon>
);

/* Sheriff */
export const SheriffIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M12 2l2.2 4.6L19 7l-3.4 3.3L16.2 15 12 12.9 7.8 15l.6-4.7L5 7l4.8-.4L12 2z" />
  </SvgIcon>
);

/* Search */
export const SearchIcon = (props) => (
  <SvgIcon {...props}>
    <circle cx="11" cy="11" r="7" />
    <path d="M21 21l-3.5-3.5" />
  </SvgIcon>
);

/* Logout */
export const LogoutIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
    <path d="M16 17l5-5-5-5" />
    <path d="M21 12H9" />
  </SvgIcon>
);

/* Theme (moon/sun hybrid) */
export const ThemeIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
  </SvgIcon>
);

/* Collapse chevrons */
export const CollapseIcon = ({ collapsed, ...props }) => (
  <SvgIcon {...props}>
    {collapsed ? <path d="M9 6l6 6-6 6" /> : <path d="M15 6l-6 6 6 6" />}
  </SvgIcon>
);
