/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN METRIC SHARD [V2.1.1-EAGLE-EYE-STABLE]                                                                            ║
 * ║ [RECTIFIED: HOVER OBSTRUCTION ELIMINATED | Z-INDEX HIERARCHY LOCKED | NO DATA COLLISION]                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.1.1-FLUID | PRODUCTION READY | BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE                                                   ║
 * ║ IDENTITY ANCHORED: WILSON KHANYEZI | SOVEREIGN ARCHITECT | RECTIFIED: OVERLAP ANNIHILATION                                             ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React from 'react';
import styles from './MetricCard.module.css';

/**
 * @function MetricCard
 * @desc Renders a high-density forensic shard with hardened layout physics.
 */
const MetricCard = ({ icon: Icon, title, value, subtitle, trend }) => {
  const displayValue = typeof value === 'object' ? 'SYNCING...' : value;

  return (
    <div className={styles.card}>
      {/* 🛡️ BACKGROUND LAYER: Grid and Glow (Z-Index: 1) */}
      <div className={styles.internalGrid}></div>
      <div className={styles.bezelGlow}></div>
      <div className={styles.cardScanline}></div>

      {/* 🛡️ CONTENT LAYER: (Z-Index: 10) */}
      <div className={styles.shardBuffer}>
        <div className={styles.header}>
          <div className={styles.iconBezel}>
            <Icon size={14} className={styles.icon}/>
          </div>
          <span className={styles.title}>{title}</span>
        </div>

        <div className={styles.content}>
          <div className={styles.valueArea}>
            <div className={styles.value}>
              {displayValue}
            </div>
            {trend && (
              <div className={styles.trendArea}>
                <span className={styles.trendValue}>{trend}</span>
              </div>
            )}
          </div>
        </div>

        {subtitle && (
          <div className={styles.footer}>
            <div className={styles.subtitle}>{subtitle}</div>
            <div className={styles.statusDot}></div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricCard;
