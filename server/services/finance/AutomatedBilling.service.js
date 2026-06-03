/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - AUTOMATED SOVEREIGN BILLING WORKER [V2.0.0-OMEGA]                                                                           ║
 * ║ [LEDGER GENERATION | DYNAMIC PRICING INTEGRATION | FORENSIC AUDIT ANCHORING]                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.0.0-OMEGA | PRODUCTION READY | BILLION DOLLAR SPEC                                                                          ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/finance/AutomatedBilling.service.js                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated the upgrade to support dynamic pricing and database insertions.                      ║
 * ║ • AI Engineering (Gemini) - EPITOMISED: Fortified with full JSDoc, Mongoose context bindings, and structural error handling.           ║
 * ║ • AI Engineering (DeepSeek) - ENHANCED: Added defensive fallback logic, enriched forensic comments, and normalized error handling.     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';
import ForensicService from '../forensic/ForensicService.js';
import RevenueForecaster from '../analytics/RevenueForecaster.service.js';
import Invoice from '../../models/Invoice.js';

export class AutomatedBillingService {
  /**
   * Generates a forensic-grade sovereign invoice for a target node and anchors it into the database.
   *
   * @param {string} targetTenantId - The unique identifier of the tenant receiving the invoice.
   * @param {Object} tenantData - Telemetry and configuration data for the tenant.
   * @param {number} [dynamicPriceOverride] - Optional price override from the pricing engine.
   * @returns {Promise<Object>} The fully anchored invoice document with forensic signature.
   */
  static async generateInvoice(targetTenantId, tenantData, dynamicPriceOverride = null) {
    console.log(`[FINANCE-WORKER] 💳 Initiating Sovereign Invoice generation for Node: ${targetTenantId}`);

    try {
      // ======================================================================
      // 1. DYNAMIC VALUATION & PRICE DISCOVERY
      // ======================================================================
      let amountDue = dynamicPriceOverride;
      let valuationRef = 'MANUAL_STRIKE';

      // When no boardroom override exists, delegate to the AI Revenue Forecaster
      if (amountDue === null || amountDue === undefined) {
        try {
          const valuation = await RevenueForecaster.calculateNodeValuation(tenantData);
          // Standard 10% platform resource allocation fee (configurable via Pricing Engine)
          amountDue = valuation.projectedValue * 0.10;
          valuationRef = valuation.forensicSignature?.substring(0, 16) || 'DYNAMIC_ALLOC';
        } catch (forecastError) {
          console.error(`[FINANCE-WORKER] Revenue forecast failed for ${targetTenantId}: ${forecastError.message}`);
          // Fallback to a baseline charge to prevent billing pipeline collapse
          amountDue = 1000; // ZAR 1,000 – absolute floor for platform continuity
          valuationRef = 'FORECAST_FALLBACK';
        }
      }

      // ======================================================================
      // 2. INVOICE IDENTITY & CORE MANIFEST
      // ======================================================================
      const invoiceId = `INV-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;

      const invoiceManifest = {
        id: invoiceId, // Logical reference – visible in dashboards
        traceId: invoiceId,
        tenantId: 'WILSY_ROOT',
        recipientTenantId: targetTenantId,
        amount: Number(amountDue.toFixed(2)),
        totalAmount: Number(amountDue.toFixed(2)),
        currency: 'ZAR',
        type: 'MONTHLY_PLATFORM_FEE',
        timestamp: new Date().toISOString(),
        dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // T+30 standard net settlement
        valuationRef,
        status: 'ISSUED',
        lineItems: [
          { description: 'Sovereign Core Infrastructure Allocation', price: Number(amountDue.toFixed(2)) }
        ]
      };

      // ======================================================================
      // 3. FORENSIC CRYPTOGRAPHIC SEAL
      // ======================================================================
      const billingSignature = ForensicService.signTransaction(invoiceManifest);
      invoiceManifest.billingSignature = billingSignature;

      // ======================================================================
      // 4. ANCHOR TO THE MASTER ROOT LEDGER (MONGOOSE)
      // ======================================================================
      const sovereignDb = mongoose.connection.useDb('wilsy-sovereign-root', { useCache: true });
      const SovereignInvoice = sovereignDb.models.Invoice || sovereignDb.model('Invoice', Invoice.schema);

      const anchoredRecord = await SovereignInvoice.create({
        ...invoiceManifest,
        date: invoiceManifest.timestamp, // Map to legacy schema field
      });

      console.log(`[FINANCE-WORKER] ✅ Sovereign Invoice ${invoiceId} anchored with signature: ${billingSignature.substring(0, 12)}...`);

      return anchoredRecord;

    } catch (error) {
      console.error(`[FINANCE-WORKER-FRACTURE] Invoice generation failed for ${targetTenantId}: ${error.message}`);
      throw error; // Re-throw to allow upstream controller to return proper 500
    }
  }
}

export default AutomatedBillingService;
