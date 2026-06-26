/* eslint-disable */
import React, { useMemo, useState } from 'react';
import {
  AlertTriangle,
  Banknote,
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
  Target,
  Users,
} from 'lucide-react';
import styles from './WilsyAccountOperatingRoom.module.css';

const ACCOUNT_LIST_VIEWS = Object.freeze([
  { id: 'ALL_ACCOUNTS', label: 'All Accounts', detail: 'Every source-backed organization' },
  { id: 'CUSTOMER_READY', label: 'Customer Ready', detail: 'Active account relationships' },
  { id: 'REVENUE_LINKED', label: 'Revenue Linked', detail: 'Accounts connected to deal motion' },
  { id: 'ACTION_REQUIRED', label: 'Action Required', detail: 'Missing proof, owner, or account posture' },
]);

const ACCOUNT_TOP_TABS = Object.freeze([
  { id: 'records', label: 'Records', icon: Building2 },
  { id: 'relationships', label: 'Relationships', icon: GitBranch },
  { id: 'revenue', label: 'Revenue', icon: Banknote },
  { id: 'sources', label: 'Sources', icon: Network },
]);

const ACCOUNT_SORT_OPTIONS = Object.freeze([
  { id: 'authority', label: 'Authority score' },
  { id: 'name', label: 'Account name' },
  { id: 'industry', label: 'Industry' },
  { id: 'activity', label: 'Latest activity' },
]);

const ACCOUNT_FILTER_GROUPS = Object.freeze([
  {
    id: 'system',
    label: 'System Defined Filters',
    options: Object.freeze([
      'Active Customers',
      'No Owner',
      'Revenue Linked',
      'Missing Industry',
      'Recently Touched',
      'Dormant Accounts',
    ]),
  },
  {
    id: 'authority',
    label: 'Authority Signals',
    options: Object.freeze([
      'Account Verified',
      'Proof Pending',
      'Deal Influence',
      'Contact Graph Ready',
      'Customer Success Watch',
    ]),
  },
]);

/**
 * @function resolveAccountId
 * @description Resolves a stable account id from flexible CRM account payloads.
 * @param {Object} record - Account record.
 * @param {number} index - Fallback index.
 * @returns {string} Stable account id.
 * @collaboration R77A Accounts Operating Room, live CRM source records, row selection.
 */
function resolveAccountId(record = {}, index = 0) {
  return String(record._id || record.id || record.uuid || record.recordId || record.accountId || record.name || `account-${index}`);
}

/**
 * @function resolveAccountValue
 * @description Resolves normalized account field values from live CRM payloads.
 * @param {Object} record - Account record.
 * @param {string} field - Field name.
 * @returns {string} Display value.
 * @collaboration R77A Accounts Operating Room, source-flexible CRM data, Zoho coverage parity.
 */
function resolveAccountValue(record = {}, field = '') {
  const values = {
    name: record.name || record.accountName || record.company || record.companyName || record.organization,
    industry: record.industry || record.sector || record.vertical || record.category,
    owner: record.owner || record.ownerName || record.assignedTo || record.createdBy,
    status: record.status || record.lifecycleStage || record.accountStatus || record.customerStatus,
    source: record.source || record.sourceSystem || record.connector || record.origin || record.channel,
    website: record.website || record.domain || record.url,
    phone: record.phone || record.mainPhone || record.telephone || record.officePhone,
    email: record.email || record.billingEmail || record.primaryEmail || record.contactEmail,
    revenue: record.annualRevenue || record.revenue || record.value || record.amount || record.arr || record.mrr,
    employees: record.employees || record.employeeCount || record.headcount || record.size,
    country: record.country || record.region || record.billingCountry,
    city: record.city || record.billingCity,
    lastActivity: record.lastActivity || record.lastTouchedAt || record.lastContactedAt || record.updatedAt || record.createdAt,
    provenanceHash: record.provenanceHash || record.cryptographicHash || record.rootHash || record.sealHash,
  };

  return String(values[field] || '—').trim() || '—';
}

/**
 * @function isKnownAccountValue
 * @description Determines whether an account field value is meaningful.
 * @param {string} value - Candidate display value.
 * @returns {boolean} True when value is known.
 * @collaboration R77A account quality scoring, authority posture, source proof readiness.
 */
function isKnownAccountValue(value = '') {
  const text = String(value || '').trim();
  return Boolean(text && text !== '—' && text !== 'UNSEALED' && text.toUpperCase() !== 'NONE');
}

/**
 * @function resolveAccountStatus
 * @description Resolves account operating status.
 * @param {Object} record - Account record.
 * @returns {string} Status label.
 * @collaboration R77A account cockpit, customer lifecycle posture, source-compatible CRM payloads.
 */
function resolveAccountStatus(record = {}) {
  const raw = resolveAccountValue(record, 'status').toUpperCase();

  if (raw.includes('ACTIVE') || raw.includes('CUSTOMER') || raw.includes('OPEN')) return 'ACTIVE';
  if (raw.includes('RISK') || raw.includes('ESCALATED')) return 'AT_RISK';
  if (raw.includes('INACTIVE') || raw.includes('LOST') || raw.includes('ARCHIVED')) return 'INACTIVE';

  return 'NEW';
}

/**
 * @function resolveAccountSource
 * @description Resolves account source label.
 * @param {Object} record - Account record.
 * @returns {string} Source label.
 * @collaboration R77A source route proof, account provenance, live CRM source registry.
 */
function resolveAccountSource(record = {}) {
  const source = resolveAccountValue(record, 'source');
  return source === '—' ? 'Backend CRM' : source;
}

/**
 * @function resolveAccountScore
 * @description Calculates account authority readiness from proof, owner, business fields and revenue linkage.
 * @param {Object} record - Account record.
 * @returns {number} Account authority score.
 * @collaboration R77A account intelligence, customer graph, proof and revenue posture.
 */
function resolveAccountScore(record = {}) {
  const hasName = isKnownAccountValue(resolveAccountValue(record, 'name'));
  const hasIndustry = isKnownAccountValue(resolveAccountValue(record, 'industry'));
  const hasOwner = isKnownAccountValue(resolveAccountValue(record, 'owner'));
  const hasPhone = isKnownAccountValue(resolveAccountValue(record, 'phone'));
  const hasEmail = isKnownAccountValue(resolveAccountValue(record, 'email'));
  const hasWebsite = isKnownAccountValue(resolveAccountValue(record, 'website'));
  const hasProof = isKnownAccountValue(resolveAccountValue(record, 'provenanceHash'));
  const hasRevenue = isKnownAccountValue(resolveAccountValue(record, 'revenue'));
  const status = resolveAccountStatus(record);

  const fieldScore = [hasName, hasIndustry, hasOwner, hasPhone, hasEmail, hasWebsite].filter(Boolean).length * 9;
  const proofScore = hasProof ? 18 : 0;
  const revenueScore = hasRevenue ? 14 : 0;
  const statusScore = status === 'ACTIVE' ? 14 : status === 'AT_RISK' ? 8 : status === 'INACTIVE' ? 0 : 6;

  return Math.max(0, Math.min(100, fieldScore + proofScore + revenueScore + statusScore));
}

/**
 * @function resolveAccountBand
 * @description Converts account authority score to a readable band.
 * @param {number} score - Account authority score.
 * @returns {string} Authority band.
 * @collaboration R77A Accounts table, executive account prioritization, CRM command cockpit.
 */
function resolveAccountBand(score = 0) {
  if (score >= 78) return 'Authority Ready';
  if (score >= 54) return 'Commercial Warm';
  if (score >= 28) return 'Needs Proof';
  return 'Unqualified';
}

/**
 * @function resolveAccountHref
 * @description Builds safe account quick action links.
 * @param {Object} record - Account record.
 * @param {string} channel - Action channel.
 * @returns {string|null} Account action href or null.
 * @collaboration R77A account outreach, browser-safe communication links, table quick actions.
 */
function resolveAccountHref(record = {}, channel = 'email') {
  if (channel === 'email') {
    const email = resolveAccountValue(record, 'email');
    return isKnownAccountValue(email) ? `mailto:${email}` : null;
  }

  if (channel === 'website') {
    const website = resolveAccountValue(record, 'website');
    if (!isKnownAccountValue(website)) return null;
    return /^https?:\/\//i.test(website) ? website : `https://${website}`;
  }

  const phone = resolveAccountValue(record, 'phone');
  const normalizedPhone = String(phone || '').replace(/[^\d+]/g, '');
  return isKnownAccountValue(phone) && normalizedPhone ? `tel:${normalizedPhone}` : null;
}

/**
 * @function filterAccountByView
 * @description Applies the active account list view to a record.
 * @param {Object} record - Account record.
 * @param {string} listViewId - Active view id.
 * @returns {boolean} True when record matches.
 * @collaboration R77A account view rail, customer operations, source-backed filtering.
 */
function filterAccountByView(record = {}, listViewId = 'ALL_ACCOUNTS') {
  if (listViewId === 'CUSTOMER_READY') return resolveAccountStatus(record) === 'ACTIVE';
  if (listViewId === 'REVENUE_LINKED') return isKnownAccountValue(resolveAccountValue(record, 'revenue'));
  if (listViewId === 'ACTION_REQUIRED') {
    return !isKnownAccountValue(resolveAccountValue(record, 'owner'))
      || !isKnownAccountValue(resolveAccountValue(record, 'industry'))
      || !isKnownAccountValue(resolveAccountValue(record, 'provenanceHash'));
  }

  return true;
}

/**
 * @function sortAccountRecords
 * @description Sorts account records for the active operator sort mode.
 * @param {Array<Object>} records - Account records.
 * @param {string} sortMode - Sort mode.
 * @returns {Array<Object>} Sorted records.
 * @collaboration R77A Accounts sort deck, operating cockpit, enterprise CRM parity.
 */
function sortAccountRecords(records = [], sortMode = 'authority') {
  const sortedRecords = [...records];

  return sortedRecords.sort((leftRecord, rightRecord) => {
    if (sortMode === 'name') {
      return resolveAccountValue(leftRecord, 'name').localeCompare(resolveAccountValue(rightRecord, 'name'));
    }

    if (sortMode === 'industry') {
      return resolveAccountValue(leftRecord, 'industry').localeCompare(resolveAccountValue(rightRecord, 'industry'));
    }

    if (sortMode === 'activity') {
      const leftDate = Date.parse(resolveAccountValue(leftRecord, 'lastActivity')) || 0;
      const rightDate = Date.parse(resolveAccountValue(rightRecord, 'lastActivity')) || 0;
      return rightDate - leftDate;
    }

    return resolveAccountScore(rightRecord) - resolveAccountScore(leftRecord);
  });
}

/**
 * @function buildAccountMetrics
 * @description Builds Accounts operating metrics from live CRM records and source posture.
 * @param {Object} params - Metric inputs.
 * @returns {Array<Object>} Metric cards.
 * @collaboration R77A Accounts cockpit, source truth, revenue and graph telemetry.
 */
function buildAccountMetrics({
  accounts = [],
  contacts = [],
  deals = [],
  evidence = [],
  sourcePosture = {},
} = {}) {
  const activeAccounts = accounts.filter(record => resolveAccountStatus(record) === 'ACTIVE').length;
  const revenueLinked = accounts.filter(record => isKnownAccountValue(resolveAccountValue(record, 'revenue'))).length;
  const authorityReady = accounts.filter(record => resolveAccountScore(record) >= 54).length;
  const connectedRoutes = Number(sourcePosture.connected || sourcePosture.connectedRoutes || 0);

  return [
    {
      id: 'accounts',
      label: 'Account Graph',
      value: String(accounts.length),
      detail: accounts.length ? 'Source-backed organizations available' : 'No accounts returned yet',
      progress: accounts.length ? Math.round((authorityReady / Math.max(1, accounts.length)) * 100) : 0,
      icon: Building2,
    },
    {
      id: 'customers',
      label: 'Customer Readiness',
      value: `${activeAccounts}/${accounts.length || 0}`,
      detail: 'Active customer and operating account posture',
      progress: accounts.length ? Math.round((activeAccounts / Math.max(1, accounts.length)) * 100) : 0,
      icon: CheckCircle2,
    },
    {
      id: 'relationships',
      label: 'Relationship Linkage',
      value: String(contacts.length || deals.length || 0),
      detail: `${contacts.length || 0} contacts · ${deals.length || 0} deal records`,
      progress: Math.min(100, Math.max(0, contacts.length * 5 + deals.length * 9)),
      icon: GitBranch,
    },
    {
      id: 'proof',
      label: 'Proof Surface',
      value: String(evidence.length || connectedRoutes),
      detail: evidence.length ? 'Evidence anchors available' : 'Awaiting sealed account proof',
      progress: Math.min(100, Math.max(0, evidence.length * 12 + connectedRoutes * 8)),
      icon: FileCheck2,
    },
  ];
}

/**
 * @function WilsyAccountOperatingRoom
 * @description Renders the sovereign Accounts operating room for organization intelligence, revenue posture and proof.
 * @param {Object} props - Component props.
 * @returns {JSX.Element} Accounts operating room.
 * @collaboration R77A Accounts module, CRMDashboard route ownership, Wilsy OS CRM uniformity.
 */
export default function WilsyAccountOperatingRoom({
  accounts = [],
  contacts = [],
  deals = [],
  evidence = [],
  connectors = [],
  sourcePosture = {},
  sourceErrors = [],
  loading = false,
  tenantConfig = {},
  user = {},
  onRefresh = () => {},
  onCreate = () => {},
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTopTab, setActiveTopTab] = useState('records');
  const [activeListView, setActiveListView] = useState('ALL_ACCOUNTS');
  const [sortMode, setSortMode] = useState('authority');
  const [sortMenuOpen, setSortMenuOpen] = useState(false);
  const [selectedRowIds, setSelectedRowIds] = useState([]);
  const [openRowActionId, setOpenRowActionId] = useState('');
  const [filterRailOpen, setFilterRailOpen] = useState(true);

  const normalizedAccounts = Array.isArray(accounts) ? accounts : [];
  const activeView = ACCOUNT_LIST_VIEWS.find(view => view.id === activeListView) || ACCOUNT_LIST_VIEWS[0];
  const activeSort = ACCOUNT_SORT_OPTIONS.find(option => option.id === sortMode) || ACCOUNT_SORT_OPTIONS[0];
  const tenantLabel = tenantConfig?.legalName || tenantConfig?.name || tenantConfig?.tenantName || 'Wilsy OS Root';
  const role = String(user?.role || user?.accountRole || tenantConfig?.role || 'ACCOUNT_OPERATOR').toUpperCase();

  const filteredAccounts = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    return sortAccountRecords(
      normalizedAccounts.filter((record) => {
        if (!filterAccountByView(record, activeListView)) return false;

        if (!query) return true;

        return [
          'name',
          'industry',
          'owner',
          'status',
          'source',
          'website',
          'phone',
          'email',
          'country',
          'city',
        ].some(field => resolveAccountValue(record, field).toLowerCase().includes(query));
      }),
      sortMode
    );
  }, [activeListView, normalizedAccounts, searchQuery, sortMode]);

  const accountMetrics = useMemo(() => buildAccountMetrics({
    accounts: normalizedAccounts,
    contacts,
    deals,
    evidence,
    sourcePosture,
  }), [contacts, deals, evidence, normalizedAccounts, sourcePosture]);

  const visibleIds = filteredAccounts.map((record, index) => resolveAccountId(record, index));
  const allRowsSelected = visibleIds.length > 0 && visibleIds.every(recordId => selectedRowIds.includes(recordId));

  /**
   * @function handleToggleAllAccountSelection
   * @description Toggles selection for every visible account row.
   * @collaboration R77A Accounts table, bulk account operations, operator list control.
   */
  function handleToggleAllAccountSelection() {
    if (allRowsSelected) {
      setSelectedRowIds([]);
      return;
    }

    setSelectedRowIds(visibleIds);
  }

  /**
   * @function handleToggleAccountSelection
   * @description Toggles one account row selection.
   * @param {string} recordId - Account record id.
   * @collaboration R77A Accounts table, row action state, bulk account operations.
   */
  function handleToggleAccountSelection(recordId) {
    setSelectedRowIds(previous => (
      previous.includes(recordId)
        ? previous.filter(value => value !== recordId)
        : [...previous, recordId]
    ));
  }

  /**
   * @function renderAccountMetrics
   * @description Renders account graph, customer readiness, relationship linkage and proof metrics.
   * @returns {JSX.Element} Account metrics deck.
   * @collaboration R77A Accounts command surface, Wilsy OS operating metrics, source proof.
   */
  function renderAccountMetrics() {
    return (
      <section className={styles.accountMetricDeck} aria-label="Accounts operating metrics">
        {accountMetrics.map((metric) => {
          const Icon = metric.icon;

          return (
            <article key={metric.id}>
              <span className={styles.accountMetricIcon}>
                <Icon size={20} />
              </span>
              <span className={styles.accountMetricCopy}>
                <small>{metric.label}</small>
                <strong>{metric.value}</strong>
                <em>{metric.detail}</em>
              </span>
              <i className={styles.accountMetricBar}>
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
   * @description Renders Accounts list views and authority filters.
   * @returns {JSX.Element|null} Filter rail.
   * @collaboration R77A Accounts filtering, enterprise CRM parity, Wilsy account intelligence.
   */
  function renderFilterRail() {
    if (!filterRailOpen) return null;

    return (
      <aside className={styles.accountFilterRail} aria-label="Account filters">
        <header>
          <span>
            <small>Filter Accounts by</small>
            <strong>Authority Signals</strong>
          </span>
          <button type="button" onClick={(event) => event.currentTarget.blur()} aria-label="Filter options">
            <MoreHorizontal size={17} />
          </button>
        </header>

        <label className={styles.accountFilterSearch}>
          <Search size={18} />
          <input
            value={searchQuery}
            onChange={event => setSearchQuery(event.target.value)}
            placeholder="Search filters"
            aria-label="Search account filters"
          />
        </label>

        {ACCOUNT_FILTER_GROUPS.map(group => (
          <section key={group.id} className={styles.accountFilterGroup}>
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
   * @description Renders the source-backed Accounts records cockpit.
   * @returns {JSX.Element} Records tab.
   * @collaboration R77A Accounts list cockpit, authority-aware rows, source-honest empty state.
   */
  function renderRecordsTab() {
    return (
      <section className={styles.accountRecordsWorkspace} data-wilsy-account-records="organization-list-view">
        {renderFilterRail()}

        <section className={styles.accountRecordsPanel}>
          <header className={styles.accountRecordsHeader}>
            <span>
              <small>{activeView.label}</small>
              <strong>{filteredAccounts.length} accounts</strong>
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
            <section className={styles.accountBulkActionBar} aria-label="Account bulk actions">
              <strong>{selectedRowIds.length} selected</strong>
              <button type="button"><Mail size={14} />Mass Email</button>
              <button type="button"><Users size={14} />Assign Owner</button>
              <button type="button"><Shield size={14} />Proof Review</button>
              <button type="button" onClick={() => setSelectedRowIds([])}>Clear</button>
            </section>
          ) : null}

          <div className={styles.accountRecordsTableFrame}>
            <table className={styles.accountRecordsTable}>
              <thead>
                <tr>
                  <th>
                    <input
                      type="checkbox"
                      aria-label="Select all visible accounts"
                      checked={allRowsSelected}
                      onChange={handleToggleAllAccountSelection}
                    />
                  </th>
                  <th>Account Name</th>
                  <th>Industry</th>
                  <th>Owner</th>
                  <th>Status</th>
                  <th>Phone</th>
                  <th>Email</th>
                  <th>Source</th>
                  <th>Score</th>
                  <th aria-label="Row actions" />
                </tr>
              </thead>
              <tbody>
                {filteredAccounts.length ? filteredAccounts.map((record, index) => {
                  const recordId = resolveAccountId(record, index);
                  const score = resolveAccountScore(record);
                  const status = resolveAccountStatus(record);
                  const emailHref = resolveAccountHref(record, 'email');
                  const phoneHref = resolveAccountHref(record, 'phone');
                  const websiteHref = resolveAccountHref(record, 'website');

                  return (
                    <tr key={recordId} data-selected={selectedRowIds.includes(recordId) ? 'true' : 'false'}>
                      <td>
                        <input
                          type="checkbox"
                          aria-label={`Select ${resolveAccountValue(record, 'name')}`}
                          checked={selectedRowIds.includes(recordId)}
                          onChange={() => handleToggleAccountSelection(recordId)}
                        />
                      </td>
                      <td>
                        <a
                          className={styles.accountNameCell}
                          href={websiteHref || undefined}
                          onClick={(event) => { if (!websiteHref) event.preventDefault(); }}
                        >
                          <strong>{resolveAccountValue(record, 'name')}</strong>
                          <em>{resolveAccountSource(record)}</em>
                        </a>
                      </td>
                      <td>{resolveAccountValue(record, 'industry')}</td>
                      <td>{resolveAccountValue(record, 'owner')}</td>
                      <td>
                        <span className={styles[`accountStatus${status}`] || styles.accountStatusNEW}>
                          {status}
                        </span>
                      </td>
                      <td>
                        {phoneHref ? <a href={phoneHref}>{resolveAccountValue(record, 'phone')}</a> : resolveAccountValue(record, 'phone')}
                      </td>
                      <td>
                        {emailHref ? <a href={emailHref}>{resolveAccountValue(record, 'email')}</a> : resolveAccountValue(record, 'email')}
                      </td>
                      <td>{resolveAccountSource(record)}</td>
                      <td>
                        <span className={styles.accountScorePill}>{resolveAccountBand(score)} · {score}</span>
                      </td>
                      <td className={styles.accountRowActionsCell}>
                        <button type="button" onClick={() => setOpenRowActionId(openRowActionId === recordId ? '' : recordId)} title="Account actions">
                          <MoreHorizontal size={17} />
                        </button>
                        {openRowActionId === recordId ? (
                          <section className={styles.accountRowActionMenu} aria-label="Account actions">
                            <a href={emailHref || undefined} onClick={(event) => { if (!emailHref) event.preventDefault(); }}>Email Account</a>
                            <a href={phoneHref || undefined} onClick={(event) => { if (!phoneHref) event.preventDefault(); }}>Call Account</a>
                            <button type="button">Link Contacts</button>
                            <button type="button">Open Deals</button>
                            <button type="button">Proof Trail</button>
                          </section>
                        ) : null}
                      </td>
                    </tr>
                  );
                }) : (
                  <tr className={styles.accountEmptyRow}>
                    <td colSpan={10}>
                      <section>
                        <Database size={34} />
                        <span>
                          <strong>No live account records in this view yet.</strong>
                          <em>Sync organization sources, import verified accounts, or create a governed account. WILSY OS will surface ownership, revenue linkage and proof posture as soon as records arrive.</em>
                        </span>
                        <div>
                          <button type="button" onClick={onRefresh} disabled={loading}>
                            <RefreshCcw size={15} />
                            Sync Sources
                          </button>
                          <button type="button" onClick={onCreate}>
                            <Plus size={15} />
                            Create Account
                          </button>
                        </div>
                      </section>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <footer className={styles.accountRecordsFooter}>
            <span>Live Accounts {filteredAccounts.length}</span>
            <strong>{filteredAccounts.length ? `1 to ${filteredAccounts.length}` : '0 to 0'}</strong>
          </footer>
        </section>
      </section>
    );
  }

  /**
   * @function renderRelationshipTab
   * @description Renders account-contact-deal relationship graph intelligence.
   * @returns {JSX.Element} Relationship tab.
   * @collaboration R77A Accounts relationship graph, contact linkage, deal influence intelligence.
   */
  function renderRelationshipTab() {
    return (
      <section className={styles.accountTabSurface} data-account-tab="relationships">
        <section className={styles.relationshipGrid}>
          <article className={styles.relationshipPanel}>
            <header>
              <small>Account Graph</small>
              <strong>{contacts.length} contacts · {deals.length} deals</strong>
            </header>
            <div className={styles.relationshipNodeGrid}>
              {filteredAccounts.slice(0, 12).map((record, index) => (
                <span key={resolveAccountId(record, index)} data-linked={resolveAccountScore(record) >= 54 ? 'true' : 'false'}>
                  <Building2 size={15} />
                  <em>{resolveAccountValue(record, 'name')}</em>
                  <b>{resolveAccountValue(record, 'industry')}</b>
                </span>
              ))}
            </div>
          </article>

          <article className={styles.relationshipPanel}>
            <header>
              <small>Influence Posture</small>
              <strong>{deals.length || 0} deal links</strong>
            </header>
            <p>Accounts become the commercial spine: contacts, deals, tasks, meetings, consent, revenue posture and evidence all attach to one governed organization graph.</p>
            <div className={styles.relationshipStats}>
              <span><Users size={16} />{contacts.length || 0} contacts</span>
              <span><Target size={16} />{deals.length || 0} deals</span>
              <span><FileCheck2 size={16} />{evidence.length || 0} proof anchors</span>
            </div>
          </article>
        </section>
      </section>
    );
  }

  /**
   * @function renderRevenueTab
   * @description Renders account revenue and customer readiness posture.
   * @returns {JSX.Element} Revenue tab.
   * @collaboration R77A Accounts revenue HUD, customer success posture, operating account intelligence.
   */
  function renderRevenueTab() {
    const revenueLinked = filteredAccounts.filter(record => isKnownAccountValue(resolveAccountValue(record, 'revenue'))).length;
    const activeAccounts = filteredAccounts.filter(record => resolveAccountStatus(record) === 'ACTIVE').length;
    const atRiskAccounts = filteredAccounts.filter(record => resolveAccountStatus(record) === 'AT_RISK').length;

    return (
      <section className={styles.accountTabSurface} data-account-tab="revenue">
        <section className={styles.revenueGrid}>
          <article className={styles.revenuePanel}>
            <Banknote size={24} />
            <span>
              <small>Revenue Linkage</small>
              <strong>{revenueLinked}/{filteredAccounts.length} linked</strong>
              <em>ARR, MRR, pipeline value and account commercial posture.</em>
            </span>
          </article>
          <article className={styles.revenuePanel}>
            <CheckCircle2 size={24} />
            <span>
              <small>Customer Motion</small>
              <strong>{activeAccounts} active · {atRiskAccounts} at risk</strong>
              <em>Customer success and account ownership remain visible before executive review.</em>
            </span>
          </article>
          <article className={styles.revenuePanel}>
            <FileCheck2 size={24} />
            <span>
              <small>Evidence Chain</small>
              <strong>{evidence.length || 0} anchors</strong>
              <em>Account proof, contract, consent and source receipts belong to the account graph.</em>
            </span>
          </article>
        </section>
      </section>
    );
  }

  /**
   * @function renderSourcesTab
   * @description Renders source route and connector posture for Accounts.
   * @returns {JSX.Element} Sources tab.
   * @collaboration R77A Accounts source proof, connector readiness, migration parity.
   */
  function renderSourcesTab() {
    return (
      <section className={styles.accountTabSurface} data-account-tab="sources">
        <section className={styles.sourceGrid}>
          <article className={styles.sourcePanel}>
            <header>
              <small>Source Routes</small>
              <strong>{Number(sourcePosture.connected || 0)}/{Number(sourcePosture.total || connectors.length || 0)}</strong>
            </header>
            <p>{sourceErrors.length ? `${sourceErrors.length} source route gaps detected.` : 'Accounts source posture is monitored.'}</p>
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
   * @description Resolves the active Accounts tab content.
   * @returns {JSX.Element} Active tab content.
   * @collaboration R77A Accounts tabbed workspace, Leads/Contacts operating principles, CRM OS uniformity.
   */
  function renderTabContent() {
    if (activeTopTab === 'relationships') return renderRelationshipTab();
    if (activeTopTab === 'revenue') return renderRevenueTab();
    if (activeTopTab === 'sources') return renderSourcesTab();

    return renderRecordsTab();
  }

  return (
    <section
      className={styles.accountOperatingRoom}
      data-wilsy-crm-visual-contract="R78B-UNIFIED-CRM-SHELL"
      data-wilsy-account-operating-room="R77A-ACCOUNTS-OPERATING-ROOM"
      data-wilsy-account-module="organization-intelligence"
      data-wilsy-account-canvas-parity="LEADS_CONTACTS_FULL_CANVAS"
    >
      <header className={styles.accountAppHeader}>
        <section className={styles.accountHeaderPrimary}>
          <span className={styles.accountTitleBlock}>
            <small>Customer Accounts</small>
            <strong>Accounts</strong>
            <em>{tenantLabel} · Account workspace · ownership and source records monitored</em>
          </span>

          <section className={styles.accountHeaderUtilities}>
            <button type="button" className={styles.accountIconButton} onClick={onRefresh} aria-label="Refresh accounts">
              <RefreshCcw size={18} className={loading ? styles.spin : ''} />
            </button>
            <button type="button" className={styles.accountIconButton} aria-label="Open calendar">
              <CalendarDays size={18} />
            </button>
            <button type="button" className={styles.accountIconButton} aria-label="Account settings">
              <SlidersHorizontal size={18} />
            </button>
            <button type="button" className={styles.accountThemeAuthority}>
              <Sparkles size={17} />
              <span>
                <small>Theme</small>
                <strong>Authority</strong>
              </span>
              <ChevronDown size={15} />
            </button>
          </section>
        </section>

        <section className={styles.accountCommandRow}>
          <label className={styles.accountSearch}>
            <Search size={19} />
            <input
              value={searchQuery}
              onChange={event => setSearchQuery(event.target.value)}
              placeholder="Search accounts, owners, industries, proof, revenue"
              aria-label="Search accounts"
            />
            <kbd>⌘K</kbd>
          </label>

          <section className={styles.accountToolbar}>
            <div className={styles.accountListViewWrap}>
              <button type="button" className={styles.accountViewButton}>
                <Building2 size={17} />
                <span>
                  <strong>{activeView.label}</strong>
                  <em>{activeView.detail}</em>
                </span>
                <ChevronDown size={15} />
              </button>
              <section className={styles.accountDropdownMenu} aria-label="Account list views">
                {ACCOUNT_LIST_VIEWS.map(view => (
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

            <div className={styles.accountSortWrap}>
              <button type="button" onClick={() => setSortMenuOpen(value => !value)}>
                <SlidersHorizontal size={17} />
                Sort
                <ChevronDown size={15} />
              </button>
              {sortMenuOpen ? (
                <section className={styles.accountDropdownMenu} aria-label="Account sort options">
                  {ACCOUNT_SORT_OPTIONS.map(option => (
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

            <button type="button" className={styles.accountPrimaryAction} onClick={onCreate}>
              <Plus size={17} />
              Create Account
            </button>
          </section>
        </section>

        <section className={styles.accountTabBar}>
          <div className={styles.accountTabs}>
            {ACCOUNT_TOP_TABS.map(tab => {
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

          <section className={styles.accountInvestorStrip}>
            <article>
              <small>Source Routes</small>
              <strong>{Number(sourcePosture.connected || 0)}/{Number(sourcePosture.total || connectors.length || 0)}</strong>
              <em>Source readiness</em>
            </article>
            <article>
              <small>Organization Root</small>
              <strong>{String(sourcePosture.rootHash || sourcePosture.hash || 'UNSEALED').slice(0, 12)}</strong>
              <em>PROVENANCE</em>
            </article>
            <article>
              <small>Customer Motion</small>
              <strong>{filteredAccounts.filter(record => resolveAccountStatus(record) === 'ACTIVE').length}/{filteredAccounts.length}</strong>
              <em>ACTIVE · RISK · OWNERSHIP</em>
            </article>
            <article>
              <small>Graph Authority</small>
              <strong>{contacts.length || deals.length ? 'ONLINE' : 'WATCH'}</strong>
              <em>CONTACT · DEAL · PROOF</em>
            </article>
          </section>
        </section>
      </header>

      {renderAccountMetrics()}
      {sourceErrors.length ? (
        <section className={styles.accountSourceWarning}>
          <AlertTriangle size={18} />
          <span>{sourceErrors.length} source route{sourceErrors.length === 1 ? '' : 's'} unavailable. Showing received accounts only.</span>
        </section>
      ) : null}
      {renderTabContent()}
    </section>
  );
}
