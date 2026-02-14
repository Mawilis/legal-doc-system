/**
 * Legal hold manager for litigation and investigation holds
 */
class LegalHoldManager {
    constructor() {
        this.holds = new Map();
        this.affectedRecords = new Map();
    }

    createHold(holdId, metadata) {
        this.holds.set(holdId, {
            id: holdId,
            createdAt: new Date().toISOString(),
            createdBy: metadata.createdBy || 'SYSTEM',
            reason: metadata.reason || 'Legal hold',
            caseReference: metadata.caseReference,
            expiresAt: metadata.expiresAt || null,
            status: 'ACTIVE',
            affectedRecordCount: 0
        });
        return this.holds.get(holdId);
    }

    placeHoldOnRecord(holdId, recordType, recordId) {
        if (!this.holds.has(holdId)) {
            throw new Error(`Legal hold ${holdId} does not exist`);
        }

        const key = `${recordType}:${recordId}`;
        if (!this.affectedRecords.has(key)) {
            this.affectedRecords.set(key, new Set());
        }
        
        this.affectedRecords.get(key).add(holdId);
        
        // Increment hold counter
        const hold = this.holds.get(holdId);
        hold.affectedRecordCount++;
        
        return true;
    }

    isRecordOnHold(recordType, recordId) {
        const key = `${recordType}:${recordId}`;
        if (!this.affectedRecords.has(key)) return false;
        
        // Check if any holds are still active
        const holdIds = this.affectedRecords.get(key);
        for (const holdId of holdIds) {
            const hold = this.holds.get(holdId);
            if (hold && hold.status === 'ACTIVE') {
                return true;
            }
        }
        return false;
    }

    getHoldsForRecord(recordType, recordId) {
        const key = `${recordType}:${recordId}`;
        const holdIds = this.affectedRecords.get(key) || new Set();
        const holds = [];
        
        for (const holdId of holdIds) {
            const hold = this.holds.get(holdId);
            if (hold) holds.push(hold);
        }
        
        return holds;
    }

    releaseHold(holdId, releasedBy = 'SYSTEM') {
        const hold = this.holds.get(holdId);
        if (!hold) return false;
        
        hold.status = 'RELEASED';
        hold.releasedAt = new Date().toISOString();
        hold.releasedBy = releasedBy;
        
        return true;
    }

    getActiveHolds() {
        const active = [];
        for (const [holdId, hold] of this.holds.entries()) {
            if (hold.status === 'ACTIVE') {
                active.push(hold);
            }
        }
        return active;
    }
}

module.exports = { LegalHoldManager };
