import React from 'react'
import styles from './Dashboard.module.css'

const Dashboard = () => {
  return (
    <div className={styles.dashboard}>
      <h1>Super Admin Dashboard</h1>
      <div className={styles.stats}>
        <div className={styles.statCard}>
          <h3>Active Users</h3>
          <p>1,234</p>
        </div>
        <div className={styles.statCard}>
          <h3>Active Tenants</h3>
          <p>56</p>
        </div>
        <div className={styles.statCard}>
          <h3>Security Events</h3>
          <p>0</p>
        </div>
        <div className={styles.statCard}>
          <h3>System Health</h3>
          <p>98%</p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
