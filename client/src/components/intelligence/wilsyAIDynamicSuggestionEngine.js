/* eslint-disable */

/**
 * @constant WILSY_AI_SUGGESTION_MEMORY_KEY
 * @description Local runtime key for non-sensitive Wilsy AI suggestion exposure and usage memory.
 */
export const WILSY_AI_SUGGESTION_MEMORY_KEY = 'wilsy.ai.dynamicSuggestionMemory.v1';

/**
 * @function normalizeWilsySuggestionArray
 * @description Normalizes unknown collection input into a compact array for suggestion generation.
 * @param {*} value - Candidate value.
 * @returns {Array} Normalized array.
 * @collaboration Wilsy AI dynamic suggestion engine, operator model adapters, and source-safe array normalization.
 */
export function normalizeWilsySuggestionArray(value) {
  if (!value) {
    return [];
  }

  if (Array.isArray(value)) {
    return value.filter(Boolean);
  }

  if (typeof value === 'object') {
    return Object.values(value).filter(Boolean);
  }

  return [];
}

/**
 * @function sanitizeWilsySuggestionText
 * @description Converts unknown text into a safe compact display string.
 * @param {*} value - Candidate text.
 * @param {string} fallback - Fallback text.
 * @returns {string} Safe text.
 * @collaboration Wilsy AI dynamic suggestions, operator-facing prompt labels, and workspace-safe display text.
 */
export function sanitizeWilsySuggestionText(value, fallback = '') {
  const text = String(value || fallback || '').replace(/\s+/g, ' ').trim();
  return text;
}

/**
 * @function resolveWilsySuggestionWorkspace
 * @description Resolves the active workspace from live model and context without hard-coding a CRM label.
 * @param {Object} model - Wilsy operator model.
 * @param {Object} context - Runtime workspace context.
 * @returns {string} Active workspace label.
 * @collaboration Wilsy AI composer, live workspace context, tenant-aware UI language, and dynamic suggestion naming.
 */
export function resolveWilsySuggestionWorkspace(model = {}, context = {}) {
  return sanitizeWilsySuggestionText(
    context.workspace ||
      context.focus ||
      model.workspace ||
      model.module ||
      model.contextLabel ||
      model.surface ||
      model.domain,
    'Workspace',
  );
}

/**
 * @function hashWilsySuggestionSeed
 * @description Builds a deterministic positive hash used to rotate suggestions without fixed menu order.
 * @param {*} value - Seed input.
 * @returns {number} Numeric hash.
 * @collaboration Wilsy AI suggestion entropy, non-repeating recommendations, local usage memory, and deterministic test harnesses.
 */
export function hashWilsySuggestionSeed(value = '') {
  return Array.from(String(value || '')).reduce((hash, char) => {
    return ((hash << 5) - hash + char.charCodeAt(0)) >>> 0;
  }, 2166136261);
}

/**
 * @function normalizeWilsySuggestionCandidate
 * @description Normalizes a raw candidate into an executable Wilsy AI suggestion descriptor.
 * @param {Object} candidate - Raw candidate.
 * @returns {Object} Normalized suggestion.
 * @collaboration Wilsy AI suggestion ranking, command token prompts, source trace guidance, and operator execution loops.
 */
export function normalizeWilsySuggestionCandidate(candidate = {}) {
  const label = sanitizeWilsySuggestionText(candidate.label || candidate.title || candidate.name || candidate.prompt, 'Inspect workspace');
  const prompt = sanitizeWilsySuggestionText(candidate.prompt || candidate.description || label, label);
  const seed = sanitizeWilsySuggestionText(candidate.id || candidate.intent || label || prompt, 'wilsy-suggestion');

  return {
    id: seed.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '') || 'wilsy_suggestion',
    label,
    prompt,
    intent: sanitizeWilsySuggestionText(candidate.intent, 'workspace_follow_up'),
    origin: sanitizeWilsySuggestionText(candidate.origin, 'workspace'),
    score: Number.isFinite(Number(candidate.score)) ? Number(candidate.score) : 1,
  };
}

/**
 * @function resolveWilsySuggestionMemory
 * @description Loads non-sensitive suggestion exposure memory from storage when available.
 * @param {Storage|null} storage - Optional storage adapter.
 * @returns {Object} Suggestion memory payload.
 * @collaboration Wilsy AI dynamic suggestions, local operator continuity, non-repeating recommendation memory, and safe browser persistence.
 */
export function resolveWilsySuggestionMemory(storage = null) {
  const runtimeStorage =
    storage ||
    (typeof window !== 'undefined' && window.localStorage ? window.localStorage : null);

  if (!runtimeStorage) {
    return { recentIds: [], usage: {}, openedAt: 0 };
  }

  try {
    const parsed = JSON.parse(runtimeStorage.getItem(WILSY_AI_SUGGESTION_MEMORY_KEY) || '{}');

    return {
      recentIds: Array.isArray(parsed.recentIds) ? parsed.recentIds.slice(0, 24) : [],
      usage: parsed.usage && typeof parsed.usage === 'object' ? parsed.usage : {},
      openedAt: Number(parsed.openedAt || 0),
    };
  } catch (error) {
    return { recentIds: [], usage: {}, openedAt: 0 };
  }
}

/**
 * @function saveWilsySuggestionMemory
 * @description Saves bounded suggestion exposure memory without saving model knowledge or sensitive content.
 * @param {Object} memory - Suggestion memory payload.
 * @param {Storage|null} storage - Optional storage adapter.
 * @returns {Object} Saved memory payload.
 * @collaboration Wilsy AI dynamic suggestions, local recommendation memory, non-sensitive browser persistence, and operator usage growth.
 */
export function saveWilsySuggestionMemory(memory = {}, storage = null) {
  const nextMemory = {
    recentIds: Array.isArray(memory.recentIds) ? memory.recentIds.slice(0, 24) : [],
    usage: memory.usage && typeof memory.usage === 'object' ? memory.usage : {},
    openedAt: Number(memory.openedAt || Date.now()),
  };
  const runtimeStorage =
    storage ||
    (typeof window !== 'undefined' && window.localStorage ? window.localStorage : null);

  if (runtimeStorage) {
    try {
      runtimeStorage.setItem(WILSY_AI_SUGGESTION_MEMORY_KEY, JSON.stringify(nextMemory));
    } catch (error) {
      return nextMemory;
    }
  }

  return nextMemory;
}

/**
 * @function recordWilsyAISuggestionUsage
 * @description Records which suggestion the operator selected so future recommendations can grow from actual usage.
 * @param {Object} suggestion - Selected suggestion descriptor.
 * @param {Storage|null} storage - Optional storage adapter.
 * @returns {Object} Updated suggestion memory.
 * @collaboration Wilsy AI operator usage, dynamic recommendation growth, contextual prompts, and local non-sensitive memory.
 */
export function recordWilsyAISuggestionUsage(suggestion = {}, storage = null) {
  const memory = resolveWilsySuggestionMemory(storage);
  const stableId = sanitizeWilsySuggestionText(
    suggestion.stableId || suggestion.sourceId || suggestion.id || suggestion.intent || suggestion.label || suggestion.prompt,
    'wilsy_suggestion',
  );
  const id = stableId.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '') || 'wilsy_suggestion';

  return saveWilsySuggestionMemory(
    {
      ...memory,
      usage: {
        ...memory.usage,
        [id]: Number(memory.usage?.[id] || 0) + 1,
      },
    },
    storage,
  );
}

/**
 * @function resolveWilsyAIConversationTitle
 * @description Creates a saved-chat title from workspace and prompt context without generic placeholders.
 * @param {Object} payload - Title payload.
 * @returns {string} Dynamic chat title.
 * @collaboration Wilsy AI saved chats, workspace memory, contextual naming, and operator continuity.
 */
export function resolveWilsyAIConversationTitle(payload = {}) {
  const workspace = sanitizeWilsySuggestionText(payload.workspace, 'Workspace');
  const promptText = sanitizeWilsySuggestionText(payload.promptText || payload.prompt || payload.question, '');
  const existingTitle = sanitizeWilsySuggestionText(payload.thread?.title, '');
  const existingIsPlaceholder = /new chat|current workspace|workspace conversation|saved wilsy ai chat/i.test(existingTitle);

  if (!promptText && existingTitle && !existingIsPlaceholder) {
    return existingTitle;
  }

  if (!promptText) {
    return `${workspace} · New conversation`;
  }

  const normalized = promptText
    .replace(/^open\s+/i, '')
    .replace(/^tell me\s+/i, '')
    .replace(/^walk me through\s+/i, '')
    .replace(/^show me\s+/i, '')
    .replace(/^check whether\s+/i, 'Check ')
    .replace(/\?+$/g, '')
    .trim();

  const focus = normalized.length > 72 ? `${normalized.slice(0, 69)}...` : normalized;
  return `${workspace} · ${focus || promptText.slice(0, 72)}`;
}

/**
 * @function buildWilsyDynamicSuggestions
 * @description Builds six dynamic, non-repeating, context-aware suggestions from live workspace data, typing, usage, and source posture.
 * @param {Object} payload - Suggestion generation payload.
 * @returns {Array} Six suggestion descriptors.
 * @collaboration Wilsy AI composer, live CRM/workspace context, usage memory, source trace, evidence anchors, and approval-safe model growth.
 */
export function buildWilsyDynamicSuggestions(payload = {}) {
  const model = payload.model || {};
  const context = payload.context || {};
  const promptTextRaw = sanitizeWilsySuggestionText(payload.promptText, '');
  const promptText = promptTextRaw.toLowerCase();
  const workspace = resolveWilsySuggestionWorkspace(model, context);
  const refreshKey = Number(payload.refreshKey || Date.now());
  const memory = payload.rotationMemory || resolveWilsySuggestionMemory(payload.storage || null);
  const commandTokens = normalizeWilsySuggestionArray(
    model.commandTokens?.length
      ? model.commandTokens
      : model.executionThread?.length
        ? model.executionThread
        : model.playableActions?.length
          ? model.playableActions
          : model.actions,
  );
  const sourceTrace = normalizeWilsySuggestionArray(model.sourceTrace);
  const evidenceAnchors = normalizeWilsySuggestionArray(model.evidenceAnchors);
  const telemetryPacks = normalizeWilsySuggestionArray(model.telemetryPacks);
  const conversations = normalizeWilsySuggestionArray(payload.conversationThreads);
  const candidates = [];

  if (promptTextRaw) {
    candidates.push(
      normalizeWilsySuggestionCandidate({
        id: 'typed_deep_search',
        label: `Go deeper on "${promptTextRaw.slice(0, 46)}${promptTextRaw.length > 46 ? '...' : ''}"`,
        prompt: `Go deeper on this using ${workspace} authority, evidence, source routes, release readiness, queue hygiene, and repair context: ${promptTextRaw}`,
        intent: 'deep_follow_up',
        origin: 'typeahead',
        score: 42,
      }),
      normalizeWilsySuggestionCandidate({
        id: 'typed_find_blocker',
        label: 'Find the real blocker behind this',
        prompt: `Find the real blocker behind this question and give me the next safe move: ${promptTextRaw}`,
        intent: 'blocker_search',
        origin: 'typeahead',
        score: 41,
      }),
      normalizeWilsySuggestionCandidate({
        id: 'typed_stage_candidate',
        label: 'Stage an answer candidate if this is not approved',
        prompt: `If this cannot be answered from approved ${workspace} sources, draft the answer candidate and stage it for approval instead of saving it into the model: ${promptTextRaw}`,
        intent: 'approval_candidate',
        origin: 'typeahead',
        score: 40,
      }),
    );
  }

  commandTokens.slice(0, 12).forEach((token, index) => {
    const label = sanitizeWilsySuggestionText(token.label || token.title || token.name || token.intent, `Route ${index + 1}`);
    const route = sanitizeWilsySuggestionText(token.route || token.href || token.url, '');

    candidates.push(
      normalizeWilsySuggestionCandidate({
        id: `route_${index}_${label}`,
        label: `Open ${label}`,
        prompt: route
          ? `Open ${label} and explain the safest next move through ${route}`
          : `Open ${label} and explain the safest next move`,
        intent: token.intent || 'command_route',
        origin: 'command_token',
        score: 26 - index,
      }),
    );
  });

  sourceTrace.slice(0, 8).forEach((source, index) => {
    const label = sanitizeWilsySuggestionText(source.label || source.surface || source.source || source.statusLabel, `Source ${index + 1}`);

    candidates.push(
      normalizeWilsySuggestionCandidate({
        id: `source_${index}_${label}`,
        label: `Read ${label}`,
        prompt: `Read ${label} and tell me what is blocking ${workspace}`,
        intent: 'source_read',
        origin: 'source_trace',
        score: 20 - index,
      }),
    );
  });

  evidenceAnchors.slice(0, 8).forEach((anchor, index) => {
    const label = sanitizeWilsySuggestionText(anchor.label || anchor.title || anchor.name || anchor, `Evidence ${index + 1}`);

    candidates.push(
      normalizeWilsySuggestionCandidate({
        id: `evidence_${index}_${label}`,
        label: `Verify ${label}`,
        prompt: `Verify ${label} and show what evidence is still missing before ${workspace} moves`,
        intent: 'evidence_anchor',
        origin: 'evidence_anchor',
        score: 21 - index,
      }),
    );
  });

  telemetryPacks.slice(0, 6).forEach((pack, index) => {
    const label = sanitizeWilsySuggestionText(pack.label || pack.title || pack.name, `Telemetry ${index + 1}`);

    candidates.push(
      normalizeWilsySuggestionCandidate({
        id: `telemetry_${index}_${label}`,
        label: `Inspect ${label}`,
        prompt: `Inspect ${label} and surface the next operational risk in ${workspace}`,
        intent: 'telemetry_scan',
        origin: 'telemetry',
        score: 16 - index,
      }),
    );
  });

  [
    ['outstanding', `What is still outstanding in ${workspace}?`, `Tell me what is still outstanding in ${workspace} using authority, evidence, release, queue, and repair context.`, 'what_next', 14],
    ['authority', `Who must approve the next ${workspace} move?`, `Walk me through the authority path for ${workspace} and identify reviewer, approver, release owner, and mutation boundary.`, 'authority_graph', 13],
    ['evidence', `Which evidence is missing before ${workspace} moves?`, `Show the evidence gaps before ${workspace} moves and separate proof already present from proof still missing.`, 'evidence_checklist', 12],
    ['release', `Is ${workspace} safe to release?`, `Check whether ${workspace} is safe to release and explain what blocks release if approval or receipts are missing.`, 'release_readiness', 11],
    ['queue', `Where is ${workspace} queue drift?`, `Find stale reviews, orphan approvals, repeated pending states, and missing receipts in ${workspace}.`, 'queue_hygiene', 10],
    ['repair', `What repair route should ${workspace} open?`, `Prepare the repair route for missing role, receipt, permission, source binding, or packet proof in ${workspace}.`, 'repair_route', 9],
    ['approval', `What needs approval in ${workspace}?`, `Separate approved, pending, rejected, and unverified decisions in ${workspace}.`, 'approval_map', 8],
    ['handover', `Prepare the ${workspace} handover brief`, `Prepare a compact handover brief for ${workspace} with risks, proof gaps, owner, and next action.`, 'handover_brief', 7],
  ].forEach(([id, label, prompt, intent, score]) => {
    candidates.push(
      normalizeWilsySuggestionCandidate({
        id: `${workspace}_${id}`,
        label,
        prompt,
        intent,
        origin: 'workspace_model',
        score,
      }),
    );
  });

  conversations
    .flatMap((thread) => normalizeWilsySuggestionArray(thread.turns))
    .slice(0, 12)
    .forEach((turn, index) => {
      const prompt = sanitizeWilsySuggestionText(turn.promptText || turn.prompt || turn.question, '');

      if (prompt) {
        candidates.push(
          normalizeWilsySuggestionCandidate({
            id: `memory_${index}_${prompt}`,
            label: prompt.length > 72 ? `${prompt.slice(0, 69)}...` : prompt,
            prompt: `Continue this ${workspace} conversation and identify the next safe move: ${prompt}`,
            intent: 'conversation_memory',
            origin: 'conversation_memory',
            score: 9 + Math.min(index, 4),
          }),
        );
      }
    });

  const seen = new Set();
  const unique = candidates.filter((candidate) => {
    const key = `${candidate.label}::${candidate.prompt}`.toLowerCase();

    if (seen.has(key)) {
      return false;
    }

    seen.add(key);
    return true;
  });

  const seed = hashWilsySuggestionSeed(
    [
      workspace,
      promptTextRaw,
      refreshKey,
      unique.length,
      memory.openedAt,
      Object.keys(memory.usage || {}).join('|'),
    ].join('::'),
  );
  const recent = new Set(memory.recentIds || []);
  const scored = unique
    .map((candidate, index) => {
      const baseId = candidate.id;
      const entropy = (hashWilsySuggestionSeed(`${baseId}:${seed}:${index}`) % 47) / 2.5;
      const recentPenalty = recent.has(baseId) ? -80 : 0;
      const usageBoost = Math.min(Number(memory.usage?.[baseId] || 0), 12);

      return {
        ...candidate,
        sourceId: baseId,
        rank: candidate.score + entropy + usageBoost + recentPenalty,
      };
    })
    .sort((first, second) => second.rank - first.rank);

  const selected = scored.slice(0, 6);

  if (!promptTextRaw && selected.length && payload.persistExposure !== false) {
    saveWilsySuggestionMemory(
      {
        ...memory,
        recentIds: [...selected.map((item) => item.sourceId), ...(memory.recentIds || [])].slice(0, 24),
        openedAt: Date.now(),
      },
      payload.storage || null,
    );
  }

  return selected.map((item, index) => ({
    ...item,
    id: `${item.sourceId}_${refreshKey}_${index}`,
    stableId: item.sourceId,
  }));
}
