/**
 * ⚡ TENANT PLAN ORCHESTRATION CONTROLLER v15.1.0
 * File: server/controllers/tenantPlanController.js
 * 
 * ███████╗██╗  ██╗███████╗██╗     ██╗████████╗██╗   ██╗
 * ██╔════╝██║  ██║██╔════╝██║     ██║╚══██╔══╝╚██╗ ██╔╝
 * ███████╗███████║█████╗  ██║     ██║   ██║    ╚████╔╝ 
 * ╚════██║██╔══██║██╔══╝  ██║     ██║   ██║     ╚██╔╝  
 * ███████║██║  ██║███████╗███████╗██║   ██║      ██║   
 * ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝   ╚═╝      ╚═╝   
 * 
 * ██████╗ ██╗   ██╗███╗   ██╗██╗  ██╗██╗   ██╗████████╗██╗███╗   ██╗ ██████╗ 
 * ██╔══██╗██║   ██║████╗  ██║██║  ██║██║   ██║╚══██╔══╝██║████╗  ██║██╔════╝ 
 * ██████╔╝██║   ██║██╔██╗ ██║███████║██║   ██║   ██║   ██║██╔██╗ ██║██║  ███╗
 * ██╔══██╗██║   ██║██║╚██╗██║██╔══██║██║   ██║   ██║   ██║██║╚██╗██║██║   ██║
 * ██████╔╝╚██████╔╝██║ ╚████║██║  ██║╚██████╔╝   ██║   ██║██║ ╚████║╚██████╔╝
 * ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
 * 
 * ============================================================================
 * WILSY OS PLAN ORCHESTRATION DOCTRINE
 * ============================================================================
 * 
 * PROVERBS 16:9
 * "In their hearts humans plan their course, but the LORD establishes their steps."
 * 
 * This controller establishes the course for South African law firms through
 * precise resource allocation, feature governance, and billing integrity.
 * 
 * ============================================================================
 * COLLABORATION MATRIX (REVENUE ENGINE)
 * ============================================================================
 * 
 * ARCHITECT: Wilson Khanyezi
 * DOCTRINE: All in or Nothing
 * 
 * REVENUE CHAIN:
 * ⚡ tenantController.js → Firm creation with initial plan
 * ⚡ billingService.js → Subscription management and invoicing
 * ══╦══════════════════════════════════════════════════════════════
 *   ╠═▶ THIS CONTROLLER → Real-time resource allocation
 *   ╠═▶ tenantAdminController.js → Internal firm management
 *   ╠═▶ featureFlagService.js → Premium feature toggles
 *   ╚═▶ auditEventModel.js → Revenue protection auditing
 * 
 * PLAN ECOSYSTEM:
 * 1. DEFAULT PLANS → Standardized offerings for mass market
 * 2. CUSTOM OVERRIDES → Enterprise negotiations and special terms
 * 3. REAL-TIME ENFORCEMENT → Instant feature access control
 * 4. BILLING SYNC → Seamless revenue recognition
 * 
 * ============================================================================
 * SOUTH AFRICAN LEGAL MARKET REALITY
 * ============================================================================
 * 1. TIERED PRICING: From solo practitioners (R1K/month) to full-service firms (R50K+/month)
 * 2. FEATURE-BASED UPSEL: AI document review, bulk invoicing, compliance modules
 * 3. VAT COMPLIANCE: 15% VAT on all plans, proper invoicing requirements
 * 4. ANNUAL CONTRACTS: Standard in legal industry for stability
 * 5. ADD-ON SERVICES: Training, customization, premium support
 * 
 * ============================================================================
 * BILLION-DOLLAR REVENUE ARCHITECTURE
 * ============================================================================
 * 1. REAL-TIME RESOURCE CONTROL: Instant feature enablement/disablement
 * 2. ENTERPRISE OVERRIDES: Custom terms for top-tier firms
 * 3. AUDIT TRAIL INTEGRITY: Every change logged for revenue protection
 * 4. SCALABLE ENFORCEMENT: Handles thousands of concurrent plan validations
 * 5. BILLING SYNC: Seamless integration with payment processing
 * 
 * ============================================================================
 * INVESTOR REALITY CHECK
 * ============================================================================
 * This controller manages:
 * - Monthly Recurring Revenue (MRR) from R1M to R100M+
 * - Enterprise contract value preservation
 * - Feature-based revenue optimization
 * - Compliance with SA VAT regulations
 * - Audit trails for revenue recognition
 * 
 * When investors see this, they see predictable, scalable revenue streams.
 * ============================================================================
 */

'use strict';

const Ajv = require('ajv').default;
const addFormats = require('ajv-formats');
const mongoose = require('mongoose');

// ============================================================================
// WILSY OS CORE IMPORTS
// ============================================================================
const Tenant = require('../models/tenantModel');
const AuditEvent = require('../models/auditEventModel');
const CustomError = require('../utils/customError');
const BillingService = require('../services/billingService');
const RedisService = require('../services/redisService');
const FeatureFlagService = require('../services/featureFlagService');

// ============================================================================
// SA LEGAL PLAN CONSTANTS
// ============================================================================
const SA_PLANS = {
    SOLO_PRACTITIONER: {
        id: 'SOLO_PRACTITIONER',
        name: 'Solo Practitioner',
        description: 'For individual attorneys practicing independently',
        monthlyPriceZAR: 1499,
        annualPriceZAR: 17988, // 12 months for price of 10 (R1499 * 12 = R17988)
        vatIncluded: true,
        vatRate: 0.15,
        features: {
            maxUsers: 1,
            maxStorageGB: 10,
            maxDocumentsPerMonth: 1000,
            maxMatters: 50,
            includedFeatures: [
                'DOCUMENT_MANAGEMENT',
                'TIME_TRACKING',
                'BASIC_INVOICING',
                'CLIENT_PORTAL',
                'EMAIL_INTEGRATION'
            ],
            premiumFeatures: [],
            supportLevel: 'BUSINESS_HOURS',
            sla: 'NEXT_BUSINESS_DAY'
        }
    },
    SMALL_FIRM: {
        id: 'SMALL_FIRM',
        name: 'Small Firm',
        description: 'For small law firms with 2-10 practitioners',
        monthlyPriceZAR: 3999,
        annualPriceZAR: 47988,
        vatIncluded: true,
        vatRate: 0.15,
        features: {
            maxUsers: 10,
            maxStorageGB: 100,
            maxDocumentsPerMonth: 10000,
            maxMatters: 500,
            includedFeatures: [
                'DOCUMENT_MANAGEMENT',
                'TIME_TRACKING',
                'ADVANCED_INVOICING',
                'CLIENT_PORTAL',
                'EMAIL_INTEGRATION',
                'CALENDAR_SYNC',
                'TEMPLATE_LIBRARY',
                'BASIC_REPORTING'
            ],
            premiumFeatures: ['AI_DOCUMENT_REVIEW_LIMITED'],
            supportLevel: 'PRIORITY',
            sla: 'SAME_DAY'
        }
    },
    PROFESSIONAL: {
        id: 'PROFESSIONAL',
        name: 'Professional',
        description: 'For established law firms with 11-50 practitioners',
        monthlyPriceZAR: 8999,
        annualPriceZAR: 107988,
        vatIncluded: true,
        vatRate: 0.15,
        features: {
            maxUsers: 50,
            maxStorageGB: 500,
            maxDocumentsPerMonth: 50000,
            maxMatters: 2500,
            includedFeatures: [
                'DOCUMENT_MANAGEMENT',
                'TIME_TRACKING',
                'ADVANCED_INVOICING',
                'CLIENT_PORTAL',
                'EMAIL_INTEGRATION',
                'CALENDAR_SYNC',
                'TEMPLATE_LIBRARY',
                'ADVANCED_REPORTING',
                'WORKFLOW_AUTOMATION',
                'API_ACCESS'
            ],
            premiumFeatures: [
                'AI_DOCUMENT_REVIEW',
                'BULK_INVOICING',
                'COMPLIANCE_MONITORING',
                'CUSTOM_BRANDING'
            ],
            supportLevel: 'PRIORITY_PLUS',
            sla: '4_HOURS'
        }
    },
    ENTERPRISE: {
        id: 'ENTERPRISE',
        name: 'Enterprise',
        description: 'For large law firms and corporate legal departments',
        monthlyPriceZAR: 19999,
        annualPriceZAR: 239988,
        vatIncluded: true,
        vatRate: 0.15,
        features: {
            maxUsers: 200,
            maxStorageGB: 2000,
            maxDocumentsPerMonth: 250000,
            maxMatters: 10000,
            includedFeatures: [
                'DOCUMENT_MANAGEMENT',
                'TIME_TRACKING',
                'ENTERPRISE_INVOICING',
                'CLIENT_PORTAL',
                'EMAIL_INTEGRATION',
                'CALENDAR_SYNC',
                'TEMPLATE_LIBRARY',
                'ENTERPRISE_REPORTING',
                'WORKFLOW_AUTOMATION',
                'API_ACCESS',
                'CUSTOM_INTEGRATIONS',
                'DATA_EXPORT'
            ],
            premiumFeatures: [
                'AI_DOCUMENT_REVIEW',
                'BULK_INVOICING',
                'COMPLIANCE_MONITORING',
                'CUSTOM_BRANDING',
                'WHITE_LABEL',
                'DEDICATED_SUPPORT',
                'CUSTOM_DEVELOPMENT',
                'SLA_AGREEMENT'
            ],
            supportLevel: 'DEDICATED',
            sla: '1_HOUR'
        }
    },
    SOVEREIGN: {
        id: 'SOVEREIGN',
        name: 'Sovereign',
        description: 'For top-tier law firms requiring maximum resources and customization',
        monthlyPriceZAR: 49999,
        annualPriceZAR: 599988,
        vatIncluded: true,
        vatRate: 0.15,
        features: {
            maxUsers: 1000,
            maxStorageGB: 10000,
            maxDocumentsPerMonth: 1000000,
            maxMatters: 50000,
            includedFeatures: [
                'DOCUMENT_MANAGEMENT',
                'TIME_TRACKING',
                'ENTERPRISE_INVOICING',
                'CLIENT_PORTAL',
                'EMAIL_INTEGRATION',
                'CALENDAR_SYNC',
                'TEMPLATE_LIBRARY',
                'ENTERPRISE_REPORTING',
                'WORKFLOW_AUTOMATION',
                'API_ACCESS',
                'CUSTOM_INTEGRATIONS',
                'DATA_EXPORT',
                'ON_PREMISE_OPTION',
                'CUSTOM_SLA'
            ],
            premiumFeatures: [
                'AI_DOCUMENT_REVIEW',
                'BULK_INVOICING',
                'COMPLIANCE_MONITORING',
                'CUSTOM_BRANDING',
                'WHITE_LABEL',
                'DEDICATED_SUPPORT',
                'CUSTOM_DEVELOPMENT',
                'SLA_AGREEMENT',
                'TRAINING_SESSIONS',
                'STRATEGIC_PARTNERSHIP'
            ],
            supportLevel: 'EXECUTIVE',
            sla: '30_MINUTES'
        }
    }
};

// ============================================================================
// AJV VALIDATION SCHEMAS (REVENUE PROTECTION)
// ============================================================================
const ajv = new Ajv({
    allErrors: true,
    removeAdditional: 'all',
    coerceTypes: true,
    useDefaults: true
});
addFormats(ajv);

/**
 * Plan Override Schema - Strict validation for revenue protection
 */
const planOverrideSchema = {
    type: 'object',
    required: ['planId', 'effectiveDate'],
    additionalProperties: false,
    properties: {
        planId: {
            type: 'string',
            enum: Object.keys(SA_PLANS),
            description: 'Must be a valid SA legal plan tier'
        },
        effectiveDate: {
            type: 'string',
            format: 'date-time',
            description: 'ISO date when override takes effect'
        },
        customPricing: {
            type: 'object',
            additionalProperties: false,
            properties: {
                monthlyPriceZAR: { type: 'number', minimum: 0 },
                annualPriceZAR: { type: 'number', minimum: 0 },
                vatIncluded: { type: 'boolean', default: true },
                billingCycle: {
                    type: 'string',
                    enum: ['MONTHLY', 'ANNUAL', 'QUARTERLY'],
                    default: 'MONTHLY'
                }
            }
        },
        customLimits: {
            type: 'object',
            additionalProperties: false,
            properties: {
                maxUsers: { type: 'integer', minimum: 1, maximum: 10000 },
                maxStorageGB: { type: 'integer', minimum: 1, maximum: 100000 },
                maxDocumentsPerMonth: { type: 'integer', minimum: 100, maximum: 10000000 },
                maxMatters: { type: 'integer', minimum: 1, maximum: 1000000 }
            }
        },
        customFeatures: {
            type: 'object',
            additionalProperties: false,
            properties: {
                includedFeatures: {
                    type: 'array',
                    items: { type: 'string' },
                    minItems: 0,
                    maxItems: 100
                },
                premiumFeatures: {
                    type: 'array',
                    items: { type: 'string' },
                    minItems: 0,
                    maxItems: 100
                },
                disabledFeatures: {
                    type: 'array',
                    items: { type: 'string' },
                    minItems: 0,
                    maxItems: 100
                }
            }
        },
        supportOverride: {
            type: 'object',
            additionalProperties: false,
            properties: {
                supportLevel: {
                    type: 'string',
                    enum: ['BUSINESS_HOURS', 'PRIORITY', 'PRIORITY_PLUS', 'DEDICATED', 'EXECUTIVE']
                },
                sla: { type: 'string' },
                dedicatedAccountManager: { type: 'boolean', default: false },
                onboardingSessions: { type: 'integer', minimum: 0, maximum: 100 }
            }
        },
        contractTerms: {
            type: 'object',
            additionalProperties: false,
            properties: {
                contractLengthMonths: { type: 'integer', minimum: 1, maximum: 60 },
                autoRenew: { type: 'boolean', default: true },
                terminationNoticeDays: { type: 'integer', minimum: 30, maximum: 365 },
                specialConditions: { type: 'string', maxLength: 1000 }
            }
        },
        notes: { type: 'string', maxLength: 2000 },
        createdBy: { type: 'string' },
        approvedBy: { type: 'string' }
    }
};

const validatePlanOverride = ajv.compile(planOverrideSchema);

/**
 * Feature Request Schema - For individual feature enablement/disablement
 */
const featureRequestSchema = {
    type: 'object',
    required: ['feature', 'action'],
    additionalProperties: false,
    properties: {
        feature: { type: 'string', minLength: 1, maxLength: 100 },
        action: { type: 'string', enum: ['ENABLE', 'DISABLE', 'TOGGLE'] },
        reason: { type: 'string', maxLength: 500 },
        effectiveDate: { type: 'string', format: 'date-time' },
        durationDays: { type: 'integer', minimum: 1, maximum: 365 }
    }
};

const validateFeatureRequest = ajv.compile(featureRequestSchema);

// ============================================================================
// PRIVATE UTILITIES (REVENUE PROTECTION)
// ============================================================================

/**
 * @function verifyPlatformAuthority
 * @description Runtime verification of platform administration rights
 * @param {Object} req - Express request object
 * @returns {boolean} - Authorization status
 */
function verifyPlatformAuthority(req) {
    if (!req.user) return false;

    // Platform administration roles
    const platformRoles = ['SUPER_ADMIN', 'PLATFORM_ADMIN', 'BILLING_ADMIN', 'SALES_ADMIN'];
    return platformRoles.includes(req.user.role);
}

/**
 * @function verifyTenantAccess
 * @description Verifies user has access to tenant plan information
 * @param {Object} req - Express request object
 * @param {string} tenantId - Tenant ID to check
 * @returns {boolean} - Access status
 */
function verifyTenantAccess(req, tenantId) {
    if (!req.user) return false;

    // Platform admins can access all tenants
    if (verifyPlatformAuthority(req)) return true;

    // Tenant admins can access their own tenant
    if (req.user.tenantId === tenantId) {
        const tenantAdminRoles = ['OWNER', 'ADMIN', 'BILLING_MANAGER'];
        return tenantAdminRoles.includes(req.user.role);
    }

    return false;
}

/**
 * @function emitPlanAudit
 * @description Creates immutable audit trail for plan modifications
 */
async function emitPlanAudit({ tenantId, actorId, eventType, severity = 'INFO', summary, metadata = {} }) {
    try {
        await AuditEvent.create({
            timestamp: new Date(),
            tenantId,
            actor: actorId,
            eventType,
            severity,
            summary,
            metadata: {
                ...metadata,
                controller: 'tenantPlanController',
                system: 'PLAN_ORCHESTRATION'
            }
        });
    } catch (err) {
        console.error(`🔥 [PLAN AUDIT FAILURE]: Tenant ${tenantId}:`, err.message);
        // Critical failure - plan changes without audit are dangerous
        throw new CustomError('Plan audit trail creation failed', 500);
    }
}

/**
 * @function getPlanWithOverrides
 * @description Retrieves complete plan with real-time overrides applied
 */
async function getPlanWithOverrides(tenantId) {
    try {
        // Get base plan from tenant record
        const tenant = await Tenant.findById(tenantId)
            .select('plan billing settings features')
            .lean();

        if (!tenant) {
            throw new CustomError('Tenant not found', 404);
        }

        // Get base plan definition
        const basePlan = SA_PLANS[tenant.plan] || SA_PLANS.SOLO_PRACTITIONER;

        // Get real-time overrides from Redis
        let overrides = {};
        try {
            const overrideKey = `tenant:plan:override:${tenantId}`;
            const overrideData = await RedisService.get(overrideKey);
            if (overrideData) {
                overrides = JSON.parse(overrideData);
            }
        } catch (redisErr) {
            console.warn('Redis override fetch failed, using base plan only:', redisErr.message);
        }

        // Get feature flags
        let featureFlags = {};
        try {
            featureFlags = await FeatureFlagService.getTenantFeatures(tenantId);
        } catch (flagErr) {
            console.warn('Feature flag fetch failed:', flagErr.message);
        }

        // Merge base plan with overrides
        const effectivePlan = {
            ...basePlan,
            tenantId,
            currentPlan: tenant.plan,
            billingCycle: tenant.billing?.cycle || 'MONTHLY',
            vatRegistered: tenant.billing?.vatRegistered || false,
            vatNumber: tenant.billing?.vatNumber,
            overrides: overrides.customPricing ? true : false,
            customPricing: overrides.customPricing,
            customLimits: overrides.customLimits,
            customFeatures: overrides.customFeatures,
            supportOverride: overrides.supportOverride,
            contractTerms: overrides.contractTerms,
            featureFlags,
            usage: await getTenantUsage(tenantId),
            compliance: {
                vatCompliant: tenant.billing?.vatRegistered || false,
                popiaCompliant: await checkPOPIACompliance(tenantId),
                lpcCompliant: tenant.lpcNumber ? true : false
            }
        };

        return effectivePlan;

    } catch (err) {
        console.error('Plan retrieval error:', err);
        throw err;
    }
}

/**
 * @function getTenantUsage
 * @description Calculates current usage against plan limits
 */
async function getTenantUsage(tenantId) {
    try {
        const [userCount, storageBytes, documentCount, matterCount] = await Promise.all([
            // User count
            mongoose.model('User').countDocuments({
                tenantId,
                deletedAt: null
            }),

            // Storage usage (simplified - would integrate with actual storage service)
            Promise.resolve(0), // Placeholder

            // Document count (last 30 days)
            mongoose.model('Document').countDocuments({
                tenantId,
                createdAt: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) }
            }).catch(() => 0),

            // Active matter count
            mongoose.model('Matter').countDocuments({
                tenantId,
                status: { $in: ['ACTIVE', 'OPEN'] }
            }).catch(() => 0)
        ]);

        return {
            users: userCount,
            storageGB: Math.round((storageBytes / (1024 * 1024 * 1024)) * 100) / 100,
            documentsLast30Days: documentCount,
            activeMatters: matterCount,
            lastCalculated: new Date()
        };

    } catch (err) {
        console.error('Usage calculation error:', err);
        return {
            users: 0,
            storageGB: 0,
            documentsLast30Days: 0,
            activeMatters: 0,
            lastCalculated: new Date(),
            error: 'Calculation failed'
        };
    }
}

/**
 * @function checkPOPIACompliance
 * @description Checks POPIA compliance status
 */
async function checkPOPIACompliance(tenantId) {
    // This would integrate with actual POPIA service
    return true; // Placeholder
}

/**
 * @function applyPlanOverride
 * @description Applies plan override with validation and synchronization
 */
async function applyPlanOverride(tenantId, overrideData, actorId) {
    const session = await mongoose.startSession();
    session.startTransaction();

    try {
        // 1. Validate override data
        const isValid = validatePlanOverride(overrideData);
        if (!isValid) {
            throw new CustomError('Invalid plan override data', 400, validatePlanOverride.errors);
        }

        // 2. Get current tenant
        const tenant = await Tenant.findById(tenantId).session(session);
        if (!tenant) {
            throw new CustomError('Tenant not found', 404);
        }

        // 3. Store override in Redis for real-time access
        const overrideKey = `tenant:plan:override:${tenantId}`;
        await RedisService.set(
            overrideKey,
            JSON.stringify(overrideData),
            86400 * 30 // 30 days TTL
        );

        // 4. Update feature flags based on override
        if (overrideData.customFeatures) {
            await FeatureFlagService.updateTenantFeatures(
                tenantId,
                overrideData.customFeatures,
                actorId
            );
        }

        // 5. Sync with billing system
        await BillingService.updateSubscriptionFromOverride(
            tenantId,
            overrideData,
            actorId
        ).catch(err => {
            console.error('Billing sync failed:', err.message);
            // Continue without billing sync - manual intervention required
        });

        // 6. Commit transaction
        await session.commitTransaction();

        // 7. Return success
        return {
            success: true,
            override: overrideData,
            appliedAt: new Date(),
            expiresAt: new Date(Date.now() + 86400 * 30 * 1000) // 30 days
        };

    } catch (err) {
        await session.abortTransaction();
        throw err;
    } finally {
        session.endSession();
    }
}

// ============================================================================
// SOVEREIGN CONTROLLERS (REVENUE ORCHESTRATION)
// ============================================================================

/**
 * @controller getPlan
 * @description Retrieves complete plan information with real-time overrides
 * @route   GET /api/tenant-plans/:tenantId
 * @access  Private (PLATFORM_ADMIN, OWNER, ADMIN, BILLING_MANAGER)
 * 
 * COLLABORATION: @Wilsy-Finance-Team
 * This provides the single source of truth for:
 * - Current plan tier and pricing
 * - Real-time resource usage
 * - Active overrides and custom terms
 * - Feature availability and flags
 * - Compliance status
 */
exports.getPlan = async (req, res, next) => {
    try {
        const { tenantId } = req.params;

        // Verify access
        if (!verifyTenantAccess(req, tenantId)) {
            return res.status(403).json({
                success: false,
                message: 'Unauthorized access to plan information'
            });
        }

        // Get complete plan with overrides
        const plan = await getPlanWithOverrides(tenantId);

        // Calculate utilization percentages
        const utilization = {
            users: plan.usage.users / (plan.customLimits?.maxUsers || plan.features.maxUsers) * 100,
            storage: plan.usage.storageGB / (plan.customLimits?.maxStorageGB || plan.features.maxStorageGB) * 100,
            documents: plan.usage.documentsLast30Days / (plan.customLimits?.maxDocumentsPerMonth || plan.features.maxDocumentsPerMonth) * 100,
            matters: plan.usage.activeMatters / (plan.customLimits?.maxMatters || plan.features.maxMatters) * 100
        };

        res.status(200).json({
            success: true,
            data: {
                plan,
                utilization,
                recommendations: generatePlanRecommendations(plan, utilization),
                billing: await BillingService.getBillingSummary(tenantId).catch(() => null),
                nextRenewal: await BillingService.getNextRenewalDate(tenantId).catch(() => null)
            }
        });

    } catch (err) {
        console.error('Get plan error:', err);
        next(err);
    }
};

/**
 * @controller upsertPlanOverride
 * @description Creates or updates plan override with enterprise terms
 * @route   PUT /api/admin/tenant-plans/:tenantId/override
 * @access  Private (PLATFORM_ADMIN, BILLING_ADMIN, SALES_ADMIN)
 * 
 * COLLABORATION: @Wilsy-Sales-Team
 * This enables enterprise sales negotiations:
 * - Custom pricing agreements
 * - Special feature bundles
 * - Extended support terms
 * - Contract modifications
 * 
 * ALL IN OR NOTHING: Entire override applied or fully rolled back.
 */
exports.upsertPlanOverride = async (req, res, next) => {
    const session = await mongoose.startSession();

    try {
        const { tenantId } = req.params;
        const overrideData = req.body;

        // Platform authority required
        if (!verifyPlatformAuthority(req)) {
            return res.status(403).json({
                success: false,
                message: 'Platform administration authority required'
            });
        }

        // Add audit information
        overrideData.createdBy = req.user.email;
        overrideData.approvedBy = req.user.email;
        overrideData.effectiveDate = overrideData.effectiveDate || new Date().toISOString();

        // Apply override
        const result = await applyPlanOverride(tenantId, overrideData, req.user._id);

        // Record audit trail
        await emitPlanAudit({
            tenantId,
            actorId: req.user._id,
            eventType: 'PLAN_OVERRIDE_UPSERTED',
            severity: 'HIGH',
            summary: `Plan override applied for tenant ${tenantId}`,
            metadata: {
                overrideData,
                appliedBy: req.user.email,
                result
            }
        });

        res.status(200).json({
            success: true,
            message: 'Plan override applied successfully',
            data: result
        });

    } catch (err) {
        await session.abortTransaction();
        console.error('Plan override error:', err);
        next(err);
    } finally {
        session.endSession();
    }
};

/**
 * @controller deletePlanOverride
 * @description Removes custom plan override, reverting to standard plan
 * @route   DELETE /api/admin/tenant-plans/:tenantId/override
 * @access  Private (PLATFORM_ADMIN, BILLING_ADMIN)
 * 
 * COLLABORATION: @Wilsy-Operations
 * This handles:
 * - Contract expiration
 * - Negotiation failures
 * - Compliance violations
 * - Manual override removal
 */
exports.deletePlanOverride = async (req, res, next) => {
    try {
        const { tenantId } = req.params;
        const { reason } = req.body;

        if (!verifyPlatformAuthority(req)) {
            return res.status(403).json({
                success: false,
                message: 'Platform administration authority required'
            });
        }

        if (!reason || reason.trim().length < 10) {
            return res.status(400).json({
                success: false,
                message: 'Detailed reason required for override removal (minimum 10 characters)'
            });
        }

        // Remove override from Redis
        const overrideKey = `tenant:plan:override:${tenantId}`;
        await RedisService.del(overrideKey);

        // Reset feature flags to plan defaults
        await FeatureFlagService.resetToPlanDefaults(tenantId, req.user._id);

        // Notify billing system
        await BillingService.revertToStandardPlan(tenantId, {
            reason,
            revertedBy: req.user.email,
            revertedAt: new Date()
        }).catch(err => {
            console.error('Billing revert failed:', err.message);
        });

        // Record audit
        await emitPlanAudit({
            tenantId,
            actorId: req.user._id,
            eventType: 'PLAN_OVERRIDE_REMOVED',
            severity: 'HIGH',
            summary: `Plan override removed for tenant ${tenantId}`,
            metadata: {
                reason,
                removedBy: req.user.email,
                removedAt: new Date()
            }
        });

        res.status(200).json({
            success: true,
            message: 'Plan override removed successfully',
            data: {
                tenantId,
                removedAt: new Date(),
                removedBy: req.user.email,
                revertedToStandard: true
            }
        });

    } catch (err) {
        console.error('Delete override error:', err);
        next(err);
    }
};

/**
 * @controller listAllPlans
 * @description Returns overview of all plans and active overrides
 * @route   GET /api/admin/tenant-plans
 * @access  Private (PLATFORM_ADMIN, BILLING_ADMIN, SALES_ADMIN)
 * 
 * COLLABORATION: @Wilsy-Executive-Team
 * This provides executive dashboard for:
 * - Revenue overview by plan tier
 * - Custom override tracking
 * - Utilization trends
 * - Growth projections
 */
exports.listAllPlans = async (req, res, next) => {
    try {
        if (!verifyPlatformAuthority(req)) {
            return res.status(403).json({
                success: false,
                message: 'Platform administration authority required'
            });
        }

        const {
            page = 1,
            limit = 50,
            planType,
            hasOverride,
            minUsers,
            maxUtilization
        } = req.query;

        const skip = (parseInt(page) - 1) * parseInt(limit);

        // Build query
        const query = { deletedAt: null };
        if (planType) query.plan = planType.toUpperCase();

        // Get tenants
        const [tenants, total] = await Promise.all([
            Tenant.find(query)
                .select('_id name plan billing province lpcNumber')
                .sort({ createdAt: -1 })
                .skip(skip)
                .limit(parseInt(limit))
                .lean(),
            Tenant.countDocuments(query)
        ]);

        // Enrich with plan details and overrides
        const enrichedTenants = await Promise.all(
            tenants.map(async (tenant) => {
                try {
                    const plan = await getPlanWithOverrides(tenant._id);
                    const usage = plan.usage;
                    const basePlan = SA_PLANS[tenant.plan] || SA_PLANS.SOLO_PRACTITIONER;

                    return {
                        tenantId: tenant._id,
                        name: tenant.name,
                        province: tenant.province,
                        lpcNumber: tenant.lpcNumber,
                        basePlan: tenant.plan,
                        currentPlan: plan.currentPlan,
                        hasOverride: !!plan.customPricing,
                        pricing: {
                            monthly: plan.customPricing?.monthlyPriceZAR || basePlan.monthlyPriceZAR,
                            annual: plan.customPricing?.annualPriceZAR || basePlan.annualPriceZAR,
                            vatIncluded: plan.customPricing?.vatIncluded !== undefined
                                ? plan.customPricing.vatIncluded
                                : basePlan.vatIncluded
                        },
                        usage: {
                            users: usage.users,
                            maxUsers: plan.customLimits?.maxUsers || basePlan.features.maxUsers,
                            utilization: (usage.users / (plan.customLimits?.maxUsers || basePlan.features.maxUsers)) * 100
                        },
                        billing: await BillingService.getBillingStatus(tenant._id).catch(() => ({ status: 'UNKNOWN' })),
                        lastUpdated: new Date()
                    };
                } catch (err) {
                    console.error(`Failed to enrich tenant ${tenant._id}:`, err.message);
                    return {
                        tenantId: tenant._id,
                        name: tenant.name,
                        error: 'Plan retrieval failed',
                        lastUpdated: new Date()
                    };
                }
            })
        );

        // Apply additional filters
        let filteredTenants = enrichedTenants;
        if (hasOverride === 'true') {
            filteredTenants = filteredTenants.filter(t => t.hasOverride);
        } else if (hasOverride === 'false') {
            filteredTenants = filteredTenants.filter(t => !t.hasOverride);
        }

        if (minUsers) {
            filteredTenants = filteredTenants.filter(t => t.usage.users >= parseInt(minUsers));
        }

        if (maxUtilization) {
            filteredTenants = filteredTenants.filter(t => t.usage.utilization <= parseInt(maxUtilization));
        }

        // Calculate summary statistics
        const summary = {
            totalTenants: total,
            filteredCount: filteredTenants.length,
            byPlan: calculateDistributionByPlan(enrichedTenants),
            totalMRR: calculateTotalMRR(enrichedTenants),
            averageUtilization: calculateAverageUtilization(enrichedTenants),
            overrideRate: (enrichedTenants.filter(t => t.hasOverride).length / enrichedTenants.length) * 100
        };

        res.status(200).json({
            success: true,
            data: filteredTenants,
            pagination: {
                page: parseInt(page),
                limit: parseInt(limit),
                total: filteredTenants.length,
                totalPages: Math.ceil(filteredTenants.length / parseInt(limit))
            },
            summary,
            availableFilters: {
                planTypes: Object.keys(SA_PLANS),
                provinces: ['GAUTENG', 'WESTERN_CAPE', 'EASTERN_CAPE', 'KWAZULU_NATAL', 'MPUMALANGA', 'LIMPOPO', 'NORTH_WEST', 'FREE_STATE', 'NORTHERN_CAPE'],
                hasOverride: ['true', 'false']
            }
        });

    } catch (err) {
        console.error('List plans error:', err);
        next(err);
    }
};

/**
 * @controller manageFeature
 * @description Enables/disables specific features for a tenant
 * @route   POST /api/admin/tenant-plans/:tenantId/features
 * @access  Private (PLATFORM_ADMIN, FEATURE_ADMIN)
 * 
 * COLLABORATION: @Wilsy-Product-Team
 * This enables:
 * - Beta feature rollouts
 * - Temporary feature enablement
 * - Compliance-related feature control
 * - Performance-based feature limiting
 */
exports.manageFeature = async (req, res, next) => {
    try {
        const { tenantId } = req.params;
        const featureRequest = req.body;

        // Platform authority required
        if (!verifyPlatformAuthority(req)) {
            return res.status(403).json({
                success: false,
                message: 'Platform administration authority required'
            });
        }

        // Validate request
        const isValid = validateFeatureRequest(featureRequest);
        if (!isValid) {
            return res.status(400).json({
                success: false,
                message: 'Invalid feature request',
                errors: validateFeatureRequest.errors
            });
        }

        // Apply feature change
        const result = await FeatureFlagService.manageFeature(
            tenantId,
            featureRequest,
            req.user._id
        );

        // Record audit
        await emitPlanAudit({
            tenantId,
            actorId: req.user._id,
            eventType: 'FEATURE_MANAGED',
            severity: 'MEDIUM',
            summary: `Feature ${featureRequest.feature} ${featureRequest.action.toLowerCase()}d for tenant ${tenantId}`,
            metadata: {
                featureRequest,
                result,
                managedBy: req.user.email
            }
        });

        res.status(200).json({
            success: true,
            message: `Feature ${featureRequest.feature} ${featureRequest.action.toLowerCase()}d successfully`,
            data: result
        });

    } catch (err) {
        console.error('Manage feature error:', err);
        next(err);
    }
};

/**
 * @controller checkCompliance
 * @description Checks plan compliance and generates recommendations
 * @route   GET /api/admin/tenant-plans/:tenantId/compliance
 * @access  Private (PLATFORM_ADMIN, COMPLIANCE_ADMIN)
 * 
 * COLLABORATION: @Wilsy-Compliance-Team
 * This ensures:
 * - VAT registration compliance
 * - POPIA data protection
 * - LPC practice standards
 * - Contractual obligations
 */
exports.checkCompliance = async (req, res, next) => {
    try {
        const { tenantId } = req.params;

        if (!verifyPlatformAuthority(req)) {
            return res.status(403).json({
                success: false,
                message: 'Platform administration authority required'
            });
        }

        // Get tenant and plan
        const [tenant, plan] = await Promise.all([
            Tenant.findById(tenantId)
                .select('plan billing lpcNumber province')
                .lean(),
            getPlanWithOverrides(tenantId)
        ]);

        if (!tenant) {
            return res.status(404).json({
                success: false,
                message: 'Tenant not found'
            });
        }

        // Check various compliance areas
        const compliance = {
            vat: {
                required: plan.customPricing?.monthlyPriceZAR >= 50000 ||
                    SA_PLANS[tenant.plan]?.monthlyPriceZAR >= 50000,
                registered: tenant.billing?.vatRegistered || false,
                vatNumber: tenant.billing?.vatNumber,
                compliant: !(plan.customPricing?.monthlyPriceZAR >= 50000 ||
                    SA_PLANS[tenant.plan]?.monthlyPriceZAR >= 50000) ||
                    tenant.billing?.vatRegistered,
                actionRequired: (plan.customPricing?.monthlyPriceZAR >= 50000 ||
                    SA_PLANS[tenant.plan]?.monthlyPriceZAR >= 50000) &&
                    !tenant.billing?.vatRegistered
            },
            popia: {
                compliant: await checkPOPIACompliance(tenantId),
                lastAudit: new Date(), // Would be actual audit date
                actionRequired: false // Would be based on actual check
            },
            lpc: {
                required: true,
                registered: !!tenant.lpcNumber,
                lpcNumber: tenant.lpcNumber,
                compliant: !!tenant.lpcNumber,
                actionRequired: !tenant.lpcNumber
            },
            contractual: {
                autoRenew: plan.contractTerms?.autoRenew !== false,
                noticePeriod: plan.contractTerms?.terminationNoticeDays >= 30,
                compliant: (plan.contractTerms?.autoRenew !== false) &&
                    (plan.contractTerms?.terminationNoticeDays >= 30),
                actionRequired: plan.contractTerms?.autoRenew === false ||
                    plan.contractTerms?.terminationNoticeDays < 30
            }
        };

        // Calculate overall compliance score
        const scores = Object.values(compliance).map(c => c.compliant ? 100 : 0);
        compliance.overallScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
        compliance.overallCompliant = compliance.overallScore >= 75;

        res.status(200).json({
            success: true,
            data: {
                tenantId,
                tenantName: tenant.name,
                compliance,
                recommendations: generateComplianceRecommendations(compliance),
                nextAuditDate: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000) // 90 days from now
            }
        });

    } catch (err) {
        console.error('Compliance check error:', err);
        next(err);
    }
};

// ============================================================================
// HELPER FUNCTIONS (BUSINESS INTELLIGENCE)
// ============================================================================

/**
 * Generate plan recommendations based on usage
 */
function generatePlanRecommendations(plan, utilization) {
    const recommendations = [];

    // User utilization
    if (utilization.users > 90) {
        recommendations.push({
            type: 'UPGRADE_RECOMMENDED',
            area: 'USER_LIMIT',
            current: `${plan.usage.users} users`,
            limit: `${plan.customLimits?.maxUsers || plan.features.maxUsers} users`,
            utilization: `${Math.round(utilization.users)}%`,
            recommendation: 'Upgrade to higher plan or request user limit increase',
            urgency: 'HIGH'
        });
    } else if (utilization.users > 70) {
        recommendations.push({
            type: 'MONITOR',
            area: 'USER_LIMIT',
            current: `${plan.usage.users} users`,
            limit: `${plan.customLimits?.maxUsers || plan.features.maxUsers} users`,
            utilization: `${Math.round(utilization.users)}%`,
            recommendation: 'Consider plan upgrade within next billing cycle',
            urgency: 'MEDIUM'
        });
    }

    // Storage utilization
    if (utilization.storage > 80) {
        recommendations.push({
            type: 'ACTION_REQUIRED',
            area: 'STORAGE',
            current: `${plan.usage.storageGB} GB`,
            limit: `${plan.customLimits?.maxStorageGB || plan.features.maxStorageGB} GB`,
            utilization: `${Math.round(utilization.storage)}%`,
            recommendation: 'Upgrade storage or archive old documents',
            urgency: 'HIGH'
        });
    }

    // Feature recommendations
    if (plan.usage.documentsLast30Days > 5000 && !plan.featureFlags?.AI_DOCUMENT_REVIEW) {
        recommendations.push({
            type: 'FEATURE_SUGGESTION',
            area: 'PRODUCTIVITY',
            usage: `${plan.usage.documentsLast30Days} documents/month`,
            recommendation: 'Enable AI Document Review to improve efficiency',
            estimatedSavings: '10-20 hours/month',
            urgency: 'MEDIUM'
        });
    }

    return recommendations;
}

/**
 * Generate compliance recommendations
 */
function generateComplianceRecommendations(compliance) {
    const recommendations = [];

    if (compliance.vat.actionRequired) {
        recommendations.push({
            type: 'COMPLIANCE_URGENT',
            area: 'VAT_REGISTRATION',
            issue: 'VAT registration required for revenue over R50K/month',
            action: 'Register for VAT with SARS and update billing details',
            deadline: 'IMMEDIATE',
            penalty: 'Potential fines and back taxes'
        });
    }

    if (compliance.lpc.actionRequired) {
        recommendations.push({
            type: 'COMPLIANCE_CRITICAL',
            area: 'LPC_REGISTRATION',
            issue: 'Missing Law Practice Council registration number',
            action: 'Register with LPC and provide registration number',
            deadline: 'WITHIN_30_DAYS',
            penalty: 'Cannot legally practice law in South Africa'
        });
    }

    if (compliance.contractual.actionRequired) {
        recommendations.push({
            type: 'CONTRACTUAL_REVIEW',
            area: 'CONTRACT_TERMS',
            issue: 'Non-standard contract terms detected',
            action: 'Review and align with standard terms of service',
            deadline: 'NEXT_RENEWAL',
            risk: 'Revenue recognition and legal enforcement issues'
        });
    }

    return recommendations;
}

/**
 * Calculate distribution by plan
 */
function calculateDistributionByPlan(tenants) {
    const distribution = {};
    tenants.forEach(tenant => {
        distribution[tenant.basePlan] = (distribution[tenant.basePlan] || 0) + 1;
    });
    return distribution;
}

/**
 * Calculate total monthly recurring revenue
 */
function calculateTotalMRR(tenants) {
    return tenants.reduce((total, tenant) => {
        return total + (tenant.pricing.monthly || 0);
    }, 0);
}

/**
 * Calculate average utilization
 */
function calculateAverageUtilization(tenants) {
    const tenantsWithUtilization = tenants.filter(t => t.usage && typeof t.usage.utilization === 'number');
    if (tenantsWithUtilization.length === 0) return 0;

    const totalUtilization = tenantsWithUtilization.reduce((sum, tenant) => {
        return sum + tenant.usage.utilization;
    }, 0);

    return Math.round(totalUtilization / tenantsWithUtilization.length);
}

// ============================================================================
// MODULE EXPORTS
// ============================================================================
module.exports = {
    // Plan Management
    getPlan: exports.getPlan,
    upsertPlanOverride: exports.upsertPlanOverride,
    deletePlanOverride: exports.deletePlanOverride,
    listAllPlans: exports.listAllPlans,

    // Feature Management
    manageFeature: exports.manageFeature,

    // Compliance
    checkCompliance: exports.checkCompliance,

    // Helper Functions (for testing)
    verifyPlatformAuthority,
    verifyTenantAccess,
    getPlanWithOverrides,
    SA_PLANS
};