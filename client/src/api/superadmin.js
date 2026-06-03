/* eslint-disable */
import api from '../services/api';

/**
 * 📊 Retrieves Global Wealth Metrics & Valuation
 */
export const getGlobalStats = async () => {
  const { data } = await api.get('/superadmin/stats');
  return data;
};

/**
 * 🏢 Retrieves All Firms and their Financial Health
 */
export const getFirms = async () => {
  const { data } = await api.get('/superadmin/firms');
  return data;
};

/**
 * 🔐 Triggers Global Omega Key Rotation
 */
export const rotateKeys = async () => {
  const { data } = await api.post('/superadmin/crypto/rotate');
  return data;
};
