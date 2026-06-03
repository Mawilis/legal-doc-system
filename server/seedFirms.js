/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ 🚀 BILLION-DOLLAR SEEDING PROTOCOL - WILSY OS                             ║
 * ║ Simulating a High-Velocity Legal Market Injection                         ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */
import mongoose from 'mongoose';
import Tenant from './models/Tenant.js';
import User from './models/User.js';

const seed = async () => {
  try {
    await mongoose.connect('mongodb://127.0.0.1:27017/wilsy_os_dev');
    console.log('✅ Connected to Wilsy OS Persistence Layer...');

    const plans = ['basic', 'professional', 'enterprise'];
    const firms = [];

    for (let i = 1; i <= 50; i++) {
      const plan = plans[i % 3];
      const mrr = plan === 'enterprise' ? 7999 : plan === 'professional' ? 2499 : 799;

      firms.push({
        name: `Sovereign Law Group ${i}`,
        slug: `sovereign-law-${i}`,
        subscription: plan,
        status: 'active',
        billing: {
          monthlyRevenue: mrr,
          currency: 'ZAR'
        }
      });
    }

    await Tenant.insertMany(firms);
    console.log(`🚀 50 Sovereign Law Firms successfully deployed into the matrix.`);

    // Check global metrics
    const stats = await Tenant.aggregate([
      { $group: { _id: null, totalMRR: { $sum: '$billing.monthlyRevenue' }, totalValuation: { $sum: '$investorMetrics.estimatedValuation' } } }
    ]);

    console.log('--- MARKET VALUATION REPORT ---');
    console.log(`Global MRR: R${stats[0].totalMRR.toLocaleString()}`);
    console.log(`System Valuation: R${stats[0].totalValuation.toLocaleString()}`);
    console.log('-------------------------------');

    process.exit(0);
  } catch (err) {
    console.error(err);
    process.exit(1);
  }
};

seed();
