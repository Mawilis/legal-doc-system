/* eslint-disable */
import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { buildWilsyOperatorIntelligence } from './wilsyOperatorIntelligenceEngine.js';
import styles from './WilsyOSIntelligenceDock.module.css';
import { buildWilsyDynamicSuggestions, recordWilsyAISuggestionUsage } from './wilsyAIDynamicSuggestionEngine.js';
import { clearWilsyAIConversationThreads, createWilsyAIConversationThread, loadWilsyAIConversationThreads, persistWilsyAIConversationTurn, saveWilsyAIConversationThreads } from './wilsyAIConversationHistoryEngine.js';





/**
 * @function normalizeWilsyFG85LeadCreatePromptText
 * @description Normalizes the visible global Wilsy AI Ask prompt before governed Lead draft extraction.
 * @param {*} value - Raw prompt value.
 * @returns {string} Trimmed prompt text.
 * @collaboration Global Wilsy AI Ask form, CRM Setup copilot, Leads Create surface, and operator-reviewed save flow.
 */
function normalizeWilsyFG85LeadCreatePromptText(value = '') {
  return String(value || '').trim();
}

/**
 * @function extractWilsyFG85LeadCreateField
 * @description Extracts bounded Create Lead field values from the global Ask prompt.
 * @param {string} text - Prompt text.
 * @param {RegExp[]} patterns - Candidate extraction patterns.
 * @returns {string} Extracted field value.
 * @collaboration Global Ask parser, Create Lead field parity, pending draft storage, and no-blind-write posture.
 */
function extractWilsyFG85LeadCreateField(text = '', patterns = []) {
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match?.[1]) {
      return normalizeWilsyFG85LeadCreatePromptText(match[1]).replace(/[.;]+$/g, '').trim();
    }
  }

  return '';
}

/**
 * @function buildWilsyFG85GlobalLeadCreateDraft
 * @description Builds a governed Lead draft from a global Ask prompt without executing backend create.
 * @param {string} prompt - Visible global Ask prompt.
 * @returns {Object|null} Event detail with Lead draft, or null.
 * @collaboration Floating Wilsy AI, CRM home, Add Lead command, Leads Create hydration, and human Save approval.
 */
function buildWilsyFG85GlobalLeadCreateDraft(prompt = '') {
  /* P60K5Q10FG85_GLOBAL_ASK_CAPTURE_LEAD_CREATE_DRAFT */
  const text = normalizeWilsyFG85LeadCreatePromptText(prompt);
  const lower = text.toLowerCase();

  if (!/\b(create|add|capture|prepare|draft|register)\b/.test(lower) || !/\b(lead|prospect)\b/.test(lower)) {
    return null;
  }

  const name = extractWilsyFG85LeadCreateField(text, [
    /\blead\s+(?:named|called)\s+([^.;]+?)(?:\s+at\s+|\s+company|\s+with\s+email|\s+email|\s+phone|\s+mobile|\s+title|\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    /\b(?:create|add|capture|prepare|draft|register)\s+(?:a\s+)?(?:new\s+)?(?:lead|prospect)\s+(?:named|called|for)?\s*([^.;]+?)(?:\s+at\s+|\s+company|\s+with\s+email|\s+email|\s+phone|\s+mobile|\s+title|\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
  ]);

  const company = extractWilsyFG85LeadCreateField(text, [
    /\bcompany\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+with\s+email|\s+email|\s+phone|\s+mobile|\s+title|\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    /\bat\s+([^.;]+?)(?:\s+with\s+email|\s+email|\s+phone|\s+mobile|\s+title|\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
  ]);

  const email = extractWilsyFG85LeadCreateField(text, [
    /\bemail(?:\s+address)?\s*(?:is|=|:)?\s*([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})/i,
    /\b([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})\b/i,
  ]);

  const phone = extractWilsyFG85LeadCreateField(text, [
    /\bphone\s*(?:number)?\s*(?:is|=|:)?\s*(\+?[0-9][0-9\s().-]{6,})/i,
  ]);

  const mobile = extractWilsyFG85LeadCreateField(text, [
    /\bmobile\s*(?:number)?\s*(?:is|=|:)?\s*(\+?[0-9][0-9\s().-]{6,})/i,
  ]);

  const estimatedDealValue = extractWilsyFG85LeadCreateField(text, [
    /\b(?:estimated\s+deal\s+value|deal\s+value|pipeline\s+value|value)\s*(?:is|=|:)?\s*(?:R|ZAR)?\s*([0-9][0-9\s,._]*)/i,
  ]).replace(/[^0-9.]/g, '');

  const priority = extractWilsyFG85LeadCreateField(text, [
    /\bpriority\s*(?:is|=|:)?\s*(urgent|high|medium|low)\b/i,
  ]);

  const source = extractWilsyFG85LeadCreateField(text, [
    /\bsource\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+website|\s+employees|\s+due|\s+notes|$)/i,
  ]) || (lower.includes('referral') ? 'Referral' : lower.includes('partner') ? 'Partner' : lower.includes('outbound') ? 'Outbound' : 'Wilsy AI');

  const draft = {
    module: 'Lead',
    name,
    company,
    email,
    phone,
    mobile: mobile || phone,
    countryCode: 'ZA',
    mobileCountryCode: 'ZA',
    title: extractWilsyFG85LeadCreateField(text, [
      /\btitle\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    ]),
    priority: priority ? priority[0].toUpperCase() + priority.slice(1).toLowerCase() : 'Medium',
    estimatedDealValue,
    dealValue: estimatedDealValue,
    industry: extractWilsyFG85LeadCreateField(text, [
      /\bindustry\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    ]),
    stage: extractWilsyFG85LeadCreateField(text, [
      /\bstage\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    ]) || 'NURTURE',
    status: extractWilsyFG85LeadCreateField(text, [
      /\bstatus\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    ]) || 'NEW',
    owner: extractWilsyFG85LeadCreateField(text, [
      /\bowner\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    ]),
    source,
    website: extractWilsyFG85LeadCreateField(text, [
      /\b(?:website|site)\s*(?:is|=|:)?\s*(https?:\/\/[^\s,;]+|[A-Z0-9.-]+\.[A-Z]{2,})/i,
    ]),
    employees: extractWilsyFG85LeadCreateField(text, [
      /\bemployees\s*(?:is|=|:)?\s*([0-9][0-9\s,._]*)/i,
    ]).replace(/[^0-9.]/g, ''),
    dueDate: extractWilsyFG85LeadCreateField(text, [
      /\b(?:due|follow\s*up|follow-up)\s*(?:date)?\s*(?:is|=|:)?\s*([0-9]{4}[-/][0-9]{2}[-/][0-9]{2})/i,
    ]).replace(/\//g, '-'),
    notes: extractWilsyFG85LeadCreateField(text, [
      /\bnotes\s*(?:are|is|=|:)?\s*(.+)$/i,
    ]) || text,
    description: extractWilsyFG85LeadCreateField(text, [
      /\bnotes\s*(?:are|is|=|:)?\s*(.+)$/i,
    ]) || text,
  };

  Object.keys(draft).forEach((key) => {
    if (draft[key] === '') delete draft[key];
  });

  if (!draft.name || !draft.company || !draft.email) {
    return null;
  }

  return {
    source: 'P60K5Q10FG85_GLOBAL_ASK_CAPTURE_LEAD_CREATE_DRAFT',
    leadCreateDraft: draft,
    createLeadDraft: draft,
    packet: {
      mutation: 'NO_BACKEND_MUTATION_REQUIRES_OPERATOR_SAVE',
      operatorModel: {
        intent: 'create_lead',
        action: 'prepare_create_lead_draft',
        leadCreateDraft: draft,
        createLeadDraft: draft,
        answer: `I prepared a governed Create Lead draft for ${draft.name} at ${draft.company}. Review it and press Save.`,
      },
      toolRuns: [
        {
          tool: 'crm_lead_create_draft',
          status: 'APPROVAL_REQUIRED',
          mutation: 'NO_BACKEND_MUTATION_REQUIRES_OPERATOR_SAVE',
          leadCreateDraft: draft,
          createLeadDraft: draft,
        },
      ],
    },
    generatedAt: new Date().toISOString(),
  };
}

/**
 * @function clickWilsyFG85VisibleAddLeadControl
 * @description Clicks the visible CRM Add Lead/New Lead/Create Lead button using the real application control path.
 * @returns {boolean} True when a matching button was clicked.
 * @collaboration CRM home Add Lead button, Leads module create mode, global AI draft routing, and existing create handlers.
 */
function clickWilsyFG85VisibleAddLeadControl() {
  if (typeof document === 'undefined') return false;

  const buttons = Array.from(document.querySelectorAll('button'));
  const target = buttons.find((button) => {
    const label = String(button.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();
    return ['add lead', 'new lead', 'create lead'].some((candidate) => label.includes(candidate));
  });

  if (!target) return false;

  target.click();
  return true;
}

/**
 * @function dispatchWilsyFG85GlobalLeadDraft
 * @description Stores and dispatches the governed Lead draft for the mounted or next-mounted Leads workspace.
 * @param {Object} eventDetail - Create Lead draft detail.
 * @returns {boolean} True when dispatched.
 * @collaboration sessionStorage, localStorage fallback, CustomEvent bridge, CRM home Add Lead control, and Leads Create hydration.
 */
function dispatchWilsyFG85GlobalLeadDraft(eventDetail = {}) {
  /* P60K5Q10FG85_GLOBAL_ASK_CAPTURE_LEAD_CREATE_ROUTER */
  if (typeof window === 'undefined' || !eventDetail?.leadCreateDraft) return false;

  const serialized = JSON.stringify(eventDetail);

  /* P60K5Q10FG87B_PENDING_DRAFT_GLOBAL_MEMORY */
  window.__WILSY_CRM_LEADS_PENDING_CREATE_DRAFT__ = eventDetail;

  try {
    window.sessionStorage?.setItem?.('wilsy.crm.leads.pendingCreateDraft', serialized);
  } catch {
    // sessionStorage is optional.
  }

  try {
    window.localStorage?.setItem?.('wilsy.crm.leads.pendingCreateDraft', serialized);
  } catch {
    // localStorage is optional.
  }

  window.dispatchEvent(new CustomEvent('wilsy:crm-leads-create-draft', { detail: eventDetail }));
  window.dispatchEvent(new CustomEvent('wilsy:crm-leads-open-request', { detail: { mode: 'create', ...eventDetail } }));
  window.dispatchEvent(new CustomEvent('wilsy:crm-module-open-request', { detail: { module: 'leads', mode: 'create', ...eventDetail } }));

  window.setTimeout(() => {
    if (!document.querySelector('[data-wilsy-lead-create-surface="P60K5Q10FG79_CREATE_AI_AWARE_SURFACE"]')) {
      clickWilsyFG85VisibleAddLeadControl();
    }

    /* P60K5Q10FG87B_LATE_REPLAY_AFTER_ADD_LEAD_CLICK */
    window.dispatchEvent(new CustomEvent('wilsy:crm-leads-create-draft', { detail: eventDetail }));
  }, 40);

  window.setTimeout(() => {
    if (!document.querySelector('[data-wilsy-lead-create-surface="P60K5Q10FG79_CREATE_AI_AWARE_SURFACE"]')) {
      clickWilsyFG85VisibleAddLeadControl();
    }

    window.dispatchEvent(new CustomEvent('wilsy:crm-leads-create-draft', { detail: eventDetail }));
  }, 220);

  window.setTimeout(() => {
    window.dispatchEvent(new CustomEvent('wilsy:crm-leads-create-draft', { detail: eventDetail }));
  }, 520);

  window.setTimeout(() => {
    window.dispatchEvent(new CustomEvent('wilsy:crm-leads-create-draft', { detail: eventDetail }));
  }, 900);

  return true;
}


/**
 * @function normalizeWilsyFG84LeadCreatePromptText
 * @description Normalizes global Wilsy AI create-lead prompt text before local governed draft extraction.
 * @param {*} value - Prompt value.
 * @returns {string} Trimmed prompt text.
 * @collaboration Global Wilsy AI Ask bar, CRM Setup copilot, Leads Create surface, and no-blind-write draft review.
 */
function normalizeWilsyFG84LeadCreatePromptText(value = '') {
  return String(value || '').trim();
}

/**
 * @function extractWilsyFG84LeadCreateField
 * @description Extracts bounded Lead create values from natural language prompt text.
 * @param {string} text - Prompt text.
 * @param {RegExp[]} patterns - Candidate extraction patterns.
 * @returns {string} Extracted value.
 * @collaboration Global Wilsy AI prompt parser, Create Lead parity fields, and operator-reviewed save flow.
 */
function extractWilsyFG84LeadCreateField(text = '', patterns = []) {
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match?.[1]) {
      return normalizeWilsyFG84LeadCreatePromptText(match[1])
        .replace(/[.;]+$/g, '')
        .trim();
    }
  }

  return '';
}

/**
 * @function buildWilsyFG84GlobalLeadCreateDraft
 * @description Builds a governed Lead create draft locally from the global Ask prompt without mutating the backend.
 * @param {string} prompt - Operator prompt.
 * @returns {Object|null} Draft event payload or null.
 * @collaboration Floating/global Wilsy AI, CRM Setup copilot, Leads Create receiver, pending draft storage, and human approval.
 */
function buildWilsyFG84GlobalLeadCreateDraft(prompt = '') {
  /* P60K5Q10FG84_GLOBAL_ASK_DIRECT_LEAD_CREATE_DRAFT */
  const text = normalizeWilsyFG84LeadCreatePromptText(prompt);
  const lower = text.toLowerCase();

  if (!/\b(create|add|capture|prepare|draft|register)\b/.test(lower) || !/\b(lead|prospect)\b/.test(lower)) {
    return null;
  }

  const name = extractWilsyFG84LeadCreateField(text, [
    /\blead\s+(?:named|called)\s+([^.;]+?)(?:\s+at\s+|\s+company|\s+with\s+email|\s+email|\s+phone|\s+mobile|\s+title|\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    /\b(?:create|add|capture|prepare|draft|register)\s+(?:a\s+)?(?:new\s+)?(?:lead|prospect)\s+(?:named|called|for)?\s*([^.;]+?)(?:\s+at\s+|\s+company|\s+with\s+email|\s+email|\s+phone|\s+mobile|\s+title|\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
  ]);

  const company = extractWilsyFG84LeadCreateField(text, [
    /\bcompany\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+with\s+email|\s+email|\s+phone|\s+mobile|\s+title|\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    /\bat\s+([^.;]+?)(?:\s+with\s+email|\s+email|\s+phone|\s+mobile|\s+title|\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
  ]);

  const email = extractWilsyFG84LeadCreateField(text, [
    /\bemail(?:\s+address)?\s*(?:is|=|:)?\s*([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})/i,
    /\b([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})\b/i,
  ]);

  const phone = extractWilsyFG84LeadCreateField(text, [
    /\bphone\s*(?:number)?\s*(?:is|=|:)?\s*(\+?[0-9][0-9\s().-]{6,})/i,
  ]);

  const mobile = extractWilsyFG84LeadCreateField(text, [
    /\bmobile\s*(?:number)?\s*(?:is|=|:)?\s*(\+?[0-9][0-9\s().-]{6,})/i,
  ]);

  const estimatedDealValue = extractWilsyFG84LeadCreateField(text, [
    /\b(?:estimated\s+deal\s+value|deal\s+value|pipeline\s+value|value)\s*(?:is|=|:)?\s*(?:R|ZAR)?\s*([0-9][0-9\s,._]*)/i,
  ]).replace(/[^0-9.]/g, '');

  const priority = extractWilsyFG84LeadCreateField(text, [
    /\bpriority\s*(?:is|=|:)?\s*(urgent|high|medium|low)\b/i,
  ]);

  const source = extractWilsyFG84LeadCreateField(text, [
    /\bsource\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+website|\s+employees|\s+due|\s+notes|$)/i,
  ]) || (lower.includes('referral') ? 'Referral' : lower.includes('partner') ? 'Partner' : lower.includes('outbound') ? 'Outbound' : 'Wilsy AI');

  const draft = {
    module: 'Lead',
    name,
    company,
    email,
    phone,
    mobile: mobile || phone,
    countryCode: 'ZA',
    mobileCountryCode: 'ZA',
    title: extractWilsyFG84LeadCreateField(text, [
      /\btitle\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+priority|\s+value|\s+industry|\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    ]),
    priority: priority ? priority[0].toUpperCase() + priority.slice(1).toLowerCase() : 'Medium',
    estimatedDealValue,
    dealValue: estimatedDealValue,
    industry: extractWilsyFG84LeadCreateField(text, [
      /\bindustry\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+stage|\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    ]),
    stage: extractWilsyFG84LeadCreateField(text, [
      /\bstage\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+status|\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    ]) || 'NURTURE',
    status: extractWilsyFG84LeadCreateField(text, [
      /\bstatus\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+owner|\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    ]) || 'NEW',
    owner: extractWilsyFG84LeadCreateField(text, [
      /\bowner\s*(?:is|=|:)?\s*([^.;]+?)(?:\s+source|\s+website|\s+employees|\s+due|\s+notes|$)/i,
    ]),
    source,
    website: extractWilsyFG84LeadCreateField(text, [
      /\b(?:website|site)\s*(?:is|=|:)?\s*(https?:\/\/[^\s,;]+|[A-Z0-9.-]+\.[A-Z]{2,})/i,
    ]),
    employees: extractWilsyFG84LeadCreateField(text, [
      /\bemployees\s*(?:is|=|:)?\s*([0-9][0-9\s,._]*)/i,
    ]).replace(/[^0-9.]/g, ''),
    dueDate: extractWilsyFG84LeadCreateField(text, [
      /\b(?:due|follow\s*up|follow-up)\s*(?:date)?\s*(?:is|=|:)?\s*([0-9]{4}[-/][0-9]{2}[-/][0-9]{2})/i,
    ]).replace(/\//g, '-'),
    notes: extractWilsyFG84LeadCreateField(text, [
      /\bnotes\s*(?:are|is|=|:)?\s*(.+)$/i,
    ]) || text,
    description: extractWilsyFG84LeadCreateField(text, [
      /\bnotes\s*(?:are|is|=|:)?\s*(.+)$/i,
    ]) || text,
  };

  Object.keys(draft).forEach((key) => {
    if (draft[key] === '') delete draft[key];
  });

  if (!draft.name || !draft.company || !draft.email) {
    return null;
  }

  return {
    source: 'P60K5Q10FG84_GLOBAL_ASK_DIRECT_LEAD_CREATE_DRAFT',
    leadCreateDraft: draft,
    createLeadDraft: draft,
    packet: {
      mutation: 'NO_BACKEND_MUTATION_REQUIRES_OPERATOR_SAVE',
      operatorModel: {
        intent: 'create_lead',
        action: 'prepare_create_lead_draft',
        leadCreateDraft: draft,
        createLeadDraft: draft,
        answer: `I prepared a governed Create Lead draft for ${draft.name} at ${draft.company}. Review it and press Save.`,
      },
      toolRuns: [
        {
          tool: 'crm_lead_create_draft',
          status: 'APPROVAL_REQUIRED',
          mutation: 'NO_BACKEND_MUTATION_REQUIRES_OPERATOR_SAVE',
          leadCreateDraft: draft,
          createLeadDraft: draft,
        },
      ],
    },
    generatedAt: new Date().toISOString(),
  };
}

/**
 * @function dispatchWilsyFG84GlobalAskLeadCreateDraft
 * @description Stores and dispatches a governed Create Lead draft from the global Ask bar into the Leads workspace.
 * @param {Object} eventDetail - Create Lead draft event detail.
 * @returns {boolean} True when dispatched.
 * @collaboration Global Ask submit, browser event bridge, pending draft storage, route transition, and Leads Create hydration.
 */
function dispatchWilsyFG84GlobalAskLeadCreateDraft(eventDetail = {}) {
  /* P60K5Q10FG84_GLOBAL_ASK_DIRECT_LEAD_CREATE_ROUTER */
  if (typeof window === 'undefined' || !eventDetail?.leadCreateDraft) {
    return false;
  }

  try {
    window.sessionStorage?.setItem?.('wilsy.crm.leads.pendingCreateDraft', JSON.stringify(eventDetail));
  } catch {
    // Session storage is optional; live event remains primary.
  }

  window.dispatchEvent(new CustomEvent('wilsy:crm-leads-create-draft', { detail: eventDetail }));
  window.dispatchEvent(new CustomEvent('wilsy:crm-leads-open-request', { detail: { mode: 'create', ...eventDetail } }));
  window.dispatchEvent(new CustomEvent('wilsy:crm-module-open-request', { detail: { module: 'leads', mode: 'create', ...eventDetail } }));

  try {
    if (!window.location.pathname.includes('/crm/leads')) {
      window.history.pushState({ wilsyModule: 'leads', wilsyMode: 'create' }, '', '/crm/leads');
      window.dispatchEvent(new PopStateEvent('popstate', { state: { wilsyModule: 'leads', wilsyMode: 'create' } }));
      window.dispatchEvent(new CustomEvent('wilsy:workspace-context-changed', { detail: { module: 'leads', mode: 'create' } }));

      window.setTimeout(() => {
        if (!document.querySelector('[data-wilsy-lead-create-surface="P60K5Q10FG79_CREATE_AI_AWARE_SURFACE"]')) {
          window.location.assign('/crm/leads');
        }
      }, 180);
    }
  } catch {
    try {
      window.location.assign('/crm/leads');
    } catch {
      return true;
    }
  }

  return true;
}


/**
 * @function dispatchWilsyFG83BGlobalLeadCreateDraftBridge
 * @description Dispatches governed Lead create drafts from global Wilsy AI Ask responses into the Leads Create workspace.
 * @param {Object} packet - Wilsy AI operator packet.
 * @returns {boolean} True when a Create Lead draft was dispatched.
 * @collaboration Global Wilsy AI, CRM Setup copilot, Leads Create surface, pending draft storage, and no-blind-write operator approval.
 */
function dispatchWilsyFG83BGlobalLeadCreateDraftBridge(packet = {}) {
  /* P60K5Q10FG83B_GLOBAL_AI_ASK_RESPONSE_LEAD_CREATE_BRIDGE */
  if (typeof window === 'undefined' || !packet || typeof packet !== 'object') {
    return false;
  }

  const operatorModel = packet.operatorModel || packet.model || packet.payload?.operatorModel || {};
  const firstTool = Array.isArray(packet.toolRuns) ? packet.toolRuns[0] : null;
  const draft =
    operatorModel.leadCreateDraft ||
    operatorModel.createLeadDraft ||
    operatorModel.draft?.leadCreateDraft ||
    operatorModel.draft?.lead ||
    firstTool?.leadCreateDraft ||
    firstTool?.createLeadDraft ||
    firstTool?.draft?.leadCreateDraft ||
    firstTool?.draft?.lead ||
    firstTool?.draft;

  const isCreateLead =
    operatorModel.intent === 'create_lead' ||
    operatorModel.action === 'prepare_create_lead_draft' ||
    firstTool?.tool === 'crm_lead_create_draft' ||
    Boolean(draft);

  if (!isCreateLead || !draft || typeof draft !== 'object') {
    return false;
  }

  const eventDetail = {
    source: 'P60K5Q10FG83B_GLOBAL_AI_ASK_RESPONSE_LEAD_CREATE_BRIDGE',
    leadCreateDraft: draft,
    createLeadDraft: draft,
    packet,
    generatedAt: new Date().toISOString(),
  };

  try {
    window.sessionStorage?.setItem?.('wilsy.crm.leads.pendingCreateDraft', JSON.stringify(eventDetail));
  } catch {
    // Session storage is optional; live event remains primary.
  }

  window.dispatchEvent(new CustomEvent('wilsy:crm-leads-create-draft', { detail: eventDetail }));
  window.dispatchEvent(new CustomEvent('wilsy:crm-leads-open-request', { detail: { mode: 'create', ...eventDetail } }));
  window.dispatchEvent(new CustomEvent('wilsy:crm-module-open-request', { detail: { module: 'leads', mode: 'create', ...eventDetail } }));

  try {
    if (!window.location.pathname.includes('/crm/leads')) {
      window.history.pushState({ wilsyModule: 'leads', wilsyMode: 'create' }, '', '/crm/leads');
      window.dispatchEvent(new PopStateEvent('popstate', { state: { wilsyModule: 'leads', wilsyMode: 'create' } }));
    }
  } catch {
    // Navigation is best-effort; pending draft storage hydrates when Leads mounts.
  }

  return true;
}


/**
 * @function dispatchWilsyFG82GlobalLeadCreateDraftBridge
 * @description Dispatches governed Create Lead drafts from any global Wilsy AI packet into the mounted Leads workspace.
 * @param {Object} packet - Wilsy AI operator response packet.
 * @returns {boolean} True when a Create Lead draft event was dispatched.
 * @collaboration Global Wilsy AI dock, CRM Setup copilot, Leads Create surface, and governed no-blind-write draft review.
 */
function dispatchWilsyFG82GlobalLeadCreateDraftBridge(packet = {}) {
  /* P60K5Q10FG82_GLOBAL_AI_CREATE_LEAD_DRAFT_BRIDGE */
  if (typeof window === 'undefined' || !packet || typeof packet !== 'object') {
    return false;
  }

  const operatorModel = packet.operatorModel || packet.model || packet.payload?.operatorModel || {};
  const firstTool = Array.isArray(packet.toolRuns) ? packet.toolRuns[0] : null;
  const draft =
    operatorModel.leadCreateDraft ||
    operatorModel.createLeadDraft ||
    operatorModel.draft?.leadCreateDraft ||
    operatorModel.draft?.lead ||
    firstTool?.leadCreateDraft ||
    firstTool?.createLeadDraft ||
    firstTool?.draft?.leadCreateDraft ||
    firstTool?.draft?.lead ||
    firstTool?.draft;

  const isCreateLead =
    operatorModel.intent === 'create_lead' ||
    operatorModel.action === 'prepare_create_lead_draft' ||
    firstTool?.tool === 'crm_lead_create_draft' ||
    Boolean(draft);

  if (!isCreateLead || !draft || typeof draft !== 'object') {
    return false;
  }

  const eventDetail = {
    source: 'P60K5Q10FG82_GLOBAL_AI_CREATE_LEAD_DRAFT_BRIDGE',
    leadCreateDraft: draft,
    createLeadDraft: draft,
    packet,
    generatedAt: new Date().toISOString(),
  };

  try {
    window.sessionStorage?.setItem?.('wilsy.crm.leads.pendingCreateDraft', JSON.stringify(eventDetail));
  } catch {
    // Session storage is optional; the live event is the primary bridge.
  }

  window.dispatchEvent(new CustomEvent('wilsy:crm-leads-create-draft', { detail: eventDetail }));
  return true;
}


const WILSY_INTELLIGENCE_ROOT_ID = 'wilsy-os-intelligence-dock-root';
const WILSY_INTELLIGENCE_STORAGE_KEY = 'wilsy-os-intelligence-dock-state-v2-large-productivity';
/* WILSY_P60K5Q10AG_AI_OPERATOR_MODEL_SURFACE_JSX_MARKER */
/* WILSY_P60K5Q10AH_AI_DOCK_SIZE_CONTRACT_JSX_MARKER */
const WILSY_AI_CONTEXT_ROUTE = '/api/source-registry/health?wilsyAiContext=RESOLVE';

/**
 * @function humanizeWilsyAIBackendToken
 * @description Converts internal Wilsy AI contract tokens into operator-facing language for the Intelligence Dock.
 * @param {string} value - Raw service token or status.
 * @returns {string} Human-readable label.
 * @collaboration Keeps backend contracts intact while preventing backend language from leaking into the production UI.
 */
function humanizeWilsyAIBackendToken(value = '') {
  const token = String(value || '').trim();

  const dictionary = {
    WILSY_AI_SOVEREIGN_CONTEXT_RESOLVED: 'Workspace intelligence ready',
    DETERMINISTIC_GOVERNANCE_REASONER: 'Live CRM setup guidance',
    EVIDENCE_COMPLETE: 'Checks complete',
    GOVERNANCE_AI_TIER: 'Governance guidance available',
    GOVERNANCE_AI_TIER_AVAILABLE_FOR_PACKAGING: 'Ready for workflow packaging',
    CORE_INTELLIGENCE: 'Core guidance active',
    SOURCE_REGISTRY_HEALTH_GET_CONTEXT_BRIDGE: 'Live workspace context',
  };

  if (dictionary[token]) {
    return dictionary[token];
  }

  return token
    .replace(/^WILSY_AI_/, '')
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

/**
 * @function buildWilsyAIProductivityCopy
 * @description Shapes raw Wilsy AI context into a useful operator assistant surface without changing the backend contract.
 * @param {Object} payload - Raw Wilsy AI context payload.
 * @returns {Object} UI-safe payload with human-readable fields.
 * @collaboration Wilsy AI context resolver, CRM Setup live workspace, evidence posture, and frontend productivity shell.
 */
function buildWilsyAIProductivityCopy(payload = {}) {
  if (!payload || typeof payload !== 'object') {
    return payload;
  }

  const nextBestActions = Array.isArray(payload.nextBestActions)
    ? payload.nextBestActions.map((action) => ({
        ...action,
        title:
          action.rank === 1
            ? 'Review setup authority'
            : action.rank === 2
              ? 'Prepare release checklist'
              : action.title || 'Inspect setup queue',
        description:
          action.rank === 1
            ? 'Check role power, staged review proof, approval state, and release readiness before moving the setup forward.'
            : action.rank === 2
              ? 'Draft the evidence checklist needed before any release command is used.'
              : action.description || 'Check stale setup work and missing receipts before continuing.',
        billingTierSignal: humanizeWilsyAIBackendToken(action.billingTierSignal),
        evidenceStatus: humanizeWilsyAIBackendToken(action.evidenceStatus),
      }))
    : [];

  return {
    ...payload,
    result: humanizeWilsyAIBackendToken(payload.result),
    bridge: humanizeWilsyAIBackendToken(payload.bridge),
    workspace: {
      ...(payload.workspace || {}),
      focus: payload.workspace?.focus || 'Authority graph',
      operatingRole: payload.workspace?.operatingRole || 'Security Admin',
      monetizationSignal: humanizeWilsyAIBackendToken(payload.workspace?.monetizationSignal),
    },
    modelRoute: {
      ...(payload.modelRoute || {}),
      selectedRoute: humanizeWilsyAIBackendToken(payload.modelRoute?.selectedRoute),
      limitation: 'Read-only guidance. Nothing changes unless you approve a governed command.',
    },
    evidencePosture: {
      ...(payload.evidencePosture || {}),
      status: humanizeWilsyAIBackendToken(payload.evidencePosture?.status),
    },
    billingEntitlement: {
      ...(payload.billingEntitlement || {}),
      tier: humanizeWilsyAIBackendToken(payload.billingEntitlement?.tier),
      requiredTierSignal: humanizeWilsyAIBackendToken(payload.billingEntitlement?.requiredTierSignal),
      upgradeSignal: humanizeWilsyAIBackendToken(payload.billingEntitlement?.upgradeSignal),
    },
    nextBestActions,
    uiCopy: {
      statusTitle: 'Workspace status',
      statusSummary: 'Live CRM setup guidance is ready for this workspace.',
      lensTitle: 'Operating lens',
      nextMoveTitle: 'Recommended next step',
      coverageTitle: 'AI coverage',
    },
  };
}


/**
 * @function parseWilsyOperatorJsonResponse
 * @description Parses Wilsy Operator Kernel responses without throwing raw browser JSON errors into the UI.
 * @param {Response} response - Fetch response.
 * @returns {Promise<Object>} Parsed JSON payload.
 * @collaboration Ask Wilsy frontend loop, production JSON safety, and no-fake-answer error handling.
 */
async function parseWilsyOperatorJsonResponse(response) {
  const rawText = await response.text();

  if (!rawText || !rawText.trim()) {
    throw new Error('Wilsy Operator Kernel returned an empty response. No fake answer was generated.');
  }

  try {
    return JSON.parse(rawText);
  } catch (error) {
    throw new Error(`Wilsy Operator Kernel returned non-JSON output: ${rawText.slice(0, 180)}`);
  }
}

/**
 * @function extractWilsyPreparedWorkLink
 * @description Extracts a review or execution link from Operator Kernel model output.
 * @param {Object} model - Operator model response.
 * @returns {string} Prepared work link.
 * @collaboration Task Reminder Execution Bridge, Calendar Execution Bridge, approval review links, and productivity UI.
 */
function extractWilsyPreparedWorkLink(model = {}) {
  const tool = Array.isArray(model?.toolRuns) ? model.toolRuns[0] || {} : {};
  const answer = String(model?.answer || '');
  const commandPlan = Array.isArray(model?.commandPlan) ? model.commandPlan : [];
  const planText = commandPlan.join('\n');
  const linkPattern = /(\/crm\/(?:tasks|calendar|documents)\/(?:drafts|events)\/[A-Za-z0-9._-]+)/;
  const answerMatch = answer.match(linkPattern);
  const planMatch = planText.match(linkPattern);

  return (
    tool.crmTaskLink ||
    tool.taskLink ||
    tool.crmCalendarLink ||
    tool.eventLink ||
    tool.crmDocumentLink ||
    tool.documentLink ||
    answerMatch?.[1] ||
    planMatch?.[1] ||
    ''
  );
}

/**
 * @function buildWilsyPreparedOperatorItem
 * @description Builds a structured prepared-work card only for real prepared drafts, events, tasks, reminders, or calendar items.
 * @param {Object} model - Operator model response.
 * @returns {Object|null} Prepared work item for rendering.
 * @collaboration Ask Wilsy, task/reminder drafts, meeting drafts, approval gates, and operator productivity controls.
 */
function buildWilsyPreparedOperatorItem(model = {}) {
  const tool = Array.isArray(model?.toolRuns) ? model.toolRuns[0] || {} : {};
  const draft = tool.draft || {};
  const answer = String(model?.answer || '');
  const commandPlan = Array.isArray(model?.commandPlan) ? model.commandPlan : [];
  const planText = commandPlan.join('\n');
  const link = extractWilsyPreparedWorkLink(model);
  const status = String(tool.status || '').toUpperCase();
  const isMissingOrFoundry =
    status === 'TOOL_MISSING' ||
    status === 'NO_SOURCE_FOUND' ||
    status === 'SOURCE_UNAVAILABLE' ||
    tool.tool === 'capability_foundry' ||
    Boolean(model?.capabilityFoundryCandidate?.candidateId);

  if (isMissingOrFoundry && !draft.title && !draft.subject && !link) {
    return null;
  }

  const eligible =
    Boolean(draft.title || draft.subject) ||
    Boolean(link && /\/crm\/(?:tasks|calendar|documents)\/(?:drafts|events)\//.test(link)) ||
    ['APPROVAL_REQUIRED', 'EVENT_CREATED', 'TASK_CREATED', 'REMINDER_CREATED', 'DRAFT_PREPARED'].includes(status);

  if (!eligible) {
    return null;
  }

  const titleFromAnswer = answer.match(/Title:\s*([^.;]+)/i)?.[1];
  const dateFromAnswer = answer.match(/Due date:\s*([^.;]+)/i)?.[1] || answer.match(/Date:\s*([^.;]+)/i)?.[1];
  const timeFromAnswer = answer.match(/Time:\s*([^.;]+)/i)?.[1];
  const priorityFromAnswer = answer.match(/Priority:\s*([^.;]+)/i)?.[1];

  const kind =
    draft.kind ||
    (String(tool.tool || '').includes('document') ? 'document' : '') ||
    (String(tool.tool || '').includes('calendar') ? 'meeting' : '') ||
    (String(model?.action || '').includes('reminder') ? 'reminder' : '') ||
    (String(model?.action || '').includes('task') ? 'task' : '') ||
    'work item';

  const fields = [
    {
      label: 'Document type',
      value: draft.documentType || '',
    },
    {
      label: 'Title',
      value: draft.title || draft.subject || titleFromAnswer || '',
    },
    {
      label: 'Purpose',
      value: draft.purpose || '',
    },
    {
      label: 'Delivery requested',
      value: typeof draft.deliveryRequested === 'boolean' ? (draft.deliveryRequested ? 'Yes' : 'No') : '',
    },
    {
      label: kind === 'meeting' ? 'Date' : 'Due date',
      value: draft.dueDateLabel || draft.dateLabel || dateFromAnswer || '',
    },
    {
      label: 'Time',
      value: draft.timeLabel || timeFromAnswer || '',
    },
    {
      label: 'Priority',
      value: draft.priority || priorityFromAnswer || '',
    },
    {
      label: 'Duration',
      value: draft.durationLabel || '',
    },
    {
      label: 'Participants',
      value: Array.isArray(draft.participants) ? draft.participants.join(', ') : '',
    },
    {
      label: 'Agenda',
      value: draft.agenda || '',
    },
  ].filter((field) => field.value);

  if (fields.length === 0 && !link) {
    return null;
  }

  return {
    kind,
    title: `${kind.charAt(0).toUpperCase()}${kind.slice(1)} prepared`,
    status: tool.statusLabel || 'Approval required',
    link,
    linkLabel: link.includes('/documents/drafts/') ? 'Review Draft' : link.includes('/events/') || (link.includes('/tasks/') && !link.includes('/drafts/')) ? 'Open item' : 'Open review',
    planText: planText || answer,
    documentPreview: tool.documentPreview || draft.documentPreview || null,
    fields,
  };
}

/**
 * @function hasWilsyCapabilityCandidate
 * @description Detects whether the Operator Kernel response contains a Capability Foundry candidate.
 * @param {Object} model - Operator model.
 * @returns {boolean} Whether a Foundry candidate exists.
 * @collaboration Capability Foundry, no-fake-answer policy, and single-answer UI normalization.
 */
function hasWilsyCapabilityCandidate(model = {}) {
  return Boolean(model?.capabilityFoundryCandidate?.candidateId);
}

/**
 * @function buildWilsyFoundryDisplayTitle
 * @description Builds a clean business title for Capability Foundry responses.
 * @param {Object} model - Operator model.
 * @returns {string} Display title.
 * @collaboration Capability Foundry, tenant-facing business English, and answer normalization.
 */
function buildWilsyFoundryDisplayTitle(model = {}) {
  const candidate = model?.capabilityFoundryCandidate;

  if (!candidate?.candidateId) {
    return model?.title || 'Wilsy answer';
  }

  return `${candidate.businessName || 'Capability'} staged for review`;
}

/**
 * @function buildWilsyFoundryDisplayAnswer
 * @description Builds a clean business answer for Capability Foundry responses and suppresses generic tool language.
 * @param {Object} model - Operator model.
 * @returns {string} Display answer.
 * @collaboration Capability Foundry, no-fake-answer policy, and tenant productivity UI.
 */
function buildWilsyFoundryDisplayAnswer(model = {}) {
  const candidate = model?.capabilityFoundryCandidate;

  if (!candidate?.candidateId) {
    return model?.answer || '';
  }

  return `Wilsy cannot complete this request from the approved production registry yet. A reusable capability has been staged for admin review: ${candidate.businessName || 'Capability candidate'}. Candidate: ${candidate.candidateId}.`;
}

/**
 * @function buildWilsyFoundryDisplayOutcome
 * @description Builds a clean business outcome for Capability Foundry responses.
 * @param {Object} model - Operator model.
 * @returns {string} Display outcome.
 * @collaboration Capability Foundry, approval gates, self-extending tool registry, and production honesty.
 */
function buildWilsyFoundryDisplayOutcome(model = {}) {
  const candidate = model?.capabilityFoundryCandidate;

  if (!candidate?.candidateId) {
    return model?.outcome || '';
  }

  return 'Next decision: review the manifest, tool contract, proof cases, source binding, and promotion gates before publishing this capability.';
}

/**
 * @function getWilsyDisplayTitle
 * @description Returns the normalized answer title for regular and Capability Foundry responses.
 * @param {Object} model - Operator model.
 * @returns {string} Display title.
 * @collaboration Ask Wilsy answer surface, Capability Foundry, and production business-English output.
 */
function getWilsyDisplayTitle(model = {}) {

  /* WILSY_P60K5Q10DG_NATURAL_TITLE_GUARD */
  const wilsyMachineGapTitleText = [
    model?.title,
    model?.answer,
    model?.outcome,
    model?.status,
    model?.code,
    model?.errorCode,
    model?.reason,
    ...(Array.isArray(model?.sourceTrace) ? model.sourceTrace.map((trace) => `${trace?.tool || trace?.label || ''} ${trace?.status || ''} ${trace?.message || ''}`) : []),
  ]
    .filter(Boolean)
    .join(' ');

  if (/QUANTUM_LINK|_RESTORING|NO FAKE GUIDANCE|failed tool response|I cannot answer that yet|tool response is visible for repair/i.test(wilsyMachineGapTitleText)) {
    return 'Source connection needs repair';
  }
  return hasWilsyCapabilityCandidate(model) ? buildWilsyFoundryDisplayTitle(model) : model?.title || 'Wilsy answer';
}
/**
 * @function getWilsyModelAnswer
 * @description Returns the visible Wilsy Answer text from the operator model while preserving capability-foundry display behavior.
 * @param {object} model - Operator model.
 * @returns {string} Sanitized Wilsy Answer text.
 * @collaboration Wilsy Answer, capability foundry, document review panel, and split AI dock runtime.
 */
function getWilsyModelAnswer(model = {}) {
  return sanitizeWilsyVisibleOperatorText(hasWilsyCapabilityCandidate(model) ? buildWilsyFoundryDisplayAnswer(model) : model?.answer || '');
}

/**
 * @function getWilsyModelOutcome
 * @description Returns the visible Wilsy outcome text from the operator model while preserving capability-foundry display behavior.
 * @param {object} model - Operator model.
 * @returns {string} Sanitized Wilsy outcome text.
 * @collaboration Wilsy Answer, capability foundry, document review panel, and split AI dock runtime.
 */
function getWilsyModelOutcome(model = {}) {
  return sanitizeWilsyVisibleOperatorText(hasWilsyCapabilityCandidate(model) ? buildWilsyFoundryDisplayOutcome(model) : model?.outcome || '');
}

/**
 * @function getWilsyDisplayAnswer
 * @description Provides a stable visible answer helper for Wilsy Answer rendering without breaking older dock render paths.
 * @param {object} model - Operator model or display model.
 * @returns {string} Sanitized visible answer.
 * @collaboration Wilsy Answer, operator model display, document review panel, and split AI dock runtime.
 */
function getWilsyDisplayAnswer(model = {}) {

  /* WILSY_P60K5Q10DG_NATURAL_ANSWER_GUARD */
  const wilsyMachineGapAnswerText = [
    model?.title,
    model?.answer,
    model?.outcome,
    model?.status,
    model?.code,
    model?.errorCode,
    model?.reason,
    ...(Array.isArray(model?.sourceTrace) ? model.sourceTrace.map((trace) => `${trace?.tool || trace?.label || ''} ${trace?.status || ''} ${trace?.message || ''}`) : []),
  ]
    .filter(Boolean)
    .join(' ');

  if (/QUANTUM_LINK|_RESTORING|NO FAKE GUIDANCE|failed tool response|I cannot answer that yet|tool response is visible for repair/i.test(wilsyMachineGapAnswerText)) {
    const sourceLabel = Array.isArray(model?.sourceTrace) && (model.sourceTrace[0]?.tool || model.sourceTrace[0]?.label)
      ? (model.sourceTrace[0]?.tool || model.sourceTrace[0]?.label)
      : 'operator source';

    return `I checked the ${sourceLabel}, but the command link is still restoring. I will not guess or invent guidance. Next move: restore the source connection, then rerun the request.`;
  }
  if (typeof getWilsyModelAnswer === 'function') {
    return getWilsyModelAnswer(model);
  }

  if (typeof sanitizeWilsyVisibleOperatorText === 'function') {
    return sanitizeWilsyVisibleOperatorText(model?.answer || '');
  }

  return String(model?.answer || '').trim();
}

/**
 * @function getWilsyDisplayOutcome
 * @description Provides a stable visible outcome helper so the Wilsy AI dock cannot crash when rendering outcome text.
 * @param {object} model - Operator model or display model.
 * @returns {string} Sanitized visible outcome.
 * @collaboration Wilsy Answer, operator model display, document review panel, and split AI dock runtime.
 */
function getWilsyDisplayOutcome(model = {}) {

  /* WILSY_P60K5Q10DG_NATURAL_OUTCOME_GUARD */
  const wilsyMachineGapOutcomeText = [
    model?.title,
    model?.answer,
    model?.outcome,
    model?.status,
    model?.code,
    model?.errorCode,
    model?.reason,
    ...(Array.isArray(model?.sourceTrace) ? model.sourceTrace.map((trace) => `${trace?.tool || trace?.label || ''} ${trace?.status || ''} ${trace?.message || ''}`) : []),
  ]
    .filter(Boolean)
    .join(' ');

  if (/QUANTUM_LINK|_RESTORING|NO FAKE GUIDANCE|failed tool response|I cannot answer that yet|tool response is visible for repair/i.test(wilsyMachineGapOutcomeText)) {
    const sourceLabel = Array.isArray(model?.sourceTrace) && (model.sourceTrace[0]?.tool || model.sourceTrace[0]?.label)
      ? (model.sourceTrace[0]?.tool || model.sourceTrace[0]?.label)
      : 'operator source';

    return `Checked: ${sourceLabel} · Needs source repair · Next: restore command link`;
  }
  if (typeof getWilsyModelOutcome === 'function') {
    return getWilsyModelOutcome(model);
  }

  if (typeof sanitizeWilsyVisibleOperatorText === 'function') {
    return sanitizeWilsyVisibleOperatorText(model?.outcome || model?.answer || '');
  }

  return String(model?.outcome || model?.answer || '').trim();
}




/**
 * @function resolveWilsyOperatorFirstName
 * @description Resolves the operator first name from live model context, browser profile storage, visible identity text, or the known local founder/operator fallback.
 * @param {Object} model - Current Wilsy operator model.
 * @returns {string} Operator first name for natural greetings.
 * @collaboration Wilsy identity context, tenant identity surface, browser session state, and natural assistant response engine.
 */
function resolveWilsyOperatorFirstName(model = {}) {
  const modelCandidates = [
    model?.operator?.firstName,
    model?.operator?.name,
    model?.operatorName,
    model?.user?.firstName,
    model?.user?.name,
    model?.profile?.firstName,
    model?.profile?.name,
    model?.tenantOperator?.firstName,
    model?.tenantOperator?.name,
  ];

  const storageCandidates = [];

  if (typeof window !== 'undefined') {
    [
      'wilsyUser',
      'wilsy:user',
      'wilsy_operator_profile',
      'operatorProfile',
      'user',
      'profile',
      'authUser',
      'currentUser',
    ].forEach((key) => {
      try {
        const rawValue = window.localStorage?.getItem(key) || window.sessionStorage?.getItem(key);

        if (!rawValue) {
          return;
        }

        const parsedValue = JSON.parse(rawValue);
        storageCandidates.push(
          parsedValue?.firstName,
          parsedValue?.name,
          parsedValue?.displayName,
          parsedValue?.user?.firstName,
          parsedValue?.user?.name,
          parsedValue?.profile?.firstName,
          parsedValue?.profile?.name,
        );
      } catch (error) {
        storageCandidates.push(window.localStorage?.getItem(key), window.sessionStorage?.getItem(key));
      }
    });

    try {
      const visibleIdentity = document?.querySelector?.('[data-wilsy-operator-name], [data-operator-name], [data-user-name]');
      storageCandidates.push(visibleIdentity?.textContent);
    } catch (error) {
      storageCandidates.push('');
    }
  }

  const candidate = [...modelCandidates, ...storageCandidates]
    .map((value) => String(value || '').trim())
    .find((value) => value && !/security admin|finance operator|operator|tenant|root/i.test(value));

  const firstName = String(candidate || 'Wilson')
    .replace(/[^a-zA-ZÀ-ÿ'\-\s]/g, ' ')
    .trim()
    .split(/\s+/)[0];

  return firstName || 'Wilson';
}

/**
 * @function resolveWilsyTemporalGreeting
 * @description Builds a local time-aware greeting from the operator browser clock.
 * @param {Date} now - Browser-local date instance.
 * @returns {string} Natural daypart greeting.
 * @collaboration Browser local time, Wilsy live composer, and human-facing assistant tone.
 */
function resolveWilsyTemporalGreeting(now = new Date()) {
  const hour = now.getHours();

  if (hour < 12) {
    return 'Good morning';
  }

  if (hour < 18) {
    return 'Good afternoon';
  }

  return 'Good evening';
}

/**
 * @function buildWilsyDynamicOperatorDirectives
 * @description Builds context-aware quick directives from model state instead of exposing fixed childish suggestion cards.
 * @param {Object} model - Current Wilsy operator model.
 * @param {string} activeIntent - Current active operator intent.
 * @returns {Array<Object>} Dynamic directive descriptors.
 * @collaboration Wilsy operator model, command tokens, source route judge, CRM setup authority graph, evidence posture, and quick prompt surface.
 */
function buildWilsyDynamicOperatorDirectives(model = {}, activeIntent = '') {
  const commandTokens = Array.isArray(model?.commandTokens)
    ? model.commandTokens
    : Array.isArray(model?.executionThread)
      ? model.executionThread
      : Array.isArray(model?.playableActions)
        ? model.playableActions
        : Array.isArray(model?.actions)
          ? model.actions
          : [];

  const sourceTrace = Array.isArray(model?.sourceTrace) ? model.sourceTrace : [];
  const routeCount = commandTokens.length;
  const sourceCount = sourceTrace.length || 1;
  const workspace = model?.workspace || model?.module || model?.contextLabel || 'CRM Setup';
  const outstandingCount = Math.max(routeCount || 3, sourceCount + 2);

  const dynamicDirectives = [
    {
      id: `dynamic_outstanding_${outstandingCount}`,
      intent: 'what_next',
      label: `Tell me what is outstanding in ${workspace}`,
      prompt: `Tell me what is outstanding in ${workspace}`,
      description: `${sourceCount} live source${sourceCount === 1 ? '' : 's'} checked · ${outstandingCount} route checks available`,
    },
    {
      id: `dynamic_authority_${routeCount || 'route'}`,
      intent: 'authority_graph',
      label: `Walk me through the ${workspace} authority path`,
      prompt: `Walk me through the ${workspace} authority path`,
      description: 'Resolve reviewer, approver, release owner, and mutation boundary',
    },
    {
      id: `dynamic_evidence_${sourceCount}`,
      intent: 'evidence_checklist',
      label: `Show the evidence gaps before setup moves`,
      prompt: `Show the evidence gaps before setup moves`,
      description: 'Find missing staged proof, packet status, receipts, and command-surface evidence',
    },
    {
      id: `dynamic_release_${routeCount || 'readiness'}`,
      intent: 'release_readiness',
      label: `Check whether this setup is safe to release`,
      prompt: `Check whether this setup is safe to release`,
      description: 'Judge readiness before any command mutates workspace state',
    },
  ];

  return dynamicDirectives.map((directive) => ({
    ...directive,
    id: directive.id === activeIntent ? `${directive.id}_active` : directive.id,
  }));
}


/**
 * @function normalizeWilsyConversationArray
 * @description Normalizes model arrays so the conversation engine can scan command tokens, source traces, telemetry, and evidence anchors safely.
 * @param {*} value - Candidate array-like value.
 * @returns {Array} Safe array for conversational CRM reasoning.
 * @collaboration Wilsy AI conversation engine, CRM source trace, command-token routes, telemetry packs, and evidence anchors.
 */
function normalizeWilsyConversationArray(value = []) {
  return Array.isArray(value) ? value.filter(Boolean) : [];
}

/**
 * @function resolveWilsyConversationGreetingState
 * @description Allows Wilsy AI to greet the operator once per browser session and then continue naturally without repeating the greeting on every answer.
 * @param {Object} model - Current Wilsy operator model.
 * @param {string} firstName - Resolved operator first name.
 * @param {string} promptText - Current prompt text.
 * @returns {boolean} True only when this is the first meaningful conversational answer in the current session scope.
 * @collaboration Wilsy operator identity, browser session memory, natural response flow, and continuation-aware AI composer.
 */
function resolveWilsyConversationGreetingState(model = {}, firstName = 'Wilson', promptText = '') {
  const workspace = model?.workspace || model?.module || model?.contextLabel || 'CRM Setup';
  const promptReady = String(promptText || '').trim().length > 0;

  if (!promptReady) {
    return false;
  }

  if (typeof window === 'undefined') {
    return true;
  }

  const key = `wilsy.ai.greeted.v1.${workspace}.${firstName}`.toLowerCase().replace(/[^a-z0-9.]+/g, '-');

  try {
    if (window.sessionStorage?.getItem(key) === 'true') {
      return false;
    }

    window.sessionStorage?.setItem(key, 'true');
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * @function buildWilsyDeepCrmWorkspaceScan
 * @description Builds a deeper CRM operating readout from the current model, including source traces, command routes, telemetry packs, authority posture, evidence anchors, and release constraints.
 * @param {Object} model - Current Wilsy operator model.
 * @param {string} promptText - Current operator prompt text.
 * @returns {Object} Natural conversational response parts.
 * @collaboration Wilsy CRM setup cockpit, source route judge, evidence anchors, command tokens, tenant authority graph, and governed command flow.
 */
function buildWilsyDeepCrmWorkspaceScan(model = {}, promptText = '') {
  const workspace = model?.workspace || model?.module || model?.contextLabel || 'CRM Setup';
  const prompt = String(promptText || '').toLowerCase();
  const commandTokens = normalizeWilsyConversationArray(
    model?.commandTokens?.length
      ? model.commandTokens
      : model?.executionThread?.length
        ? model.executionThread
        : model?.playableActions?.length
          ? model.playableActions
          : model?.actions,
  );
  const sourceTrace = normalizeWilsyConversationArray(model?.sourceTrace);
  const telemetry = normalizeWilsyConversationArray(model?.telemetryPacks);
  const evidenceAnchors = normalizeWilsyConversationArray(model?.evidenceAnchors);
  const routeJudge = model?.sourceRouteJudge || {};
  const displayAnswer = getWilsyDisplayAnswer(model);
  const routeNames = commandTokens
    .map((token) => token?.label || token?.title || token?.name || token?.intent || token?.route)
    .filter(Boolean);
  const sourceNames = sourceTrace
    .map((trace) => trace?.label || trace?.source || trace?.surface || trace?.statusLabel)
    .filter(Boolean);
  const evidenceNames = evidenceAnchors
    .map((anchor) => anchor?.label || anchor?.title || anchor?.name || anchor)
    .filter(Boolean);
  const telemetryNames = telemetry
    .map((item) => item?.label || item?.title || item?.name)
    .filter(Boolean);

  const hasAuthorityIntent = /authority|permission|approver|approval|reviewer|release owner|owner|role|power/.test(prompt);
  const hasEvidenceIntent = /evidence|proof|receipt|anchor|checklist|packet|manifest/.test(prompt);
  const hasReleaseIntent = /release|ready|readiness|ship|publish|go live|unlock/.test(prompt);
  const hasQueueIntent = /queue|hygiene|stale|drift|pending|orphan/.test(prompt);
  const hasPackageIntent = /package|workflow|lane|playbook|process/.test(prompt);

  const routeSummary = routeNames.length
    ? `I found ${routeNames.length} governed route${routeNames.length === 1 ? '' : 's'} behind this answer: ${routeNames.slice(0, 5).join(', ')}.`
    : `I do not see a complete command-route set yet, so I am treating ${workspace} as read-only until the route judge is satisfied.`;

  const sourceSummary = sourceNames.length
    ? `The connected source posture points at ${sourceNames.slice(0, 4).join(', ')}.`
    : `The source trace is thin, so I am relying on the visible ${workspace} model, authority graph, command tokens, and evidence posture before recommending movement.`;

  const evidenceSummary = evidenceNames.length
    ? `Evidence already visible: ${evidenceNames.slice(0, 5).join(', ')}.`
    : `The evidence still needs to be proven through staged review proof, packet status, approval receipt, operator identity, tenant identity, and command-surface record.`;

  const judgeSummary =
    routeJudge?.decision ||
    routeJudge?.reason ||
    routeJudge?.status ||
    'Prepare work only. Mutation stays locked until authority, evidence, and release permission agree.';

  if (hasAuthorityIntent) {
    return {
      opening: `On the authority path, the real issue is separation of power.`,
      readout: `${sourceSummary} ${routeSummary}`,
      decision: `Before setup moves, resolve four things: who reviews, who approves, who owns release, and which evidence each step requires.`,
      nextMove: `The useful next move is to trace the authority route against the staged review packet, then bind missing role evidence before checking release readiness.`,
      boundary: `Do not let one role hold review power, approval power, release power, and mutation power. ${judgeSummary}`,
    };
  }

  if (hasEvidenceIntent) {
    return {
      opening: `For evidence, I would not start with another card. I would build the proof pack first.`,
      readout: `${sourceSummary} ${evidenceSummary}`,
      decision: `The proof pack should show staged review proof, packet state, approval receipt, tenant identity, operator identity, and the exact command surface that would be affected.`,
      nextMove: `Bind the missing anchors first, then check whether the release route is still blocked. If any receipt is missing, prepare the repair route instead of pushing the setup forward.`,
      boundary: `${judgeSummary}`,
    };
  }

  if (hasReleaseIntent) {
    return {
      opening: `Release readiness is not a yes-or-no button here. It is a lock check.`,
      readout: `${sourceSummary} ${routeSummary}`,
      decision: `Treat release as blocked unless staged proof, approval state, release owner, packet integrity, and receipt trail all match.`,
      nextMove: `Check release after evidence binding. If the approval receipt or release owner is missing, hold the release and open a repair route.`,
      boundary: `${judgeSummary}`,
    };
  }

  if (hasQueueIntent) {
    return {
      opening: `Queue hygiene is where hidden setup risk usually appears.`,
      readout: `${sourceSummary} ${telemetryNames.length ? `Telemetry surfaces include ${telemetryNames.slice(0, 5).join(', ')}.` : routeSummary}`,
      decision: `Look for stale setup reviews, repeated pending states, orphan approvals, missing receipts, and packets that appear staged but cannot prove who approved the next move.`,
      nextMove: `Start by isolating stale packets, then attach receipts or mark the packet for repair before it reaches release readiness.`,
      boundary: `${judgeSummary}`,
    };
  }

  if (hasPackageIntent) {
    return {
      opening: `Packaging the workflow only makes sense after authority and evidence are clean.`,
      readout: `${routeSummary} ${evidenceSummary}`,
      decision: `A proper tenant workflow should repeat the safe sequence: inspect authority, bind evidence, judge release, inspect queue drift, then package the governed lane.`,
      nextMove: `Package only the lane that can prove who may review, approve, release, and mutate. Everything else stays in repair.`,
      boundary: `${judgeSummary}`,
    };
  }

  return {
    opening: `Here is the operational read: ${workspace} is not waiting for another suggestion. It is waiting for proof that the next move is safe.`,
    readout: displayAnswer
      ? `${displayAnswer} ${sourceSummary}`
      : `${sourceSummary} ${routeSummary}`,
    decision: `The outstanding work is authority, evidence, release judgement, and queue hygiene. Those are not equal priorities; authority and evidence come first because they decide whether any later move is valid.`,
    nextMove: `Work it in this order: trace the authority route, bind the missing evidence anchors, then judge release readiness. If the route still cannot prove approval or receipt trail, prepare the repair route.`,
    boundary: `${judgeSummary}`,
  };
}


/**
 * @function buildWilsyNaturalConversationAnswer
 * @description Builds a natural time-aware human response for Wilsy AI, including greeting, operator name, acknowledgement, and model-grounded reasoning.
 * @param {Object} model - Current Wilsy operator model.
 * @param {string} promptText - Operator prompt text.
 * @returns {string} Natural assistant response for character-by-character streaming.
 * @collaboration Wilsy live composer, dynamic directive engine, operator identity, local time greeting, CRM setup context, source route judge, and evidence-first governance.
 */
function buildWilsyNaturalConversationAnswer(model = {}, promptText = '') {
  const firstName = resolveWilsyOperatorFirstName(model);
  const shouldGreet = resolveWilsyConversationGreetingState(model, firstName, promptText);
  const greeting = shouldGreet ? `${resolveWilsyTemporalGreeting()}, ${firstName}. ` : '';
  const scan = buildWilsyDeepCrmWorkspaceScan(model, promptText);
  const continuationLead = shouldGreet
    ? `${greeting}I am in the ${model?.workspace || model?.module || model?.contextLabel || 'CRM Setup'} workspace with you.`
    : scan.opening;

  const opening = shouldGreet ? `${continuationLead} ${scan.opening}` : continuationLead;

  return [
    opening,
    scan.readout,
    scan.decision,
    scan.nextMove,
    scan.boundary,
  ]
    .filter(Boolean)
    .join('\n\n');
}

/**
 * @function buildWilsyDynamicComposerPlaceholder
 * @description Builds the CRM setup input placeholder from active model context instead of a fixed string.
 * @param {Object} model - Current Wilsy operator model.
 * @returns {string} Dynamic input placeholder.
 * @collaboration Wilsy operator input, CRM setup context, and dynamic directive system.
 */
function buildWilsyDynamicComposerPlaceholder(model = {}) {
  const workspace = model?.workspace || model?.module || model?.contextLabel || 'CRM Setup';
  return `Ask Wilsy what needs attention in ${workspace}...`;
}


/**
 * @function buildWilsyCinematicComposerAnswer
 * @description Builds a deeper natural response that can be typed into the live composer without dumping a shallow hardcoded line.
 * @param {Object} model - Current Wilsy operator model.
 * @param {string} promptText - Operator prompt text.
 * @returns {string} Cinematic single-surface response text.
 * @collaboration Wilsy AI composer, live workspace state, source route judge, command tokens, evidence anchors, and operator-facing natural reasoning.
 */
function buildWilsyCinematicComposerAnswer(model = {}, promptText = '') {
  const title = getWilsyDisplayTitle(model);
  const answer = getWilsyDisplayAnswer(model);
  const routeJudge = model?.sourceRouteJudge || {};
  const sourceTrace = Array.isArray(model?.sourceTrace) ? model.sourceTrace : [];
  const telemetry = Array.isArray(model?.telemetryPacks) ? model.telemetryPacks : [];
  const commandTokens = Array.isArray(model?.commandTokens)
    ? model.commandTokens
    : Array.isArray(model?.executionThread)
      ? model.executionThread
      : Array.isArray(model?.playableActions)
        ? model.playableActions
        : Array.isArray(model?.actions)
          ? model.actions
          : [];
  const routeCount = commandTokens.length;
  const connectedSources = sourceTrace.filter((trace) => /complete|ready|connected|success/i.test(`${trace?.status || ''} ${trace?.statusLabel || ''}`)).length || sourceTrace.length || 1;
  const firstMove = commandTokens[0]?.label || commandTokens[0]?.title || 'trace the authority route';
  const secondMove = commandTokens[1]?.label || commandTokens[1]?.title || 'bind evidence anchors';
  const thirdMove = commandTokens[2]?.label || commandTokens[2]?.title || 'judge release readiness';
  const authorityBoundary =
    telemetry.find((item) => /authority/i.test(item?.label || ''))?.value ||
    'the reviewer, approver, release owner, tenant identity, operator identity, and mutation boundary must agree before setup work moves';
  const evidenceAnchor =
    telemetry.find((item) => /evidence/i.test(item?.label || ''))?.value ||
    'the staged proof, packet status, approval receipt, command surface, and tenant context must be visible';
  const routeDecision =
    routeJudge.decision ||
    routeJudge.reason ||
    'Wilsy may prepare the route, but it may not mutate setup state until the source route and approval evidence are proven.';
  const directive = String(promptText || '').trim();

  return [
    title,
    answer,
    `I checked ${connectedSources} connected setup source${connectedSources === 1 ? '' : 's'} and found ${routeCount || 'multiple'} governed route${routeCount === 1 ? '' : 's'} available for the next move. I am not going to turn that into another card. I am keeping it inside this live composer and letting the workspace behave like operating software.`,
    `The safe path is: ${String(firstMove).toLowerCase()} first, then ${String(secondMove).toLowerCase()}, then ${String(thirdMove).toLowerCase()}. That sequence matters because ${authorityBoundary}.`,
    `Evidence boundary: ${evidenceAnchor}.`,
    `Route judge: ${routeDecision}`,
    directive
      ? `Your directive is "${directive}". I will use that as the operating focus, but I will only expose actions that can survive authority, evidence, and release checks.`
      : 'The next interaction should feel like the system is thinking with you: text appears as it is being composed, route words become clickable inline, and the chrome disappears when the thought is complete.',
  ]
    .filter(Boolean)
    .join('\n\n');
}


/**
 * @function buildWilsySingleSurfaceCompetitiveAnswer
 * @description Builds a richer natural operator answer from the live Wilsy model without adding cards, rails, or separate panels.
 * @param {Object} model - Current Wilsy operator model.
 * @param {string} promptText - Operator prompt text.
 * @returns {string} Natural response text for the single live composer surface.
 * @collaboration Wilsy OS AI composer, command-token payload, source route judge, evidence anchors, operator prompt, and single-surface streaming contract.
 */
function buildWilsySingleSurfaceCompetitiveAnswer(model = {}, promptText = '') {
  const title = getWilsyDisplayTitle(model);
  const answer = getWilsyDisplayAnswer(model);
  const routeJudge = model?.sourceRouteJudge || {};
  const commandTokens = Array.isArray(model?.commandTokens)
    ? model.commandTokens
    : Array.isArray(model?.executionThread)
      ? model.executionThread
      : Array.isArray(model?.playableActions)
        ? model.playableActions
        : Array.isArray(model?.actions)
          ? model.actions
          : [];
  const telemetry = Array.isArray(model?.telemetryPacks) ? model.telemetryPacks : [];
  const firstToken = commandTokens[0] || {};
  const secondToken = commandTokens[1] || {};
  const thirdToken = commandTokens[2] || {};
  const firstMove = firstToken.label || firstToken.title || firstToken.buttonLabel || 'trace the authority route';
  const secondMove = secondToken.label || secondToken.title || secondToken.buttonLabel || 'bind evidence anchors';
  const thirdMove = thirdToken.label || thirdToken.title || thirdToken.buttonLabel || 'judge release readiness';
  const authorityBoundary =
    telemetry.find((item) => /authority/i.test(item?.label || ''))?.value ||
    'review, approval, release, and mutation powers must stay separated';
  const evidenceAnchor =
    telemetry.find((item) => /evidence/i.test(item?.label || ''))?.value ||
    'proof must be attached before any governed command can execute';
  const routeDecision =
    routeJudge.decision ||
    routeJudge.reason ||
    'Wilsy prepares the route, but mutation stays locked until the authority path and evidence trail are proven.';
  const directive = String(promptText || '').trim();

  return [
    title,
    answer,
    `I am keeping this inside one live Wilsy AI composer, not opening another card. The useful move is to ${String(firstMove).toLowerCase()} because ${authorityBoundary}. After that, ${String(secondMove).toLowerCase()} so ${evidenceAnchor}. Then ${String(thirdMove).toLowerCase()} before any setup state changes.`,
    `The route judge is clear: ${routeDecision}`,
    directive
      ? `I am using your directive — "${directive}" — as the operating focus. I will not pretend the workspace is safe until the source route, evidence anchors, and approval boundary agree.`
      : 'The next move must feel like operating software: one live answer, inline decisions, no card stack, no fake execution.',
  ]
    .filter(Boolean)
    .join('\n\n');
}


/**
 * @function sanitizeWilsyVisibleOperatorText
 * @description Removes raw internal CRM routes from visible Wilsy Answer text while preserving governed review actions in Prepared Work.
 * @param {string} value - Visible answer value.
 * @returns {string} Business-readable visible text without internal route leakage.
 * @collaboration Wilsy Answer, Prepared Work, tenant document review, approval plan, and no-reset AI workspace.
 */
function sanitizeWilsyVisibleOperatorText(value = '') {
  return String(value || '')
    .replace(/Review link:\s*\/crm\/(?:documents|tasks|calendar)\/(?:drafts|events)\/[A-Za-z0-9._-]+\.?/gi, 'Use Review Draft to inspect the governed draft.')
    .replace(/\/crm\/(?:documents|tasks|calendar)\/(?:drafts|events)\/[A-Za-z0-9._-]+/gi, 'the governed review action')
    .replace(/\bQUANTUM_LINK_RESTORING\b/gi, 'the command link is still restoring')
    /* WILSY_P60K5Q10DG_MACHINE_TEXT_SANITIZER */
    .replace(/\b[A-Z]{2,}_[A-Z0-9_]{2,}\b/g, '')
    .replace(/NO FAKE GUIDANCE WAS GENERATED\.?/gi, 'I will not guess or invent guidance.')
    .replace(/THE FAILED TOOL RESPONSE IS VISIBLE FOR REPAIR\.?/gi, 'The source issue is visible for repair.')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * @function normalizeWilsyFoundryModelForDisplay
 * @description Normalizes Capability Foundry responses before React state render so stale generic wording cannot leak into the UI.
 * @param {Object} model - Operator model response.
 * @returns {Object} Normalized model.
 * @collaboration Capability Foundry, no-fake-answer policy, and single-answer production UI.
 */
function normalizeWilsyFoundryModelForDisplay(model = {}) {
  const candidate = model?.capabilityFoundryCandidate;

  if (!candidate?.candidateId) {
    return model;
  }

  const businessName = candidate.businessName || 'Business capability';
  const candidateId = candidate.candidateId;

  return {
    ...model,
    title: `${businessName} staged for review`,
    answer: `Wilsy has staged ${businessName} as a reusable capability for admin review. This capability is not live for tenant users yet.`,
    outcome: 'Next decision: review the manifest, tool contract, proof cases, source binding, and promotion gates before publishing this capability.',
  };
}

/**
 * @function buildWilsyCapabilityReviewItem
 * @description Builds one review surface for Capability Foundry candidates.
 * @param {Object} model - Operator model response.
 * @returns {Object|null} Capability review item.
 * @collaboration Capability Foundry, self-extending tool registry, approval gates, and no-fake-answer workflow.
 */
function buildWilsyCapabilityReviewItem(model = {}) {
  const candidate = model?.capabilityFoundryCandidate;

  if (!candidate?.candidateId) {
    return null;
  }

  return {
    candidateId: candidate.candidateId,
    capabilityId: candidate.capabilityId,
    businessName: candidate.businessName || 'Capability candidate',
    status: candidate.status || 'STAGED_FOR_REVIEW',
    quarantinePath: candidate.quarantinePath || '',
    approvalRequired: candidate.approvalRequired !== false,
    nextDecision: 'Review manifest, tool contract, proof cases, source binding, and promotion gates before publishing.',
    planText: [
      `Capability: ${candidate.businessName || 'Capability candidate'}`,
      `Candidate: ${candidate.candidateId}`,
      `Status: ${candidate.status || 'STAGED_FOR_REVIEW'}`,
      `Quarantine: ${candidate.quarantinePath || 'not available'}`,
      'Publication: not live. Human/admin approval required before promotion.',
    ].join('\n'),
  };
}

/**
 * @function buildWilsyOperatorAskUrl
 * @description Builds the backend Wilsy Operator Model GET URL using the proven source-registry health bridge.
 * @param {string} prompt - Operator question.
 * @param {Object} snapshot - Current workspace snapshot.
 * @param {Object} context - Current merged context.
 * @returns {string} Backend ask URL.
 * @collaboration Q10Z source-registry GET bridge, Wilsy Operator Model backend, and browser-safe no-mutation ask loop.
 */
function buildWilsyOperatorAskUrl(prompt = '', snapshot = {}, context = {}) {
  const url = new URL(WILSY_AI_CONTEXT_ROUTE, window.location.origin);

  url.searchParams.set('wilsyAiContext', 'ASK');
  url.searchParams.set('operatorQuestion', String(prompt || '').trim());
  url.searchParams.set('tenantId', window.localStorage?.getItem('wilsy-tenant-id') || 'MASTER');
  url.searchParams.set('operatorId', window.localStorage?.getItem('wilsy-operator-id') || 'WILSY_OPERATOR');
  url.searchParams.set('workspaceRoute', snapshot.path || window.location.pathname || '/crm/setup');
  url.searchParams.set(
    'workspaceSurface',
    String(snapshot.text || context.focus || 'CRM Operating Controls Authority Graph Evidence Approval Release').slice(0, 1400)
  );

  return url.pathname + url.search;
}

/**
 * @function resolveWilsyOperatorIntent
 * @description Resolves the operator's question or quick prompt into a productive Wilsy AI intent.
 * @param {string} prompt - Operator-entered prompt.
 * @param {string} activePrompt - Current selected quick prompt id.
 * @returns {string} Operator intent id.
 * @collaboration Wilsy AI dock prompt loop, CRM Setup workspace context, and governed command preparation.
 */
function resolveWilsyOperatorIntent(prompt = '', activePrompt = 'what_next') {
  const text = String(prompt || '').toLowerCase();
  const isLeadPrompt = /\blead\b|\bleads\b|prospect|prospects/i.test(text);
  const isTaskPrompt = /\btask\b|\btasks\b|todo|to-do|follow up|follow-up/i.test(text);

  if (isLeadPrompt) {
    return 'crm_leads_summary';
  }

  if (isTaskPrompt) {
    return text.includes('next week') ? 'crm_tasks_due_next_week' : 'crm_tasks_due_this_week';
  }

  if (text.includes('release') || text.includes('ready') || text.includes('approval')) {
    return 'release_readiness';
  }

  if (text.includes('authority') || text.includes('role') || text.includes('permission')) {
    return 'authority_graph';
  }

  if (text.includes('evidence') || text.includes('checklist') || text.includes('proof')) {
    return 'evidence_checklist';
  }

  if (text.includes('queue') || text.includes('stale') || text.includes('missing')) {
    return 'queue_hygiene';
  }

  if (text.includes('package') || text.includes('bill') || text.includes('tenant') || text.includes('tier')) {
    return 'workflow_packaging';
  }

  return activePrompt || 'what_next';
}

/**
 * @function buildWilsyOperatorModelSurface
 * @description Builds the user-facing Wilsy Operator Model answer, action board, and governed command plan from live workspace context.
 * @param {Object} params - Operator model input bundle.
 * @param {Object} params.context - Merged workspace context.
 * @param {Object} params.backendContext - Live backend context.
 * @param {Array} params.cards - Legacy card data used only as fallback evidence.
 * @param {string} params.operatorPrompt - Current operator prompt.
 * @param {string} params.activePrompt - Current quick prompt id.
 * @returns {Object} Operator model surface.
 * @collaboration Q10Z live AI context, CRM Setup authority graph, evidence posture, release controls, and human approval boundary.
 */
function buildWilsyOperatorModelSurface({
  context = {},
  backendContext = {},
  cards = [],
  operatorPrompt = '',
  activePrompt = 'what_next',
} = {}) {
  const intent = resolveWilsyOperatorIntent(operatorPrompt, activePrompt);
  const workspaceName = context.workspace || backendContext?.workspace?.label || 'Current workspace';
  const role = context.role || backendContext?.workspace?.operatingRole || 'Operator';
  const focus = context.focus || backendContext?.workspace?.focus || 'Workspace control';
  const actions = Array.isArray(backendContext?.nextBestActions) && backendContext.nextBestActions.length > 0
    ? backendContext.nextBestActions
    : cards.map((card, index) => ({
        rank: index + 1,
        title: card.title,
        description: card.body,
        mode: 'read_only',
        mutation: false,
      }));

  const actionDefaults = [
    {
      rank: 1,
      title: 'Review setup authority',
      description: 'Check who can approve, release, withdraw, and verify this setup packet.',
      mode: 'read_only',
      mutation: false,
    },
    {
      rank: 2,
      title: 'Prepare release checklist',
      description: 'Build the checklist needed before any release command can be used.',
      mode: 'draft_only',
      mutation: false,
    },
    {
      rank: 3,
      title: 'Inspect queue hygiene',
      description: 'Find stale setup work, missing receipts, and unresolved approval blockers.',
      mode: 'read_only',
      mutation: false,
    },
  ];

  const productiveActions = actions.length > 0 ? actions.slice(0, 4) : actionDefaults;

  const answerMap = {
    what_next: {
      title: 'Here is the next useful move',
      answer: `For ${workspaceName}, start with authority and evidence. Confirm ${role} has the right control path, then check staged review proof, approval state, and release readiness before moving work forward.`,
      outcome: 'Move setup work forward without guessing.',
    },
    release_readiness: {
      title: 'Release readiness check',
      answer: 'Before release, verify staged review proof, approval state, release permission, packet integrity, and receipt trail. Do not use a release command until all five checks are clear.',
      outcome: 'Prevent premature release and protect audit posture.',
    },
    authority_graph: {
      title: 'Authority graph interpretation',
      answer: `The active lens is ${focus}. Use it to match each action to the authority available in this workspace: who can review, who can approve, who can release, and what proof each step needs.`,
      outcome: 'Match every action to authority before execution.',
    },
    evidence_checklist: {
      title: 'Evidence checklist',
      answer: 'Collect staged review proof, packet status, approval receipt, release readiness, operator identity, tenant identity, and command-surface evidence before any governed command.',
      outcome: 'Create an approval-ready evidence pack.',
    },
    queue_hygiene: {
      title: 'Queue hygiene review',
      answer: 'Inspect setup reviews for stale status, missing receipts, repeated pending states, orphaned approvals, and release blockers. Prioritize items with proof gaps first.',
      outcome: 'Clear blockers before new setup work enters the queue.',
    },
    workflow_packaging: {
      title: 'Tenant value packaging',
      answer: 'Package this as governance guidance: authority checks, release readiness, evidence checklist, and queue hygiene. That is billable productivity because it reduces approval risk and saves operator time.',
      outcome: 'Turn live guidance into a tenant-facing workflow tier.',
    },
  };

  const selected = answerMap[intent] || answerMap.what_next;

  const checklist = [
    'Confirm tenant and operator identity are visible.',
    'Check staged review proof and current approval state.',
    'Verify release readiness before any release command.',
    'Capture evidence gaps before moving to the next packet.',
    'Prepare a governed command only after the operator approves.',
  ];

  const quickPrompts = [
    { id: 'what_next', label: 'What should I do next?' },
    { id: 'release_readiness', label: 'Check release readiness' },
    { id: 'authority_graph', label: 'Explain authority graph' },
    { id: 'evidence_checklist', label: 'Prepare evidence checklist' },
    { id: 'queue_hygiene', label: 'Inspect queue hygiene' },
    { id: 'workflow_packaging', label: 'Package tenant workflow' },
  ];

  return {
    intent,
    title: selected.title,
    answer: selected.answer,
    outcome: selected.outcome,
    quickPrompts,
    actions: productiveActions,
    checklist,
    commandPlan: [
      `Workspace: ${workspaceName}`,
      `Operator role: ${role}`,
      `Intent: ${selected.title}`,
      `Outcome: ${selected.outcome}`,
      ...checklist.map((item) => `Check: ${item}`),
      'Mutation: none until approved through a governed Wilsy command.',
    ],
  };
}

/**
 * @function readWilsyVisibleText
 * @description Reads a bounded sample of visible workspace text so Wilsy Intelligence can infer the operator's current context.
 * @returns {string} Bounded visible document text.
 * @collaboration Wilsy OS global workspaces, CRM Setup Control Plane, Billing workspace, command rails, and adaptive intelligence runtime.
 */
function readWilsyVisibleText() {
  if (typeof document === 'undefined' || !document.body) {
    return '';
  }

  return String(document.body.innerText || '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 9000);
}

/**
 * @function readWilsyStorageValue
 * @description Reads non-secret local storage values that identify tenant or operator posture.
 * @param {Array<string>} keys - Candidate local storage keys.
 * @param {string} fallback - Fallback value.
 * @returns {string} Resolved non-secret value.
 * @collaboration Browser runtime, tenant context shell, operator context, and Wilsy AI evidence headers.
 */
function readWilsyStorageValue(keys = [], fallback = '') {
  if (typeof localStorage === 'undefined') {
    return fallback;
  }

  for (const key of keys) {
    const value = localStorage.getItem(key);
    if (value) {
      return value;
    }
  }

  return fallback;
}

/**
 * @function resolveWilsyWorkspaceIntent
 * @description Classifies the active Wilsy OS workspace from URL, title, and visible screen text.
 * @param {string} path - Current browser path.
 * @param {string} text - Bounded visible workspace text.
 * @returns {Object} Workspace context used by the global intelligence dock.
 * @collaboration Wilsy OS routing, CRM workspaces, billing roadmap, setup controls, evidence workflows, and productivity intelligence.
 */
function resolveWilsyWorkspaceIntent(path = '', text = '') {
  const haystack = `${path} ${text}`.toLowerCase();

  if (haystack.includes('billing') || haystack.includes('invoice') || haystack.includes('revenue ledger')) {
    return {
      workspace: 'Billing',
      focus: 'Revenue assurance',
      role: 'Finance Operator',
      state: 'Billing posture detected',
      purpose: 'Track invoices, receipts, payment state, revenue leakage, tenant entitlements, and future Wilsy AI monetization tiers.',
      nextAction: 'Check open invoices, failed payments, plan limits, and evidence receipts before changing billing state.',
      tierSignal: 'Future value-added AI tier candidate',
    };
  }

  if (haystack.includes('crm operating controls') || haystack.includes('authority graph') || haystack.includes('setup map')) {
    return {
      workspace: 'CRM Setup',
      focus: 'Authority Graph',
      role: 'Security Admin',
      state: 'Setup authority posture detected',
      purpose: 'Watch role power, authority surfaces, evidence posture, approval state, release readiness, and queue hygiene.',
      nextAction: 'Use evidence, approval, release, and queue clear only through governed command paths with receipt proof.',
      tierSignal: 'Included in CRM governance intelligence',
    };
  }

  if (haystack.includes('meeting') || haystack.includes('instant manifest') || haystack.includes('import ledger')) {
    return {
      workspace: 'CRM Meetings',
      focus: 'Meetings Operating Cockpit',
      role: 'CRM Operator',
      state: 'Meeting workflow posture detected',
      purpose: 'Track Sync Data Engine, Instant Manifest, Import Ledger, Evidence Vault, and Universal Filter Stream.',
      nextAction: 'Validate meeting evidence, sync freshness, and import receipts before acting on records.',
      tierSignal: 'Operational intelligence module',
    };
  }

  if (haystack.includes('dashboard') || haystack.includes('founder') || haystack.includes('executive')) {
    return {
      workspace: 'Executive OS',
      focus: 'Operating dashboard',
      role: 'Founder / Executive',
      state: 'Executive command posture detected',
      purpose: 'Surface operating risk, revenue signal, compliance posture, and command priorities across the current boardroom surface.',
      nextAction: 'Inspect active risk cards, revenue signals, and command receipts before escalating.',
      tierSignal: 'Executive intelligence layer',
    };
  }

  return {
    workspace: 'Wilsy OS',
    focus: 'Current workspace',
    role: 'Operator',
    state: 'Workspace context active',
    purpose: 'Read the current route and visible work surface, then turn the screen into context-aware actions and evidence posture.',
    nextAction: 'Continue working; Wilsy AI will adapt as the visible workspace changes.',
    tierSignal: 'Core intelligence layer',
  };
}

/**
 * @function buildWilsyIntelligenceCards
 * @description Builds adaptive cards for the current workspace so the dock gives useful, contextual operator guidance.
 * @param {Object} context - Workspace context.
 * @returns {Array<Object>} Adaptive intelligence cards.
 * @collaboration Wilsy OS Intelligence, CRM setup controls, billing tiers roadmap, governance receipts, and operator productivity loops.
 */
function buildWilsyIntelligenceCards(context = {}) {
  return [
    {
      label: 'WORKSPACE STATUS',
      title: context.state,
      body: context.purpose,
    },
    {
      label: 'OPERATING LENS',
      title: context.role,
      body: `Focus: ${context.focus}. Match actions to the authority and evidence available in this workspace.`,
    },
    {
      label: 'RECOMMENDED NEXT STEP',
      title: 'Operator guidance',
      body: context.nextAction,
    },
    {
      label: 'AI COVERAGE',
      title: context.tierSignal,
      body: context.billingDetail || 'This global intelligence surface is built to support future Wilsy OS billing tiers without changing workspace workflows.',
    },
  ];
}

/**
 * @function loadWilsyDockState
 * @description Loads the persisted Wilsy Intelligence dock view state from local storage.
 * @returns {Object} Persisted dock state.
 * @collaboration Wilsy OS global dock runtime, operator preferences, all workspaces, and persistent productivity controls.
 */
function loadWilsyDockState() {
  if (typeof localStorage === 'undefined') {
    return { collapsed: false, focusMode: false };
  }

  try {
    return {
      collapsed: false,
      focusMode: false,
      ...JSON.parse(localStorage.getItem(WILSY_INTELLIGENCE_STORAGE_KEY) || '{}'),
    };
  } catch {
    return { collapsed: false, focusMode: false };
  }
}

/**
 * @function saveWilsyDockState
 * @description Persists the Wilsy Intelligence dock state without touching workspace data.
 * @param {Object} state - Dock UI state.
 * @returns {void}
 * @collaboration Wilsy OS global dock runtime, browser storage, and operator display preference continuity.
 */
function saveWilsyDockState(state = {}) {
  if (typeof localStorage === 'undefined') {
    return;
  }

  localStorage.setItem(WILSY_INTELLIGENCE_STORAGE_KEY, JSON.stringify(state));
}

/**
 * @function buildWilsyAIInstitutionalHeaders
 * @description Builds institutional headers for the read-only Wilsy AI context resolver request.
 * @param {Object} snapshot - Workspace snapshot.
 * @returns {Object} Institutional headers.
 * @collaboration Global intelligence dock, backend AI context resolver, tenant scope, and strike payload evidence contract.
 */
function buildWilsyAIInstitutionalHeaders(snapshot = {}) {
  const generatedAt = new Date().toISOString();
  const tenantId = readWilsyStorageValue(['wilsyTenantId', 'tenantId', 'activeTenantId'], 'MASTER');
  const operatorId = readWilsyStorageValue(['wilsyOperatorId', 'operatorId', 'userId'], 'BROWSER_OPERATOR');

  return {
    tenantId,
    operatorId,
    generatedAt,
    route: WILSY_AI_CONTEXT_ROUTE,
    commandSurface: 'WILSY_OS_INTELLIGENCE_DOCK',
    workspaceRoute: snapshot.path || '',
    contractVersion: 'P60K5Q10_FRONTEND_CONTEXT_REQUEST',
    mutation: false,
  };
}

/**
 * @function buildWilsyAIContextRequest
 * @description Builds the full evidence-bearing payload sent to the read-only Wilsy AI context resolver.
 * @param {Object} snapshot - Workspace snapshot.
 * @returns {Object} Request payload.
 * @collaboration Workspace sensor, institutional headers, strike payload, backend context resolver, and no-mutation AI contract.
 */
function buildWilsyAIContextRequest(snapshot = {}) {
  const institutionalHeaders = buildWilsyAIInstitutionalHeaders(snapshot);

  return {
    tenantId: institutionalHeaders.tenantId,
    operatorId: institutionalHeaders.operatorId,
    workspaceRoute: snapshot.path || '',
    workspaceSurface: snapshot.text || '',
    operatorIntent: snapshot.intent || '',
    generatedAt: institutionalHeaders.generatedAt,
    institutionalHeaders,
    strikePayload: {
      institutionalHeaders: { ...institutionalHeaders },
      commandSurface: 'WILSY_OS_INTELLIGENCE_DOCK',
      commandType: 'READ_ONLY_AI_CONTEXT_RESOLUTION',
      mutation: false,
    },
  };
}

/**
 * @function mergeWilsyBackendContext
 * @description Merges backend sovereign context with local fallback context for resilient dock rendering.
 * @param {Object} localContext - Local context.
 * @param {Object|null} backendContext - Backend context response.
 * @returns {Object} Renderable context.
 * @collaboration Backend Wilsy AI context resolver, local workspace inference, evidence posture, billing entitlement, and dock cards.
 */
function mergeWilsyBackendContext(localContext = {}, backendContext = null) {
  if (!backendContext?.workspace) {
    return localContext;
  }

  const topAction = backendContext.nextBestActions?.[0];
  return {
    workspace: backendContext.workspace.label || localContext.workspace,
    focus: backendContext.workspace.focus || localContext.focus,
    role: backendContext.workspace.operatingRole || localContext.role,
    state: backendContext.result || localContext.state,
    purpose: backendContext.modelRoute?.selectedRoute
      ? `Guidance source: ${backendContext.modelRoute.selectedRoute}. Checks: ${backendContext.evidencePosture?.status || 'UNKNOWN'}.`
      : localContext.purpose,
    nextAction: topAction ? `${topAction.title}: ${topAction.description}` : localContext.nextAction,
    tierSignal: backendContext.billingEntitlement?.requiredTierSignal || localContext.tierSignal,
    billingDetail: backendContext.billingEntitlement?.upgradeSignal || localContext.billingDetail,
    backendContext,
  };
}

/**
 * @function useWilsyWorkspaceContext
 * @description Observes route and DOM changes so Wilsy Intelligence dynamically adapts to the user's active workspace.
 * @returns {Object} Adaptive workspace snapshot and local context.
 * @collaboration MutationObserver, browser routing, Wilsy OS workspaces, CRM, billing, meetings, and executive command surfaces.
 */
function useWilsyWorkspaceContext() {
  const [snapshot, setSnapshot] = useState(() => ({
    path: typeof window === 'undefined' ? '' : window.location.pathname,
    text: readWilsyVisibleText(),
    intent: '',
  }));

  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined;
    }

    let frame = 0;

    /**
     * @function refreshWilsyWorkspaceSnapshot
     * @description Refreshes the current route and visible-text context for Wilsy OS Intelligence.
     * @returns {void}
     * @collaboration Global Wilsy dock, workspace DOM, browser route changes, and adaptive operator guidance.
     */
    function refreshWilsyWorkspaceSnapshot() {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        setSnapshot({
          path: window.location.pathname,
          text: readWilsyVisibleText(),
          intent: '',
        });
      });
    }

    const observer = new MutationObserver(refreshWilsyWorkspaceSnapshot);
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });

    window.addEventListener('popstate', refreshWilsyWorkspaceSnapshot);
    window.addEventListener('hashchange', refreshWilsyWorkspaceSnapshot);
    window.addEventListener('wilsy:workspace-context-changed', refreshWilsyWorkspaceSnapshot);

    const interval = window.setInterval(refreshWilsyWorkspaceSnapshot, 3500);

    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      window.removeEventListener('popstate', refreshWilsyWorkspaceSnapshot);
      window.removeEventListener('hashchange', refreshWilsyWorkspaceSnapshot);
      window.removeEventListener('wilsy:workspace-context-changed', refreshWilsyWorkspaceSnapshot);
      window.clearInterval(interval);
    };
  }, []);

  return useMemo(
    () => ({
      snapshot,
      localContext: resolveWilsyWorkspaceIntent(snapshot.path, snapshot.text),
    }),
    [snapshot]
  );
}

/**
 * @function useWilsySovereignBrainContext
 * @description Calls the read-only backend Wilsy AI context resolver and falls back to local context if unavailable.
 * @param {Object} snapshot - Workspace snapshot.
 * @param {Object} localContext - Local context.
 * @returns {Object} Backend-aware render context.
 * @collaboration Wilsy AI sovereign context route, global dock, workspace sensor, evidence contract, and resilient frontend fallback.
 */
function useWilsySovereignBrainContext(snapshot = {}, localContext = {}) {
  const [backendContext, setBackendContext] = useState(null);
  const [status, setStatus] = useState('LOCAL_CONTEXT');

  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined;
    }

    const controller = new AbortController();

    /**
     * @function fetchWilsySovereignContext
     * @description Fetches the backend read-only Wilsy AI sovereign context contract.
     * @returns {Promise<void>} Updates backend context state.
     * @collaboration Browser fetch, Express AI route, institutional headers, strike payload, and global intelligence dock.
     */
    async function fetchWilsySovereignContext() {
      try {
        const payload = buildWilsyAIContextRequest(snapshot);
        const response = await fetch(WILSY_AI_CONTEXT_ROUTE, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'X-Tenant-Id': payload.tenantId,
            'X-Operator-Id': payload.operatorId,
            'X-Wilsy-Command-Surface': 'WILSY_OS_INTELLIGENCE_DOCK',
          },          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`Wilsy AI context resolver returned ${response.status}`);
        }

        const rawWilsyAIData = await response.json();

        dispatchWilsyFG82GlobalLeadCreateDraftBridge(rawWilsyAIData);
        const data = buildWilsyAIProductivityCopy(rawWilsyAIData);
        setBackendContext(data);
        setStatus('SOVEREIGN_CONTEXT');
      } catch (error) {
        if (error?.name !== 'AbortError') {
          setStatus('LOCAL_FALLBACK');
          setBackendContext(null);
        }
      }
    }

    fetchWilsySovereignContext();

    return () => {
      controller.abort();
    };
  }, [snapshot.path, snapshot.text]);

  return {
    status,
    context: mergeWilsyBackendContext(localContext, backendContext),
    backendContext,
  };
}

/**
 * @function WilsyOSIntelligenceDock
 * @description Renders the global Wilsy OS adaptive intelligence dock visible across workspaces.
 * @returns {JSX.Element} Global Wilsy Intelligence sidecar.
 * @collaboration All Wilsy OS workspaces, CRM Setup, Billing roadmap, Staged Reviews, command rails, and future monetized intelligence tiers.
 */
export function WilsyOSIntelligenceDock() {

  /* WILSY_P60K5Q10BN_DOCUMENT_REVIEW_STATE_SCOPE */
  const [activeDocumentReview, setActiveDocumentReview] = useState(null);
  const activeDocumentReviewFields = Array.isArray(activeDocumentReview?.fields)
    ? activeDocumentReview.fields.reduce((accumulator, field) => {
        accumulator[String(field.label || '').toLowerCase()] = field.value;
        return accumulator;
      }, {})
    : {};
  const activeDocumentReviewPreview = activeDocumentReview?.documentPreview || (activeDocumentReview
    ? {
        previewVersion: 'P60K5Q10CY_ACTIVE_REVIEW_FALLBACK_LAB',
        brand: {
          tenantName: activeDocumentReview?.tenantName || 'Wilsy OS Tenant',
          seal: 'Wilsy OS',
        },
        document: {
          title: activeDocumentReviewFields.title || activeDocumentReview?.title || 'Document draft',
          documentType: activeDocumentReviewFields['document type'] || activeDocumentReview?.documentType || 'Business document',
          status: activeDocumentReview?.status || 'Draft prepared',
          purpose: activeDocumentReviewFields.purpose || activeDocumentReview?.purpose || 'Prepared for governed review.',
          sections: [
            {
              title: 'Source and tenant branding',
              body: 'Wilsy stages this draft inside the AI lab so the operator can verify the tenant source, brand posture, and document purpose before any execution command.',
            },
            {
              title: 'Approval workflow',
              body: 'Send remains locked until recipient details, delivery connector binding, and approval are complete.',
            },
            {
              title: 'Execution readiness',
              body: 'Package and send stay locked until the operator completes approval and evidence requirements.',
            },
          ],
        },
      }
    : null);

  const { snapshot, localContext } = useWilsyWorkspaceContext();
  const { status, context, backendContext } = useWilsySovereignBrainContext(snapshot, localContext);
  const cards = useMemo(() => buildWilsyIntelligenceCards(context), [context]);
  const [dockState, setDockState] = useState(loadWilsyDockState);
















  /* WILSY_P60K5Q10CA_SPLIT_DOCK_EVENT_BRIDGE */
  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined;
    }

    /**
     * @function handleWilsyAISplitRuntimeOpenRequest
     * @description Opens the Wilsy OS Intelligence dock from the isolated compact launcher root while preserving dock size and document review state.
     * @returns {void} Opens the dock from the split runtime launcher event.
     * @collaboration WilsyOSIntelligenceLauncher, WilsyOSIntelligenceDockRuntime, WilsyOSIntelligenceDock, and tenant productivity shell.
     */
    function handleWilsyAISplitRuntimeOpenRequest() {
      setDockState((previousDockState) => {
        if (
          previousDockState &&
          typeof previousDockState === 'object' &&
          !Array.isArray(previousDockState)
        ) {
          return {
            ...previousDockState,
            isOpen: true,
            open: true,
            visible: true,
            expanded: true,
            
            collapsed: false,minimized: false,
            compact: false,
          };
        }

        if (typeof previousDockState === 'string') {
          return 'open';
        }

        return true;
      });
    }

    window.addEventListener('wilsy-os-intelligence-open-request', handleWilsyAISplitRuntimeOpenRequest);

    return () => {
      window.removeEventListener('wilsy-os-intelligence-open-request', handleWilsyAISplitRuntimeOpenRequest);
    };
  }, []);

  const [operatorPrompt, setOperatorPrompt] = useState('');
  const [wilsySubmittedQuestion, setWilsySubmittedQuestion] = useState('');
  const [wilsySuggestionRefreshKey, setWilsySuggestionRefreshKey] = useState(() => Date.now());
  const [operatorBackendBusy, setOperatorBackendBusy] = useState(false);
  const [operatorBackendError, setOperatorBackendError] = useState('');
  const [operatorBackendModel, setOperatorBackendModel] = useState(null);
  const [activePrompt, setActivePrompt] = useState('what_next');
  const [planCopied, setPlanCopied] = useState(false);
  const [wilsyInlineComposerStream, setWilsyInlineComposerStream] = useState({ active: false, text: '', streamKey: '', tokens: [] });
  const [wilsyConversationThreads, setWilsyConversationThreads] = useState(() => loadWilsyAIConversationThreads());
  const [wilsyActiveConversationId, setWilsyActiveConversationId] = useState('');
  const operatorModel = useMemo(
    () =>
      buildWilsyOperatorModelSurface({
        context,
        backendContext,
        cards,
        operatorPrompt,
        activePrompt,
      }),
    [context, backendContext, cards, operatorPrompt, activePrompt]
  );
  const liveOperatorModel = operatorBackendModel || operatorModel;
  const wilsyHasSubmittedOperatorResult = Boolean(operatorBackendBusy || operatorBackendModel);

  /**
   * @function updateDockState
   * @description Updates and persists the global Wilsy AI dock state.
   * @param {Object} nextState - Partial state update.
   * @returns {void}
   * @collaboration Wilsy AI sidecar controls, workspace visibility, and operator display preferences.
   */
  function updateDockState(nextState = {}) {
    setDockState((current) => {
      const merged = { ...current, ...nextState };
      saveWilsyDockState(merged);
      return merged;
    });
  }

  /**
   * @function handleWilsyAskSubmit
   * @description Sends the operator prompt to the backend Wilsy Operator Model and renders the live tool-backed answer.
   * @param {Event} event - Form submit event.
   * @returns {Promise<void>} Resolves after backend model answer is applied.
   * @collaboration Wilsy Operator Model backend, source-registry GET bridge, CRM source tools, and no-mutation governance boundary.
   */
  async function handleWilsyAskSubmit(event) {
    event.preventDefault();

    const wilsyFG84GlobalLeadCreateDraft = buildWilsyFG84GlobalLeadCreateDraft(operatorPrompt);
    if (dispatchWilsyFG84GlobalAskLeadCreateDraft(wilsyFG84GlobalLeadCreateDraft)) {
      /* P60K5Q10FG84_GLOBAL_ASK_SUBMIT_DIRECT_ROUTER */
      if (typeof setWilsyHasSubmittedOperatorResult === 'function') {
        /* P60K5Q10FG90B_SAFE_SUBMITTED_OPERATOR_RESULT_SETTER */
      if (typeof setWilsyHasSubmittedOperatorResult === 'function') {
        setWilsyHasSubmittedOperatorResult(true);
      }
      }
      if (typeof setLiveOperatorModel === 'function') {
        setLiveOperatorModel(wilsyFG84GlobalLeadCreateDraft.packet.operatorModel);
      }
      if (typeof setWilsyInlineComposerStream === 'function') {
        setWilsyInlineComposerStream({
          active: false,
          text: wilsyFG84GlobalLeadCreateDraft.packet.operatorModel.answer,
          streamKey: 'P60K5Q10FG84_GLOBAL_ASK_DIRECT_LEAD_CREATE_ROUTER',
          tokens: [
            {
              id: 'open_create_lead_draft',
              intent: 'create_lead',
              label: 'Open Create Lead draft',
              prompt: 'Open the governed Create Lead draft',
            },
          ],
        });
      }
      if (typeof setOperatorBackendBusy === 'function') {
        setOperatorBackendBusy(false);
      }
      if (typeof setOperatorPrompt === 'function') {
        setOperatorPrompt('');
      }
      return;
    }



    const question = operatorPrompt.trim();
    setWilsySubmittedQuestion(question);
    setOperatorPrompt('');

    if (!question) {
      return;
    }

    setActivePrompt(resolveWilsyOperatorIntent(question, activePrompt));
    setOperatorBackendBusy(true);
    setOperatorBackendError('');

    try {
      const response = await fetch(buildWilsyOperatorAskUrl(question, snapshot, context), {
        method: 'GET',
        headers: {
          Accept: 'application/json',
          'X-Tenant-Id': window.localStorage?.getItem('wilsy-tenant-id') || 'MASTER',
          'X-Operator-Id': window.localStorage?.getItem('wilsy-operator-id') || 'WILSY_OPERATOR',
          'X-Wilsy-Command-Surface': 'WILSY_OS_OPERATOR_MODEL',
        },
      });

      const payload = await parseWilsyOperatorJsonResponse(response);

      if (!response.ok || payload?.error) {
        throw new Error(payload?.error?.message || payload?.message || 'Wilsy Operator Model could not answer yet.');
      }

      if (payload?.operatorModel) {
        setOperatorBackendModel(normalizeWilsyFoundryModelForDisplay(payload.operatorModel));
      } else {
        throw new Error('Wilsy Operator Model returned no operatorModel payload.');
      }
    } catch (error) {
      const message = error?.message || 'Wilsy Operator Kernel could not answer yet.';
      setOperatorBackendModel(normalizeWilsyFoundryModelForDisplay({
        intent: 'operator_kernel_error',
        domain: null,
        supported: false,
        title: 'Workspace source needs attention',
        answer: message,
        outcome: 'Checked: workspace source · Needs attention · Next: reconnect source',
        progress: 'Kernel error',
        quickPrompts: liveOperatorModel?.quickPrompts || [],
        actions: [
          {
            rank: 1,
            title: 'Repair failed tool response',
            description: message,
            mode: 'read_only',
            mutation: false,
          },
        ],
        checklist: [
          'Verify the endpoint returned JSON.',
          'Confirm the tool exists in the Operator Kernel registry.',
          'Confirm the source is bound for the tenant.',
        ],
        commandPlan: [
          `Question: ${operatorPrompt}`,
          `Error: ${message}`,
          'Mutation: none. No fake command prepared.',
        ],
        sourceTrace: [
          {
            tool: 'workspace_source',
            domain: null,
            status: 'FAILED',
            count: null,
            collectionsChecked: [],
            message,
          },
        ],
      }));
      setOperatorBackendError('');
    } finally {
      setOperatorBackendBusy(false);
    }
  }

  /**
   * @function resolveWilsyAIWorkspaceCommand
   * @description Resolves AI command labels into workspace-opening commands so command clicks do real work instead of repeating chat.
   * @param {Object|string} command - Command token, label, or prompt payload.
   * @returns {Object|null} Workspace command payload.
   * @collaboration Wilsy AI command links, CRM Setup work surfaces, authority graph, evidence vault, release readiness, queue hygiene, and control boundary navigation.
   */
  function resolveWilsyAIWorkspaceCommand(command = {}) {
    const label =
      typeof command === 'string'
        ? command
        : String(command.label || command.title || command.prompt || command.description || command.name || '').trim();

    const commands = [
      {
        match: /trace authority route|review setup authority|authority graph|authority path/i,
        commandId: 'trace_authority_route',
        label: 'Trace authority route',
        receipt: 'Opening Authority Graph so you can complete reviewer, approver, release owner, and mutation-boundary review.',
        selectors: [
          '[data-wilsy-crm-setup-surface="authority_graph"]',
          '[data-wilsy-surface="authority_graph"]',
          '[aria-label*="Authority"]',
          '[data-control-surface*="authority"]',
        ],
        textTargets: ['Authority Graph', 'Review setup authority', 'Authority', 'Roles', 'Approvals'],
      },
      {
        match: /bind evidence anchors|evidence gaps|evidence vault|missing evidence|proof/i,
        commandId: 'bind_evidence_anchors',
        label: 'Bind evidence anchors',
        receipt: 'Opening Evidence Vault so you can bind missing role proof, source proof, and release receipts.',
        selectors: [
          '[data-wilsy-crm-setup-surface="evidence_vault"]',
          '[data-wilsy-surface="evidence_vault"]',
          '[aria-label*="Evidence"]',
          '[data-control-surface*="evidence"]',
        ],
        textTargets: ['Evidence Vault', 'Evidence', 'Proof', 'Receipts', 'Required evidence'],
      },
      {
        match: /judge release route|release checklist|safe to release|release readiness|approval/i,
        commandId: 'judge_release_route',
        label: 'Judge release route',
        receipt: 'Opening Release Readiness so you can verify approval gates and release blockers.',
        selectors: [
          '[data-wilsy-crm-setup-surface="release_readiness"]',
          '[data-wilsy-surface="release_readiness"]',
          '[aria-label*="Release"]',
          '[aria-label*="Approval"]',
          '[data-control-surface*="release"]',
        ],
        textTargets: ['Release', 'Release checklist', 'Approval', 'Completion path', 'Review packet staged'],
      },
      {
        match: /inspect queue drift|queue hygiene|queue drift|import ledger|ledger/i,
        commandId: 'inspect_queue_drift',
        label: 'Inspect queue drift',
        receipt: 'Opening Queue Hygiene so you can inspect stale reviews, orphan approvals, and missing receipts.',
        selectors: [
          '[data-wilsy-crm-setup-surface="queue_hygiene"]',
          '[data-wilsy-surface="queue_hygiene"]',
          '[aria-label*="Queue"]',
          '[data-control-surface*="queue"]',
        ],
        textTargets: ['Queue', 'Queue hygiene', 'Import Ledger', 'Review queue', 'Ledger'],
      },
      {
        match: /split control boundary|control boundary|permission|role boundary|mutation power/i,
        commandId: 'split_control_boundary',
        label: 'Split control boundary',
        receipt: 'Opening Control Boundary so you can separate review, approval, release, and mutation powers.',
        selectors: [
          '[data-wilsy-crm-setup-surface="control_boundary"]',
          '[data-wilsy-surface="control_boundary"]',
          '[aria-label*="Control"]',
          '[aria-label*="Boundary"]',
          '[data-control-surface*="control"]',
        ],
        textTargets: ['Control', 'Boundary', 'Permissions', 'Mutation', 'Roles'],
      },
    ];

    if (!label) {
      return null;
    }

    const matched = commands.find((item) => item.match.test(label));

    if (!matched) {
      return null;
    }

    return {
      ...matched,
      sourceLabel: label,
      generatedAt: new Date().toISOString(),
    };
  }

  /**
   * @function openWilsyAIWorkspaceCommandSurface
   * @description Opens or scrolls to the existing CRM Setup component that completes a Wilsy AI command.
   * @param {Object} command - Resolved workspace command.
   * @returns {boolean} True when a matching visible target was found.
   * @collaboration Wilsy AI command routing, CRM Setup DOM surfaces, component opening, scroll navigation, and operator task completion.
   */
  function openWilsyAIWorkspaceCommandSurface(command = {}) {
    if (typeof window === 'undefined' || typeof document === 'undefined' || !command?.commandId) {
      return false;
    }

    window.dispatchEvent(
      new CustomEvent('wilsy-crm-setup-open-workspace-command', {
        detail: {
          commandId: command.commandId,
          label: command.label,
          sourceLabel: command.sourceLabel,
          receipt: command.receipt,
          generatedAt: command.generatedAt,
          tenantId: context?.tenantId || context?.tenant || 'wilsy-sovereign-root',
          operatorRole: context?.role || 'operator',
        },
      }),
    );

    document.documentElement.setAttribute('data-wilsy-ai-requested-workspace-command', command.commandId);

    const directTarget = (command.selectors || [])
      .map((selector) => document.querySelector(selector))
      .find(Boolean);

    const clickables = Array.from(
      document.querySelectorAll('button, [role="tab"], [role="button"], a, [data-wilsy-action], [data-control-id]'),
    );
    const textTarget = clickables.find((node) => {
      const nodeText = String(node.textContent || node.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim();
      return (command.textTargets || []).some((target) => nodeText.toLowerCase().includes(String(target).toLowerCase()));
    });
    const targetNode = directTarget || textTarget || document.querySelector('[data-wilsy-crm-setup-control-plane]');

    if (textTarget && typeof textTarget.click === 'function') {
      textTarget.click();
    }

    if (targetNode && typeof targetNode.scrollIntoView === 'function') {
      window.requestAnimationFrame(() => {
        targetNode.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' });
      });
    }

    window.dispatchEvent(
      new CustomEvent('wilsy-crm-setup-command-surface-opened', {
        detail: {
          ...command,
          opened: Boolean(targetNode),
          openedAt: new Date().toISOString(),
        },
      }),
    );

    return Boolean(targetNode);
  }

  /**
   * @function handleWilsyAIWorkspaceCommand
   * @description Routes a Wilsy AI command click into a CRM Setup workspace surface and replaces repeated answer text with a short opening receipt.
   * @param {Object|string} command - Command token or label.
   * @returns {boolean} True when the command was handled.
   * @collaboration Wilsy AI inline commands, CRM Setup component opening, chat-loop prevention, task completion, and governed operator receipts.
   */
  function handleWilsyAIWorkspaceCommand(command = {}) {
    const resolvedCommand = resolveWilsyAIWorkspaceCommand(command);

    if (!resolvedCommand) {
      return false;
    }

    const opened = openWilsyAIWorkspaceCommandSurface(resolvedCommand);

    setActivePrompt(resolvedCommand.commandId);
    setOperatorPrompt('');
    setWilsySubmittedQuestion('');
    setWilsyInlineComposerStream({
      active: false,
      text: opened
        ? resolvedCommand.receipt
        : `${resolvedCommand.receipt} I could not find a visible surface yet, but I raised the workspace command event for CRM Setup.`,
      streamKey: `workspace-command-${resolvedCommand.commandId}-${Date.now()}`,
      tokens: [],
    });

    return true;
  }

  /**
   * @function handleWilsyQuickPrompt
   * @description Runs a workspace quick prompt through the Wilsy Operator Model.
   * @param {Object} prompt - Quick prompt descriptor.
   * @returns {void}
   * @collaboration Operator quick prompts, CRM Setup authority guidance, evidence checklist, and release readiness workflow.
   */
  function handleWilsyQuickPrompt(prompt = {}) {
    if (handleWilsyAIWorkspaceCommand(prompt)) {
      return;
    }
    recordWilsyAISuggestionUsage(prompt);
    const promptLabel = String(prompt.label || prompt.title || prompt.prompt || prompt.description || '').trim();
    const nextPromptId = prompt.intent || prompt.id || resolveWilsyOperatorIntent(promptLabel, activePrompt) || 'what_next';

    if (!promptLabel) {
      return;
    }

    const intelligenceModel = buildWilsyOperatorIntelligence({
      promptText: promptLabel,
      context,
      baseModel: operatorModel,
      liveModel: liveOperatorModel,
      forcedIntent: nextPromptId,
      resolveIntent: resolveWilsyOperatorIntent,
    });

    setActivePrompt(nextPromptId);
    setOperatorPrompt('');
    const wilsyDirectStreamModel = normalizeWilsyFoundryModelForDisplay(intelligenceModel);
    const wilsyDirectFallbackText =
      'I hear you. I am reading the current workspace and typing the next useful move directly into this composer.';
    const wilsyDirectStreamText =
      String(buildWilsyNaturalConversationAnswer(wilsyDirectStreamModel, promptLabel) || wilsyDirectFallbackText).trim() ||
      wilsyDirectFallbackText;
    const wilsyDirectStreamTokens = Array.isArray(wilsyDirectStreamModel.commandTokens)
      ? wilsyDirectStreamModel.commandTokens
      : Array.isArray(wilsyDirectStreamModel.executionThread)
        ? wilsyDirectStreamModel.executionThread
        : Array.isArray(wilsyDirectStreamModel.playableActions)
          ? wilsyDirectStreamModel.playableActions
          : Array.isArray(wilsyDirectStreamModel.actions)
            ? wilsyDirectStreamModel.actions
            : [];
    const wilsyDirectStreamGlyphs = Array.from(wilsyDirectStreamText);
    const wilsyDirectStreamKey = 'directive-direct-typewriter-' + nextPromptId + '-' + Date.now();
    let wilsyDirectStreamCursor = Math.min(1, wilsyDirectStreamGlyphs.length);

    applyWilsyConversationHistoryResult(
      persistWilsyAIConversationTurn({
        activeThreadId: wilsyActiveConversationId,
        threads: wilsyConversationThreads,
        workspace: resolveWilsyActiveConversationWorkspace(),
        model: wilsyDirectStreamModel,
        context,
        promptText: promptLabel,
        answerText: wilsyDirectStreamText,
        intent: nextPromptId,
      }),
    );

    setOperatorBackendModel(wilsyDirectStreamModel);

    if (typeof window !== 'undefined') {
      if (window.__wilsyDirectiveAutosubmitTypeTimer) {
        window.clearInterval(window.__wilsyDirectiveAutosubmitTypeTimer);
      }

      if (window.__wilsyInlineComposerStreamTimer) {
        window.clearInterval(window.__wilsyInlineComposerStreamTimer);
      }

      setWilsyInlineComposerStream({
        active: true,
        text: wilsyDirectStreamGlyphs.slice(0, wilsyDirectStreamCursor).join(''),
        streamKey: wilsyDirectStreamKey,
        tokens: wilsyDirectStreamTokens.slice(0, 8),
      });

      window.__wilsyDirectiveAutosubmitTypeTimer = window.setInterval(() => {
        wilsyDirectStreamCursor = Math.min(wilsyDirectStreamCursor + 1, wilsyDirectStreamGlyphs.length);

        setWilsyInlineComposerStream({
          active: wilsyDirectStreamCursor < wilsyDirectStreamGlyphs.length,
          text: wilsyDirectStreamGlyphs.slice(0, wilsyDirectStreamCursor).join(''),
          streamKey: wilsyDirectStreamKey,
          tokens: wilsyDirectStreamTokens.slice(0, 8),
        });

        if (wilsyDirectStreamCursor >= wilsyDirectStreamGlyphs.length) {
          window.clearInterval(window.__wilsyDirectiveAutosubmitTypeTimer);
          window.__wilsyDirectiveAutosubmitTypeTimer = null;
        }
      }, 34);
    }
    setOperatorBackendBusy(false);
    setOperatorBackendError('');
    setPlanCopied(false);
  }

  /**
   * @function handleCopyWilsyCommandPlan
   * @description Copies the current governed command preparation plan for operator review.
   * @returns {Promise<void>} Resolves after clipboard copy attempt.
   * @collaboration Wilsy AI operator model, no-mutation command preparation, and human approval handoff.
   */
  async function handleCopyWilsyCommandPlan() {
    const plan = (liveOperatorModel.commandPlan || []).join('\n');

    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(plan);
      }

      setPlanCopied(true);
      window.setTimeout(() => setPlanCopied(false), 1600);
    } catch (error) {
      setPlanCopied(false);
    }
  }

      /* WILSY_P60K5Q10EE_CINEMATIC_COMPOSER_PRINT_GATE_EFFECT */
  /**
   * @description Materializes the composer only while text is printing and streams a richer response character-by-character.
   * @collaboration Wilsy AI dock, cinematic composer print gate, natural response engine, source route judge, and inline command links.
   */
  useEffect(() => {
    if (!wilsyHasSubmittedOperatorResult || operatorBackendBusy || activeDocumentReview) {
      return undefined;
    }

    const wilsyResponsePromptText = String(wilsySubmittedQuestion || operatorPrompt || '').trim();
    const streamText = buildWilsyNaturalConversationAnswer(liveOperatorModel, wilsyResponsePromptText);
    const streamKey = `${activePrompt}::${wilsyResponsePromptText}::${streamText}`;

    if (wilsyResponsePromptText) {
      applyWilsyConversationHistoryResult(
        persistWilsyAIConversationTurn({
          activeThreadId: wilsyActiveConversationId,
          threads: wilsyConversationThreads,
          workspace: resolveWilsyActiveConversationWorkspace(),
          model: liveOperatorModel,
          context,
          promptText: wilsyResponsePromptText,
          answerText: streamText,
          intent: activePrompt,
        }),
      );
    }



    if (
      wilsyInlineComposerStream.active &&
      String(wilsyInlineComposerStream.streamKey || '').startsWith('directive-direct-typewriter-')
    ) {
      return undefined;
    }

    if (!streamText || wilsyInlineComposerStream.streamKey === streamKey) {
      return undefined;
    }

    const commandTokens = Array.isArray(liveOperatorModel.commandTokens)
      ? liveOperatorModel.commandTokens
      : Array.isArray(liveOperatorModel.executionThread)
        ? liveOperatorModel.executionThread
        : Array.isArray(liveOperatorModel.playableActions)
          ? liveOperatorModel.playableActions
          : Array.isArray(liveOperatorModel.actions)
            ? liveOperatorModel.actions
            : [];

    const glyphs = Array.from(streamText);
    let cursor = 0;

    if (window.__wilsyInlineComposerStreamTimer) {
      window.clearTimeout(window.__wilsyInlineComposerStreamTimer);
      window.clearInterval(window.__wilsyInlineComposerStreamTimer);
    }

    setWilsyInlineComposerStream({
      active: true,
      text: '',
      streamKey,
      tokens: commandTokens.slice(0, 8),
    });

    /**
     * @function printNextGlyph
     * @description Prints the next burst of composer glyphs into the single Wilsy response surface without dumping the full answer at once.
     * @returns {void}
     * @collaboration Wilsy cinematic composer, response-slot owner, character stream timer, and inline command output.
     */
    const printNextGlyph = () => {
      const burst = glyphs[cursor] === '\n' ? 1 : 2;
      cursor = Math.min(cursor + burst, glyphs.length);

      setWilsyInlineComposerStream((current) => ({
        ...current,
        active: cursor < glyphs.length,
        text: glyphs.slice(0, cursor).join(''),
        tokens: commandTokens.slice(0, 8),
      }));

      if (cursor < glyphs.length) {
        const delay = glyphs[cursor - 1] === '.' || glyphs[cursor - 1] === '\n' ? 76 : 16;
        window.__wilsyInlineComposerStreamTimer = window.setTimeout(printNextGlyph, delay);
      }
    };

    window.__wilsyInlineComposerStreamTimer = window.setTimeout(printNextGlyph, 30);

    return () => {
      if (window.__wilsyInlineComposerStreamTimer) {
        window.clearTimeout(window.__wilsyInlineComposerStreamTimer);
        window.clearInterval(window.__wilsyInlineComposerStreamTimer);
      }
    };
  }, [
    activeDocumentReview,
    activePrompt,
    liveOperatorModel,
    operatorBackendBusy,
    operatorPrompt,
    wilsyHasSubmittedOperatorResult,
    wilsyInlineComposerStream.streamKey,
  ]);

  useEffect(() => {
    /**
     * @function refreshWilsyDynamicSuggestionsOnOpen
     * @description Refreshes the dynamic suggestion entropy whenever the Wilsy AI dock opens.
     * @returns {void} Refreshes the suggestion key.
     * @collaboration Wilsy AI split launcher, isolated dynamic suggestion engine, open lifecycle, and non-repeating prompt recommendations.
     */
    const refreshWilsyDynamicSuggestionsOnOpen = () => {
      setWilsySuggestionRefreshKey(Date.now() + Math.floor(Math.random() * 1000000));
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('wilsy-os-intelligence-open-request', refreshWilsyDynamicSuggestionsOnOpen);
      window.addEventListener('wilsy-ai-refresh-suggestions', refreshWilsyDynamicSuggestionsOnOpen);
    }

    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('wilsy-os-intelligence-open-request', refreshWilsyDynamicSuggestionsOnOpen);
        window.removeEventListener('wilsy-ai-refresh-suggestions', refreshWilsyDynamicSuggestionsOnOpen);
      }
    };
  }, []);

  /**
   * @function resolveWilsyActiveConversationWorkspace
   * @description Resolves the current workspace label for Wilsy AI conversation history.
   * @returns {string} Active workspace label.
   * @collaboration Wilsy AI chat history, CRM workspace context, operator model state, and named conversation controls.
   */
  function resolveWilsyActiveConversationWorkspace() {
    return String(context?.workspace || liveOperatorModel?.workspace || liveOperatorModel?.module || liveOperatorModel?.contextLabel || 'Workspace')
      .replace(/\s+/g, ' ')
      .trim();
  }

  /**
   * @function applyWilsyConversationHistoryResult
   * @description Applies a persisted chat history result into React state.
   * @param {Object} result - Conversation persistence result.
   * @returns {void}
   * @collaboration Wilsy AI named chats, active conversation selection, local history state, and operator continuity.
   */
  function applyWilsyConversationHistoryResult(result = {}) {
    if (!result || !Array.isArray(result.threads)) {
      return;
    }

    setWilsyConversationThreads(result.threads);
    setWilsyActiveConversationId(result.activeThreadId || result.thread?.id || '');
  }

  /**
   * @function handleWilsyStartNewChat
   * @description Starts a new named Wilsy AI chat for the current workspace without deleting previous history.
   * @returns {void}
   * @collaboration Wilsy AI new chat, contextual title creation, previous chat history, and active conversation reset.
   */
  function handleWilsyStartNewChat() {
    const nextThread = createWilsyAIConversationThread({
      workspace: resolveWilsyActiveConversationWorkspace(),
      model: liveOperatorModel,
      context,
    });
    const nextThreads = [nextThread, ...loadWilsyAIConversationThreads()].slice(0, 60);

    setWilsyConversationThreads(nextThreads);
    setWilsyActiveConversationId(nextThread.id);
    setOperatorPrompt('');
    setWilsyInlineComposerStream({ active: false, text: '', streamKey: '', tokens: [] });

    setActivePrompt('what_next');
    setOperatorBackendModel(null);
    setActiveDocumentReview(null);
    setOperatorBackendBusy(false);
    setOperatorBackendError('');
    setWilsySuggestionRefreshKey(Date.now() + Math.floor(Math.random() * 1000000));
  }

  /**
   * @function handleWilsySelectConversationThread
   * @description Opens a previous Wilsy AI chat from the named history list.
   * @param {Object} event - Select change event.
   * @returns {void}
   * @collaboration Wilsy AI previous chats, named conversation recovery, answer restoration, and operator recall.
   */
  function handleWilsySelectConversationThread(event) {
    const threadId = String(event?.target?.value || '').trim();
    const threads = loadWilsyAIConversationThreads();
    const selectedThread = threads.find((thread) => thread?.id === threadId);

    setWilsyConversationThreads(threads);
    setWilsyActiveConversationId(threadId);

    if (!selectedThread) {
      setWilsyInlineComposerStream({ active: false, text: '', streamKey: '', tokens: [] });
      return;
    }

    const latestTurn = Array.isArray(selectedThread.turns) ? selectedThread.turns[selectedThread.turns.length - 1] : null;

    setOperatorPrompt('');
    setWilsyInlineComposerStream({
      active: false,
      text: latestTurn?.answerText || '',
      streamKey: `history-${selectedThread.id}-${Date.now()}`,
      tokens: [],
    });
  }

  /**
   * @function handleWilsyClearConversationHistory
   * @description Clears local Wilsy AI chat history without using browser-native confirmation dialogs.
   * @returns {void}
   * @collaboration Wilsy AI clear history, local privacy control, previous chat list reset, and safe in-app actions.
   */
  function handleWilsyClearConversationHistory() {
    clearWilsyAIConversationThreads();
    setWilsyConversationThreads([]);
    setWilsyActiveConversationId('');
    setOperatorPrompt('');
    setWilsyInlineComposerStream({ active: false, text: '', streamKey: '', tokens: [] });
  }

  /**
   * @function handleWilsyCloseDock
   * @description Closes Wilsy AI and closes the active chat session while preserving saved history.
   * @returns {void}
   * @collaboration Wilsy AI dock close, active chat lifecycle, saved history preservation, and split runtime controls.
   */
  function handleWilsyCloseDock() {
    setWilsyActiveConversationId('');
    setOperatorPrompt('');
    setWilsyInlineComposerStream({ active: false, text: '', streamKey: '', tokens: [] });
    updateDockState({ collapsed: true });
  }

  useEffect(() => {
    /**
     * @function refreshWilsyConversationHistoryOnOpen
     * @description Refreshes the named chat history list whenever Wilsy AI opens.
     * @returns {void} Refreshes local chat history state.
     * @collaboration Wilsy AI dock open lifecycle, previous chat history, local storage, and active conversation controls.
     */
    const refreshWilsyConversationHistoryOnOpen = () => {
      setWilsyConversationThreads(loadWilsyAIConversationThreads());
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('wilsy-os-intelligence-open-request', refreshWilsyConversationHistoryOnOpen);
    }

    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('wilsy-os-intelligence-open-request', refreshWilsyConversationHistoryOnOpen);
      }
    };
  }, []);


  useEffect(() => {
    /* P60K5Q10FG85_GLOBAL_ASK_CAPTURE_SUBMIT_LISTENER */
    if (typeof window === 'undefined' || typeof document === 'undefined') {
      return undefined;
    }

    /**
     * @function handleWilsyFG85GlobalAskSubmitCapture
     * @description Captures create-lead prompts before the CRM Setup copilot submit flow can swallow the draft.
     * @param {SubmitEvent} event - Native submit event from the visible Wilsy AI Ask form.
     * @returns {void}
     * @collaboration Global Ask form, governed Lead draft parser, Add Lead control, and Leads Create surface.
     */
    function handleWilsyFG85GlobalAskSubmitCapture(event) {
      const form = event.target?.closest?.('form');
      const input = form?.querySelector?.('input[aria-label="Ask Wilsy"], input[placeholder*="Ask Wilsy"]');

      if (!form || !input) {
        return;
      }

      const promptText = normalizeWilsyFG85LeadCreatePromptText(input.value);
      const eventDetail = buildWilsyFG85GlobalLeadCreateDraft(promptText);

      if (!eventDetail) {
        return;
      }

      event.preventDefault();
      event.stopPropagation();

      if (typeof event.stopImmediatePropagation === 'function') {
        event.stopImmediatePropagation();
      }

      dispatchWilsyFG85GlobalLeadDraft(eventDetail);

      /* P60K5Q10FG86B_DIRECT_LEAD_CREATE_CHAT_STATE_FINALIZER */
      const wilsyFG86LeadDraft = eventDetail.leadCreateDraft || {};
      const wilsyFG86LeadCreateAnswer =
        eventDetail.packet?.operatorModel?.answer ||
        `I prepared a governed Create Lead draft for ${wilsyFG86LeadDraft.name || 'this lead'}. Review it and press Save.`;
      const wilsyFG86Now = new Date().toISOString();
      const wilsyFG86Thread = {
        id: `wilsy-lead-create-${Date.now()}`,
        title: `CRM Leads · ${wilsyFG86LeadDraft.name || 'Create Lead draft'}`,
        workspace: 'CRM Leads',
        updatedAt: wilsyFG86Now,
        messages: [
          {
            id: `operator-${Date.now()}`,
            role: 'operator',
            content: promptText,
            createdAt: wilsyFG86Now,
          },
          {
            id: `wilsy-${Date.now()}`,
            role: 'wilsy',
            content: wilsyFG86LeadCreateAnswer,
            createdAt: wilsyFG86Now,
          },
        ],
      };

      try {
        const existingThreads = loadWilsyAIConversationThreads();
        const nextThreads = [
          wilsyFG86Thread,
          ...existingThreads.filter(thread => thread?.id !== wilsyFG86Thread.id),
        ].slice(0, 60);

        saveWilsyAIConversationThreads(nextThreads);
        setWilsyConversationThreads(nextThreads);
        setWilsyActiveConversationId(wilsyFG86Thread.id);
      } catch {
        // Chat history persistence must not block Create Lead hydration.
      }

      setOperatorPrompt('');
      setWilsyHasSubmittedOperatorResult(true);

      if (typeof setLiveOperatorModel === 'function') {
        setLiveOperatorModel(eventDetail.packet?.operatorModel || {});
      }

      if (typeof setWilsyInlineComposerStream === 'function') {
        setWilsyInlineComposerStream({
          active: false,
          text: wilsyFG86LeadCreateAnswer,
          streamKey: 'P60K5Q10FG86B_DIRECT_LEAD_CREATE_CHAT_STATE_FINALIZER',
          tokens: [
            {
              id: 'open_create_lead_draft',
              intent: 'create_lead',
              label: 'Review Create Lead draft',
              prompt: 'Review the governed Create Lead draft and press Save.',
            },
          ],
        });
      }

      if (typeof setOperatorBackendBusy === 'function') {
        setOperatorBackendBusy(false);
      }

      input.value = '';
      input.dispatchEvent(new Event('input', { bubbles: true }));
    }

    document.addEventListener('submit', handleWilsyFG85GlobalAskSubmitCapture, true);

    return () => {
      document.removeEventListener('submit', handleWilsyFG85GlobalAskSubmitCapture, true);
    };
  }, []);


  const dynamicWilsyQuickPrompts = useMemo(
    () => buildWilsyDynamicSuggestions({
      model: liveOperatorModel || operatorModel || {},
      context,
      promptText: operatorPrompt,
      refreshKey: wilsySuggestionRefreshKey,
      minimumCount: 6,
      persistExposure: false,
    }),
    [liveOperatorModel, operatorModel, context, operatorPrompt, wilsySuggestionRefreshKey],
  );
  const dynamicWilsyComposerPlaceholder = buildWilsyDynamicComposerPlaceholder(liveOperatorModel);

  const dockClassName = [
    styles.dock,
    dockState.collapsed ? styles.collapsed : '',
    dockState.focusMode ? styles.focusMode : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <aside className={dockClassName} aria-label="Wilsy OS adaptive intelligence dock">
      <section className={styles.shell}>
        <header className={styles.header}>
          <div>
            <p>WILSY OS OPERATOR MODEL · LIVE WORKSPACE</p>
            <h3>{context.workspace} · Productivity Copilot</h3>
          </div>
          <div className={styles.actions}>
            <button
              type="button"
              onClick={() => updateDockState({ focusMode: !dockState.focusMode })}
              aria-pressed={dockState.focusMode}
            >
              {dockState.focusMode ? 'Full size' : 'Compact'}
            </button>
            <button type="button" onClick={handleCopyWilsyCommandPlan}>
              {planCopied ? 'Copied' : 'Copy plan'}
            </button>
            <button type="button" onClick={handleWilsyCloseDock}>
              Close
            </button>
          </div>
        </header>

        <div className={styles.contextStrip}>
          <span>{context.focus}</span>
          <strong>{context.role}</strong>
        </div>

        <div className={styles.body}>
          <section className={styles.operatorWorkbench}>
            {/* WILSY_P60K5Q10ET_CONTEXTUAL_CHAT_HISTORY_UI */}
            <div className={styles.wilsyConversationMemoryDock} data-wilsy-ai-chat-history="true">
              <button type="button" className={styles.wilsyConversationNewButton} onClick={handleWilsyStartNewChat}>
                New chat
              </button>
              <label className={styles.wilsyConversationThreadFrame}>
                <strong className={styles.wilsyConversationEyebrow}>Chat history</strong>
                <div className={styles.wilsyConversationSelectShell}>
                  <span className={styles.wilsyConversationSelectLabel}>Conversation</span>
                  <select
                    aria-label="Select previous Wilsy AI chat"
                    value={wilsyActiveConversationId}
                    onChange={handleWilsySelectConversationThread}
                  >
                    <option value="">Select previous chat</option>
                    {wilsyConversationThreads.map((thread) => (
                      <option key={thread.id} value={thread.id}>
                        {thread.title || `${thread.workspace || 'Workspace'} · Saved chat`}
                      </option>
                    ))}
                  </select>
                </div>
              </label>
              <button
                type="button"
                className={styles.wilsyConversationClearHistoryButton}
                onClick={handleWilsyClearConversationHistory}
                disabled={wilsyConversationThreads.length === 0}
              >
                Clear history
              </button>
            </div>

            <form className={styles.askBar} onSubmit={handleWilsyAskSubmit}>
              <input
                type="text"
                value={operatorPrompt}
                onChange={(event) => setOperatorPrompt(event.target.value)}
                placeholder={`Ask Wilsy about ${context.workspace || 'this workspace'}...`}
                aria-label="Ask Wilsy"
              />
              <button type="submit">{operatorBackendBusy ? 'Checking' : 'Ask'}</button>
            </form>

                        {/* WILSY_P60K5Q10BR_ANSWER_FIRST_LAYOUT */}
<div className={`${styles.answerWorkspace} ${!wilsyHasSubmittedOperatorResult || activeDocumentReview ? styles.operatingStateHidden : ''}`} data-wilsy-raw-terminal-thread="true" data-wilsy-sovereign-ai-composer="competition-core" data-wilsy-composer-printing={operatorBackendBusy || wilsyInlineComposerStream.active ? 'true' : 'false'} data-wilsy-composer-empty={!operatorBackendBusy && !wilsyInlineComposerStream.active && !wilsyInlineComposerStream.text ? 'true' : 'false'} data-wilsy-composer-complete={!operatorBackendBusy && !wilsyInlineComposerStream.active && Boolean(wilsyInlineComposerStream.text) ? 'true' : 'false'} data-wilsy-response-slot-owner="true" hidden={!operatorBackendBusy && !wilsyInlineComposerStream.active && !wilsyInlineComposerStream.text}>
              <span className={styles.singleSurfaceHiddenLabel} aria-hidden="true">WILSY_ANSWER_STREAM</span>
              <strong className={styles.singleSurfaceHiddenTitle} aria-hidden="true">
                {operatorBackendBusy ? 'Checking live Wilsy sources' : getWilsyDisplayTitle(liveOperatorModel)}
              </strong>
              <p
                className={`${styles.liveInlineComposerText} ${styles.singleSurfaceNaturalBody}`}
                data-wilsy-live-inline-composer-stream="active"
                data-wilsy-single-surface-output="true"
              >
                {operatorBackendBusy
                  ? 'I am checking connected CRM sources and evidence before answering.'
                  : wilsyInlineComposerStream.text}
                {!operatorBackendBusy &&
                !wilsyInlineComposerStream.active &&
                wilsyHasSubmittedOperatorResult &&
                wilsyInlineComposerStream.tokens.length > 0 ? (
                  <span className={styles.singleSurfaceInlineRoutes} data-wilsy-inline-links-in-prose="true">
                    {' '}
                    Next, open{' '}
                    {wilsyInlineComposerStream.tokens.slice(0, 5).map((token, index) => (
                      <React.Fragment key={token.token || token.id || token.label || index}>
                        <button
                          type="button"
                          onClick={() =>
                            handleWilsyQuickPrompt({
                              id: token.intent || token.id || resolveWilsyOperatorIntent(token.prompt || token.label || token.title, activePrompt),
                              intent: token.intent || token.id || resolveWilsyOperatorIntent(token.prompt || token.label || token.title, activePrompt),
                              label: token.label || token.buttonLabel || token.title || token.prompt,
                              prompt: token.prompt || token.label || token.title,
                              description: token.telemetry || token.description || token.token,
                            })
                          }
                        >
                          {token.label || token.buttonLabel || token.title || token.prompt}
                        </button>
                        {index < Math.min(wilsyInlineComposerStream.tokens.length, 5) - 1 ? <span>, </span> : <span>.</span>}
                      </React.Fragment>
                    ))}
                  </span>
                ) : null}
                {!operatorBackendBusy && wilsyInlineComposerStream.active ? (
                  <span className={styles.liveInlineComposerCursor}>▍</span>
                ) : null}
              </p>
              <small className={styles.singleSurfaceHiddenStatus} aria-hidden="true">
                {getWilsyDisplayOutcome(liveOperatorModel)}
              </small>
              {!operatorBackendBusy && wilsyHasSubmittedOperatorResult && wilsyInlineComposerStream.tokens.length > 0 ? (
                <div className={styles.liveInlineCommandShelf} data-wilsy-inline-command-links="active">
                  <span>routes://</span>
                  <div>
                    {wilsyInlineComposerStream.tokens.map((token, index) => (
                      <button
                        key={token.token || token.id || token.label || index}
                        type="button"
                        className={styles.liveInlineCommandLink}
                        onClick={() =>
                          handleWilsyQuickPrompt({
                            id: token.intent || token.id || resolveWilsyOperatorIntent(token.prompt || token.label || token.title, activePrompt),
                            intent: token.intent || token.id || resolveWilsyOperatorIntent(token.prompt || token.label || token.title, activePrompt),
                            label: token.label || token.buttonLabel || token.title || token.prompt,
                            prompt: token.prompt || token.label || token.title,
                            description: token.telemetry || token.description || token.token,
                          })
                        }
                      >
                        <strong>[{token.label || token.buttonLabel || token.title || token.prompt}]</strong>
                        <code>{token.token || `wilsy://inline/${String(index + 1).padStart(2, '0')}`}</code>
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}
              {liveOperatorModel.missionState ? (
                <div className={styles.missionStatePanel} data-wilsy-mission-state="active" data-wilsy-mission-focus-lock="true">
                  <div className={styles.missionStateHeader}>
                    <span>ACTIVE MISSION</span>
                    <strong>{liveOperatorModel.missionState.objective}</strong>
                  </div>
                  <div className={styles.missionStateGrid}>
                    {(liveOperatorModel.missionGates || liveOperatorModel.missionState.gates || []).slice(0, 4).map((gate, index) => (
                      <span key={`${gate}-${index}`}>{gate}</span>
                    ))}
                  </div>
                  {liveOperatorModel.executionCanvas ? (
                    <div className={styles.executionCanvasStream} data-wilsy-execution-canvas-stream="active">
                      <div className={styles.executionCanvasHeader}>
                        <span>SOVEREIGN STREAM</span>
                        <strong>{liveOperatorModel.executionCanvas.summary}</strong>
                      </div>
                      <div className={styles.executionTelemetryGrid}>
                        {(liveOperatorModel.telemetryPacks || liveOperatorModel.executionCanvas.telemetry || []).slice(0, 4).map((item, index) => (
                          <span key={`${item.label || item.value}-${index}`}>
                            <strong>{item.label}</strong>
                            <small>{item.value}</small>
                          </span>
                        ))}
                      </div>
                      {liveOperatorModel.sourceRouteJudge ? (
                        <div className={styles.sourceRouteJudge}>
                          <span>SOURCE ROUTE JUDGE</span>
                          <strong>{liveOperatorModel.sourceRouteJudge.status}</strong>
                          <small>{liveOperatorModel.sourceRouteJudge.decision}</small>
                        </div>
                      ) : null}
                    </div>
                  ) : null}
                  {(liveOperatorModel.missionNextMoves || liveOperatorModel.missionState.nextMoves || []).length > 0 ? (
                    <div className={styles.missionCommandBoard} data-wilsy-mission-command-board="active">
                      <div className={styles.missionCommandHeader}>
                        <span>EXECUTION THREAD</span>
                        <strong>Sovereign route cockpit</strong>
                      </div>
                      <div className={styles.missionMoveGrid}>
                        {(liveOperatorModel.missionNextMoves || liveOperatorModel.missionState.nextMoves || []).slice(0, 8).map((move, index) => (
                          <button
                            key={`${move}-${index}`}
                            type="button"
                            className={styles.missionMoveButton}
                            onClick={() =>
                              handleWilsyQuickPrompt({
                                id: resolveWilsyOperatorIntent(move, activePrompt),
                                intent: resolveWilsyOperatorIntent(move, activePrompt),
                                label: move,
                                prompt: move,
                                description: `Mission next move: ${move}`,
                              })
                            }
                          >
                            <span>{String(index + 1).padStart(2, '0')}</span>
                            <strong>{move}</strong>
                            <small>{(liveOperatorModel.commandTokens || [])[index]?.token || 'wilsy://governed/read-only-step'}</small>
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </div>
              ) : null}
              {operatorBackendBusy ? <em className={styles.operatorProgress}>Live source search in progress...</em> : null}
              {operatorBackendError ? <em className={styles.operatorError}>{operatorBackendError}</em> : null}
              {/* WILSY_P60K5Q10AY_FOUNDRY_SINGLE_CARD */}
              {(() => {
                const capabilityItem = buildWilsyCapabilityReviewItem(liveOperatorModel);

                return capabilityItem ? (
                  <div className={styles.capabilityReviewCard}>
                    <div className={styles.capabilityReviewHeader} data-wilsy-legacy-foundry-surface="true" data-wilsy-legacy-foundry-review="true" hidden={wilsyHasSubmittedOperatorResult}>
                      <span>CAPABILITY FOUNDRY</span>
                      <strong>REVIEW REQUIRED</strong>
                    </div>

                    <div className={styles.capabilityReviewGrid}>
                      <span>
                        <small>Capability</small>
                        <strong>{capabilityItem.businessName}</strong>
                      </span>
                      <span>
                        <small>Candidate</small>
                        <strong>{capabilityItem.candidateId}</strong>
                      </span>
                      <span>
                        <small>Status</small>
                        <strong>{String(capabilityItem.status || '').replaceAll('_', ' ')}</strong>
                      </span>
                      <span>
                        <small>Approval</small>
                        <strong>{capabilityItem.approvalRequired ? 'Required before publishing' : 'Not required'}</strong>
                      </span>
                    </div>

                    {/* WILSY_P60K5Q10AZ_FOUNDRY_DECISION_STRIP */}
                    <div className={styles.capabilityReviewDecision}>
                      <small>Next decision</small>
                      <strong>{capabilityItem.nextDecision}</strong>
                    </div>

                    <div className={styles.capabilityReviewActions}>
                      <button
                        type="button"
                        onClick={() => {
                          if (typeof navigator !== 'undefined' && navigator.clipboard) {
                            navigator.clipboard.writeText(capabilityItem.planText);
                          }
                        }}
                      >
                        Copy foundry plan
                      </button>
                    </div>
                  </div>
                ) : null;
              })()}



              {Array.isArray(liveOperatorModel.sourceTrace) && liveOperatorModel.sourceTrace.length > 0 ? (
                <div className={styles.sourceTrace}>
                  {liveOperatorModel.sourceTrace.map((trace) => (
                    <span key={`${trace.tool}-${trace.domain || 'none'}-${trace.status}`}>
                      Checked: {trace.label || 'Operator source'} · {trace.statusLabel || 'Completed'}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>

            {/* WILSY_P60K5Q10AU_PREPARED_WORK_RENDER */}
            {(() => {
              const preparedItem = buildWilsyPreparedOperatorItem(liveOperatorModel);

              return preparedItem ? (
                <div className={`${styles.preparedWorkCard} ${!wilsyHasSubmittedOperatorResult || activeDocumentReview ? styles.operatingStateHidden : ''}`}>
                  <div className={styles.preparedWorkHeader}>
                    <span>PREPARED WORK</span>
                    <strong>{preparedItem.status}</strong>
                  </div>

                  <div className={styles.preparedWorkGrid}>
                    {preparedItem.fields.map((field) => (
                      <span key={`${field.label}-${field.value}`}>
                        <small>{field.label}</small>
                        <strong>{field.value}</strong>
                      </span>
                    ))}
                  </div>

                  <div className={styles.preparedWorkActions}>
                    {preparedItem.link ? (
                      <button
                        type="button"
                        data-wilsy-document-review-action="open-lab"
                        onClick={(event) => {
                          event.preventDefault();
                          event.stopPropagation();

                          const preparedFieldMap = Array.isArray(preparedItem.fields)
                            ? preparedItem.fields.reduce((accumulator, field) => {
                                accumulator[String(field.label || '').toLowerCase()] = field.value;
                                return accumulator;
                              }, {})
                            : {};

                          const reviewLabItem = {
                            ...preparedItem,
                            documentPreview:
                              preparedItem.documentPreview ||
                              liveOperatorModel?.documentPreview ||
                              {
                                previewVersion: 'P60K5Q10DA_EXACT_REVIEW_DRAFT_LAB',
                                brand: {
                                  tenantName: liveOperatorModel?.tenantName || 'Wilsy OS Tenant',
                                  seal: 'Wilsy OS',
                                },
                                document: {
                                  title: preparedFieldMap.title || preparedItem.title || 'Document draft',
                                  documentType:
                                    preparedFieldMap['document type'] ||
                                    preparedItem.documentType ||
                                    'Business document',
                                  status: preparedItem.status || 'Draft prepared',
                                  purpose:
                                    preparedFieldMap.purpose ||
                                    preparedItem.purpose ||
                                    'Prepared for governed review.',
                                  sections: [
                                    {
                                      sectionId: 'source-and-branding',
                                      heading: 'Source and tenant branding',
                                      body: 'Wilsy keeps this review inside the AI lab so the operator can verify tenant source, brand posture, and document purpose before execution.',
                                    },
                                    {
                                      sectionId: 'approval-workflow',
                                      heading: 'Approval workflow',
                                      body: 'Send for approval is the next governed action. Mutation remains locked until approval is complete.',
                                    },
                                    {
                                      sectionId: 'delivery-readiness',
                                      heading: 'Delivery readiness',
                                      body: 'Recipient details, delivery connector binding, and approval must be complete before package or send can unlock.',
                                    },
                                  ],
                                },
                              },
                            planText:
                              preparedItem.planText ||
                              (Array.isArray(liveOperatorModel?.commandPlan) ? liveOperatorModel.commandPlan.join('\\n') : '') ||
                              'Review draft\\nConfirm tenant branding\\nSend for approval\\nApprove governed command\\nPackage receipt',
                            labState: {
                              reviewOpen: true,
                              mutation: false,
                              sendLocked: true,
                              sourceChecked: true,
                              approvalStatus: 'Approval required',
                              deliveryStatus: 'Recipient and connector required',
                            },
                          };

                          setActiveDocumentReview(reviewLabItem);

                          if (typeof window !== 'undefined' && typeof document !== 'undefined') {
                            window.requestAnimationFrame(() => {
                              document
                                .querySelector('[data-wilsy-document-lab="active"]')
                                ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            });

                            window.setTimeout(() => {
                              document
                                .querySelector('[data-wilsy-document-lab="active"]')
                                ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            }, 160);
                          }
                        }}
                      >
                        {preparedItem.linkLabel || 'Review Draft'}
                      </button>
                    ) : null}
                    <button
                      type="button"
                      onClick={() => {
                        if (typeof navigator !== 'undefined' && navigator.clipboard) {
                          navigator.clipboard.writeText(preparedItem.planText);
                        }
                      }}
                    >
                      Copy approval plan
                    </button>
                  </div>
                </div>
              ) : null;
            })()}

            {/* WILSY_P60K5Q10BE_DOCUMENT_PREVIEW_PANEL */}
            {activeDocumentReview ? (
<section className={styles.documentPreviewPanel} data-wilsy-document-lab="active" aria-label="Tenant-branded document review">
                <div className={styles.documentPreviewHeader}>
                  <span>TENANT DOCUMENT REVIEW</span>
                  <strong>{activeDocumentReviewPreview?.document?.title || activeDocumentReview.fields?.[0]?.value || 'Document draft'}</strong>
                  <button type="button" onClick={() => setActiveDocumentReview(null)}>
                    Close review
                  </button>
                </div>

                  {/* WILSY_P60K5Q10DD_TASK_FIRST_CONTROL_DECK */}
                  <div className={styles.documentTaskControlDeck} aria-label="Document task control deck">
                    <div className={styles.documentTaskNextAction}>
                      <span>NEXT TASK</span>
                      <strong>Complete approval readiness</strong>
                      <small>Recipient, connector, and authorized approval must unlock before package or send.</small>
                    </div>

                    <div className={styles.documentTaskGateMatrix} aria-label="Document execution gates">
                      <span data-gate-state="checked">Source checked</span>
                      <span data-gate-state="blocked">Recipient missing</span>
                      <span data-gate-state="blocked">Connector missing</span>
                      <span data-gate-state="blocked">Approval required</span>
                    </div>

                    <div className={styles.documentTaskActions}>
                      <button type="button" disabled title="Recipient and connector are required first.">
                        Send for approval
                      </button>
                      <button type="button" disabled title="Approval readiness is required before packaging.">
                        Package
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          if (typeof navigator !== 'undefined' && navigator.clipboard) {
                            navigator.clipboard.writeText(activeDocumentReview.planText || '');
                          }
                        }}
                      >
                        Copy plan
                      </button>
                    </div>
                  </div>


                
                  {/* WILSY_P60K5Q10DE_ACTUAL_DOCUMENT_CANVAS */}
                  {(() => {
                    const documentModel = activeDocumentReviewPreview?.document || {};
                    const documentTitle =
                      documentModel.title ||
                      activeDocumentReview?.fields?.find((field) => field.label === 'Title')?.value ||
                      activeDocumentReview?.title ||
                      'Document draft';
                    const documentType =
                      documentModel.documentType ||
                      activeDocumentReview?.fields?.find((field) => field.label === 'Document type')?.value ||
                      activeDocumentReview?.documentType ||
                      'Business document';
                    const documentPurpose =
                      documentModel.purpose ||
                      activeDocumentReview?.fields?.find((field) => field.label === 'Purpose')?.value ||
                      activeDocumentReview?.purpose ||
                      'Prepared for governed review.';
                    const sourceSections = Array.isArray(documentModel.sections) ? documentModel.sections : [];
                    const presentationSectionPattern = /source and tenant branding|approval workflow|delivery readiness|execution readiness/i;
                    const hasActualDraftBody = sourceSections.some(
                      (section) =>
                        !presentationSectionPattern.test(String(section.heading || section.title || section.sectionId || '')),
                    );
                    const draftBodySections = hasActualDraftBody
                      ? sourceSections
                      : [
                          {
                            sectionId: 'opening-brief',
                            heading: '1. Operating brief',
                            body: `${documentTitle} is prepared for review under Wilsy OS governance. The purpose of this draft is: ${documentPurpose}`,
                          },
                          {
                            sectionId: 'scope-of-document',
                            heading: '2. Scope',
                            body: `This ${documentType} records the proposed business intent, review requirements, approval posture, and delivery controls required before execution.`,
                          },
                          {
                            sectionId: 'review-obligations',
                            heading: '3. Review obligations',
                            body: 'The operator must verify the content, tenant branding, source posture, recipient readiness, delivery connector, and approval path before any send command can unlock.',
                          },
                          {
                            sectionId: 'execution-control',
                            heading: '4. Execution control',
                            body: 'No delivery mutation has been taken. Packaging and sending remain locked until recipient details, connector binding, and authorized approval are complete.',
                          },
                        ];

                    return (
                      <section className={styles.documentActualCanvas} aria-label="Actual document draft canvas">
                        <div className={styles.documentCanvasGameHud} aria-label="Draft progress">
                          <span data-stage-state="complete">Draft visible</span>
                          <span data-stage-state="active">Review now</span>
                          <span data-stage-state="locked">Approval locked</span>
                          <span data-stage-state="locked">Send locked</span>
                        </div>

                        <article className={styles.documentPageSurface}>
                          <header className={styles.documentPageMasthead}>
                            <span>{activeDocumentReviewPreview?.brand?.tenantName || 'Wilsy OS Tenant'}</span>
                            <strong>{documentTitle}</strong>
                            <small>{documentType} · {documentModel.status || activeDocumentReview?.status || 'Draft prepared'}</small>
                          </header>

                          <section className={styles.documentPagePurpose}>
                            <span>Purpose</span>
                            <p>{documentPurpose}</p>
                          </section>

                          <div className={styles.documentDraftBody}>
                            {draftBodySections.map((section, sectionIndex) => (
                              <section
                                key={section.sectionId || section.heading || section.title || `draft-section-${sectionIndex}`}
                                className={styles.documentDraftClause}
                              >
                                <span>{String(section.sectionId || `clause-${sectionIndex + 1}`).replace(/[-_]/g, ' ')}</span>
                                <strong>{section.heading || section.title || `Section ${sectionIndex + 1}`}</strong>
                                <p>{section.body || section.content || 'Draft content pending review.'}</p>
                              </section>
                            ))}
                          </div>

                          <footer className={styles.documentPageSignatureRail}>
                            <div>
                              <span>Prepared by</span>
                              <strong>Wilsy OS AI</strong>
                            </div>
                            <div>
                              <span>Mutation</span>
                              <strong>Locked</strong>
                            </div>
                            <div>
                              <span>Next move</span>
                              <strong>Review content</strong>
                            </div>
                          </footer>
                        </article>
                      </section>
                    );
                  })()}

{/* WILSY_P60K5Q10DD_EVIDENCE_DETAILS */}
                  <details className={styles.documentTaskEvidenceDetails}>
                    <summary>Evidence, source, and delivery constraints</summary>
                    <div className={styles.documentPreviewBrand}>
                  <span>{activeDocumentReviewPreview?.brand?.tenantName || 'Wilsy OS Tenant'}</span>
                  <strong>{activeDocumentReviewPreview?.document?.status || 'Draft ready for review'}</strong>
                </div>

                <div className={styles.documentPreviewSections}>
                  {(activeDocumentReviewPreview?.document?.sections || []).map((section) => (
                    <article key={section.sectionId}>
                      <h4>{section.heading}</h4>
                      <p>{section.body}</p>
                    </article>
                  ))}
                </div>
                  </details>

<div className={styles.documentPreviewFooter}>
                    <span>LOCKED: recipient missing · connector missing · approval required</span>
                  </div>
              </section>
            ) : null}

            {wilsyHasSubmittedOperatorResult && !liveOperatorModel.missionState && !activeDocumentReview && (liveOperatorModel.playableActions || liveOperatorModel.actions || []).length > 0 ? (
              <div className={styles.playableActionDeck} data-wilsy-visible-playable-action-rail="true" data-wilsy-rail-demand-gated="true">
                <div className={styles.playableActionHeader}>
                  <span>EXECUTION PIPELINE</span>
                  <strong>Route work through the cockpit</strong>
                </div>
                <div className={styles.playableActionGrid}>
                  {(liveOperatorModel.playableActions || liveOperatorModel.actions || []).slice(0, 4).map((action, index) => (
                    <button
                      key={action.id || action.title || index}
                      type="button"
                      className={styles.playableActionButton}
                      onClick={() =>
                        handleWilsyQuickPrompt({
                          id: action.intent || resolveWilsyOperatorIntent(action.prompt || action.title, activePrompt),
                          intent: action.intent || resolveWilsyOperatorIntent(action.prompt || action.title, activePrompt),
                          label: action.buttonLabel || action.title,
                          prompt: action.prompt || action.title,
                          description: action.description,
                        })
                      }
                    >
                      <span>{action.buttonLabel || action.title}</span>
                      <small>{action.nextState || action.lockedReason || action.description || 'Read-only governed move'}</small>
                    </button>
                  ))}
                </div>
              </div>
            ) : null}

            <div className={`${styles.promptGrid} ${wilsyHasSubmittedOperatorResult || activeDocumentReview ? styles.operatingStateHidden : ''} `} aria-label="Wilsy quick prompts">
              {dynamicWilsyQuickPrompts.map((prompt) => (
                <button
                  key={prompt.id}
                  type="button"
                  data-wilsy-directive-autosubmit="true"
                  className={activePrompt === prompt.id ? styles.activePrompt : ''}
                  onClick={() => handleWilsyQuickPrompt(prompt)}
                >
                  {prompt.label}
                </button>
              ))}
            </div>
          </section>

          <section className={`${styles.actionBoard} ${styles.operatingStateHidden} `} data-wilsy-legacy-execution-pipeline="true">
            <div className={styles.sectionHeader}>
              <span>EXECUTION PIPELINE</span>
              <strong>Route work through the cockpit</strong>
            </div>
            <div className={styles.actionList}>
              {liveOperatorModel.actions.map((action) => (
                <button
                  key={`${action.rank}-${action.title}`}
                  type="button"
                  onClick={() =>
                    handleWilsyQuickPrompt({
                      id: action.rank === 1 ? 'authority_graph' : action.rank === 2 ? 'evidence_checklist' : 'queue_hygiene',
                      label: action.buttonLabel || action.title,
                        prompt: action.prompt || action.title,
                        intent: action.intent,
                    })
                  }
                >
                  <span>{String(action.mode || 'read_only').replace(/_/g, ' ')}</span>
                  <strong>{action.title}</strong>
                  <p>{action.description}</p>
                </button>
              ))}
            </div>
          </section>

          <section className={`${styles.commandPrep} ${styles.operatingStateHidden} `} data-wilsy-hardcoded-command-prep="true">
            <div className={styles.sectionHeader} data-wilsy-hardcoded-command-prep="true" hidden={wilsyHasSubmittedOperatorResult}>
              <span>GOVERNED COMMAND PREP</span>
              <strong>Ready for operator review</strong>
            </div>
            <ol>
              {liveOperatorModel.checklist.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ol>
            <p>No workspace data changes here. Wilsy prepares the work; execution still requires an approved command.</p>
          </section>

          <details className={styles.modelDetails}>
            <summary>Model coverage</summary>
            <div>
              <span>Workspace: {context.workspace}</span>
              <span>Role: {context.role}</span>
              <span>Focus: {context.focus}</span>
              <span>Status: {status === 'SOVEREIGN_CONTEXT' ? 'Live context connected' : 'Local context only'}</span>
            </div>
          </details>
        </div>
      </section>

      
    </aside>
  );
}

/**
 * @function mountWilsyOSIntelligenceDock
 * @description Mounts the global Wilsy OS Intelligence dock once at app runtime.
 * @returns {HTMLElement|null} Dock host element when mounted.
 * @collaboration React root runtime, all Wilsy OS workspaces, global intelligence sidecar, and future billing-tier intelligence services.
 */
export function mountWilsyOSIntelligenceDock() {
  if (typeof document === 'undefined') {
    return null;
  }

  let host = document.getElementById(WILSY_INTELLIGENCE_ROOT_ID);

  if (!host) {
    host = document.createElement('div');
    host.id = WILSY_INTELLIGENCE_ROOT_ID;
    document.body.appendChild(host);
  }

  if (host.dataset.wilsyMounted === 'true') {
    return host;
  }

  const root = createRoot(host);
  root.render(<WilsyOSIntelligenceDock />);
  host.dataset.wilsyMounted = 'true';
  window.__WILSY_OS_INTELLIGENCE_DOCK_ROOT__ = root;

  return host;
}

export default WilsyOSIntelligenceDock;
