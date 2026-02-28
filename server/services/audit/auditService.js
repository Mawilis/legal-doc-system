/* eslint-disable */
export const auditMiddleware = () => (req, res, next) => next();
export const AuditLogger = { log: async () => true };
export default { auditMiddleware, AuditLogger };
