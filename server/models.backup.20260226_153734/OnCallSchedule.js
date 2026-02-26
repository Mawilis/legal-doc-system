/* eslint-disable */
import { DataTypes } from 'sequelize.js';
import { sequelize } from '../config/database.js.js';

const OnCallSchedule = sequelize.define(
  'OnCallSchedule',
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    name: {
      type: DataTypes.STRING(100),
      allowNull: false,
    },
    description: {
      type: DataTypes.TEXT,
      allowNull: true,
    },
    schedule: {
      type: DataTypes.JSONB,
      allowNull: false,
      comment: 'Schedule definition with rotations, shifts, and team members',
    },
    timezone: {
      type: DataTypes.STRING(50),
      defaultValue: 'Africa/Johannesburg',
    },
    active: {
      type: DataTypes.BOOLEAN,
      defaultValue: true,
      index: true,
    },
    primaryContacts: {
      type: DataTypes.JSONB,
      defaultValue: [],
    },
    secondaryContacts: {
      type: DataTypes.JSONB,
      defaultValue: [],
    },
    escalationPolicy: {
      type: DataTypes.JSONB,
      defaultValue: {
        intervals: [15, 30, 60],
        targets: ['primary', 'secondary', 'manager'],
      },
    },
    metadata: {
      type: DataTypes.JSONB,
      allowNull: true,
    },
  },
  {
    timestamps: true,
    tableName: 'oncall_schedules',
  }
);

export default OnCallSchedule;
