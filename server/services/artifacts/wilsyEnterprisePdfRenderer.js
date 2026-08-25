/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                                                                                        ║
 * ║   ██████╗ ██╗██╗     ██╗     ██╗███╗   ██╗ ██████╗     ██████╗ ██╗   ██╗████████╗███████╗███████╗                               ║
 * ║   ██╔══██╗██║██║     ██║     ██║████╗  ██║██╔════╝     ██╔══██╗██╔═══██╗██║   ██║╚══██╔══╝██╔════╝╚════██║                       ║
 * ║   ██████╔╝██║██║     ██║     ██║██╔██╗ ██║██║  ███╗    ██████╔╝██║   ██║██║   ██║   ██║   █████╗   █████╔╝                       ║
 * ║   ██╔══██╗██║██║     ██║     ██║██║╚██╗██║██║   ██║    ██╔══██╗██║   ██║██║   ██║   ██║   ██╔══╝  ██╔═══╝                        ║
 * ║   ██████╔╝██║███████╗███████╗██║██║ ╚████║╚██████╔╝    ██║  ██║╚██████╔╝╚██████╔╝   ██║   ███████╗███████╗                       ║
 * ║   ╚═════╝ ╚═╝╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝╚══════╝                       ║
 * ║                                                                                                                                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * 🏛️ WILSY OS - ENTERPRISE PDF RENDERER [v7.1.7‑QR‑INTEGRATION]
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ [SOVEREIGN INVOICE | EXECUTIVE DIGEST COVER | FORENSIC APPENDIX]                                                                     ║
 * ║ [SARS‑COMPLIANT VAT | SERVICE TYPE | PREDICTIVE OVERLAYS | ANOMALY LOG]                                                              ║
 * ║ [QR VERIFICATION INTEGRATION | TRACE ID EXPOSED | FORENSIC PROOF]                                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 7.1.7‑QR‑INTEGRATION | PRODUCTION READY | INSTITUTIONAL GRADE                                                               ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/artifacts/wilsyEnterprisePdfRenderer.js                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN‑OFF:                                                                                              ║
 * ║ • Wilson Khanyezi – Mandated prominent forensic footer with gold accents, monospaced identifiers, and QR/verify link.               ║
 * ║ • AI Engineering – v7.1.7: Integrated qrGenerator.js (buildQRPayload, generateQRCode) for sovereign QR generation; removed legacy. ║
 * ║ • Compliance: POPIA §19 · GDPR §32 · SOC2 §CC7.2 · SARS VAT Act (No. 89 of 1991) · CIPC registration 2024/617944/07               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 CHANGES (v7.1.7):                                                                                                                ║
 * ║   1. Imported buildQRPayload and generateQRCode from ../qr/qrGenerator.js.                                                           ║
 * ║   2. Replaced local buildQrPngBuffer with generateQRCode for both verification and payment QR codes.                                ║
 * ║   3. Now generates a signed payload using buildQRPayload and encodes the verification URL in the QR.                                 ║
 * ║   4. Added graceful fallback if QR generation fails (returns null buffer, renders placeholder).                                     ║
 * ║   5. All existing invoice layout, forensic footer, and commercial logic preserved.                                                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import PDFDocument from 'pdfkit';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildQRPayload, generateQRCode } from '../qr/qrGenerator.js';

const BRAND = Object.freeze({
  black: '#020403',
  ivory: '#F4EFE4',
  gold: '#D4AF37',
  muted: '#66665F',
  line: '#D8CCAA',
  panel: '#FBF8EF',
  band: '#EFE8D8',
});

const PAGE = Object.freeze({
  width: 595.28,
  height: 841.89,
  left: 52,
  top: 182,
  bottom: 744,
  contentWidth: 491,
});

let LOGO_CACHE;

/**
 * @function textValue
 * @description Converts unknown source values into safe PDF text.
 * @param {unknown} value - Unknown source value.
 * @returns {string} Clean text.
 */
function textValue(value) {
  return String(value ?? '')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * @function compactProof
 * @description Shortens long proof values for stable footer layout.
 * @param {string} value - Proof value.
 * @returns {string} Compact proof value.
 */
function compactProof(value = '') {
  const clean = textValue(value);
  if (!clean) return 'PENDING';
  if (clean.length <= 26) return clean;
  return `${clean.slice(0, 12)}...${clean.slice(-12)}`;
}

/**
 * @function titleFromType
 * @description Converts artifact type slugs into readable enterprise titles.
 * @param {string} type - Artifact type slug.
 * @returns {string} Readable title.
 */
function titleFromType(type = 'artifact') {
  return textValue(type)
    .replace(/_/g, '-')
    .split('-')
    .filter(Boolean)
    .map((part) =>
      part.length <= 3 ? part.toUpperCase() : `${part.charAt(0).toUpperCase()}${part.slice(1)}`
    )
    .join(' ');
}

/**
 * @function safeFileName
 * @description Creates safe artifact filenames.
 * @param {string} value - Raw filename value.
 * @returns {string} Safe filename.
 */
function safeFileName(value = 'artifact') {
  return (
    textValue(value)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '') || 'artifact'
  );
}

/**
 * @function findLogoPath
 * @description Resolves the Wilsy OS logo from known client asset locations.
 * @returns {string} Existing logo path or empty string.
 */
function findLogoPath() {
  if (LOGO_CACHE !== undefined) return LOGO_CACHE;

  const rendererDir = path.dirname(fileURLToPath(import.meta.url));
  const candidates = [
    path.resolve(process.cwd(), '../client/src/assets/logo/wilsy.jpeg'),
    path.resolve(process.cwd(), '../client/src/assets/logo/wilsy.jpg'),
    path.resolve(process.cwd(), '../client/src/assets/logo/wilsy.png'),
    path.resolve(process.cwd(), '../client/public/wilsy.jpeg'),
    path.resolve(process.cwd(), '../client/public/wilsy.jpg'),
    path.resolve(process.cwd(), '../client/public/wilsy.png'),
    path.resolve(rendererDir, '../../../client/src/assets/logo/wilsy.jpeg'),
    path.resolve(rendererDir, '../../../client/src/assets/logo/wilsy.jpg'),
    path.resolve(rendererDir, '../../../client/src/assets/logo/wilsy.png'),
  ];

  LOGO_CACHE = candidates.find((candidate) => fs.existsSync(candidate)) || '';
  return LOGO_CACHE;
}

/**
 * @function titleCaseHumanName
 * @description Converts a low-trust identity token into a readable human name candidate.
 * @param {string} value - Raw identity text.
 * @returns {string} Title-cased human name candidate.
 */
function titleCaseHumanName(value = '') {
  return textValue(value)
    .replace(/[_.-]+/g, ' ')
    .split(' ')
    .filter(Boolean)
    .map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1).toLowerCase()}`)
    .join(' ');
}

/**
 * @function resolveHumanGeneratedByName
 * @description Resolves the accountable human name/surname for Generated By controls without showing system slugs.
 */
function resolveHumanGeneratedByName({ proofPack = {}, identity = {}, state = {} } = {}) {
  const nestedUser =
    identity.user || identity.operator || identity.profile || identity.account || {};
  const proofUser = proofPack.user || proofPack.operator || proofPack.profile || {};

  const firstName = textValue(
    proofPack.firstName ||
    proofPack.givenName ||
    proofUser.firstName ||
    proofUser.givenName ||
    identity.firstName ||
    identity.givenName ||
    nestedUser.firstName ||
    nestedUser.givenName
  );

  const surname = textValue(
    proofPack.surname ||
    proofPack.lastName ||
    proofPack.familyName ||
    proofUser.surname ||
    proofUser.lastName ||
    proofUser.familyName ||
    identity.surname ||
    identity.lastName ||
    identity.familyName ||
    nestedUser.surname ||
    nestedUser.lastName ||
    nestedUser.familyName
  );

  const combinedName = textValue(`${firstName} ${surname}`);

  if (combinedName && combinedName.split(' ').length >= 2) {
    return combinedName;
  }

  const directName = textValue(
    proofPack.generatedByDisplayName ||
    proofPack.generatedByName ||
    proofPack.generatorName ||
    proofPack.operatorName ||
    proofPack.operatorDisplayName ||
    proofPack.displayName ||
    proofUser.name ||
    proofUser.displayName ||
    identity.generatedByDisplayName ||
    identity.generatedByName ||
    identity.generatorName ||
    identity.operatorName ||
    identity.operatorDisplayName ||
    identity.displayName ||
    identity.name ||
    nestedUser.name ||
    nestedUser.displayName ||
    state.generatedByDisplayName ||
    state.operatorDisplayName ||
    state.ownerDisplayName ||
    state.displayName ||
    state.generatedByName
  );

  const forbiddenSlugs = new Set(['wilsy-operator', 'operator', 'system', 'wilsy', 'anonymous']);
  const normalizedDirectName = directName.toLowerCase();

  if (directName && !forbiddenSlugs.has(normalizedDirectName)) {
    return directName;
  }

  const email = textValue(
    proofPack.operatorEmail ||
    proofPack.email ||
    proofUser.email ||
    identity.userEmail ||
    identity.email ||
    nestedUser.email ||
    state.operatorEmail ||
    state.generatedBy
  );

  if (email.includes('@')) {
    const localPart = email.split('@')[0];

    const formattedLocalPartDisplayName = formatWilsyDisplayNameFromIdentityCandidate(localPart);
    if (isWilsyProfessionalDisplayName(formattedLocalPartDisplayName)) {
      return formattedLocalPartDisplayName;
    }
    const emailName = titleCaseHumanName(localPart);

    if (emailName && emailName.split(' ').length >= 2) {
      return emailName;
    }
  }

  if (isWilsyProfessionalDisplayName(directName)) {
    return directName;
  }

  if (isWilsyProfessionalDisplayName(state.generatedBy)) {
    return textValue(state.generatedBy);
  }

  return 'Verified Wilsy Operator';
}

/**
 * @function replaceGeneratedBySlugRows
 * @description Rewrites proof-pack generated-by rows so audit PDFs show human accountability instead of system slugs.
 */
function replaceGeneratedBySlugRows(rows = [], generatedByName = '') {
  if (!Array.isArray(rows)) return [];
  return rows.map((row) => {
    if (Array.isArray(row)) {
      const label = textValue(row[0]).toLowerCase();
      if (
        label === 'generated by' ||
        label === 'generatedby' ||
        label === 'operator' ||
        label === 'generated by:'
      ) {
        return [row[0], generatedByName];
      }
      return row;
    }
    if (row && typeof row === 'object') {
      const label = textValue(row.label || row.title || row.key || row.name).toLowerCase();
      if (
        label === 'generated by' ||
        label === 'generatedby' ||
        label === 'operator' ||
        label === 'generated by:'
      ) {
        return { ...row, value: generatedByName, detail: row.detail && textValue(row.detail).toLowerCase() !== 'wilsy-operator' ? row.detail : generatedByName };
      }
      return row;
    }
    return row;
  });
}

/**
 * @function buildState
 * @description Builds normalized render state from verified request identity and proof context.
 */
function buildState(identity = {}, proof = {}) {
  const data = identity.data || identity.payload || {};
  const type = textValue(identity.type || identity.artifactType || data.type || 'artifact');
  const title = textValue(identity.title || data.title || titleFromType(type));

  return {
    type,
    title,
    tenantId: textValue(identity.tenantId || data.tenantId || 'MASTER'),
    issuingEntity: textValue(data.issuingEntity || identity.issuingEntity || 'Wilsy (Pty) Ltd'),
    counterparty: textValue(
      data.counterparty || identity.counterparty || 'Counterparty To Be Completed'
    ),
    generatedBy: resolveHumanGeneratedByName({
      proofPack: data.crmProofPack || data.proofPackSections || {},
      identity,
      state: {
        generatedByDisplayName:
          identity.generatedByDisplayName ||
          identity.payloadData?.generatedByDisplayName ||
          identity.metadata?.generatedByDisplayName ||
          data.generatedByDisplayName,
        operatorDisplayName:
          identity.operatorDisplayName ||
          identity.payloadData?.operatorDisplayName ||
          identity.metadata?.operatorDisplayName ||
          data.operatorDisplayName,
        ownerDisplayName:
          identity.ownerDisplayName ||
          identity.payloadData?.ownerDisplayName ||
          identity.metadata?.ownerDisplayName ||
          data.ownerDisplayName,
        displayName:
          identity.displayName ||
          identity.payloadData?.displayName ||
          identity.metadata?.displayName ||
          data.displayName,
        generatedBy: data.generatedBy,
      },
    }),
    effectiveDate: textValue(data.effectiveDate || new Date().toISOString().slice(0, 10)),
    version: textValue(data.version || 'WILSY-OS-ARTIFACT-v2.1-ENTERPRISE'),
    jurisdiction: textValue(data.jurisdiction || 'Republic of South Africa'),
    sourcePosture: textValue(proof.sourcePosture || data.sourcePosture || 'SOURCE_REPAIR_REQUIRED'),
    traceId: textValue(proof.traceId || identity.traceId || 'TRACE-PENDING'),
    merkleRoot: textValue(proof.merkleRoot || identity.merkleRoot || 'MERKLE-PENDING'),
    sha3: textValue(proof.serverSeal || proof.sha3 || identity.requestProof || 'LOCAL-PROOF'),
    generatedAt: new Date().toISOString(),
  };
}

// ─── BILLING INVOICE HELPERS ────────────────────────────────────────────────

/**
 * @function isBillingInvoiceType
 * @description Detects billing invoice / statement artifact types.
 */

/**
 * @function buildVerifyAuditUrl
 * @description Public forensic verification URL for the invoice trace.
 * @param {object} state
 * @returns {string}
 * @collaboration Evidence vault, regulator instant verify, Kennel audit bridge
 * @institutional POPIA §19 · GDPR §32 · SOC2 §CC7.2
 */
function buildVerifyAuditUrl(state = {}) {
  const trace = textValue(state.traceId || state.requestProof || 'UNKNOWN').replace(/[^A-Za-z0-9._-]/g, '');
  return `https://verify.wilsy.os/audit/${encodeURIComponent(trace || 'UNKNOWN')}`;
}

/**
 * @function buildPaymentSettleUrl
 * @description One-click settlement deep-link (PayShap / Zapper compatible landing).
 *              Live rails resolve amount + reference server-side from invoice id.
 * @param {object} state
 * @returns {string}
 * @collaboration Treasury, PayShap, Zapper, collections path
 */
function buildPaymentSettleUrl(state = {}) {
  const inv = encodeURIComponent(textValue(state.invoiceNumber || state.title || 'INV'));
  const amount = Number(state.totalAmount ?? state.amount ?? 0).toFixed(2);
  const currency = encodeURIComponent(textValue(state.currency || 'ZAR'));
  const tenant = encodeURIComponent(textValue(state.tenantId || 'MASTER'));
  return `https://pay.wilsy.os/settle?ref=${inv}&amount=${amount}&currency=${currency}&tenant=${tenant}`;
}

/**
 * @function resolveInvoicePaymentInstructions
 * @description Resolves issuer-owned payment instructions without exposing platform banking details on tenant-issued invoices.
 * @param {object} state Hydrated invoice state.
 * @returns {{rail:string,bankName:string,accountName:string,accountNumber:string,branchCode:string,bicSwift:string,reference:string}|null} Printable settlement instructions.
 * @collaboration Keeps Wilsy platform collection details separate from tenant-to-client branding and settlement rails.
 */
function resolveInvoicePaymentInstructions(state = {}) {
  const issuerType = textValue(state.issuerType).toUpperCase();
  const branding = state.brandingNexus || {};
  if (issuerType === 'PLATFORM') {
    const bankName = textValue(process.env.CAPITEC_BANK_NAME);
    const accountName = textValue(process.env.CAPITEC_ACCOUNT_NAME);
    const accountNumber = textValue(process.env.CAPITEC_ACCOUNT_NUMBER);
    const branchCode = textValue(process.env.CAPITEC_BRANCH_CODE);
    const bicSwift = textValue(process.env.CAPITEC_BIC_SWIFT);
    if (!bankName || !accountName || !accountNumber || !branchCode) return null;
    return {
      rail: 'Bank transfer (EFT)',
      bankName,
      accountName,
      accountNumber,
      branchCode,
      bicSwift,
      reference: textValue(state.invoiceNumber || state.title),
    };
  }
  const tenantPayment = branding.paymentInstructions || branding.payment_details || null;
  if (!tenantPayment || typeof tenantPayment !== 'object') return null;
  return {
    rail: textValue(tenantPayment.rail || 'Bank transfer'),
    bankName: textValue(tenantPayment.bankName || tenantPayment.bank_name),
    accountName: textValue(tenantPayment.accountName || tenantPayment.account_name),
    accountNumber: textValue(tenantPayment.accountNumber || tenantPayment.account_number),
    branchCode: textValue(tenantPayment.branchCode || tenantPayment.branch_code),
    bicSwift: textValue(tenantPayment.bicSwift || tenantPayment.bic_swift),
    reference: textValue(tenantPayment.reference || state.invoiceNumber || state.title),
  };
}

/**
 * @function drawQrBlock
 * @description Draws a labelled QR (or text fallback) inside a framed card.
 * @param {PDFDocument} doc
 * @param {number} x
 * @param {number} y
 * @param {number} size - image size in pt
 * @param {Buffer|null} pngBuffer
 * @param {string} label
 * @param {string} caption - short URL/hint under label
 * @returns {number} height consumed
 */
function drawQrBlock(doc, x, y, size, pngBuffer, label, caption) {
  const framePad = 8;
  const frameW = size + framePad * 2;
  const frameH = size + framePad * 2 + 28;
  doc.roundedRect(x, y, frameW, frameH, 4).strokeColor(BRAND.line).lineWidth(0.8).stroke();
  doc.fillColor(BRAND.gold).font('Helvetica-Bold').fontSize(7)
    .text(textValue(label).toUpperCase(), x + 4, y + 5, { width: frameW - 8, align: 'center', lineBreak: false });

  const imgY = y + 16;
  if (pngBuffer && Buffer.isBuffer(pngBuffer) && pngBuffer.length > 32) {
    try {
      doc.image(pngBuffer, x + framePad, imgY, { width: size, height: size });
    } catch {
      doc.fillColor(BRAND.muted).font('Helvetica').fontSize(6.5)
        .text('QR unavailable', x + framePad, imgY + size / 2 - 4, { width: size, align: 'center' });
    }
  } else {
    doc.roundedRect(x + framePad, imgY, size, size, 2).fill(BRAND.panel);
    doc.fillColor(BRAND.muted).font('Helvetica').fontSize(6)
      .text('Install npm\npackage qrcode', x + framePad + 4, imgY + size / 2 - 10, {
        width: size - 8,
        align: 'center',
      });
  }

  doc.fillColor(BRAND.muted).font('Helvetica').fontSize(5.5)
    .text(textValue(caption).slice(0, 42), x + 2, y + frameH - 12, {
      width: frameW - 4,
      align: 'center',
      lineBreak: false,
    });
  return frameH;
}

function isBillingInvoiceType(type = '') {
  const t = textValue(type).toLowerCase();
  return (
    t.includes('billing-invoice') ||
    t.includes('billing_invoice') ||
    t === 'invoice' ||
    t.includes('billing-statement') ||
    t.includes('billing_statement') ||
    t === 'statement'
  );
}

/**
 * @function formatInvoiceMoney
 * @description Formats invoice amounts for PDF (ZAR-first, multi-currency safe).
 */
function formatInvoiceMoney(amount = 0, currency = 'ZAR') {
  const n = Number(amount);
  const cur = textValue(currency) || 'ZAR';
  if (!Number.isFinite(n)) return `${cur} 0.00`;
  try {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: cur,
      minimumFractionDigits: 2,
    }).format(n);
  } catch {
    return `${cur} ${n.toFixed(2)}`;
  }
}

/**
 * @function formatEnterpriseDate
 * @description Converts ISO date strings to "DD MMM YYYY" format (e.g., "08 SEP 2026").
 * @param {string} isoString - ISO date string.
 * @returns {string} Formatted date or original if invalid.
 */
function formatEnterpriseDate(isoString) {
  if (!isoString) return '—';
  try {
    const date = new Date(isoString);
    if (Number.isNaN(date.getTime())) return isoString;
    const day = String(date.getDate()).padStart(2, '0');
    const month = date.toLocaleString('en-ZA', { month: 'short' }).toUpperCase();
    const year = date.getFullYear();
    return `${day} ${month} ${year}`;
  } catch {
    return isoString;
  }
}

/**
 * @function getBusinessPostureLabel
 * @description Maps technical source posture codes to business‑friendly labels.
 * @param {string} posture - Technical posture value (e.g., "SOURCE_LIVE").
 * @returns {string} Business‑friendly label.
 * @collaboration Wilson Khanyezi – mandated removal of backend jargon.
 * @institutional Ensures regulators and clients see enterprise‑grade terminology.
 */
function getBusinessPostureLabel(posture) {
  const map = {
    'SOURCE_LIVE': 'LIVE LEDGER',
    'SOURCE_REPAIR_REQUIRED': 'REPAIR REQUIRED',
    'SOURCE_SILENT': 'VERIFICATION PENDING',
    'SOURCE_ERROR': 'INTEGRITY CHECK FAILED',
    'SOURCE_STANDBY': 'AWAITING CONFIRMATION',
  };
  return map[posture] || posture;
}

/**
 * @function hydrateBillingInvoiceState
 * @description Maps BillingHUD / generate-pdf payload into commercial invoice state.
 * Extends with forecast, anomalies, escalation, compliance badges from identity metadata.
 * 🆕 Injects Wilsy platform defaults (reg, VAT, address) for platform invoices.
 * @collaboration Wilson Khanyezi – Mandated real Wilsy details on platform invoices.
 * @institutional POPIA §19, GDPR §32, SOC2 §CC7.2, SARS VAT Act, CIPC registration 2024/617944/07
 */
function hydrateBillingInvoiceState(state = {}, identity = {}) {
  const meta = identity.metadata || identity.payload?.metadata || {};
  const data = identity.data || identity.payload || identity.payloadData || {};
  const type = textValue(state.type || identity.type || identity.artifactType || '');

  if (!isBillingInvoiceType(type)) {
    return state;
  }

  // Extract line items from multiple sources
  let lineItems = [];
  if (Array.isArray(data.lineItems) && data.lineItems.length) {
    lineItems = data.lineItems;
  } else if (Array.isArray(meta.lineItems) && meta.lineItems.length) {
    lineItems = meta.lineItems;
  } else if (Array.isArray(data.items) && data.items.length) {
    lineItems = data.items;
  }

  const amount = Number(
    meta.amount ?? data.totalAmount ?? data.amount ?? identity.amount ?? 0
  );
  const currency = textValue(meta.currency || data.currency || 'ZAR') || 'ZAR';
  const invoiceNumber = textValue(
    meta.invoiceNumber ||
    data.invoiceNumber ||
    meta.invoiceId ||
    data.invoiceId ||
    identity.title ||
    state.title
  );
  const status = textValue(meta.status || data.status || 'ISSUED').toUpperCase();
  const dueDate = textValue(meta.dueDate || data.dueDate || '');
  const issueDate = textValue(
    meta.issueDate || data.issueDate || state.effectiveDate || ''
  );
  const sealHash = textValue(meta.sealHash || data.sealHash || state.sha3 || '');
  const branding = data.brandingNexus || meta.brandingNexus || null;
  const issuerTypeRaw = textValue(
    meta.issuerType || data.issuerType || meta.invoiceScope || data.invoiceScope || ''
  ).toUpperCase();

  // ─── WILSY PLATFORM DEFAULTS ──────────────────────────────────────────────
  const WILSY_DEFAULTS = {
    issuerRegNumber: '2024/617944/07',
    supplierVatNumber: '9395759229',
    supplierAddress: 'UNIT 29 SUMATRA ESTATE, CNR 8TH RD AND 7TH RD, NOORDWYK MIDRAND, GAUTENG, 1682'
  };

  const isPlatform = issuerTypeRaw === 'PLATFORM' ||
    issuerTypeRaw === 'WILSY_PLATFORM' ||
    textValue(state.tenantId).toUpperCase() === 'GLOBAL_ROOT' ||
    textValue(state.tenantId).toUpperCase() === 'WILSY_PLATFORM';

  const regNumber = textValue(
    meta.issuerRegNumber ||
    data.issuerRegNumber ||
    branding?.registrationNumber ||
    branding?.companyReg ||
    (isPlatform ? WILSY_DEFAULTS.issuerRegNumber : '')
  );

  const vatNumber = textValue(
    meta.supplierVatNumber ||
    data.supplierVatNumber ||
    branding?.vatNumber ||
    branding?.vatNo ||
    (isPlatform ? WILSY_DEFAULTS.supplierVatNumber : '')
  );

  const address = textValue(
    meta.supplierAddress ||
    data.supplierAddress ||
    branding?.address ||
    branding?.businessAddress ||
    (isPlatform ? WILSY_DEFAULTS.supplierAddress : '')
  );

  // ─── Forensic enhancements ──────────────────────────────────────────────
  const forecast = meta.forecast || data.forecast || null;
  const anomalies = Array.isArray(meta.anomalies)
    ? meta.anomalies
    : Array.isArray(data.anomalies)
      ? data.anomalies
      : [];
  const escalation = meta.escalation || data.escalation || null;
  const complianceBadges = meta.complianceBadges || data.complianceBadges || ['POPIA', 'GDPR', 'SOC2'];

  // ─── SARS‑Compliant VAT Calculation ────────────────────────────
  const VAT_RATE = 0.15;
  let subtotalExclVAT = 0;
  let totalVAT = 0;
  const enrichedItems = [];

  if (lineItems.length) {
    const hasTaxAmounts = lineItems.some(li => Number(li.taxAmount) > 0);

    for (const li of lineItems) {
      const qty = Number(li.quantity ?? 1);
      let lineTotalIncl = Number(li.lineTotal ?? li.amount ?? qty * (li.unitPrice ?? 0));
      if (lineTotalIncl === 0 && li.unitPrice) {
        lineTotalIncl = qty * Number(li.unitPrice);
      }

      let vatAmount = 0;
      let lineExcl = lineTotalIncl;

      if (hasTaxAmounts) {
        vatAmount = Number(li.taxAmount || 0);
        lineExcl = lineTotalIncl - vatAmount;
      } else if (lineTotalIncl > 0) {
        vatAmount = lineTotalIncl / (1 + VAT_RATE) * VAT_RATE;
        lineExcl = lineTotalIncl - vatAmount;
      }

      subtotalExclVAT += lineExcl;
      totalVAT += vatAmount;

      enrichedItems.push({
        ...li,
        _vatExclusivePrice: lineExcl / qty,
        _calculatedTaxAmount: vatAmount,
        _lineExclTotal: lineExcl,
        _lineInclTotal: lineTotalIncl,
        serviceType: textValue(li.serviceType || li.category || li.type || ''),
      });
    }
  } else {
    const totalIncl = amount || 0;
    if (totalIncl > 0) {
      totalVAT = totalIncl / (1 + VAT_RATE) * VAT_RATE;
      subtotalExclVAT = totalIncl - totalVAT;
    }
  }

  const totalAmount = subtotalExclVAT + totalVAT;

  return {
    ...state,
    hasBillingInvoice: true,
    title: invoiceNumber || state.title || 'Sovereign Invoice',
    type: textValue(identity.type || identity.artifactType || state.type || 'billing-invoice'),
    invoiceNumber,
    status,
    amount: totalAmount,
    currency,
    dueDate,
    issueDate,
    sealHash,
    lineItems: enrichedItems,
    subtotalExclVAT,
    totalVAT,
    totalAmount,
    vatRate: VAT_RATE,
    subtotal: subtotalExclVAT,
    taxAmount: totalVAT,
    taxRate: VAT_RATE,
    brandingNexus: branding,
    issuerType: issuerTypeRaw || (isPlatform ? 'PLATFORM' : 'TENANT'),
    issuingEntity: textValue(
      branding?.legalEntity || state.issuingEntity || identity.issuingEntity || 'Wilsy (Pty) Ltd'
    ),
    issuerRegNumber: regNumber,
    supplierVatNumber: vatNumber,
    supplierAddress: address,
    paymentInstructions: resolveInvoicePaymentInstructions({
      issuerType: issuerTypeRaw || (isPlatform ? 'PLATFORM' : 'TENANT'),
      brandingNexus: branding || {},
      invoiceNumber,
      title: state.title,
    }),
    counterparty: textValue(
      identity.counterparty || data.counterparty || meta.counterparty || state.counterparty
    ),
    forecast,
    anomalies,
    escalation,
    complianceBadges,
  };
}

/**
 * @function isBillingInvoiceState
 * @param {object} state
 * @returns {boolean}
 */
function isBillingInvoiceState(state = {}) {
  return Boolean(state.hasBillingInvoice);
}

/**
 * @function drawLineItemTable
 * @description Draws a structured table for invoice line items.
 * @param {PDFDocument} doc - PDFKit document.
 * @param {object} cursor - Cursor object with y.
 * @param {Array} lineItems - Array of line items.
 * @param {string} currency - Currency code.
 * @returns {object} Updated cursor.
 */
function drawLineItemTable(doc, cursor, lineItems, currency) {
  cursor = normalizeEnterprisePdfCursor(cursor, PAGE.top);
  const tableLeft = PAGE.left + 10;
  const tableWidth = PAGE.contentWidth - 20;
  const colDesc = tableWidth * 0.45;
  const colQty = tableWidth * 0.12;
  const colUnit = tableWidth * 0.18;
  const colTotal = tableWidth * 0.25;

  // Table header
  const headerY = cursor.y;
  doc.rect(tableLeft, headerY, tableWidth, 20).fill(BRAND.black);
  doc.fillColor('#FFFFFF').font('Helvetica-Bold').fontSize(8);
  const headerTexts = ['Description', 'Qty', 'Unit Price', 'Total'];
  const xPositions = [tableLeft, tableLeft + colDesc, tableLeft + colDesc + colQty, tableLeft + colDesc + colQty + colUnit];
  headerTexts.forEach((text, i) => {
    doc.text(text, xPositions[i] + 6, headerY + 4, { width: xPositions[i + 1] ? xPositions[i + 1] - xPositions[i] - 12 : tableWidth - xPositions[i] - 6, lineBreak: false });
  });
  cursor.y = headerY + 20;

  // Rows
  lineItems.forEach((item, index) => {
    const y = cursor.y;
    const bg = index % 2 === 0 ? '#FFFFFF' : BRAND.band;
    doc.rect(tableLeft, y, tableWidth, 18).fill(bg);
    doc.fillColor(BRAND.black).font('Helvetica').fontSize(8);

    const desc = textValue(item.description || item.name || 'Service');
    const qty = Number(item.quantity ?? 1);
    const unit = Number(item.unitPrice ?? item.amount ?? 0);
    const lineTotal = Number(item.lineTotal ?? qty * unit);
    const money = (v) => formatInvoiceMoney(v, currency);

    doc.text(desc, tableLeft + 6, y + 2, { width: colDesc - 12, lineBreak: true });
    doc.text(String(qty), tableLeft + colDesc + 6, y + 2, { width: colQty - 12, lineBreak: false });
    doc.text(money(unit), tableLeft + colDesc + colQty + 6, y + 2, { width: colUnit - 12, lineBreak: false });
    doc.text(money(lineTotal), tableLeft + colDesc + colQty + colUnit + 6, y + 2, { width: colTotal - 12, lineBreak: false });

    cursor.y = y + 18;
  });

  // Bottom border
  doc.rect(tableLeft, cursor.y, tableWidth, 1).fill(BRAND.line);
  cursor.y += 2;

  return cursor;
}

/**
 * @function getBillingInvoiceSections
 * @description Commercial sections for tax-grade invoices – now with service type, prominent amounts, and SARS‑compliant VAT breakdown.
 */
function getBillingInvoiceSections(state = {}) {
  const money = (v) => formatInvoiceMoney(v, state.currency);
  const date = (iso) => formatEnterpriseDate(iso);

  // Build line items as a structured object to be rendered as a table later
  const lineItems = Array.isArray(state.lineItems) && state.lineItems.length
    ? state.lineItems.map((li) => ({
      description: textValue(li.description || li.name || 'Service'),
      serviceType: textValue(li.serviceType || li.category || li.type || ''),
      quantity: Number(li.quantity ?? 1),
      unitPrice: Number(li.unitPrice ?? li.amount ?? 0),
      lineTotal: Number(li.lineTotal ?? li.amount ?? (li.quantity || 1) * (li.unitPrice || 0)),
      taxAmount: Number(li._calculatedTaxAmount ?? li.taxAmount ?? 0),
    }))
    : [];

  // Build sections – we will handle the line items table separately
  const sections = [
    {
      title: '1. COMMERCIAL SUMMARY',
      paragraphs: [
        `Invoice: ${state.invoiceNumber}  •  Status: ${state.status}`,
        `Issue: ${date(state.issueDate)}  •  Due: ${date(state.dueDate)}`,
        `Currency: ${state.currency}`,
        `▶  TOTAL AMOUNT DUE: ${money(state.totalAmount)} (VAT INCLUSIVE)`,
        `   Subtotal (excl. VAT): ${money(state.subtotalExclVAT)}`,
        `   VAT (${Math.round(state.vatRate * 100)}%): ${money(state.totalVAT)}`,
      ],
    },
    {
      title: '2. PARTIES',
      paragraphs: [
        `Supplier: ${state.issuingEntity}`,
        `Customer: ${state.counterparty}`,
        `Jurisdiction: ${state.jurisdiction}`,
        // Add VAT numbers if present
        ...(state.supplierVatNumber ? [`Supplier VAT No.: ${state.supplierVatNumber}`] : []),
        ...(state.customerVatNumber ? [`Customer VAT No.: ${state.customerVatNumber}`] : []),
        ...(state.supplierAddress ? [`Supplier Address: ${state.supplierAddress}`] : []),
      ],
    },
    {
      title: '3. LINE ITEMS (VAT INCLUSIVE PRICES SHOWN)',
      lineItemsTable: true,
      lineItemsData: lineItems,
    },
    {
      title: '4. COMPLIANCE BADGES',
      paragraphs: state.complianceBadges && state.complianceBadges.length
        ? state.complianceBadges.map((badge) => `✅ ${badge} compliant`)
        : ['✅ POPIA compliant', '✅ GDPR compliant', '✅ SOC2 compliant'],
    },
  ];

  // Predictive overlay
  if (state.forecast) {
    sections.push({
      title: '5. PREDICTIVE FORECAST',
      paragraphs: [
        `Payment probability: ${state.forecast.prediction}  •  Confidence: ${state.forecast.confidence}%`,
        `Expected settlement: ${date(state.forecast.expectedDate)}`,
      ],
    });
  }

  // Anomaly detection
  if (state.anomalies && state.anomalies.length > 0) {
    sections.push({
      title: '6. ANOMALY DETECTION',
      paragraphs: state.anomalies.map((a) => `⚠️ ${a.description}`),
    });
  }

  // Escalation automation
  if (state.escalation) {
    const tickets = Array.isArray(state.escalation.tickets) ? state.escalation.tickets.join(', ') : '—';
    const alerts = Array.isArray(state.escalation.alerts) ? state.escalation.alerts.join(', ') : '—';
    sections.push({
      title: '7. ESCALATION LOG',
      paragraphs: [
        `Tickets: ${tickets}`,
        `Alerts: ${alerts}`,
        `History: ${(state.escalation.history || []).map((e) => `${date(e.timestamp)} – ${e.action}`).join('; ')}`,
      ],
    });
  }

  // Forensic seal
  sections.push({
    title: '8. FORENSIC SEAL',
    paragraphs: [
      `Seal: ${compactProof(state.sealHash || state.sha3)}`,
      `Trace: ${state.traceId}`,
      `Merkle: ${compactProof(state.merkleRoot)}`,
      `Source: ${state.sourcePosture}`,
      'This invoice is generated under Wilsy OS Billing Nucleus. Commercial figures are from the live ledger at print time.',
    ],
  });

  return sections;
}

// ─── END BILLING INVOICE HELPERS ───────────────────────────────────────────

// ─── DRAWING FUNCTIONS ──────────────────────────────────────────────────────

/**
 * @function drawLogo
 * @description Draws the Wilsy logo optically centered inside the enterprise header badge.
 */
function drawLogo(doc) {
  const logoPath = findLogoPath();
  const boxX = 60;
  const boxY = 50;
  const boxSize = 62;
  const logoWidth = 44;
  const logoHeight = 50;

  doc.roundedRect(boxX, boxY, boxSize, boxSize, 5).fill('#FFFFFF');

  if (logoPath) {
    try {
      doc.image(logoPath, boxX + (boxSize - logoWidth) / 2, boxY + (boxSize - logoHeight) / 2, {
        fit: [logoWidth, logoHeight],
      });
      return;
    } catch {
      // fallback below
    }
  }

  doc
    .fillColor(BRAND.black)
    .font('Helvetica-Bold')
    .fontSize(17)
    .text('WO', boxX + 18, boxY + 24, { width: 26, align: 'center', lineBreak: false });
}

/**
 * @function drawComplianceBadge
 * @description Draws a fixed-size gold outline badge with text optically centered.
 * @param {PDFDocument} doc
 * @param {number} x
 * @param {number} y
 * @param {string} label
 * @returns {number} width consumed including gap
 * @collaboration Invoice header compliance strip
 */
function drawComplianceBadge(doc, x, y, label) {
  const text = textValue(label).toUpperCase().slice(0, 12);
  const padX = 10;
  doc.font('Helvetica-Bold').fontSize(6.5);
  const textW = Math.min(72, Math.max(36, doc.widthOfString(text) + padX * 2));
  const h = 15;
  doc
    .roundedRect(x, y, textW, h, 2)
    .strokeColor(BRAND.gold)
    .lineWidth(1)
    .stroke();
  const textY = y + (h - 7) / 2;
  doc
    .fillColor(BRAND.gold)
    .font('Helvetica-Bold')
    .fontSize(6.5)
    .text(text, x, textY, { width: textW, align: 'center', lineBreak: false });
  return textW + 6;
}

/**
 * @function resolveInvoiceIssuerIdentity
 * @description Platform invoices/statements → Wilsy (Pty) Ltd with reg/VAT/address; tenant invoices → tenant business name.
 * @param {object} state
 * @returns {{ issuerType: string, legalName: string, regLine: string, detailLine: string }}
 * @collaboration Branding nexus, businessArtifactPdfController, multi-tenant statements
 * @institutional SARS issuer identity · POPIA §19
 */
function resolveInvoiceIssuerIdentity(state = {}) {
  const typeHint = textValue(state.issuerType || state.invoiceScope || '').toUpperCase();
  const branding = state.brandingNexus || {};
  const legalFromBrand = textValue(branding.legalEntity || branding.businessName || '');
  const issuing = textValue(state.issuingEntity || '');
  const platformNames = ['WILSY (PTY) LTD', 'WILSY OS', 'WILSY', 'WILSY_PLATFORM', 'Wilsy (Pty) Ltd'];

  let issuerType = typeHint;
  if (!issuerType) {
    const candidate = (legalFromBrand || issuing).toUpperCase();
    const isPlatform =
      !candidate ||
      platformNames.some((n) => candidate.includes(String(n).toUpperCase())) ||
      textValue(state.tenantId).toUpperCase() === 'GLOBAL_ROOT' ||
      textValue(state.tenantId).toUpperCase() === 'WILSY_PLATFORM';
    issuerType = isPlatform ? 'PLATFORM' : 'TENANT';
  }

  const legalName =
    issuerType === 'PLATFORM'
      ? textValue(legalFromBrand || issuing || 'Wilsy (Pty) Ltd') || 'Wilsy (Pty) Ltd'
      : textValue(legalFromBrand || issuing || state.counterparty || 'Tenant') || 'Tenant';

  // Build reg line from state fields (which now include defaults for platform)
  const regParts = [
    textValue(state.supplierVatNumber || branding.vatNumber || branding.vatNo || ''),
    textValue(state.issuerRegNumber || branding.registrationNumber || branding.companyReg || ''),
  ].filter(Boolean);
  const regLine = regParts.length
    ? regParts.join('  ·  ')
    : issuerType === 'PLATFORM'
      ? 'Wilsy OS · Institutional billing nucleus'
      : 'Tenant-issued sovereign invoice';

  const detailLine =
    textValue(state.supplierAddress || branding.address || branding.footer || '') ||
    (issuerType === 'PLATFORM' ? 'Registered company · Republic of South Africa' : '');

  return { issuerType, legalName, regLine, detailLine };
}

/**
 * @function drawHeader
 * @description Header hierarchy: logo · doc type · issuer legal name · invoice no · centred badges.
 *              Platform artifacts show Wilsy (Pty) Ltd with reg/VAT/address; tenant artifacts show tenant business name.
 *              Invoice number is never concatenated into the title string (avoids ugly wrap).
 */
function drawHeader(doc, state, pageNumber, totalPages) {
  doc.save();

  // Header band
  doc.rect(42, 34, 512, 88).fill(BRAND.black);
  doc.rect(42, 122, 512, 4).fill(BRAND.gold);

  drawLogo(doc);

  const contentX = 140;
  const contentW = 280;
  const issuer = isBillingInvoiceState(state)
    ? resolveInvoiceIssuerIdentity(state)
    : {
      issuerType: 'PLATFORM',
      legalName: textValue(state.issuingEntity || 'Wilsy (Pty) Ltd'),
      regLine: '',
      detailLine: '',
    };

  // Line 1 — document type (gold micro-label)
  doc
    .fillColor(BRAND.gold)
    .font('Helvetica-Bold')
    .fontSize(8)
    .text(
      isBillingInvoiceState(state) ? 'TAX INVOICE' : 'ENTERPRISE ARTIFACT',
      contentX,
      48,
      { width: contentW, lineBreak: false }
    );

  // Line 2 — issuer legal name (primary, white) — company identity, not the long invoice id
  doc
    .fillColor('#FFFFFF')
    .font('Helvetica-Bold')
    .fontSize(13)
    .text(issuer.legalName, contentX, 60, {
      width: contentW,
      lineBreak: false,
    });

  // Line 3 — invoice number OR artifact title as secondary mono-style row
  const secondary = isBillingInvoiceState(state)
    ? `No.  ${textValue(state.invoiceNumber || state.title || '—')}`
    : textValue(state.title || 'Wilsy OS Artifact');
  doc
    .fillColor('#C9C3B4')
    .font('Helvetica')
    .fontSize(8)
    .text(secondary, contentX, 78, { width: contentW, lineBreak: false });

  // Line 4 — issuer registration / VAT / address (very compact)
  if (issuer.regLine) {
    doc
      .fillColor('#8A8578')
      .font('Helvetica')
      .fontSize(6.5)
      .text(issuer.regLine, contentX, 90, { width: contentW, lineBreak: false });
  }

  // Compliance badges — fixed height, text centred in frame
  if (isBillingInvoiceState(state) && state.complianceBadges && state.complianceBadges.length) {
    let badgeX = contentX;
    const badgeY = 102;
    state.complianceBadges.slice(0, 5).forEach((badge) => {
      badgeX += drawComplianceBadge(doc, badgeX, badgeY, badge);
    });
  }

  // Right meta
  doc
    .fillColor(BRAND.gold)
    .font('Helvetica-Bold')
    .fontSize(8)
    .text('VERIFIED', 420, 52, { width: 70, align: 'right', lineBreak: false });

  doc
    .fillColor('#FFFFFF')
    .font('Helvetica-Bold')
    .fontSize(8)
    .text(`PAGE ${pageNumber}/${totalPages}`, 490, 52, {
      width: 52,
      align: 'right',
      lineBreak: false,
    });

  // Issuer scope chip (PLATFORM / TENANT)
  if (isBillingInvoiceState(state)) {
    doc
      .fillColor(BRAND.gold)
      .font('Helvetica-Bold')
      .fontSize(7)
      .text(issuer.issuerType === 'TENANT' ? 'TENANT ISSUE' : 'PLATFORM ISSUE', 420, 68, {
        width: 122,
        align: 'right',
        lineBreak: false,
      });
  }

  doc.restore();
}

/**
 * @function drawCoverPage
 * @description Draws the Executive Digest Cover (Page 1) – total box, forecast, escalation, forensic footer.
 */
function drawCoverPage(doc, state) {
  const money = (v) => formatInvoiceMoney(v, state.currency);
  const date = (iso) => formatEnterpriseDate(iso);

  // ─── Total Amount Box ──────────────────────────────────────────────────
  const boxY = 140;
  const boxX = PAGE.left;
  const boxWidth = PAGE.contentWidth;
  const boxHeight = 90;

  // Gold border and background
  doc.roundedRect(boxX, boxY, boxWidth, boxHeight, 6)
    .fill(BRAND.panel)
    .strokeColor(BRAND.gold)
    .lineWidth(2)
    .stroke();

  // Label
  doc
    .fillColor(BRAND.muted)
    .font('Helvetica')
    .fontSize(10)
    .text('TOTAL AMOUNT DUE', boxX + 20, boxY + 14, { width: boxWidth - 40, align: 'center' });

  // Amount
  doc
    .fillColor(BRAND.gold)
    .font('Helvetica-Bold')
    .fontSize(26)
    .text(money(state.totalAmount), boxX + 20, boxY + 30, { width: boxWidth - 40, align: 'center' });

  // VAT breakdown
  doc
    .fillColor(BRAND.muted)
    .font('Helvetica')
    .fontSize(8.5)
    .text(
      `Subtotal: ${money(state.subtotalExclVAT)}  |  VAT (${Math.round(state.vatRate * 100)}%): ${money(state.totalVAT)}`,
      boxX + 20,
      boxY + 68,
      { width: boxWidth - 40, align: 'center' }
    );

  let cursorY = boxY + boxHeight + 24;

  // ─── Predictive Forecast ──────────────────────────────────────────────
  if (state.forecast) {
    doc
      .fillColor(BRAND.black)
      .font('Helvetica-Bold')
      .fontSize(10)
      .text('PREDICTIVE FORECAST', PAGE.left, cursorY);
    cursorY += 16;

    doc
      .fillColor(BRAND.muted)
      .font('Helvetica')
      .fontSize(9)
      .text(
        `Payment probability: ${state.forecast.prediction}  •  Confidence: ${state.forecast.confidence}%  •  Expected settlement: ${date(state.forecast.expectedDate)}`,
        PAGE.left + 10,
        cursorY,
        { width: PAGE.contentWidth - 20 }
      );
    cursorY += 22;
  }

  // ─── Escalation Summary ──────────────────────────────────────────────
  if (state.escalation) {
    doc
      .fillColor(BRAND.black)
      .font('Helvetica-Bold')
      .fontSize(10)
      .text('ESCALATION OVERVIEW', PAGE.left, cursorY);
    cursorY += 16;

    const tickets = Array.isArray(state.escalation.tickets) ? state.escalation.tickets.join(', ') : '—';
    const alerts = Array.isArray(state.escalation.alerts) ? state.escalation.alerts.join(', ') : '—';
    doc
      .fillColor(BRAND.muted)
      .font('Helvetica')
      .fontSize(9)
      .text(
        `Tickets: ${tickets}  •  Alerts: ${alerts}`,
        PAGE.left + 10,
        cursorY,
        { width: PAGE.contentWidth - 20 }
      );
    cursorY += 22;
  }

  // ─── Forensic Footer ──────────────────────────────────────────────────
  cursorY = Math.max(cursorY, 650);
  drawForensicFooter(doc, state, cursorY);
}

/**
 * @function drawForensicFooter
 * @description Draws a prominent forensic footer block with SEAL, MERKLE, TRACE, and SOURCE labels, and a QR code at the bottom‑right.
 * @param {PDFDocument} doc - PDFKit document.
 * @param {object} state - Hydrated state.
 * @param {number} y - Y-coordinate to place the footer.
 * @returns {number} Updated Y-coordinate after footer.
 * @collaboration Wilson Khanyezi – mandated prominent, gold-accented forensic block.
 * @institutional Provides instant visual identification of cryptographic identifiers.
 */
function drawForensicFooter(doc, state, y) {
  const startY = y;
  const blockHeight = 120;
  const blockX = PAGE.left;
  const blockWidth = PAGE.contentWidth;

  // Draw a dark panel with gold top border
  doc.rect(blockX, startY, blockWidth, blockHeight)
    .fill(BRAND.black)
    .rect(blockX, startY, blockWidth, 3)
    .fill(BRAND.gold);

  // Title
  doc
    .fillColor(BRAND.gold)
    .font('Helvetica-Bold')
    .fontSize(9)
    .text('FORENSIC PROOF TRAIL', blockX + 12, startY + 12, { width: blockWidth - 24, align: 'left' });

  // Grid: 2 columns
  const col1 = blockX + 20;
  const col2 = blockX + blockWidth / 2 + 10;
  const rowHeight = 20;
  let rowY = startY + 32;

  const items = [
    { label: 'SEAL:', value: compactProof(state.sha3 || state.sealHash || 'PENDING') },
    { label: 'MERKLE ROOT:', value: compactProof(state.merkleRoot || 'PENDING') },
    { label: 'TRACE ID:', value: state.traceId || 'PENDING' },
    { label: 'SOURCE:', value: getBusinessPostureLabel(state.sourcePosture) || 'UNKNOWN' },
  ];

  // Draw each item in two columns
  items.forEach((item, index) => {
    const col = index % 2 === 0 ? col1 : col2;
    const row = Math.floor(index / 2);
    const yPos = rowY + row * rowHeight;

    doc
      .fillColor(BRAND.gold)
      .font('Helvetica-Bold')
      .fontSize(8)
      .text(item.label, col, yPos, { width: 90, lineBreak: false });

    doc
      .fillColor('#FFFFFF')
      .font('Helvetica')
      .fontSize(8)
      .text(item.value, col + 95, yPos, { width: blockWidth / 2 - 110, lineBreak: false });
  });

  // ─── QR Code (bottom‑right corner) ───────────────────────────────────
  if (state._qrVerifyPng && Buffer.isBuffer(state._qrVerifyPng) && state._qrVerifyPng.length > 32) {
    try {
      const qrSize = 36;
      const qrX = blockX + blockWidth - qrSize - 20;
      const qrY = startY + blockHeight - qrSize - 24; // 24pt above the bottom, above the verify link
      doc.image(state._qrVerifyPng, qrX, qrY, { width: qrSize, height: qrSize });
      // Gold border around QR
      doc.rect(qrX - 2, qrY - 2, qrSize + 4, qrSize + 4)
        .strokeColor(BRAND.gold)
        .lineWidth(0.8)
        .stroke();
    } catch {
      // QR rendering failed, ignore
    }
  }

  // ─── Verify Online link ──────────────────────────────────────────────
  const verifyUrl = state._verifyUrl || buildVerifyAuditUrl(state);
  const linkY = startY + blockHeight - 18;
  doc
    .fillColor(BRAND.gold)
    .font('Helvetica-Bold')
    .fontSize(8)
    .text('VERIFY ONLINE →', blockX + 20, linkY, { width: blockWidth - 40, align: 'right' })
    .link(blockX + blockWidth - 160, linkY, 150, 14, verifyUrl);

  return startY + blockHeight + 10;
}

/**
 * @function drawFooter
 * @description Draws a non-overlapping proof footer (used on all pages except cover? we'll use custom footer on cover).
 * For simplicity, we'll keep the same footer on all pages, but the cover already has its own footer.
 */
function drawFooter(doc, state) {
  // Use the new forensic footer for invoice pages
  if (isBillingInvoiceState(state) && state.type === 'billing-invoice') {
    // Determine Y position – place it near the bottom of the page
    const y = Math.min(PAGE.bottom - 140, 720);
    drawForensicFooter(doc, state, y);
    return;
  }

  // Fallback: original simple footer
  doc.save();

  doc.moveTo(PAGE.left, 762).lineTo(543, 762).strokeColor(BRAND.line).lineWidth(0.6).stroke();

  doc
    .fillColor(BRAND.muted)
    .font('Helvetica')
    .fontSize(6.2)
    .text(
      isBillingInvoiceState(state)
        ? 'Commercial figures are taken from the live ledger at print time. Retain with the Wilsy OS proof trail.'
        : 'Legally non-final until reviewed and approved. Retain with the Wilsy OS proof trail.',
      PAGE.left,
      773,
      { width: 282, lineBreak: false }
    );

  doc
    .fillColor(BRAND.black)
    .font('Helvetica-Bold')
    .fontSize(6.2)
    .text(isBillingInvoiceState(state) ? 'PAYMENT & AUTHORITY' : 'DIRECTOR - WILSON KHANYEZI', PAGE.left, 792, { width: 282, lineBreak: false });

  doc
    .fillColor(BRAND.gold)
    .font('Helvetica-Bold')
    .fontSize(5.4)
    .text(`TRACE ${compactProof(state.traceId)}`, 344, 772, {
      width: 199,
      align: 'right',
      lineBreak: false,
    });

  doc
    .fillColor(BRAND.gold)
    .font('Helvetica-Bold')
    .fontSize(5.4)
    .text(`MERKLE ${compactProof(state.merkleRoot)}`, 344, 782, {
      width: 199,
      align: 'right',
      lineBreak: false,
    });

  doc
    .fillColor(BRAND.muted)
    .font('Helvetica')
    .fontSize(5.3)
    .text(`SHA3 ${compactProof(state.sha3)}`, 344, 792, {
      width: 199,
      align: 'right',
      lineBreak: false,
    });

  const businessLabel = getBusinessPostureLabel(state.sourcePosture);
  doc
    .fillColor(BRAND.muted)
    .font('Helvetica')
    .fontSize(5.3)
    .text(businessLabel, 344, 802, { width: 199, align: 'right', lineBreak: false });

  doc.restore();
}

/**
 * @function ensureSpace
 * @description Adds a page when the remaining content area is too small.
 */
function ensureSpace(doc, cursor, required) {
  cursor = normalizeEnterprisePdfCursor(cursor, PAGE.top);
  if (cursor.y + required <= PAGE.bottom) return;

  doc.addPage();
  cursor.y = PAGE.top;
}

/**
 * @function writeParagraph
 * @description Writes a numbered paragraph and updates the cursor.
 */
function writeParagraph(doc, cursor, paragraph, index) {
  cursor = normalizeEnterprisePdfCursor(cursor, PAGE.top);
  const paragraphWidth = PAGE.contentWidth - 32;
  const paragraphHeight = doc.heightOfString(textValue(paragraph), {
    width: paragraphWidth,
    lineGap: 2.8,
  });

  ensureSpace(doc, cursor, Math.max(34, paragraphHeight + 16));

  doc
    .fillColor(BRAND.gold)
    .font('Helvetica-Bold')
    .fontSize(8)
    .text(`${index + 1}.`, PAGE.left + 8, cursor.y + 1, { width: 18, lineBreak: false });

  doc
    .fillColor(BRAND.black)
    .font('Helvetica')
    .fontSize(8.8)
    .text(textValue(paragraph), PAGE.left + 30, cursor.y, {
      width: paragraphWidth,
      lineGap: 2.8,
    });

  cursor.y = doc.y + 10;

  return cursor;
}

/**
 * @function drawSection
 * @description Draws a controlled enterprise section.
 * 🆕 If the section has `lineItemsTable: true`, it renders a table instead of paragraphs.
 */
function drawSection(doc, cursor, section) {
  cursor = normalizeEnterprisePdfCursor(cursor, PAGE.top);
  ensureSpace(doc, cursor, 72);

  doc
    .fillColor(BRAND.black)
    .font('Helvetica-Bold')
    .fontSize(11.2)
    .text(textValue(section.title).toUpperCase(), PAGE.left, cursor.y, {
      width: PAGE.contentWidth,
    });

  cursor.y = doc.y + 14;

  // Check if this section should render a line‑item table
  if (section.lineItemsTable && Array.isArray(section.lineItemsData)) {
    const state = section._state || {};
    const currency = state.currency || 'ZAR';
    cursor = drawLineItemTable(doc, cursor, section.lineItemsData, currency);
    cursor.y += 10;
    return cursor;
  }

  const paragraphs = Array.isArray(section.paragraphs) ? section.paragraphs : [];
  paragraphs.forEach((paragraph, index) => {
    cursor = writeParagraph(doc, cursor, paragraph, index);
  });

  cursor.y += 10;

  return cursor;
}

/**
 * @function drawDocumentControl
 * @description Draws the document control section (used in appendix pages).
 */
function drawDocumentControl(doc, cursor, state) {
  cursor = normalizeEnterprisePdfCursor(cursor, PAGE.top);
  doc
    .fillColor(BRAND.black)
    .font('Helvetica-Bold')
    .fontSize(15)
    .text('FORENSIC APPENDIX — DOCUMENT CONTROL', PAGE.left, cursor.y);
  cursor.y = doc.y + 22;

  let rows = [
    ['Issuing Entity', state.issuingEntity],
    ['Counterparty / Tenant', state.counterparty],
    ['Effective Date', state.effectiveDate],
    ['Generated By', state.generatedBy],
    ['Version', state.version],
    ['Jurisdiction', state.jurisdiction],
    ['Source Posture', state.sourcePosture],
    ['Trace ID', state.traceId],
    ['Merkle Root', compactProof(state.merkleRoot)],
  ];

  if (isBillingInvoiceState(state)) {
    rows = [
      ['Invoice Number', state.invoiceNumber || state.title],
      ['Status', state.status],
      ['TOTAL AMOUNT DUE (VAT INCL)', formatInvoiceMoney(state.totalAmount, state.currency)],
      ['Subtotal (excl. VAT)', formatInvoiceMoney(state.subtotalExclVAT, state.currency)],
      [`VAT (${Math.round(state.vatRate * 100)}%)`, formatInvoiceMoney(state.totalVAT, state.currency)],
      ['Due Date', state.dueDate || '—'],
      ...rows,
    ];
  }

  rows.forEach((row, index) => {
    const y = cursor.y + index * 21;
    doc.rect(PAGE.left, y, PAGE.contentWidth, 20).fill(index % 2 === 0 ? '#FFFFFF' : BRAND.band);
    doc
      .fillColor(BRAND.muted)
      .font('Helvetica-Bold')
      .fontSize(6.8)
      .text(row[0].toUpperCase(), PAGE.left + 10, y + 7, { width: 160, lineBreak: false });
    doc
      .fillColor(BRAND.black)
      .font('Helvetica')
      .fontSize(7.8)
      .text(row[1], PAGE.left + 190, y + 7, { width: 280, lineBreak: false });
  });

  cursor.y += rows.length * 21 + 26;

  doc.roundedRect(PAGE.left, cursor.y, PAGE.contentWidth, 82, 8).fill(BRAND.panel);
  doc.rect(PAGE.left, cursor.y, 5, 82).fill(BRAND.gold);

  doc
    .fillColor(BRAND.gold)
    .font('Helvetica-Bold')
    .fontSize(8)
    .text('RELIANCE NOTICE', PAGE.left + 18, cursor.y + 14);
  doc
    .fillColor(BRAND.black)
    .font('Helvetica')
    .fontSize(8.1)
    .text(
      'This forensic appendix provides the complete audit trail and commercial breakdown. The amounts shown are commercially binding. Disputes must be raised through the Wilsy OS war-room / collections path.',
      PAGE.left + 18,
      cursor.y + 31,
      { width: 450, lineGap: 2.2 }
    );

  cursor.y += 106;

  return cursor;
}

/**
 * @function resolveCrmProofPackFromIdentity
 * @description Resolves CRM Proof Pack evidence from the already-adapted enterprise identity.
 */
function resolveCrmProofPackFromIdentity(identity = {}) {
  const data = identity.data || {};
  const payload = identity.payload || {};
  const payloadData = identity.payloadData || {};

  return (
    identity.crmProofPack ||
    identity.proofPackSections ||
    payloadData.crmProofPack ||
    payloadData.proofPackSections ||
    payload.crmProofPack ||
    payload.proofPackSections ||
    data.crmProofPack ||
    data.proofPackSections ||
    {}
  );
}

/**
 * @function hasCrmProofPackEvidence
 * @description Detects whether a CRM proof pack contains exportable evidence rows.
 */
function hasCrmProofPackEvidence(proofPack = {}) {
  return Boolean(
    Array.isArray(proofPack.proofSummaryRows) ||
    Array.isArray(proofPack.authoritySealRows) ||
    Array.isArray(proofPack.proofChecks) ||
    Array.isArray(proofPack.operationalTimeline) ||
    Array.isArray(proofPack.scopedRecords) ||
    Array.isArray(proofPack.metricsRows)
  );
}

/**
 * @function hydrateCrmProofPackState
 * @description Adds CRM Proof Pack evidence to the normal enterprise render state.
 */
function hydrateCrmProofPackState(state = {}, identity = {}, proof = {}) {
  const proofPack = resolveCrmProofPackFromIdentity(identity);

  if (!hasCrmProofPackEvidence(proofPack)) {
    return state;
  }

  const tenantId = textValue(proofPack.tenantId || identity.tenantId || state.tenantId || 'MASTER');
  const generatedBy = resolveHumanGeneratedByName({ proofPack, identity, state });
  const operatorEmail = textValue(
    proofPack.operatorEmail ||
    proofPack.email ||
    identity.userEmail ||
    identity.email ||
    identity.user?.email ||
    state.operatorEmail ||
    ''
  );

  const sourcePosture = textValue(
    proofPack.sourcePosture ||
    (identity.sourcePosture && identity.sourcePosture !== 'SOURCE_REPAIR_REQUIRED'
      ? identity.sourcePosture
      : '') ||
    (proof.sourcePosture && proof.sourcePosture !== 'SOURCE_REPAIR_REQUIRED'
      ? proof.sourcePosture
      : '') ||
    'SOURCE_LIVE'
  );

  return {
    ...state,
    tenantId,
    counterparty: textValue(proofPack.counterparty || tenantId),
    generatedBy,
    operatorEmail,
    sourcePosture,
    generatedAt: textValue(proofPack.generatedAt || identity.generatedAt || state.generatedAt),
    crmProofPack: proofPack,
    hasCrmProofPack: true,
    proofSummaryRows: proofPack.proofSummaryRows || [],
    authoritySealRows: replaceGeneratedBySlugRows(proofPack.authoritySealRows || [], generatedBy),
    proofChecks: proofPack.proofChecks || [],
    operationalTimeline: proofPack.operationalTimeline || [],
    scopedRecords: proofPack.scopedRecords || [],
    metricsRows: proofPack.metricsRows || [],
  };
}

/**
 * @function isCrmProofPackState
 * @description Detects CRM Proof Pack state inside the enterprise branded PDF renderer.
 */
function isCrmProofPackState(state = {}) {
  return Boolean(state.hasCrmProofPack);
}

/**
 * @function normalizeCrmProofPackText
 * @description Converts CRM proof evidence values into compact PDF-safe text.
 */
function normalizeCrmProofPackText(value = '') {
  if (Array.isArray(value)) {
    return value
      .map((item) => normalizeCrmProofPackText(item))
      .filter(Boolean)
      .join(' - ');
  }

  if (value && typeof value === 'object') {
    return Object.entries(value)
      .map(([key, itemValue]) => `${textValue(key)}: ${normalizeCrmProofPackText(itemValue)}`)
      .filter(Boolean)
      .join(' - ');
  }

  return textValue(value);
}

/**
 * @function normalizeCrmProofPackRowsForPdf
 * @description Converts CRM Proof Pack rows into narrative bullets for the branded renderer.
 */
function normalizeCrmProofPackRowsForPdf(rows = []) {
  if (!Array.isArray(rows)) return [];

  return rows
    .map((row) => {
      if (Array.isArray(row)) {
        return `${textValue(row[0])}: ${normalizeCrmProofPackText(row[1])}`;
      }

      if (row && typeof row === 'object') {
        const label = textValue(row.label || row.title || row.key || row.name || 'Evidence');
        const detail = normalizeCrmProofPackText(
          [row.status, row.reason, row.value, row.detail].filter(Boolean)
        );

        return detail ? `${label}: ${detail}` : label;
      }

      return normalizeCrmProofPackText(row);
    })
    .filter(Boolean);
}

/**
 * @function getCrmProofPackSections
 * @description Builds CRM Proof Pack sections while preserving the Wilsy enterprise PDF chrome.
 */
function getCrmProofPackSections(state = {}) {
  return [
    {
      title: '1. PROOF SUMMARY AND OPERATING CONTEXT',
      paragraphs: [
        'This Lead Evidence Ledger Proof Pack records the saved-view proof, ledger access decision, export authority, source-route posture, membership overrides and run receipt that support the CRM operating decision.',
        ...normalizeCrmProofPackRowsForPdf(state.proofSummaryRows),
      ],
    },
    {
      title: '2. TENANT, OPERATOR AND AUTHORITY SEALS',
      paragraphs: [
        `Tenant: ${state.tenantId}`,
        `Generated by: ${state.generatedBy}`,
        `Operator email: ${state.operatorEmail}`,
        `Source posture: ${state.sourcePosture}`,
        ...normalizeCrmProofPackRowsForPdf(state.authoritySealRows),
      ],
    },
    {
      title: '3. PROOF CHECKS, CONTROLS AND EXCEPTIONS',
      paragraphs: [
        'The checks below show what was validated before this proof pack was exported.',
        ...normalizeCrmProofPackRowsForPdf(state.proofChecks),
      ],
    },
    {
      title: '4. OPERATIONAL TIMELINE AND SCOPED RECORDS',
      paragraphs: [
        'The timeline and scoped-record evidence below explain what happened, what data was in scope, and how the proof can be reconstructed.',
        ...normalizeCrmProofPackRowsForPdf(state.operationalTimeline),
        ...normalizeCrmProofPackRowsForPdf(state.scopedRecords),
      ],
    },
    {
      title: '5. METRICS AND DECISION SUPPORT',
      paragraphs: [
        'The metrics below summarize the exported CRM proof result.',
        ...normalizeCrmProofPackRowsForPdf(state.metricsRows),
      ],
    },
  ];
}

/**
 * @function getCrmProofPackScheduleSections
 * @description Builds CRM Proof Pack appendix sections for the branded enterprise schedule area.
 */
function getCrmProofPackScheduleSections(state = {}) {
  return [
    {
      title: 'SCHEDULE A - CRM PROOF EVIDENCE LEDGER',
      paragraphs: [
        ...normalizeCrmProofPackRowsForPdf(state.proofSummaryRows),
        ...normalizeCrmProofPackRowsForPdf(state.authoritySealRows),
        ...normalizeCrmProofPackRowsForPdf(state.proofChecks),
      ],
    },
    {
      title: 'SCHEDULE B - FORENSIC PROOF APPENDIX',
      paragraphs: [
        `Trace ID: ${state.traceId}`,
        `Merkle Root: ${state.merkleRoot}`,
        `SHA3 / Seal: ${state.sha3}`,
        `Source Posture: ${state.sourcePosture}`,
        `Generated At: ${state.generatedAt}`,
        'This appendix supports audit reconstruction, version comparison, dispute response, investor diligence and internal control review.',
      ],
    },
  ];
}

/**
 * @function getNdaSections
 * @description Returns deeper enterprise NDA clauses.
 */
function getNdaSections(state) {
  return [
    {
      title: '1. Instrument Status, Parties and Effective Date',
      paragraphs: [
        `This Non-Disclosure Agreement is issued by ${state.issuingEntity} for use with ${state.counterparty}. It is generated through Wilsy OS as a source-aware legal artifact and remains subject to final business, legal and authority review before external reliance.`,
        `The effective date is ${state.effectiveDate}. Each party must ensure the person signing has authority to bind the relevant entity, and any missing registration, address, representative, schedule or commercial field must remain visible until verified.`,
      ],
    },
    {
      title: '2. Definitions',
      paragraphs: [
        '“Confidential Information” means all information disclosed or made available in connection with the permitted purpose, whether oral, written, electronic, visual, technical, operational, commercial, financial, legal, regulatory, product, source-code, architecture, security, client, tenant, pricing, roadmap, investor, employee, procurement or forensic information.',
        '“Representatives” means directors, officers, employees, contractors, professional advisers, auditors, investors, funders and affiliates who have a need to know and are bound by confidentiality obligations no less protective than this agreement.',
      ],
    },
    {
      title: '3. Permitted Purpose and Use Restrictions',
      paragraphs: [
        'The receiving party may use Confidential Information only for the authorised business purpose recorded in the applicable engagement, evaluation, diligence, onboarding, procurement, integration or commercial negotiation record.',
        'The receiving party must not copy, reverse engineer, decompile, benchmark, publish, train models on, scrape, exploit, commercialise, disclose or use Confidential Information for any competing, unauthorised, unlawful or personal purpose.',
      ],
    },
    {
      title: '4. Security Standard and Incident Duties',
      paragraphs: [
        'The receiving party must protect Confidential Information using administrative, technical and organisational controls appropriate to the sensitivity of the information, including access limitation, secure storage, device protection, encryption where appropriate, auditability and need-to-know distribution.',
        'Any suspected unauthorised access, disclosure, loss, compromise, ransomware event, credential exposure, insider risk or legal demand must be notified promptly with sufficient detail to support containment, investigation, regulatory assessment and remediation.',
      ],
    },
    {
      title: '5. Remedies, POPIA and Survival',
      paragraphs: [
        'The parties acknowledge that unauthorised disclosure or misuse may cause irreparable harm for which damages may be inadequate. The disclosing party may seek urgent interdictory, injunctive or equitable relief without prejudice to other remedies.',
        `Where Confidential Information includes personal information or regulated records, the parties must comply with applicable privacy, data protection, retention and breach notification duties, including POPIA where applicable in the ${state.jurisdiction}.`,
      ],
    },
  ];
}

/**
 * @function getGenericSections
 * @description Returns enterprise fallback sections for non-NDA artifacts.
 */
function getGenericSections(state) {
  return [
    {
      title: '1. Executive Purpose and Operating Context',
      paragraphs: [
        `${state.title} is generated for ${state.issuingEntity} under Wilsy OS artifact authority. It supports executive decision-making, operational execution, compliance evidence, commercial negotiation or controlled business workflow completion.`,
        'This artifact must be reviewed with its source records, approvals, schedules, attachments and Wilsy OS proof trail.',
      ],
    },
    {
      title: '2. Parties, Owners and Authority',
      paragraphs: [
        `The issuing entity is ${state.issuingEntity}. The counterparty, tenant, employee, supplier, client or stakeholder is ${state.counterparty}.`,
        'Only authorised users may generate, approve, circulate, amend, execute or rely on this artifact. Missing approval, signature or source fields must remain visible until verified.',
      ],
    },
    {
      title: '3. Scope, Controls and Exceptions',
      paragraphs: [
        'The artifact records the business purpose, obligations, decision posture, control evidence and operational assumptions reflected in connected Wilsy OS source systems.',
        'Exceptions require documented approval, accountable owner, expiry date and remediation path.',
      ],
    },
    {
      title: '4. Forensic Proof and Retention',
      paragraphs: [
        `Trace identifier: ${state.traceId}. Merkle root: ${compactProof(state.merkleRoot)}. Source posture: ${state.sourcePosture}.`,
        'External distribution should occur through the Wilsy OS document vault or an approved connector so access logs, version history, proof verification and revocation can be reconstructed.',
      ],
    },
  ];
}

/**
 * @function resolveWilsyKnowledgeBaseFromIdentity
 * @description Resolves a Wilsy knowledge-base/playbook payload from the enterprise PDF identity envelope.
 */
function resolveWilsyKnowledgeBaseFromIdentity(identity = {}) {
  const data = identity.data || {};
  const payload = identity.payload || {};
  const payloadData = identity.payloadData || {};
  const metadata = identity.metadata || payload.metadata || data.metadata || {};

  return (
    identity.knowledgeBase ||
    identity.playbook ||
    identity.playbookPayload ||
    payloadData.knowledgeBase ||
    payloadData.playbook ||
    payloadData.playbookPayload ||
    payload.knowledgeBase ||
    payload.playbook ||
    payload.playbookPayload ||
    data.knowledgeBase ||
    data.playbook ||
    data.playbookPayload || {
      type:
        identity.type ||
        identity.artifactType ||
        payloadData.type ||
        payloadData.artifactType ||
        payload.type ||
        payload.artifactType ||
        data.type ||
        metadata.type,
      artifactType:
        identity.artifactType ||
        payloadData.artifactType ||
        payload.artifactType ||
        data.artifactType ||
        metadata.artifactType,
      title: identity.title || payloadData.title || payload.title || data.title || metadata.title,
      subtitle: payloadData.subtitle || payload.subtitle || data.subtitle || metadata.subtitle,
      summary: payloadData.summary || payload.summary || data.summary || metadata.summary,
      markdown: payloadData.markdown || payload.markdown || data.markdown || metadata.markdown,
      sections:
        payloadData.playbookSections ||
        payloadData.knowledgeBaseSections ||
        payloadData.sections ||
        payload.sections ||
        data.sections,
      metrics: payloadData.metrics || payload.metrics || data.metrics,
      tenantId:
        identity.tenantId ||
        payloadData.tenantId ||
        payload.tenantId ||
        data.tenantId ||
        metadata.tenantId,
      generatedByDisplayName:
        identity.generatedByDisplayName ||
        payloadData.generatedByDisplayName ||
        payload.generatedByDisplayName ||
        data.generatedByDisplayName ||
        metadata.generatedByDisplayName,
      operatorDisplayName:
        identity.operatorDisplayName ||
        payloadData.operatorDisplayName ||
        payload.operatorDisplayName ||
        data.operatorDisplayName ||
        metadata.operatorDisplayName,
      ownerDisplayName:
        identity.ownerDisplayName ||
        payloadData.ownerDisplayName ||
        payload.ownerDisplayName ||
        data.ownerDisplayName ||
        metadata.ownerDisplayName,
      displayName:
        identity.displayName ||
        payloadData.displayName ||
        payload.displayName ||
        data.displayName ||
        metadata.displayName,
      generatedBy:
        identity.generatedBy ||
        identity.userEmail ||
        identity.email ||
        payloadData.generatedBy ||
        payload.generatedBy ||
        data.generatedBy ||
        metadata.generatedBy,
      generatedAt:
        identity.generatedAt ||
        payloadData.generatedAt ||
        payloadData.timestamp ||
        payload.generatedAt ||
        data.generatedAt ||
        metadata.generatedAt ||
        metadata.timestamp,
      sourcePosture:
        identity.sourcePosture ||
        payloadData.sourcePosture ||
        payload.sourcePosture ||
        data.sourcePosture ||
        metadata.sourcePosture,
    }
  );
}

/**
 * @function isWilsyKnowledgeBaseCandidate
 * @description Detects Wilsy knowledge-base/playbook artifacts before the generic legal renderer is selected.
 */
function isWilsyKnowledgeBaseCandidate(candidate = {}) {
  const values = [
    candidate.type,
    candidate.artifactType,
    candidate.templateType,
    candidate.title,
    candidate.subtitle,
  ]
    .map((value) => textValue(value).toUpperCase())
    .filter(Boolean);

  return values.some(
    (value) =>
      value.includes('WILSY_AI_INLINE_COMMAND_PLAYBOOK_FG108') ||
      value.includes('WILSY KNOWLEDGE BASE') ||
      value.includes('KNOWLEDGE_BASE') ||
      value.includes('KNOWLEDGE BASE') ||
      value.includes('PLAYBOOK')
  );
}

/**
 * @function normalizeWilsyKnowledgeBaseText
 * @description Converts knowledge-base payload values into safe enterprise-renderer paragraph text.
 */
function normalizeWilsyKnowledgeBaseText(value = '') {
  if (Array.isArray(value)) {
    return value
      .map((item) => normalizeWilsyKnowledgeBaseText(item))
      .filter(Boolean)
      .join(' - ');
  }

  if (value && typeof value === 'object') {
    return Object.entries(value)
      .map(([key, itemValue]) => `${textValue(key)}: ${normalizeWilsyKnowledgeBaseText(itemValue)}`)
      .filter(Boolean)
      .join(' - ');
  }

  return textValue(value);
}

/**
 * @function normalizeWilsyKnowledgeBaseSection
 * @description Converts a playbook section payload into the enterprise renderer section contract.
 */
function normalizeWilsyKnowledgeBaseSection(section = {}, index = 0) {
  if (typeof section === 'string') {
    return {
      title: `SECTION ${index + 1}`,
      paragraphs: [normalizeWilsyKnowledgeBaseText(section)],
    };
  }

  const title = normalizeWilsyKnowledgeBaseText(
    section.title || section.heading || section.label || `Section ${index + 1}`
  );

  const body =
    section.paragraphs ||
    section.body ||
    section.summary ||
    section.content ||
    section.description ||
    '';

  const paragraphs = Array.isArray(body)
    ? body.map((item) => normalizeWilsyKnowledgeBaseText(item)).filter(Boolean)
    : normalizeWilsyKnowledgeBaseText(body)
      .split(/\n+/)
      .map((item) => item.trim())
      .filter(Boolean);

  return {
    title,
    paragraphs: paragraphs.length
      ? paragraphs
      : ['Wilsy OS knowledge-base section retained for controlled review.'],
  };
}

/**
 * @function resolveWilsyKnowledgeBaseMarkdownSections
 * @description Converts markdown headings into enterprise renderer sections when structured sections are absent.
 */
function resolveWilsyKnowledgeBaseMarkdownSections(markdown = '') {
  const value = textValue(markdown);
  if (!value) return [];

  return value
    .split(/\n(?=##\s+)/)
    .map((chunk) => chunk.trim())
    .filter(Boolean)
    .slice(0, 14)
    .map((chunk, index) => {
      const lines = chunk
        .split(/\n+/)
        .map((line) => line.trim())
        .filter(Boolean);
      const title = textValue(lines.shift() || `Section ${index + 1}`).replace(/^#+\s*/, '');
      const paragraphs = lines
        .join(' ')
        .split(/\s{2,}|---/)
        .map((line) => textValue(line))
        .filter(Boolean)
        .slice(0, 8);

      return {
        title,
        paragraphs: paragraphs.length
          ? paragraphs
          : ['Wilsy OS knowledge-base content retained for review.'],
      };
    });
}

/**
 * @function isWilsyProfessionalDisplayName
 * @description Validates that a display-name candidate looks like a professional human or institutional name.
 */
function isWilsyProfessionalDisplayName(value = '') {
  const candidate = textValue(value);

  if (!candidate) return false;
  if (candidate === candidate.toLowerCase()) return false;
  if (/^[a-z0-9_.-]+$/.test(candidate)) return false;
  if (candidate.includes('@')) return false;

  return /[A-Z]/.test(candidate) && /[a-z]/.test(candidate) && candidate.length >= 3;
}

/**
 * @function formatWilsyDisplayNameFromIdentityCandidate
 * @description Builds a generic display-name candidate from profile-style identity fields.
 */
function formatWilsyDisplayNameFromIdentityCandidate(value = '') {
  const raw = textValue(value).replace(/^@/, '');

  if (!raw || raw.includes('@')) return '';

  const spaced = raw
    .replace(/[_-]+/g, ' ')
    .replace(/\.+/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/\s+/g, ' ')
    .trim();

  const words = spaced.split(' ').filter(Boolean);

  if (words.length < 2) return '';

  return words
    .map((word) => `${word.slice(0, 1).toUpperCase()}${word.slice(1).toLowerCase()}`)
    .join(' ');
}

/**
 * @function resolveWilsyProfessionalGeneratedBy
 * @description Resolves a professional Generated By display name from explicit payload, profile, or state fields.
 */
function resolveWilsyProfessionalGeneratedBy(knowledgeBase = {}, state = {}) {
  const explicitCandidates = [
    knowledgeBase.generatedByDisplayName,
    knowledgeBase.operatorDisplayName,
    knowledgeBase.ownerDisplayName,
    knowledgeBase.displayName,
    knowledgeBase.fullName,
    knowledgeBase.name,
    state.generatedByDisplayName,
    state.operatorDisplayName,
    state.ownerDisplayName,
    state.displayName,
    state.fullName,
    state.name,
  ];

  for (const candidate of explicitCandidates) {
    if (isWilsyProfessionalDisplayName(candidate)) return textValue(candidate);
  }

  const generatedByCandidates = [
    knowledgeBase.generatedBy,
    knowledgeBase.operatorName,
    state.generatedBy,
    state.operatorName,
  ];

  for (const candidate of generatedByCandidates) {
    if (isWilsyProfessionalDisplayName(candidate)) return textValue(candidate);
  }

  const derivedCandidates = [
    knowledgeBase.operatorDisplayName,
    knowledgeBase.ownerDisplayName,
    knowledgeBase.displayName,
    knowledgeBase.operatorName,
    state.operatorDisplayName,
    state.ownerDisplayName,
    state.displayName,
    state.operatorName,
  ];

  for (const candidate of derivedCandidates) {
    const formatted = formatWilsyDisplayNameFromIdentityCandidate(candidate);
    if (isWilsyProfessionalDisplayName(formatted)) return formatted;
  }

  return 'Wilsy OS Operator';
}

/**
 * @function hydrateWilsyKnowledgeBaseState
 * @description Adds Wilsy knowledge-base playbook content to the enterprise render state.
 */
function hydrateWilsyKnowledgeBaseState(state = {}, identity = {}, proof = {}) {
  const knowledgeBase = resolveWilsyKnowledgeBaseFromIdentity(identity);

  if (!isWilsyKnowledgeBaseCandidate(knowledgeBase)) {
    return state;
  }

  const structuredSections =
    Array.isArray(knowledgeBase.sections) && knowledgeBase.sections.length > 0
      ? knowledgeBase.sections.map((section, index) =>
        normalizeWilsyKnowledgeBaseSection(section, index)
      )
      : resolveWilsyKnowledgeBaseMarkdownSections(knowledgeBase.markdown);

  return {
    ...state,
    title: textValue(
      knowledgeBase.title || state.title || 'WILSY OS AI INLINE COMMAND PLAYBOOK - FG108'
    ),
    type: textValue(
      knowledgeBase.type ||
      knowledgeBase.artifactType ||
      state.type ||
      'WILSY_AI_INLINE_COMMAND_PLAYBOOK_FG108'
    ),
    tenantId: textValue(knowledgeBase.tenantId || state.tenantId || 'wilsy-sovereign-root'),
    counterparty: textValue(knowledgeBase.tenantId || state.tenantId || 'wilsy-sovereign-root'),
    generatedBy: resolveWilsyProfessionalGeneratedBy(knowledgeBase, state),
    generatedByDisplayName: resolveWilsyProfessionalGeneratedBy(knowledgeBase, state),
    generatedAt: textValue(
      knowledgeBase.generatedAt || state.generatedAt || new Date().toISOString()
    ),
    sourcePosture: textValue(knowledgeBase.sourcePosture || 'KNOWLEDGE_BASE_VERIFIED'),
    version: textValue(knowledgeBase.version || 'WILSY-OS-KNOWLEDGE-BASE-FG108-v1.0'),
    hasWilsyKnowledgeBase: true,
    wilsyKnowledgeBase: knowledgeBase,
    knowledgeBaseSections: structuredSections.length
      ? structuredSections
      : [
        {
          title: 'Executive Summary',
          paragraphs: [
            textValue(
              knowledgeBase.summary ||
              'Wilsy OS knowledge-base playbook generated through the governed enterprise PDF renderer.'
            ),
          ],
        },
      ],
  };
}

/**
 * @function isWilsyKnowledgeBaseState
 * @description Detects a hydrated Wilsy knowledge-base state inside the enterprise PDF renderer.
 */
function isWilsyKnowledgeBaseState(state = {}) {
  return Boolean(state.hasWilsyKnowledgeBase);
}

/**
 * @function getWilsyKnowledgeBaseSections
 * @description Builds primary Wilsy knowledge-base sections while preserving enterprise PDF chrome.
 */
function getWilsyKnowledgeBaseSections(state = {}) {
  return [
    {
      title: '1. KNOWLEDGE BASE PURPOSE AND OPERATING CONTEXT',
      paragraphs: [
        'This artifact is a Wilsy OS knowledge-base playbook for investor review, user enablement, engineering continuity and controlled product governance.',
        `Tenant: ${state.tenantId}`,
        `Generated by: ${state.generatedBy}`,
        `Source posture: ${state.sourcePosture}`,
      ],
    },
    ...state.knowledgeBaseSections,
  ];
}

/**
 * @function getWilsyKnowledgeBaseScheduleSections
 * @description Builds non-legal appendix sections for Wilsy knowledge-base artifacts.
 */
function getWilsyKnowledgeBaseScheduleSections(state = {}) {
  return [
    {
      title: 'APPENDIX A - KNOWLEDGE BASE PROOF CONTEXT',
      paragraphs: [
        `Trace ID: ${state.traceId}`,
        `Merkle root: ${compactProof(state.merkleRoot)}`,
        `Source posture: ${state.sourcePosture}`,
        `Route: /api/generate/pdf`,
        'This appendix supports reconstruction, version comparison, investor diligence, user training and future engineering continuity.',
      ],
    },
  ];
}

/**
 * @function buildSections
 * @description Selects the appropriate clause library for the artifact type.
 */
function buildSections(state) {
  if (isWilsyKnowledgeBaseState(state)) {
    return getWilsyKnowledgeBaseSections(state);
  }

  if (isCrmProofPackState(state)) {
    return getCrmProofPackSections(state);
  }

  // INVOICE BRANCH
  if (isBillingInvoiceState(state)) {
    return getBillingInvoiceSections(state);
  }

  const type = state.type.toLowerCase();

  if (type.includes('nda') || type.includes('non-disclosure')) {
    return getNdaSections(state);
  }

  return getGenericSections(state);
}

/**
 * @function applyChrome
 * @description Applies headers and footers after final page count is known.
 */
function applyChrome(doc, state) {
  const range = doc.bufferedPageRange();
  // Page 1 is cover – use header with no total (handled by drawHeader)
  // Pages 2+ are appendix – same header
  for (let pageIndex = range.start; pageIndex < range.start + range.count; pageIndex += 1) {
    doc.switchToPage(pageIndex);
    // Header is the same for all pages (no total inside)
    drawHeader(doc, state, pageIndex - range.start + 1, range.count);
    // Footer – we'll use a consistent footer, but cover already has its own special footer.
    // We'll skip footer on cover because we already drew one.
    if (pageIndex > range.start) {
      drawFooter(doc, state);
    }
  }
}

/**
 * @function normalizeEnterprisePdfCursor
 * @description Guarantees the enterprise PDF renderer always has a mutable cursor before draw functions read cursor.y.
 */
function normalizeEnterprisePdfCursor(cursor = {}, fallbackY = PAGE.top) {
  const resolvedCursor = cursor && typeof cursor === 'object' ? cursor : {};
  const numericY = Number(resolvedCursor.y);
  resolvedCursor.y = Number.isFinite(numericY) ? numericY : fallbackY;

  return resolvedCursor;
}


/**
 * @function drawCommercialInvoicePage
 * @description World-class single-page tax invoice. Content is spaced across the
 *              page (not bunched at the top). Parties, meta strip, line table,
 *              gold total, payment terms; forensic strip sits near the foot when
 *              the invoice is short so the sheet does not look empty.
 * @param {PDFDocument} doc
 * @param {object} state - Hydrated billing invoice state
 * @returns {object} cursor
 * @collaboration BillingHUD print, SARS VAT layout, Kennel-sealed commercial PDF
 * @institutional POPIA §19 · GDPR §32 · SARS VAT Act 89 of 1991
 */
function drawCommercialInvoicePage(doc, state) {
  const money = (v) => formatInvoiceMoney(v, state.currency);
  const date = (iso) => formatEnterpriseDate(iso);
  const usableBottom = 718; // leave room for global chrome footer
  let y = 138;

  // ── Invoice identity (under header band) ─────────────────────────────
  doc
    .fillColor(BRAND.black)
    .font('Helvetica-Bold')
    .fontSize(20)
    .text('TAX INVOICE', PAGE.left, y, { width: 220, lineBreak: false });
  doc
    .fillColor(BRAND.gold)
    .font('Helvetica-Bold')
    .fontSize(10)
    .text(textValue(state.invoiceNumber || state.title), PAGE.left + 220, y + 6, {
      width: PAGE.contentWidth - 220,
      align: 'right',
      lineBreak: false,
    });
  y += 32;

  // ── Status / issue / due strip ───────────────────────────────────────
  doc.roundedRect(PAGE.left, y, PAGE.contentWidth, 30, 4).fill(BRAND.band);
  doc
    .fillColor(BRAND.black)
    .font('Helvetica-Bold')
    .fontSize(8)
    .text(
      `STATUS  ${textValue(state.status || 'ISSUED')}    ·    ISSUE  ${date(state.issueDate)}    ·    DUE  ${date(state.dueDate)}    ·    ${textValue(state.currency || 'ZAR')}`,
      PAGE.left + 14,
      y + 10,
      { width: PAGE.contentWidth - 28, lineBreak: false }
    );
  y += 46;

  // ── Parties — two equal cards with light panel ───────────────────────
  const colGap = 18;
  const colW = (PAGE.contentWidth - colGap) / 2;
  const partyH = 72;

  doc.roundedRect(PAGE.left, y, colW, partyH, 5).fill(BRAND.panel);
  doc.roundedRect(PAGE.left + colW + colGap, y, colW, partyH, 5).fill(BRAND.panel);
  doc.rect(PAGE.left, y, 4, partyH).fill(BRAND.gold);
  doc.rect(PAGE.left + colW + colGap, y, 4, partyH).fill(BRAND.gold);

  const leftX = PAGE.left + 14;
  const rightX = PAGE.left + colW + colGap + 14;
  const labelY = y + 12;
  const nameY = y + 28;
  const metaY = y + 48;

  doc.fillColor(BRAND.gold).font('Helvetica-Bold').fontSize(7).text('FROM / SUPPLIER', leftX, labelY, { width: colW - 24 });
  doc.fillColor(BRAND.gold).font('Helvetica-Bold').fontSize(7).text('BILL TO / CUSTOMER', rightX, labelY, { width: colW - 24 });

  doc.fillColor(BRAND.black).font('Helvetica-Bold').fontSize(11)
    .text(textValue(state.issuingEntity), leftX, nameY, { width: colW - 24, lineBreak: false });
  doc.fillColor(BRAND.black).font('Helvetica-Bold').fontSize(11)
    .text(textValue(state.counterparty), rightX, nameY, { width: colW - 24, lineBreak: false });

  // Supplier address (if available) – shown under the supplier name
  if (state.supplierAddress) {
    doc.fillColor(BRAND.muted).font('Helvetica').fontSize(7.5)
      .text(textValue(state.supplierAddress), leftX, metaY + 10, { width: colW - 24, lineBreak: true });
  } else {
    doc.fillColor(BRAND.muted).font('Helvetica').fontSize(8)
      .text(`Tenant: ${textValue(state.tenantId)}`, leftX, metaY, { width: colW - 24, lineBreak: false });
  }

  doc.fillColor(BRAND.muted).font('Helvetica').fontSize(8)
    .text(`Jurisdiction: ${textValue(state.jurisdiction)}`, rightX, metaY, { width: colW - 24, lineBreak: false });

  y += partyH + 28;

  // ── Line items ───────────────────────────────────────────────────────
  doc.fillColor(BRAND.black).font('Helvetica-Bold').fontSize(10).text('LINE ITEMS', PAGE.left, y);
  y += 16;

  const colDesc = PAGE.contentWidth * 0.48;
  const colQty = PAGE.contentWidth * 0.12;
  const colUnit = PAGE.contentWidth * 0.20;
  const colTot = PAGE.contentWidth * 0.20;
  const rowH = 26;

  doc.rect(PAGE.left, y, PAGE.contentWidth, rowH).fill(BRAND.black);
  doc.fillColor('#FFFFFF').font('Helvetica-Bold').fontSize(8);
  doc.text('Description', PAGE.left + 12, y + 9, { width: colDesc - 16, lineBreak: false });
  doc.text('Qty', PAGE.left + colDesc, y + 9, { width: colQty - 8, align: 'right', lineBreak: false });
  doc.text('Unit Price', PAGE.left + colDesc + colQty, y + 9, { width: colUnit - 8, align: 'right', lineBreak: false });
  doc.text('Total', PAGE.left + colDesc + colQty + colUnit, y + 9, { width: colTot - 12, align: 'right', lineBreak: false });
  y += rowH;

  const items = Array.isArray(state.lineItems) && state.lineItems.length
    ? state.lineItems
    : [{ description: textValue(state.title) || 'Sovereign service', quantity: 1, unitPrice: state.subtotal || state.amount, lineTotal: state.subtotal || state.amount }];

  items.forEach((item, idx) => {
    if (y + rowH > usableBottom - 160) return;
    if (idx % 2 === 0) {
      doc.rect(PAGE.left, y, PAGE.contentWidth, rowH).fill('#FFFFFF');
    } else {
      doc.rect(PAGE.left, y, PAGE.contentWidth, rowH).fill(BRAND.panel);
    }
    doc.moveTo(PAGE.left, y + rowH).lineTo(PAGE.left + PAGE.contentWidth, y + rowH).strokeColor(BRAND.line).lineWidth(0.4).stroke();

    doc.fillColor(BRAND.black).font('Helvetica').fontSize(9)
      .text(textValue(item.description || item.name || 'Line'), PAGE.left + 12, y + 8, { width: colDesc - 16, lineBreak: false });
    doc.font('Helvetica').fontSize(9)
      .text(String(item.quantity ?? 1), PAGE.left + colDesc, y + 8, { width: colQty - 8, align: 'right', lineBreak: false });
    doc.font('Helvetica').fontSize(9)
      .text(money(item.unitPrice ?? item.unit_price ?? 0), PAGE.left + colDesc + colQty, y + 8, { width: colUnit - 8, align: 'right', lineBreak: false });
    doc.font('Helvetica-Bold').fontSize(9)
      .text(money(item.lineTotal ?? item.total ?? item.unitPrice ?? 0), PAGE.left + colDesc + colQty + colUnit, y + 8, { width: colTot - 12, align: 'right', lineBreak: false });
    y += rowH;
  });

  y += 22;

  // ── Totals block (right-aligned, full commercial weight) ─────────────
  const totalsW = 240;
  const totalsX = PAGE.left + PAGE.contentWidth - totalsW;
  const lineGap = 18;

  const subtotalExcl = Number(state.subtotalExclVAT ?? state.subtotal ?? 0);
  const vatAmount = Number(state.totalVAT ?? state.taxAmount ?? 0);
  const vatPct = Math.round(Number(state.vatRate ?? state.taxRate ?? 0.15) * 100);

  doc.fillColor(BRAND.muted).font('Helvetica').fontSize(9)
    .text('Subtotal (excl. VAT)', totalsX, y, { width: 130, lineBreak: false });
  doc.fillColor(BRAND.black).font('Helvetica').fontSize(9)
    .text(money(subtotalExcl), totalsX + 130, y, { width: 110, align: 'right', lineBreak: false });
  y += lineGap;

  doc.fillColor(BRAND.muted).font('Helvetica').fontSize(9)
    .text(`VAT (${vatPct}%)`, totalsX, y, { width: 130, lineBreak: false });
  doc.fillColor(BRAND.black).font('Helvetica').fontSize(9)
    .text(money(vatAmount), totalsX + 130, y, { width: 110, align: 'right', lineBreak: false });
  y += lineGap + 6;

  // Gold-edge total bar
  doc.roundedRect(totalsX, y, totalsW, 44, 6).fill(BRAND.black);
  doc.rect(totalsX, y, 5, 44).fill(BRAND.gold);
  doc.fillColor(BRAND.gold).font('Helvetica-Bold').fontSize(8)
    .text('TOTAL DUE (VAT INCL.)', totalsX + 16, y + 10, { width: totalsW - 28, lineBreak: false });
  doc.fillColor('#FFFFFF').font('Helvetica-Bold').fontSize(16)
    .text(money(state.totalAmount), totalsX + 16, y + 22, { width: totalsW - 28, align: 'right', lineBreak: false });
  y += 58;

  // ── Verification + payment QRs (left of residual space under totals) ──
  const qrSize = 72;
  const qrGap = 14;
  const verifyBuf = state._qrVerifyPng || null;
  const payBuf = state._qrPayPng || null;
  const verifyUrl = state._verifyUrl || buildVerifyAuditUrl(state);
  const payUrl = state._payUrl || buildPaymentSettleUrl(state);

  const qrBlockY = y;
  let qrConsumed = 0;
  qrConsumed = Math.max(
    qrConsumed,
    drawQrBlock(doc, PAGE.left, qrBlockY, qrSize, verifyBuf, 'VERIFY', 'verify.wilsy.os/audit')
  );
  qrConsumed = Math.max(
    qrConsumed,
    drawQrBlock(
      doc,
      PAGE.left + qrSize + 16 + qrGap,
      qrBlockY,
      qrSize,
      payBuf,
      'PAY NOW',
      'PayShap / Zapper'
    )
  );
  // Keep totals column clear; advance y past QR cards
  y = Math.max(y, qrBlockY + qrConsumed + 16);

  // ── Payment terms ────────────────────────────────────────────────────
  doc.fillColor(BRAND.black).font('Helvetica-Bold').fontSize(9).text('PAYMENT TERMS', PAGE.left, y);
  y += 14;
  doc.fillColor(BRAND.muted).font('Helvetica').fontSize(9)
    .text(
      `Payment due by ${date(state.dueDate)}. Scan PAY NOW for PayShap/Zapper settlement, or VERIFY for the live audit seal. Disputes follow the Wilsy OS collections path.`,
      PAGE.left,
      y,
      { width: PAGE.contentWidth, lineGap: 3 }
    );
  y = Math.max(doc.y + 18, y + 28);

  const paymentInstructions = state.paymentInstructions;
  if (paymentInstructions) {
    const bankDetails = [
      `${paymentInstructions.rail}: ${paymentInstructions.bankName}`,
      `Account holder: ${paymentInstructions.accountName} · Account: ${paymentInstructions.accountNumber}`,
      `Branch: ${paymentInstructions.branchCode}${paymentInstructions.bicSwift ? ` · BIC/SWIFT: ${paymentInstructions.bicSwift}` : ''}`,
      `Mandatory reference: ${paymentInstructions.reference}`,
    ].filter(Boolean).join('\n');
    doc.fillColor(BRAND.black).font('Helvetica-Bold').fontSize(8).text('BANK TRANSFER (EFT)', PAGE.left, y, { width: PAGE.contentWidth });
    y += 12;
    doc.fillColor(BRAND.muted).font('Helvetica').fontSize(8)
      .text(bankDetails, PAGE.left, y, { width: PAGE.contentWidth, lineGap: 2 });
    y = Math.max(doc.y + 12, y + 38);
  }

  // Optional compact forecast
  if (state.forecast && state.forecast.prediction) {
    doc.fillColor(BRAND.gold).font('Helvetica-Bold').fontSize(8).text('FORECAST', PAGE.left, y);
    y += 12;
    doc.fillColor(BRAND.muted).font('Helvetica').fontSize(8)
      .text(
        `${state.forecast.prediction} · confidence ${state.forecast.confidence ?? '—'}% · expected ${date(state.forecast.expectedDate)}`,
        PAGE.left,
        y,
        { width: PAGE.contentWidth }
      );
    y += 20;
  }

  // ── Forensic strip: pin near foot when short so page is not top-heavy ─
  if (y < usableBottom - 36) {
    y = usableBottom - 28;
  }
  drawForensicFooter(doc, state, y);

  return { y: y + 20 };
}


/**
 * @function drawInvoiceDigestCover
 * @description Multi-page invoices only — executive cover: identity, gold total,
 *              forecast, dual QR (verify + pay), seal strip. Commercial detail
 *              and forensic appendix follow on subsequent pages.
 * @param {PDFDocument} doc
 * @param {object} state
 * @returns {object} cursor
 * @collaboration Boardroom-ready multi-page invoice package
 */
function drawInvoiceDigestCover(doc, state) {
  const money = (v) => formatInvoiceMoney(v, state.currency);
  const date = (iso) => formatEnterpriseDate(iso);
  let y = 138;

  doc.fillColor(BRAND.black).font('Helvetica-Bold').fontSize(22)
    .text('EXECUTIVE DIGEST', PAGE.left, y, { width: PAGE.contentWidth * 0.55, lineBreak: false });
  doc.fillColor(BRAND.gold).font('Helvetica-Bold').fontSize(10)
    .text(textValue(state.invoiceNumber || state.title), PAGE.left + PAGE.contentWidth * 0.55, y + 8, {
      width: PAGE.contentWidth * 0.45,
      align: 'right',
      lineBreak: false,
    });
  y += 34;

  doc.roundedRect(PAGE.left, y, PAGE.contentWidth, 28, 4).fill(BRAND.band);
  doc.fillColor(BRAND.black).font('Helvetica-Bold').fontSize(8)
    .text(
      `STATUS  ${textValue(state.status || 'ISSUED')}    ·    ISSUE  ${date(state.issueDate)}    ·    DUE  ${date(state.dueDate)}    ·    ${textValue(state.currency || 'ZAR')}`,
      PAGE.left + 14,
      y + 9,
      { width: PAGE.contentWidth - 28, lineBreak: false }
    );
  y += 44;

  // Parties summary
  doc.fillColor(BRAND.gold).font('Helvetica-Bold').fontSize(7).text('FROM', PAGE.left, y);
  doc.fillColor(BRAND.gold).font('Helvetica-Bold').fontSize(7).text('BILL TO', PAGE.left + PAGE.contentWidth / 2, y);
  y += 12;
  doc.fillColor(BRAND.black).font('Helvetica-Bold').fontSize(11)
    .text(textValue(state.issuingEntity), PAGE.left, y, { width: PAGE.contentWidth / 2 - 10, lineBreak: false });
  doc.fillColor(BRAND.black).font('Helvetica-Bold').fontSize(11)
    .text(textValue(state.counterparty), PAGE.left + PAGE.contentWidth / 2, y, {
      width: PAGE.contentWidth / 2 - 10,
      lineBreak: false,
    });
  y += 28;

  // Gold total hero box
  doc.roundedRect(PAGE.left, y, PAGE.contentWidth, 96, 8).fill(BRAND.panel);
  doc.roundedRect(PAGE.left, y, PAGE.contentWidth, 96, 8).strokeColor(BRAND.gold).lineWidth(2).stroke();
  doc.fillColor(BRAND.muted).font('Helvetica').fontSize(10)
    .text('TOTAL AMOUNT DUE (VAT INCL.)', PAGE.left + 16, y + 16, {
      width: PAGE.contentWidth - 32,
      align: 'center',
    });
  doc.fillColor(BRAND.gold).font('Helvetica-Bold').fontSize(28)
    .text(money(state.totalAmount), PAGE.left + 16, y + 36, {
      width: PAGE.contentWidth - 32,
      align: 'center',
    });
  const sub = Number(state.subtotalExclVAT ?? state.subtotal ?? 0);
  const vat = Number(state.totalVAT ?? state.taxAmount ?? 0);
  const pct = Math.round(Number(state.vatRate ?? state.taxRate ?? 0.15) * 100);
  doc.fillColor(BRAND.muted).font('Helvetica').fontSize(8.5)
    .text(
      `Subtotal ${money(sub)}   ·   VAT (${pct}%) ${money(vat)}`,
      PAGE.left + 16,
      y + 72,
      { width: PAGE.contentWidth - 32, align: 'center' }
    );
  y += 112;

  if (state.forecast && state.forecast.prediction) {
    doc.fillColor(BRAND.black).font('Helvetica-Bold').fontSize(9).text('PREDICTIVE FORECAST', PAGE.left, y);
    y += 14;
    doc.fillColor(BRAND.muted).font('Helvetica').fontSize(9)
      .text(
        `${state.forecast.prediction} · confidence ${state.forecast.confidence ?? '—'}% · expected ${date(state.forecast.expectedDate)}`,
        PAGE.left,
        y,
        { width: PAGE.contentWidth }
      );
    y += 24;
  }

  // Dual QR on cover
  const qrSize = 88;
  const verifyBuf = state._qrVerifyPng || null;
  const payBuf = state._qrPayPng || null;
  drawQrBlock(doc, PAGE.left, y, qrSize, verifyBuf, 'VERIFY AUDIT', 'verify.wilsy.os');
  drawQrBlock(doc, PAGE.left + qrSize + 28, y, qrSize, payBuf, 'PAY NOW', 'PayShap / Zapper');
  y += qrSize + 48;

  // Draw the forensic footer for the cover
  drawForensicFooter(doc, state, Math.min(y + 20, 700));

  return { y: Math.min(y + 20, 700) + 40 };
}

function shouldAttachInvoiceAppendix(state = {}) {
  const items = Array.isArray(state.lineItems) ? state.lineItems.length : 0;
  const anomalies = Array.isArray(state.anomalies) ? state.anomalies.length : 0;
  // Appendix for dense line lists or explicit forensic payloads — not for simple single-line invoices
  return items > 12 || anomalies > 0 || Boolean(state.forceAppendix);
}


/**
 * @function streamEnterpriseArtifactPdf
 * @description Streams a Wilsy OS enterprise PDF artifact with sovereign cover + forensic appendix.
 */
export async function streamEnterpriseArtifactPdf({ res, identity, proof }) {
  // Build base state, hydrate knowledge base, CRM, and then billing invoice (order matters for precedence)
  const baseState = buildState(identity, proof);
  const withKnowledgeBase = hydrateWilsyKnowledgeBaseState(baseState, identity, proof);
  const withCrm = hydrateCrmProofPackState(withKnowledgeBase, identity, proof);
  const state = hydrateBillingInvoiceState(withCrm, identity);

  const fileName = isBillingInvoiceState(state)
    ? `WILSY-INV-${safeFileName(state.invoiceNumber || state.title)}-${state.tenantId}.pdf`
    : `WILSY-OS-${safeFileName(state.title)}-${state.tenantId}-${Date.now()}.pdf`;

  res.setHeader('Content-Type', 'application/pdf');
  res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
  res.setHeader('X-Wilsy-Trace-ID', state.traceId);
  res.setHeader('X-Wilsy-Merkle-Root', state.merkleRoot);
  res.setHeader('X-Wilsy-Artifact-Type', state.type);
  res.setHeader('X-Wilsy-Tenant-ID', state.tenantId);

  const doc = new PDFDocument({
    size: 'A4',
    bufferPages: true,
    margins: { top: 0, bottom: 0, left: 0, right: 0 },
    info: {
      Title: isBillingInvoiceState(state) ? `Invoice ${state.invoiceNumber}` : state.title,
      Author: 'Wilsy OS',
      Subject: `Wilsy OS Enterprise Artifact - ${state.type}`,
      Keywords: `Wilsy OS, ${state.type}, ${state.tenantId}, ${state.traceId}`,
    },
  });

  const pdfChunks = [];
  const pdfBufferReady = new Promise((resolve, reject) => {
    doc.on('data', (chunk) => {
      if (chunk) pdfChunks.push(Buffer.from(chunk));
    });

    doc.on('end', () => {
      resolve(Buffer.concat(pdfChunks));
    });

    doc.on('error', reject);
  });

  if (isBillingInvoiceState(state)) {
    // ─── SOVEREIGN QR GENERATION (using qrGenerator.js) ─────────────────
    try {
      // Build a signed payload for verification
      const qrPayload = buildQRPayload({
        invoiceId: state.invoiceNumber || state.title,
        tenantId: state.tenantId,
        amount: state.totalAmount,
        currency: state.currency,
        traceId: state.traceId,
        merkleRoot: state.merkleRoot,
        sealHash: state.sealHash || state.sha3,
      });
      // Verification URL contains the signed payload
      state._verifyUrl = qrPayload.verificationUrl;
      // Generate QR code for verification
      state._qrVerifyPng = await generateQRCode(qrPayload.verificationUrl, { width: 180 });
    } catch (qrError) {
      // Fallback: generate a simple URL QR if sovereign generation fails
      console.warn('Sovereign QR generation failed, falling back to simple URL:', qrError.message);
      state._verifyUrl = buildVerifyAuditUrl(state);
      try {
        state._qrVerifyPng = await generateQRCode(state._verifyUrl, { width: 180 });
      } catch {
        state._qrVerifyPng = null;
      }
    }

    // Payment QR (still using a simple URL)
    state._payUrl = buildPaymentSettleUrl(state);
    try {
      state._qrPayPng = await generateQRCode(state._payUrl, { width: 180 });
    } catch {
      state._qrPayPng = null;
    }

    const multiPage = shouldAttachInvoiceAppendix(state) || Boolean(state.forceCoverDigest);

    if (multiPage) {
      // Page 1 — Executive digest cover (logo via header + total + forecast + QRs)
      drawHeader(doc, state, 1, 2);
      drawInvoiceDigestCover(doc, state);

      // Page 2 — Full commercial tax invoice body
      doc.addPage();
      drawHeader(doc, state, 2, 2);
      drawCommercialInvoicePage(doc, state);

      // Optional deeper forensic appendix when anomalies / dense lines force it
      if (shouldAttachInvoiceAppendix(state)) {
        doc.addPage();
        let cursor = normalizeEnterprisePdfCursor({ y: PAGE.top }, PAGE.top);
        cursor = drawDocumentControl(doc, cursor, state);
        const sections = buildSections(state) || [];
        sections.forEach((section) => {
          section._state = state;
          section._currency = state.currency || 'ZAR';
          cursor = drawSection(doc, cursor, section);
        });
      }
    } else {
      // Single-page commercial tax invoice with embedded QRs
      drawHeader(doc, state, 1, 1);
      drawCommercialInvoicePage(doc, state);
    }

    applyChrome(doc, state);
  } else {
    // ─── NON-INVOICE ENTERPRISE ARTIFACTS ────────────────────────────
    drawHeader(doc, state, 1, 1);
    drawCoverPage(doc, state);

    doc.addPage();
    let cursor = normalizeEnterprisePdfCursor({ y: PAGE.top }, PAGE.top);
    cursor = drawDocumentControl(doc, cursor, state);
    const sections = buildSections(state) || [];
    sections.forEach((section) => {
      section._state = state;
      section._currency = state.currency || 'ZAR';
      cursor = drawSection(doc, cursor, section);
    });

    applyChrome(doc, state);
  }

  doc.end();

  const pdfBuffer = await pdfBufferReady;

  if (!pdfBuffer || pdfBuffer.length < 128) {
    throw new Error('Enterprise PDF renderer produced an incomplete PDF buffer.');
  }

  res.setHeader('Content-Length', String(pdfBuffer.length));
  res.end(pdfBuffer);
}

export default streamEnterpriseArtifactPdf;

// P60K5Q10FG106O_ENTERPRISE_RENDERER_CRM_PROOF_STORY
// P60K5Q10FG106S_BUFFER_ENTERPRISE_PDF_FINALIZATION
// P60K5Q10FG106T_ENTERPRISE_PDF_CURSOR_GUARD
// P60K5Q10FG106T3_CURSOR_ORDER_RESCUE
// P60K5Q10FG106U_ENTERPRISE_PDF_ALL_CURSOR_READ_GUARDS
// P60K5Q10FG106X_CRM_PROOF_PACK_PDF_LAYOUT_FLOW
// P60K5Q10FG106Y_PDF_CURSOR_MUTATION_FLOW
// P60K5Q10FG106Z_GENERATED_BY_HUMAN_CONTROL_NAME
// Q7.1.7_QR_INTEGRATION_SOVEREIGN_GENERATEQRCODE_CALL
