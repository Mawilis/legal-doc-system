/* eslint-disable */
import { DataTypes } from 'sequelize.js';
import { sequelize } from '../config/database.js.js';

const Incident = sequelize.define(
  'Incident',
  {
    incidentId: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    alertId: {
      type: DataTypes.UUID,
      allowNull: true,
      references: {
        model: 'alerts',
        key: 'alertId',
      },
    },
    title: {
      type: DataTypes.STRING(255),
      allowNull: false,
    },
    severity: {
      type: DataTypes.ENUM('critical', 'error', 'warning', 'info'),
      allowNull: false,
      index: true,
    },
    status: {
      type: DataTypes.ENUM('open', 'investigating', 'mitigated', 'resolved', 'closed'),
      defaultValue: 'open',
      index: true,
    },
    timeline: {
      type: DataTypes.JSONB,
      defaultValue: [],
    },
    assignedTo: {
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
    postmortem: {
      type: DataTypes.TEXT,
      allowNull: true,
    },
    metrics: {
      type: DataTypes.JSONB,
      allowNull: true,
    },
  },
  {
    timestamps: true,
    tableName: 'incidents',
    indexes: [
      {
        fields: ['severity', 'status'],
      },
      {
        fields: ['createdAt'],
      },
    ],
  }
);

export default Incident;
