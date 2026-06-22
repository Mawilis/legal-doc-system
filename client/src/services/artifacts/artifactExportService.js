/* eslint-disable */
import {
  AlignmentType,
  Document,
  HeadingLevel,
  ImageRun,
  Packer,
  Paragraph,
  Table,
  TableCell,
  TableRow,
  TextRun,
  WidthType
} from 'docx';
import wilsyDocxLogoUrl from '../../assets/logo/wilsy.jpeg';

const DOCX_MIME = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
const PDF_ENDPOINT = '/api/generate/pdf';

/**
 * @function normaliseType
 * @description Normalizes artifact type values for proof and filename contracts.
 * @param {string} value - Raw artifact type.
 * @returns {string} Normalized artifact type.
 * @collaboration Keeps exports aligned across PDF, DOCX, JSON and SEND PACK.
 */
function normaliseType(value = 'artifact') {
  return String(value || 'artifact').trim().toLowerCase().replace(/_/g, '-').replace(/[^a-z0-9-]+/g, '-');
}

/**
 * @function safeFileName
 * @description Converts artifact titles into safe filenames.
 * @param {string} value - Raw filename.
 * @returns {string} Safe filename.
 * @collaboration Prevents broken local downloads and inconsistent attachment names.
 */
function safeFileName(value = 'artifact') {
  return String(value || 'artifact').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'artifact';
}

/**
 * @function sha512Hex
 * @description Creates a SHA-512 hex digest using browser crypto.
 * @param {string} value - Value to digest.
 * @returns {Promise<string>} Hex digest.
 * @collaboration Preserves Wilsy OS artifact proof verification.
 */
async function sha512Hex(value) {
  const buffer = await crypto.subtle.digest('SHA-512', new TextEncoder().encode(value));

  return Array.from(new Uint8Array(buffer)).map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

/**
 * @function getBrowserToken
 * @description Resolves the active Wilsy OS auth token from browser storage.
 * @returns {string} Token without Bearer prefix.
 * @collaboration Keeps protected artifact routes authenticated without hard-coding auth context internals.
 */
function getBrowserToken() {
  const keys = ['token', 'accessToken', 'wilsy_token', 'wilsyAuthToken', 'sovereignToken', 'authToken'];

  for (const key of keys) {
    const value = localStorage.getItem(key) || sessionStorage.getItem(key);
    if (value && value.length > 10) return value.replace(/^Bearer\s+/i, '');
  }

  return '';
}

/**
 * @function downloadBlob
 * @description Downloads a browser blob.
 * @param {Blob} blob - Blob to download.
 * @param {string} filename - Filename.
 * @returns {void}
 * @collaboration Provides a consistent delivery layer for all artifact outputs.
 */
function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');

  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();

  window.setTimeout(() => URL.revokeObjectURL(url), 1500);
}

/**
 * @function blobToBase64
 * @description Converts a blob into base64 for EML attachments.
 * @param {Blob} blob - Blob.
 * @returns {Promise<string>} Base64 value.
 * @collaboration Enables real SEND PACK attachments instead of mailto shortcuts.
 */
function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = () => {
      const value = String(reader.result || '');
      resolve(value.includes(',') ? value.split(',')[1] : value);
    };

    reader.onerror = () => reject(reader.error || new Error('Unable to read attachment blob.'));
    reader.readAsDataURL(blob);
  });
}

/**
 * @function wrapBase64
 * @description Wraps base64 for MIME email files.
 * @param {string} value - Base64 value.
 * @returns {string} Wrapped base64.
 * @collaboration Makes generated email packages more compatible with desktop mail clients.
 */
function wrapBase64(value) {
  return String(value || '').match(/.{1,76}/g)?.join('\r\n') || '';
}

/**
 * @function createPayload
 * @description Builds the common artifact payload.
 * @param {object} artifact - Artifact template.
 * @param {string} tenantId - Tenant identifier.
 * @param {object} tenantConfig - Tenant config.
 * @returns {object} Artifact payload.
 * @collaboration Gives every export the same readiness, approval, risk and signature context.
 */
function createPayload(artifact, tenantId, tenantConfig = {}) {
  return {
    title: artifact.title,
    type: normaliseType(artifact.type || artifact.id || artifact.title),
    tenantId,
    issuingEntity: tenantConfig?.companyName || tenantConfig?.name || 'Wilsy (Pty) Ltd',
    counterparty: 'Counterparty To Be Completed',
    readiness: artifact.readiness || 'Source-scored in Wilsy OS',
    risk: artifact.risk || 'STANDARD',
    approvals: artifact.approvals || ['Owner', 'Legal'],
    clausePack: artifact.clausePack || 'Wilsy Standard v1',
    lifecycle: ['Draft', 'Review', 'Approve', 'Send', 'Sign', 'Vault'],
    signatureRoute: 'Wilsy Sign / DocuSign-ready handoff',
    sourcePosture: 'SOURCE_REPAIR_REQUIRED',
    generatedAt: new Date().toISOString()
  };
}

/**
 * @function createPdfBlob
 * @description Generates a proof-sealed PDF through the backend artifact renderer.
 * @param {object} artifact - Artifact template.
 * @param {object} payload - Artifact payload.
 * @returns {Promise<Blob>} PDF blob.
 * @collaboration Keeps PDF generation on the branded Wilsy OS backend renderer.
 */
async function createPdfBlob(artifact, payload) {
  const type = payload.type;
  const tenantId = payload.tenantId;
  const timestamp = new Date().toISOString();
  const nonce = crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
  const proof = await sha512Hex(`${type}|${tenantId}|${timestamp}`);
  const token = getBrowserToken();

  const response = await fetch(PDF_ENDPOINT, {
    method: 'POST',
    credentials: 'include',
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      'Accept': 'application/pdf, application/json',
      'Content-Type': 'application/json',
      'X-Tenant-Id': tenantId,
      'X-Tenant-ID': tenantId,
      'X-Artifact-Type': type,
      'X-Request-Proof': proof,
      'X-Artifact-Proof': proof,
      'X-Forensic-Timestamp': timestamp,
      'X-Artifact-Timestamp': timestamp,
      'X-Cryptographic-Nonce': nonce
    },
    body: JSON.stringify({
      type,
      artifactType: type,
      title: artifact.title,
      tenantId,
      payload,
      data: payload,
      metadata: {
        type,
        artifactType: type,
        tenantId,
        timestamp,
        requestProof: proof,
        nonce,
        sourcePosture: payload.sourcePosture
      }
    })
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => `PDF generation failed: ${response.status}`);
    throw new Error(errorText || `PDF generation failed: ${response.status}`);
  }

  return response.blob();
}


/**
 * @function loadWilsyDocxLogoImage
 * @description Loads the Wilsy logo as a DOCX ImageRun.
 * @returns {Promise<ImageRun|null>} Logo image run or null fallback.
 * @collaboration Embeds the real Wilsy logo into DOCX exports without touching the PDF engine.
 */
async function loadWilsyDocxLogoImage() {
  try {
    const response = await fetch(wilsyDocxLogoUrl);
    const data = await response.arrayBuffer();

    return new ImageRun({
      data,
      transformation: {
        width: 92,
        height: 92
      }
    });
  } catch (error) {
    console.warn('[WILSY DOCX] Logo image could not be embedded. Falling back to text mark.', error);
    return null;
  }
}

/**
 * @function createDocxBlob
 * @description Creates and validates a real Microsoft Word OpenXML package.
 * @param {object} artifact - Artifact template.
 * @param {object} payload - Artifact payload.
 * @returns {Promise<Blob>} Valid DOCX blob.
 * @collaboration Stops invalid JSON-renamed DOCX files from leaving Wilsy OS.
 */

async function createDocxBlob(artifact, payload) {
  const value = (input, fallback = '') => String(input ?? fallback);
  const generatedAt = value(payload.generatedAt, new Date().toISOString());
  const wilsyLogoImage = await loadWilsyDocxLogoImage();
  const title = value(artifact.title, 'Wilsy OS Enterprise Artifact');
  const artifactType = value(payload.type, artifact.type || artifact.id || 'enterprise-artifact');
  const issuingEntity = value(payload.issuingEntity, 'Wilsy (Pty) Ltd');
  const counterparty = value(payload.counterparty, 'Counterparty To Be Completed');
  const tenant = value(payload.tenantId, 'MASTER');
  const risk = value(payload.risk, 'STANDARD');
  const sourcePosture = value(payload.sourcePosture, 'SOURCE_REPAIR_REQUIRED');
  const clausePack = value(payload.clausePack, 'Wilsy Standard v1');
  const signatureRoute = value(payload.signatureRoute, 'Wilsy Sign / DocuSign-ready handoff');

  const approvalsText = Array.isArray(payload.approvals)
    ? payload.approvals.join(', ')
    : value(payload.approvals, 'Owner, Legal');

  const lifecycleText = Array.isArray(payload.lifecycle)
    ? payload.lifecycle.join(' → ')
    : value(payload.lifecycle, 'Draft → Review → Approve → Send → Sign → Vault');

  const controlRows = [
    ['ISSUING ENTITY', issuingEntity],
    ['COUNTERPARTY / TENANT', counterparty],
    ['TENANT', tenant],
    ['ARTIFACT TYPE', artifactType],
    ['RISK', risk],
    ['APPROVALS', approvalsText],
    ['CLAUSE PACK', clausePack],
    ['SIGNATURE ROUTE', signatureRoute],
    ['LIFECYCLE', lifecycleText],
    ['SOURCE POSTURE', sourcePosture],
    ['GENERATED AT', generatedAt]
  ];

  const p = (textValue, options = {}) => new Paragraph({
    heading: options.heading,
    alignment: options.alignment,
    spacing: { before: options.before ?? 0, after: options.after ?? 160 },
    children: [
      new TextRun({
        text: value(textValue),
        bold: Boolean(options.bold),
        size: options.size || 22,
        color: options.color || '111827'
      })
    ]
  });

  const cell = (children, options = {}) => new TableCell({
    width: options.width ? { size: options.width, type: WidthType.DXA } : undefined,
    shading: options.fill ? { fill: options.fill } : undefined,
    margins: { top: 120, bottom: 120, left: 160, right: 160 },
    children: Array.isArray(children) ? children : [children]
  });

  const brandedHeader = new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [1900, 5360, 2100],
    rows: [
      new TableRow({
        children: [
          cell([
            new Paragraph({
              alignment: AlignmentType.CENTER,
              spacing: { after: 0 },
              children: [
                wilsyLogoImage || new TextRun({
                  text: 'WILSY OS',
                  bold: true,
                  size: 24,
                  color: 'D4AF37'
                })
              ]
            })
          ], { width: 1900, fill: '050806' }),
          cell([
            p('WILSY OS ENTERPRISE ARTIFACT', { bold: true, size: 20, color: 'D4AF37', after: 80 }),
            p(title.toUpperCase(), { bold: true, size: 34, color: 'FFFFFF', after: 80 }),
            p('Authority • Review • Execution • Forensic Proof • Source-Aware Control', { size: 16, color: 'F8F5EC', after: 0 })
          ], { width: 5360, fill: '050806' }),
          cell([
            p('VERIFIED', { bold: true, size: 20, color: 'D4AF37', after: 80 }),
            p('EDITABLE DOCX', { bold: true, size: 18, color: 'FFFFFF', after: 0 })
          ], { width: 2100, fill: '050806' })
        ]
      }),
      new TableRow({
        children: [
          cell([p('', { after: 0 })], { width: 1900, fill: 'D4AF37' }),
          cell([p('', { after: 0 })], { width: 5360, fill: 'D4AF37' }),
          cell([p('', { after: 0 })], { width: 2100, fill: 'D4AF37' })
        ]
      })
    ]
  });

  const controlTable = new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3000, 6360],
    rows: controlRows.map(([label, rowValue], index) => new TableRow({
      children: [
        cell([
          p(label, { bold: true, size: 18, color: '4B5563', after: 0 })
        ], { width: 3000, fill: index % 2 === 0 ? 'EFE9DA' : 'FFFFFF' }),
        cell([
          p(rowValue, { size: 19, color: '111827', after: 0 })
        ], { width: 6360, fill: index % 2 === 0 ? 'EFE9DA' : 'FFFFFF' })
      ]
    }))
  });

  const noticeTable = new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [180, 9180],
    rows: [
      new TableRow({
        children: [
          cell([p('', { after: 0 })], { width: 180, fill: 'D4AF37' }),
          cell([
            p('REVIEW AND RELIANCE NOTICE', { bold: true, size: 20, color: 'B18A00' }),
            p('This artifact is generated by Wilsy OS as an enterprise source-aware control document. It is not final for signature, external circulation, filing, regulatory submission, investor diligence, litigation or commercial reliance until reviewed by the responsible business owner and, where appropriate, legal, finance, security, privacy, compliance or executive leadership.', { size: 20, color: '111827', after: 0 })
          ], { width: 9180, fill: 'FBF8EF' })
        ]
      })
    ]
  });

  const sectionTitle = (textValue) => p(textValue, {
    heading: HeadingLevel.HEADING_1,
    bold: true,
    size: 26,
    color: '111827',
    before: 260,
    after: 160
  });

  const bullet = (textValue) => new Paragraph({
    bullet: { level: 0 },
    spacing: { after: 120 },
    children: [new TextRun({ text: value(textValue), size: 21, color: '111827' })]
  });

  const doc = new Document({
    creator: 'Wilsy OS',
    title,
    description: artifact.description || 'Wilsy OS enterprise artifact',
    sections: [
      {
        properties: {
          page: {
            margin: { top: 900, right: 900, bottom: 900, left: 900 }
          }
        },
        children: [
          brandedHeader,
          p(''),
          sectionTitle('DOCUMENT CONTROL'),
          controlTable,
          p(''),
          noticeTable,

          sectionTitle('1. EXECUTIVE PURPOSE AND OPERATING CONTEXT'),
          p(`${title} is generated for ${issuingEntity} under Wilsy OS artifact authority. It supports executive decision-making, operational execution, compliance evidence, commercial negotiation or controlled business workflow completion.`),
          p('This artifact must be reviewed with its source records, approvals, schedules, attachments and Wilsy OS proof trail.'),

          sectionTitle('2. SOURCE FIELDS REQUIRING COMPLETION'),
          bullet('Counterparty legal name, registration number and registered address.'),
          bullet('Representative name, title and authority.'),
          bullet('Commercial purpose, governing law deviations and execution date.'),
          bullet('Signature method, approval owner and vault retention path.'),

          sectionTitle('3. EXECUTION AND AUTHORITY'),
          p('WILSY EXECUTION', { bold: true, size: 22 }),
          p(`Entity: ${issuingEntity}`),
          p('DIRECTOR - WILSON KHANYEZI', { bold: true }),
          p(`Date: ${generatedAt.slice(0, 10)}`),
          p(''),
          p('COUNTERPARTY EXECUTION', { bold: true, size: 22 }),
          p(`Entity: ${counterparty}`),
          p('Name / Title / Authority: ______________________________'),
          p('Date: ______________________________'),

          sectionTitle('4. FORENSIC PROOF APPENDIX'),
          p('Retain this editable DOCX together with the generated Wilsy OS PDF artifact, approval evidence, signature evidence, vault record and proof trail.'),
          p(`Source Posture: ${sourcePosture}`),
          p(`Lifecycle: ${lifecycleText}`),
          p('WILSY OS CONFIDENTIAL — Retain with proof trail.', {
            bold: true,
            size: 18,
            color: 'B18A00',
            alignment: AlignmentType.RIGHT,
            before: 320
          })
        ]
      }
    ]
  });

  const blob = typeof Packer.toBlob === 'function'
    ? await Packer.toBlob(doc)
    : new Blob([await Packer.toArrayBuffer(doc)], { type: DOCX_MIME });

  const signatureBytes = new Uint8Array(await blob.slice(0, 4).arrayBuffer());
  const signature = Array.from(signatureBytes).join(',');

  if (signature !== '80,75,3,4') {
    throw new Error('DOCX integrity failed: generated file is not an OpenXML ZIP package.');
  }

  return blob.type === DOCX_MIME
    ? blob
    : new Blob([await blob.arrayBuffer()], { type: DOCX_MIME });
}

/**
 * @function createJsonBlob
 * @description Creates a machine-readable artifact audit payload.
 * @param {object} artifact - Artifact template.
 * @param {object} payload - Artifact payload.
 * @returns {Blob} JSON blob.
 * @collaboration Gives every artifact a system-of-record export.
 */
function createJsonBlob(artifact, payload) {
  return new Blob([JSON.stringify({ artifact, payload, generatedAt: new Date().toISOString() }, null, 2)], {
    type: 'application/json'
  });
}

/**
 * @function createEmailPackBlob
 * @description Creates a professional unsent EML package with HTML body and PDF attachment.
 * @param {object} artifact - Artifact template.
 * @param {object} payload - Artifact payload.
 * @param {Blob} pdfBlob - PDF attachment blob.
 * @param {string} pdfFilename - PDF filename.
 * @returns {Promise<Blob>} EML blob.
 * @collaboration Makes SEND PACK a real package rather than a grade-one mailto draft.
 */


async function createEmailPackBlob(artifact, payload, attachments = []) {
  const boundary = `wilsy_mixed_${Date.now()}_${Math.random().toString(16).slice(2)}`;
  const htmlBoundary = `wilsy_alt_${Date.now()}_${Math.random().toString(16).slice(2)}`;

  const escapeHtml = (value) => String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

  const approvalsText = Array.isArray(payload.approvals)
    ? payload.approvals.join(', ')
    : String(payload.approvals || 'Owner, Legal');

  const lifecycleText = Array.isArray(payload.lifecycle)
    ? payload.lifecycle.join(' → ')
    : String(payload.lifecycle || 'Draft → Review → Approve → Send → Sign → Vault');

  const sourcePosture = payload.sourcePosture || 'SOURCE_REPAIR_REQUIRED';
  const traceId = payload.traceId || `SEND-${Date.now().toString(16).toUpperCase()}`;
  const subject = `[WILSY SENDROOM] ${artifact.title} | ${payload.tenantId} | ${payload.risk}`;

  const attachmentListPlain = attachments.map((attachment, index) => (
    `${index + 1}. ${attachment.filename} (${attachment.label || attachment.contentType})`
  )).join('\r\n');

  const attachmentListHtml = attachments.map((attachment) => (
    `<li><strong>${escapeHtml(attachment.label || 'Attachment')}</strong>: ${escapeHtml(attachment.filename)}</li>`
  )).join('');

  const plain = [
    'WILSY OS SEND ROOM',
    '',
    `Artifact: ${artifact.title}`,
    `Tenant: ${payload.tenantId}`,
    `Risk: ${payload.risk}`,
    `Source Posture: ${sourcePosture}`,
    `Approvals Required: ${approvalsText}`,
    `Clause Pack: ${payload.clausePack}`,
    `Signature Route: ${payload.signatureRoute}`,
    `Lifecycle: ${lifecycleText}`,
    `Trace ID: ${traceId}`,
    '',
    'Attachments:',
    attachmentListPlain || 'No attachments listed.',
    '',
    'Action Gate:',
    '[ ] Confirm source fields and placeholders.',
    '[ ] Complete owner/legal approval.',
    '[ ] Confirm signature recipients and authority.',
    '[ ] Send for signature only after approval.',
    '[ ] Vault executed artifact with proof trail.',
    '',
    'This is an unsent controlled package. Do not forward externally until approval gates are complete.',
    '',
    'Wilsy OS Artifact Desk'
  ].join('\r\n');

  const html = `<!doctype html>
<html>
  <body style="margin:0;background:#050806;color:#f8f5ec;font-family:Arial,Helvetica,sans-serif;">
    <div style="padding:28px;">
      <div style="max-width:860px;margin:auto;border:1px solid #d4af37;border-radius:24px;overflow:hidden;background:#0d1410;">
        <div style="background:#050806;border-bottom:6px solid #d4af37;padding:26px 30px;">
          <div style="color:#d4af37;font-size:13px;letter-spacing:4px;font-weight:900;text-transform:uppercase;">Wilsy OS Send Room</div>
          <h1 style="color:#ffffff;margin:12px 0 6px;font-size:32px;">${escapeHtml(artifact.title)}</h1>
          <div style="color:#cfc7b3;font-size:14px;">Controlled review • approval gate • signature route • vault handoff • audit evidence</div>
        </div>

        <div style="padding:26px 30px;">
          <table style="width:100%;border-collapse:collapse;color:#f8f5ec;font-size:14px;">
            <tr><td style="padding:10px;border-bottom:1px solid #2f392f;color:#d4af37;font-weight:800;">Tenant</td><td style="padding:10px;border-bottom:1px solid #2f392f;">${escapeHtml(payload.tenantId)}</td></tr>
            <tr><td style="padding:10px;border-bottom:1px solid #2f392f;color:#d4af37;font-weight:800;">Risk</td><td style="padding:10px;border-bottom:1px solid #2f392f;">${escapeHtml(payload.risk)}</td></tr>
            <tr><td style="padding:10px;border-bottom:1px solid #2f392f;color:#d4af37;font-weight:800;">Source Posture</td><td style="padding:10px;border-bottom:1px solid #2f392f;">${escapeHtml(sourcePosture)}</td></tr>
            <tr><td style="padding:10px;border-bottom:1px solid #2f392f;color:#d4af37;font-weight:800;">Approvals</td><td style="padding:10px;border-bottom:1px solid #2f392f;">${escapeHtml(approvalsText)}</td></tr>
            <tr><td style="padding:10px;border-bottom:1px solid #2f392f;color:#d4af37;font-weight:800;">Clause Pack</td><td style="padding:10px;border-bottom:1px solid #2f392f;">${escapeHtml(payload.clausePack)}</td></tr>
            <tr><td style="padding:10px;border-bottom:1px solid #2f392f;color:#d4af37;font-weight:800;">Signature Route</td><td style="padding:10px;border-bottom:1px solid #2f392f;">${escapeHtml(payload.signatureRoute)}</td></tr>
            <tr><td style="padding:10px;border-bottom:1px solid #2f392f;color:#d4af37;font-weight:800;">Lifecycle</td><td style="padding:10px;border-bottom:1px solid #2f392f;">${escapeHtml(lifecycleText)}</td></tr>
            <tr><td style="padding:10px;border-bottom:1px solid #2f392f;color:#d4af37;font-weight:800;">Trace ID</td><td style="padding:10px;border-bottom:1px solid #2f392f;">${escapeHtml(traceId)}</td></tr>
          </table>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:24px;">
            <div style="border:1px solid #3d472f;border-radius:18px;padding:18px;background:#111a14;">
              <h2 style="color:#d4af37;margin:0 0 12px;font-size:18px;">Action Gate</h2>
              <ol style="line-height:1.8;margin:0;padding-left:20px;color:#f8f5ec;">
                <li>Confirm source fields and placeholders.</li>
                <li>Complete owner/legal approval.</li>
                <li>Confirm signature recipients and authority.</li>
                <li>Send for signature only after approval.</li>
                <li>Vault executed artifact with proof trail.</li>
              </ol>
            </div>

            <div style="border:1px solid #3d472f;border-radius:18px;padding:18px;background:#111a14;">
              <h2 style="color:#d4af37;margin:0 0 12px;font-size:18px;">Package Contents</h2>
              <ul style="line-height:1.8;margin:0;padding-left:20px;color:#f8f5ec;">
                ${attachmentListHtml || '<li>No attachments listed.</li>'}
              </ul>
            </div>
          </div>

          <div style="margin-top:24px;border-left:6px solid #d4af37;background:#fbf8ef;color:#111827;padding:18px;border-radius:12px;">
            <strong>Reliance Notice:</strong> This package is generated as an unsent controlled send pack.
            External dispatch should occur only after approval, signature routing confirmation and vaulting instructions are complete.
          </div>
        </div>
      </div>
    </div>
  </body>
</html>`;

  const parts = [
    'From: Wilsy OS Artifact Desk <noreply@wilsyos.local>',
    'To: ',
    'Cc: ',
    `Subject: ${subject}`,
    `Date: ${new Date().toUTCString()}`,
    `Message-ID: <wilsy-${Date.now()}@wilsyos.local>`,
    'X-Unsent: 1',
    `X-Wilsy-Artifact-Type: ${payload.type}`,
    `X-Wilsy-Tenant-ID: ${payload.tenantId}`,
    `X-Wilsy-Source-Posture: ${sourcePosture}`,
    `X-Wilsy-Trace-ID: ${traceId}`,
    'MIME-Version: 1.0',
    `Content-Type: multipart/mixed; boundary="${boundary}"`,
    '',
    `--${boundary}`,
    `Content-Type: multipart/alternative; boundary="${htmlBoundary}"`,
    '',
    `--${htmlBoundary}`,
    'Content-Type: text/plain; charset="UTF-8"',
    'Content-Transfer-Encoding: 7bit',
    '',
    plain,
    '',
    `--${htmlBoundary}`,
    'Content-Type: text/html; charset="UTF-8"',
    'Content-Transfer-Encoding: 7bit',
    '',
    html,
    '',
    `--${htmlBoundary}--`,
    ''
  ];

  for (const attachment of attachments) {
    const base64 = wrapBase64(await blobToBase64(attachment.blob));

    parts.push(
      `--${boundary}`,
      `Content-Type: ${attachment.contentType}; name="${attachment.filename}"`,
      'Content-Transfer-Encoding: base64',
      `Content-Disposition: attachment; filename="${attachment.filename}"`,
      '',
      base64,
      ''
    );
  }

  parts.push(`--${boundary}--`, '');

  return new Blob([parts.join('\r\n')], { type: 'message/rfc822' });
}

/**
 * @function generateArtifactExport
 * @description Generates and downloads the selected Wilsy OS artifact export.
 * @param {object} args - Export arguments.
 * @returns {Promise<object>} Artifact receipt.
 * @collaboration Centralizes PDF, DOCX, JSON and SEND PACK behavior outside the UI component.
 */
export async function generateArtifactExport({ artifact, format, tenantId, tenantConfig }) {
  const payload = createPayload(artifact, tenantId, tenantConfig);
  const baseName = `WILSY-OS-${safeFileName(artifact.title)}-${tenantId}-${Date.now()}`;

  if (format === 'PDF') {
    const blob = await createPdfBlob(artifact, payload);
    const filename = `${baseName}.pdf`;
    downloadBlob(blob, filename);
    return { title: artifact.title, format, filename, tenantId, generatedAt: payload.generatedAt };
  }

  if (format === 'DOCX') {
    const blob = await createDocxBlob(artifact, payload);
    const filename = `${baseName}.docx`;
    downloadBlob(blob, filename);
    return { title: artifact.title, format, filename, tenantId, generatedAt: payload.generatedAt };
  }


  if (format === 'EMAIL') {
    const pdfBlob = await createPdfBlob(artifact, payload);
    const pdfFilename = `${baseName}.pdf`;

    const docxBlob = await createDocxBlob(artifact, payload);
    const docxFilename = `${baseName}.docx`;

    const manifest = {
      artifact: {
        title: artifact.title,
        type: payload.type,
        tenantId,
        risk: payload.risk,
        sourcePosture: payload.sourcePosture,
        clausePack: payload.clausePack,
        signatureRoute: payload.signatureRoute,
        lifecycle: payload.lifecycle,
        approvals: payload.approvals
      },
      sendRoom: {
        status: 'UNSENT_CONTROLLED_PACKAGE',
        actionGate: [
          'Confirm source fields and placeholders',
          'Complete owner/legal approval',
          'Confirm signature recipients and authority',
          'Send for signature only after approval',
          'Vault executed artifact with proof trail'
        ],
        generatedAt: new Date().toISOString()
      }
    };

    const manifestFilename = `${baseName}-sendroom-manifest.json`;
    const manifestBlob = new Blob([JSON.stringify(manifest, null, 2)], {
      type: 'application/json'
    });

    const emailBlob = await createEmailPackBlob(artifact, payload, [
      {
        label: 'Boardroom PDF artifact',
        filename: pdfFilename,
        contentType: 'application/pdf',
        blob: pdfBlob
      },
      {
        label: 'Editable DOCX review file',
        filename: docxFilename,
        contentType: DOCX_MIME,
        blob: docxBlob
      },
      {
        label: 'Wilsy Send Room manifest',
        filename: manifestFilename,
        contentType: 'application/json',
        blob: manifestBlob
      }
    ]);

    const filename = `${baseName}-SEND-ROOM.eml`;
    downloadBlob(emailBlob, filename);

    return {
      title: artifact.title,
      format: 'SEND ROOM',
      filename,
      tenantId,
      generatedAt: payload.generatedAt
    };
  }

  const blob = createJsonBlob(artifact, payload);
  const filename = `${baseName}.json`;
  downloadBlob(blob, filename);
  return { title: artifact.title, format: 'JSON', filename, tenantId, generatedAt: payload.generatedAt };
}

export default generateArtifactExport;
