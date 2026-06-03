/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║                         THE SOVEREIGN OPERATING SYSTEM FOR GLOBAL BUSINESS                                                         ║
 * ║                              SOVEREIGN DATABASE SEEDER | GOD MODE PROTOCOL                                                          ║
 * ║                                   NO COMPETITION. NO COMPROMISE. THE FUTURE, NOW.                                                  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import crypto from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '../.env') });

import User from '../models/User.js';
import TenantConfig from '../models/TenantConfig.js';
import Deal, { DEAL_TYPES, DEAL_STAGES, CURRENCIES, MATERIALITY_LEVELS, DEAL_RISK_LEVELS } from '../models/Deal.js';

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/wilsy-os';

async function seedCitadel() {
  try {
    console.log('🚀 INITIATING SOVEREIGN DATABASE SEED...');
    await mongoose.connect(MONGODB_URI);
    console.log('✅ Connected to Quantum Vault');

    // 1. Find or Create the Sovereign Tenant with the correct ObjectId
    const tenantId = '69cb49e30276ea90ea1a0961';

    let tenant = await TenantConfig.findById(tenantId);

    if (!tenant) {
      console.log('📦 Creating missing Sovereign Tenant...');
      tenant = await TenantConfig.create({
        _id: tenantId,
        tenantId: 'WILSY-PTY-LTD',
        name: 'WILSY (PTY) LTD',
        legalEntityName: 'WILSY (PTY) LTD',
        registrationNumber: '2024/617944/07',
        tier: 'SOVEREIGN',
        status: 'ACTIVE',
        businessType: 'CORPORATE',
        industry: 'TECHNOLOGY',
        tagline: 'The Sovereign Operating System for Global Business',
        contactEmail: 'info@wilsy.com',
        contactPhone: '+27 69 046 5710',
        address: {
          street: 'Quantum House, 15 Technology Lane',
          city: 'Johannesburg',
          province: 'Gauteng',
          country: 'South Africa',
          postalCode: '2196'
        },
        branding: {
          primaryColor: '#ffd700',
          secondaryColor: '#10b981',
          accentColor: '#3b82f6',
          logo: '/assets/images/superadmin/wilsy.jpeg',
          favicon: '/favicon.ico',
          theme: 'dark'
        },
        settings: {
          allowMultiTenant: true,
          enforceMFA: true,
          retentionYears: 100,
          auditLevel: 'FORENSIC',
          defaultLanguage: 'en',
          timezone: 'Africa/Johannesburg'
        },
        features: [
          'AI_SALES_INTELLIGENCE',
          'QUANTUM_SECURITY',
          '100_YEAR_RETENTION',
          'MULTI_TENANT_ISOLATION',
          'FORENSIC_AUDIT',
          'BLOCKCHAIN_VERIFICATION'
        ],
        limits: {
          maxUsers: 10000,
          maxStorageGB: 10000,
          maxApiRequestsPerHour: 10000000,
          maxDealsPerMonth: 10000
        },
        metadata: {
          createdBy: 'WILSON_KHAYEZYI',
          purpose: 'SOVEREIGN_ROOT_OF_TRUST',
          quantumProtected: true,
          ciproRegistered: true,
          companyName: 'WILSY (PTY) LTD',
          registrationDate: new Date()
        },
        createdAt: new Date(),
        updatedAt: new Date()
      });
      console.log(`✅ Tenant Created: ${tenant.name} (${tenant._id})`);
    } else {
      console.log(`✅ Tenant Found: ${tenant.name} (${tenant._id})`);
    }

    // 2. Fix Siyabonga's User Profile
    const user = await User.findOneAndUpdate(
      { email: 'wilsywk@gmail.com' },
      {
        tenantId: tenant._id,
        role: 'sales_representative',
        tenantName: tenant.name,
        isActive: true,
        emailVerified: true,
        "metadata.company": tenant.name,
        "metadata.department": "Sales & Customer Success",
        "metadata.tenantName": tenant.name
      },
      { returnDocument: 'after' }
    );

    if (user) {
      console.log(`✅ Siyabonga Linked: ${user.email} -> ${tenant.name}`);
    } else {
      console.log('⚠️ User not found with email: wilsywk@gmail.com');
    }

    // 3. Fix Wilson's user
    const wilson = await User.findOneAndUpdate(
      { email: 'wilsonkhanyezi@gmail.com' },
      {
        tenantId: tenant._id,
        tenantName: tenant.name,
        isActive: true,
        "metadata.company": tenant.name,
        "metadata.tenantName": tenant.name
      },
      { returnDocument: 'after' }
    );
    if (wilson) {
      console.log(`✅ Wilson Updated: ${wilson.email} -> ${tenant.name}`);
    }

    // 4. Wipe old deals
    const tenantIdString = tenant._id.toString();
    await Deal.deleteMany({ tenantId: tenantIdString });

    const ownerId = user?._id || (await User.findOne({ email: 'wilsywk@gmail.com' }))?._id;
    if (!ownerId) {
      console.log('⚠️ No owner found, skipping deal creation');
    } else {
      const ownerIdString = ownerId.toString();

      const deals = [
        {
          dealId: `DEAL-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
          tenantId: tenantIdString,
          acquirerId: new mongoose.Types.ObjectId(),
          targetId: new mongoose.Types.ObjectId(),
          dealType: DEAL_TYPES.ACQUISITION,
          stage: DEAL_STAGES.PROPOSAL,
          value: 1200000,
          currency: CURRENCIES.ZAR,
          materiality: MATERIALITY_LEVELS.SMALL_MERGER,
          riskLevel: DEAL_RISK_LEVELS.MEDIUM,
          consideration: {
            cash: 1000000,
            shares: 200000,
            description: "80% cash, 20% equity"
          },
          timeline: {
            expectedClosing: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
          },
          probability: {
            overall: 88,
            regulatory: 85,
            shareholder: 90,
            financing: 85,
            integration: 90
          },
          audit: {
            createdBy: ownerIdString,
            createdAt: new Date()
          },
          metadata: {
            source: 'seed',
            tags: ['enterprise', 'strategic']
          },
          previousHash: null,
          forensicHash: crypto.createHash('sha256').update(JSON.stringify({
            dealId: `DEAL-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
            tenantId: tenantIdString,
            stage: DEAL_STAGES.PROPOSAL,
            value: 1200000
          })).digest('hex')
        },
        {
          dealId: `DEAL-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
          tenantId: tenantIdString,
          acquirerId: new mongoose.Types.ObjectId(),
          targetId: new mongoose.Types.ObjectId(),
          dealType: DEAL_TYPES.MERGER,
          stage: DEAL_STAGES.NEGOTIATION,
          value: 2800000,
          currency: CURRENCIES.ZAR,
          materiality: MATERIALITY_LEVELS.INTERMEDIATE_MERGER,
          riskLevel: DEAL_RISK_LEVELS.MEDIUM,
          consideration: {
            cash: 1800000,
            shares: 1000000,
            description: "64% cash, 36% equity"
          },
          timeline: {
            expectedClosing: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000)
          },
          probability: {
            overall: 92,
            regulatory: 88,
            shareholder: 95,
            financing: 90,
            integration: 95
          },
          audit: {
            createdBy: ownerIdString,
            createdAt: new Date()
          },
          metadata: {
            source: 'seed',
            tags: ['merger', 'high-value']
          },
          previousHash: null,
          forensicHash: crypto.createHash('sha256').update(JSON.stringify({
            dealId: `DEAL-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
            tenantId: tenantIdString,
            stage: DEAL_STAGES.NEGOTIATION,
            value: 2800000
          })).digest('hex')
        },
        {
          dealId: `DEAL-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
          tenantId: tenantIdString,
          acquirerId: new mongoose.Types.ObjectId(),
          targetId: new mongoose.Types.ObjectId(),
          dealType: DEAL_TYPES.STRATEGIC_INVESTMENT,
          stage: DEAL_STAGES.QUALIFIED,
          value: 450000,
          currency: CURRENCIES.ZAR,
          materiality: MATERIALITY_LEVELS.EXEMPT,
          riskLevel: DEAL_RISK_LEVELS.LOW,
          consideration: {
            cash: 450000,
            description: "All cash"
          },
          timeline: {
            expectedClosing: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000)
          },
          probability: {
            overall: 65,
            regulatory: 95,
            shareholder: 80,
            financing: 70,
            integration: 60
          },
          audit: {
            createdBy: ownerIdString,
            createdAt: new Date()
          },
          metadata: {
            source: 'seed',
            tags: ['investment', 'growth']
          },
          previousHash: null,
          forensicHash: crypto.createHash('sha256').update(JSON.stringify({
            dealId: `DEAL-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
            tenantId: tenantIdString,
            stage: DEAL_STAGES.QUALIFIED,
            value: 450000
          })).digest('hex')
        },
        {
          dealId: `DEAL-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
          tenantId: tenantIdString,
          acquirerId: new mongoose.Types.ObjectId(),
          targetId: new mongoose.Types.ObjectId(),
          dealType: DEAL_TYPES.ACQUISITION,
          stage: DEAL_STAGES.PROPOSAL,
          value: 890000,
          currency: CURRENCIES.ZAR,
          materiality: MATERIALITY_LEVELS.SMALL_MERGER,
          riskLevel: DEAL_RISK_LEVELS.MEDIUM,
          consideration: {
            cash: 690000,
            shares: 200000,
            description: "77% cash, 23% equity"
          },
          timeline: {
            expectedClosing: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
          },
          probability: {
            overall: 45,
            regulatory: 60,
            shareholder: 55,
            financing: 50,
            integration: 45
          },
          audit: {
            createdBy: ownerIdString,
            createdAt: new Date()
          },
          metadata: {
            source: 'seed',
            tags: ['prospecting']
          },
          previousHash: null,
          forensicHash: crypto.createHash('sha256').update(JSON.stringify({
            dealId: `DEAL-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
            tenantId: tenantIdString,
            stage: DEAL_STAGES.PROPOSAL,
            value: 890000
          })).digest('hex')
        },
        {
          dealId: `DEAL-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
          tenantId: tenantIdString,
          acquirerId: new mongoose.Types.ObjectId(),
          targetId: new mongoose.Types.ObjectId(),
          dealType: DEAL_TYPES.JOINT_VENTURE,
          stage: DEAL_STAGES.PROPOSAL,
          value: 3500000,
          currency: CURRENCIES.ZAR,
          materiality: MATERIALITY_LEVELS.LARGE_MERGER,
          riskLevel: DEAL_RISK_LEVELS.HIGH,
          consideration: {
            cash: 2000000,
            shares: 1500000,
            description: "57% cash, 43% equity"
          },
          timeline: {
            expectedClosing: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000)
          },
          probability: {
            overall: 78,
            regulatory: 70,
            shareholder: 80,
            financing: 75,
            integration: 85
          },
          audit: {
            createdBy: ownerIdString,
            createdAt: new Date()
          },
          metadata: {
            source: 'seed',
            tags: ['joint-venture', 'high-value']
          },
          previousHash: null,
          forensicHash: crypto.createHash('sha256').update(JSON.stringify({
            dealId: `DEAL-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
            tenantId: tenantIdString,
            stage: DEAL_STAGES.PROPOSAL,
            value: 3500000
          })).digest('hex')
        }
      ];

      // Insert deals using insertMany to bypass pre-save middleware
      await Deal.insertMany(deals, { validateBeforeSave: false });

      const totalValue = deals.reduce((sum, d) => sum + d.value, 0);
      console.log(`✅ Pipeline Data Injected (R${totalValue.toLocaleString()} Total Value)`);
      console.log(`   Deals added: ${deals.length}`);
    }

    // 5. Verify the data
    const dealCount = await Deal.countDocuments({ tenantId: tenantIdString });
    console.log(`\n📊 Pipeline Summary:`);
    console.log(`   Total Deals: ${dealCount}`);

    console.log('\n🏆 SEED COMPLETE. The Citadel is perfectly synchronized.');
    console.log('📋 Next Steps:');
    console.log('   1. Clear browser localStorage (Application tab → Local Storage → Clear)');
    console.log('   2. Refresh and login as wilsywk@gmail.com');
    console.log('   3. Experience the Quantum CRM Dashboard with real pipeline data');

    process.exit(0);
  } catch (error) {
    console.error('❌ SEED FAILED:', error);
    console.error(error.stack);
    process.exit(1);
  }
}

seedCitadel();
