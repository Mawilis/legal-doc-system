import React from 'react';

/** Base SVG wrapper */
function Svg({
  size = 18,
  stroke = 'currentColor',
  fill = 'none',
  strokeWidth = 1.8,
  children,
  ...rest
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={fill}
      stroke={stroke}
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...rest}
    >
      {children}
    </svg>
  );
}

export const DashboardIcon = (props) => (
  <Svg {...props}>
    <rect x="3" y="3" width="7" height="7" rx="1" />
    <rect x="14" y="3" width="7" height="7" rx="1" />
    <rect x="14" y="14" width="7" height="7" rx="1" />
    <rect x="3" y="14" width="7" height="7" rx="1" />
  </Svg>
);

export const DocumentsIcon = (props) => (
  <Svg {...props}>
    <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
    <path d="M14 3v5h5" />
    <path d="M9 13h6M9 17h6M9 9h2" />
  </Svg>
);

export const AnalyticsIcon = (props) => (
  <Svg {...props}>
    <path d="M3 3v18h18" />
    <path d="M7 15l4-4 3 3 5-6" />
    <circle cx="11" cy="11" r="1.2" fill="currentColor" stroke="none" />
    <circle cx="15" cy="14" r="1.2" fill="currentColor" stroke="none" />
    <circle cx="20" cy="8" r="1.2" fill="currentColor" stroke="none" />
  </Svg>
);

export const SheriffIcon = (props) => (
  <Svg {...props}>
    <circle cx="12" cy="8" r="3" />
    <path d="M4 20a8 8 0 0 1 16 0" />
    <path d="M12 2l2 2-2 2-2-2 2-2zM4 8l2 2-2 2-2-2 2-2zM22 8l-2 2 2 2 2-2-2-2zM12 18l2 2-2 2-2-2 2-2z" />
  </Svg>
);

export const ProfileIcon = (props) => (
  <Svg {...props}>
    <circle cx="12" cy="8" r="3" />
    <path d="M4 20a8 8 0 0 1 16 0" />
  </Svg>
);

export const ChatIcon = (props) => (
  <Svg {...props}>
    <path d="M21 15a4 4 0 0 1-4 4H8l-5 3 1.5-4A4 4 0 0 1 4 15V7a4 4 0 0 1 4-4h9a4 4 0 0 1 4 4z" />
    <path d="M7 8h10M7 12h7" />
  </Svg>
);

export const SettingsIcon = (props) => (
  <Svg {...props}>
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.07a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.07c.7 0 1.32-.4 1.6-1.02.29-.62.2-1.35-.23-1.89l-.06-.06A2 2 0 1 1 7.21 3.2l.06.06c.54.43 1.27.52 1.89.23.62-.28 1.02-.9 1.02-1.6V2a2 2 0 1 1 4 0v.07c0 .7.4 1.32 1.02 1.6.62.29 1.35.2 1.89-.23l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06c-.43.54-.52 1.27-.23 1.89.28.62.9 1.02 1.6 1.02H22a2 2 0 1 1 0 4h-.07c-.7 0-1.32.4-1.6 1.02Z" />
  </Svg>
);

export const AdminIcon = (props) => (
  <Svg {...props}>
    <path d="M12 2l7 4v5c0 5-3 9-7 11-4-2-7-6-7-11V6l7-4z" />
    <path d="M10 13l2 2 4-4" />
  </Svg>
);

export const UsersIcon = (props) => (
  <Svg {...props}>
    <circle cx="9" cy="8" r="3" />
    <path d="M2 20a7 7 0 0 1 14 0" />
    <circle cx="17" cy="10" r="2.5" />
    <path d="M17 20a6 6 0 0 0-6-4" />
  </Svg>
);

export const SearchIcon = (props) => (
  <Svg {...props}>
    <circle cx="11" cy="11" r="7" />
    <path d="M21 21l-4.3-4.3" />
  </Svg>
);

export const TagIcon = (props) => (
  <Svg {...props}>
    <path d="M20.59 13.41 12 22l-9-9 8.59-8.59a2 2 0 0 1 2.82 0l6.18 6.18a2 2 0 0 1 0 2.82Z" />
    <circle cx="7.5" cy="12.5" r="1.5" fill="currentColor" stroke="none" />
  </Svg>
);

export const HomeIcon = (props) => (
  <Svg {...props}>
    <path d="M3 11l9-8 9 8" />
    <path d="M5 10v10h14V10" />
  </Svg>
);

export const TrashIcon = (props) => (
  <Svg {...props}>
    <path d="M3 6h18" />
    <path d="M8 6V4h8v2" />
    <rect x="6" y="6" width="12" height="14" rx="2" />
  </Svg>
);

export const PencilIcon = (props) => (
  <Svg {...props}>
    <path d="M12 20h9" />
    <path d="M16.5 3.5 20.5 7.5 7 21 3 21 3 17z" />
  </Svg>
);

export const PlusIcon = (props) => (
  <Svg {...props}>
    <path d="M12 5v14M5 12h14" />
  </Svg>
);

export const FolderIcon = (props) => (
  <Svg {...props}>
    <path d="M3 7h6l2 2h10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
  </Svg>
);

export const LockIcon = (props) => (
  <Svg {...props}>
    <rect x="5" y="11" width="14" height="10" rx="2" />
    <path d="M8 11V8a4 4 0 0 1 8 0v3" />
  </Svg>
);

export const ShieldIcon = (props) => (
  <Svg {...props}>
    <path d="M12 2l7 4v6c0 5-3 8-7 10-4-2-7-5-7-10V6z" />
  </Svg>
);

export const LogoutIcon = (props) => (
  <Svg {...props}>
    <path d="M9 21H5a2 2 0 0 1-2-2V5c0-1.1.9-2 2-2h4" />
    <path d="M16 17l5-5-5-5" />
    <path d="M21 12H9" />
  </Svg>
);

export const LoginIcon = (props) => (
  <Svg {...props}>
    <path d="M15 3h4a2 2 0 0 1 2 2v14c0 1.1-.9 2-2 2h-4" />
    <path d="M10 17l-5-5 5-5" />
    <path d="M21 12H5" />
  </Svg>
);

export const MenuIcon = (props) => (
  <Svg {...props}>
    <path d="M3 6h18M3 12h18M3 18h18" />
  </Svg>
);

export const ArrowIcon = (props) => (
  <Svg {...props}>
    <path d="M15 18l-6-6 6-6" />
  </Svg>
);

export const SunIcon = (props) => (
  <Svg {...props}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2M12 20v2M4 12H2M22 12h-2M4.93 4.93L3.51 3.51M20.49 20.49l-1.42-1.42M4.93 19.07l-1.42 1.42M20.49 3.51l-1.42 1.42" />
  </Svg>
);

export const MoonIcon = (props) => (
  <Svg {...props}>
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
  </Svg>
);

export const UserIcon = (props) => (
  <Svg {...props}>
    <circle cx="12" cy="8" r="3" />
    <path d="M4 20a8 8 0 0 1 16 0" />
  </Svg>
);
