// server/services/statusService.js

const ALLOWED_TRANSITIONS = new Set([
    'Draft->Pending',
    'Pending->Approved', 'Pending->Rejected', 'Pending->Draft',
    'Approved->Submitted', 'Approved->Rejected',
    'Submitted->In Transit', 'Submitted->Suspended',
    'In Transit->Served', 'In Transit->Failed Service',
    'Served->Returned',
    'Failed Service->Returned',
    'Returned->Completed', 'Returned->Rejected',
    'Completed->Archived', 'Completed->Appealed',
    'Archived->Expunged'
]);

/**
 * Enforces the Status State Machine
 * @param {Document} doc - The mongoose document
 * @param {String} toStatus - The target status
 * @param {String} userId - The ID of the user performing action
 * @param {String} reason - Audit reason
 */
const changeStatus = async (doc, toStatus, userId, reason) => {
    // 1. Idempotency Check
    if (doc.status === toStatus) return doc;

    const key = `${doc.status}->${toStatus}`;

    // 2. Enforce Transition Logic
    if (!ALLOWED_TRANSITIONS.has(key)) {
        throw new Error(`Illegal status transition: Cannot move from '${doc.status}' to '${toStatus}'`);
    }

    // 3. Append to Immutable History
    doc.statusHistory.push({
        from: doc.status,
        to: toStatus,
        reason: reason || 'State Transition',
        changedBy: userId,
        changedAt: new Date()
    });

    // 4. Update Status
    doc.status = toStatus;

    // 5. Save (Triggers financial hooks automatically)
    return await doc.save();
};

module.exports = { changeStatus };