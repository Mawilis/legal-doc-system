/*
 * ====================================================================================
 * WILSY OS SOVEREIGN INTEGRATION TESTS – BLOCKCHAIN SERVICE
 * ====================================================================================
 * FILE:        client/tests/blockchain.test.js
 * VERSION:     v1.0.0-OMEGA-PHASE9
 * AUTHORITY:   Wilsy OS Kennel EOS / Lead Architect @WilsyCore
 * EPITOME:     Integration tests for blockchain anchoring, notarization,
 *              proof verification, and compliance sealing.
 * INSTITUTIONAL CONTEXT: Phase 9 – Blockchain Anchoring.
 * COMPLIANCE:  POPIA §19, GDPR §32, SOC2 §CC7.2
 * COLLABORATION: @WilsyCore @QALead @BlockchainLead
 * ====================================================================================
 */

import { describe, it, expect, vi, beforeAll, afterAll } from 'vitest';
import crypto from 'node:crypto';

// Mock external heavy dependencies before importing the service
vi.mock('web3', () => ({
  default: vi.fn(),
}));
vi.mock('elliptic', () => ({
  ec: vi.fn(),
}));
vi.mock('ethereumjs-tx', () => ({
  Transaction: vi.fn(),
}));
vi.mock('merkletreejs', () => ({
  MerkleTree: vi.fn(),
}));
vi.mock('sha3', () => ({
  SHA3: vi.fn(),
}));

// Mock mongoose models
vi.mock('../../server/models/Telemetry.js', () => ({
  default: {
    create: vi.fn().mockResolvedValue({}),
  },
}));
vi.mock('../../server/models/blockchainTransactionModel.js', () => ({
  default: vi.fn().mockImplementation(() => ({
    save: vi.fn().mockResolvedValue({ _id: 'mock-tx-id' }),
  })),
}));
vi.mock('../../server/models/documentModel.js', () => ({
  default: {
    findByIdAndUpdate: vi.fn().mockResolvedValue({}),
  },
}));
vi.mock('../../server/models/firmModel.js', () => ({
  default: {},
}));

// Mock cryptoCore
vi.mock('../../server/utils/cryptoCore.js', () => ({
  default: {
    encrypt: vi.fn().mockReturnValue('encrypted'),
    generateForensicId: vi.fn().mockReturnValue('BC-123'),
  },
}));

// Mock logger
vi.mock('../../server/utils/logger.js', () => ({
  default: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
}));

// Now import the service (after mocks are in place)
import blockchainService, {
  anchorToBlockchain,
  verifyBlockchainProof,
  createSmartContractCompliance,
} from '../../server/services/blockchainService.js';

describe('Blockchain Service Integration Tests', () => {

  // ─── notarizeDocument ──────────────────────────────────────────────────────
  describe('notarizeDocument', () => {
    const mockDocument = {
      _id: 'doc123',
      contentHash: 'abc123',
      content: 'some content',
    };
    const mockFirmId = 'firm456';
    const mockUser = {
      _id: 'user789',
      role: 'firmAdmin',
      tenantId: 'tenant1',
      mfaEnabled: true,
    };

    it('should notarize a document successfully with evidence seal', async () => {
      // Force simulation mode for reliability
      const origActive = blockchainService.isActive;
      blockchainService.isActive = false;

      const result = await blockchainService.notarizeDocument(mockDocument, mockFirmId, mockUser);
      expect(result).toHaveProperty('success', true);
      expect(result).toHaveProperty('transactionId');
      expect(result).toHaveProperty('blockchainTxHash');
      expect(result).toHaveProperty('documentHash');
      expect(result).toHaveProperty('evidenceSeal');
      expect(typeof result.evidenceSeal).toBe('string');
      expect(result).toHaveProperty('latencyMs');
      expect(result.latencyMs).toBeGreaterThanOrEqual(0);

      blockchainService.isActive = origActive;
    });

    it('should throw if user role is unauthorized', async () => {
      const badUser = { ...mockUser, role: 'viewer' };
      await expect(blockchainService.notarizeDocument(mockDocument, mockFirmId, badUser))
        .rejects.toThrow(/Unauthorized role/);
    });

    it('should throw if MFA is not enabled', async () => {
      const noMfaUser = { ...mockUser, mfaEnabled: false };
      await expect(blockchainService.notarizeDocument(mockDocument, mockFirmId, noMfaUser))
        .rejects.toThrow(/MFA must be enabled/);
    });

    it('should throw if tenant context is missing', async () => {
      const noTenantUser = { ...mockUser, tenantId: undefined };
      await expect(blockchainService.notarizeDocument(mockDocument, mockFirmId, noTenantUser))
        .rejects.toThrow(/Tenant context missing/);
    });
  });

  // ─── verifyBlockchainProof ────────────────────────────────────────────────
  describe('verifyBlockchainProof', () => {
    it('should return verified proof with timestamp and latency', async () => {
      const result = await verifyBlockchainProof('0x123');
      expect(result).toHaveProperty('verified', true);
      expect(result).toHaveProperty('timestamp');
      expect(result.timestamp).toBeInstanceOf(Date);
      expect(result).toHaveProperty('proof', 'INSTITUTIONAL_VERIFIED');
      expect(result).toHaveProperty('latencyMs');
      expect(result.latencyMs).toBeGreaterThanOrEqual(0);
    });
  });

  // ─── createSmartContractCompliance ────────────────────────────────────────
  describe('createSmartContractCompliance', () => {
    it('should deploy a compliance contract and return seal and latency', async () => {
      const result = await createSmartContractCompliance('rec123', { clause: 'popia19' });
      expect(result).toHaveProperty('contractAddress');
      expect(result.contractAddress).toMatch(/^0x[a-f0-9]{40}$/);
      expect(result).toHaveProperty('status', 'DEPLOYED');
      expect(result).toHaveProperty('seal');
      expect(typeof result.seal).toBe('string');
      expect(result).toHaveProperty('latencyMs');
      expect(result.latencyMs).toBeGreaterThanOrEqual(0);
    });
  });

  // ─── anchorToBlockchain (exported bridge) ──────────────────────────────
  describe('anchorToBlockchain', () => {
    it('should call notarizeDocument with proper parameters', async () => {
      const spy = vi.spyOn(blockchainService, 'notarizeDocument').mockResolvedValue({ success: true });
      const metadata = {
        documentId: 'doc123',
        firmId: 'firm456',
        userId: 'user789',
        tenantId: 'tenant1',
        mfaEnabled: true,
      };
      const result = await anchorToBlockchain('hash123', metadata);
      expect(result).toHaveProperty('success', true);
      expect(spy).toHaveBeenCalledOnce();
      spy.mockRestore();
    });
  });
});

/*
 * ====================================================================================
 * INSTITUTIONAL CERTIFICATION SEAL – BLOCKCHAIN INTEGRATION TESTS
 * Status:          PRODUCTION READY
 * Version:         v1.0.0-OMEGA-PHASE9
 * Compliance:      POPIA §19 | GDPR §32 | SOC2 §CC7.2
 * Coverage:        notarizeDocument, verifyBlockchainProof, createSmartContractCompliance
 * Mocks:           Web3, elliptic, mongoose, models (vitest style)
 * ====================================================================================
 */
