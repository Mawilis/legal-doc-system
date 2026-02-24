/* eslint-disable */
import { DataTypes } from 'sequelize';
import { sequelize } from '../config/database.js';

const Alert = sequelize.define(
  'Alert',
  {
    alertId: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    title: {
      type: DataTypes.STRING(255),
      allowNull: false,
    },
    message: {
      type: DataTypes.TEXT,
      allowNull: false,
    },
    severity: {
      type: DataTypes.ENUM('critical', 'error', 'warning', 'info', 'debug'),
      allowNull: false,
      index: true,
    },
    source: {
      type: DataTypes.STRING(100),
      allowNull: false,
      index: true,
    },
    details: {
      type: DataTypes.JSONB,
      allowNull: true,
    },
    status: {
      type: DataTypes.ENUM('active', 'acknowledged', 'resolved', 'suppressed', 'expired'),
      defaultValue: 'active',
      index: true,
    },
    acknowledgedAt: {
      type: DataTypes.DATE,
      allowNull: true,
    },
    acknowledgedBy: {
      type: DataTypes.STRING(100),
      allowNull: true,
    },
    resolvedAt: {
      type: DataTypes.DATE,
      allowNull: true,
    },
    resolution: {
      type: DataTypes.TEXT,
      allowNull: true,
    },
    metadata: {
      type: DataTypes.JSONB,
      allowNull: true,
    },
  },
  {
    timestamps: true,
    tableName: 'alerts',
    indexes: [
      {
        fields: ['severity', 'status'],
      },
      {
        fields: ['source', 'createdAt'],
      },
    ],
  }
);

export default Alert;
