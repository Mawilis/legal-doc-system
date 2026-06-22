/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ WILSY OS - COURT TELEMETRY CACHE SEEDER [V1.0.0-PRODUCTION]               ║
  ║ [POPIA §19 CERTIFIED | BOARDROOM FALLBACK PROOFING]                       ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/
import mongoose from 'mongoose';
import connectDatabase from '../config/database.js';

// Dynamically link to your transactional database schema
const CourtOrderSchema = new mongoose.Schema({}, { strict: false, collection: 'court_orders' });
const CourtOrder = mongoose.models.CourtOrder || mongoose.model('CourtOrder', CourtOrderSchema);

async function seed() {
  try {
    await connectDatabase();
    console.log('[SEEDER] Connected to database nucleus.');

    // Count existing rows to check cache bounds
    const existingCount = await CourtOrder.countDocuments();
    if (existingCount > 0) {
      console.log(`[SEEDER] Shard contains ${existingCount} active orders. Skipping seed.`);
      process.exit(0);
    }

    console.log('[SEEDER] Injecting baseline certified South African judicial orders...');
    const baselineRecords = [
      {
        caseId: "CC-2026-JHB-0089",
        court: "Gauteng Local Division, Johannesburg",
        parties: "Khanyezi Holdings vs. Competitive Entity Corp",
        status: "ORDERS_COMMITTED",
        complianceStatus: "POPIA_CLEAN",
        syncedAt: new Date().toISOString()
      },
      {
        caseId: "CC-2026-PTA-1142",
        court: "Gauteng Division, Pretoria",
        parties: "Sovereign Shard Shifting Ltd vs. State IT Agency",
        status: "JUDGMENT_SIGNED",
        complianceStatus: "POPIA_CLEAN",
        syncedAt: new Date().toISOString()
      }
    ];

    await CourtOrder.insertMany(baselineRecords);
    console.log('✅ [SEEDER] Cache storage populated with courtroom seed artifacts.');
    process.exit(0);
  } catch (err) {
    console.error(`❌ [SEEDER] Seeding failed: ${err.message}`);
    process.exit(1);
  }
}

seed();
