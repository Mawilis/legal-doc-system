import mongoose from "mongoose"
import crypto from "crypto"

const { Schema } = mongoose

function canonicalize(obj) {
    const sorted = {}
    Object.keys(obj).sort().forEach(k => {
        sorted[k] = obj[k]
    })
    return JSON.stringify(sorted)
}

const securityLogSchema = new Schema(
    {
        timestamp: {
            type: Date,
            default: Date.now,
            required: true,
            index: true,
            immutable: true
        },

        eventType: {
            type: String,
            required: true,
            enum: [
                "unauthorized_access",
                "tenant_isolation_breach",
                "rate_limit_exceeded",
                "suspicious_pattern",
                "data_exfiltration_attempt",
                "privilege_escalation",
                "compliance_violation",
                "system_integrity_check",
                "authentication_failure",
                "authorization_failure",
                "api_abuse",
                "ddos_attempt",
                "data_breach",
                "consent_violation",
                "data_subject_request",
                "regulatory_report"
            ],
            index: true
        },

        severity: {
            type: String,
            enum: ["info", "warning", "error", "critical", "breach"],
            default: "warning",
            required: true,
            index: true
        },

        userId: {
            type: String,
            index: true,
            sparse: true
        },

        tenantId: {
            type: String,
            required: true,
            index: true
        },

        requestId: {
            type: String,
            required: true,
            index: true
        },

        ipAddress: {
            type: String
        },

        userAgent: {
            type: String,
            maxlength: 500
        },

        details: {
            type: Schema.Types.Mixed,
            required: true
        },

        requiresBreachNotification: {
            type: Boolean,
            default: false,
            index: true
        },

        breachNotifiedAt: {
            type: Date,
            index: true
        },

        dataSubjectsAffected: {
            type: Number,
            default: 0
        },

        notificationSentTo: [
            {
                authority: {
                    type: String,
                    enum: ["info_regulator", "client", "both"]
                },
                sentAt: Date,
                reference: String
            }
        ],

        retentionPolicy: {
            type: String,
            enum: [
                "companies_act_10_years",
                "popia_1_year",
                "tax_act_5_years",
                "forensic_permanent"
            ],
            default: "companies_act_10_years",
            required: true
        },

        retentionStart: {
            type: Date,
            default: Date.now
        },

        retentionEnd: {
            type: Date
        },

        forensicHash: {
            type: String,
            index: true
        },

        previousHash: {
            type: String,
            index: true
        },

        blockchainAnchor: {
            transactionId: String,
            blockNumber: Number,
            timestamp: Date,
            network: {
                type: String,
                enum: ["ethereum", "hyperledger", "none"],
                default: "none"
            }
        }
    },
    {
        timestamps: true,
        collection: "security_logs",
        strict: true
    }
)

securityLogSchema.index({ tenantId: 1, timestamp: -1 })
securityLogSchema.index({ eventType: 1, severity: 1, timestamp: -1 })
securityLogSchema.index({ requiresBreachNotification: 1, breachNotifiedAt: 1 })
securityLogSchema.index({ retentionEnd: 1 })

securityLogSchema.pre("save", async function (next) {

    try {

        if (!this.retentionEnd) {

            const end = new Date(this.retentionStart)

            switch (this.retentionPolicy) {
                case "companies_act_10_years":
                    end.setFullYear(end.getFullYear() + 10)
                    break
                case "popia_1_year":
                    end.setFullYear(end.getFullYear() + 1)
                    break
                case "tax_act_5_years":
                    end.setFullYear(end.getFullYear() + 5)
                    break
                case "forensic_permanent":
                    end.setFullYear(end.getFullYear() + 100)
                    break
            }

            this.retentionEnd = end
        }

        const lastLog = await this.constructor
            .findOne({ tenantId: this.tenantId })
            .sort({ timestamp: -1 })
            .select("forensicHash")

        if (lastLog) {
            this.previousHash = lastLog.forensicHash
        }

        const canonicalData = canonicalize({
            timestamp: this.timestamp.toISOString(),
            eventType: this.eventType,
            severity: this.severity,
            userId: this.userId,
            tenantId: this.tenantId,
            requestId: this.requestId,
            ipAddress: this.ipAddress,
            details: this.details,
            previousHash: this.previousHash
        })

        this.forensicHash = crypto
            .createHash("sha256")
            .update(canonicalData)
            .digest("hex")

        next()

    } catch (err) {
        next(err)
    }

})

securityLogSchema.statics.findBreachNotifications = function () {

    return this.find({
        requiresBreachNotification: true,
        breachNotifiedAt: null,
        severity: { $in: ["critical", "breach"] }
    })
        .sort({ timestamp: -1 })
        .limit(100)
        .lean()

}

securityLogSchema.statics.getTenantSecurityStats = async function (tenantId, days = 30) {

    const since = new Date()
    since.setDate(since.getDate() - days)

    return this.aggregate([
        { $match: { tenantId, timestamp: { $gte: since } } },
        {
            $group: {
                _id: { eventType: "$eventType", severity: "$severity" },
                count: { $sum: 1 }
            }
        },
        {
            $group: {
                _id: "$_id.eventType",
                severities: {
                    $push: {
                        severity: "$_id.severity",
                        count: "$count"
                    }
                },
                total: { $sum: "$count" }
            }
        },
        { $sort: { total: -1 } }
    ])

}

securityLogSchema.statics.verifyHashChain = async function (tenantId) {

    const logs = await this.find({ tenantId })
        .sort({ timestamp: 1 })
        .lean()

    const broken = []

    for (let i = 1; i < logs.length; i++) {

        if (logs[i].previousHash !== logs[i - 1].forensicHash) {

            broken.push({
                index: i,
                expected: logs[i - 1].forensicHash,
                actual: logs[i].previousHash
            })

        }

    }

    return {
        verified: broken.length === 0,
        totalLogs: logs.length,
        brokenLinks: broken
    }

}

securityLogSchema.methods.verifyHashIntegrity = function () {

    const canonicalData = canonicalize({
        timestamp: this.timestamp.toISOString(),
        eventType: this.eventType,
        severity: this.severity,
        userId: this.userId,
        tenantId: this.tenantId,
        requestId: this.requestId,
        ipAddress: this.ipAddress,
        details: this.details,
        previousHash: this.previousHash
    })

    const hash = crypto
        .createHash("sha256")
        .update(canonicalData)
        .digest("hex")

    return hash === this.forensicHash

}

const SecurityLogModel = mongoose.model("SecurityLog", securityLogSchema)

export default SecurityLogModel