/* eslint-disable */
import React, { useMemo, useState } from 'react';
import {
  AlertTriangle,
  Building2,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  Database,
  Download,
  FileCheck2,
  Filter,
  GitBranch,
  Mail,
  MoreHorizontal,
  Network,
  Phone,
  Plus,
  RefreshCcw,
  Search,
  Shield,
  SlidersHorizontal,
  Sparkles,
  UserRound,
  Users,
} from 'lucide-react';
import styles from './WilsyContactOperatingRoom.module.css';

const CONTACT_LIST_VIEWS = Object.freeze([
  { id: 'ALL_CONTACTS', label: 'All Contacts', detail: 'Every source-backed relationship' },
  { id: 'CONSENT_READY', label: 'Consent Ready', detail: 'Communication authority confirmed' },
  { id: 'ACCOUNT_LINKED', label: 'Account Linked', detail: 'Connected to business graph' },
  { id: 'ACTION_REQUIRED', label: 'Action Required', detail: 'Missing consent, account, or proof' },
]);

const CONTACT_TOP_TABS = Object.freeze([
  { id: 'records', label: 'Records', icon: Users },
  { id: 'relationships', label: 'Relationships', icon: GitBranch },
  { id: 'consent', label: 'Consent', icon: Shield },
  { id: 'sources', label: 'Sources', icon: Network },
]);

const CONTACT_SORT_OPTIONS = Object.freeze([
  { id: 'relationship', label: 'Relationship score' },
  { id: 'name', label: 'Contact name' },
  { id: 'account', label: 'Account name' },
  { id: 'activity', label: 'Latest activity' },
]);

const CONTACT_FILTER_GROUPS = Object.freeze([
  {
    id: 'system',
    label: 'System Defined Filters',
    options: Object.freeze([
      'Consent Ready',
      'Missing Email',
      'Account Linked',
      'Authority Pending',
      'Recently Touched',
      'Inactive Contacts',
    ]),
  },
  {
    id: 'relationship',
    label: 'Relationship Signals',
    options: Object.freeze([
      'Decision Makers',
      'Customer Success',
      'Deal Influencers',
      'Support Contacts',
      'Partner Contacts',
    ]),
  },
]);

/**
 * @function resolveContactId
 * @description Resolves a stable contact row id from flexible CRM contact payloads.
 * @param {Object} record - Contact record.
 * @param {number} index - Fallback index.
 * @returns {string} Stable contact id.
 * @collaboration R76C Contacts Operating Room, live CRM source records, row selection.
 */
function resolveContactId(record = {}, index = 0) {
  return String(record._id || record.id || record.uuid || record.recordId || record.contactId || record.email || `contact-${index}`);
}

/**
 * @function resolveContactValue
 * @description Resolves normalized contact field values from live CRM payloads.
 * @param {Object} record - Contact record.
 * @param {string} field - Field name.
 * @returns {string} Display value.
 * @collaboration R76C Contacts Operating Room, Zoho-coverage parity, source-flexible CRM data.
 */
function resolveContactValue(record = {}, field = '') {
  const values = {
    name: record.name || record.contactName || record.fullName || [record.firstName, record.lastName].filter(Boolean).join(' '),
    accountName: record.accountName || record.company || record.companyName || record.organization || record.account?.name,
    email: record.email || record.primaryEmail || record.contactEmail,
    phone: record.phone || record.mobile || record.mobileNumber || record.workPhone || record.telephone,
    title: record.title || record.jobTitle || record.role || record.designation,
    department: record.department || record.team || record.function,
    source: record.source || record.sourceSystem || record.connector || record.origin || record.channel,
    owner: record.owner || record.ownerName || record.assignedTo || record.createdBy,
    status: record.status || record.lifecycleStage || record.contactStatus,
    consentStatus: record.consentStatus || record.communicationConsent || record.popiaConsent || record.marketingConsent,
    lastActivity: record.lastActivity || record.lastContactedAt || record.lastTouchedAt || record.updatedAt || record.createdAt,
    provenanceHash: record.provenanceHash || record.cryptographicHash || record.rootHash || record.sealHash,
  };

  return String(values[field] || '—').trim() || '—';
}

/**
 * @function isKnownContactValue
 * @description Determines whether a contact value is meaningful.
 * @param {string} value - Candidate display value.
 * @returns {boolean} True when value is known.
 * @collaboration R76C data quality scoring, Contacts field intelligence, source proof posture.
 */
function isKnownContactValue(value = '') {
  const text = String(value || '').trim();
  return Boolean(text && text !== '—' && text !== 'UNSEALED' && text.toUpperCase() !== 'NONE');
}

/**
 * @function resolveContactStatus
 * @description Resolves operational contact status.
 * @param {Object} record - Contact record.
 * @returns {string} Status label.
 * @collaboration R76C relationship cockpit, contact status table, source-compatible CRM payloads.
 */
function resolveContactStatus(record = {}) {
  const raw = resolveContactValue(record, 'status').toUpperCase();

  if (raw.includes('ACTIVE') || raw.includes('CUSTOMER') || raw.includes('OPEN')) return 'ACTIVE';
  if (raw.includes('RISK') || raw.includes('ESCALATED')) return 'AT_RISK';
  if (raw.includes('INACTIVE') || raw.includes('LOST') || raw.includes('ARCHIVED')) return 'INACTIVE';

  return 'NEW';
}

/**
 * @function resolveContactConsent
 * @description Resolves contact communication and privacy consent posture.
 * @param {Object} record - Contact record.
 * @returns {string} Consent posture.
 * @collaboration R76C POPIA/GDPR consent posture, contact communications, compliance HUD.
 */
function resolveContactConsent(record = {}) {
  const raw = String(resolveContactValue(record, 'consentStatus')).toUpperCase();

  if (raw.includes('TRUE') || raw.includes('YES') || raw.includes('VERIFIED') || raw.includes('OPT_IN') || raw.includes('CONSENT')) return 'VERIFIED';
  if (raw.includes('FALSE') || raw.includes('NO') || raw.includes('OPT_OUT') || raw.includes('REVOKED')) return 'REVOKED';
  if (raw.includes('PENDING') || raw.includes('REVIEW')) return 'PENDING';

  return 'PENDING';
}

/**
 * @function resolveContactSource
 * @description Resolves the contact source label.
 * @param {Object} record - Contact record.
 * @returns {string} Source label.
 * @collaboration R76C source route proof, contact provenance, live CRM source registry.
 */
function resolveContactSource(record = {}) {
  return resolveContactValue(record, 'source') === '—' ? 'Backend CRM' : resolveContactValue(record, 'source');
}

/**
 * @function resolveContactScore
 * @description Calculates relationship readiness from consent, account linkage, communication fields and proof.
 * @param {Object} record - Contact record.
 * @returns {number} Relationship score.
 * @collaboration R76C relationship intelligence, contact prioritization, Wilsy OS proof scoring.
 */
function resolveContactScore(record = {}) {
  const consent = resolveContactConsent(record);
  const status = resolveContactStatus(record);
  const hasAccount = isKnownContactValue(resolveContactValue(record, 'accountName'));
  const hasEmail = isKnownContactValue(resolveContactValue(record, 'email'));
  const hasPhone = isKnownContactValue(resolveContactValue(record, 'phone'));
  const hasTitle = isKnownContactValue(resolveContactValue(record, 'title'));
  const hasProof = isKnownContactValue(resolveContactValue(record, 'provenanceHash'));

  const fieldScore = [hasAccount, hasEmail, hasPhone, hasTitle].filter(Boolean).length * 12;
  const consentScore = consent === 'VERIFIED' ? 22 : consent === 'PENDING' ? 8 : 0;
  const statusScore = status === 'ACTIVE' ? 14 : status === 'AT_RISK' ? 6 : status === 'INACTIVE' ? 0 : 8;
  const proofScore = hasProof ? 16 : 0;

  return Math.max(0, Math.min(100, fieldScore + consentScore + statusScore + proofScore));
}

/**
 * @function resolveContactBand
 * @description Converts contact score to an operator-facing readiness band.
 * @param {number} score - Contact relationship score.
 * @returns {string} Readiness band.
 * @collaboration R76C Contacts score pills, operator prioritization, CRM command cockpit.
 */
function resolveContactBand(score = 0) {
  if (score >= 78) return 'Command Ready';
  if (score >= 54) return 'Relationship Warm';
  if (score >= 28) return 'Needs Proof';
  return 'Unqualified';
}

/**
 * @function resolveContactHref
 * @description Builds safe contact action links.
 * @param {Object} record - Contact record.
 * @param {string} channel - Contact channel.
 * @returns {string|null} Contact href or null.
 * @collaboration R76C quick actions, contact outreach, browser-safe communication links.
 */
function resolveContactHref(record = {}, channel = 'email') {
  if (channel === 'email') {
    const email = resolveContactValue(record, 'email');
    return isKnownContactValue(email) ? `mailto:${email}` : null;
  }

  const phone = resolveContactValue(record, 'phone');
  const normalizedPhone = String(phone || '').replace(/[^\d+]/g, '');
  return isKnownContactValue(phone) && normalizedPhone ? `tel:${normalizedPhone}` : null;
}

/**
 * @function filterContactByView
 * @description Applies the active contact list view to a record.
 * @param {Object} record - Contact record.
 * @param {string} listViewId - Active view id.
 * @returns {boolean} True when record matches the view.
 * @collaboration R76C Contacts view rail, relationship operations, source-backed filtering.
 */
function filterContactByView(record = {}, listViewId = 'ALL_CONTACTS') {
  if (listViewId === 'CONSENT_READY') return resolveContactConsent(record) === 'VERIFIED';
  if (listViewId === 'ACCOUNT_LINKED') return isKnownContactValue(resolveContactValue(record, 'accountName'));
  if (listViewId === 'ACTION_REQUIRED') {
    return resolveContactConsent(record) !== 'VERIFIED'
      || !isKnownContactValue(resolveContactValue(record, 'accountName'))
      || !isKnownContactValue(resolveContactValue(record, 'email'));
  }

  return true;
}

/**
 * @function sortContactRecords
 * @description Sorts contact records for the active operator sort mode.
 * @param {Array<Object>} records - Contact records.
 * @param {string} sortMode - Sort mode.
 * @returns {Array<Object>} Sorted records.
 * @collaboration R76C Contacts sort deck, relationship cockpit, Zoho-grade list parity.
 */
function sortContactRecords(records = [], sortMode = 'relationship') {
  const sortedRecords = [...records];

  return sortedRecords.sort((leftRecord, rightRecord) => {
    if (sortMode === 'name') {
      return resolveContactValue(leftRecord, 'name').localeCompare(resolveContactValue(rightRecord, 'name'));
    }

    if (sortMode === 'account') {
      return resolveContactValue(leftRecord, 'accountName').localeCompare(resolveContactValue(rightRecord, 'accountName'));
    }

    if (sortMode === 'activity') {
      const leftDate = Date.parse(resolveContactValue(leftRecord, 'lastActivity')) || 0;
      const rightDate = Date.parse(resolveContactValue(rightRecord, 'lastActivity')) || 0;
      return rightDate - leftDate;
    }

    return resolveContactScore(rightRecord) - resolveContactScore(leftRecord);
  });
}

/**
 * @function buildContactMetrics
 * @description Builds Contacts operating metrics from live CRM records and source posture.
 * @param {Object} params - Metric inputs.
 * @returns {Array<Object>} Metric cards.
 * @collaboration R76C Contacts cockpit, source truth, relationship intelligence telemetry.
 */
function buildContactMetrics({
  contacts = [],
  accounts = [],
  deals = [],
  evidence = [],
  sourcePosture = {},
} = {}) {
  const consentReady = contacts.filter(record => resolveContactConsent(record) === 'VERIFIED').length;
  const accountLinked = contacts.filter(record => isKnownContactValue(resolveContactValue(record, 'accountName'))).length;
  const relationshipReady = contacts.filter(record => resolveContactScore(record) >= 54).length;
  const connectedRoutes = Number(sourcePosture.connected || sourcePosture.connectedRoutes || 0);

  return [
    {
      id: 'contacts',
      label: 'Relationship Graph',
      value: String(contacts.length),
      detail: contacts.length ? 'Source-backed contacts available' : 'No contacts returned yet',
      progress: contacts.length ? Math.round((relationshipReady / Math.max(1, contacts.length)) * 100) : 0,
      icon: Users,
    },
    {
      id: 'consent',
      label: 'Consent Readiness',
      value: `${consentReady}/${contacts.length || 0}`,
      detail: 'Communication authority and privacy posture',
      progress: contacts.length ? Math.round((consentReady / Math.max(1, contacts.length)) * 100) : 0,
      icon: Shield,
    },
    {
      id: 'accounts',
      label: 'Account Linkage',
      value: `${accountLinked}/${contacts.length || 0}`,
      detail: `${accounts.length || 0} account records in current source snapshot`,
      progress: contacts.length ? Math.round((accountLinked / Math.max(1, contacts.length)) * 100) : 0,
      icon: Building2,
    },
    {
      id: 'proof',
      label: 'Proof Surface',
      value: String(evidence.length || deals.length || connectedRoutes),
      detail: evidence.length ? 'Evidence anchors available' : 'Awaiting sealed contact proof',
      progress: Math.min(100, Math.max(0, evidence.length * 12 + connectedRoutes * 8)),
      icon: FileCheck2,
    },
  ];
}


/**
 * @function resolveCrmGlobalThemeAuthorityLabel
 * @description Resolves a business-facing label for the active Command Center operating skin.
 * @param {Object} themeRuntime - Active CRM/global theme runtime packet.
 * @returns {string} Business-facing theme label.
 * @collaboration R79B Command Center theme authority, CRM module chrome, 26-skin global registry.
 */
function resolveCrmGlobalThemeAuthorityLabel(themeRuntime = {}) {
  const rawLabel = themeRuntime.label
    || themeRuntime.name
    || themeRuntime.title
    || themeRuntime.displayName
    || themeRuntime.themeLabel
    || themeRuntime.skinLabel
    || themeRuntime.themeId
    || 'Command Center Theme';

  return String(rawLabel)
    .replace(/[-_]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, letter => letter.toUpperCase());
}

/**
 * @function resolveCrmGlobalThemeAuthorityMode
 * @description Resolves a business-facing mode label for the active global theme runtime.
 * @param {Object} themeRuntime - Active CRM/global theme runtime packet.
 * @returns {string} Business-facing mode label.
 * @collaboration R79B Day/Night/Auto command mode, Command Center runtime, CRM module chrome.
 */
function resolveCrmGlobalThemeAuthorityMode(themeRuntime = {}) {
  const rawMode = themeRuntime.resolvedMode || themeRuntime.effectiveMode || themeRuntime.mode || 'night';
  const normalized = String(rawMode).replace(/[-_]+/g, ' ').trim();

  return normalized ? normalized.replace(/\b\w/g, letter => letter.toUpperCase()) : 'Night';
}

/**
 * @function openCrmGlobalThemeAuthorityFallback
 * @description Opens the global theme authority through the CRM/Command Center event bridge when no direct handler is provided.
 * @returns {void}
 * @collaboration R79B module theme authority button, Account Command Center, global skin governance.
 */
function openCrmGlobalThemeAuthorityFallback() {
  if (typeof window === 'undefined') return;

  window.dispatchEvent(new CustomEvent('wilsy:crm:open-command-center', {
    detail: {
      panel: 'preferences',
      section: 'theme-authority',
      source: 'CRM_GLOBAL_THEME_AUTHORITY'
    }
  }));
}

/**
 * @function WilsyContactOperatingRoom
 * @description Renders the sovereign Contacts operating room for relationship intelligence, consent posture and source proof.
 * @param {Object} props - Component props.
 * @returns {JSX.Element} Contacts operating room.
 * @collaboration R76C Contacts module, CRMDashboard route ownership, Wilsy OS CRM competitive surface.
 */
export default function WilsyContactOperatingRoom({
  contacts = [],
  accounts = [],
  deals = [],
  evidence = [],
  connectors = [],
  sourcePosture = {},
  sourceErrors = [],
  loading = false,
  themeRuntime = {},
  tenantConfig = {},
  user = {},
  onRefresh = () => {},
  onCreate = () => {},
  onOpenThemeAuthority = openCrmGlobalThemeAuthorityFallback,
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTopTab, setActiveTopTab] = useState('records');
  const [activeListView, setActiveListView] = useState('ALL_CONTACTS');
  const [sortMode, setSortMode] = useState('relationship');
  const [sortMenuOpen, setSortMenuOpen] = useState(false);
  const [selectedRowIds, setSelectedRowIds] = useState([]);
  const [openRowActionId, setOpenRowActionId] = useState('');
  const [filterRailOpen, setFilterRailOpen] = useState(true);

  const normalizedContacts = Array.isArray(contacts) ? contacts : [];
  const activeView = CONTACT_LIST_VIEWS.find(view => view.id === activeListView) || CONTACT_LIST_VIEWS[0];
  const activeSort = CONTACT_SORT_OPTIONS.find(option => option.id === sortMode) || CONTACT_SORT_OPTIONS[0];
  const tenantLabel = tenantConfig?.legalName || tenantConfig?.name || tenantConfig?.tenantName || 'Wilsy OS Root';
  const role = String(user?.role || user?.accountRole || tenantConfig?.role || 'RELATIONSHIP_OPERATOR').toUpperCase();
  const globalThemeAuthorityLabel = resolveCrmGlobalThemeAuthorityLabel(themeRuntime);
  const globalThemeAuthorityMode = resolveCrmGlobalThemeAuthorityMode(themeRuntime);

  const filteredContacts = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    return sortContactRecords(
      normalizedContacts.filter((record) => {
        if (!filterContactByView(record, activeListView)) return false;

        if (!query) return true;

        return [
          'name',
          'accountName',
          'email',
          'phone',
          'title',
          'department',
          'source',
          'owner',
          'status',
          'consentStatus',
        ].some(field => resolveContactValue(record, field).toLowerCase().includes(query));
      }),
      sortMode
    );
  }, [activeListView, normalizedContacts, searchQuery, sortMode]);

  const contactMetrics = useMemo(() => buildContactMetrics({
    contacts: normalizedContacts,
    accounts,
    deals,
    evidence,
    sourcePosture,
  }), [accounts, deals, evidence, normalizedContacts, sourcePosture]);

  const visibleIds = filteredContacts.map((record, index) => resolveContactId(record, index));
  const allRowsSelected = visibleIds.length > 0 && visibleIds.every(recordId => selectedRowIds.includes(recordId));

  /**
   * @function handleToggleAllContactSelection
   * @description Toggles selection for every visible contact row.
   * @collaboration R76C Contacts table, bulk action posture, operator list control.
   */
  function handleToggleAllContactSelection() {
    if (allRowsSelected) {
      setSelectedRowIds([]);
      return;
    }

    setSelectedRowIds(visibleIds);
  }

  /**
   * @function handleToggleContactSelection
   * @description Toggles one contact row selection.
   * @param {string} recordId - Contact record id.
   * @collaboration R76C Contacts table, row action state, bulk operations.
   */
  function handleToggleContactSelection(recordId) {
    setSelectedRowIds(previous => (
      previous.includes(recordId)
        ? previous.filter(value => value !== recordId)
        : [...previous, recordId]
    ));
  }

  /**
   * @function renderContactMetrics
   * @description Renders relationship, consent, account and proof telemetry.
   * @returns {JSX.Element} Contact metrics deck.
   * @collaboration R76C Contacts command surface, Wilsy OS operating metrics, source proof.
   */
  function renderContactMetrics() {
    return (
      <section className={styles.contactMetricDeck} aria-label="Contacts operating metrics">
        {contactMetrics.map((metric) => {
          const Icon = metric.icon;

          return (
            <article key={metric.id}>
              <span className={styles.contactMetricIcon}>
                <Icon size={20} />
              </span>
              <span className={styles.contactMetricCopy}>
                <small>{metric.label}</small>
                <strong>{metric.value}</strong>
                <em>{metric.detail}</em>
              </span>
              <i className={styles.contactMetricBar}>
                <b style={{ width: `${metric.progress}%` }} />
              </i>
            </article>
          );
        })}
      </section>
    );
  }

  /**
   * @function renderFilterRail
   * @description Renders Contacts list views and relationship filters.
   * @returns {JSX.Element|null} Filter rail.
   * @collaboration R76C Contacts filtering, Zoho parity, Wilsy relationship intelligence.
   */
  function renderFilterRail() {
    if (!filterRailOpen) return null;

    return (
      <aside className={styles.contactFilterRail} aria-label="Contact filters">
        <header>
          <span>
            <small>Filter Contacts by</small>
            <strong>Relationship Signals</strong>
          </span>
          <button type="button" onClick={(event) => event.currentTarget.blur()} aria-label="Filter options">
            <MoreHorizontal size={17} />
          </button>
        </header>

        <label className={styles.contactFilterSearch}>
          <Search size={18} />
          <input
            value={searchQuery}
            onChange={event => setSearchQuery(event.target.value)}
            placeholder="Search filters"
            aria-label="Search contact filters"
          />
        </label>

        {CONTACT_FILTER_GROUPS.map(group => (
          <section key={group.id} className={styles.contactFilterGroup}>
            <strong>{group.label}</strong>
            {group.options.map(option => (
              <button key={option} type="button">
                <span aria-hidden="true" />
                <em>{option}</em>
              </button>
            ))}
          </section>
        ))}
      </aside>
    );
  }

  /**
   * @function renderRecordsTab
   * @description Renders the source-backed Contacts records cockpit.
   * @returns {JSX.Element} Records tab.
   * @collaboration R76C Contacts list cockpit, consent-aware rows, source-honest empty state.
   */
  function renderRecordsTab() {
    return (
      <section className={styles.contactRecordsWorkspace} data-wilsy-contact-records="relationship-list-view">
        {renderFilterRail()}

        <section className={styles.contactRecordsPanel}>
          <header className={styles.contactRecordsHeader}>
            <span>
              <small>{activeView.label}</small>
              <strong>{filteredContacts.length} contacts</strong>
              <em>{selectedRowIds.length ? `${selectedRowIds.length} selected` : `${activeSort.label} order`}</em>
            </span>

            <div>
              {!filterRailOpen ? (
                <button type="button" onClick={() => setFilterRailOpen(true)}>
                  <Filter size={15} />
                  Filters
                </button>
              ) : null}
              <button type="button" onClick={onRefresh}>
                <RefreshCcw size={15} className={loading ? styles.spin : ''} />
                Refresh
              </button>
              <button type="button">
                <Download size={15} />
                Export
              </button>
            </div>
          </header>

          {selectedRowIds.length ? (
            <section className={styles.contactBulkActionBar} aria-label="Contact bulk actions">
              <strong>{selectedRowIds.length} selected</strong>
              <button type="button"><Mail size={14} />Mass Email</button>
              <button type="button"><Shield size={14} />Consent Review</button>
              <button type="button"><Building2 size={14} />Link Account</button>
              <button type="button" onClick={() => setSelectedRowIds([])}>Clear</button>
            </section>
          ) : null}

          <div className={styles.contactRecordsTableFrame}>
            <table className={styles.contactRecordsTable}>
              <thead>
                <tr>
                  <th>
                    <input
                      type="checkbox"
                      aria-label="Select all visible contacts"
                      checked={allRowsSelected}
                      onChange={handleToggleAllContactSelection}
                    />
                  </th>
                  <th>Contact Name</th>
                  <th>Account Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Title</th>
                  <th>Consent</th>
                  <th>Score</th>
                  <th>Owner</th>
                  <th aria-label="Row actions" />
                </tr>
              </thead>
              <tbody>
                {filteredContacts.length ? filteredContacts.map((record, index) => {
                  const recordId = resolveContactId(record, index);
                  const score = resolveContactScore(record);
                  const consent = resolveContactConsent(record);
                  const emailHref = resolveContactHref(record, 'email');
                  const phoneHref = resolveContactHref(record, 'phone');

                  return (
                    <tr key={recordId} data-selected={selectedRowIds.includes(recordId) ? 'true' : 'false'}>
                      <td>
                        <input
                          type="checkbox"
                          aria-label={`Select ${resolveContactValue(record, 'name')}`}
                          checked={selectedRowIds.includes(recordId)}
                          onChange={() => handleToggleContactSelection(recordId)}
                        />
                      </td>
                      <td>
                        <button type="button" className={styles.contactNameCell}>
                          <strong>{resolveContactValue(record, 'name')}</strong>
                          <em>{resolveContactStatus(record)} · {resolveContactSource(record)}</em>
                        </button>
                      </td>
                      <td>{resolveContactValue(record, 'accountName')}</td>
                      <td>
                        {emailHref ? <a href={emailHref}>{resolveContactValue(record, 'email')}</a> : resolveContactValue(record, 'email')}
                      </td>
                      <td>
                        {phoneHref ? <a href={phoneHref}>{resolveContactValue(record, 'phone')}</a> : resolveContactValue(record, 'phone')}
                      </td>
                      <td>{resolveContactValue(record, 'title')}</td>
                      <td>
                        <span className={styles[`contactStatus${consent}`] || styles.contactStatusPENDING}>
                          {consent}
                        </span>
                      </td>
                      <td>
                        <span className={styles.contactScorePill}>{resolveContactBand(score)} · {score}</span>
                      </td>
                      <td>{resolveContactValue(record, 'owner')}</td>
                      <td className={styles.contactRowActionsCell}>
                        <button type="button" onClick={() => setOpenRowActionId(openRowActionId === recordId ? '' : recordId)} title="Contact actions">
                          <MoreHorizontal size={17} />
                        </button>
                        {openRowActionId === recordId ? (
                          <section className={styles.contactRowActionMenu} aria-label="Contact actions">
                            <a href={emailHref || undefined} onClick={(event) => { if (!emailHref) event.preventDefault(); }}>Send Email</a>
                            <a href={phoneHref || undefined} onClick={(event) => { if (!phoneHref) event.preventDefault(); }}>Call Contact</a>
                            <button type="button">Consent Review</button>
                            <button type="button">Link Account</button>
                            <button type="button">Open Proof Trail</button>
                          </section>
                        ) : null}
                      </td>
                    </tr>
                  );
                }) : (
                  <tr className={styles.contactEmptyRow}>
                    <td colSpan={10}>
                      <section>
                        <Database size={34} />
                        <span>
                          <strong>No live contact records in this view yet.</strong>
                          <em>Sync relationship sources, import verified contacts, or create a governed contact. WILSY OS will surface consent, account linkage and proof posture as soon as records arrive.</em>
                        </span>
                        <div>
                          <button type="button" onClick={onRefresh} disabled={loading}>
                            <RefreshCcw size={15} />
                            Sync Sources
                          </button>
                          <button type="button" onClick={onCreate}>
                            <Plus size={15} />
                            Create Contact
                          </button>
                        </div>
                      </section>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <footer className={styles.contactRecordsFooter}>
            <span>Live Contacts {filteredContacts.length}</span>
            <strong>{filteredContacts.length ? `1 to ${filteredContacts.length}` : '0 to 0'}</strong>
          </footer>
        </section>
      </section>
    );
  }

  /**
   * @function renderRelationshipTab
   * @description Renders contact-account-deal relationship graph intelligence.
   * @returns {JSX.Element} Relationship tab.
   * @collaboration R76C Contacts relationship graph, account linkage, deal influence intelligence.
   */
  function renderRelationshipTab() {
    const linkedContacts = filteredContacts.filter(record => isKnownContactValue(resolveContactValue(record, 'accountName')));

    return (
      <section className={styles.contactTabSurface} data-contact-tab="relationships">
        <section className={styles.relationshipGrid}>
          <article className={styles.relationshipPanel}>
            <header>
              <small>Relationship Graph</small>
              <strong>{linkedContacts.length}/{filteredContacts.length} account-linked</strong>
            </header>
            <div className={styles.relationshipNodeGrid}>
              {filteredContacts.slice(0, 12).map((record, index) => (
                <span key={resolveContactId(record, index)} data-linked={isKnownContactValue(resolveContactValue(record, 'accountName')) ? 'true' : 'false'}>
                  <UserRound size={15} />
                  <em>{resolveContactValue(record, 'name')}</em>
                  <b>{resolveContactValue(record, 'accountName')}</b>
                </span>
              ))}
            </div>
          </article>

          <article className={styles.relationshipPanel}>
            <header>
              <small>Influence Posture</small>
              <strong>{deals.length || 0} deal links</strong>
            </header>
            <p>Contacts become operating graph nodes: account influence, deal motion, support posture, consent, and evidence all stay visible in one relationship cockpit.</p>
            <div className={styles.relationshipStats}>
              <span><Building2 size={16} />{accounts.length || 0} accounts</span>
              <span><GitBranch size={16} />{deals.length || 0} deals</span>
              <span><FileCheck2 size={16} />{evidence.length || 0} proof anchors</span>
            </div>
          </article>
        </section>
      </section>
    );
  }

  /**
   * @function renderConsentTab
   * @description Renders consent, communication readiness and compliance posture.
   * @returns {JSX.Element} Consent tab.
   * @collaboration R76C Contacts compliance HUD, POPIA/GDPR posture, communication authority.
   */
  function renderConsentTab() {
    const verified = filteredContacts.filter(record => resolveContactConsent(record) === 'VERIFIED').length;
    const pending = filteredContacts.filter(record => resolveContactConsent(record) === 'PENDING').length;
    const revoked = filteredContacts.filter(record => resolveContactConsent(record) === 'REVOKED').length;

    return (
      <section className={styles.contactTabSurface} data-contact-tab="consent">
        <section className={styles.consentGrid}>
          <article className={styles.consentPanel}>
            <Shield size={24} />
            <span>
              <small>Communication Authority</small>
              <strong>{verified}/{filteredContacts.length} verified</strong>
              <em>POPIA · GDPR · SOC2 contact communication posture.</em>
            </span>
          </article>
          <article className={styles.consentPanel}>
            <AlertTriangle size={24} />
            <span>
              <small>Review Queue</small>
              <strong>{pending} pending · {revoked} revoked</strong>
              <em>Contacts without clear consent stay visible before outreach.</em>
            </span>
          </article>
          <article className={styles.consentPanel}>
            <CheckCircle2 size={24} />
            <span>
              <small>Evidence Chain</small>
              <strong>{evidence.length || 0} anchors</strong>
              <em>Consent and source receipts belong to the contact graph.</em>
            </span>
          </article>
        </section>
      </section>
    );
  }

  /**
   * @function renderSourcesTab
   * @description Renders source route and connector posture for Contacts.
   * @returns {JSX.Element} Sources tab.
   * @collaboration R76C Contacts source proof, connector readiness, migration parity.
   */
  function renderSourcesTab() {
    return (
      <section className={styles.contactTabSurface} data-contact-tab="sources">
        <section className={styles.sourceGrid}>
          <article className={styles.sourcePanel}>
            <header>
              <small>Source Routes</small>
              <strong>{Number(sourcePosture.connected || 0)}/{Number(sourcePosture.total || connectors.length || 0)}</strong>
            </header>
            <p>{sourceErrors.length ? `${sourceErrors.length} source route gaps detected.` : 'Contacts source posture is monitored.'}</p>
            <button type="button" onClick={onRefresh}>
              <RefreshCcw size={15} />
              Sync Sources
            </button>
          </article>

          <article className={styles.sourcePanel}>
            <header>
              <small>Connector Matrix</small>
              <strong>{connectors.length || 0}</strong>
            </header>
            <div className={styles.connectorMatrix}>
              {connectors.length ? connectors.slice(0, 10).map((connector, index) => (
                <span key={connector.id || connector.key || connector.name || `connector-${index}`}>
                  <Network size={14} />
                  <em>{connector.label || connector.name || connector.key || 'Connector'}</em>
                  <b>{connector.status || connector.posture || 'WATCH'}</b>
                </span>
              )) : (
                <span>
                  <Network size={14} />
                  <em>No connector payload returned</em>
                  <b>GATED</b>
                </span>
              )}
            </div>
          </article>
        </section>
      </section>
    );
  }

  /**
   * @function renderTabContent
   * @description Resolves the active Contacts tab content.
   * @returns {JSX.Element} Active tab content.
   * @collaboration R76C Contacts tabbed workspace, Leads-grade operating principles, CRM OS consistency.
   */
  function renderTabContent() {
    if (activeTopTab === 'relationships') return renderRelationshipTab();
    if (activeTopTab === 'consent') return renderConsentTab();
    if (activeTopTab === 'sources') return renderSourcesTab();

    return renderRecordsTab();
  }

  return (
    <section
      className={styles.contactOperatingRoom}
      data-wilsy-crm-visual-contract="R78B-UNIFIED-CRM-SHELL"
      data-wilsy-contact-operating-room="R76C-CONTACTS-OPERATING-ROOM"
      data-wilsy-contact-module="relationship-intelligence"
      data-wilsy-contact-canvas-parity="LEADS_FULL_CANVAS_R76E"
    >
      <header className={styles.contactAppHeader}>
        <section className={styles.contactHeaderPrimary}>
          <span className={styles.contactTitleBlock}>
            <small>Customer Relationships</small>
            <strong>Contacts</strong>
            <em>{tenantLabel} · Relationship workspace · consent and source records monitored</em>
          </span>

          <section className={styles.contactHeaderUtilities}>
            <button type="button" className={styles.contactIconButton} onClick={onRefresh} aria-label="Refresh contacts">
              <RefreshCcw size={18} className={loading ? styles.spin : ''} />
            </button>
            <button type="button" className={styles.contactIconButton} aria-label="Open calendar">
              <CalendarDays size={18} />
            </button>
            <button type="button" className={styles.contactIconButton} aria-label="Contact settings">
              <SlidersHorizontal size={18} />
            </button>
            <button
              type="button"
              className={styles.contactThemeAuthority}
              onClick={onOpenThemeAuthority}
              aria-label={`Open global theme authority: ${globalThemeAuthorityLabel}`}
              data-wilsy-global-theme-authority-control="command-center"
            >
              <Sparkles size={17} />
              <span>
                <small>Theme Authority</small>
                <strong>{globalThemeAuthorityLabel}</strong>
                <em>{globalThemeAuthorityMode}</em>
              </span>
              <ChevronDown size={15} />
            </button>
          </section>
        </section>

        <section className={styles.contactCommandRow}>
          <label className={styles.contactSearch}>
            <Search size={19} />
            <input
              value={searchQuery}
              onChange={event => setSearchQuery(event.target.value)}
              placeholder="Search contacts, accounts, consent, email, phone"
              aria-label="Search contacts"
            />
            <kbd>⌘K</kbd>
          </label>

          <section className={styles.contactToolbar}>
            <div className={styles.contactListViewWrap}>
              <button type="button" className={styles.contactViewButton}>
                <Users size={17} />
                <span>
                  <strong>{activeView.label}</strong>
                  <em>{activeView.detail}</em>
                </span>
                <ChevronDown size={15} />
              </button>
              <section className={styles.contactDropdownMenu} aria-label="Contact list views">
                {CONTACT_LIST_VIEWS.map(view => (
                  <button
                    key={view.id}
                    type="button"
                    data-active={view.id === activeListView ? 'true' : 'false'}
                    onClick={() => setActiveListView(view.id)}
                  >
                    <span>{view.label}</span>
                    <em>{view.detail}</em>
                  </button>
                ))}
              </section>
            </div>

            <button type="button" data-active={filterRailOpen ? 'true' : 'false'} onClick={() => setFilterRailOpen(value => !value)}>
              <Filter size={17} />
              Filter
            </button>

            <div className={styles.contactSortWrap}>
              <button type="button" onClick={() => setSortMenuOpen(value => !value)}>
                <SlidersHorizontal size={17} />
                Sort
                <ChevronDown size={15} />
              </button>
              {sortMenuOpen ? (
                <section className={styles.contactDropdownMenu} aria-label="Contact sort options">
                  {CONTACT_SORT_OPTIONS.map(option => (
                    <button
                      key={option.id}
                      type="button"
                      data-active={option.id === sortMode ? 'true' : 'false'}
                      onClick={() => {
                        setSortMode(option.id);
                        setSortMenuOpen(false);
                      }}
                    >
                      <span>{option.label}</span>
                    </button>
                  ))}
                </section>
              ) : null}
            </div>

            <button type="button" className={styles.contactPrimaryAction} onClick={onCreate}>
              <Plus size={17} />
              Create Contact
            </button>
          </section>
        </section>

        <section className={styles.contactTabBar}>
          <div className={styles.contactTabs}>
            {CONTACT_TOP_TABS.map(tab => {
              const Icon = tab.icon;

              return (
                <button
                  key={tab.id}
                  type="button"
                  data-active={activeTopTab === tab.id ? 'true' : 'false'}
                  onClick={() => setActiveTopTab(tab.id)}
                >
                  <Icon size={16} />
                  {tab.label}
                </button>
              );
            })}
          </div>

          <section className={styles.contactInvestorStrip}>
            <article>
              <small>Source Routes</small>
              <strong>{Number(sourcePosture.connected || 0)}/{Number(sourcePosture.total || connectors.length || 0)}</strong>
              <em>Source readiness</em>
            </article>
            <article>
              <small>Relationship Root</small>
              <strong>{String(sourcePosture.rootHash || sourcePosture.hash || 'UNSEALED').slice(0, 12)}</strong>
              <em>PROVENANCE</em>
            </article>
            <article>
              <small>Consent</small>
              <strong>{filteredContacts.filter(record => resolveContactConsent(record) === 'VERIFIED').length}/{filteredContacts.length}</strong>
              <em>POPIA · GDPR · SOC2</em>
            </article>
            <article>
              <small>Graph Authority</small>
              <strong>{accounts.length || deals.length ? 'ONLINE' : 'WATCH'}</strong>
              <em>ACCOUNT · DEAL · PROOF</em>
            </article>
          </section>
        </section>
      </header>

      {renderContactMetrics()}
      {sourceErrors.length ? (
        <section className={styles.contactSourceWarning}>
          <AlertTriangle size={18} />
          <span>{sourceErrors.length} source route{sourceErrors.length === 1 ? '' : 's'} unavailable. Showing received contacts only.</span>
        </section>
      ) : null}
      {renderTabContent()}
    </section>
  );
}
