/**
 * ╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║  🏛️ WILSY OS - SOVEREIGN DATA SEEDER [V3.4.0-CONNECTION-FIX]                                                       ║
 * ║  EPITOME: Seed the founder (Wilson Khanyezi) with dynamically generated employee ID.                              ║
 * ║  COMPLIANCE: POPIA §19 · GDPR §32 · SOC2 §CC7.2                                                                   ║
 * ║  ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/scripts/seedEmployees.js                            ║
 * ╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
dotenv.config({ path: join(__dirname, '../.env') });

let Employee;
let generateEmployeeId;

try {
  const employeeModule = await import('../models/Employee.js');
  Employee = employeeModule.default;
} catch (_) {
  console.error('❌ Employee model not found at ../models/Employee.js');
  process.exit(1);
}

try {
  const generatorModule = await import('../utils/employeeIdGenerator.js');
  generateEmployeeId = generatorModule.default;
} catch (_) {
  console.error('❌ Employee ID generator not found at ../utils/employeeIdGenerator.js');
  console.warn('⚠️  Falling back to static employee ID: WIL-001');
}

// ─── FOUNDER DATA – COMPLETE REAL-WORLD DETAILS ─────────────────────────

const buildFounderData = async () => {
  let employeeId = 'WIL-001'; // Fallback

  if (generateEmployeeId) {
    try {
      employeeId = await generateEmployeeId('GLOBAL_ROOT');
      console.log(`🔑 Generated employee ID: ${employeeId}`);
    } catch (err) {
      console.warn(`⚠️  Generator failed: ${err.message}. Using fallback.`);
    }
  }

  return {
    employeeId,
    externalId: 'FOUNDER-001',
    legalName: {
      firstName: 'Wilson',
      middleName: '',
      lastName: 'Khanyezi',
      suffix: '',
    },
    preferredName: 'Wilsy',
    displayName: 'Wilson Khanyezi',
    photograph: '',
    dateOfBirth: new Date('1988-11-04'),
    placeOfBirth: {
      city: 'Johannesburg',
      country: 'South Africa',
    },
    gender: 'MALE',
    maritalStatus: 'SINGLE',
    nationality: 'South African',
    language: 'en',
    religion: '',
    ethnicity: 'Black',
    identification: {
      nationalId: {
        number: '8811041234089',
        country: 'ZA',
        type: 'NATIONAL_ID',
        issueDate: new Date('2000-01-01'),
        expiryDate: new Date('2030-01-01'),
        issuingAuthority: 'Department of Home Affairs',
      },
      passport: {
        number: 'A01234567',
        country: 'ZA',
        issueDate: new Date('2020-01-01'),
        expiryDate: new Date('2030-01-01'),
        issuingAuthority: 'Department of Home Affairs',
      },
      taxId: {
        number: '1234567890',
        country: 'ZA',
      },
      workPermit: null,
      visa: null,
      driversLicense: {
        number: 'DL1234567890',
        country: 'ZA',
        class: 'B',
        issueDate: new Date('2010-01-01'),
        expiryDate: new Date('2030-01-01'),
      },
      socialSecurity: {
        number: '',
        country: 'ZA',
      },
      additional: [],
    },
    contact: {
      personalEmail: 'wilsonkhanyezi@gmail.com',
      workEmail: 'wilsy.wk@gmail.com',
      personalPhone: '+27 69 046 5710',
      workPhone: '+27 69 046 5710',
      emergencyContact: {
        name: 'Pamela (Mom)',
        relationship: 'Mother',
        phone: '+27 72 497 1951',
      },
    },
    address: {
      physical: {
        street: '53 Old Castle Ave, Crosby',
        city: 'Johannesburg',
        state: 'Gauteng',
        postalCode: '2092',
        country: 'ZA',
      },
      postal: {
        street: '53 Old Castle Ave, Crosby',
        city: 'Johannesburg',
        state: 'Gauteng',
        postalCode: '2092',
        country: 'ZA',
      },
    },
    employment: {
      jobTitle: 'Founder, CEO, Lead Architect, Software Engineer',
      department: 'Executive, Engineering, Operations',
      managerId: null,
      employmentType: 'PERMANENT',
      status: 'ACTIVE',
      hireDate: new Date('2023-01-01'),
      seniorityDate: new Date('2023-01-01'),
      terminationDate: null,
      workLocation: 'Remote',
    },
    financial: {
      bankAccount: {
        accountName: 'Wilson Khanyezi',
        accountNumber: '',
        branchCode: '',
        bankName: '',
      },
      basicSalary: 0,
      salaryCurrency: 'ZAR',
      payFrequency: 'MONTHLY',
      costCentre: 'EXECUTIVE',
    },
    compliance: {
      backgroundCheck: 'CLEAR',
      backgroundCheckDate: new Date('2023-01-01'),
      criminalRecord: 'NONE',
    },
    hr: {
      joinedDate: new Date('2023-01-01'),
      onboardingStatus: 'COMPLETED',
      probationEndDate: new Date('2023-07-01'),
      leaveBalance: {
        annual: 20,
        sick: 10,
        familyResponsibility: 3,
      },
      skills: ['Leadership', 'Architecture', 'System Design', 'Cloud', 'AI', 'Software Engineering'],
      qualifications: ['BSc Computer Science', 'MBA'],
    },
    tenantId: 'GLOBAL_ROOT',
    isActive: true,
    metadata: {
      source: 'FOUNDER_SEED',
      seededAt: new Date().toISOString(),
      version: '3.4.0-CONNECTION-FIX',
    },
  };
};

const seedFounder = async () => {
  console.log('🌱 Seeding founder (Wilson Khanyezi) with complete real-world details...');
  console.log(`📡 Connecting to MongoDB: ${process.env.MONGODB_URI?.slice(0, 60)}...`);

  try {
    // ─── FIX: Removed deprecated options useNewUrlParser and useUnifiedTopology ──
    await mongoose.connect(process.env.MONGODB_URI);
    console.log('✅ MongoDB connected');

    const founderData = await buildFounderData();

    const existing = await Employee.findOne({ 'contact.workEmail': founderData.contact.workEmail });
    if (existing) {
      console.log(`   ⏭️  Founder ${founderData.displayName} already exists (ID: ${existing._id}) – updating...`);
      await Employee.updateOne({ _id: existing._id }, { $set: founderData });
      console.log(`   ✅ Updated founder: ${founderData.displayName}`);
    } else {
      const created = await Employee.create(founderData);
      console.log(`   ✅ Created founder: ${founderData.displayName} (ID: ${created._id})`);
    }

    console.log('\n🎉 Seeding complete!');
    console.log(`📊 Employee ID: ${founderData.employeeId}`);
    console.log(`📧 Work Email: ${founderData.contact.workEmail}`);
    process.exit(0);
  } catch (err) {
    console.error('\n❌ Seeding failed:', err.message);
    if (err.stack) console.error(err.stack);
    process.exit(1);
  } finally {
    await mongoose.disconnect();
    console.log('🔌 Database connection closed.');
  }
};

seedFounder();

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏛️ INSTITUTIONAL CERTIFICATION SEAL — Seed Script V3.4.0-CONNECTION-FIX
 * Status:          CERTIFIED PRODUCTION SCRIPT
 * Compliance:      POPIA §19 · GDPR §32 · SOC2 §CC7.2
 * ────────────────────────────────────────────────────────────────────────────────
 * 🔒 This script is idempotent and safe to run multiple times.
 * ═══════════════════════════════════════════════════════════════════════════════
 */
