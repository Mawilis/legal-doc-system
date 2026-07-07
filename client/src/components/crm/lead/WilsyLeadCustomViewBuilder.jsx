/* eslint-disable */
import React, { useMemo, useState } from 'react';
import { CheckCircle2, Eye, Save, SlidersHorizontal, X } from 'lucide-react';
import styles from './WilsyLeadOperatingRoom.module.css';

const WILSY_CUSTOM_VIEW_FIELDS = Object.freeze([
  { id: 'status', label: 'Status' },
  { id: 'stage', label: 'Stage' },
  { id: 'owner', label: 'Owner' },
  { id: 'company', label: 'Company' },
  { id: 'source', label: 'Source' },
  { id: 'priority', label: 'Priority' },
  { id: 'score', label: 'Minimum score' },
  { id: 'value', label: 'Minimum value' },
]);

/**
 * @function normalizeWilsyLeadCustomViewText
 * @description Normalizes values used by the Lead custom view builder and matcher.
 * @param {*} value - Candidate value.
 * @returns {string} Normalized text.
 * @collaboration Custom View Builder, live Lead records, saved view criteria, and Organizer filtering.
 */
export function normalizeWilsyLeadCustomViewText(value = '') {
  return String(value ?? '').replace(/\s+/g, ' ').trim();
}

/**
 * @function resolveWilsyLeadCustomViewFieldValue
 * @description Resolves a field value from a Lead record or its source payload.
 * @param {Object} record - Lead record.
 * @param {string} field - Criteria field id.
 * @returns {string|number} Resolved field value.
 * @collaboration Custom View Builder, backend Lead row aliases, source payload aliases, and saved view filtering.
 */
export function resolveWilsyLeadCustomViewFieldValue(record = {}, field = '') {
  const sourcePayload = record && typeof record.sourcePayload === 'object' && record.sourcePayload ? record.sourcePayload : {};
  const fieldId = normalizeWilsyLeadCustomViewText(field).toLowerCase();

  if (fieldId === 'owner') {
    return normalizeWilsyLeadCustomViewText(record.ownerName || record.ownerDisplayName || record.owner || record.assignedToName || sourcePayload.ownerName || sourcePayload.owner);
  }

  if (fieldId === 'company') {
    return normalizeWilsyLeadCustomViewText(record.companyName || record.company || record.accountName || sourcePayload.companyName || sourcePayload.company);
  }

  if (fieldId === 'source') {
    return normalizeWilsyLeadCustomViewText(record.source || record.leadSource || record.origin || sourcePayload.source || sourcePayload.leadSource);
  }

  if (fieldId === 'priority') {
    return normalizeWilsyLeadCustomViewText(record.priority || record.leadPriority || record.urgency || sourcePayload.priority || sourcePayload.leadPriority);
  }

  if (fieldId === 'score') {
    return Number(record.score || record.leadScore || record.priorityScore || record.sourceCompletenessScore || sourcePayload.score || sourcePayload.leadScore || 0);
  }

  if (fieldId === 'value') {
    return Number(String(record.value || record.dealValue || record.estimatedValue || record.pipelineValue || sourcePayload.value || sourcePayload.dealValue || 0).replace(/[^0-9.-]/g, ''));
  }

  if (fieldId === 'stage') {
    return normalizeWilsyLeadCustomViewText(record.stage || record.pipelineStage || sourcePayload.stage);
  }

  return normalizeWilsyLeadCustomViewText(record.status || record.leadStatus || sourcePayload.status);
}

/**
 * @function doesWilsyLeadMatchCustomViewCriteria
 * @description Checks whether a Lead record matches custom saved view criteria.
 * @param {Object} record - Lead record.
 * @param {Object} criteria - Saved view criteria.
 * @returns {boolean} Whether the record matches.
 * @collaboration Custom View Builder, Organizer saved views, live backend Lead rows, and Records grid filtering.
 */
export function doesWilsyLeadMatchCustomViewCriteria(record = {}, criteria = {}) {
  const field = normalizeWilsyLeadCustomViewText(criteria.field || 'status').toLowerCase();
  const operator = normalizeWilsyLeadCustomViewText(criteria.operator || 'contains').toLowerCase();
  const expected = normalizeWilsyLeadCustomViewText(criteria.value);
  const resolved = resolveWilsyLeadCustomViewFieldValue(record, field);

  if (field === 'score' || field === 'value') {
    const numericResolved = Number(resolved || 0);
    const numericExpected = Number(String(expected || '0').replace(/[^0-9.-]/g, ''));

    if (operator === 'less_than') {
      return numericResolved < numericExpected;
    }

    if (operator === 'equals') {
      return numericResolved === numericExpected;
    }

    return numericResolved >= numericExpected;
  }

  const resolvedText = normalizeWilsyLeadCustomViewText(resolved).toLowerCase();
  const expectedText = expected.toLowerCase();

  if (!expectedText) {
    return Boolean(resolvedText);
  }

  if (operator === 'equals') {
    return resolvedText === expectedText;
  }

  if (operator === 'starts_with') {
    return resolvedText.startsWith(expectedText);
  }

  if (operator === 'not_contains') {
    return !resolvedText.includes(expectedText);
  }

  return resolvedText.includes(expectedText);
}

/**
 * @function buildWilsyLeadCustomViewPayload
 * @description Builds a persisted custom Lead view payload from builder draft state.
 * @param {Object} draft - Builder draft state.
 * @param {number} previewCount - Matching preview count.
 * @returns {Object} Persistable custom view payload.
 * @collaboration Custom View Builder, local saved views, Organizer live models, and source-backed CRM filtering.
 */
export function buildWilsyLeadCustomViewPayload(draft = {}, previewCount = 0) {
  const label = normalizeWilsyLeadCustomViewText(draft.label) || 'Custom Lead View';
  const idSeed = `${label}-${draft.field}-${draft.operator}-${draft.value}`.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

  return {
    id: `CUSTOM_${idSeed || Date.now()}`,
    label,
    detail: `${previewCount} live`,
    staticDetail: normalizeWilsyLeadCustomViewText(draft.description) || 'Saved custom criteria',
    custom: true,
    createdByUser: true,
    liveBackendConnected: true,
    compactOrganizer: true,
    criteria: {
      field: draft.field || 'status',
      operator: draft.operator || 'contains',
      value: normalizeWilsyLeadCustomViewText(draft.value),
    },
    visibility: draft.visibility || 'private',
    generatedAt: new Date().toISOString(),
  };
}

/**
 * @function WilsyLeadCustomViewBuilder
 * @description Renders the production Lead custom view builder instead of routing custom-view creation into unrelated command centers.
 * @param {Object} props - Component props.
 * @returns {JSX.Element|null} Custom view builder overlay.
 * @collaboration Leads Organizer, live backend records, saved custom views, Records grid, and Wilsy OS CRM productivity workflow.
 */
export default function WilsyLeadCustomViewBuilder({
  isOpen = false,
  onClose = () => {},
  onSave = () => {},
  liveLeads = [],
  existingViews = [],
}) {
  const [draft, setDraft] = useState({
    label: 'Wilson Owned Leads',
    description: 'Live backend Leads assigned to Wilson',
    field: 'owner',
    operator: 'contains',
    value: 'Wilson',
    visibility: 'private',
  });

  const previewRows = useMemo(() => (
    Array.isArray(liveLeads)
      ? liveLeads.filter(record => doesWilsyLeadMatchCustomViewCriteria(record, draft))
      : []
  ), [draft, liveLeads]);

  /**
   * @function updateDraft
   * @description Updates a Custom View Builder draft field.
   * @param {string} field - Draft field.
   * @param {*} value - Draft value.
   * @returns {void}
   * @collaboration Custom View Builder form state, live preview, saved Lead views, and Records filtering.
   */
  const updateDraft = (field, value) => {
    setDraft(previous => ({
      ...previous,
      [field]: value,
    }));
  };

  /**
   * @function saveView
   * @description Saves the current Custom View Builder draft.
   * @returns {void}
   * @collaboration Saved custom views, Organizer list, local persistence, and live backend row filtering.
   */
  const saveView = () => {
    onSave(buildWilsyLeadCustomViewPayload(draft, previewRows.length));
  };

  if (!isOpen) {
    return null;
  }

  return (
    <section className={styles.leadCustomViewOverlay} data-wilsy-lead-custom-view-builder="true">
      <article className={styles.leadCustomViewPanel}>
        <header className={styles.leadCustomViewHeader}>
          <div>
            <span><SlidersHorizontal size={16} /> Lead Custom View</span>
            <strong>Build a live saved view</strong>
            <em>Criteria-driven views filter current backend Lead records immediately.</em>
          </div>
          <div className={styles.leadCustomViewHeaderActions} data-wilsy-lead-custom-view-header-actions="P60K5Q10FG100E_HEADER_SAVE_ACTION">
            <button type="button" onClick={saveView} className={styles.leadCustomViewHeaderSave}>
              <Save size={16} />
              Save view
            </button>
            <button type="button" onClick={onClose} aria-label="Close custom view builder">
              <X size={18} />
            </button>
          </div>
        </header>

        <div className={styles.leadCustomViewGrid}>
          <label>
            <span>View name</span>
            <input value={draft.label} onChange={event => updateDraft('label', event.target.value)} />
          </label>

          <label>
            <span>Description</span>
            <input value={draft.description} onChange={event => updateDraft('description', event.target.value)} />
          </label>

          <label>
            <span>Field</span>
            <select value={draft.field} onChange={event => updateDraft('field', event.target.value)}>
              {WILSY_CUSTOM_VIEW_FIELDS.map(field => (
                <option key={field.id} value={field.id}>{field.label}</option>
              ))}
            </select>
          </label>

          <label>
            <span>Operator</span>
            <select value={draft.operator} onChange={event => updateDraft('operator', event.target.value)}>
              <option value="contains">Contains</option>
              <option value="equals">Equals</option>
              <option value="starts_with">Starts with</option>
              <option value="not_contains">Does not contain</option>
              <option value="greater_than">Greater than / equal</option>
              <option value="less_than">Less than</option>
            </select>
          </label>

          <label>
            <span>Value</span>
            <input value={draft.value} onChange={event => updateDraft('value', event.target.value)} />
          </label>

          <label>
            <span>Visibility</span>
            <select value={draft.visibility} onChange={event => updateDraft('visibility', event.target.value)}>
              <option value="private">Private</option>
              <option value="team">Team</option>
              <option value="tenant">Tenant</option>
            </select>
          </label>
        </div>

        <section className={styles.leadCustomViewPreview}>
          <strong><Eye size={16} /> Live preview</strong>
          <span>{previewRows.length}/{Array.isArray(liveLeads) ? liveLeads.length : 0} backend rows match</span>
          <em>{existingViews.length} saved custom views available in this workspace.</em>
        </section>

        <footer className={styles.leadCustomViewActions}>
          <button type="button" onClick={onClose}>Cancel</button>
          <button type="button" onClick={saveView}>
            <Save size={16} />
            Save custom view
          </button>
          <span><CheckCircle2 size={14} /> Live criteria ready</span>
        </footer>
      </article>
    </section>
  );
}
