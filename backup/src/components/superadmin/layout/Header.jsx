import React from 'react'
import styles from './Header.module.css'

const Header = () => {
  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        <img src="/assets/images/superadmin/wilsy-logo.svg" alt="WILSY OS" />
      </div>
      <div className={styles.actions}>
        <div className={styles.status}>
          <span className={styles.indicator}></span>
          Quantum Secure
        </div>
        <div className={styles.profile}>
          <span>WK</span>
        </div>
      </div>
    </header>
  )
}

export default Header
