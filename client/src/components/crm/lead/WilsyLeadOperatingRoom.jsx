/* eslint-disable */
import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Activity,
  CalendarDays,
  CheckCircle2,
  ClipboardList,
  Command,
  Database,
  Download,
  FileInput,
  Filter,
  Fingerprint,
  LayoutPanelTop,
  Mail,
  MoreHorizontal,
  Phone,
  Plus,
  RotateCw,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  SplitSquareHorizontal,
  Upload,
  UserRoundCog,
  WandSparkles
} from 'lucide-react';
import { WILSY_CRM_THEME_ENGINE_BRIDGE_VERSION, resolveCrmThemeEngineOptions } from '../theme/wilsyCrmThemeEngineBridge.js';
import styles from './WilsyLeadOperatingRoom.module.css';

const WILSY_LEAD_OPERATING_ROOM_VERSION = 'R67D-SOVEREIGN-HEADER-COMMAND-BRIDGE';

const WILSY_LEAD_THEME_AUTHORITY = 'CRM_THEME_ENGINE_BRIDGE';

const EMPTY_LEAD_DRAFT = Object.freeze({
  name: '',
  company: '',
  email: '',
  phone: '',
  mobile: '',
  title: '',
  source: 'Website',
  status: 'NEW',
  industry: '',
  owner: '',
  rating: 'Warm',
  employees: '',
  website: '',
  annualRevenue: '',
  street: '',
  city: '',
  state: '',
  zipCode: '',
  country: '',
  description: ''
});

const REQUIRED_LEAD_FIELDS = Object.freeze(['name', 'company', 'email']);

const LEAD_COLUMNS = Object.freeze([
  { key: 'name', label: 'Lead Name' },
  { key: 'company', label: 'Company' },
  { key: 'email', label: 'Email' },
  { key: 'phone', label: 'Phone' },
  { key: 'provenanceHash', label: 'Provenance Hash' },
  { key: 'complianceStatus', label: 'Compliance Status' },
  { key: 'owner', label: 'Owner' },
  { key: 'lastActivity', label: 'Last Activity' }
]);

const LEAD_VIEWS = Object.freeze(['ALL', 'VERIFIED', 'PENDING', 'FAILED']);

const SETUP_GROUPS = [
  { title: 'General', items: ['Personal Settings', 'Users', 'Company Settings'] },
  { title: 'Security Control', items: ['Profiles', 'Roles and Sharing', 'Compliance Settings'] },
  { title: 'Customization', items: ['Modules and Fields', 'Lead Layouts', 'Workflow Rules'] },
  { title: 'Data Administration', items: ['Import', 'Export', 'Data Backup'] },
  { title: 'Developer Hub', items: ['APIs and SDKs', 'Extensions', 'Catalyst Solutions'] }
];

/**
 * @function resolveLeadRole
 * @description Resolves a normalized CRM role for Lead workspace permissions.
 * @param {Object} user - User packet.
 * @param {Object} tenantConfig - Tenant config.
 * @returns {string} Normalized role.
 * @collaboration Keeps Lead actions role-aware without hardcoding one operator.
 */
function resolveLeadRole(user = {}, tenantConfig = {}) {
  return String(user?.role || user?.accountRole || user?.profile?.role || tenantConfig?.role || tenantConfig?.userRole || 'SALES_REP').toUpperCase();
}

/**
 * @function resolveTenantId
 * @description Resolves tenant id for Lead command fabric calls.
 * @param {Object} tenantConfig - Tenant config.
 * @param {Object} user - User packet.
 * @returns {string} Tenant id.
 * @collaboration Keeps search, sync and create tenant-bound.
 */
function resolveTenantId(tenantConfig = {}, user = {}) {
  return String(tenantConfig?.tenantId || tenantConfig?.id || tenantConfig?.tenantKey || user?.tenantId || user?.tenant?.id || 'MASTER');
}

/**
 * @function canUseLeadAction
 * @description Evaluates whether a role can use a Lead action.
 * @param {string} role - Normalized role.
 * @param {string} action - Action key.
 * @returns {boolean} Permission result.
 * @collaboration Prevents sales users from seeing admin-only controls.
 */
function canUseLeadAction(role = 'SALES_REP', action = 'view') {
  const masterRoles = ['MASTER', 'FOUNDER', 'SUPER_ADMIN', 'ROOT'];
  const adminRoles = [...masterRoles, 'TENANT_ADMIN', 'ADMIN', 'CRM_ADMIN'];
  const managerRoles = [...adminRoles, 'SALES_MANAGER', 'MANAGER'];

  if (masterRoles.includes(role)) return true;
  if (['view', 'search', 'create', 'calendar', 'note', 'call', 'meeting', 'email', 'sync'].includes(action)) return true;
  if (['import', 'export', 'bulk', 'assign'].includes(action)) return managerRoles.includes(role);
  if (['delete', 'subscription', 'tenant-admin', 'setup'].includes(action)) return adminRoles.includes(role);

  return false;
}

/**
 * @function createEmptyLeadDraft
 * @description Creates an empty Lead draft with operator owner default.
 * @param {Object} user - User packet.
 * @returns {Object} Empty draft.
 * @collaboration Keeps create state deterministic until backend save.
 */
function createEmptyLeadDraft(user = {}) {
  return {
    ...EMPTY_LEAD_DRAFT,
    owner: user?.name || user?.fullName || user?.email || ''
  };
}

/**
 * @function getComplianceStatus
 * @description Resolves compliance status from Lead source fields.
 * @param {Object} record - Lead record.
 * @returns {string} Compliance status.
 * @collaboration Shows audit posture without inventing records.
 */
function getComplianceStatus(record = {}) {
  const raw = String(record.complianceStatus || record.sourceStatus || record.verificationStatus || '').toUpperCase();

  if (raw.includes('VERIFIED') || raw.includes('SOURCE_LIVE') || raw.includes('PASSED')) return 'VERIFIED';
  if (raw.includes('FAILED') || raw.includes('REJECTED')) return 'FAILED';
  if (raw.includes('PENDING') || raw.includes('REVIEW')) return 'PENDING';

  return 'PENDING';
}

/**
 * @function getProvenanceHash
 * @description Resolves a provenance hash from available record fields.
 * @param {Object} record - Lead record.
 * @returns {string} Provenance hash.
 * @collaboration Surfaces source-trace transparency in the ledger.
 */
function getProvenanceHash(record = {}) {
  return String(record.cryptographicHash || record.provenanceHash || record.rootHash || record.sealHash || record._id || record.id || 'UNSEALED');
}

/**
 * @function isLeadDraftValid
 * @description Checks required fields before backend creation.
 * @param {Object} draft - Lead draft.
 * @returns {boolean} True when valid.
 * @collaboration Blocks empty-click lead creation.
 */
function isLeadDraftValid(draft = {}) {
  return REQUIRED_LEAD_FIELDS.every(field => String(draft[field] || '').trim().length > 0);
}

/**
 * @function normalizeLeadPayload
 * @description Adds source metadata to the lead payload.
 * @param {Object} draft - Lead draft.
 * @param {string} tenantId - Tenant id.
 * @returns {Object} Normalized payload.
 * @collaboration Separates browser action from backend authority.
 */
function normalizeLeadPayload(draft = {}, tenantId = 'MASTER') {
  return {
    ...draft,
    tenantId,
    complianceStatus: 'PENDING',
    sourceStatus: 'SOURCE_LIVE',
    sourceSystem: 'WILSY_OS_LEAD_CONTEXTUAL_COMMAND_STRIP',
    operatingRoom: 'LEADS'
  };
}

/**
 * @function resolveLeadValue
 * @description Resolves grid values from flexible backend Lead records.
 * @param {Object} record - Lead record.
 * @param {string} field - Logical field.
 * @returns {string} Display value.
 * @collaboration Supports current and future CRM schemas.
 */
function resolveLeadValue(record = {}, field = '') {
  const values = {
    name: record.name || record.fullName || [record.firstName, record.lastName].filter(Boolean).join(' '),
    company: record.company || record.accountName || record.organization,
    email: record.email || record.primaryEmail,
    phone: record.phone || record.mobile || record.primaryPhone,
    provenanceHash: getProvenanceHash(record),
    complianceStatus: getComplianceStatus(record),
    owner: record.owner || record.ownerName || record.assignedTo,
    lastActivity: record.lastActivity || record.updatedAt || record.createdAt
  };

  return String(values[field] || '—');
}

/**
 * @function buildCalendarDays
 * @description Builds day cells for the Lead calendar shell.
 * @returns {number[]} Day slots.
 * @collaboration Provides activity planning without fake backend events.
 */
function buildCalendarDays() {
  return Array.from({ length: 35 }, (_, index) => index + 1);
}

/**
 * @function WilsyLeadOperatingRoom
 * @description Renders the production Lead operating room with contextual command strip and skin-aware density.
 * @param {Object} props - Component props.
 * @returns {JSX.Element} Lead operating room.
 * @collaboration Replaces action-fatigue layout with a high-density sovereign cockpit.
 */
export default function WilsyLeadOperatingRoom({
  leads = [],
  searchTerm = '',
  onSearch,
  onSync,
  onSaveLead,
  tenantConfig = {},
  user = {},
  loading = false
}) {
  const role = resolveLeadRole(user, tenantConfig);
  const tenantId = resolveTenantId(tenantConfig, user);
  const [mode, setMode] = useState('list');
  const [activeFilter, setActiveFilter] = useState('ALL');
  const [leadSkin, setLeadSkin] = useState('WILSY_NEBULA_COMMAND');
  const [splitView, setSplitView] = useState(false);
  const [calendarOpen, setCalendarOpen] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const [setupOpen, setSetupOpen] = useState(false);
  const [coreToolsOpen, setCoreToolsOpen] = useState(false);
  const [draft, setDraft] = useState(() => createEmptyLeadDraft(user));
  const [saveStatus, setSaveStatus] = useState('');
  const [syncStatus, setSyncStatus] = useState('SOURCE_READY_UPSTREAM');
  const [syncTelemetry, setSyncTelemetry] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const hasAutoHydratedTelemetryRef = useRef(false);
  const leadThemeOptions = useMemo(() => resolveCrmThemeEngineOptions(), []);
  const activeLeadThemeOption = leadThemeOptions.find(option => option.id === leadSkin) || leadThemeOptions[0];


  const complianceMetrics = useMemo(() => {
    const total = leads.length;
    const verified = leads.filter(record => getComplianceStatus(record) === 'VERIFIED').length;
    const pending = leads.filter(record => getComplianceStatus(record) === 'PENDING').length;
    const failed = leads.filter(record => getComplianceStatus(record) === 'FAILED').length;

    return { total, verified, pending, failed };
  }, [leads]);

  const filteredLeads = useMemo(() => {
    const query = String(searchTerm || '').trim().toLowerCase();

    return leads.filter(record => {
      const matchesSearch = !query || JSON.stringify(record || {}).toLowerCase().includes(query);
      const status = getComplianceStatus(record);
      const matchesFilter = activeFilter === 'ALL' || status === activeFilter;

      return matchesSearch && matchesFilter;
    });
  }, [activeFilter, leads, searchTerm]);

  const sourcePosture = leads.length ? 'SOURCE_LIVE' : 'SOURCE_READY_EMPTY';
  const routeRegistry = Array.isArray(syncTelemetry?.registry) ? syncTelemetry.registry : [];
  const liveSources = syncTelemetry?.liveSources ?? routeRegistry.filter(route => route.connected).length;
  const totalSources = syncTelemetry?.totalSources ?? routeRegistry.length;
  const rootHash = syncTelemetry?.rootHashShort || syncTelemetry?.rootHash || 'UNSEALED';
  useEffect(() => {
    if (hasAutoHydratedTelemetryRef.current) return;
    hasAutoHydratedTelemetryRef.current = true;

    if (typeof onSync === 'function') {
      setIsSyncing(true);
      setSyncStatus('R66G_AUTO_TELEMETRY_HYDRATION');

      onSync()
        .then((telemetry) => {
          setSyncTelemetry(telemetry || null);
          setSyncStatus(telemetry?.sourceStatus || 'SOURCE_SYNC_COMPLETE');
        })
        .catch((error) => {
          setSyncStatus(error?.message || 'SOURCE_SYNC_FAILED');
        })
        .finally(() => {
          setIsSyncing(false);
        });
    }
  }, []);


  /**
   * @function updateDraftField
   * @description Updates one field on the Lead draft.
   * @param {string} field - Field key.
   * @param {string} value - Field value.
   * @returns {void}
   * @collaboration Keeps draft local until backend save.
   */
  function updateDraftField(field, value) {
    setDraft(previous => ({
      ...previous,
      [field]: value
    }));
  }

  /**
   * @function handleSearchChange
   * @description Routes Lead search through command fabric.
   * @param {string} query - Search query.
   * @returns {void}
   * @collaboration Keeps search source-backed.
   */
  function handleSearchChange(query) {
    if (typeof onSearch === 'function') {
      onSearch(query);
    }
  }

  /**
   * @function handleSourceSync
   * @description Executes backend source sync and captures telemetry.
   * @returns {Promise<void>} Sync operation.
   * @collaboration Converts empty state into a source ingestion control plane.
   */
  async function handleSourceSync() {
    if (!canUseLeadAction(role, 'sync')) {
      setSyncStatus('SYNC_LOCKED_BY_ROLE');
      return;
    }

    setIsSyncing(true);
    setSyncStatus('SYNCING_SOURCE_ROUTES');

    try {
      const telemetry = typeof onSync === 'function' ? await onSync() : null;
      setSyncTelemetry(telemetry || null);
      setSyncStatus(telemetry?.sourceStatus || 'SOURCE_SYNC_COMPLETE');
    } catch (error) {
      setSyncStatus(error?.message || 'SOURCE_SYNC_FAILED');
    } finally {
      setIsSyncing(false);
    }
  }

  /**
   * @function handleSaveLead
   * @description Saves a valid Lead draft through backend command fabric.
   * @param {boolean} createAnother - Whether to reset the draft after save.
   * @returns {Promise<void>} Save operation.
   * @collaboration Prevents fake rows and preserves backend authority.
   */
  async function handleSaveLead(createAnother = false) {
    if (!canUseLeadAction(role, 'create')) {
      setSaveStatus('Create Lead is locked by role policy.');
      return;
    }

    if (!isLeadDraftValid(draft)) {
      setSaveStatus('Lead name, company and email are required before backend creation.');
      return;
    }

    setSaveStatus('Sending verified Lead payload to backend command fabric...');

    try {
      if (typeof onSaveLead === 'function') {
        await onSaveLead(normalizeLeadPayload(draft, tenantId));
      }

      setSaveStatus('Lead saved through backend command fabric.');

      if (createAnother) {
        setDraft(createEmptyLeadDraft(user));
        return;
      }

      setMode('list');
    } catch (error) {
      setSaveStatus(error?.message || 'Backend rejected the Lead payload.');
    }
  }

  /**
   * @function renderSkinSwitcher
   * @description Renders local Lead skin switcher.
   * @returns {JSX.Element} Skin switcher.
   * @collaboration Proves layout survives skin switching before global token provider rollout.
   */
  function renderSkinSwitcher() {
    return (
      <section className={styles.skinSwitcher} aria-label="Lead skin switcher">
        {leadThemeOptions.map(option => (
          <button
            key={option.id}
            type="button"
            className={option.id === activeLeadThemeOption.id ? styles.skinActive : styles.skinButton}
            onClick={() => setLeadSkin(option.id)}
            title={`Theme source: ${option.source}`}
          >
            {option.label}
          </button>
        ))}
      </section>
    );
  }

  /**
   * @function renderContextualCommandStrip
   * @description Renders the condensed command strip.
   * @returns {JSX.Element} Command strip.
   * @collaboration Removes button fatigue while keeping high-velocity actions one click away.
   */
  function renderContextualCommandStrip() {
    return (
      <section className={styles.commandStrip} data-wilsy-command-strip="contextual">
        <label className={styles.commandSearch}>
          <Search size={17} />
          <input
            value={searchTerm}
            onChange={event => handleSearchChange(event.target.value)}
            placeholder="Search records, evidence, hashes... (⌘K)"
            aria-label="Search Lead records"
          />
          <kbd>⌘K</kbd>
        </label>

        <div className={styles.commandActions}>
          <button type="button" className={styles.primaryToolbarButton} onClick={() => setMode('create')} disabled={!canUseLeadAction(role, 'create')}>
            <Plus size={17} />
            <span>New Lead</span>
          </button>

          <button type="button" className={styles.toolbarButton} onClick={handleSourceSync} disabled={!canUseLeadAction(role, 'sync') || isSyncing}>
            <RotateCw size={17} />
            <span>{isSyncing ? 'Syncing' : 'Sync Sources'}</span>
          </button>

          <div className={styles.coreToolsWrap}>
            <button type="button" className={styles.toolbarButton} onClick={() => setCoreToolsOpen(previous => !previous)}>
              <MoreHorizontal size={17} />
              <span>Core Tools</span>
            </button>

            {coreToolsOpen ? (
              <section className={styles.coreToolsMenu} aria-label="Lead core tools">
                <button type="button" disabled={!canUseLeadAction(role, 'import')}><Upload size={15} />Import Leads</button>
                <button type="button" disabled={!canUseLeadAction(role, 'import')}><FileInput size={15} />Import Notes</button>
                <button type="button" onClick={() => setCalendarOpen(true)}><CalendarDays size={15} />Calendar View</button>
                <button type="button" onClick={() => setSplitView(previous => !previous)}><SplitSquareHorizontal size={15} />{splitView ? 'Single Interface' : 'Split Interface'}</button>
                <button type="button" onClick={() => setCommandOpen(true)}><Command size={15} />Command Center</button>
                <button type="button" disabled={!canUseLeadAction(role, 'setup')} onClick={() => setSetupOpen(true)}><Settings size={15} />Setup</button>
                <button type="button" disabled={!canUseLeadAction(role, 'export')}><Download size={15} />Export Leads</button>
              </section>
            ) : null}
          </div>
        </div>
      </section>
    );
  }

  /**
   * @function renderHeader
   * @description Renders the sovereign Lead command header with shortcuts, telemetry, search and theme authority.
   * @returns {JSX.Element} Header.
   * @collaboration Converts the Lead header from a title card into the operating app bar.
   */
  function renderHeader() {
    const routeLabel = totalSources ? `${liveSources}/${totalSources}` : 'Awaiting sync';
    const rootLabel = String(rootHash || 'UNSEALED').slice(0, 14);
    const complianceLabel = complianceMetrics.total
      ? `${complianceMetrics.verified}/${complianceMetrics.total} verified`
      : 'No records yet';

    return (
      <header className={styles.appHeader} data-wilsy-lead-appbar="sovereign-header-command-bridge">
        <section className={styles.headerPrimaryRow}>
          <section className={styles.headerIdentity}>
            <small>Leads Engine // Platform Skin: {activeLeadThemeOption?.id || 'WILSY_NEBULA_COMMAND'}</small>
            <strong>{mode === 'create' ? 'Create Verified Lead' : 'Lead Operating Room'}</strong>
            <em>{tenantId} · {role} · {syncStatus}</em>
          </section>

          <section className={styles.headerThemeDock} data-wilsy-header-theme-dock="theme-engine-authority">
            {renderSkinSwitcher()}
          </section>
        </section>

        <section className={styles.headerCommandGrid} data-wilsy-header-command-grid="investor-grade">
          <label className={styles.headerSearch}>
            <Search size={18} />
            <input
              value={searchTerm}
              onChange={event => handleSearchChange(event.target.value)}
              placeholder="Search leads, evidence, hashes, companies... (⌘K)"
              aria-label="Search Lead records"
            />
            <kbd>⌘K</kbd>
          </label>

          <section className={styles.headerInvestorStrip} data-wilsy-investor-strip="source-root-compliance">
            <article>
              <small>Source Routes</small>
              <strong>{routeLabel}</strong>
              <em>{sourcePosture}</em>
            </article>
            <article>
              <small>Sovereign Root</small>
              <strong>{rootLabel}</strong>
              <em>Provenance</em>
            </article>
            <article>
              <small>Compliance</small>
              <strong>{complianceLabel}</strong>
              <em>POPIA · GDPR · SOC2</em>
            </article>
            <article>
              <small>Theme Authority</small>
              <strong>{activeLeadThemeOption?.label || 'NEBULA'}</strong>
              <em>{activeLeadThemeOption?.source || 'wilsyOperatingSkins'}</em>
            </article>
          </section>

          <section className={styles.headerShortcutBar} data-wilsy-header-shortcuts="production">
            <button
              type="button"
              className={styles.headerPrimaryAction}
              onClick={() => setMode('create')}
              disabled={!canUseLeadAction(role, 'create')}
            >
              <Plus size={18} />
              <span>New Lead</span>
            </button>

            <button type="button" onClick={handleSourceSync} disabled={!canUseLeadAction(role, 'sync') || isSyncing}>
              <RotateCw size={18} />
              <span>{isSyncing ? 'Syncing' : 'Sync Sources'}</span>
            </button>

            <button type="button" disabled={!canUseLeadAction(role, 'import')}>
              <Upload size={18} />
              <span>Import Leads</span>
            </button>

            <button type="button" onClick={() => setCalendarOpen(true)}>
              <CalendarDays size={18} />
              <span>Calendar</span>
            </button>

            <button type="button" onClick={() => setSplitView(previous => !previous)}>
              <SplitSquareHorizontal size={18} />
              <span>{splitView ? 'Single View' : 'Split View'}</span>
            </button>

            <button type="button" onClick={() => setCommandOpen(true)}>
              <Command size={18} />
              <span>Command Center</span>
            </button>

            <button type="button" disabled={!canUseLeadAction(role, 'setup')} onClick={() => setSetupOpen(true)}>
              <Settings size={18} />
              <span>Setup</span>
            </button>

            <div className={styles.headerMoreDock}>
              <button type="button" onClick={() => setCoreToolsOpen(previous => !previous)}>
                <MoreHorizontal size={18} />
                <span>More</span>
              </button>

              {coreToolsOpen ? (
                <section className={styles.headerMoreMenu} aria-label="Lead more actions">
                  <button type="button" disabled={!canUseLeadAction(role, 'import')}><FileInput size={15} />Import Notes</button>
                  <button type="button" disabled={!canUseLeadAction(role, 'export')}><Download size={15} />Export Leads</button>
                  <button type="button"><ShieldCheck size={15} />Proof Trail</button>
                  <button type="button"><Sparkles size={15} />Wilsy AI Services</button>
                </section>
              ) : null}
            </div>
          </section>
        </section>
      </header>
    );
  }

  /**
   * @function renderPipelineTelemetry
   * @description Renders high-density pipeline telemetry.
   * @returns {JSX.Element} Telemetry panel.
   * @collaboration Moves counters into a compact scannable column.
   */
  function renderPipelineTelemetry() {
    const rows = [
      { label: 'Total Ingested', value: complianceMetrics.total, posture: sourcePosture },
      { label: 'Compliance Passed', value: complianceMetrics.verified, posture: 'VERIFIED' },
      { label: 'Audit Pending', value: complianceMetrics.pending, posture: 'PENDING' },
      { label: 'Failed Gates', value: complianceMetrics.failed, posture: 'FAILED' },
      { label: 'Source Routes', value: totalSources ? `${liveSources}/${totalSources}` : '—', posture: 'UPLINK' },
      { label: 'Root Hash', value: String(rootHash).slice(0, 12), posture: 'PROVENANCE' }
    ];

    return (
      <section className={styles.telemetryPanel} data-wilsy-telemetry-panel="dense">
        <h3>Pipeline Telemetry</h3>
        {rows.map(row => (
          <article key={row.label}>
            <span>{row.label}</span>
            <strong>{row.value}</strong>
            <em>{row.posture}</em>
          </article>
        ))}
      </section>
    );
  }

  /**
   * @function renderSourceRoutes
   * @description Renders source ingestion routes.
   * @returns {JSX.Element} Source route panel.
   * @collaboration Turns empty state into source activation instead of dead space.
   */
  function renderSourceRoutes() {
    return (
      <section className={styles.sourcePanel}>
        <h3>Source Ingestion Routes</h3>

        {routeRegistry.length ? routeRegistry.map(route => (
          <button key={route.key} type="button" className={route.connected ? styles.routeLive : styles.routeGap}>
            <span>{route.key}</span>
            <strong>{route.count ?? 0}</strong>
          </button>
        )) : (
          <div className={styles.routeEmpty}>
            <Database size={22} />
            <strong>No upstream telemetry sealed.</strong>
            <p>Attach authentic source routes to seal the provenance ledger.</p>
            <button type="button" onClick={handleSourceSync}>Initialize Upstream Channels</button>
          </div>
        )}
      </section>
    );
  }

  /**
   * @function renderComplianceTabs
   * @description Renders compact compliance filter tabs.
   * @returns {JSX.Element} Compliance tabs.
   * @collaboration Lets operators isolate verified, pending and failed records.
   */
  function renderComplianceTabs() {
    const counts = {
      ALL: complianceMetrics.total,
      VERIFIED: complianceMetrics.verified,
      PENDING: complianceMetrics.pending,
      FAILED: complianceMetrics.failed
    };

    return (
      <section className={styles.complianceTabs}>
        {LEAD_VIEWS.map(view => (
          <button
            key={view}
            type="button"
            className={activeFilter === view ? styles.complianceTabActive : styles.complianceTab}
            onClick={() => setActiveFilter(view)}
          >
            {view}<span>{counts[view]}</span>
          </button>
        ))}
      </section>
    );
  }


  /**
   * @function renderEmptyActivationBoard
   * @description Renders a sovereign activation board when the Lead ledger has no records.
   * @returns {JSX.Element} Empty ledger activation board.
   * @collaboration Converts empty data into useful operator actions without fabricating rows.
   */
  function renderEmptyActivationBoard() {
    const routeLabel = totalSources ? `${liveSources}/${totalSources}` : 'AWAITING SYNC';
    const rootLabel = String(rootHash || 'UNSEALED').slice(0, 12);

    return (
      <section
        className={styles.emptyActivationBoard}
        data-wilsy-empty-activation-board="R67D-SOVEREIGN-HEADER-COMMAND-BRIDGE"
      >
        <header className={styles.activationHero}>
          <span>
            <Fingerprint size={38} />
          </span>
          <div>
            <small>Sovereign Ledger Activation</small>
            <strong>No Backend Lead Rows Returned.</strong>
            <p>
              The ledger is empty because Wilsy OS refuses to fake records. Activate a verified
              upstream channel, import real source data, or create a validated lead to seal the first row.
            </p>
          </div>
          <em>{tenantId} · {role}</em>
        </header>

        <section className={styles.activationGrid}>
          <article className={styles.activationCard}>
            <Database size={22} />
            <small>Source Routes</small>
            <strong>{routeLabel}</strong>
            <p>Initialize CRM, email, webform, partner, import and governance channels.</p>
            <button type="button" onClick={handleSourceSync}>Initialize Upstream Channels</button>
          </article>

          <article className={styles.activationCard}>
            <ShieldCheck size={22} />
            <small>Root Seal</small>
            <strong>{rootLabel}</strong>
            <p>Every accepted lead must produce a provenance hash and auditable source posture.</p>
            <button type="button" onClick={handleSourceSync}>Refresh Seal Telemetry</button>
          </article>

          <article className={styles.activationCard}>
            <Upload size={22} />
            <small>Import Dock</small>
            <strong>CSV / Notes / Evidence</strong>
            <p>Prepare real source ingestion without allowing decorative sample rows.</p>
            <button type="button" disabled={!canUseLeadAction(role, 'import')}>Open Import Queue</button>
          </article>

          <article className={styles.activationCard}>
            <WandSparkles size={22} />
            <small>Wilsy AI</small>
            <strong>Enrichment Ready</strong>
            <p>Score, enrich, deduplicate and draft outreach after a real lead is present.</p>
            <button type="button">Prepare AI Enrichment</button>
          </article>

          <article className={styles.activationCard}>
            <ClipboardList size={22} />
            <small>Compliance Matrix</small>
            <strong>POPIA · GDPR · SOC2</strong>
            <p>Bind consent, source basis, retention posture and audit events to every lead.</p>
            <button type="button" onClick={() => setCommandOpen(true)}>Open Command Center</button>
          </article>

          <article className={styles.activationCardPrimary}>
            <Plus size={22} />
            <small>Verified Create</small>
            <strong>Create the first real Lead</strong>
            <p>Lead name, company and email are required before backend creation activates.</p>
            <button type="button" onClick={() => setMode('create')}>Create Verified Lead</button>
          </article>
        </section>

        <footer className={styles.activationFooter}>
          <span>No synthetic rows</span>
          <span>Backend authority only</span>
          <span>Provenance hash required</span>
          <span>Compliance binding required</span>
        </footer>
      </section>
    );
  }


  /**
   * @function renderLedger
   * @description Renders the Data Provenance Ledger without leaving dead space when empty.
   * @returns {JSX.Element} Ledger.
   * @collaboration Keeps provenance dominant while turning empty state into a responsive activation board.
   */
  function renderLedger() {
    const hasRows = filteredLeads.length > 0;

    return (
      <section
        className={styles.ledgerPanel}
        data-wilsy-ledger-state={hasRows ? 'populated' : 'empty'}
      >
        <header>
          <span>
            <small>Data Provenance Ledger</small>
            <strong>All Leads</strong>
          </span>
          <div>
            <button type="button" onClick={handleSourceSync} disabled={isSyncing}>
              <CheckCircle2 size={16} />
              {isSyncing ? 'Syncing' : 'Sync'}
            </button>
            <button type="button" disabled={!canUseLeadAction(role, 'export')}>
              <Download size={16} />
              Export
            </button>
          </div>
        </header>

        {hasRows ? (
          <div className={styles.tableFrame}>
            <table>
              <thead>
                <tr>
                  <th><input type="checkbox" aria-label="Select all leads" /></th>
                  {LEAD_COLUMNS.map(column => <th key={column.key}>{column.label}</th>)}
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredLeads.map((record, index) => (
                  <tr key={record._id || record.id || `lead-record-${index}`}>
                    <td><input type="checkbox" aria-label={`Select lead ${index + 1}`} /></td>
                    {LEAD_COLUMNS.map(column => (
                      <td key={column.key}>
                        {column.key === 'complianceStatus' ? (
                          <span className={styles[`status${resolveLeadValue(record, column.key)}`] || styles.statusPENDING}>
                            {resolveLeadValue(record, column.key)}
                          </span>
                        ) : column.key === 'provenanceHash' ? (
                          <code title={resolveLeadValue(record, column.key)}>
                            {resolveLeadValue(record, column.key).slice(0, 18)}
                          </code>
                        ) : resolveLeadValue(record, column.key)}
                      </td>
                    ))}
                    <td><button type="button">Manage</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className={styles.ledgerEmptyFrame}>
            {renderEmptyActivationBoard()}
          </div>
        )}
      </section>
    );
  }

  /**
   * @function renderListMode
   * @description Renders the high-density Lead command canvas.
   * @returns {JSX.Element} List mode.
   * @collaboration Replaces button flood with telemetry, source routes and provenance ledger.
   */
  function renderListMode() {
    return (
      <section className={splitView ? styles.coreGridSplit : styles.coreGrid}>
        <aside className={styles.leftColumn}>
          {renderPipelineTelemetry()}
          {renderComplianceTabs()}
          {renderSourceRoutes()}
        </aside>

        <main className={styles.rightColumn}>
          {renderLedger()}
        </main>

        {splitView ? (
          <aside className={styles.intelligencePanel}>
            <header><Sparkles size={20} /><span><small>Wilsy AI</small><strong>Lead Intelligence</strong></span></header>
            <p>Select a Lead to reveal timeline, notes, next activity, probability, evidence, compliance posture and AI recommendations.</p>
            <button type="button">Prepare outreach</button>
            <button type="button">Schedule next step</button>
            <button type="button">Open proof trail</button>
          </aside>
        ) : null}
      </section>
    );
  }

  /**
   * @function renderCreateMode
   * @description Renders the focused Create Lead surface.
   * @returns {JSX.Element} Create Lead surface.
   * @collaboration Captures verified lead payloads for backend command fabric.
   */
  function renderCreateMode() {
    return (
      <section className={styles.createSurface}>
        <header className={styles.createHeader}>
          <span><small>Focused Create</small><strong>Create Verified Lead</strong><em>Capture, enrich, schedule and prove the Lead source from one workspace.</em></span>
          <div>
            <button type="button" onClick={() => setMode('list')}>Cancel</button>
            <button type="button" disabled={!canUseLeadAction(role, 'create')} onClick={() => handleSaveLead(true)}>Save and New</button>
            <button type="button" className={styles.saveButton} disabled={!canUseLeadAction(role, 'create')} onClick={() => handleSaveLead(false)}>Save</button>
          </div>
        </header>

        <main className={styles.createGrid}>
          <section className={styles.formPanel}>
            <h3>Lead Information</h3>
            <div className={styles.formGrid}>
              <label><span>Lead Name *</span><input value={draft.name} onChange={event => updateDraftField('name', event.target.value)} /></label>
              <label><span>Company *</span><input value={draft.company} onChange={event => updateDraftField('company', event.target.value)} /></label>
              <label><span>Email *</span><input value={draft.email} onChange={event => updateDraftField('email', event.target.value)} /></label>
              <label><span>Phone</span><input value={draft.phone} onChange={event => updateDraftField('phone', event.target.value)} /></label>
              <label><span>Mobile</span><input value={draft.mobile} onChange={event => updateDraftField('mobile', event.target.value)} /></label>
              <label><span>Title</span><input value={draft.title} onChange={event => updateDraftField('title', event.target.value)} /></label>
              <label><span>Lead Source</span><select value={draft.source} onChange={event => updateDraftField('source', event.target.value)}><option>Website</option><option>Referral</option><option>Partner</option><option>Outbound</option><option>Event</option><option>Wilsy AI</option></select></label>
              <label><span>Status</span><select value={draft.status} onChange={event => updateDraftField('status', event.target.value)}><option>NEW</option><option>OPEN</option><option>CONTACTED</option><option>QUALIFIED</option><option>DISQUALIFIED</option></select></label>
              <label><span>Industry</span><input value={draft.industry} onChange={event => updateDraftField('industry', event.target.value)} /></label>
              <label><span>Owner</span><input value={draft.owner} onChange={event => updateDraftField('owner', event.target.value)} /></label>
              <label><span>Website</span><input value={draft.website} onChange={event => updateDraftField('website', event.target.value)} /></label>
              <label><span>Employees</span><input value={draft.employees} onChange={event => updateDraftField('employees', event.target.value)} /></label>
            </div>

            <h3>Address Information</h3>
            <div className={styles.formGrid}>
              <label className={styles.wideField}><span>Street</span><input value={draft.street} onChange={event => updateDraftField('street', event.target.value)} /></label>
              <label><span>City</span><input value={draft.city} onChange={event => updateDraftField('city', event.target.value)} /></label>
              <label><span>State</span><input value={draft.state} onChange={event => updateDraftField('state', event.target.value)} /></label>
              <label><span>Zip Code</span><input value={draft.zipCode} onChange={event => updateDraftField('zipCode', event.target.value)} /></label>
              <label><span>Country</span><input value={draft.country} onChange={event => updateDraftField('country', event.target.value)} /></label>
            </div>

            <h3>Description Information</h3>
            <label className={styles.descriptionField}><span>Description / Notes</span><textarea value={draft.description} onChange={event => updateDraftField('description', event.target.value)} /></label>
          </section>

          <aside className={styles.createCommandPanel}>
            <section><ShieldCheck size={23} /><strong>Source posture</strong><p>Backend create activates only after required fields are valid. Browser does not manufacture Lead authority.</p><span>{saveStatus || 'Awaiting validated Lead payload.'}</span></section>
            <section><CalendarDays size={23} /><strong>Activity shortcuts</strong><button type="button" onClick={() => setCalendarOpen(true)}><CalendarDays size={16} />Create meeting</button><button type="button" onClick={() => setCalendarOpen(true)}><Phone size={16} />Create call</button><button type="button" onClick={() => setCalendarOpen(true)}><Activity size={16} />Mark unavailable</button></section>
            <section><Sparkles size={23} /><strong>Wilsy AI services</strong><button type="button"><WandSparkles size={16} />Enrich Lead</button><button type="button"><Mail size={16} />Draft outreach</button><button type="button"><ClipboardList size={16} />Score readiness</button></section>
          </aside>
        </main>
      </section>
    );
  }

  /**
   * @function renderCalendarDrawer
   * @description Renders the Lead calendar drawer.
   * @returns {JSX.Element|null} Calendar drawer.
   * @collaboration Gives Leads call, meeting and unavailable planning.
   */
  function renderCalendarDrawer() {
    if (!calendarOpen) return null;

    return (
      <section className={styles.drawer} aria-label="Lead calendar workspace">
        <header><span><small>Calendar</small><strong>Lead Activity Month</strong></span><button type="button" onClick={() => setCalendarOpen(false)}>Close</button></header>
        <nav><button type="button">Meeting</button><button type="button">Call</button><button type="button">Mark As Unavailable</button></nav>
        <div className={styles.calendarGrid}>{buildCalendarDays().map(day => <button key={day} type="button"><strong>{day <= 31 ? day : ''}</strong>{day % 7 === 0 ? <span>Call</span> : null}{day % 11 === 0 ? <em>Meeting</em> : null}</button>)}</div>
      </section>
    );
  }

  /**
   * @function renderCommandDrawer
   * @description Renders tenant and subscription command drawer.
   * @returns {JSX.Element|null} Command drawer.
   * @collaboration Surfaces Master and tenant administration controls.
   */
  function renderCommandDrawer() {
    if (!commandOpen) return null;

    const isMaster = ['MASTER', 'FOUNDER', 'SUPER_ADMIN', 'ROOT'].includes(role);
    const isAdmin = isMaster || ['TENANT_ADMIN', 'ADMIN', 'CRM_ADMIN'].includes(role);

    return (
      <section className={styles.drawer} aria-label="Lead command center">
        <header><span><small>Command Center</small><strong>{tenantId} · {role}</strong></span><button type="button" onClick={() => setCommandOpen(false)}>Close</button></header>
        <div className={styles.commandTiles}>
          {isMaster ? <button type="button"><UserRoundCog size={18} />Manage Organizations</button> : null}
          {isMaster ? <button type="button"><LayoutPanelTop size={18} />Tenant Activities</button> : null}
          {isAdmin ? <button type="button"><ShieldCheck size={18} />Manage Subscription</button> : null}
          {isAdmin ? <button type="button"><Sparkles size={18} />Upgrade Tier</button> : null}
          <button type="button"><WandSparkles size={18} />Wilsy AI Services</button>
          <button type="button"><ClipboardList size={18} />Sales Shortcuts</button>
        </div>
      </section>
    );
  }

  /**
   * @function renderSetupDrawer
   * @description Renders CRM setup drawer.
   * @returns {JSX.Element|null} Setup drawer.
   * @collaboration Groups operating controls into enterprise setup domains.
   */
  function renderSetupDrawer() {
    if (!setupOpen) return null;

    const groups = [
      { title: 'General', items: ['Personal Settings', 'Users', 'Company Settings'] },
      { title: 'Security Control', items: ['Profiles', 'Roles and Sharing', 'Compliance Settings'] },
      { title: 'Customization', items: ['Modules and Fields', 'Lead Layouts', 'Workflow Rules'] },
      { title: 'Data Administration', items: ['Import', 'Export', 'Data Backup'] },
      { title: 'Developer Hub', items: ['APIs and SDKs', 'Extensions', 'Catalyst Solutions'] }
    ];

    return (
      <section className={styles.drawerWide} aria-label="Lead setup workspace">
        <header><span><small>Setup</small><strong>CRM Operating Controls</strong></span><button type="button" onClick={() => setSetupOpen(false)}>Close</button></header>
        <div className={styles.setupGrid}>{groups.map(group => <article key={group.title}><strong>{group.title}</strong>{group.items.map(item => <button key={item} type="button">{item}</button>)}</article>)}</div>
      </section>
    );
  }

  return (
    <section
      className={[styles.leadOperatingRoom, activeLeadThemeOption?.className].filter(Boolean).join(' ')}
      style={activeLeadThemeOption?.cssVars || undefined}
      data-wilsy-lead-operating-room={WILSY_LEAD_OPERATING_ROOM_VERSION}
      data-wilsy-lead-skin={activeLeadThemeOption?.id || 'WILSY_NEBULA_COMMAND'}
      data-wilsy-theme-engine-source="wilsyOperatingSkins"
      data-wilsy-theme-bridge-version={WILSY_CRM_THEME_ENGINE_BRIDGE_VERSION}
    >
      {renderHeader()}
      {renderContextualCommandStrip()}
      {mode === 'create' ? renderCreateMode() : renderListMode()}
      {renderCalendarDrawer()}
      {renderCommandDrawer()}
      {renderSetupDrawer()}
      {loading || isSyncing ? <div className={styles.loadingVeil}>Synchronising CRM sources...</div> : null}
    </section>
  );
}
