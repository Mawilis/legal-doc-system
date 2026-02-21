/* eslint-disable */
/**
 * Wilsy OS Forensic Redactor
 * Designed for 100M+ User Scale
 */
export const redactPII = (obj) => {
  if (!obj || typeof obj !== 'object') return obj;
  
  const result = Array.isArray(obj) ? [] : {};
  const piiKeys = /email|idNumber|passport|phone|address|account|cell|mobile/i;

  for (const [key, value] of Object.entries(obj)) {
    if (piiKeys.test(key) && typeof value === 'string') {
      result[key] = '[REDACTED]';
    } else if (typeof value === 'object' && value !== null) {
      result[key] = redactPII(value);
    } else {
      result[key] = value;
    }
  }
  return result;
};

export const maskIp = (ip) => {
  if (!ip || typeof ip !== 'string' || !ip.includes('.')) return '[REDACTED]';
  const parts = ip.split('.');
  return parts.length === 4 ? `${parts[0]}.${parts[1]}.xxx.xxx` : '[REDACTED]';
};
