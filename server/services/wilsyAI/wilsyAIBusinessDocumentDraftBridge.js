/* eslint-disable */
import { resolveWilsyTenantDocumentSource } from './wilsyAIDocumentSourceResolver.js';

/**
 * @function coerceWilsyDocumentText
 * @description Safely coerces business document values into bounded tenant-safe text.
 * @param {unknown} value - Raw value.
 * @param {number} limit - Maximum length.
 * @returns {string} Bounded text.
 * @collaboration Business Document Draft Bridge, Operator Kernel, and contract-form preparation.
 */
function coerceWilsyDocumentText(value = '', limit = 1400) {
  return String(value || '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, limit);
}

/**
 * @function buildWilsyDocumentDraftId
 * @description Builds a stable document draft identifier.
 * @param {string} prefix - Draft prefix.
 * @returns {string} Draft id.
 * @collaboration CRM document draft links, evidence receipts, and prepared work UI.
 */
function buildWilsyDocumentDraftId(prefix = 'document_draft') {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

/**
 * @function inferWilsyDocumentType
 * @description Infers the requested business document type.
 * @param {string} question - Operator request.
 * @returns {string} Document type.
 * @collaboration Contract forms, proposals, letters, memos, and document draft routing.
 */
function inferWilsyDocumentType(question = '') {
  const text = coerceWilsyDocumentText(question, 1000).toLowerCase();

  if (/\bcontract\b/.test(text) && /\bform\b/.test(text)) {
    return 'Contract Form';
  }

  if (/\bcontract\b/.test(text)) {
    return 'Contract';
  }

  if (/\bproposal\b/.test(text)) {
    return 'Proposal';
  }

  if (/\bagreement\b/.test(text)) {
    return 'Agreement';
  }

  if (/\bletter\b/.test(text)) {
    return 'Business Letter';
  }

  if (/\bmemo\b|\bmemorandum\b/.test(text)) {
    return 'Business Memo';
  }

  return 'Business Document';
}

/**
 * @function inferWilsyDocumentDeliveryRequest
 * @description Determines whether the user asked to send or deliver the document.
 * @param {string} question - Operator request.
 * @returns {boolean} Whether delivery was requested.
 * @collaboration Document draft workflow, delivery connector boundaries, and no-silent-send policy.
 */
function inferWilsyDocumentDeliveryRequest(question = '') {
  return /\b(send|email|mail|deliver|share|forward)\b/i.test(
    coerceWilsyDocumentText(question, 1000)
  );
}

/**
 * @function extractWilsyDocumentRecipientEmails
 * @description Extracts recipient email addresses from a business document request.
 * @param {string} question - Operator request.
 * @returns {Array<string>} Unique recipient emails.
 * @collaboration Document delivery preparation, email connector boundaries, and approval workflow.
 */
function extractWilsyDocumentRecipientEmails(question = '') {
  const matches = coerceWilsyDocumentText(question, 1800).match(
    /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi
  );

  return [...new Set(matches || [])];
}

/**
 * @function extractWilsyDocumentPurpose
 * @description Extracts a practical purpose statement for the document draft.
 * @param {string} question - Operator request.
 * @param {string} documentType - Document type.
 * @returns {string} Purpose statement.
 * @collaboration Document draft generation, business-English summaries, and operator review.
 */
function extractWilsyDocumentPurpose(question = '', documentType = 'Business Document') {
  const text = coerceWilsyDocumentText(question, 1400);
  const aboutMatch = text.match(/\b(?:about|for|regarding|concerning)\s+(.+)$/i);

  if (aboutMatch) {
    return coerceWilsyDocumentText(aboutMatch[1], 260);
  }

  return `Prepare ${documentType} for review.`;
}

/**
 * @function buildWilsyDocumentSections
 * @description Builds first-pass sections for the requested business document.
 * @param {string} documentType - Document type.
 * @returns {Array<string>} Section list.
 * @collaboration Business document draft generation, contract-form structure, and review workflow.
 */
function buildWilsyDocumentSections(documentType = 'Business Document') {
  if (/contract/i.test(documentType)) {
    return [
      'Parties',
      'Scope of engagement',
      'Commercial terms',
      'Obligations',
      'Duration and termination',
      'Confidentiality',
      'Signatures',
    ];
  }

  if (/proposal/i.test(documentType)) {
    return [
      'Executive summary',
      'Client need',
      'Proposed solution',
      'Scope',
      'Pricing',
      'Delivery plan',
      'Approval',
    ];
  }

  if (/letter/i.test(documentType)) {
    return ['Recipient', 'Purpose', 'Main message', 'Requested action', 'Closing'];
  }

  return ['Purpose', 'Context', 'Key details', 'Risks and assumptions', 'Next action', 'Approval'];
}

/**
 * @function buildWilsyTenantBrandedDocumentPreview
 * @description Builds a tenant-branded document preview payload for no-reset AI review.
 * @param {Object} draft - Business document draft.
 * @returns {Object} Tenant-branded document preview payload.
 * @collaboration Business Document Draft Bridge, tenant branded document system, AI review panel, and governed send workflow.
 */
function buildWilsyTenantBrandedDocumentPreview(draft = {}) {
  const generatedAt = new Date().toISOString();
  const brandName =
    draft.tenantBrand?.name || (draft.tenantId === 'MASTER' ? 'Wilsy OS Root' : draft.tenantId);

  return {
    previewVersion: 'P60K5Q10BE_TENANT_BRANDED_DOCUMENT_PREVIEW',
    source: draft.documentSource || null,
    draftId: draft.draftId,
    tenantId: draft.tenantId,
    operatorId: draft.operatorId,
    brand: {
      tenantName: brandName,
      seal: 'WILSY_OS_TENANT_BRANDED_DOCUMENT',
      posture: 'Draft review only',
    },
    document: {
      documentType: draft.documentType,
      title: draft.title,
      purpose: draft.purpose,
      status: draft.deliveryRequested ? 'Draft ready; delivery pending' : 'Draft ready for review',
      generatedAt,
      sections: (draft.sections || []).map((section, index) => ({
        sectionId: `section_${index + 1}`,
        heading: section,
        body: `Review and complete ${section.toLowerCase()} for this ${String(draft.documentType || 'document').toLowerCase()}.`,
      })),
      delivery: {
        requested: Boolean(draft.deliveryRequested),
        recipients: draft.recipientEmails || [],
        missingFields: draft.missingFields || [],
        approvalRequired: true,
      },
    },
    actions: {
      reviewInsideWilsyAI: true,
      canSend: false,
      sendReason: 'Sending requires recipient details, delivery connector binding, and approval.',
    },
  };
}

/**
 * @function persistWilsyBusinessDocumentDraft
 * @description Persists the document draft when MongoDB is available while preserving no-send mutation boundaries.
 * @param {Object} params - Persistence params.
 * @param {Object} params.draft - Draft payload.
 * @param {Object} params.documentPreview - Preview payload.
 * @returns {Promise<Object>} Persistence status.
 * @collaboration Document review bridge, CRM document drafts, evidence receipts, and tenant branded document storage.
 */
async function persistWilsyBusinessDocumentDraft({ draft = {}, documentPreview = {} } = {}) {
  try {
    const mongoose = await import('mongoose');
    const db = mongoose.default?.connection?.db || mongoose.connection?.db;

    if (!db) {
      return {
        status: 'PERSISTENCE_UNAVAILABLE',
        message:
          'MongoDB is not connected; document preview is available in the Operator Model response only.',
      };
    }

    await db.collection('wilsy_business_document_drafts').updateOne(
      { draftId: draft.draftId, tenantId: draft.tenantId },
      {
        $set: {
          draftId: draft.draftId,
          tenantId: draft.tenantId,
          operatorId: draft.operatorId,
          documentType: draft.documentType,
          title: draft.title,
          purpose: draft.purpose,
          sections: draft.sections,
          deliveryRequested: draft.deliveryRequested,
          recipientEmails: draft.recipientEmails,
          missingFields: draft.missingFields,
          crmDocumentDraftLink: draft.crmDocumentDraftLink,
          documentPreview,
          updatedAt: new Date(),
        },
        $setOnInsert: {
          createdAt: new Date(),
        },
      },
      { upsert: true }
    );

    return {
      status: 'PERSISTED',
      message: 'Document draft persisted for tenant-branded review.',
    };
  } catch (error) {
    return {
      status: 'PERSISTENCE_ERROR',
      message: error?.message || 'Document draft persistence failed.',
    };
  }
}

/**
 * @function buildWilsyBusinessDocumentDraft
 * @description Builds a review-ready business document draft without sending or publishing it.
 * @param {Object} params - Draft params.
 * @param {string} params.question - Operator request.
 * @param {string} params.tenantId - Tenant id.
 * @param {string} params.operatorId - Operator id.
 * @returns {Object} Business document draft.
 * @collaboration Generate Business Document capability, prepared work UI, and delivery connector boundary.
 */
export function buildWilsyBusinessDocumentDraft({
  question = '',
  tenantId = 'MASTER',
  operatorId = 'WILSY_OPERATOR',
} = {}) {
  const documentType = inferWilsyDocumentType(question);
  const deliveryRequested = inferWilsyDocumentDeliveryRequest(question);
  const recipientEmails = extractWilsyDocumentRecipientEmails(question);
  const draftId = buildWilsyDocumentDraftId('document_draft');
  const purpose = extractWilsyDocumentPurpose(question, documentType);
  const sections = buildWilsyDocumentSections(documentType);
  const missingFields = [];

  if (deliveryRequested && recipientEmails.length === 0) {
    missingFields.push('recipient email address');
  }

  if (deliveryRequested) {
    missingFields.push('approved delivery connector');
  }

  return {
    draftId,
    tenantId,
    operatorId,
    kind: 'document',
    documentType,
    title: documentType,
    purpose,
    sections,
    deliveryRequested,
    recipientEmails,
    missingFields,
    readyForReview: true,
    readyForDelivery: deliveryRequested ? missingFields.length === 0 : false,
    crmDocumentDraftLink: `/crm/documents/drafts/${draftId}`,
    sourceQuestion: coerceWilsyDocumentText(question, 1200),
    documentSource: null,
    sourceStatus: 'SOURCE_NOT_EVALUATED',
    sourceBacked: false,
    tenantBrand: null,
    executionStatus: deliveryRequested
      ? 'Document draft prepared. Delivery requires recipient details, connector binding, and approval.'
      : 'Document draft prepared for review.',
  };
}

/**
 * @function buildWilsyDocumentInstitutionalHeaders
 * @description Builds institutional headers for document draft evidence.
 * @param {Object} params - Header params.
 * @returns {Object} Institutional headers.
 * @collaboration Business Document Draft Bridge, evidence receipts, and operator proof.
 */
function buildWilsyDocumentInstitutionalHeaders({
  tenantId = 'MASTER',
  operatorId = 'WILSY_OPERATOR',
  route = '/api/source-registry/health',
  commandSurface = 'WILSY_BUSINESS_DOCUMENT_DRAFT_BRIDGE',
} = {}) {
  return {
    tenantId,
    operatorId,
    generatedAt: new Date().toISOString(),
    route,
    commandSurface,
    mutation: false,
    contractVersion: 'P60K5Q10BA_BUSINESS_DOCUMENT_DRAFT_BRIDGE',
  };
}

/**
 * @function executeWilsyBusinessDocumentDraftBridge
 * @description Prepares a business document draft and preserves no-send/no-mutation approval boundaries.
 * @param {Object} params - Bridge params.
 * @param {Object} params.req - Express request.
 * @param {string} params.question - Operator request.
 * @param {string} params.tenantId - Tenant id.
 * @param {string} params.operatorId - Operator id.
 * @returns {Promise<Object>} Document draft tool result.
 * @collaboration Operator Kernel, Business Document Draft Bridge, Prepared Work UI, and Capability Foundry promotion path.
 */
export async function executeWilsyBusinessDocumentDraftBridge({
  req = {},
  question = '',
  tenantId = 'MASTER',
  operatorId = 'WILSY_OPERATOR',
} = {}) {
  const draft = buildWilsyBusinessDocumentDraft({
    question,
    tenantId,
    operatorId,
  });
  const documentSource = await resolveWilsyTenantDocumentSource({
    tenantId,
    operatorId,
    documentType: draft.documentType,
    question,
  });

  draft.documentSource = documentSource;
  draft.sourceStatus = documentSource.status;
  draft.sourceBacked = Boolean(documentSource.sourceFound && documentSource.approved);
  draft.tenantBrand = documentSource.tenantBrand;

  if (
    documentSource.sourceFound &&
    documentSource.approved &&
    Array.isArray(documentSource.sections) &&
    documentSource.sections.length
  ) {
    draft.sections = documentSource.sections;
  }

  const institutionalHeaders = buildWilsyDocumentInstitutionalHeaders({
    tenantId,
    operatorId,
  });
  const documentPreview = buildWilsyTenantBrandedDocumentPreview(draft);
  draft.documentPreview = documentPreview;
  const persistence = await persistWilsyBusinessDocumentDraft({
    draft,
    documentSource,
    documentPreview,
  });

  return {
    tool: 'business_document_draft_bridge',
    label: 'Business Document Draft',
    domain: 'documents',
    status: !(documentSource.sourceFound && documentSource.approved)
      ? 'SOURCE_MISSING'
      : draft.deliveryRequested
        ? 'DRAFT_READY_DELIVERY_PENDING'
        : 'DRAFT_PREPARED',
    statusLabel: !(documentSource.sourceFound && documentSource.approved)
      ? 'Approved source missing'
      : draft.deliveryRequested
        ? 'Draft ready; delivery pending'
        : 'Draft prepared',
    mutation: false,
    draft,
    documentSource,
    sourceChecked: {
      tool: documentSource.toolChecked || 'Tenant Document Library',
      status: documentSource.status,
      sourceFound: Boolean(documentSource.sourceFound),
      approved: Boolean(documentSource.approved),
      sourceSystem: documentSource.sourceSystem || 'TENANT_DOCUMENT_LIBRARY',
      sourceReference: documentSource.sourceReference || documentSource.sourcePath || null,
    },
    documentPreview,
    persistence,
    crmDocumentLink: draft.crmDocumentDraftLink,
    documentLink: draft.crmDocumentDraftLink,
    missingFields: draft.missingFields,
    connector: 'Document Draft Bridge',
    message: draft.deliveryRequested
      ? 'The document draft is ready. Sending requires delivery details, connector binding, and approval.'
      : 'The document draft is ready for review.',
    institutionalHeaders,
    strikePayload: {
      institutionalHeaders,
      commandType: 'BUSINESS_DOCUMENT_DRAFT_PREPARED',
      mutation: false,
    },
  };
}

export default executeWilsyBusinessDocumentDraftBridge;
