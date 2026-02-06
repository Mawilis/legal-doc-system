/**
 * File: server/scripts/genesis.js
 * STATUS: EPITOME | DATA SEEDING | V2 (FIXED SLUGS)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Populates the Wilsy OS Database with "Billion Dollar" demo data.
 * - FIX: Generates unique 'slugs' for tenants to prevent MongoDB E11000 errors.
 * -----------------------------------------------------------------------------
 */

require('dotenv').config();
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

// --- SCHEMAS (Simplified for Seeding) ---
// Note: We include 'slug' here to ensure we populate it correctly
const TenantSchema = new mongoose.Schema({
    name: String, 
    domain: String, 
    slug: { type: String, unique: true }, // <--- The Critical Field
    status: String, 
    plan: String, 
    billing: { mrr: Number, nextInvoice: Date },
    settings: { complianceScore: Number }
});
const Tenant = mongoose.models.Tenant || mongoose.model('Tenant', TenantSchema);

const UserSchema = new mongoose.Schema({
    name: String, email: String, password: String, role: String, 
    tenantId: mongoose.Schema.Types.ObjectId, status: String
});
const User = mongoose.models.User || mongoose.model('User', UserSchema);

const DocumentSchema = new mongoose.Schema({
    title: String, type: String, status: String, tenantId: mongoose.Schema.Types.ObjectId,
    createdAt: Date, metadata: Object
});
const Document = mongoose.models.Document || mongoose.model('Document', DocumentSchema);

// --- SEED DATA ---
const SEED_PASSWORD = 'BillionDollarCode!';

const connectDB = async () => {
    try {
        await mongoose.connect(process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/wilsy', { family: 4 });
        console.log('✅ Connected to MongoDB');
    } catch (err) {
        console.error('❌ DB Connection Failed:', err);
        process.exit(1);
    }
};

const seed = async () => {
    await connectDB();

    console.log('🌱 Starting Genesis Seeding...');

    // 1. CLEANUP: Remove any tenants with null slugs from previous failed runs
    const cleanup = await Tenant.deleteMany({ slug: null });
    if (cleanup.deletedCount > 0) {
        console.log(`🧹 Cleaned up ${cleanup.deletedCount} broken tenant records.`);
    }

    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(SEED_PASSWORD, salt);

    // --- TENANTS ---
    const tenants = [
        { name: 'Wilsy HQ', domain: 'wilsy.os', slug: 'wilsy-hq', plan: 'Enterprise', mrr: 0, compliance: 100 },
        { name: 'Smith & Associates', domain: 'smith.law', slug: 'smith-associates', plan: 'Professional', mrr: 15000, compliance: 98 },
        { name: 'Legal Eagles Inc', domain: 'legaleagles.co.za', slug: 'legal-eagles', plan: 'Starter', mrr: 2500, compliance: 85 },
        { name: 'Pretoria Public Defenders', domain: 'ppd.gov.za', slug: 'ppd', plan: 'Enterprise', mrr: 45000, compliance: 92 }
    ];

    let tenantDocs = [];

    for (const t of tenants) {
        let tenant = await Tenant.findOne({ domain: t.domain });
        if (!tenant) {
            try {
                tenant = await Tenant.create({
                    name: t.name,
                    domain: t.domain,
                    slug: t.slug, // Explicitly setting the slug
                    status: 'active',
                    plan: t.plan,
                    billing: { mrr: t.mrr, nextInvoice: new Date(Date.now() + 86400000 * 15) },
                    settings: { complianceScore: t.compliance }
                });
                console.log(`✅ Tenant Created: ${t.name}`);
            } catch (err) {
                console.error(`❌ Failed to create tenant ${t.name}:`, err.message);
            }
        } else {
            console.log(`ℹ️  Tenant Exists: ${t.name}`);
            // Ensure existing tenants have slugs (Migration on the fly)
            if (!tenant.slug) {
                tenant.slug = t.slug;
                await tenant.save();
                console.log(`   -> Fixed missing slug for ${t.name}`);
            }
        }
        if(tenant) tenantDocs.push(tenant);
    }

    // --- USERS ---
    const superAdminEmail = 'wilsonkhanyezi@gmail.com';
    let superAdmin = await User.findOne({ email: superAdminEmail });
    if (!superAdmin) {
        superAdmin = await User.create({
            name: 'Wilson Khanyezi',
            email: superAdminEmail,
            password: hashedPassword,
            role: 'SUPER_ADMIN',
            status: 'active',
            tenantId: tenantDocs[0]._id // HQ
        });
        console.log(`👑 Super Admin Created: ${superAdminEmail}`);
    } else {
        console.log(`ℹ️  Super Admin Exists: ${superAdminEmail}`);
        // Ensure SuperAdmin is linked to HQ
        if (!superAdmin.tenantId && tenantDocs[0]) {
            superAdmin.tenantId = tenantDocs[0]._id;
            await superAdmin.save();
        }
    }

    // Create Tenant Admins
    const userMap = [
        { name: 'John Smith', email: 'john@smith.law', role: 'TENANT_ADMIN', tenantIdx: 1 },
        { name: 'Sarah Eagle', email: 'sarah@legaleagles.co.za', role: 'TENANT_ADMIN', tenantIdx: 2 },
        { name: 'Advocate Zulu', email: 'zulu@ppd.gov.za', role: 'LAWYER', tenantIdx: 3 }
    ];

    for (const u of userMap) {
        if (!tenantDocs[u.tenantIdx]) continue; // Skip if tenant creation failed
        
        let user = await User.findOne({ email: u.email });
        if (!user) {
            await User.create({
                name: u.name,
                email: u.email,
                password: hashedPassword,
                role: u.role,
                status: 'active',
                tenantId: tenantDocs[u.tenantIdx]._id
            });
            console.log(`👤 User Created: ${u.email}`);
        }
    }

    // --- DOCUMENTS ---
    const docTypes = ['Summons', 'Court Order', 'Affidavit', 'Warrant'];
    const docStatuses = ['Draft', 'Pending Signature', 'Filed', 'Served'];
    
    const docCount = await Document.countDocuments();
    if (docCount < 50 && tenantDocs.length > 0) {
        console.log('📄 Seeding Documents...');
        const docs = [];
        for (let i = 0; i < 50; i++) {
            const randomTenant = tenantDocs[Math.floor(Math.random() * tenantDocs.length)];
            const randomType = docTypes[Math.floor(Math.random() * docTypes.length)];
            const randomStatus = docStatuses[Math.floor(Math.random() * docStatuses.length)];
            
            docs.push({
                title: `${randomType} - Case #${Math.floor(Math.random() * 10000)}`,
                type: randomType,
                status: randomStatus,
                tenantId: randomTenant._id,
                createdAt: new Date(Date.now() - Math.floor(Math.random() * 10000000000))
            });
        }
        await Document.insertMany(docs);
        console.log(`✅ 50 Documents Created`);
    } else {
        console.log(`ℹ️  Documents already seeded (${docCount})`);
    }

    console.log('===================================');
    console.log('🌌 GENESIS COMPLETE. UNIVERSE READY.');
    console.log('===================================');
    process.exit(0);
};

seed();
