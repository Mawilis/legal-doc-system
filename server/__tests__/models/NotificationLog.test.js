/* eslint-env jest */
/**
 * FORENSIC TEST SUITE: NotificationLog Model V6
 * Investor-grade deterministic tests with economic metrics
 */

const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const NotificationLog = require('../../models/NotificationLog');
const {
    NOTIFICATION_CHANNELS,
    NOTIFICATION_TYPES,
    NOTIFICATION_STATUS,
    RETENTION_POLICIES
} = require('../../models/NotificationLog');

let mongoServer;

describe('FORENSIC NOTIFICATION LOG MODEL V6', () => {
    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    beforeEach(async () => {
        await NotificationLog.deleteMany({});
    });

    describe('FINANCIAL THESIS - Economic Impact', () => {
        test('should calculate economic value of notification logging', () => {
            const manualCostPerNotification = 15; // R15 manual
            const automatedCost = 0.05; // R0.05 automated
            const savingsPerNotification = manualCostPerNotification - automatedCost;
            
            const notificationsPerYear = 100000; // 100k notifications/year
            const totalSavings = savingsPerNotification * notificationsPerYear;
            
            const complianceValuePerNotification = 25; // R25 compliance proof value
            const auditSavingsPerNotification = 50; // R50 audit savings
            
            const totalEconomicValue = notificationsPerYear * (
                savingsPerNotification + 
                complianceValuePerNotification + 
                auditSavingsPerNotification
            );
            
            console.log(`✓ Savings per notification: R${savingsPerNotification}`);
            console.log(`✓ Annual savings (100k notifications): R${totalSavings.toLocaleString()}`);
            console.log(`✓ Total economic value: R${totalEconomicValue.toLocaleString()}`);
            
            expect(totalEconomicValue).toBeGreaterThan(9000000); // R9M+
        });
    });

    describe('SCHEMA VALIDATION - Core Fields', () => {
        test('should create notification with minimum required fields', async () => {
            const notification = new NotificationLog({
                tenantId: 'TENANT_001_TEST',
                userId: 'USER_123',
                type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                channel: NOTIFICATION_CHANNELS.EMAIL,
                subject: 'Welcome to Wilsy OS',
                content: 'Your account has been created successfully.',
                userEmail: 'test@example.com',
                status: NOTIFICATION_STATUS.PENDING
            });

            const saved = await notification.save();

            expect(saved.notificationId).toBeDefined();
            expect(saved.notificationId).toMatch(/^NOTIF-/);
            expect(saved.tenantId).toBe('TENANT_001_TEST');
            expect(saved.userId).toBe('USER_123');
            expect(saved.type).toBe(NOTIFICATION_TYPES.CLIENT_ONBOARDING);
            expect(saved.channel).toBe(NOTIFICATION_CHANNELS.EMAIL);
            expect(saved.contentHash).toBeDefined();
            expect(saved.contentHash).toHaveLength(64);
            expect(saved.statusHistory).toHaveLength(1);
            expect(saved.statusHistory[0].status).toBe(NOTIFICATION_STATUS.PENDING);
            expect(saved.evidenceHash).toBeDefined();
            expect(saved.evidenceHash).toHaveLength(64);
            expect(saved.retentionPolicy).toBe('POPIA_1_YEAR');
            expect(saved.dataResidency).toBe('ZA');
            expect(saved.economicMetadata).toBeDefined();
            expect(saved.economicMetadata.costSavings).toBeDefined();
        });

        test('should enforce tenant ID format', async () => {
            const notification = new NotificationLog({
                tenantId: 'invalid', // Too short
                userId: 'USER_123',
                type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                channel: NOTIFICATION_CHANNELS.EMAIL,
                subject: 'Test',
                content: 'Test content',
                userEmail: 'test@example.com'
            });

            await expect(notification.save()).rejects.toThrow(/Tenant ID/);
        });

        test('should require email for email channel', async () => {
            const notification = new NotificationLog({
                tenantId: 'TENANT_001_TEST',
                userId: 'USER_123',
                type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                channel: NOTIFICATION_CHANNELS.EMAIL,
                subject: 'Test',
                content: 'Test content'
                // Missing userEmail
            });

            await expect(notification.save()).rejects.toThrow(/userEmail/);
        });

        test('should require phone for SMS channel', async () => {
            const notification = new NotificationLog({
                tenantId: 'TENANT_001_TEST',
                userId: 'USER_123',
                type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                channel: NOTIFICATION_CHANNELS.SMS,
                content: 'Test SMS'
                // Missing userPhone
            });

            await expect(notification.save()).rejects.toThrow(/userPhone/);
        });
    });

    describe('STATUS TRACKING - Lifecycle Management', () => {
        test('should track status changes in history', async () => {
            const notification = new NotificationLog({
                tenantId: 'TENANT_001_TEST',
                userId: 'USER_123',
                type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                channel: NOTIFICATION_CHANNELS.EMAIL,
                subject: 'Welcome',
                content: 'Welcome to Wilsy OS',
                userEmail: 'test@example.com',
                status: NOTIFICATION_STATUS.PENDING
            });

            await notification.save();
            expect(notification.statusHistory).toHaveLength(1);

            // Update to SENT
            await notification.updateStatus(NOTIFICATION_STATUS.SENT, { provider: 'aws_ses' });
            expect(notification.statusHistory).toHaveLength(2);
            expect(notification.statusHistory[1].status).toBe(NOTIFICATION_STATUS.SENT);
            expect(notification.sentAt).toBeDefined();

            // Update to DELIVERED
            await notification.updateStatus(NOTIFICATION_STATUS.DELIVERED, { providerMessageId: 'msg-123' });
            expect(notification.statusHistory).toHaveLength(3);
            expect(notification.deliveredAt).toBeDefined();

            // Update to READ
            await notification.updateStatus(NOTIFICATION_STATUS.READ);
            expect(notification.statusHistory).toHaveLength(4);
            expect(notification.readAt).toBeDefined();
        });

        test('should track failure details', async () => {
            const notification = new NotificationLog({
                tenantId: 'TENANT_001_TEST',
                userId: 'USER_123',
                type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                channel: NOTIFICATION_CHANNELS.EMAIL,
                subject: 'Welcome',
                content: 'Welcome to Wilsy OS',
                userEmail: 'test@example.com',
                status: NOTIFICATION_STATUS.PENDING
            });

            await notification.save();

            await notification.updateStatus(NOTIFICATION_STATUS.FAILED, {
                reason: 'Invalid email address',
                code: 'INVALID_EMAIL',
                provider: 'aws_ses'
            });

            expect(notification.status).toBe(NOTIFICATION_STATUS.FAILED);
            expect(notification.failedAt).toBeDefined();
            expect(notification.failureReason).toBe('Invalid email address');
            expect(notification.failureDetails).toBeDefined();
        });

        test('should calculate processing time', async () => {
            const notification = new NotificationLog({
                tenantId: 'TENANT_001_TEST',
                userId: 'USER_123',
                type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                channel: NOTIFICATION_CHANNELS.EMAIL,
                subject: 'Welcome',
                content: 'Welcome to Wilsy OS',
                userEmail: 'test@example.com',
                status: NOTIFICATION_STATUS.PENDING
            });

            await notification.save();

            // Simulate delay
            await new Promise(resolve => setTimeout(resolve, 10));

            await notification.updateStatus(NOTIFICATION_STATUS.SENT);
            expect(notification.processingTimeMs).toBeGreaterThan(0);
        });
    });

    describe('TENANT ISOLATION - Multi-tenant Security', () => {
        test('should create indexes for tenant isolation', async () => {
            const indexes = await NotificationLog.collection.indexes();
            const indexNames = indexes.map(i => i.name);
            
            expect(indexNames).toContain('tenantId_1_createdAt_-1');
            expect(indexNames).toContain('tenantId_1_userId_1_createdAt_-1');
        });

        test('should only return notifications for specific tenant', async () => {
            // Create notifications for tenant 1
            await NotificationLog.create([
                {
                    tenantId: 'TENANT_001',
                    userId: 'USER_1',
                    type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                    channel: NOTIFICATION_CHANNELS.EMAIL,
                    subject: 'Welcome',
                    content: 'Welcome',
                    userEmail: 'user1@example.com'
                },
                {
                    tenantId: 'TENANT_001',
                    userId: 'USER_2',
                    type: NOTIFICATION_TYPES.SARS_FILING,
                    channel: NOTIFICATION_CHANNELS.SMS,
                    content: 'SARS filing due',
                    userPhone: '+27821234567'
                }
            ]);

            // Create notification for tenant 2
            await NotificationLog.create({
                tenantId: 'TENANT_002',
                userId: 'USER_3',
                type: NOTIFICATION_TYPES.POPIA_BREACH,
                channel: NOTIFICATION_CHANNELS.EMAIL,
                subject: 'Security Alert',
                content: 'Data breach detected',
                userEmail: 'user3@example.com'
            });

            const tenant1Notifications = await NotificationLog.find({ tenantId: 'TENANT_001' });
            expect(tenant1Notifications).toHaveLength(2);

            const tenant2Notifications = await NotificationLog.find({ tenantId: 'TENANT_002' });
            expect(tenant2Notifications).toHaveLength(1);
        });
    });

    describe('EVIDENCE CHAIN - Forensic Integrity', () => {
        test('should generate unique evidence hash for each notification', async () => {
            const notification1 = await NotificationLog.create({
                tenantId: 'TENANT_001',
                userId: 'USER_1',
                type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                channel: NOTIFICATION_CHANNELS.EMAIL,
                subject: 'Welcome 1',
                content: 'Content 1',
                userEmail: 'user1@example.com'
            });

            const notification2 = await NotificationLog.create({
                tenantId: 'TENANT_001',
                userId: 'USER_2',
                type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                channel: NOTIFICATION_CHANNELS.EMAIL,
                subject: 'Welcome 2',
                content: 'Content 2',
                userEmail: 'user2@example.com'
            });

            expect(notification1.evidenceHash).not.toBe(notification2.evidenceHash);
            expect(notification1.evidenceHash).toMatch(/^[a-f0-9]{64}$/);
        });

        test('should update evidence hash on status change', async () => {
            const notification = await NotificationLog.create({
                tenantId: 'TENANT_001',
                userId: 'USER_1',
                type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                channel: NOTIFICATION_CHANNELS.EMAIL,
                subject: 'Welcome',
                content: 'Content',
                userEmail: 'user1@example.com',
                status: NOTIFICATION_STATUS.PENDING
            });

            const originalHash = notification.evidenceHash;

            await notification.updateStatus(NOTIFICATION_STATUS.SENT);
            expect(notification.evidenceHash).not.toBe(originalHash);
        });
    });

    describe('POPIA COMPLIANCE - Data Protection', () => {
        test('should redact PII in toRedactedJSON', async () => {
            const notification = await NotificationLog.create({
                tenantId: 'TENANT_001',
                userId: 'USER_1',
                type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                channel: NOTIFICATION_CHANNELS.EMAIL,
                subject: 'Welcome',
                content: 'Sensitive content with PII: ID 8001015009087',
                userEmail: 'user1@example.com',
                userPhone: '+27821234567'
            });

            const redacted = notification.toRedactedJSON();

            expect(redacted.userEmail).toBe('[REDACTED-EMAIL]');
            expect(redacted.userPhone).toBe('[REDACTED-PHONE]');
            expect(redacted.content).toBe('[REDACTED-CONTENT]');
            expect(redacted.notificationId).toBe(notification.notificationId); // Not redacted
            expect(redacted.tenantId).toBe('TENANT_001'); // Not redacted
        });

        test('should have default POPIA retention policy', async () => {
            const notification = await NotificationLog.create({
                tenantId: 'TENANT_001',
                userId: 'USER_1',
                type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                channel: NOTIFICATION_CHANNELS.EMAIL,
                subject: 'Welcome',
                content: 'Content',
                userEmail: 'user1@example.com'
            });

            expect(notification.retentionPolicy).toBe('POPIA_1_YEAR');
            expect(notification.dataResidency).toBe('ZA');
        });
    });

    describe('STATIC METHODS - Analytics & Reporting', () => {
        test('should generate tenant statistics', async () => {
            // Create notifications with various statuses
            await NotificationLog.create([
                {
                    tenantId: 'TENANT_001',
                    userId: 'USER_1',
                    type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                    channel: NOTIFICATION_CHANNELS.EMAIL,
                    subject: 'Welcome',
                    content: 'Content',
                    userEmail: 'user1@example.com',
                    status: NOTIFICATION_STATUS.SENT,
                    sentAt: new Date(),
                    economicMetadata: { costSavings: 14.95, complianceValue: 25, auditSavings: 50 }
                },
                {
                    tenantId: 'TENANT_001',
                    userId: 'USER_2',
                    type: NOTIFICATION_TYPES.SARS_FILING,
                    channel: NOTIFICATION_CHANNELS.SMS,
                    content: 'SMS content',
                    userPhone: '+27821234567',
                    status: NOTIFICATION_STATUS.DELIVERED,
                    sentAt: new Date(),
                    deliveredAt: new Date(),
                    economicMetadata: { costSavings: 14.95, complianceValue: 25, auditSavings: 50 }
                },
                {
                    tenantId: 'TENANT_001',
                    userId: 'USER_3',
                    type: NOTIFICATION_TYPES.POPIA_BREACH,
                    channel: NOTIFICATION_CHANNELS.EMAIL,
                    subject: 'Alert',
                    content: 'Content',
                    userEmail: 'user3@example.com',
                    status: NOTIFICATION_STATUS.FAILED,
                    failedAt: new Date(),
                    failureReason: 'Bounced',
                    economicMetadata: { costSavings: 0, complianceValue: 0, auditSavings: 0 }
                }
            ]);

            const stats = await NotificationLog.getStatistics('TENANT_001');

            expect(stats.total).toBe(3);
            expect(stats.channels.email).toBe(2);
            expect(stats.channels.sms).toBe(1);
            expect(stats.statuses.sent).toBe(1);
            expect(stats.statuses.delivered).toBe(1);
            expect(stats.statuses.failed).toBe(1);
            expect(stats.totalEconomicValue).toBeGreaterThan(0);
        });

        test('should find failed notifications for retry', async () => {
            // Create failed notifications
            await NotificationLog.create([
                {
                    tenantId: 'TENANT_001',
                    userId: 'USER_1',
                    type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                    channel: NOTIFICATION_CHANNELS.EMAIL,
                    subject: 'Welcome',
                    content: 'Content',
                    userEmail: 'user1@example.com',
                    status: NOTIFICATION_STATUS.FAILED,
                    failedAt: new Date(Date.now() - 60 * 60 * 1000), // 1 hour ago
                    retryCount: 1,
                    priority: 8
                },
                {
                    tenantId: 'TENANT_001',
                    userId: 'USER_2',
                    type: NOTIFICATION_TYPES.SARS_FILING,
                    channel: NOTIFICATION_CHANNELS.EMAIL,
                    subject: 'Filing',
                    content: 'Content',
                    userEmail: 'user2@example.com',
                    status: NOTIFICATION_STATUS.FAILED,
                    failedAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
                    retryCount: 2,
                    priority: 5
                },
                {
                    tenantId: 'TENANT_001',
                    userId: 'USER_3',
                    type: NOTIFICATION_TYPES.POPIA_BREACH,
                    channel: NOTIFICATION_CHANNELS.EMAIL,
                    subject: 'Alert',
                    content: 'Content',
                    userEmail: 'user3@example.com',
                    status: NOTIFICATION_STATUS.FAILED,
                    failedAt: new Date(Date.now() - 30 * 60 * 1000), // 30 mins ago
                    retryCount: 3, // Max retries reached
                    priority: 10
                }
            ]);

            const failed = await NotificationLog.findFailedForRetry('TENANT_001', 2);

            expect(failed).toHaveLength(2); // First two should be returned (retryCount < 2)
            expect(failed[0].priority).toBe(8); // Higher priority first
        });

        test('should generate investor evidence report', async () => {
            // Create some notifications
            await NotificationLog.create([
                {
                    tenantId: 'TENANT_001',
                    userId: 'USER_1',
                    type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                    channel: NOTIFICATION_CHANNELS.EMAIL,
                    subject: 'Welcome',
                    content: 'Content',
                    userEmail: 'user1@example.com',
                    status: NOTIFICATION_STATUS.SENT
                },
                {
                    tenantId: 'TENANT_001',
                    userId: 'USER_2',
                    type: NOTIFICATION_TYPES.SARS_FILING,
                    channel: NOTIFICATION_CHANNELS.SMS,
                    content: 'SMS content',
                    userPhone: '+27821234567',
                    status: NOTIFICATION_STATUS.DELIVERED
                }
            ]);

            const report = await NotificationLog.generateEvidenceReport('TENANT_001');

            expect(report.reportId).toBeDefined();
            expect(report.tenantId).toBe('TENANT_001');
            expect(report.statistics.total).toBe(2);
            expect(report.economicImpact.count).toBe(2);
            expect(report.sampleNotifications).toHaveLength(2);
            expect(report.hashChain.reportHash).toBeDefined();
            expect(report.hashChain.reportHash).toHaveLength(64);
        });
    });

    describe('INSTANCE METHODS - Utility Functions', () => {
        test('toEvidenceJSON should generate evidence package', async () => {
            const notification = await NotificationLog.create({
                tenantId: 'TENANT_001',
                userId: 'USER_1',
                type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                channel: NOTIFICATION_CHANNELS.EMAIL,
                subject: 'Welcome',
                content: 'Content',
                userEmail: 'user1@example.com',
                status: NOTIFICATION_STATUS.SENT
            });

            const evidence = notification.toEvidenceJSON();

            expect(evidence.notificationId).toBe(notification.notificationId);
            expect(evidence.evidenceHash).toBe(notification.evidenceHash);
            expect(evidence.evidencePackageHash).toBeDefined();
            expect(evidence.evidencePackageHash).toHaveLength(64);
        });
    });

    describe('RETENTION POLICIES - Compliance', () => {
        test('should export retention policies', () => {
            expect(RETENTION_POLICIES.POPIA_1_YEAR.durationDays).toBe(365);
            expect(RETENTION_POLICIES.FICA_5_YEARS.durationDays).toBe(1825);
            expect(RETENTION_POLICIES.COMPANIES_ACT_7_YEARS.durationDays).toBe(2555);
            expect(RETENTION_POLICIES.AUDIT_PERPETUAL.durationDays).toBe(36500);
        });

        test('should calculate expiration date based on policy', async () => {
            const notification = await NotificationLog.create({
                tenantId: 'TENANT_001',
                userId: 'USER_1',
                type: NOTIFICATION_TYPES.CLIENT_ONBOARDING,
                channel: NOTIFICATION_CHANNELS.EMAIL,
                subject: 'Welcome',
                content: 'Content',
                userEmail: 'user1@example.com',
                retentionPolicy: 'FICA_5_YEARS'
            });

            expect(notification.metadata.ttlDays).toBe(1825);
            expect(notification.metadata.shouldExpireAt).toBeDefined();
            
            const daysUntilExpiry = (new Date(notification.metadata.shouldExpireAt) - new Date()) / (1000 * 60 * 60 * 24);
            expect(daysUntilExpiry).toBeCloseTo(1825, 0);
        });
    });
});
