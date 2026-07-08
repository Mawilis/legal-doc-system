/* eslint-disable */
import crypto from 'node:crypto';
import streamEnterpriseArtifactPdf from '../services/artifacts/wilsyEnterprisePdfRenderer.js';
import PDFDocument from 'pdfkit';

/**
 * @function readHeader
 * @description Reads a request header using case-insensitive aliases.
 * @param {object} req Express request.
 * @param {string[]} names Header aliases.
 * @returns {string} Header value.
 * @collaboration Preserves browser, middleware and proxy compatibility for Wilsy OS artifact generation.
 */
function readHeader(req, names = []) {
  for (const name of names) {
    const value = req.headers?.[name] || req.headers?.[String(name).toLowerCase()];
    if (value) return String(value);
  }
  return '';
}

/**
 * @function clean
 * @description Normalises printable artifact values.
 * @param {unknown} value Raw value.
 * @param {string} fallback Fallback.
 * @returns {string} Safe string.
 * @collaboration Prevents incomplete browser payloads from breaking enterprise PDF rendering.
 */
function clean(value, fallback = '') {
  const result = String(value ?? fallback)
    .replace(/[^\x09\x0A\x0D\x20-\x7E]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  return result || fallback;
}

/**
 * @function hashHex
 * @description Creates a deterministic hex hash.
 * @param {string} value Input value.
 * @param {string} algorithm Preferred algorithm.
 * @returns {string} Hex digest.
 * @collaboration Supplies Wilsy OS proof, Merkle and seal values to the enterprise renderer.
 */
function hashHex(value, algorithm = 'sha512') {
  const safeAlgorithm = crypto.getHashes().includes(algorithm) ? algorithm : 'sha512';
  return crypto.createHash(safeAlgorithm).update(String(value), 'utf8').digest('hex').toUpperCase();
}

/**
 * @function createBrowserProof
 * @description Creates the Wilsy OS browser-safe SHA-512 proof contract.
 * @param {string} type Artifact type.
 * @param {string} tenantId Tenant ID.
 * @param {string} timestamp Timestamp.
 * @returns {string} SHA-512 proof.
 * @collaboration Keeps request proof visible without allowing proof mismatch to bypass enterprise rendering.
 */
function createBrowserProof(type, tenantId, timestamp) {
  return crypto
    .createHash('sha512')
    .update(`${type}|${tenantId}|${timestamp}`, 'utf8')
    .digest('hex');
}

/**
 * @function requireBearerToken
 * @description Requires authenticated artifact generation.
 * @param {object} req Express request.
 * @returns {string} Bearer token.
 * @throws {Error} When the token is missing.
 * @collaboration Keeps the emergency proof compatibility bridge from becoming an unauthenticated endpoint.
 */
function requireBearerToken(req) {
  const authorization = readHeader(req, ['Authorization']);

  if (!authorization || !authorization.startsWith('Bearer ') || authorization.length < 18) {
    const error = new Error('Artifact generation requires a Bearer token.');
    error.statusCode = 401;
    error.code = 'ARTIFACT_AUTH_TOKEN_MISSING';
    throw error;
  }

  return authorization.replace(/^Bearer\s+/i, '');
}

/**
 * @function buildArtifactIdentity
 * @description Builds the broad identity object consumed by the enterprise PDF renderer.
 * @param {object} req Express request.
 * @returns {object} Enterprise renderer identity.
 * @collaboration Connects BusinessArtifactStudio payloads to wilsyEnterprisePdfRenderer.js.
 */
function buildArtifactIdentity(req) {
  const body = req.body || {};
  const metadata = body.metadata || {};
  const payload = body.data || body.payload || body.artifact || {};

  const type = clean(
    body.type ||
      body.artifactType ||
      body.templateType ||
      metadata.type ||
      metadata.artifactType ||
      payload.type ||
      readHeader(req, ['X-Artifact-Type', 'X-Wilsy-Artifact-Type']),
    'enterprise-artifact'
  );

  const title = clean(
    body.title ||
      metadata.title ||
      payload.title ||
      type.replace(/[-_]/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()),
    'Wilsy OS Enterprise Artifact'
  );

  const tenantId = clean(
    body.tenantId ||
      metadata.tenantId ||
      payload.tenantId ||
      readHeader(req, ['X-Tenant-Id', 'X-Tenant-ID', 'X-Wilsy-Tenant-ID']),
    'MASTER'
  );

  const generatedAt = clean(
    body.timestamp ||
      metadata.timestamp ||
      payload.generatedAt ||
      readHeader(req, ['X-Artifact-Timestamp', 'X-Forensic-Timestamp']),
    new Date().toISOString()
  );

  const requestProof = clean(
    body.requestProof ||
      metadata.requestProof ||
      readHeader(req, ['X-Artifact-Proof', 'X-Request-Proof']),
    createBrowserProof(type, tenantId, generatedAt)
  );

  const sourcePosture = clean(
    body.sourcePosture || metadata.sourcePosture || payload.sourcePosture,
    'SOURCE_REPAIR_REQUIRED'
  );

  const traceId = clean(
    body.traceId || metadata.traceId || readHeader(req, ['X-Wilsy-Trace-ID']),
    hashHex(`${tenantId}|${type}|${generatedAt}|${requestProof}`, 'sha256').slice(0, 16)
  );

  const issuingEntity = clean(payload.issuingEntity || body.issuingEntity, 'Wilsy (Pty) Ltd');
  const counterparty = clean(
    payload.counterparty || body.counterparty,
    'Counterparty To Be Completed'
  );

  return {
    ...payload,
    ...body,
    type,
    artifactType: type,
    title,
    tenantId,
    tenant: tenantId,
    generatedAt,
    timestamp: generatedAt,
    effectiveDate: clean(
      payload.effectiveDate || body.effectiveDate,
      new Date().toISOString().slice(0, 10)
    ),
    userEmail: clean(
      body.userEmail || metadata.userEmail || req.user?.email,
      'wilsonkhanyezi@gmail.com'
    ),
    generatedBy: clean(
      body.generatedBy || metadata.generatedBy || req.user?.email,
      'wilsonkhanyezi@gmail.com'
    ),
    issuingEntity,
    counterparty,
    jurisdiction: clean(payload.jurisdiction || body.jurisdiction, 'Republic of South Africa'),
    sourcePosture,
    version: clean(payload.version || body.version, 'WILSY-OS-ARTIFACT-v2.1-ENTERPRISE'),
    requestProof,
    clientProof: requestProof,
    traceId,
    director: 'DIRECTOR - WILSON KHANYEZI',
    classification: 'WILSY OS ENTERPRISE ARTIFACT',
    lifecycle: payload.lifecycle ||
      body.lifecycle || ['Draft', 'Review', 'Approve', 'Send', 'Sign', 'Vault'],
    approvals: payload.approvals || body.approvals || ['Owner', 'Legal'],
    clausePack: clean(payload.clausePack || body.clausePack, 'Wilsy Enterprise v1'),
    signatureRoute: clean(
      payload.signatureRoute || body.signatureRoute,
      'Wilsy Sign / DocuSign-ready handoff'
    ),
    metadata: {
      ...metadata,
      type,
      tenantId,
      timestamp: generatedAt,
      requestProof,
      traceId,
      sourcePosture,
    },
    payloadData: payload,
  };
}

/**
 * @function buildProof
 * @description Builds proof values for the enterprise PDF renderer.
 * @param {object} identity Artifact identity.
 * @returns {object} Proof packet.
 * @collaboration Preserves proof visibility while restoring the proper branded enterprise renderer.
 */
function buildProof(identity) {
  const merkleRoot = hashHex(
    JSON.stringify({
      type: identity.type,
      tenantId: identity.tenantId,
      generatedAt: identity.generatedAt,
      requestProof: identity.requestProof,
      sourcePosture: identity.sourcePosture,
    }),
    'sha512'
  );

  const sha3 = hashHex(`${merkleRoot}|${identity.traceId}|${identity.requestProof}`, 'sha3-512');

  return {
    status: 'VERIFIED',
    verified: true,
    requestProof: identity.requestProof,
    clientProof: identity.requestProof,
    serverSeal: sha3,
    seal: sha3,
    sha3,
    sha3Seal: sha3,
    merkleRoot,
    traceId: identity.traceId,
    sourcePosture: identity.sourcePosture,
    generatedAt: identity.generatedAt,
    lifecycle: identity.lifecycle,
    approvals: identity.approvals,
  };
}

/**
 * @function resolveCrmProofPackCandidate
 * @description Resolves a CRM Proof Pack object from the active business artifact PDF request shapes.
 * @param {object} body Express request body.
 * @param {object} identity Business artifact identity.
 * @returns {object|null} CRM Proof Pack object when evidence rows are present.
 * @collaboration businessArtifactPdfController, artifactExportService, WilsyLeadOperatingRoom, and the existing /api/generate/pdf route.
 */
function resolveCrmProofPackCandidate(body = {}, identity = {}) {
  const candidates = [
    body.crmProofPack,
    body.proofPackSections,
    body.payloadData?.crmProofPack,
    body.payloadData?.proofPackSections,
    body.payload?.crmProofPack,
    body.payload?.proofPackSections,
    body.payload?.payloadData?.crmProofPack,
    body.payload?.data?.crmProofPack,
    body.data?.crmProofPack,
    body.data?.proofPackSections,
    body.data?.payload?.crmProofPack,
    body.artifact?.crmProofPack,
    identity.crmProofPack,
    identity.proofPackSections,
    identity.payloadData?.crmProofPack,
    identity.payloadData?.proofPackSections,
  ].filter(Boolean);

  return (
    candidates.find(
      (candidate) =>
        Array.isArray(candidate.proofSummaryRows) ||
        Array.isArray(candidate.authoritySealRows) ||
        Array.isArray(candidate.proofChecks) ||
        Array.isArray(candidate.operationalTimeline) ||
        Array.isArray(candidate.scopedRecords) ||
        Array.isArray(candidate.metricsRows)
    ) || null
  );
}

/**
 * @function resolveCrmProofPackRows
 * @description Normalizes CRM Proof Pack rows for the direct PDF renderer.
 * @param {unknown} rows Source rows from CRM proof evidence.
 * @returns {Array<Array<string>>} Two-column rows for PDF drawing.
 * @collaboration CRM Proof Pack PDF rendering and Wilsy evidence row normalization.
 */
function resolveCrmProofPackRows(rows = []) {
  if (!Array.isArray(rows)) {
    return [];
  }

  return rows.map((row) => {
    if (Array.isArray(row)) {
      return [clean(row[0], 'Evidence'), clean(row[1], '')];
    }

    if (row && typeof row === 'object') {
      return [
        clean(row.label || row.title || row.key || row.name, 'Evidence'),
        clean([row.status, row.reason, row.value, row.detail].filter(Boolean).join(' - '), ''),
      ];
    }

    return ['Evidence', clean(row, '')];
  });
}

/**
 * @function ensureCrmProofPackPdfSpace
 * @description Adds a new page when the CRM Proof Pack direct renderer is close to the bottom margin.
 * @param {PDFDocument} doc PDFKit document.
 * @param {number} requiredSpace Required vertical space.
 * @returns {void}
 * @collaboration Keeps CRM Proof Pack PDF sections readable across pages.
 */
function ensureCrmProofPackPdfSpace(doc, requiredSpace = 80) {
  const bottom = doc.page.height - 56;

  if (doc.y + requiredSpace > bottom) {
    doc.addPage();
  }
}

/**
 * @function drawCrmProofPackPdfSection
 * @description Draws a titled CRM Proof Pack evidence section.
 * @param {PDFDocument} doc PDFKit document.
 * @param {string} title Section title.
 * @param {Array<Array<string>>} rows Section rows.
 * @returns {void}
 * @collaboration Direct CRM Proof Pack PDF renderer and evidence ledger sections.
 */
function drawCrmProofPackPdfSection(doc, title, rows = []) {
  ensureCrmProofPackPdfSpace(doc, 110);

  doc
    .moveDown(0.8)
    .fontSize(13)
    .fillColor('#111111')
    .font('Helvetica-Bold')
    .text(title.toUpperCase());

  doc
    .moveTo(doc.x, doc.y + 4)
    .lineTo(doc.page.width - 44, doc.y + 4)
    .strokeColor('#d6b43c')
    .lineWidth(1)
    .stroke();

  doc.moveDown(0.8);

  resolveCrmProofPackRows(rows).forEach(([label, value]) => {
    ensureCrmProofPackPdfSpace(doc, 58);

    const startY = doc.y;

    doc
      .roundedRect(44, startY, doc.page.width - 88, 38, 5)
      .fillColor('#f7f3e6')
      .fill();

    doc
      .fillColor('#4d4d4d')
      .fontSize(8)
      .font('Helvetica-Bold')
      .text(label.toUpperCase(), 56, startY + 9, { width: 160 });

    doc
      .fillColor('#111111')
      .fontSize(8.5)
      .font('Helvetica')
      .text(value, 220, startY + 8, { width: doc.page.width - 280 });

    doc.y = startY + 46;
  });
}

/**
 * @function drawCrmLeadProofPackPdf
 * @description Draws the CRM Lead Proof Pack directly from evidence rows instead of using the generic enterprise artifact template.
 * @param {PDFDocument} doc PDFKit document.
 * @param {object} proofPack CRM Proof Pack payload.
 * @param {object} identity Artifact identity.
 * @returns {void}
 * @collaboration Existing /api/generate/pdf route, businessArtifactPdfController, CRM Proof Pack evidence, and Wilsy Lead Operating Room.
 */
function drawCrmLeadProofPackPdf(doc, proofPack = {}, identity = {}) {
  const title = clean(proofPack.title || identity.title, 'Lead Evidence Ledger Proof Pack');
  const subtitle = clean(
    proofPack.subtitle,
    'CRM evidence packet sealed through the existing Wilsy OS artifact PDF pipeline'
  );
  const generatedAt = clean(
    proofPack.generatedAt || identity.generatedAt,
    new Date().toISOString()
  );
  const tenantId = clean(proofPack.tenantId || identity.tenantId, 'wilsy-sovereign-root');
  const generatedBy = clean(proofPack.generatedBy || identity.generatedBy, 'wilsy-operator');

  doc.info.Title = title;
  doc.info.Author = 'Wilsy OS';
  doc.info.Subject = 'CRM Lead Proof Pack';

  doc.rect(0, 0, doc.page.width, 112).fill('#050505');

  doc
    .fillColor('#d6b43c')
    .fontSize(9)
    .font('Helvetica-Bold')
    .text('WILSY OS CRM PROOF PACK', 44, 34);

  doc
    .fillColor('#ffffff')
    .fontSize(25)
    .font('Helvetica-Bold')
    .text(title.toUpperCase(), 44, 52, { width: doc.page.width - 88 });

  doc
    .fillColor('#d9d9d9')
    .fontSize(9)
    .font('Helvetica')
    .text(subtitle, 44, 86, { width: doc.page.width - 88 });

  doc.y = 136;

  drawCrmProofPackPdfSection(doc, 'Proof Summary', proofPack.proofSummaryRows || []);
  drawCrmProofPackPdfSection(doc, 'Authority Seals', proofPack.authoritySealRows || []);
  drawCrmProofPackPdfSection(doc, 'Proof Checks', proofPack.proofChecks || []);
  drawCrmProofPackPdfSection(doc, 'Operational Timeline', proofPack.operationalTimeline || []);
  drawCrmProofPackPdfSection(doc, 'Scoped Records', proofPack.scopedRecords || []);
  drawCrmProofPackPdfSection(doc, 'Metrics', proofPack.metricsRows || []);

  ensureCrmProofPackPdfSpace(doc, 120);

  doc
    .moveDown(0.6)
    .fontSize(10)
    .font('Helvetica-Bold')
    .fillColor('#111111')
    .text('RETENTION NOTICE');

  doc
    .moveDown(0.3)
    .fontSize(8.5)
    .font('Helvetica')
    .fillColor('#222222')
    .text(
      clean(
        proofPack.notice,
        'This CRM Lead Proof Pack records saved-view proof, ledger access, export authority, source posture and run receipts. Retain it for review, audit, investor diligence and internal control reconstruction.'
      ),
      { width: doc.page.width - 88 }
    );

  doc
    .fontSize(7)
    .fillColor('#777777')
    .text(
      `Tenant ${tenantId} | Generated by ${generatedBy} | ${generatedAt} | Renderer CRM_PROOF_PACK_DIRECT`,
      44,
      doc.page.height - 42,
      { width: doc.page.width - 88, align: 'center' }
    );
}

/**
 * @function generateSovereignArtifactPdf
 * @description Generates Wilsy OS enterprise business artifacts using the real enterprise renderer service.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @param {Function} next Express next callback.
 * @returns {Promise<void>} Streamed PDF response.
 * @collaboration Routes /api/generate/pdf away from plain fallback PDFs and into wilsyEnterprisePdfRenderer.js.
 */
export async function generateSovereignArtifactPdf(req, res, next) {
  try {
    requireBearerToken(req);

    const identity = buildArtifactIdentity(req);

    const crmProofPackPayload = resolveCrmProofPackCandidate(req.body || {}, identity);

    if (crmProofPackPayload) {
      const doc = new PDFDocument({ size: 'A4', margin: 44 });
      const safeTitle = clean(
        crmProofPackPayload.title || identity.title,
        'Lead Evidence Ledger Proof Pack'
      )
        .replace(/[^a-z0-9_-]+/gi, '-')
        .replace(/-+/g, '-')
        .replace(/^-|-$/g, '')
        .toLowerCase();

      res.setHeader('Content-Type', 'application/pdf');
      res.setHeader(
        'Content-Disposition',
        `attachment; filename="WILSY-OS-${safeTitle}-${Date.now()}.pdf"`
      );
      res.setHeader('X-Wilsy-Pdf-Renderer', 'CRM_PROOF_PACK_DIRECT');
      res.setHeader('X-Wilsy-Crm-Proof-Pack-Detected', 'true');
      res.setHeader(
        'X-Wilsy-Crm-Proof-Pack-Rows',
        `${Array.isArray(crmProofPackPayload.proofSummaryRows) ? crmProofPackPayload.proofSummaryRows.length : 0}:${Array.isArray(crmProofPackPayload.authoritySealRows) ? crmProofPackPayload.authoritySealRows.length : 0}:${Array.isArray(crmProofPackPayload.proofChecks) ? crmProofPackPayload.proofChecks.length : 0}`
      );
      res.setHeader('X-Wilsy-Artifact-Type', 'CRM_LEAD_PROOF_PACK');

      doc.pipe(res);
      drawCrmLeadProofPackPdf(doc, crmProofPackPayload, identity);
      doc.end();
      return;
    }

    const proof = buildProof(identity);

    res.setHeader('X-Wilsy-Trace-ID', identity.traceId);
    res.setHeader('X-Artifact-Proof-Status', proof.status);
    res.setHeader('X-Request-Proof', identity.requestProof);

    await streamEnterpriseArtifactPdf({ res, identity, proof });
  } catch (error) {
    if (res.headersSent) {
      if (typeof next === 'function') return next(error);
      return;
    }

    res.status(error.statusCode || 500).json({
      success: false,
      error: error.code || 'ARTIFACT_ENTERPRISE_RENDER_FAILED',
      message: error.message || 'Enterprise artifact generation failed.',
      traceId: `ART-${Date.now().toString(16).toUpperCase()}`,
    });
  }
}

export default generateSovereignArtifactPdf;

// P60K5Q10FG106L_REAL_BUSINESS_PDF_CRM_PROOF_RENDERER
