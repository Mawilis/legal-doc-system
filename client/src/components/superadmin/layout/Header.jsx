/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ 🏛️ SUPER ADMIN HEADER - WILSY OS v2.0.0-REAL-CONTEXT                     ║
 * ║ Displays REAL authenticated user name and role                            ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../contexts/authContext';
import styles from './Header.module.css';


/**
 * @function Header
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const Header = () => {
  const { user } = useAuth();
  const [displayName, setDisplayName] = useState('SUPREME OPERATOR');
  const [displayRole, setDisplayRole] = useState('');

  useEffect(() => {
    if (user) {
      if (user.firstName && user.lastName) {
        setDisplayName(`${user.firstName} ${user.lastName}`.toUpperCase());
      } else if (user.firstName) {
        setDisplayName(user.firstName.toUpperCase());
      } else if (user.email) {
        setDisplayName(user.email.split('@')[0].toUpperCase());
      }

      const roleMap = {
        super_admin: 'SUPREME AUTHORITY',
        executive: 'EXECUTIVE OFFICER',
        tenant_admin: 'TENANT ADMINISTRATOR',
        sales_representative: 'SALES REPRESENTATIVE',
        user: 'USER'
      };
      setDisplayRole(roleMap[user.role] || user.role?.toUpperCase() || 'OPERATOR');
    }
  }, [user]);

  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        <img src="/assets/images/superadmin/wilsy-logo.svg" alt="WILSY OS" />
        <span className={styles.logoText}>WILSY OS</span>
      </div>
      <div className={styles.actions}>
        <div className={styles.userInfo}>
          <div className={styles.userName}>{displayName}</div>
          <div className={styles.userRole}>{displayRole}</div>
        </div>
        <div className={styles.status}>
          <span className={styles.indicator}></span>
          Quantum Secure
        </div>
        <div className={styles.profile}>
          <span>{displayName.charAt(0)}</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
