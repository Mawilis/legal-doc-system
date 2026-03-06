/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ HARDWARE SCHEMA UNIT TESTS - WILSY OS 2050                               ║
  ║ Testing Quantum Hardware Security Module                                  ║
  ║ VERSION: 2.0.1 - ALL TESTS PASSING                                       ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { expect } from 'chai';
import mongoose from 'mongoose';
import crypto from 'crypto';
import { MongoMemoryServer } from 'mongodb-memory-server';
import HardwareSchema, { 
  HARDWARE_TYPES, 
  ATTESTATION_TYPES,
  QUANTUM_ALGORITHMS 
} from '../../../models/schemas/HardwareSchema.js';

describe('🔐 WILSY OS 2050 - HARDWARE SECURITY SCHEMA', function() {
  this.timeout(30000);
  
  let mongoServer;
  let Hardware;
  let testUserId;
  let connection;

  before(async () => {
    // 🔧 FIX: Check for existing connection and close it
    if (mongoose.connection.readyState !== 0) {
      await mongoose.disconnect();
    }
    
    mongoServer = await MongoMemoryServer.create();
    const uri = mongoServer.getUri();
    
    // Create a new connection specifically for this test
    connection = await mongoose.createConnection(uri, {
      maxPoolSize: 10,
      minPoolSize: 2,
      socketTimeoutMS: 45000,
      connectTimeoutMS: 30000,
      serverSelectionTimeoutMS: 30000
    });
    
    // Register schema with this connection
    Hardware = connection.model('Hardware', HardwareSchema);
    testUserId = new mongoose.Types.ObjectId();
  });

  after(async () => {
    // Close only our connection
    if (connection) {
      await connection.close();
    }
    if (mongoServer) {
      await mongoServer.stop();
    }
  });

  beforeEach(async () => {
    if (Hardware) {
      await Hardware.deleteMany({});
    }
  });

  // ==========================================================================
  // ✅ VALIDATION TESTS
  // ==========================================================================
  describe('✅ VALIDATION', () => {
    it('should create valid YubiKey hardware entry', async () => {
      const hardware = new Hardware({
        keyId: crypto.randomUUID(),
        hardwareType: HARDWARE_TYPES.YUBIKEY_5,
        attestationType: ATTESTATION_TYPES.FIDO2,
        publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCYZM6Gj+o\n-----END PUBLIC KEY-----',
        registeredBy: testUserId,
        registeredIp: '192.168.1.100',
        serialNumber: 'YK12345678'
      });

      const saved = await hardware.save();
      expect(saved).to.have.property('_id');
      expect(saved.keyId).to.match(/^[a-f0-9-]{36}$/);
      expect(saved.hardwareType).to.equal(HARDWARE_TYPES.YUBIKEY_5);
      expect(saved.status).to.equal('active');
    });

    it('should create valid quantum hardware entry', async () => {
      const hardware = new Hardware({
        keyId: `quantum-${crypto.randomBytes(32).toString('hex')}`,
        hardwareType: HARDWARE_TYPES.QHSM,
        attestationType: ATTESTATION_TYPES.QUANTUM,
        quantumAlgorithm: QUANTUM_ALGORITHMS.DILITHIUM_5,
        publicKey: `quantum-${crypto.randomBytes(64).toString('hex')}`,
        registeredBy: testUserId,
        quantumSignature: crypto.randomBytes(128).toString('hex'),
        entanglementId: `entangled-${crypto.randomBytes(16).toString('hex')}`
      });

      const saved = await hardware.save();
      expect(saved).to.have.property('_id');
      expect(saved.quantumAlgorithm).to.equal(QUANTUM_ALGORITHMS.DILITHIUM_5);
      expect(saved.quantumSecurity.quantumReady).to.be.false;
    });

    it('should reject invalid key ID format', async () => {
      const hardware = new Hardware({
        keyId: 'invalid-key',
        hardwareType: HARDWARE_TYPES.YUBIKEY_5,
        attestationType: ATTESTATION_TYPES.FIDO2,
        publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCYZM6Gj+o\n-----END PUBLIC KEY-----',
        registeredBy: testUserId
      });

      try {
        await hardware.save();
        expect.fail('Should have thrown validation error');
      } catch (error) {
        expect(error.errors.keyId).to.exist;
      }
    });

    it('should reject invalid public key format', async () => {
      const hardware = new Hardware({
        keyId: crypto.randomUUID(),
        hardwareType: HARDWARE_TYPES.YUBIKEY_5,
        attestationType: ATTESTATION_TYPES.FIDO2,
        publicKey: 'invalid-public-key',
        registeredBy: testUserId
      });

      try {
        await hardware.save();
        expect.fail('Should have thrown validation error');
      } catch (error) {
        expect(error.errors.publicKey).to.exist;
      }
    });
  });

  // ==========================================================================
  // 🔐 ATTESTATION TESTS
  // ==========================================================================
  describe('🔐 ATTESTATION', () => {
    it('should store complete attestation chain', async () => {
      const hardware = new Hardware({
        keyId: crypto.randomUUID(),
        hardwareType: HARDWARE_TYPES.YUBIKEY_5,
        attestationType: ATTESTATION_TYPES.FIDO2,
        publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCYZM6Gj+o\n-----END PUBLIC KEY-----',
        registeredBy: testUserId,
        attestation: {
          certificate: '-----BEGIN CERTIFICATE-----\nMIID...',
          certificateChain: ['-----BEGIN CERTIFICATE-----\nMIID...', '-----BEGIN CERTIFICATE-----\nMIID...'],
          signature: crypto.randomBytes(256).toString('hex'),
          format: 'x509',
          validFrom: new Date(),
          validTo: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
          issuer: 'Yubico',
          subject: 'YubiKey 5',
          aaguid: 'f8a011f3-8c0a-4d15-8004-5e8a1b7c3d2e',
          aaguidVerified: true
        }
      });

      const saved = await hardware.save();
      expect(saved.attestation.certificateChain).to.have.length(2);
      expect(saved.attestation.aaguidVerified).to.be.true;
      expect(saved.attestation.issuer).to.equal('Yubico');
    });

    it('should verify attestation via instance method', async () => {
      const hardware = new Hardware({
        keyId: crypto.randomUUID(),
        hardwareType: HARDWARE_TYPES.YUBIKEY_5,
        attestationType: ATTESTATION_TYPES.FIDO2,
        publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCYZM6Gj+o\n-----END PUBLIC KEY-----',
        registeredBy: testUserId
      });

      await hardware.save();
      const verification = await hardware.verifyAttestation();
      expect(verification.verified).to.be.true;
      expect(verification.method).to.equal(ATTESTATION_TYPES.FIDO2);
    });
  });

  // ==========================================================================
  // 🔌 HSM INTEGRATION TESTS
  // ==========================================================================
  describe('🔌 HSM INTEGRATION', () => {
    it('should store HSM configuration', async () => {
      const hardware = new Hardware({
        keyId: `qhsm-${crypto.randomBytes(32).toString('hex')}`,
        hardwareType: HARDWARE_TYPES.YUBIHSM_2,
        attestationType: ATTESTATION_TYPES.PIV,
        publicKey: `qhsm-${crypto.randomBytes(64).toString('hex')}`,
        registeredBy: testUserId,
        hsmInfo: {
          slot: 1,
          sessionHandle: crypto.randomBytes(16).toString('hex'),
          mechanism: 'CKM_RSA_PKCS',
          keyPairId: `key-${crypto.randomBytes(8).toString('hex')}`,
          pkcs11: {
            library: '/usr/lib/softhsm/libsofthsm2.so',
            slotId: 0,
            tokenLabel: 'Quantum HSM Token'
          },
          keyAttributes: {
            type: 'signing',
            extractable: false,
            sensitive: true
          }
        }
      });

      const saved = await hardware.save();
      expect(saved.hsmInfo.slot).to.equal(1);
      expect(saved.hsmInfo.keyAttributes.sensitive).to.be.true;
    });

    it('should support cloud HSM providers', async () => {
      const hardware = new Hardware({
        keyId: `qhsm-${crypto.randomBytes(32).toString('hex')}`,
        hardwareType: HARDWARE_TYPES.QHSM,
        attestationType: ATTESTATION_TYPES.QUANTUM,
        publicKey: `qhsm-${crypto.randomBytes(64).toString('hex')}`,
        registeredBy: testUserId,
        hsmInfo: {
          cloudProvider: 'aws-cloudhsm',
          keyAttributes: {
            type: 'quantum',
            extractable: false
          }
        }
      });

      const saved = await hardware.save();
      expect(saved.hsmInfo.cloudProvider).to.equal('aws-cloudhsm');
    });
  });

  // ==========================================================================
  // 🔮 QUANTUM SECURITY TESTS
  // ==========================================================================
  describe('🔮 QUANTUM SECURITY', () => {
    it('should perform quantum verification', async () => {
      const hardware = new Hardware({
        keyId: `quantum-${crypto.randomBytes(32).toString('hex')}`,
        hardwareType: HARDWARE_TYPES.QHSM,
        attestationType: ATTESTATION_TYPES.QUANTUM,
        quantumAlgorithm: QUANTUM_ALGORITHMS.DILITHIUM_5,
        publicKey: `quantum-${crypto.randomBytes(64).toString('hex')}`,
        registeredBy: testUserId,
        entanglementId: `entangled-${crypto.randomBytes(16).toString('hex')}`
      });

      await hardware.save();
      const quantumResult = await hardware.quantumVerify();
      
      expect(quantumResult.quantumVerified).to.be.true;
      expect(quantumResult.algorithm).to.equal(QUANTUM_ALGORITHMS.DILITHIUM_5);
    });

    it('should fail quantum verification without algorithm', async () => {
      const hardware = new Hardware({
        keyId: crypto.randomUUID(),
        hardwareType: HARDWARE_TYPES.YUBIKEY_5,
        attestationType: ATTESTATION_TYPES.FIDO2,
        publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCYZM6Gj+o\n-----END PUBLIC KEY-----',
        registeredBy: testUserId
      });

      await hardware.save();
      
      try {
        await hardware.quantumVerify();
        expect.fail('Should have thrown error');
      } catch (error) {
        expect(error.message).to.include('Quantum algorithm not configured');
      }
    });
  });

  // ==========================================================================
  // 💾 BACKUP & RECOVERY TESTS
  // ==========================================================================
  describe('💾 BACKUP & RECOVERY', () => {
    it('should create backup via instance method', async () => {
      const hardware = new Hardware({
        keyId: crypto.randomUUID(),
        hardwareType: HARDWARE_TYPES.YUBIKEY_5,
        attestationType: ATTESTATION_TYPES.FIDO2,
        publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCYZM6Gj+o\n-----END PUBLIC KEY-----',
        registeredBy: testUserId
      });

      await hardware.save();
      const backupId = await hardware.createBackup('primary');
      
      expect(backupId).to.be.a('string');
      expect(backupId).to.match(/^backup-/);
      
      const updated = await Hardware.findById(hardware._id);
      expect(updated.backupInfo.backupKeyId).to.equal(backupId);
      expect(updated.backupInfo.backupType).to.equal('primary');
    });

    it('should support quantum backup', async () => {
      const hardware = new Hardware({
        keyId: `quantum-${crypto.randomBytes(32).toString('hex')}`,
        hardwareType: HARDWARE_TYPES.QHSM,
        attestationType: ATTESTATION_TYPES.QUANTUM,
        quantumAlgorithm: QUANTUM_ALGORITHMS.DILITHIUM_5,
        publicKey: `quantum-${crypto.randomBytes(64).toString('hex')}`,
        registeredBy: testUserId
      });

      await hardware.save();
      const backupId = await hardware.createBackup('quantum_entangled');
      
      const updated = await Hardware.findById(hardware._id);
      expect(updated.backupInfo.quantumBackup).to.be.true;
    });
  });

  // ==========================================================================
  // 📊 AUDIT LOG TESTS
  // ==========================================================================
  describe('📊 AUDIT LOG', () => {
    it('should log audit events', async () => {
      const hardware = new Hardware({
        keyId: crypto.randomUUID(),
        hardwareType: HARDWARE_TYPES.YUBIKEY_5,
        attestationType: ATTESTATION_TYPES.FIDO2,
        publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCYZM6Gj+o\n-----END PUBLIC KEY-----',
        registeredBy: testUserId
      });

      await hardware.save();
      await hardware.logAudit('authenticated', testUserId, '192.168.1.100', true);
      
      const updated = await Hardware.findById(hardware._id);
      expect(updated.auditLog).to.have.length(1);
      expect(updated.auditLog[0].action).to.equal('authenticated');
    });

    it('should create security events', async () => {
      const hardware = new Hardware({
        keyId: crypto.randomUUID(),
        hardwareType: HARDWARE_TYPES.YUBIKEY_5,
        attestationType: ATTESTATION_TYPES.FIDO2,
        publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCYZM6Gj+o\n-----END PUBLIC KEY-----',
        registeredBy: testUserId
      });

      await hardware.save();
      await hardware.createSecurityEvent('suspicious_activity', 'high', 'Multiple failed authentication attempts');
      
      const updated = await Hardware.findById(hardware._id);
      expect(updated.securityEvents).to.have.length(1);
      expect(updated.securityEvents[0].severity).to.equal('high');
    });
  });

  // ==========================================================================
  // 🔐 REVOCATION TESTS
  // ==========================================================================
  describe('🔐 REVOCATION', () => {
    it('should revoke hardware via instance method', async () => {
      const hardware = new Hardware({
        keyId: crypto.randomUUID(),
        hardwareType: HARDWARE_TYPES.YUBIKEY_5,
        attestationType: ATTESTATION_TYPES.FIDO2,
        publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCYZM6Gj+o\n-----END PUBLIC KEY-----',
        registeredBy: testUserId
      });

      await hardware.save();
      await hardware.revoke('lost', testUserId);
      
      const updated = await Hardware.findById(hardware._id);
      expect(updated.status).to.equal('revoked');
      expect(updated.revokedReason).to.equal('lost');
    });
  });

  // ==========================================================================
  // 📊 STATIC METHOD TESTS
  // ==========================================================================
  describe('📊 STATIC METHODS', () => {
    beforeEach(async () => {
      // Create test data
      await Hardware.create([
        {
          keyId: crypto.randomUUID(),
          hardwareType: HARDWARE_TYPES.YUBIKEY_5,
          attestationType: ATTESTATION_TYPES.FIDO2,
          publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCYZM6Gj+o\n-----END PUBLIC KEY-----',
          registeredBy: testUserId,
          status: 'active'
        },
        {
          keyId: `quantum-${crypto.randomBytes(32).toString('hex')}`,
          hardwareType: HARDWARE_TYPES.QHSM,
          attestationType: ATTESTATION_TYPES.QUANTUM,
          quantumAlgorithm: QUANTUM_ALGORITHMS.DILITHIUM_5,
          publicKey: `quantum-${crypto.randomBytes(64).toString('hex')}`,
          registeredBy: testUserId,
          status: 'active',
          quantumSecurity: { quantumReady: true }
        },
        {
          keyId: crypto.randomUUID(),
          hardwareType: HARDWARE_TYPES.YUBIKEY_5,
          attestationType: ATTESTATION_TYPES.FIDO2,
          publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCYZM6Gj+o\n-----END PUBLIC KEY-----',
          registeredBy: testUserId,
          status: 'compromised'
        }
      ]);
    });

    it('findActiveForUser should return active hardware', async () => {
      const active = await Hardware.findActiveForUser(testUserId);
      expect(active).to.have.length(2);
    });

    it('findCompromised should return compromised hardware', async () => {
      const compromised = await Hardware.findCompromised();
      expect(compromised).to.have.length(1);
    });

    it('findQuantumReady should return quantum-ready hardware', async () => {
      const quantum = await Hardware.findQuantumReady();
      expect(quantum).to.have.length(1);
    });

    it('generateQuantumKey should create quantum key', async () => {
      const quantumKey = await Hardware.generateQuantumKey('DILITHIUM_5');
      expect(quantumKey.algorithm).to.equal('DILITHIUM_5');
      expect(quantumKey.keyId).to.match(/^quantum-/);
    });

    it('getStats should return correct statistics', async () => {
      const stats = await Hardware.getStats();
      expect(stats.total).to.equal(3);
      expect(stats.active).to.equal(2);
      expect(stats.compromised).to.equal(1);
      expect(stats.quantumReady).to.equal(1);
    });
  });
});
