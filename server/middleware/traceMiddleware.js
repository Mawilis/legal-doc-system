import { v4 as uuidv4 } from 'uuid';

/**
 * 🛡️ FORENSIC TRACE ID INJECTOR
 * Injects a unique trace ID into every request header.
 * Allows tracking a single request from the browser -> Node API -> Database Ledger.
 */
export const injectTraceId = (req, res, next) => {
  const traceId = req.headers['x-trace-id'] || uuidv4();
  req.traceId = traceId;
  res.setHeader('X-Trace-ID', traceId);
  next();
};
