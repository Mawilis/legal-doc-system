#!/* eslint-disable */
/*
 * WILSY OS: USAGE HISTORY MODEL - PERSISTENT USAGE TRACKING
 * ============================================================================
 */

import { DataTypes } from 'sequelize.js';
import { sequelize } from '../config/database.js';

export const UsageHistory = sequelize.define(
  'UsageHistory',
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    tenantId: {
      type: DataTypes.STRING,
      allowNull: false,
      index: true,
    },
    timestamp: {
      type: DataTypes.DATE,
      allowNull: false,
      index: true,
    },
    count: {
      type: DataTypes.INTEGER,
      allowNull: false,
      defaultValue: 0,
    },
    cost: {
      type: DataTypes.DECIMAL(10, 2),
      allowNull: true,
    },
    period: {
      type: DataTypes.ENUM('hour', 'day', 'week', 'month'),
      allowNull: false,
      defaultValue: 'hour',
    },
    metadata: {
      type: DataTypes.JSONB,
      allowNull: true,
    },
  },
  {
    tableName: 'usage_history',
    timestamps: true,
    indexes: [
      {
        fields: ['tenantId', 'timestamp'],
      },
      {
        fields: ['tenantId', 'period', 'timestamp'],
      },
    ],
  },
);
