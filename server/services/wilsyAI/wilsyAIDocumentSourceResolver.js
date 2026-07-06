/* eslint-disable */
import fs from 'fs';
import path from 'path';

/**
 * @function normalizeWilsyDocumentSourceText
 * @description Normalizes document source resolver text for safe matching and source reporting.
 * @param {unknown} value - Raw text.
 * @param {number} limit - Maximum output length.
 * @returns {string} Normalized text.
 * @collaboration Tenant Document Source Resolver, Business Document Draft Bridge, and Operator Model.
 */
function normalizeWilsyDocumentSourceText(value = '', limit = 2000) {
  return String(value || '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, limit);
}

/**
 * @function buildWilsyDocumentSourceKeywords
 * @description Builds search keywords for the requested business document type.
 * @param {string} documentType - Requested document type.
 * @param {string} question - Operator question.
 * @returns {Array<string>} Source keywords.
 * @collaboration Tenant document library lookup, template matching, and approved document source resolution.
 */
function buildWilsyDocumentSourceKeywords(documentType = 'Business Document', question = '') {
  const source = `${documentType} ${question}`.toLowerCase();
  const keywords = new Set(['document', 'template']);

  if (source.includes('contract')) {
    keywords.add('contract');
    keywords.add('agreement');
  }

  if (source.includes('form')) {
    keywords.add('form');
  }

  if (source.includes('proposal')) {
    keywords.add('proposal');
  }

  if (source.includes('memo') || source.includes('memorandum')) {
    keywords.add('memo');
    keywords.add('memorandum');
  }

  if (source.includes('letter')) {
    keywords.add('letter');
  }

  return [...keywords];
}

/**
 * @function buildWilsyTenantBrandFromSource
 * @description Builds tenant branding metadata from a found source or tenant context.
 * @param {Object} params - Brand params.
 * @param {string} params.tenantId - Tenant id.
 * @param {Object} params.source - Source record.
 * @returns {Object} Tenant brand metadata.
 * @collaboration Tenant-branded document review, document source resolver, and Wilsy OS tenant identity.
 */
function buildWilsyTenantBrandFromSource({ tenantId = 'MASTER', source = {} } = {}) {
  return {
    tenantId,
    name:
      source?.tenantBrand?.name ||
      source?.brandName ||
      source?.tenantName ||
      (tenantId === 'MASTER' ? 'Wilsy OS Root' : tenantId),
    seal: source?.tenantBrand?.seal || source?.seal || 'WILSY_OS_TENANT_BRANDED_DOCUMENT',
    source:
      source?.sourceSystem ||
      source?.collection ||
      source?.path ||
      'TENANT_DOCUMENT_SOURCE_RESOLVER',
  };
}

/**
 * @function isWilsyApprovedDocumentSource
 * @description Determines whether a document source is approved enough to support a production draft.
 * @param {Object} source - Source record.
 * @returns {boolean} Whether source is approved.
 * @collaboration Approved document template checks, tenant governance, and no-fake-generation boundaries.
 */
function isWilsyApprovedDocumentSource(source = {}) {
  const rawStatus = normalizeWilsyDocumentSourceText(
    source.status || source.approvalStatus || source.state || source.lifecycle || '',
    120
  ).toUpperCase();

  if (!rawStatus) {
    return Boolean(source.path || source.collection);
  }

  return ['APPROVED', 'PUBLISHED', 'ACTIVE', 'READY', 'VERIFIED', 'LIVE'].some((status) =>
    rawStatus.includes(status)
  );
}

/**
 * @function scoreWilsyDocumentSource
 * @description Scores a possible document source by keyword match and approval posture.
 * @param {Object} source - Source record.
 * @param {Array<string>} keywords - Keywords.
 * @returns {number} Match score.
 * @collaboration Tenant document source ranking and source-aware draft generation.
 */
function scoreWilsyDocumentSource(source = {}, keywords = []) {
  const haystack = normalizeWilsyDocumentSourceText(
    [
      source.title,
      source.name,
      source.documentType,
      source.type,
      source.category,
      source.description,
      source.path,
      source.sourceSystem,
      source.collection,
    ]
      .filter(Boolean)
      .join(' '),
    4000
  ).toLowerCase();

  let score = 0;

  keywords.forEach((keyword) => {
    if (haystack.includes(keyword.toLowerCase())) {
      score += 10;
    }
  });

  if (isWilsyApprovedDocumentSource(source)) {
    score += 25;
  }

  if (/tenant|brand|template|artifact|document|contract/i.test(haystack)) {
    score += 8;
  }

  return score;
}

/**
 * @function extractWilsyDocumentSectionsFromSource
 * @description Extracts section headings from a document source when available.
 * @param {Object} source - Source record.
 * @returns {Array<string>} Section headings.
 * @collaboration Tenant document templates, business document draft bridge, and review panel.
 */
function extractWilsyDocumentSectionsFromSource(source = {}) {
  if (Array.isArray(source.sections) && source.sections.length) {
    return source.sections
      .map((section) =>
        normalizeWilsyDocumentSourceText(section?.heading || section?.title || section, 120)
      )
      .filter(Boolean)
      .slice(0, 12);
  }

  if (Array.isArray(source.fields) && source.fields.length) {
    return source.fields
      .map((field) => normalizeWilsyDocumentSourceText(field?.label || field?.name || field, 120))
      .filter(Boolean)
      .slice(0, 12);
  }

  return [];
}

/**
 * @function searchWilsyMongoDocumentSources
 * @description Searches connected MongoDB collections for tenant document templates, artifacts, forms, and branded document sources.
 * @param {Object} params - Search params.
 * @param {string} params.tenantId - Tenant id.
 * @param {Array<string>} params.keywords - Keywords.
 * @returns {Promise<Array<Object>>} Source candidates.
 * @collaboration Mongo document templates, artifact catalog persistence, tenant source library, and approved document generation.
 */
async function searchWilsyMongoDocumentSources({ tenantId = 'MASTER', keywords = [] } = {}) {
  try {
    const mongoose = await import('mongoose');
    const db = mongoose.default?.connection?.db || mongoose.connection?.db;

    if (!db) {
      return [];
    }

    const collections = await db.listCollections().toArray();
    const sourceCollections = collections
      .map((collection) => collection.name)
      .filter((name) =>
        /document|template|artifact|form|contract|agreement|memo|letter/i.test(name)
      )
      .slice(0, 24);

    const candidates = [];

    for (const collectionName of sourceCollections) {
      const collection = db.collection(collectionName);
      const regexes = keywords.map(
        (keyword) => new RegExp(keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i')
      );

      const query = {
        $and: [
          {
            $or: [
              { tenantId },
              { tenantId: 'MASTER' },
              { tenant: tenantId },
              { tenant: 'MASTER' },
              { isGlobal: true },
              { global: true },
            ],
          },
          {
            $or: regexes.flatMap((regex) => [
              { title: regex },
              { name: regex },
              { documentType: regex },
              { type: regex },
              { category: regex },
              { description: regex },
            ]),
          },
        ],
      };

      const rows = await collection.find(query).limit(8).toArray();

      rows.forEach((row) => {
        candidates.push({
          ...row,
          collection: collectionName,
          sourceSystem: 'MONGO_TENANT_DOCUMENT_LIBRARY',
        });
      });
    }

    return candidates;
  } catch (error) {
    return [];
  }
}

/**
 * @function searchWilsyLocalDocumentSources
 * @description Searches existing repository document/artifact/template surfaces for development source evidence without claiming a fake production source.
 * @param {Object} params - Search params.
 * @param {Array<string>} params.keywords - Keywords.
 * @returns {Array<Object>} Local source candidates.
 * @collaboration Existing Wilsy document system discovery, tenant branded artifacts, and local development proof.
 */
function searchWilsyLocalDocumentSources({ keywords = [] } = {}) {
  const root = process.cwd().endsWith('/server')
    ? path.resolve(process.cwd(), '..')
    : process.cwd();

  const roots = [
    'server/templates',
    'server/data',
    'server/documents',
    'server/models',
    'server/services/documents',
    'server/services/document',
    'client/src/data',
    'client/src/components/artifacts',
    'client/src/components/documents',
    'client/src/components/document',
  ];

  const candidates = [];

  /**
   * @function scanWilsyLocalSourceDirectory
   * @description Recursively scans a bounded source directory for document source candidates.
   * @param {string} absoluteDir - Absolute directory path.
   * @returns {void} Mutates candidates.
   * @collaboration Local document source discovery and source resolver proof.
   */
  function scanWilsyLocalSourceDirectory(absoluteDir) {
    if (!fs.existsSync(absoluteDir)) {
      return;
    }

    const entries = fs.readdirSync(absoluteDir, { withFileTypes: true });

    entries.forEach((entry) => {
      const absolutePath = path.join(absoluteDir, entry.name);
      const relativePath = path.relative(root, absolutePath);

      if (/node_modules|dist|build|coverage|\.git|wilsyAI/i.test(relativePath)) {
        return;
      }

      if (entry.isDirectory()) {
        scanWilsyLocalSourceDirectory(absolutePath);
        return;
      }

      if (!/\.(js|jsx|json|md|txt)$/i.test(entry.name)) {
        return;
      }

      const content = fs.readFileSync(absolutePath, 'utf8').slice(0, 12000);
      const haystack = `${relativePath}\n${content}`.toLowerCase();
      const hasKeyword = keywords.some((keyword) => haystack.includes(keyword.toLowerCase()));
      const hasDocumentPosture =
        /tenant|brand|template|artifact|document|contract|agreement|form/i.test(haystack);

      if (hasKeyword && hasDocumentPosture) {
        candidates.push({
          path: relativePath,
          title: entry.name.replace(/\.(js|jsx|json|md|txt)$/i, ''),
          name: entry.name,
          status: 'LOCAL_SOURCE_CANDIDATE',
          sourceSystem: 'LOCAL_WILSY_DOCUMENT_SYSTEM',
          description: normalizeWilsyDocumentSourceText(content, 300),
        });
      }
    });
  }

  roots.forEach((relativeRoot) => {
    scanWilsyLocalSourceDirectory(path.join(root, relativeRoot));
  });

  return candidates.slice(0, 20);
}

/**
 * @function resolveWilsyTenantDocumentSource
 * @description Resolves the approved tenant document source before Wilsy prepares any business document draft.
 * @param {Object} params - Resolver params.
 * @param {string} params.tenantId - Tenant id.
 * @param {string} params.operatorId - Operator id.
 * @param {string} params.documentType - Requested document type.
 * @param {string} params.question - Operator question.
 * @returns {Promise<Object>} Source resolution result.
 * @collaboration Business Document Draft Bridge, tenant branded document system, Operator Model, and no-fake-generation boundary.
 */
export async function resolveWilsyTenantDocumentSource({
  tenantId = 'MASTER',
  operatorId = 'WILSY_OPERATOR',
  documentType = 'Business Document',
  question = '',
} = {}) {
  const keywords = buildWilsyDocumentSourceKeywords(documentType, question);
  const mongoCandidates = await searchWilsyMongoDocumentSources({ tenantId, keywords });
  const localCandidates = searchWilsyLocalDocumentSources({ keywords });
  const candidates = [...mongoCandidates, ...localCandidates]
    .map((source) => ({
      source,
      score: scoreWilsyDocumentSource(source, keywords),
    }))
    .filter((candidate) => candidate.score > 0)
    .sort((left, right) => right.score - left.score);

  const approved = candidates.find((candidate) => isWilsyApprovedDocumentSource(candidate.source));

  if (!approved) {
    return {
      status: 'SOURCE_MISSING',
      sourceFound: false,
      approved: false,
      tenantId,
      operatorId,
      documentType,
      sourceSystem: 'TENANT_DOCUMENT_LIBRARY',
      toolChecked: 'Tenant Document Library',
      checkedSources: [
        'Mongo tenant document/template/artifact collections',
        'Wilsy local document/artifact/template surfaces',
      ],
      message: candidates.length
        ? `I checked the tenant document library and found candidate sources, but none are approved for ${documentType}.`
        : `I checked the tenant document library and could not find an approved ${documentType} source.`,
      tenantBrand: buildWilsyTenantBrandFromSource({ tenantId }),
      sourceCandidatesChecked: candidates.slice(0, 6).map((candidate) => ({
        score: candidate.score,
        name:
          candidate.source.title ||
          candidate.source.name ||
          candidate.source.path ||
          candidate.source.collection,
        sourceSystem:
          candidate.source.sourceSystem || candidate.source.collection || 'TENANT_DOCUMENT_LIBRARY',
        approved: isWilsyApprovedDocumentSource(candidate.source),
      })),
      candidates: [],
      sections: [],
    };
  }

  const source = approved.source;
  const sections = extractWilsyDocumentSectionsFromSource(source);

  return {
    status: 'SOURCE_FOUND',
    sourceFound: true,
    approved: isWilsyApprovedDocumentSource(source),
    tenantId,
    operatorId,
    documentType,
    sourceSystem: source.sourceSystem || source.collection || 'TENANT_DOCUMENT_LIBRARY',
    toolChecked: 'Tenant Document Library',
    sourceName: source.title || source.name || source.documentType || documentType,
    sourceReference: source._id
      ? String(source._id)
      : source.path || source.collection || 'TENANT_DOCUMENT_SOURCE',
    sourcePath: source.path || null,
    collection: source.collection || null,
    tenantBrand: buildWilsyTenantBrandFromSource({ tenantId, source }),
    sections,
    candidates: candidates.slice(0, 6).map((candidate) => ({
      score: candidate.score,
      name:
        candidate.source.title ||
        candidate.source.name ||
        candidate.source.path ||
        candidate.source.collection,
      sourceSystem:
        candidate.source.sourceSystem || candidate.source.collection || 'TENANT_DOCUMENT_LIBRARY',
      approved: isWilsyApprovedDocumentSource(candidate.source),
    })),
    message: `I checked the tenant document library and found ${source.title || source.name || documentType}.`,
  };
}

export default resolveWilsyTenantDocumentSource;
