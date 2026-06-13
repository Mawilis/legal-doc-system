/* eslint-disable */
import React from 'react'
import { Outlet } from 'react-router-dom'
import Header from './Header'
import Sidebar from './Sidebar'
import styles from './Layout.module.css'


/**
 * @function SuperAdminLayout
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const SuperAdminLayout = () => {
  return (
    <div className={styles.layout}>
      <Header />
      <div className={styles.container}>
        <Sidebar />
        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default SuperAdminLayout
