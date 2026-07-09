/* eslint-disable */
import * as knowledgeBaseManifestModule from '../../../client/src/data/wilsyKnowledgeBaseManifest.js';
import { resolveKnowledgeBaseVaultEntries } from './wilsyKnowledgeBaseVaultService.js';

/**
 * @function normalizeVaultRegistryText
 * @description Normalizes Knowledge Base registry text for backend search and category filtering.
 * @param {unknown} value Value to normalize.
 * @returns {string} Lowercase searchable text.
 * @collaboration Knowledge Base Vault registry search, manifest-backed metadata, and backend-driven filtering.
 */
function normalizeVaultRegistryText(value = '') {
  return String(value || '')
    .toLowerCase()
    .trim();
}

/**
 * @function resolveManifestRegistryEntries
 * @description Recursively resolves manifest artifact entries from any exported manifest shape without assuming a single array name.
 * @returns {Array<object>} Manifest registry entries.
 * @collaboration Knowledge Base manifest, dynamic registry metadata, future playbook indexing, and multi-document Vault search.
 */
function resolveManifestRegistryEntries() {
  const entries = [];
  const stack = Object.values(knowledgeBaseManifestModule || {});
  const seen = new WeakSet();

  while (stack.length) {
    const candidate = stack.shift();

    if (!candidate || typeof candidate !== 'object') {
      continue;
    }

    if (seen.has(candidate)) {
      continue;
    }

    seen.add(candidate);

    if (
      !Array.isArray(candidate) &&
      typeof candidate.id === 'string' &&
      typeof candidate.title === 'string'
    ) {
      entries.push(candidate);
      continue;
    }

    if (Array.isArray(candidate)) {
      candidate.forEach((item) => stack.push(item));
      continue;
    }

    Object.values(candidate).forEach((value) => {
      if (value && typeof value === 'object') {
        stack.push(value);
      }
    });
  }

  return entries;
}

/**
 * @function resolveRegistryCategory
 * @description Resolves a scalable registry category from explicit metadata or document fields.
 * @param {object} entry Vault entry.
 * @param {object} manifestEntry Manifest metadata entry.
 * @returns {string} Registry category.
 * @collaboration Dynamic Knowledge Base classification, playbook registry, and scalable Vault navigation.
 */
function resolveRegistryCategory(entry = {}, manifestEntry = {}) {
  const explicitCategory = manifestEntry.category || entry.category;

  if (explicitCategory) {
    return String(explicitCategory);
  }

  const source = [
    manifestEntry.playbookType,
    manifestEntry.artifactType,
    entry.artifactType,
    manifestEntry.title,
    entry.title,
    manifestEntry.module,
  ]
    .join(' ')
    .toLowerCase();

  if (source.includes('playbook')) return 'Playbooks';
  if (source.includes('policy')) return 'Policies';
  if (source.includes('training')) return 'Training';
  if (source.includes('manual')) return 'Manuals';
  if (source.includes('guide')) return 'Guides';
  if (source.includes('contract')) return 'Contracts';
  if (source.includes('report')) return 'Reports';
  if (source.includes('evidence')) return 'Evidence';

  return 'Documents';
}

/**
 * @function resolveRegistryTags
 * @description Resolves safe registry tags from manifest metadata and entry posture.
 * @param {object} entry Vault entry.
 * @param {object} manifestEntry Manifest metadata entry.
 * @returns {string[]} Registry tags.
 * @collaboration Manifest metadata, backend search facets, and future document discovery.
 */
function resolveRegistryTags(entry = {}, manifestEntry = {}) {
  const tags = Array.isArray(manifestEntry.tags) ? manifestEntry.tags : [];

  return Array.from(
    new Set(
      [
        ...tags,
        manifestEntry.module,
        manifestEntry.playbookType,
        manifestEntry.lifecycle,
        entry.sourcePosture,
        entry.proofStatus,
      ]
        .filter(Boolean)
        .map(String)
    )
  );
}

/**
 * @function enrichVaultRegistryEntry
 * @description Enriches a resolved Vault entry with manifest-backed registry metadata for search and categorization.
 * @param {object} entry Vault resolver entry.
 * @param {Map<string, object>} manifestById Manifest entries keyed by id.
 * @returns {object} Registry-enriched Vault entry.
 * @collaboration Live backend registry, metadata enrichment, proof routes, and frontend productivity workspace.
 */
function enrichVaultRegistryEntry(entry = {}, manifestById = new Map()) {
  const manifestEntry = manifestById.get(entry.id) || {};
  const category = resolveRegistryCategory(entry, manifestEntry);
  const tags = resolveRegistryTags(entry, manifestEntry);

  return {
    ...entry,
    category,
    tags,
    module: manifestEntry.module || entry.module || category,
    playbookType: manifestEntry.playbookType || entry.playbookType || category,
    owner: manifestEntry.owner || entry.generatedByDisplayName || 'Recorded owner',
    lifecycle: manifestEntry.lifecycle || 'locked',
    evidencePolicy: manifestEntry.evidencePolicy || 'saved_document_with_verification_record',
    registrySource: 'MANIFEST_METADATA_ENRICHED',
    searchCorpus: [
      entry.id,
      entry.title,
      entry.artifactType,
      entry.generatedByDisplayName,
      entry.sourcePosture,
      entry.proofStatus,
      entry.permissionMode,
      category,
      tags.join(' '),
      manifestEntry.module,
      manifestEntry.playbookType,
      manifestEntry.lifecycle,
      manifestEntry.evidencePolicy,
    ]
      .filter(Boolean)
      .join(' '),
  };
}

/**
 * @function resolveVaultRegistryFilters
 * @description Normalizes backend Vault search filters from route query/body.
 * @param {object} filters Incoming filters.
 * @returns {object} Normalized search filters.
 * @collaboration Backend-driven Vault search, category filters, and frontend live search contract.
 */
function resolveVaultRegistryFilters(filters = {}) {
  const query = normalizeVaultRegistryText(filters.query || filters.search || filters.q || '');
  const category = String(filters.category || filters.activeCategory || 'all').trim();
  const lifecycle = String(filters.lifecycle || 'all').trim();
  const moduleName = String(filters.module || 'all').trim();
  const playbookType = String(filters.playbookType || 'all').trim();

  return {
    query,
    category: category || 'all',
    lifecycle: lifecycle || 'all',
    module: moduleName || 'all',
    playbookType: playbookType || 'all',
  };
}

/**
 * @function doesVaultRegistryEntryMatchFilters
 * @description Checks whether an enriched registry entry matches backend search filters.
 * @param {object} entry Registry-enriched entry.
 * @param {object} filters Normalized filters.
 * @returns {boolean} Whether the entry matches.
 * @collaboration Search correctness, dynamic category facets, and scalable Vault document discovery.
 */
function doesVaultRegistryEntryMatchFilters(entry = {}, filters = {}) {
  const searchable = normalizeVaultRegistryText(entry.searchCorpus);
  const queryMatches = !filters.query || searchable.includes(filters.query);
  const categoryMatches = filters.category === 'all' || entry.category === filters.category;
  const lifecycleMatches = filters.lifecycle === 'all' || entry.lifecycle === filters.lifecycle;
  const moduleMatches = filters.module === 'all' || entry.module === filters.module;
  const playbookTypeMatches =
    filters.playbookType === 'all' || entry.playbookType === filters.playbookType;

  return (
    queryMatches && categoryMatches && lifecycleMatches && moduleMatches && playbookTypeMatches
  );
}

/**
 * @function buildVaultRegistryFacetBucket
 * @description Builds one backend facet bucket from registry-enriched Vault entries.
 * @param {Array<object>} entries Registry-enriched entries.
 * @param {string} fieldName Entry field name.
 * @param {string} allLabel Label for the all bucket.
 * @returns {Array<object>} Facet rows.
 * @collaboration Knowledge Base Vault backend facets, dynamic category filters, and production document discovery.
 */
function buildVaultRegistryFacetBucket(entries = [], fieldName = '', allLabel = 'All') {
  const counts = new Map();

  entries.forEach((entry) => {
    const value = entry[fieldName] || allLabel;
    counts.set(value, (counts.get(value) || 0) + 1);
  });

  return [
    { key: 'all', label: allLabel, count: entries.length },
    ...Array.from(counts.entries())
      .sort((first, second) => String(first[0]).localeCompare(String(second[0])))
      .map(([label, count]) => ({
        key: label,
        label,
        count,
      })),
  ];
}

/**
 * @function buildVaultRegistryFacets
 * @description Builds backend facets for categories, lifecycle, module, and playbook type.
 * @param {Array<object>} entries Registry-enriched entries.
 * @returns {object} Registry facets.
 * @collaboration Backend facets, frontend category rail, and multi-document Vault scaling.
 */
function buildVaultRegistryFacets(entries = []) {
  return {
    categories: buildVaultRegistryFacetBucket(entries, 'category'),
    lifecycle: buildVaultRegistryFacetBucket(entries, 'lifecycle'),
    modules: buildVaultRegistryFacetBucket(entries, 'module'),
    playbookTypes: buildVaultRegistryFacetBucket(entries, 'playbookType'),
  };
}

/**
 * @function resolveKnowledgeBaseVaultSearch
 * @description Resolves the manifest-backed Knowledge Base Vault with backend-driven search, category facets, and metadata enrichment.
 * @param {object} context Request context and filters.
 * @returns {Promise<object>} Filtered Vault payload.
 * @collaboration Production Knowledge Base registry, live backend search, manifest metadata, and scalable document workspace.
 */
export async function resolveKnowledgeBaseVaultSearch(context = {}) {
  const baseVault = await resolveKnowledgeBaseVaultEntries(context);
  const manifestEntries = resolveManifestRegistryEntries();
  const manifestById = new Map(manifestEntries.map((entry) => [entry.id, entry]));
  const enrichedEntries = (baseVault.entries || []).map((entry) =>
    enrichVaultRegistryEntry(entry, manifestById)
  );
  const filters = resolveVaultRegistryFilters(context.filters || context);
  const filteredEntries = enrichedEntries.filter((entry) =>
    doesVaultRegistryEntryMatchFilters(entry, filters)
  );

  return {
    ...baseVault,
    sourceMode: baseVault.sourceMode,
    registryMode: 'MANIFEST_BACKED_DYNAMIC_REGISTRY',
    searchMode: 'BACKEND_FILTERED',
    filters,
    facets: buildVaultRegistryFacets(enrichedEntries),
    totalEntryCount: enrichedEntries.length,
    filteredEntryCount: filteredEntries.length,
    entries: filteredEntries.map((entry) => {
      const { searchCorpus, ...safeEntry } = entry;
      return safeEntry;
    }),
  };
}
