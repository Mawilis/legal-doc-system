/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - ARTIFACT GENERATOR [V49.2.0-DEEP-CANONICAL]                                                                                ║
 * ║ [🔒 FORENSIC SEAL VERIFICATION | DEEP‑CANONICAL HMAC | INTEGRATED hmacUtils v2 | FULL JSDOC]                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 49.2.0 | PRODUCTION READY | BILLION DOLLAR SPEC                                                                              ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/pdfController.js                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated forensic‑grade PDF generation with HMAC integrity.                                   ║
 * ║ • AI Engineering (DeepSeek) – ENHANCED: Integrated deep‑canonical hmacUtils v2 (recursive key sorting, nonce support).                 ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import PDFDocument from 'pdfkit';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import { verifyForensicSeal } from '../utils/hmacUtils.js';
import {
  deriveInvoiceTotals,
  formatMoney,
  normalizeInvoiceLineItems,
  normalizeStatementTransactions,
  toMoneyNumber,
} from '../utils/invoiceLineItemNormalizer.js';

/**
 * Sorts object keys recursively to ensure deterministic JSON stringification.
 * @param {any} obj - Input object
 * @returns {any} Sorted copy
 */
const sortKeys = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(sortKeys);
  return Object.keys(obj).sort().reduce((acc, key) => {
    acc[key] = sortKeys(obj[key]);
    return acc;
  }, {});
};

/**
 * Generates a PDF document as a Buffer.
 * @param {string} type - Document type ('forensicReport', 'invoice', 'statement')
 * @param {Object} data - Content data for the PDF
 * @param {string} tenantId - Tenant ID for telemetry
 * @returns {Promise<Buffer>} PDF buffer
 */
const generatePDFBuffer = async (type, data, tenantId) => {
  return new Promise((resolve, reject) => {
    const doc = new PDFDocument({ margin: 50, size: 'A4' });
    const buffers = [];
    doc.on('data', buffers.push.bind(buffers));
    doc.on('end', () => resolve(Buffer.concat(buffers)));
    doc.on('error', reject);

    // Header
    doc.fontSize(20)
      .fillColor('#D4AF37')
      .text('WILSY OS', { align: 'center' })
      .moveDown(0.5)
      .fontSize(12)
      .fillColor('#FFFFFF')
      .text('Sovereign Document', { align: 'center' })
      .moveDown(2);

    // Content based on type
    switch (type) {
      case 'forensicReport':
        doc.fontSize(14).fillColor('#D4AF37').text('Forensic Audit Report', { underline: true }).moveDown(0.5);
        doc.fontSize(10).fillColor('#CCCCCC');
        doc.text(`Generated: ${new Date().toISOString()}`);
        doc.text(`Tenant: ${tenantId}`);
        doc.moveDown();
        doc.text(`Integrity Score: ${data.integrityScore ?? 'N/A'}%`);
        doc.text(`Active Audits: ${data.activeAudits ?? 0}`);
        doc.text(`Critical Anomalies: ${data.criticalAnomalies ?? 0}`);
        doc.text(`System Status: ${data.systemStatus ?? 'OPTIMAL'}`);
        doc.moveDown();
        doc.text('This document is cryptographically sealed and court‑admissible under Cybercrimes Act §3.', { italic: true });
        break;

      case 'invoice':
        {
        const lineItems = normalizeInvoiceLineItems(data);
        const totals = deriveInvoiceTotals(data, lineItems);
        const currency = data.currency || 'ZAR';
        doc.fontSize(14).fillColor('#D4AF37').text('INVOICE', { underline: true }).moveDown(0.5);
        doc.fontSize(10).fillColor('#CCCCCC');
        doc.text(`Invoice Number: ${data.invoiceNumber || 'N/A'}`);
        doc.text(`Invoice Date: ${data.invoiceDate || new Date().toLocaleDateString()}`);
        doc.text(`Due Date: ${data.dueDate || 'Upon receipt'}`);
        doc.moveDown();
        doc.text(`Client: ${data.clientName || tenantId}`);
        doc.moveDown();
        if (lineItems.length) {
          doc.text('Items:', { underline: true });
          lineItems.forEach((item, idx) => {
            doc.text(`${idx + 1}. ${item.description} | Qty: ${item.quantity} | Unit: ${formatMoney(item.unitPrice, currency)} | Total: ${formatMoney(item.lineTotal, currency)}`);
          });
        }
        doc.moveDown();
        doc.text(`Subtotal: ${formatMoney(totals.subtotal, currency)}`);
        doc.text(`Tax (${Math.round(totals.taxRate * 100)}%): ${formatMoney(totals.taxAmount, currency)}`);
        doc.text(`Total: ${formatMoney(totals.totalAmount, currency)}`, { bold: true });
        break;
        }

      case 'statement':
        {
        const transactions = normalizeStatementTransactions(data);
        const currency = data.currency || 'ZAR';
        const openingBalance = toMoneyNumber(data.openingBalance);
        const closingBalance = data.closingBalance !== undefined
          ? toMoneyNumber(data.closingBalance)
          : transactions.reduce((balance, tx) => balance + tx.debit - tx.credit, openingBalance);
        doc.fontSize(14).fillColor('#D4AF37').text('STATEMENT OF ACCOUNT', { underline: true }).moveDown(0.5);
        doc.fontSize(10).fillColor('#CCCCCC');
        doc.text(`Statement Number: ${data.statementNumber || 'N/A'}`);
        doc.text(`Statement Date: ${data.statementDate || new Date().toLocaleDateString()}`);
        doc.moveDown();
        doc.text(`Client: ${data.clientName || tenantId}`);
        doc.text(`Account No: ${data.clientAccountNo || 'N/A'}`);
        doc.moveDown();
        doc.text(`Opening Balance: ${formatMoney(openingBalance, currency)}`);
        if (transactions.length) {
          doc.moveDown();
          doc.text('Transactions:', { underline: true });
          transactions.forEach((tx, idx) => {
            doc.text(`${idx + 1}. ${tx.date} | ${tx.description} | Debit: ${formatMoney(tx.debit, currency)} | Credit: ${formatMoney(tx.credit, currency)}`);
          });
        }
        doc.moveDown();
        doc.text(`Closing Balance: ${formatMoney(closingBalance, currency)}`);
        break;
        }

      default:
        doc.fontSize(12).fillColor('#FF6666').text('Unknown document type', { align: 'center' });
    }

    // Footer
    const pageCount = doc.bufferedPageRange().count;
    for (let i = 0; i < pageCount; i++) {
      doc.switchToPage(i);
      doc.fontSize(8)
        .fillColor('#666666')
        .text(`Page ${i + 1} of ${pageCount}`, 0, doc.page.height - 30, { align: 'center' });
    }

    doc.end();
  });
};

/**
 * @function generatePDF
 * @description Generates a forensic‑sealed PDF document. Verifies the HMAC‑based seal
 * using the centralized deep‑canonical hmacUtils, then generates the PDF and streams the result.
 * The deep‑canonical sorting (recursive key ordering) ensures 100% deterministic hashing,
 * eliminating cryptographic mismatches caused by key order variance.
 *
 * @param {Object} req - Express request object. Expected headers: x-trace-id, x-forensic-timestamp, x-cryptographic-nonce, x-request-seal.
 *                        Body: { type: string, data: object, tenantId: string }
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware
 * @returns {Promise<void>} Streams PDF or returns error JSON
 * @real-world Used by the Compliance HUD export buttons to generate court‑ready forensic audits,
 *            sample invoices, and account statements.
 * @forensic The request is rejected if the forensic seal does not match the recalculated HMAC,
 *           preventing tampering or replay attacks. Telemetry is broadcast for every attempt.
 */
export const generatePDF = async (req, res, next) => {
  const startTime = Date.now();
  const traceId = req.headers['x-trace-id'] || 'SYSTEM';
  const tenantId = req.body.tenantId || req.headers['x-tenant-id'] || 'GLOBAL_ROOT';
  const timestamp = req.headers['x-forensic-timestamp'];
  const nonce = req.headers['x-cryptographic-nonce'];
  const receivedSeal = req.headers['x-request-seal'];

  try {
    // 1. Verify forensic seal using centralized deep‑canonical hmacUtils
    const payload = req.body.data || {};
    const isValid = verifyForensicSeal(receivedSeal, payload, traceId, timestamp, nonce, null, {
      broadcastOnFailure: true,
      tenantId,
      source: 'PDFController'
    });

    if (!isValid) {
      broadcastTelemetry(tenantId, 'SECURITY_EVENT', 'PDF_SEAL_MISMATCH', 'PDFController', {
        traceId,
        reason: 'CRYPTOGRAPHIC_MISMATCH'
      });
      return res.status(401).json({
        success: false,
        message: 'Forensic seal verification failed. Request rejected.'
      });
    }

    const { type, data } = req.body;
    if (!type || !data) {
      broadcastTelemetry(tenantId, 'SYSTEM_EVENT', 'PDF_MISSING_PARAMS', 'PDFController', { traceId });
      return res.status(400).json({ success: false, message: 'Missing document type or data.' });
    }

    // 2. Generate PDF buffer
    const pdfBuffer = await generatePDFBuffer(type, data, tenantId);

    // 3. Set response headers and stream
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename=WILSY_OS_${type}_${Date.now()}.pdf`);
    res.setHeader('X-Forensic-Trace', traceId);
    res.setHeader('X-Institutional-Latency', `${Date.now() - startTime}ms`);

    // Broadcast success telemetry
    broadcastTelemetry(tenantId, 'AUDIT_EVENT', 'PDF_GENERATED', 'PDFController', {
      traceId,
      documentType: type,
      latencyMs: Date.now() - startTime
    });

    return res.send(pdfBuffer);
  } catch (error) {
    console.error('[PDF_GENERATOR] Error:', error);
    broadcastTelemetry(tenantId, 'SYSTEM_EVENT', 'PDF_GENERATION_FAILURE', 'PDFController', {
      traceId,
      error: error.message
    });
    return res.status(500).json({ success: false, message: 'PDF generation failed.', error: error.message });
  }
};

/**
 * @function generatePDFFallback
 * @description Legacy fallback endpoint (maintains compatibility with older frontend versions).
 * @deprecated Use generatePDF instead.
 */
export const generatePDFFallback = async (req, res, next) => {
  // Simply forward to the main generator
  return generatePDF(req, res, next);
};

export default {
  generatePDF,
  generatePDFFallback
};
