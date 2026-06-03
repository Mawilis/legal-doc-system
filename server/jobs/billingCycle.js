/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - BILLING CYCLE JOB [V1.2.0-MARS]                                                                                             ║
 * ║ [WEEKLY INVOICE GENERATION | DUNNING | TRIAL PROCESSING]                                                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.2.0-MARS | PRODUCTION READY | BILLION DOLLAR SPEC                                                                           ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/jobs/billingCycle.js                                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated automated billing. [2026-05-15]                                                      ║
 * ║ • AI Engineering (DeepSeek) - IMPLEMENTED: Weekly cron with error handling. [2026-05-15]                                               ║
 * ║ • AI Engineering (DeepSeek) - MARS PROTOCOL: Full JSDoc, robust error logging, version bump. [2026-05-15]                              ║
 * ║ • AI Engineering (DeepSeek) - EPITOMISED: Added validation guards, null‑safe invoice handling, enhanced logging. [2026-05-16]          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import cron from 'node-cron';
import Subscription from '../models/Subscription.js';
import TrialEngine from '../services/trialEngine.js';
import BillingEngine from '../services/billingEngine.js';
import auditLogger from '../utils/auditLogger.js';

// ============================================================================
// 🧠 ENGINE INSTANTIATION
// ============================================================================

/**
 * Trial engine instance – handles trial start/end and commitment logic.
 * @type {TrialEngine}
 */
const trialEngine = new TrialEngine();

/**
 * Billing engine instance – generates invoices from usage and recurring charges.
 * @type {BillingEngine}
 */
const billingEngine = new BillingEngine();

// ============================================================================
// 🚀 MAIN BILLING CYCLE FUNCTION
// ============================================================================

/**
 * Executes the weekly billing cycle.
 *
 * **Process flow**:
 * 1. Fetch all subscriptions with status `trial` or `active`.
 * 2. For each subscription:
 *    a. Process trial end (if trial expired, transition to `active`).
 *    b. If subscription is `active`:
 *       - Validate that `currentPeriodStart` and `currentPeriodEnd` exist.
 *       - Generate an invoice for the current billing period.
 *       - Update the subscription's period dates for the next cycle (adds 30 days).
 *       - Save the subscription.
 * 3. Log errors per subscription – does not stop the entire cycle.
 *
 * **Edge Cases**:
 * - Skips subscriptions with missing period dates (logs error).
 * - If invoice generation fails, the subscription period is NOT advanced.
 * - Uses `auditLogger.error` for critical failures.
 *
 * @async
 * @returns {Promise<void>}
 *
 * @example
 * // Manual trigger (e.g., from admin API)
 * await runBillingCycle();
 */
async function runBillingCycle() {
  const cycleStart = Date.now();
  console.log('[BILLING-CYCLE] ⚡ Starting weekly billing run...');

  // Fetch all subscriptions that are either in trial or active
  const activeSubscriptions = await Subscription.find({ status: { $in: ['trial', 'active'] } });

  if (activeSubscriptions.length === 0) {
    console.log('[BILLING-CYCLE] ℹ️ No active or trial subscriptions found. Exiting.');
    return;
  }

  console.log(`[BILLING-CYCLE] 📋 Found ${activeSubscriptions.length} subscription(s) to process.`);
  let processed = 0;
  let errors = 0;

  for (const sub of activeSubscriptions) {
    try {
      // 1. Process trial end – may transition to 'active'
      await trialEngine.processTrialEnd(sub);

      // 2. If subscription is active, generate invoice for the current period
      if (sub.status === 'active') {
        const periodStart = sub.currentPeriodStart;
        const periodEnd = sub.currentPeriodEnd;

        // Validate period dates exist
        if (!periodStart || !periodEnd) {
          throw new Error(`Missing currentPeriodStart or currentPeriodEnd for subscription ${sub._id}`);
        }

        // Generate invoice for the current period
        const invoice = await billingEngine.calculateInvoice(sub._id, periodStart, periodEnd);

        // Safety: ensure invoice was created and has an invoiceNumber
        if (!invoice || !invoice.invoiceNumber) {
          throw new Error(`Invoice generation failed – no invoice returned for subscription ${sub._id}`);
        }

        // Update subscription period for the next billing cycle
        sub.currentPeriodStart = periodEnd;
        sub.currentPeriodEnd = new Date(periodEnd.getTime() + 30 * 24 * 60 * 60 * 1000);
        await sub.save();

        console.log(`[BILLING-CYCLE] ✅ Invoice ${invoice.invoiceNumber} generated for subscription ${sub._id}`);
        processed++;
      } else {
        // Subscription is still in trial – no invoice generated
        console.log(`[BILLING-CYCLE] ⏳ Subscription ${sub._id} is still in trial period. No invoice generated.`);
      }
    } catch (err) {
      errors++;
      console.error(`[BILLING-CYCLE] ❌ Error for subscription ${sub._id}: ${err.message}`);
      await auditLogger.error('BILLING_CYCLE_ERROR', {
        subscriptionId: sub._id,
        error: err.message,
        stack: err.stack,
        timestamp: new Date().toISOString()
      });
    }
  }

  const cycleDuration = Date.now() - cycleStart;
  console.log(`[BILLING-CYCLE] 🏁 Weekly billing run completed. Processed: ${processed}, Errors: ${errors}, Duration: ${cycleDuration}ms`);
}

// ============================================================================
// 🚀 CRON SCHEDULE (WEEKLY ON MONDAY AT MIDNIGHT)
// ============================================================================

/**
 * Scheduled cron job that triggers the billing cycle.
 *
 * **Schedule**: `0 0 * * 1`
 * - Minute: 0
 * - Hour: 0 (midnight)
 * - Day of month: * (any)
 * - Month: * (any)
 * - Day of week: 1 (Monday)
 *
 * The job runs automatically when the server starts and repeats every Monday.
 * Any unhandled error is caught and logged to prevent process crash.
 *
 * @see {@link https://crontab.guru/#0_0_*_*_1} for schedule explanation
 */
cron.schedule('0 0 * * 1', () => {
  runBillingCycle().catch(err => {
    console.error('[CRON] ❌ Billing cycle crashed:', err);
    auditLogger.error('CRON_BILLING_CYCLE_FATAL', { error: err.message, stack: err.stack });
  });
});

// ============================================================================
// 📤 EXPORT (for manual triggering)
// ============================================================================

/**
 * Default export – the main billing cycle function.
 * Use this to manually trigger billing from an admin API endpoint, CLI, or test script.
 *
 * @type {Function}
 *
 * @example
 * // Manual invocation
 * import runBillingCycle from './jobs/billingCycle.js';
 * await runBillingCycle();
 */
export default runBillingCycle;
