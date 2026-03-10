import React from 'react'
import { NavLink } from 'react-router-dom'
import styles from './Sidebar.module.css'

const navItems = [
  { path: '/', icon: '📊', label: 'Dashboard' },
  { path: '/users', icon: '👥', label: 'Users' },
  { path: '/tenants', icon: '🏢', label: 'Tenants' },
  { path: '/security', icon: '🔐', label: 'Security' },
  { path: '/audit', icon: '📋', label: 'Audit Trail' },
  { path: '/system', icon: '⚙️', label: 'System' },
  { path: '/reports', icon: '📈', label: 'Reports' },
]

const Sidebar = () => {
  return (
    <aside className={styles.sidebar}>
      <nav className={styles.nav}>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => 
              `${styles.link} ${isActive ? styles.active : ''}`
            }
          >
            <span className={styles.icon}>{item.icon}</span>
            <span className={styles.label}>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

export default Sidebar
