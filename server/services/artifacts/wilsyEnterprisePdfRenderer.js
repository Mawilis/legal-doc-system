/* eslint-disable */
import PDFDocument from 'pdfkit';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

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
 * @collaboration Stabilizes artifact rendering when tenant source data is incomplete.
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
 * @collaboration Preserves forensic visibility without proof-text collisions.
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
 * @collaboration Gives every artifact a tenant-facing title before source enrichment is complete.
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
 * @collaboration Prevents broken tenant downloads caused by unsafe document titles.
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
 * @collaboration Restores Wilsy OS branding inside backend-generated tenant PDFs.
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
 * @function buildState
 * @description Builds normalized render state from verified request identity and proof context.
 * @param {object} identity - Verified artifact identity.
 * @param {object} proof - Forensic proof context.
 * @returns {object} Render state.
 * @collaboration Bridges request verification into the enterprise renderer.
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
    generatedBy: textValue(
      identity.email || identity.userEmail || data.generatedBy || 'wilsonkhanyezi@gmail.com'
    ),
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

/**
 * @function drawLogo
 * @description Draws the Wilsy logo optically centered inside the enterprise header badge.
 * @param {PDFDocument} doc - PDF document.
 * @returns {void}
 * @collaboration Ensures every generated artifact has precise institutional branding.
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
 * @function drawHeader
 * @description Draws a non-overlapping Wilsy OS enterprise header with logo and accurate pagination.
 * @param {PDFDocument} doc - PDF document.
 * @param {object} state - Render state.
 * @param {number} pageNumber - Page number.
 * @param {number} totalPages - Total pages.
 * @returns {void}
 * @collaboration Produces tenant-facing header quality for legal, HR, finance and invoice artifacts.
 */
function drawHeader(doc, state, pageNumber, totalPages) {
  doc.save();

  doc.rect(42, 34, 512, 126).fill(BRAND.black);
  doc.rect(42, 160, 512, 5).fill(BRAND.gold);

  drawLogo(doc);

  const title = textValue(state.title || 'Wilsy OS Artifact').toUpperCase();
  const titleSize = title.length > 48 ? 14.5 : title.length > 34 ? 17 : title.length > 22 ? 20 : 22;

  doc
    .fillColor(BRAND.gold)
    .font('Helvetica-Bold')
    .fontSize(8.5)
    .text('WILSY OS ENTERPRISE ARTIFACT', 140, 52, { width: 300, lineBreak: false });

  doc
    .fillColor('#FFFFFF')
    .font('Helvetica-Bold')
    .fontSize(titleSize)
    .text(title, 140, 72, { width: 300, lineGap: 0 });

  doc
    .fillColor(BRAND.ivory)
    .font('Helvetica')
    .fontSize(7)
    .text('Authority • Review • Execution • Forensic Proof • Source-Aware Control', 140, 134, {
      width: 338,
      lineBreak: false,
    });

  doc
    .fillColor(BRAND.gold)
    .font('Helvetica-Bold')
    .fontSize(8)
    .text('VERIFIED', 424, 54, { width: 66, align: 'right', lineBreak: false });

  doc
    .fillColor('#FFFFFF')
    .font('Helvetica-Bold')
    .fontSize(8)
    .text(`PAGE ${pageNumber}/${totalPages}`, 494, 54, {
      width: 48,
      align: 'right',
      lineBreak: false,
    });

  doc.restore();
}

/**
 * @function drawFooter
 * @description Draws a non-overlapping proof footer.
 * @param {PDFDocument} doc - PDF document.
 * @param {object} state - Render state.
 * @returns {void}
 * @collaboration Prevents forensic proof collisions in production tenant-facing documents.
 */
function drawFooter(doc, state) {
  doc.save();

  doc.moveTo(PAGE.left, 762).lineTo(543, 762).strokeColor(BRAND.line).lineWidth(0.6).stroke();

  doc
    .fillColor(BRAND.muted)
    .font('Helvetica')
    .fontSize(6.2)
    .text(
      'Legally non-final until reviewed and approved. Retain with the Wilsy OS proof trail.',
      PAGE.left,
      773,
      {
        width: 282,
        lineBreak: false,
      }
    );

  doc
    .fillColor(BRAND.black)
    .font('Helvetica-Bold')
    .fontSize(6.2)
    .text('DIRECTOR - WILSON KHANYEZI', PAGE.left, 792, { width: 282, lineBreak: false });

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

  doc
    .fillColor(BRAND.muted)
    .font('Helvetica')
    .fontSize(5.3)
    .text(state.sourcePosture, 344, 802, { width: 199, align: 'right', lineBreak: false });

  doc.restore();
}

/**
 * @function ensureSpace
 * @description Adds a page when the remaining content area is too small.
 * @param {PDFDocument} doc - PDF document.
 * @param {object} cursor - Cursor state.
 * @param {number} required - Required height.
 * @returns {void}
 * @collaboration Maintains professional page flow and protects the footer zone.
 */
function ensureSpace(doc, cursor, required) {
  if (cursor.y + required <= PAGE.bottom) return;

  doc.addPage();
  cursor.y = PAGE.top;
}

/**
 * @function writeParagraph
 * @description Writes a numbered paragraph and updates the cursor.
 * @param {PDFDocument} doc - PDF document.
 * @param {object} cursor - Cursor state.
 * @param {string} paragraph - Paragraph text.
 * @param {number} index - Paragraph index.
 * @returns {void}
 * @collaboration Produces readable legal instrument body copy.
 */
function writeParagraph(doc, cursor, paragraph, index) {
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
}

/**
 * @function drawSection
 * @description Draws a controlled enterprise section.
 * @param {PDFDocument} doc - PDF document.
 * @param {object} cursor - Cursor state.
 * @param {object} section - Section definition.
 * @returns {void}
 * @collaboration Creates dense but readable enterprise legal and business artifacts.
 */
function drawSection(doc, cursor, section) {
  ensureSpace(doc, cursor, 72);

  doc
    .fillColor(BRAND.black)
    .font('Helvetica-Bold')
    .fontSize(11.2)
    .text(textValue(section.title).toUpperCase(), PAGE.left, cursor.y, {
      width: PAGE.contentWidth,
    });

  cursor.y = doc.y + 14;

  section.paragraphs.forEach((paragraph, index) => writeParagraph(doc, cursor, paragraph, index));

  cursor.y += 6;
}

/**
 * @function getNdaSections
 * @description Returns deeper enterprise NDA clauses.
 * @param {object} state - Render state.
 * @returns {Array<object>} NDA sections.
 * @collaboration Upgrades NDA output beyond shallow prototype clauses.
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
 * @param {object} state - Render state.
 * @returns {Array<object>} Generic enterprise sections.
 * @collaboration Gives every catalog artifact a serious baseline until type-specific libraries are completed.
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
 * @function buildSections
 * @description Selects the appropriate clause library for the artifact type.
 * @param {object} state - Render state.
 * @returns {Array<object>} Sections.
 * @collaboration Provides a safe expansion path for legal, HR, finance and operational documents.
 */
function buildSections(state) {
  const type = state.type.toLowerCase();

  if (type.includes('nda') || type.includes('non-disclosure')) {
    return getNdaSections(state);
  }

  return getGenericSections(state);
}

/**
 * @function drawDocumentControl
 * @description Draws the document control section.
 * @param {PDFDocument} doc - PDF document.
 * @param {object} cursor - Cursor state.
 * @param {object} state - Render state.
 * @returns {void}
 * @collaboration Provides tenant-facing document identity, source posture and proof metadata.
 */
function drawDocumentControl(doc, cursor, state) {
  doc
    .fillColor(BRAND.black)
    .font('Helvetica-Bold')
    .fontSize(15)
    .text('DOCUMENT CONTROL', PAGE.left, cursor.y);
  cursor.y = doc.y + 22;

  const rows = [
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
    .text('REVIEW AND RELIANCE NOTICE', PAGE.left + 18, cursor.y + 14);
  doc
    .fillColor(BRAND.black)
    .font('Helvetica')
    .fontSize(8.1)
    .text(
      'This artifact is generated by Wilsy OS as an enterprise source-aware control document. It is not final for signature, external circulation, filing, regulatory submission, investor diligence, litigation or commercial reliance until reviewed by the responsible business owner and, where appropriate, legal, finance, security, privacy, compliance or executive leadership.',
      PAGE.left + 18,
      cursor.y + 31,
      { width: 450, lineGap: 2.2 }
    );

  cursor.y += 106;
}

/**
 * @function drawProofSchedule
 * @description Draws a proof and source completion appendix.
 * @param {PDFDocument} doc - PDF document.
 * @param {object} cursor - Cursor state.
 * @param {object} state - Render state.
 * @returns {void}
 * @collaboration Adds audit and source-control depth to generated artifacts.
 */
function drawProofSchedule(doc, cursor, state) {
  doc.addPage();
  cursor.y = PAGE.top;

  drawSection(doc, cursor, {
    title: 'Schedule A — Source Fields Requiring Completion',
    paragraphs: [
      'Counterparty legal name, registration number, registered address, representative name, representative authority, commercial purpose, governing law deviations, signature method, approval owner and execution date must be completed or connected from source systems before final reliance.',
      'Where any field remains incomplete, Wilsy OS must preserve the placeholder visibly and retain the source posture so reviewers can distinguish draft automation from verified legal facts.',
    ],
  });

  drawSection(doc, cursor, {
    title: 'Schedule B — Forensic Proof Appendix',
    paragraphs: [
      `Trace ID: ${state.traceId}. Merkle Root: ${state.merkleRoot}. SHA3 / Seal: ${state.sha3}. Source Posture: ${state.sourcePosture}. Generated At: ${state.generatedAt}.`,
      'The proof appendix supports reconstruction, version comparison, audit evidence, dispute response, investor diligence and internal control review.',
    ],
  });
}

/**
 * @function drawExecution
 * @description Draws premium execution blocks.
 * @param {PDFDocument} doc - PDF document.
 * @param {object} cursor - Cursor state.
 * @param {object} state - Render state.
 * @returns {void}
 * @collaboration Produces a boardroom-ready execution page for tenant-facing artifacts.
 */
function drawExecution(doc, cursor, state) {
  doc.addPage();
  cursor.y = PAGE.top;

  doc
    .fillColor(BRAND.black)
    .font('Helvetica-Bold')
    .fontSize(15)
    .text('EXECUTION AND AUTHORITY', PAGE.left, cursor.y);
  cursor.y = doc.y + 28;

  doc
    .fillColor(BRAND.black)
    .font('Helvetica')
    .fontSize(9)
    .text(
      'IN WITNESS WHEREOF, the parties execute this artifact through authorised representatives. Electronic signatures, wet-ink signatures and system-generated proof records may be used subject to applicable law, internal approval requirements and the Wilsy OS proof trail.',
      PAGE.left,
      cursor.y,
      { width: PAGE.contentWidth, lineGap: 3 }
    );

  cursor.y = doc.y + 42;

  const blocks = [
    ['WILSY EXECUTION', state.issuingEntity, 'DIRECTOR - WILSON KHANYEZI'],
    ['COUNTERPARTY EXECUTION', state.counterparty, 'Name / Title / Authority'],
  ];

  blocks.forEach((block) => {
    ensureSpace(doc, cursor, 118);

    doc
      .fillColor(BRAND.black)
      .font('Helvetica-Bold')
      .fontSize(10)
      .text(block[0], PAGE.left, cursor.y);
    cursor.y += 24;
    doc
      .fillColor(BRAND.black)
      .font('Helvetica')
      .fontSize(8.7)
      .text(`Entity: ${block[1]}`, PAGE.left + 18, cursor.y);
    cursor.y += 38;
    doc
      .moveTo(PAGE.left + 18, cursor.y)
      .lineTo(PAGE.left + 255, cursor.y)
      .strokeColor(BRAND.black)
      .lineWidth(0.7)
      .stroke();
    cursor.y += 7;
    doc
      .fillColor(BRAND.black)
      .font('Helvetica-Bold')
      .fontSize(8.1)
      .text(block[2], PAGE.left + 18, cursor.y);
    cursor.y += 16;
    doc
      .fillColor(BRAND.black)
      .font('Helvetica')
      .fontSize(8)
      .text(`Date: ${state.effectiveDate}`, PAGE.left + 18, cursor.y);
    cursor.y += 34;
  });
}

/**
 * @function applyChrome
 * @description Applies headers and footers after final page count is known.
 * @param {PDFDocument} doc - PDF document.
 * @param {object} state - Render state.
 * @returns {void}
 * @collaboration Guarantees accurate page count and consistent enterprise document chrome.
 */
function applyChrome(doc, state) {
  const range = doc.bufferedPageRange();

  for (let pageIndex = range.start; pageIndex < range.start + range.count; pageIndex += 1) {
    doc.switchToPage(pageIndex);
    drawHeader(doc, state, pageIndex - range.start + 1, range.count);
    drawFooter(doc, state);
  }
}

/**
 * @function streamEnterpriseArtifactPdf
 * @description Streams a Wilsy OS enterprise PDF artifact with stable branding, pagination and deeper content.
 * @param {object} args - Render arguments.
 * @returns {Promise<void>} Streams the PDF response.
 * @collaboration Replaces shallow draft documents with tenant-facing enterprise artifact output.
 */
export async function streamEnterpriseArtifactPdf({ res, identity, proof }) {
  const state = buildState(identity, proof);
  const fileName = `WILSY-OS-${safeFileName(state.title)}-${state.tenantId}-${Date.now()}.pdf`;

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
      Title: state.title,
      Author: 'Wilsy OS',
      Subject: `Wilsy OS Enterprise Artifact - ${state.type}`,
      Keywords: `Wilsy OS, ${state.type}, ${state.tenantId}, ${state.traceId}`,
    },
  });

  doc.pipe(res);

  const cursor = { y: PAGE.top };

  drawDocumentControl(doc, cursor, state);
  buildSections(state).forEach((section) => drawSection(doc, cursor, section));
  drawProofSchedule(doc, cursor, state);
  drawExecution(doc, cursor, state);
  applyChrome(doc, state);

  doc.end();
}

export default streamEnterpriseArtifactPdf;
