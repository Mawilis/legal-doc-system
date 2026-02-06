/**
 * File: client/src/features/audits/utils/emitAudit.js
 * -----------------------------------------------------------------------------
 * STATUS: FIXED | Audit Emitter Utility
 * -----------------------------------------------------------------------------
 */

// ✅ FIX: Import 'logAudit' instead of 'createAudit'
import { logAudit } from '../../../services/auditService';

/**
 * Helper to quickly emit an audit log from anywhere in the frontend.
 * Usage: emitAudit('CLICK', 'Button', 'btn-123', { page: 'Home' });
 */
export const emitAudit = async (action, resourceType, resourceId, metadata = {}) => {
    try {
        const payload = {
            action,
            resourceType,
            resourceId,
            metadata,
            severity: 'INFO'
        };

        // ✅ FIX: Call the correct function
        await logAudit(payload);

    } catch (error) {
        // Fail silently so we don't block the UI
        console.warn('Audit emit failed:', error);
    }
};



