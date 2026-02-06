/* eslint-disable no-undef */
/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██████╗ ███╗   ██╗███████╗██╗     ███████╗██╗████████╗            ║
║  ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║     ██╔════╝██║╚══██╔══╝            ║
║  ██║     ██║   ██║██╔██╗ ██║█████╗  ██║     █████╗  ██║   ██║               ║
║  ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║     ██╔══╝  ██║   ██║               ║
║  ╚██████╗╚██████╔╝██║ ╚████║██║     ███████╗██║     ██║   ██║               ║
║   ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚══════╝╚═╝     ╚═╝   ╚═╝               ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  FILE: /Users/wilsonkhanyezi/legal-doc-system/server/__tests__/models/Case.test.js ║
║                                                                              ║
║  PURPOSE: Comprehensive Jest tests for Case Model with PAIA & Conflict      ║
║           ASCII: [Setup]→[Validation]→[PAIA]→[Conflict]→[Queries]→[Teardown]║
║  COMPLIANCE: Test coverage for all PAIA/POPIA/LPC requirements              ║
║                                                                              ║
║  CHIEF ARCHITECT: Wilson Khanyezi                                           ║
║  EMAIL: wilsy.wk@gmail.com | CELL: +27 69 046 5710                          ║
║                                                                              ║
║  FILENAME: Case.test.js                                                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

/**
 * @file Comprehensive Jest tests for Case Model with PAIA & Conflict Screening
 * @module tests/models/Case
 * @description Complete test suite for Case model with PAIA tracking
 * @requires mongoose, ../models/Case, mongodb-memory-server
 * @version 1.0.0
 * @since Wilsy OS v3.0
 * @author Wilson Khanyezi
 */

const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const Case = require('../../models/Case');

// Mock the AuditLedger and Conflict models
jest.mock('../../models/AuditLedger', () => ({
  log: jest.fn().mockResolvedValue({ _id: 'mockAuditId' })
}));

jest.mock('../../models/Conflict', () => ({
  screenForConflicts: jest.fn().mockResolvedValue([]),
  find: jest.fn().mockReturnValue({
    select: jest.fn().mockReturnValue({
      lean: jest.fn().mockResolvedValue([])
    })
  })
}));

// Test constants
const TEST_TENANT_ID = 'tenant_test_12345';
const TEST_USER_ID = new mongoose.Types.ObjectId();
const TEST_CASE_NUMBER = 'CC-2024-0001';
const TEST_CLIENT_NAME = 'Test Client Corporation';

// Test data factories
const createValidCaseData = (overrides = {}) => ({
  tenantId: TEST_TENANT_ID,
  caseNumber: TEST_CASE_NUMBER,
  title: 'Test Legal Matter - Contract Dispute',
  status: Case.CASE_STATUSES.PRE_INTAKE,
  client: {
    name: TEST_CLIENT_NAME,
    entityId: 'CORP-2024-001',
    contactDetails: {
      email: 'client@testcorp.co.za',
      phone: '+27 11 123 4567'
    },
    paiaDesignation: {
      isInformationOfficer: false
    }
  },
  opponents: [{
    name: 'Opposing Party Ltd',
    blindIndex: 'opp_blind_001',
    role: 'ADVERSE_PARTY',
    entityId: 'OPP-001',
    paiaRelevant: false
  }],
  legalTeam: [{
    userId: TEST_USER_ID,
    role: 'LEAD_ATTORNEY',
    assignedDate: new Date(),
    isActive: true,
    paiaResponsibilities: ['REQUEST_PROCESSING']
  }],
  matterDetails: {
    jurisdiction: 'High Court of South Africa',
    courtOrTribunal: 'Gauteng Division, Pretoria',
    matterType: 'LITIGATION',
    description: 'Contractual dispute regarding service delivery',
    openingDate: new Date(),
    estimatedCloseDate: new Date(Date.now() + 180 * 24 * 60 * 60 * 1000), // 180 days from now
    valueAtRisk: 5000000,
    currency: 'ZAR',
    paiaClassification: 'ROUTINE_DISCLOSURE'
  },
  compliance: {
    popiaConsentObtained: true,
    lpcRule7Compliant: false,
    riskLevel: 'MEDIUM',
    ectCompliant: false,
    ficaVerified: true,
    trustAccountRequired: false
  },
  audit: {
    createdBy: TEST_USER_ID,
    createdAt: new Date(),
    version: 1
  },
  metadata: {
    isConfidential: true,
    classification: 'CONFIDENTIAL',
    tags: ['contract', 'dispute', 'commercial'],
    retentionPolicy: {
      rule: 'LPC_6YR',
      disposalDate: new Date(Date.now() + 6 * 365 * 24 * 60 * 60 * 1000),
      paiaOverride: false
    },
    storageLocation: {
      dataResidencyCompliance: 'ZA_ONLY',
      primaryRegion: 'af-south-1'
    }
  },
  ...overrides
});

const createValidPaiaRequestData = (overrides = {}) => ({
  requestId: `PAIA-${TEST_CASE_NUMBER}-${Date.now()}`,
  requesterType: 'INDIVIDUAL',
  requesterDetails: {
    name: 'John Doe',
    idNumber: '8001015000089',
    contactEmail: 'john.doe@example.com',
    contactPhone: '+27 82 555 1234',
    postalAddress: '123 Test Street, Pretoria, 0001'
  },
  requestedInformation: [{
    description: 'All correspondence related to contract XYZ',
    documentType: 'EMAIL_CORRESPONDENCE',
    dateRange: {
      from: new Date('2024-01-01'),
      to: new Date('2024-06-30')
    },
    specificReference: 'Contract ref: XYZ-2024-001'
  }],
  requestDate: new Date(),
  statutoryDeadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days from now
  status: Case.PAIA_REQUEST_STATUSES.PENDING,
  metadata: {
    isUrgent: false,
    manualTrackingRequired: false
  },
  audit: {
    createdBy: TEST_USER_ID,
    createdAt: new Date()
  },
  ...overrides
});

// MongoDB Memory Server instance
let mongoServer;
let mongoUri;

/**
 * Test Suite: Case Model
 * Tests all functionality including PAIA tracking and conflict screening
 */
describe('Case Model Tests', () => {
  /**
   * Setup MongoDB Memory Server before all tests
   */
  beforeAll(async () => {
    // Start MongoDB Memory Server
    mongoServer = await MongoMemoryServer.create();
    mongoUri = mongoServer.getUri();
    
    // Connect to test database
    await mongoose.connect(mongoUri, {
      useNewUrlParser: true,
      useUnifiedTopology: true
    });
    
    console.log('Connected to MongoDB Memory Server for testing');
  });

  /**
   * Clean up database after each test
   */
  beforeEach(async () => {
    // Clear all collections
    const collections = mongoose.connection.collections;
    for (const key in collections) {
      await collections[key].deleteMany();
    }
    
    // Reset all mocks
    jest.clearAllMocks();
  });

  /**
   * Disconnect and stop MongoDB after all tests
   */
  afterAll(async () => {
    await mongoose.disconnect();
    await mongoServer.stop();
    console.log('Disconnected from MongoDB Memory Server');
  });

  /**
   * SECTION 1: BASIC VALIDATION TESTS
   * Tests schema validation and required fields
   */
  describe('Basic Validation Tests', () => {
    test('should create a valid case with all required fields', async () => {
      const caseData = createValidCaseData();
      const testCase = new Case(caseData);
      
      const savedCase = await testCase.save();
      
      expect(savedCase._id).toBeDefined();
      expect(savedCase.caseNumber).toBe(TEST_CASE_NUMBER);
      expect(savedCase.tenantId).toBe(TEST_TENANT_ID);
      expect(savedCase.status).toBe(Case.CASE_STATUSES.PRE_INTAKE);
      expect(savedCase.audit.createdBy).toEqual(TEST_USER_ID);
      expect(savedCase.audit.version).toBe(1);
    });

    test('should require tenantId field', async () => {
      const caseData = createValidCaseData({ tenantId: undefined });
      const testCase = new Case(caseData);
      
      await expect(testCase.save()).rejects.toThrow(
        /Tenant ID is required/
      );
    });

    test('should require caseNumber field', async () => {
      const caseData = createValidCaseData({ caseNumber: undefined });
      const testCase = new Case(caseData);
      
      await expect(testCase.save()).rejects.toThrow(
        /Case number is required/
      );
    });

    test('should validate caseNumber format', async () => {
      const invalidCaseNumbers = ['INVALID', 'AB-2024', '123-456-789', 'AB-2024-12345'];
      
      for (const invalidNumber of invalidCaseNumbers) {
        const caseData = createValidCaseData({ caseNumber: invalidNumber });
        const testCase = new Case(caseData);
        
        await expect(testCase.save()).rejects.toThrow(
          /Case number must match format/
        );
      }
    });

    test('should validate tenantId format', async () => {
      const invalidTenantIds = ['invalid', 'tenant', 'tenant_', 'tenant_too_long_123456789012345678901234567890'];
      
      for (const invalidId of invalidTenantIds) {
        const caseData = createValidCaseData({ tenantId: invalidId });
        const testCase = new Case(caseData);
        
        await expect(testCase.save()).rejects.toThrow(
          /Tenant ID must match pattern/
        );
      }
    });

    test('should require client name', async () => {
      const caseData = createValidCaseData();
      caseData.client.name = undefined;
      const testCase = new Case(caseData);
      
      await expect(testCase.save()).rejects.toThrow(
        /Client name is required/
      );
    });

    test('should validate client email format', async () => {
      const caseData = createValidCaseData();
      caseData.client.contactDetails.email = 'invalid-email';
      const testCase = new Case(caseData);
      
      await expect(testCase.save()).rejects.toThrow(
        /Please provide a valid email address/
      );
    });

    test('should enforce unique caseNumber constraint', async () => {
      // Create first case
      const caseData1 = createValidCaseData();
      const testCase1 = new Case(caseData1);
      await testCase1.save();
      
      // Try to create second case with same case number
      const caseData2 = createValidCaseData({ title: 'Duplicate Case' });
      const testCase2 = new Case(caseData2);
      
      await expect(testCase2.save()).rejects.toThrow(
        /duplicate key error/
      );
    });
  });

  /**
   * SECTION 2: PAIA REQUEST TRACKING TESTS
   * Tests PAIA-specific functionality
   */
  describe('PAIA Request Tracking Tests', () => {
    let testCase;

    beforeEach(async () => {
      // Create a case for PAIA tests
      const caseData = createValidCaseData();
      testCase = new Case(caseData);
      await testCase.save();
    });

    test('should add PAIA request to case', async () => {
      const paiaRequestData = createValidPaiaRequestData({
        createdBy: TEST_USER_ID
      });
      
      const result = await Case.addPaiaRequest(
        testCase._id,
        paiaRequestData
      );
      
      expect(result.success).toBe(true);
      expect(result.caseId).toEqual(testCase._id);
      expect(result.requestId).toMatch(/^PAIA-CC-2024-0001-/);
      expect(result.statutoryDeadline).toBeInstanceOf(Date);
      
      // Verify case was updated
      const updatedCase = await Case.findById(testCase._id);
      expect(updatedCase.paiaRequests).toHaveLength(1);
      expect(updatedCase.paiaTracking.totalRequests).toBe(1);
      expect(updatedCase.paiaTracking.pendingRequests).toBe(1);
      expect(updatedCase.paiaTracking.lastRequestDate).toBeInstanceOf(Date);
    });

    test('should update PAIA request status', async () => {
      // First add a PAIA request
      const paiaRequestData = createValidPaiaRequestData({
        createdBy: TEST_USER_ID
      });
      
      await Case.addPaiaRequest(testCase._id, paiaRequestData);
      
      // Update the request status
      const updatedCase = await Case.findById(testCase._id);
      const requestId = updatedCase.paiaRequests[0].requestId;
      
      const updateResult = await updatedCase.updatePaiaRequestStatus(
        requestId,
        {
          status: Case.PAIA_REQUEST_STATUSES.GRANTED,
          decisionNotes: 'Information granted in full',
          reviewedBy: TEST_USER_ID,
          reviewedAt: new Date(),
          updatedBy: TEST_USER_ID
        }
      );
      
      expect(updateResult.success).toBe(true);
      expect(updateResult.previousStatus).toBe(Case.PAIA_REQUEST_STATUSES.PENDING);
      expect(updateResult.newStatus).toBe(Case.PAIA_REQUEST_STATUSES.GRANTED);
      
      // Verify tracking counters updated
      const finalCase = await Case.findById(testCase._id);
      expect(finalCase.paiaTracking.pendingRequests).toBe(0);
      expect(finalCase.paiaRequests[0].status).toBe(Case.PAIA_REQUEST_STATUSES.GRANTED);
      expect(finalCase.paiaRequests[0].responseDetails.respondedAt).toBeInstanceOf(Date);
    });

    test('should handle PAIA request with exemptions', async () => {
      const paiaRequestData = createValidPaiaRequestData({
        createdBy: TEST_USER_ID
      });
      
      await Case.addPaiaRequest(testCase._id, paiaRequestData);
      
      const updatedCase = await Case.findById(testCase._id);
      const requestId = updatedCase.paiaRequests[0].requestId;
      
      await updatedCase.updatePaiaRequestStatus(
        requestId,
        {
          status: Case.PAIA_REQUEST_STATUSES.PARTIALLY_GRANTED,
          decisionNotes: 'Partially granted with exemptions',
          reviewDetails: {
            reviewedBy: TEST_USER_ID,
            reviewedAt: new Date(),
            exemptionsApplied: [{
              section: '37',
              reason: 'Legal professional privilege applies',
              partialRelease: true
            }]
          },
          updatedBy: TEST_USER_ID
        }
      );
      
      const finalCase = await Case.findById(testCase._id);
      expect(finalCase.paiaRequests[0].reviewDetails.exemptionsApplied).toHaveLength(1);
      expect(finalCase.paiaTracking.exemptionUsage.section37).toBe(1);
    });

    test('should validate PAIA statutory deadline is in future', async () => {
      const paiaRequestData = createValidPaiaRequestData({
        statutoryDeadline: new Date('2020-01-01'), // Past date
        createdBy: TEST_USER_ID
      });
      
      await Case.addPaiaRequest(testCase._id, paiaRequestData);
      
      // Try to save case with past deadline
      const updatedCase = await Case.findById(testCase._id);
      
      await expect(updatedCase.save()).rejects.toThrow(
        /has a past statutory deadline/
      );
    });

    test('should calculate paiaDeadlineApproaching virtual property', async () => {
      const paiaRequestData = createValidPaiaRequestData({
        statutoryDeadline: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000), // 2 days from now
        createdBy: TEST_USER_ID
      });
      
      await Case.addPaiaRequest(testCase._id, paiaRequestData);
      
      const updatedCase = await Case.findById(testCase._id);
      expect(updatedCase.paiaDeadlineApproaching).toBe(true);
    });

    test('should calculate hasActivePaiaRequests virtual property', async () => {
      const paiaRequestData = createValidPaiaRequestData({
        createdBy: TEST_USER_ID
      });
      
      await Case.addPaiaRequest(testCase._id, paiaRequestData);
      
      const updatedCase = await Case.findById(testCase._id);
      expect(updatedCase.hasActivePaiaRequests).toBe(true);
      
      // Update to non-active status
      await updatedCase.updatePaiaRequestStatus(
        updatedCase.paiaRequests[0].requestId,
        {
          status: Case.PAIA_REQUEST_STATUSES.GRANTED,
          updatedBy: TEST_USER_ID
        }
      );
      
      const finalCase = await Case.findById(testCase._id);
      expect(finalCase.hasActivePaiaRequests).toBe(false);
    });

    test('should get cases with approaching PAIA deadlines', async () => {
      // Create multiple cases with PAIA requests
      for (let i = 1; i <= 3; i++) {
        const caseData = createValidCaseData({
          caseNumber: `CC-2024-100${i}`,
          title: `Test Case ${i}`
        });
        const newCase = new Case(caseData);
        await newCase.save();
        
        const paiaRequestData = createValidPaiaRequestData({
          requestId: `PAIA-CC-2024-100${i}-${Date.now()}`,
          statutoryDeadline: new Date(Date.now() + i * 24 * 60 * 60 * 1000), // 1, 2, 3 days from now
          createdBy: TEST_USER_ID
        });
        
        await Case.addPaiaRequest(newCase._id, paiaRequestData);
      }
      
      const casesWithDeadlines = await Case.getCasesWithApproachingPaiaDeadlines(
        TEST_TENANT_ID,
        3 // 3 days threshold
      );
      
      expect(casesWithDeadlines).toHaveLength(3);
      expect(casesWithDeadlines[0].pendingRequests).toHaveLength(1);
    });
  });

  /**
   * SECTION 3: CONFLICT SCREENING TESTS
   * Tests conflict screening functionality
   */
  describe('Conflict Screening Tests', () => {
    let testCase;

    beforeEach(async () => {
      // Mock Conflict.screenForConflicts to return no conflicts
      require('../../models/Conflict').screenForConflicts.mockResolvedValue([]);
      
      const caseData = createValidCaseData();
      testCase = new Case(caseData);
      await testCase.save();
    });

    test('should perform conflict screening on new case', async () => {
      const screeningResult = await testCase.performConflictScreening();
      
      expect(screeningResult.screened).toBe(true);
      expect(screeningResult.foundConflicts).toBe(0);
      expect(screeningResult.status).toBe('CLEARED');
      expect(testCase.conflictStatus.checked).toBe(true);
      expect(testCase.conflictStatus.clearanceDate).toBeInstanceOf(Date);
      expect(testCase.conflictStatus.clearanceMethod).toBe('AUTOMATED');
    });

    test('should detect conflicts and place case on legal hold', async () => {
      // Mock Conflict.screenForConflicts to return a critical conflict
      const mockConflict = {
        _id: new mongoose.Types.ObjectId(),
        conflictReference: 'CONF-2024-001',
        severity: Case.CONFLICT_SEVERITIES.CRITICAL,
        status: 'active',
        conflictType: 'DIRECT_CONFLICT',
        description: 'Attorney previously represented opposing party'
      };
      
      require('../../models/Conflict').screenForConflicts.mockResolvedValue([mockConflict]);
      
      const screeningResult = await testCase.performConflictScreening();
      
      expect(screeningResult.screened).toBe(true);
      expect(screeningResult.foundConflicts).toBe(1);
      expect(screeningResult.criticalConflicts).toBe(1);
      expect(screeningResult.blockingConflicts).toBe(1);
      expect(screeningResult.status).toBe('BLOCKED');
      expect(testCase.status).toBe(Case.CASE_STATUSES.LEGAL_HOLD);
    });

    test('should manually clear conflicts', async () => {
      // First create a case with conflicts
      const mockConflict = {
        _id: new mongoose.Types.ObjectId(),
        conflictReference: 'CONF-2024-001',
        severity: Case.CONFLICT_SEVERITIES.HIGH,
        status: 'active'
      };
      
      require('../../models/Conflict').screenForConflicts.mockResolvedValue([mockConflict]);
      
      await testCase.performConflictScreening();
      expect(testCase.status).toBe(Case.CASE_STATUSES.LEGAL_HOLD);
      
      // Now manually clear conflicts
      const clearanceResult = await testCase.manuallyClearConflicts({
        clearedBy: TEST_USER_ID,
        clearanceMethod: 'OVERRIDE',
        clearanceNotes: 'Conflict waived by managing partner',
        previousStatus: testCase.status
      });
      
      expect(clearanceResult.success).toBe(true);
      expect(clearanceResult.clearedBy).toEqual(TEST_USER_ID);
      expect(clearanceResult.clearanceMethod).toBe('OVERRIDE');
      expect(testCase.conflictStatus.checked).toBe(true);
      expect(testCase.conflictStatus.clearanceDate).toBeInstanceOf(Date);
      expect(testCase.status).toBe(Case.CASE_STATUSES.PRE_INTAKE);
    });

    test('should skip screening for closed cases', async () => {
      const caseData = createValidCaseData({
        status: Case.CASE_STATUSES.CLOSED
      });
      const closedCase = new Case(caseData);
      
      // Should not call conflict screening for closed cases
      const saveSpy = jest.spyOn(closedCase, 'performConflictScreening');
      await closedCase.save();
      
      expect(saveSpy).not.toHaveBeenCalled();
    });

    test('should handle conflict screening errors gracefully', async () => {
      // Mock Conflict.screenForConflicts to throw error
      require('../../models/Conflict').screenForConflicts.mockRejectedValue(
        new Error('Conflict database unavailable')
      );
      
      const screeningResult = await testCase.performConflictScreening();
      
      expect(screeningResult.screened).toBe(false);
      expect(screeningResult.error).toBe('Conflict database unavailable');
      expect(screeningResult.message).toContain('manual review required');
      expect(testCase.conflictStatus.checked).toBe(false);
    });
  });

  /**
   * SECTION 4: QUERY AND STATIC METHOD TESTS
   * Tests query functionality and static methods
   */
  describe('Query and Static Method Tests', () => {
    beforeEach(async () => {
      // Create multiple test cases
      const cases = [
        createValidCaseData({
          caseNumber: 'CC-2024-0001',
          title: 'Active Case 1',
          status: Case.CASE_STATUSES.ACTIVE,
          'conflictStatus.checked': true
        }),
        createValidCaseData({
          caseNumber: 'CC-2024-0002',
          title: 'Legal Hold Case',
          status: Case.CASE_STATUSES.LEGAL_HOLD,
          'conflictStatus.checked': false
        }),
        createValidCaseData({
          caseNumber: 'CC-2024-0003',
          title: 'Pre-Intake Case',
          status: Case.CASE_STATUSES.PRE_INTAKE,
          'conflictStatus.checked': true
        }),
        createValidCaseData({
          caseNumber: 'CC-2024-0004',
          title: 'Another Active Case',
          status: Case.CASE_STATUSES.ACTIVE,
          'conflictStatus.checked': true,
          client: {
            name: 'Different Client Inc',
            contactDetails: { email: 'different@client.com' }
          }
        })
      ];
      
      for (const caseData of cases) {
        const testCase = new Case(caseData);
        await testCase.save();
      }
    });

    test('should find cases by tenant with pagination', async () => {
      const cases = await Case.findByTenant(TEST_TENANT_ID, {
        page: 1,
        limit: 10
      });
      
      expect(cases).toHaveLength(4);
      expect(cases[0].caseNumber).toBe('CC-2024-0004'); // Sorted by createdAt desc
      expect(cases[0].tenantId).toBe(TEST_TENANT_ID);
    });

    test('should filter cases by status', async () => {
      const activeCases = await Case.findByTenant(TEST_TENANT_ID, {
        status: Case.CASE_STATUSES.ACTIVE
      });
      
      expect(activeCases).toHaveLength(2);
      expect(activeCases[0].status).toBe(Case.CASE_STATUSES.ACTIVE);
      expect(activeCases[1].status).toBe(Case.CASE_STATUSES.ACTIVE);
    });

    test('should filter cases by conflict checked status', async () => {
      const checkedCases = await Case.findByTenant(TEST_TENANT_ID, {
        conflictChecked: true
      });
      
      expect(checkedCases).toHaveLength(3); // 3 cases have conflictStatus.checked = true
    });

    test('should search cases by text', async () => {
      const searchResults = await Case.findByTenant(TEST_TENANT_ID, {
        search: 'Active'
      });
      
      expect(searchResults).toHaveLength(2);
      expect(searchResults[0].title).toContain('Active');
    });

    test('should filter cases with PAIA requests', async () => {
      // Add PAIA request to one case
      const cases = await Case.find({ tenantId: TEST_TENANT_ID });
      const caseWithPaia = cases[0];
      
      const paiaRequestData = createValidPaiaRequestData({
        createdBy: TEST_USER_ID
      });
      
      await Case.addPaiaRequest(caseWithPaia._id, paiaRequestData);
      
      // Test filter
      const casesWithPaia = await Case.findByTenant(TEST_TENANT_ID, {
        hasPaiaRequests: true
      });
      
      expect(casesWithPaia).toHaveLength(1);
      expect(casesWithPaia[0]._id).toEqual(caseWithPaia._id);
    });

    test('should handle findByTenant with callback', (done) => {
      Case.findByTenant(TEST_TENANT_ID, { limit: 2 }, (err, cases) => {
        expect(err).toBeNull();
        expect(cases).toHaveLength(2);
        done();
      });
    });

    test('should run conflict screening via static method', async () => {
      const cases = await Case.find({ tenantId: TEST_TENANT_ID });
      const testCase = cases[0];
      
      // Mock conflict screening to succeed
      require('../../models/Conflict').screenForConflicts.mockResolvedValue([]);
      
      const screeningResult = await Case.runConflictScreening(testCase._id);
      
      expect(screeningResult.screened).toBe(true);
      expect(screeningResult.foundConflicts).toBe(0);
      
      // Verify case was updated
      const updatedCase = await Case.findById(testCase._id);
      expect(updatedCase.conflictStatus.checked).toBe(true);
    });
  });

  /**
   * SECTION 5: VIRTUAL PROPERTY TESTS
   * Tests computed virtual properties
   */
  describe('Virtual Property Tests', () => {
    let testCase;

    beforeEach(async () => {
      const caseData = createValidCaseData({
        matterDetails: {
          ...createValidCaseData().matterDetails,
          openingDate: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000) // 10 days ago
        }
      });
      
      testCase = new Case(caseData);
      await testCase.save();
    });

    test('should calculate isConflictFree correctly', () => {
      // Initially not checked
      expect(testCase.isConflictFree).toBe(false);
      
      // Mark as checked with no conflicts
      testCase.conflictStatus.checked = true;
      testCase.conflictStatus.foundConflicts = [];
      expect(testCase.isConflictFree).toBe(true);
      
      // Mark as checked with conflicts
      testCase.conflictStatus.foundConflicts = [new mongoose.Types.ObjectId()];
      expect(testCase.isConflictFree).toBe(false);
    });

    test('should calculate requiresManualConflictReview correctly', () => {
      // Initially not checked
      expect(testCase.requiresManualConflictReview).toBe(false);
      
      // Checked with conflicts but no clearance
      testCase.conflictStatus.checked = true;
      testCase.conflictStatus.foundConflicts = [new mongoose.Types.ObjectId()];
      testCase.conflictStatus.clearanceDate = undefined;
      expect(testCase.requiresManualConflictReview).toBe(true);
      
      // Checked with conflicts and clearance
      testCase.conflictStatus.clearanceDate = new Date();
      expect(testCase.requiresManualConflictReview).toBe(false);
    });

    test('should calculate daysOpen correctly', () => {
      expect(testCase.daysOpen).toBe(10); // 10 days from openingDate
      
      // Update opening date
      testCase.matterDetails.openingDate = new Date(Date.now() - 5 * 24 * 60 * 60 * 1000);
      expect(testCase.daysOpen).toBe(5);
    });

    test('should calculate paiaDeadlineApproaching correctly', () => {
      // Initially no PAIA requests
      expect(testCase.paiaDeadlineApproaching).toBe(false);
      
      // Add PAIA request with deadline far in future
      testCase.paiaRequests = [createValidPaiaRequestData({
        statutoryDeadline: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000) // 10 days
      })];
      expect(testCase.paiaDeadlineApproaching).toBe(false);
      
      // Update to deadline in 2 days
      testCase.paiaRequests[0].statutoryDeadline = new Date(Date.now() + 2 * 24 * 60 * 60 * 1000);
      expect(testCase.paiaDeadlineApproaching).toBe(true);
    });

    test('should calculate hasActivePaiaRequests correctly', () => {
      // Initially no PAIA requests
      expect(testCase.hasActivePaiaRequests).toBe(false);
      
      // Add active PAIA request
      testCase.paiaRequests = [createValidPaiaRequestData({
        status: Case.PAIA_REQUEST_STATUSES.PENDING
      })];
      expect(testCase.hasActivePaiaRequests).toBe(true);
      
      // Update to non-active status
      testCase.paiaRequests[0].status = Case.PAIA_REQUEST_STATUSES.GRANTED;
      expect(testCase.hasActivePaiaRequests).toBe(false);
    });
  });

  /**
   * SECTION 6: COMPLIANCE AND AUDIT TESTS
   * Tests compliance features and audit trail
   */
  describe('Compliance and Audit Tests', () => {
    test('should enforce data residency compliance', async () => {
      const caseData = createValidCaseData({
        metadata: {
          storageLocation: {
            dataResidencyCompliance: 'ZA_ONLY',
            primaryRegion: 'af-south-1'
          }
        }
      });
      
      const testCase = new Case(caseData);
      await testCase.save();
      
      expect(testCase.metadata.storageLocation.dataResidencyCompliance).toBe('ZA_ONLY');
      expect(testCase.metadata.storageLocation.primaryRegion).toBe('af-south-1');
    });

    test('should validate retention policy rules', async () => {
      const validRules = ['LPC_6YR', 'COMPANIES_ACT_7YR', 'PAIA_5YR', 'PERMANENT'];
      
      for (const rule of validRules) {
        const caseData = createValidCaseData({
          metadata: {
            retentionPolicy: { rule: rule }
          }
        });
        
        const testCase = new Case(caseData);
        await expect(testCase.save()).resolves.toBeDefined();
      }
      
      // Invalid rule should fail
      const invalidCaseData = createValidCaseData({
        metadata: {
          retentionPolicy: { rule: 'INVALID_RULE' }
        }
      });
      
      const invalidCase = new Case(invalidCaseData);
      await expect(invalidCase.save()).rejects.toThrow();
    });

    test('should update audit trail on save', async () => {
      const caseData = createValidCaseData();
      const testCase = new Case(caseData);
      
      const savedCase = await testCase.save();
      expect(savedCase.audit.version).toBe(1);
      expect(savedCase.audit.createdAt).toBeInstanceOf(Date);
      
      // Update the case
      savedCase.title = 'Updated Case Title';
      savedCase.audit.updatedBy = TEST_USER_ID;
      
      const updatedCase = await savedCase.save();
      expect(updatedCase.audit.version).toBe(2);
      expect(updatedCase.audit.updatedAt).toBeInstanceOf(Date);
    });

    test('should require active legal team for active cases', async () => {
      const caseData = createValidCaseData({
        status: Case.CASE_STATUSES.ACTIVE,
        legalTeam: [] // No legal team
      });
      
      const testCase = new Case(caseData);
      
      await expect(testCase.save()).rejects.toThrow(
        /Active cases must have at least one legal team member assigned/
      );
    });

    test('should validate risk level enum', async () => {
      const validRiskLevels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
      
      for (const riskLevel of validRiskLevels) {
        const caseData = createValidCaseData({
          compliance: { riskLevel: riskLevel }
        });
        
        const testCase = new Case(caseData);
        await expect(testCase.save()).resolves.toBeDefined();
      }
      
      // Invalid risk level should fail
      const invalidCaseData = createValidCaseData({
        compliance: { riskLevel: 'INVALID_RISK' }
      });
      
      const invalidCase = new Case(invalidCaseData);
      await expect(invalidCase.save()).rejects.toThrow();
    });
  });

  /**
   * SECTION 7: ERROR HANDLING AND EDGE CASES
   * Tests error scenarios and edge cases
   */
  describe('Error Handling and Edge Cases', () => {
    test('should handle missing required fields gracefully', async () => {
      const invalidCase = new Case({});
      
      await expect(invalidCase.save()).rejects.toThrow();
      
      // Check for specific validation errors
      try {
        await invalidCase.save();
      } catch (error) {
        expect(error.errors).toBeDefined();
        expect(error.errors.tenantId).toBeDefined();
        expect(error.errors.caseNumber).toBeDefined();
        expect(error.errors.title).toBeDefined();
        expect(error.errors['client.name']).toBeDefined();
        expect(error.errors['audit.createdBy']).toBeDefined();
      }
    });

    test('should handle non-existent case for PAIA operations', async () => {
      const nonExistentId = new mongoose.Types.ObjectId();
      const paiaRequestData = createValidPaiaRequestData({
        createdBy: TEST_USER_ID
      });
      
      await expect(
        Case.addPaiaRequest(nonExistentId, paiaRequestData)
      ).rejects.toThrow(/Case not found/);
    });

    test('should handle invalid PAIA request updates', async () => {
      const caseData = createValidCaseData();
      const testCase = new Case(caseData);
      await testCase.save();
      
      await expect(
        testCase.updatePaiaRequestStatus('non-existent-request-id', {})
      ).rejects.toThrow(/PAIA request not found/);
    });

    test('should handle missing clearance data for manual clearance', async () => {
      const caseData = createValidCaseData();
      const testCase = new Case(caseData);
      await testCase.save();
      
      await expect(
        testCase.manuallyClearConflicts({})
      ).rejects.toThrow(/Cleared by user ID is required/);
      
      await expect(
        testCase.manuallyClearConflicts({ clearedBy: TEST_USER_ID })
      ).rejects.toThrow(/Clearance method is required/);
    });

    test('should handle database connection errors gracefully', async () => {
      // Simulate database disconnection
      await mongoose.disconnect();
      
      const caseData = createValidCaseData();
      const testCase = new Case(caseData);
      
      await expect(testCase.save()).rejects.toThrow();
      
      // Reconnect for other tests
      await mongoose.connect(mongoUri);
    });
  });
});

/**
 * MERMAID DIAGRAM: Test Flow Visualization
 * 
 * ```mermaid
 * flowchart TD
 *     A[Test Start] --> B[Setup MongoDB Memory]
 *     B --> C[Clear Collections]
 *     C --> D{Test Category}
 *     
 *     D --> E[Basic Validation]
 *     D --> F[PAIA Tracking]
 *     D --> G[Conflict Screening]
 *     D --> H[Query Methods]
 *     D --> I[Virtual Properties]
 *     D --> J[Compliance]
 *     D --> K[Error Handling]
 *     
 *     E --> L[✓ Save Valid Case]
 *     E --> M[✗ Validate Required Fields]
 *     E --> N[✗ Validate Formats]
 *     
 *     F --> O[✓ Add PAIA Request]
 *     F --> P[✓ Update PAIA Status]
 *     F --> Q[✓ Handle Deadlines]
 *     
 *     G --> R[✓ Auto Screening]
 *     G --> S[✓ Conflict Detection]
 *     G --> T[✓ Manual Clearance]
 *     
 *     H --> U[✓ Find by Tenant]
 *     H --> V[✓ Filter & Search]
 *     H --> W[✓ Pagination]
 *     
 *     I --> X[✓ Calculate Days Open]
 *     I --> Y[✓ Check Conflict Free]
 *     I --> Z[✓ PAIA Status Checks]
 *     
 *     J --> AA[✓ Data Residency]
 *     J --> BB[✓ Retention Policy]
 *     J --> CC[✓ Audit Trail]
 *     
 *     K --> DD[✗ Handle Missing Fields]
 *     K --> EE[✗ Handle Invalid Updates]
 *     K --> FF[✗ Database Errors]
 *     
 *     L --> GG[Teardown]
 *     M --> GG
 *     N --> GG
 *     O --> GG
 *     P --> GG
 *     Q --> GG
 *     R --> GG
 *     S --> GG
 *     T --> GG
 *     U --> GG
 *     V --> GG
 *     W --> GG
 *     X --> GG
 *     Y --> GG
 *     Z --> GG
 *     AA --> GG
 *     BB --> GG
 *     CC --> GG
 *     DD --> GG
 *     EE --> GG
 *     FF --> GG
 *     
 *     GG[Stop MongoDB & Cleanup]
 *     
 *     style A fill:#e1f5fe
 *     style GG fill:#ffebee
 *     style L fill:#e8f5e8
 *     style M fill:#fff3e0
 * ```
 */

// Export test utilities for other test files
module.exports = {
  createValidCaseData,
  createValidPaiaRequestData,
  TEST_TENANT_ID,
  TEST_USER_ID,
  TEST_CASE_NUMBER,
  TEST_CLIENT_NAME
};

// SACRED SIGNATURE
// Wilsy Touching Lives.
// Chief Architect: Wilson Khanyezi — wilsy.wk@gmail.com | +27 69 046 5710
