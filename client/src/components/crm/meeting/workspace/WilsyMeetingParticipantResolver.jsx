/* eslint-disable */
import React, { useEffect, useMemo, useState } from 'react';
import { CheckSquare, Search, Square, UserPlus, Users, X } from 'lucide-react';
import styles from './WilsyMeetingsWorkspace.module.css';

/**
 * @function normalizeWilsyR91K179E23P1WEmail
 * @description Normalizes email identity for duplicate-safe participant resolution.
 * @param {string} value - Email value.
 * @returns {string} Normalized email.
 * @collaboration Participant resolver, duplicate guard, meeting draft.
 */
function normalizeWilsyR91K179E23P1WEmail(value = '') {
  return String(value || '').trim().toLowerCase();
}

/**
 * @function isWilsyR91K179E23P1WEmail
 * @description Validates a practical external invite email value.
 * @param {string} value - Candidate email.
 * @returns {boolean} Email validity.
 * @collaboration External invite tab, duplicate guard, selected tray.
 */
function isWilsyR91K179E23P1WEmail(value = '') {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value || '').trim());
}

/**
 * @function resolveWilsyR91K179E23P1WRecordId
 * @description Resolves a CRM source record id from supported source fields.
 * @param {Object} record - CRM source record.
 * @returns {string} Source record id.
 * @collaboration Live leads route, live contacts route, source rows.
 */
function resolveWilsyR91K179E23P1WRecordId(record = {}) {
  return String(record._id || record.id || record.recordId || record.leadId || record.contactId || record.userId || '').trim();
}

/**
 * @function resolveWilsyR91K179E23P1WName
 * @description Resolves a readable participant name from CRM/operator records.
 * @param {Object} record - Source record.
 * @returns {string} Display name.
 * @collaboration Resolver rows, selected tray, meeting editor.
 */
function resolveWilsyR91K179E23P1WName(record = {}) {
  return String(
    record.displayName ||
      record.fullName ||
      record.name ||
      record.ownerDisplayName ||
      record.ownerName ||
      `${record.firstName || ''} ${record.surname || record.lastName || ''}`.trim() ||
      record.email ||
      record.operatorEmail ||
      record.title ||
      'Unnamed participant'
  ).trim();
}

/**
 * @function resolveWilsyR91K179E23P1WEmail
 * @description Resolves email from common CRM/operator fields.
 * @param {Object} record - Source record.
 * @returns {string} Email.
 * @collaboration Resolver duplicate guard, external invite flow, source rows.
 */
function resolveWilsyR91K179E23P1WEmail(record = {}) {
  return String(record.email || record.operatorEmail || record.primaryEmail || record.workEmail || record.contactEmail || '').trim();
}

/**
 * @function resolveWilsyR91K179E23P1WOperator
 * @description Resolves current operator context from tenant config.
 * @param {Object} tenantConfig - Tenant config.
 * @returns {Object} Operator context.
 * @collaboration Team tab, tenant context, participant resolver.
 */
function resolveWilsyR91K179E23P1WOperator(tenantConfig = {}) {
  return {
    tenantId: tenantConfig.tenantId || tenantConfig.id || 'wilsy-sovereign-root',
    operatorId: tenantConfig.operatorId || tenantConfig.userId || tenantConfig.ownerId || 'wilsy-operator',
    operatorEmail: tenantConfig.operatorEmail || tenantConfig.email || tenantConfig.ownerEmail || '',
    operatorName: tenantConfig.operatorName || tenantConfig.name || tenantConfig.ownerName || 'Wilsy operator',
    operatorRole: tenantConfig.operatorRole || tenantConfig.role || 'OPERATOR',
  };
}

/**
 * @function buildWilsyR91K179E23P1WParticipant
 * @description Converts CRM, operator, or external email source into a structured participant.
 * @param {Object|string} source - Source record or email.
 * @param {Object} context - Context.
 * @returns {Object|null} Structured participant.
 * @collaboration Meeting draft, selected tray, save payload.
 */
function buildWilsyR91K179E23P1WParticipant(source = {}, context = {}) {
  if (typeof source === 'string') {
    const value = source.trim();
    if (!value) return null;

    const email = isWilsyR91K179E23P1WEmail(value) ? value : '';
    const normalizedEmail = normalizeWilsyR91K179E23P1WEmail(email);
    const displayName = email ? value.split('@')[0] : value;

    return {
      participantId: normalizedEmail || `external-${displayName.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`,
      sourceType: 'EXTERNAL',
      sourceCollection: 'manual_invite',
      sourceRecordId: '',
      displayName,
      email,
      normalizedEmail,
      role: 'REQUIRED',
      inviteStatus: 'PENDING',
      consentPosture: 'UNKNOWN',
      tenantId: context.tenantId || '',
      operatorId: context.operatorId || '',
      evidenceKey: `PARTICIPANT:${normalizedEmail || displayName.toLowerCase()}`,
    };
  }

  const sourceType = String(source.sourceType || context.sourceType || 'EXTERNAL').toUpperCase();
  const sourceCollection = source.sourceCollection || context.sourceCollection || sourceType.toLowerCase();
  const sourceRecordId = source.sourceRecordId || resolveWilsyR91K179E23P1WRecordId(source);
  const displayName = resolveWilsyR91K179E23P1WName(source);
  const email = resolveWilsyR91K179E23P1WEmail(source);
  const normalizedEmail = normalizeWilsyR91K179E23P1WEmail(source.normalizedEmail || email);
  const participantId = String(source.participantId || sourceRecordId || normalizedEmail || displayName).trim();

  if (!participantId && !displayName && !normalizedEmail) return null;

  return {
    participantId,
    sourceType,
    sourceCollection,
    sourceRecordId,
    displayName,
    email,
    normalizedEmail,
    role: source.role || 'REQUIRED',
    inviteStatus: source.inviteStatus || 'PENDING',
    consentPosture: source.consentPosture || source.consentBasis || 'UNKNOWN',
    tenantId: source.tenantId || context.tenantId || '',
    operatorId: source.operatorId || context.operatorId || '',
    evidenceKey: source.evidenceKey || `${sourceType}:${normalizedEmail || sourceRecordId || displayName.toLowerCase()}`,
    sourceRecord: source.sourceRecord || source,
  };
}

/**
 * @function buildWilsyR91K179E23P1WIdentityKey
 * @description Builds duplicate identity from normalized email or CRM source id.
 * @param {Object} participant - Participant.
 * @returns {string} Identity key.
 * @collaboration Duplicate guard, source row toggle, selected tray.
 */
function buildWilsyR91K179E23P1WIdentityKey(participant = {}) {
  const email = normalizeWilsyR91K179E23P1WEmail(participant.normalizedEmail || participant.email);
  if (email) return `EMAIL:${email}`;

  const sourceType = String(participant.sourceType || 'EXTERNAL').toUpperCase();
  const sourceRecordId = String(participant.sourceRecordId || participant.participantId || '').trim();
  if (sourceRecordId) return `${sourceType}:${sourceRecordId}`;

  return `${sourceType}:${String(participant.displayName || '').trim().toLowerCase()}`;
}

/**
 * @function normalizeWilsyR91K179E23P1WParticipants
 * @description Normalizes and deduplicates participant collections.
 * @param {Array} participants - Participant candidates.
 * @param {Object} context - Context.
 * @returns {Array<Object>} Deduped participants.
 * @collaboration Meeting draft, duplicate guard, selected tray.
 */
function normalizeWilsyR91K179E23P1WParticipants(participants = [], context = {}) {
  const seen = new Set();
  const normalized = [];

  for (const participant of Array.isArray(participants) ? participants : []) {
    const next = buildWilsyR91K179E23P1WParticipant(participant, context);
    if (!next) continue;

    const key = buildWilsyR91K179E23P1WIdentityKey(next);
    if (!key || seen.has(key)) continue;

    seen.add(key);
    normalized.push(next);
  }

  return normalized;
}

/**
 * @function extractWilsyR91K179E23P1WRecords
 * @description Extracts record arrays from live CRM payload variants.
 * @param {Object} payload - Payload.
 * @returns {Array<Object>} Records.
 * @collaboration Live CRM routes, resolver source state, source tabs.
 */
function extractWilsyR91K179E23P1WRecords(payload = {}) {
  if (Array.isArray(payload.records)) return payload.records;
  if (Array.isArray(payload.data)) return payload.data;
  if (Array.isArray(payload.leads)) return payload.leads;
  if (Array.isArray(payload.contacts)) return payload.contacts;
  return [];
}

/**
 * @function buildWilsyR91K179E23P1WOptions
 * @description Builds resolver options from live CRM sources and operator context.
 * @param {Object} sourceState - Source state.
 * @param {Object} tenantConfig - Tenant config.
 * @returns {Array<Object>} Options.
 * @collaboration Leads tab, Contacts tab, Team tab.
 */
function buildWilsyR91K179E23P1WOptions(sourceState = {}, tenantConfig = {}) {
  const operator = resolveWilsyR91K179E23P1WOperator(tenantConfig);

  const teamRecord = {
    participantId: operator.operatorId,
    userId: operator.operatorId,
    displayName: operator.operatorName,
    fullName: operator.operatorName,
    email: operator.operatorEmail,
    operatorEmail: operator.operatorEmail,
    operatorId: operator.operatorId,
    tenantId: operator.tenantId,
    role: operator.operatorRole,
    consentPosture: 'INTERNAL_OPERATOR',
  };

  return [
    ...(sourceState.leads || []).map((record) => buildWilsyR91K179E23P1WParticipant(record, {
      tenantId: operator.tenantId,
      operatorId: operator.operatorId,
      sourceType: 'LEAD',
      sourceCollection: 'leads',
    })),
    ...(sourceState.contacts || []).map((record) => buildWilsyR91K179E23P1WParticipant(record, {
      tenantId: operator.tenantId,
      operatorId: operator.operatorId,
      sourceType: 'CONTACT',
      sourceCollection: 'contacts',
    })),
    buildWilsyR91K179E23P1WParticipant(teamRecord, {
      tenantId: operator.tenantId,
      operatorId: operator.operatorId,
      sourceType: 'USER',
      sourceCollection: 'team',
    }),
  ].filter(Boolean);
}

/**
 * @function filterWilsyR91K179E23P1WOptions
 * @description Filters options by tab and search.
 * @param {Array<Object>} options - Options.
 * @param {string} tab - Tab.
 * @param {string} searchTerm - Search term.
 * @param {boolean} showEmailLess - Email-less visibility.
 * @returns {Array<Object>} Filtered options.
 * @collaboration Resolver search, source rows, source tabs.
 */
function filterWilsyR91K179E23P1WOptions(options = [], tab = 'LEADS', searchTerm = '', showEmailLess = false) {
  const activeTab = String(tab || 'LEADS').toUpperCase();
  const needle = String(searchTerm || '').trim().toLowerCase();

  return options.filter((option) => {
    const tabMatches =
      (activeTab === 'LEADS' && option.sourceType === 'LEAD') ||
      (activeTab === 'CONTACTS' && option.sourceType === 'CONTACT') ||
      (activeTab === 'TEAM' && option.sourceType === 'USER');

    if (!tabMatches) return false;
    if (!showEmailLess && !option.normalizedEmail && option.sourceType !== 'USER') return false;
    if (!needle) return true;

    return [option.displayName, option.email, option.sourceType, option.sourceCollection, option.sourceRecordId]
      .join(' ')
      .toLowerCase()
      .includes(needle);
  });
}

/**
 * @function WilsyMeetingParticipantResolver
 * @description Renders the production participant resolver with live CRM sources, external invite, selected tray, and duplicate protection.
 * @param {Object} props - Props.
 * @returns {JSX.Element} Resolver modal.
 * @collaboration Meeting editor, CRM live leads, CRM live contacts.
 */
export default function WilsyMeetingParticipantResolver({
  tenantConfig = {},
  selectedParticipants = [],
  onParticipantsChange = () => {},
  onClose = () => {},
}) {
  const operator = resolveWilsyR91K179E23P1WOperator(tenantConfig);
  const [sourceTab, setSourceTab] = useState('LEADS');
  const [searchTerm, setSearchTerm] = useState('');
  const [externalInput, setExternalInput] = useState('');
  const [showEmailLess, setShowEmailLess] = useState(false);
  const [duplicateMessage, setDuplicateMessage] = useState('');
  const [sourceState, setSourceState] = useState({ leads: [], contacts: [], loading: true, error: '' });

  const normalizedSelected = useMemo(
    () => normalizeWilsyR91K179E23P1WParticipants(selectedParticipants, operator),
    [selectedParticipants, operator.tenantId, operator.operatorId]
  );

  const sourceOptions = useMemo(
    () => buildWilsyR91K179E23P1WOptions(sourceState, tenantConfig),
    [sourceState, tenantConfig]
  );

  const visibleOptions = useMemo(
    () => filterWilsyR91K179E23P1WOptions(sourceOptions, sourceTab, searchTerm, showEmailLess),
    [sourceOptions, sourceTab, searchTerm, showEmailLess]
  );

  const selectedKeys = useMemo(
    () => new Set(normalizedSelected.map(buildWilsyR91K179E23P1WIdentityKey)),
    [normalizedSelected]
  );

  const counts = {
    LEADS: sourceOptions.filter((option) => option.sourceType === 'LEAD').length,
    CONTACTS: sourceOptions.filter((option) => option.sourceType === 'CONTACT').length,
    TEAM: sourceOptions.filter((option) => option.sourceType === 'USER').length,
    SELECTED: normalizedSelected.length,
  };

  useEffect(() => {
    let active = true;

    /**
     * @function loadWilsyR91K179E23P1WSources
     * @description Loads live CRM leads and contacts for participant resolution.
     * @returns {Promise<void>} Source load promise.
     * @collaboration CRM live routes, tenant context, resolver tabs.
     */
    async function loadWilsyR91K179E23P1WSources() {
      const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:5050';
      const headers = {
        Accept: 'application/json',
        'X-Tenant-Id': operator.tenantId,
        'X-Wilsy-Tenant-ID': operator.tenantId,
        'X-Wilsy-Client': 'MEETING_PARTICIPANT_RESOLVER',
      };

      setSourceState((current) => ({ ...current, loading: true, error: '' }));

      try {
        const [leadsResponse, contactsResponse] = await Promise.all([
          fetch(`${apiBase}/api/crm/live/leads`, { headers }),
          fetch(`${apiBase}/api/crm/live/contacts`, { headers }),
        ]);

        const [leadsPayload, contactsPayload] = await Promise.all([
          leadsResponse.json().catch(() => ({})),
          contactsResponse.json().catch(() => ({})),
        ]);

        if (!active) return;

        setSourceState({
          leads: extractWilsyR91K179E23P1WRecords(leadsPayload),
          contacts: extractWilsyR91K179E23P1WRecords(contactsPayload),
          loading: false,
          error: '',
        });
      } catch (error) {
        if (!active) return;
        setSourceState((current) => ({ ...current, loading: false, error: error?.message || 'Participant sources unavailable.' }));
      }
    }

    loadWilsyR91K179E23P1WSources();

    return () => {
      active = false;
    };
  }, [operator.tenantId]);

  /**
   * @function updateWilsyR91K179E23P1WParticipants
   * @description Pushes deduplicated participant updates to editor state.
   * @param {Array<Object>} participants - Participants.
   * @returns {void}
   * @collaboration Resolver state, meeting draft, selected tray.
   */
  function updateWilsyR91K179E23P1WParticipants(participants = []) {
    onParticipantsChange(normalizeWilsyR91K179E23P1WParticipants(participants, operator));
  }

  /**
   * @function toggleWilsyR91K179E23P1WParticipant
   * @description Selects or removes a source participant.
   * @param {Object} participant - Participant.
   * @returns {void}
   * @collaboration Checkbox rows, duplicate guard, selected tray.
   */
  function toggleWilsyR91K179E23P1WParticipant(participant = {}) {
    const normalized = buildWilsyR91K179E23P1WParticipant(participant, operator);
    if (!normalized) return;

    const key = buildWilsyR91K179E23P1WIdentityKey(normalized);

    if (selectedKeys.has(key)) {
      updateWilsyR91K179E23P1WParticipants(normalizedSelected.filter((item) => buildWilsyR91K179E23P1WIdentityKey(item) !== key));
      setDuplicateMessage('');
      return;
    }

    updateWilsyR91K179E23P1WParticipants([...normalizedSelected, normalized]);
    setDuplicateMessage('');
  }

  /**
   * @function removeWilsyR91K179E23P1WParticipant
   * @description Removes a selected participant.
   * @param {Object} participant - Participant.
   * @returns {void}
   * @collaboration Selected tab, selected tray, meeting draft.
   */
  function removeWilsyR91K179E23P1WParticipant(participant = {}) {
    const key = buildWilsyR91K179E23P1WIdentityKey(participant);
    updateWilsyR91K179E23P1WParticipants(normalizedSelected.filter((item) => buildWilsyR91K179E23P1WIdentityKey(item) !== key));
    setDuplicateMessage('');
  }

  /**
   * @function addWilsyR91K179E23P1WExternalInvites
   * @description Adds external email invites with duplicate protection.
   * @returns {void}
   * @collaboration External tab, duplicate guard, selected tray.
   */
  function addWilsyR91K179E23P1WExternalInvites() {
    const values = String(externalInput || '').split(/[\n,;]+/).map((value) => value.trim()).filter(Boolean);

    if (values.length === 0) {
      setDuplicateMessage('Enter an email address before adding an external invite.');
      return;
    }

    const invalid = values.find((value) => !isWilsyR91K179E23P1WEmail(value));

    if (invalid) {
      setDuplicateMessage(`${invalid} is not a valid invite email.`);
      return;
    }

    const currentKeys = new Set(normalizedSelected.map(buildWilsyR91K179E23P1WIdentityKey));
    const nextParticipants = [...normalizedSelected];
    const duplicates = [];

    values.forEach((email) => {
      const participant = buildWilsyR91K179E23P1WParticipant(email, operator);
      const key = buildWilsyR91K179E23P1WIdentityKey(participant);

      if (currentKeys.has(key)) {
        duplicates.push(email);
        return;
      }

      currentKeys.add(key);
      nextParticipants.push(participant);
    });

    setDuplicateMessage(duplicates.length > 0 ? `${duplicates.join(', ')} already selected.` : '');
    updateWilsyR91K179E23P1WParticipants(nextParticipants);

    if (nextParticipants.length !== normalizedSelected.length) {
      setExternalInput('');
      setSourceTab('SELECTED');
    }
  }

  return (
    <div className={styles.wilsyModalBackdrop} data-wilsy-r91k179e23p1w-modal="participant-resolver">
      <section className={`${styles.wilsyCommandModal} ${styles.participantResolverModal}`} role="dialog" aria-modal="true" aria-label="Resolve meeting participants">
        <header className={styles.participantResolverHeader}>
          <div>
            <small>Participant resolver command</small>
            <h3>Resolve meeting participants</h3>
            <p>Select live CRM leads, contacts, the current operator, or external invite emails. Duplicate identities are blocked before save.</p>
          </div>
          <nav aria-label="Participant resolver actions">
            <button type="button" className={styles.modalSecondary} onClick={onClose} aria-label="Close participant resolver">
              <X size={16} />
              Close
            </button>
            <button type="button" className={styles.primaryCommandButton} onClick={onClose}>
              <Users size={16} />
              Done · {normalizedSelected.length}
            </button>
          </nav>
        </header>

        <div className={styles.participantResolverShell}>
          <aside className={styles.participantResolverTabs} aria-label="Participant source tabs">
            {['LEADS', 'CONTACTS', 'TEAM', 'EXTERNAL', 'SELECTED'].map((tab) => (
              <button type="button" key={tab} data-active={sourceTab === tab} onClick={() => { setSourceTab(tab); setDuplicateMessage(''); }}>
                <strong>{tab}</strong>
                <span>{tab === 'EXTERNAL' ? 'Invite' : counts[tab] || 0}</span>
              </button>
            ))}
          </aside>

          <main className={styles.participantResolverStage}>
            {sourceTab !== 'EXTERNAL' && sourceTab !== 'SELECTED' ? (
              <div className={styles.participantResolverSearch}>
                <label>
                  <span>Search source</span>
                  <div className={styles.participantResolverSearchInput}>
                    <Search size={16} />
                    <input value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} placeholder="Search name, email, company, owner or CRM id" />
                  </div>
                </label>
                <label className={styles.participantResolverToggle}>
                  <input type="checkbox" checked={showEmailLess} onChange={(event) => setShowEmailLess(event.target.checked)} />
                  <span>Show records without email addresses as well</span>
                </label>
              </div>
            ) : null}

            {sourceState.loading ? <div className={styles.participantResolverNotice}><strong>Loading live CRM sources</strong><span>Reading Leads and Contacts through tenant-scoped CRM live routes.</span></div> : null}
            {sourceState.error ? <div className={styles.participantResolverNotice} data-status="warning"><strong>Source warning</strong><span>{sourceState.error}</span></div> : null}
            {duplicateMessage ? <div className={styles.participantResolverNotice} data-status="duplicate"><strong>Duplicate guard</strong><span>{duplicateMessage}</span></div> : null}

            {sourceTab === 'EXTERNAL' ? (
              <section className={styles.externalInvitePanel}>
                <label>
                  <span>Invite by email address</span>
                  <textarea value={externalInput} onChange={(event) => setExternalInput(event.target.value)} placeholder="name@company.com, second@company.com" />
                </label>
                <p>Use commas or new lines. Wilsy OS blocks duplicate email identities before save.</p>
                <button type="button" onClick={addWilsyR91K179E23P1WExternalInvites}><UserPlus size={16} />Add external invite</button>
              </section>
            ) : null}

            {sourceTab === 'SELECTED' ? (
              <section className={styles.selectedParticipantPanel}>
                {normalizedSelected.length > 0 ? normalizedSelected.map((participant) => (
                  <article key={buildWilsyR91K179E23P1WIdentityKey(participant)}>
                    <div><strong>{participant.displayName || participant.email}</strong><span>{participant.email || 'No email on source record'}</span></div>
                    <small>{participant.sourceType} · {participant.inviteStatus}</small>
                    <button type="button" onClick={() => removeWilsyR91K179E23P1WParticipant(participant)}>Remove</button>
                  </article>
                )) : <div className={styles.participantResolverEmpty}><strong>No participants selected</strong><p>Select Leads, Contacts, Team, or invite external participants.</p></div>}
              </section>
            ) : null}

            {sourceTab !== 'EXTERNAL' && sourceTab !== 'SELECTED' ? (
              <section className={styles.participantSourceList}>
                {visibleOptions.length > 0 ? visibleOptions.map((participant) => {
                  const key = buildWilsyR91K179E23P1WIdentityKey(participant);
                  const selected = selectedKeys.has(key);

                  return (
                    <button type="button" key={key} data-selected={selected} onClick={() => toggleWilsyR91K179E23P1WParticipant(participant)}>
                      {selected ? <CheckSquare size={20} /> : <Square size={20} />}
                      <span><strong>{participant.displayName || participant.email}</strong><small>{participant.email || 'No email on source record'}</small></span>
                      <em>{participant.sourceType}</em>
                    </button>
                  );
                }) : <div className={styles.participantResolverEmpty}><strong>No source records in this view</strong><p>{sourceTab === 'CONTACTS' ? 'Contacts route is live, but no contact records are available yet.' : 'No matching live source records found for this filter.'}</p></div>}
              </section>
            ) : null}
          </main>
        </div>

        <footer className={styles.wilsyModalActions}>
          <button type="button" className={styles.modalSecondary} onClick={onClose}><X size={16} />Back to meeting</button>
          <button type="button" className={styles.primaryCommandButton} onClick={onClose}><Users size={16} />Done · {normalizedSelected.length} selected</button>
        </footer>
      </section>
    </div>
  );
}
