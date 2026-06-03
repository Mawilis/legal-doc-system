import mongoose from 'mongoose';
import Tenant from './models/tenantModel.js';
import dotenv from 'dotenv';

// Load environment variables for forensic alignment
dotenv.config();

async function probe() {
  const URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/wilsy-sovereign-root';

  try {
    console.log("📡 ATTEMPTING SECURE CONNECTION...");
    await mongoose.connect(URI);
    console.log("✅ AUTHENTICATED & CONNECTED TO: ", mongoose.connection.name);

    // Using find() instead of countDocuments to bypass aggregate if permissions are tight
    const root = await Tenant.findOne({ slug: 'wilsy' }).lean();

    if (root) {
      console.log("🏆 SOVEREIGN IDENTITY FOUND:");
      console.log(JSON.stringify(root, null, 2));
      console.log("\n✅ VERDICT: Ledger is healthy. Issue is in the Auth Middleware lookup.");
    } else {
      console.log("❌ VERDICT: Connected, but Ledger is EMPTY. Seeding failed or wrote to wrong DB.");
    }

    process.exit(0);
  } catch (err) {
    console.error("🚨 CRITICAL PROBE FAILURE:");
    console.error("ERROR_CODE:", err.code);
    console.error("MESSAGE:", err.message);
    process.exit(1);
  }
}

probe();
