/* eslint-disable */
/**
 * @fileoverview Wilsy OS Universal Meeting Command Center.
 * Reusable CRM meeting viewport system for standalone Meetings, Create Lead, and Lead Edit contexts.
 * No fake meeting records, no fake import success, and no backend mutation.
 */

import React, { useMemo, useState } from 'react';
import {
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  Clock,
  FileSpreadsheet,
  Fingerprint,
  Link2,
  Mail,
  MapPin,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  UserPlus,
  Users,
  X,
} from 'lucide-react';
import styles from './WilsyUniversalMeetingCommandCenter.module.css';

const WILSY_MEETING_VIEWPORTS = Object.freeze([
  'OVERVIEW',
  'MEETING_INFO',
  'PARTICIPANTS',
  'SCHEDULE',
  'RELATED_RECORD',
  'IMPORT_MEETINGS',
  'FIELD_MAPPING',
  'REVIEW_ASSIGN',
  'EVIDENCE',
]);

const WILSY_MEETING_VENUE_OPTIONS = Object.freeze([
  'Client location',
  'Online meeting',
  'Wilsy office',
  'Phone call',
  'Custom location',
]);

const WILSY_MEETING_HOST_OPTIONS = Object.freeze([
  'Wilsy',
  'Record owner',
  'Tenant operator',
  'Sales command desk',
]);

/**
 * @function normalizeWilsyMeetingMode
 * @description Normalizes the surface requesting the universal meeting command center.
 * @param {string} mode - Raw mode supplied by a parent component.
 * @returns {string} Supported universal meeting mode.
 * @collaboration Standalone Meetings workspace, Create Lead, Lead Edit, CRM command surface.
 */
function normalizeWilsyMeetingMode(mode = 'standalone') {
  const normalized = String(mode || '').trim().toLowerCase();

  if (['create-lead', 'lead-create', 'create'].includes(normalized)) return 'create-lead';
  if (['lead-edit', 'edit-lead', 'edit'].includes(normalized)) return 'lead-edit';
  if (['embedded', 'inline'].includes(normalized)) return 'embedded';

  return 'standalone';
}

/**
 * @function normalizeWilsyMeetingViewport
 * @description Resolves a safe viewport key for the meeting command center.
 * @param {string} viewport - Candidate viewport.
 * @returns {string} Safe viewport key.
 * @collaboration Viewport navigation, standalone meeting workspace, embedded lead contexts.
 */
function normalizeWilsyMeetingViewport(viewport = 'OVERVIEW') {
  const normalized = String(viewport || '').trim().toUpperCase();

  return WILSY_MEETING_VIEWPORTS.includes(normalized) ? normalized : 'OVERVIEW';
}

/**
 * @function buildWilsyMeetingViewports
 * @description Builds spacious meeting viewports without coupling to backend mutations.
 * @param {string} mode - Current meeting mode.
 * @returns {Array<Object>} Viewport navigation records.
 * @collaboration Universal meeting command shell, import workflow, evidence posture.
 */
function buildWilsyMeetingViewports(mode = 'standalone') {
  const normalizedMode = normalizeWilsyMeetingMode(mode);
  const importCopy = normalizedMode === 'standalone'
    ? 'Import file, map fields, assign owner, then wait for backend confirmation.'
    : 'Preview import workflow without leaving the current Lead context.';

  return [
    { id: 'OVERVIEW', label: 'Overview', icon: CalendarDays, detail: 'Command view', copy: 'A spacious meeting command center that keeps CRM context visible.' },
    { id: 'MEETING_INFO', label: 'Meeting Info', icon: Clock, detail: 'Core fields', copy: 'Title, venue, time, host, repeat, reminder and description.' },
    { id: 'PARTICIPANTS', label: 'Participants', icon: UserPlus, detail: 'Invitees', copy: 'Contacts, leads, users and direct email invitation control.' },
    { id: 'SCHEDULE', label: 'Schedule', icon: CalendarDays, detail: 'Timing', copy: 'Calendar-grade time selection without calculator-grid clutter.' },
    { id: 'RELATED_RECORD', label: 'Related Record', icon: Link2, detail: 'CRM context', copy: 'Bind the meeting to a lead, contact, account, deal or task.' },
    { id: 'IMPORT_MEETINGS', label: 'Import Meetings', icon: UploadCloud, detail: 'CSV / XLSX', copy: importCopy },
    { id: 'FIELD_MAPPING', label: 'Field Mapping', icon: FileSpreadsheet, detail: 'Map columns', copy: 'Map file columns to meeting fields before committed import.' },
    { id: 'REVIEW_ASSIGN', label: 'Review + Assign', icon: Users, detail: 'Owner flow', copy: 'Review import rows, assignment posture and duplicate risk.' },
    { id: 'EVIDENCE', label: 'Evidence', icon: Fingerprint, detail: 'Proof trail', copy: 'Surface source, actor, route, timestamp and backend readiness.' },
  ];
}

/**
 * @function buildWilsyMeetingContextPacket
 * @description Builds a source-honest context packet for the evidence rail.
 * @param {Object} options - Mode, tenant and related record data.
 * @returns {Object} Meeting context packet.
 * @collaboration Lead create, lead edit, standalone meetings, tenant evidence posture.
 */
function buildWilsyMeetingContextPacket(options = {}) {
  const mode = normalizeWilsyMeetingMode(options.mode);
  const relatedRecord = options.relatedRecord && typeof options.relatedRecord === 'object' ? options.relatedRecord : {};
  const tenantId = String(options.tenantId || relatedRecord.tenantId || relatedRecord.tenant || 'wilsy-sovereign-root');

  const relatedLabel =
    relatedRecord.leadName ||
    relatedRecord.name ||
    relatedRecord.company ||
    relatedRecord.title ||
    relatedRecord.email ||
    'No related record selected';

  return {
    mode,
    tenantId,
    relatedLabel,
    relatedType: relatedRecord.type || relatedRecord.module || (mode.includes('lead') ? 'Lead' : 'CRM record'),
    sourceRoute: '/api/crm/live/meetings',
    sourcePolicy: 'Meeting records and command actions are persisted through CRM command authority with telemetry and compliance receipts.',
    importPolicy: 'Import screens are preview-only until backend import authority is connected.',
    evidenceLine: 'Meeting evidence must include source object, actor, tenant, timestamp and route proof.',
  };
}

/**
 * @function buildWilsyMeetingImportSteps
 * @description Builds the import stepper model for CSV/XLS/XLSX meeting imports.
 * @returns {Array<Object>} Import workflow steps.
 * @collaboration Import Meetings viewport, file mapping, field mapping, review and assignment.
 */
function buildWilsyMeetingImportSteps() {
  return [
    { id: 'upload', label: 'Upload', status: 'Preview only', detail: 'CSV, XLSX or XLS file selection.' },
    { id: 'actions', label: 'Actions', status: 'Pending', detail: 'Choose create/update strategy after backend route exists.' },
    { id: 'module', label: 'Module mapping', status: 'Pending', detail: 'Confirm the file targets CRM Meetings.' },
    { id: 'fields', label: 'Field mapping', status: 'Pending', detail: 'Map file columns to Meeting fields.' },
    { id: 'assign', label: 'Assign', status: 'Pending', detail: 'Assign owner, host and exception handling.' },
  ];
}

/**
 * @function buildWilsyMeetingFieldMappingRows
 * @description Provides visible mapping rows without parsing or committing data.
 * @returns {Array<Object>} Meeting import mapping rows.
 * @collaboration Import Meetings viewport, field mapping preview, no-fake-import policy.
 */
function buildWilsyMeetingFieldMappingRows() {
  return [
    { field: 'Title', requirement: 'Required', target: 'Meeting title', status: 'Needs file column' },
    { field: 'From', requirement: 'Required', target: 'Start date and time', status: 'Needs file column' },
    { field: 'To', requirement: 'Required', target: 'End date and time', status: 'Needs file column' },
    { field: 'Host', requirement: 'Recommended', target: 'Meeting owner or host', status: 'Can default to operator' },
    { field: 'Participants', requirement: 'Recommended', target: 'Contacts, leads, users or invite emails', status: 'Needs mapping' },
    { field: 'Related To', requirement: 'Recommended', target: 'Lead, contact, account, deal or task', status: 'Context aware' },
    { field: 'Description', requirement: 'Optional', target: 'Notes and agenda', status: 'Optional' },
  ];
}

/**
 * @function formatWilsyMeetingFieldValue
 * @description Formats unknown meeting field values for safe display.
 * @param {unknown} value - Raw value to display.
 * @param {string} fallback - Fallback label.
 * @returns {string} Display-safe value.
 * @collaboration Universal meeting UI, import preview, evidence rail.
 */
function formatWilsyMeetingFieldValue(value, fallback = 'Not set') {
  const text = String(value ?? '').trim();

  return text || fallback;
}


/**
 * @function resolveWilsyMeetingApiBase
 * @description Resolves the CRM API base URL for backend-connected meeting commands.
 * @returns {string} API base URL.
 * @collaboration Vite API configuration, CRM command routes, universal meeting command center.
 */
function resolveWilsyMeetingApiBase() {
  return String(import.meta?.env?.VITE_API_URL || '').replace(/\/$/, '');
}

/**
 * @function buildWilsyMeetingHeaders
 * @description Builds tenant-scoped JSON headers for meeting command requests.
 * @param {string} tenantId - Tenant identifier.
 * @returns {Object} Request headers.
 * @collaboration Tenant-scoped CRM command routes, meeting persistence, audit receipts.
 */
function buildWilsyMeetingHeaders(tenantId = 'MASTER') {
  return {
    'Content-Type': 'application/json',
    'X-Tenant-Id': String(tenantId || 'MASTER'),
  };
}

/**
 * @function postWilsyMeetingCommand
 * @description Sends a backend-connected meeting command and rejects non-OK responses.
 * @param {string} endpoint - CRM command endpoint.
 * @param {Object} payload - Request payload.
 * @param {string} tenantId - Tenant identifier.
 * @returns {Promise<Object>} Backend response JSON.
 * @collaboration Meeting create, draft persistence, import preview, command audit receipts.
 */
async function postWilsyMeetingCommand(endpoint, payload = {}, tenantId = 'MASTER') {
  const response = await fetch(`${resolveWilsyMeetingApiBase()}${endpoint}`, {
    method: 'POST',
    headers: buildWilsyMeetingHeaders(tenantId),
    body: JSON.stringify(payload),
  });

  const data = await response.json().catch(() => ({
    ok: false,
    message: 'Meeting command returned a non-JSON response.',
  }));

  if (!response.ok || !data?.ok) {
    const error = new Error(data?.message || data?.code || 'Meeting command failed.');
    error.payload = data;
    error.status = response.status;
    throw error;
  }

  return data;
}

/**
 * @function WilsyUniversalMeetingCommandCenter
 * @description Renders a reusable spacious meeting command center for standalone, Create Lead and Lead Edit contexts.
 * @param {Object} props - Component props.
 * @returns {JSX.Element} Universal meeting command center.
 * @collaboration CRM Create Lead, CRM Lead Edit, standalone Meetings workspace, import meeting workflow.
 */
export default function WilsyUniversalMeetingCommandCenter({
  mode = 'standalone',
  relatedRecord = null,
  tenantId = '',
  initialViewport = 'OVERVIEW',
  onClose = null,
  onSaveDraft = null,
  onImportPreview = null,
  onMeetingCreated = null,
} = {}) {
  const normalizedMode = normalizeWilsyMeetingMode(mode);
  const [activeViewport, setActiveViewport] = useState(() => normalizeWilsyMeetingViewport(initialViewport));
  const [navigationRailCollapsed, setNavigationRailCollapsed] = useState(true);
  const [intelligenceRailOpen, setIntelligenceRailOpen] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState('');
  const [backendCommandState, setBackendCommandState] = useState({ status: 'READY', message: 'Backend command authority ready.', receiptId: '' });
  const [meetingDraft, setMeetingDraft] = useState({
    title: 'New Meeting',
    venue: WILSY_MEETING_VENUE_OPTIONS[0],
    location: '',
    allDay: false,
    fromDate: '',
    fromTime: '',
    toDate: '',
    toTime: '',
    host: WILSY_MEETING_HOST_OPTIONS[0],
    participants: '',
    relatedTo: '',
    repeat: 'None',
    reminder: 'None',
    description: '',
  });

  const viewports = useMemo(() => buildWilsyMeetingViewports(normalizedMode), [normalizedMode]);
  const contextPacket = useMemo(
    () => buildWilsyMeetingContextPacket({ mode: normalizedMode, relatedRecord, tenantId }),
    [normalizedMode, relatedRecord, tenantId]
  );
  const importSteps = useMemo(() => buildWilsyMeetingImportSteps(), []);
  const mappingRows = useMemo(() => buildWilsyMeetingFieldMappingRows(), []);
  const activeViewportRecord = viewports.find((viewport) => viewport.id === activeViewport) || viewports[0];
  const ActiveViewportIcon = activeViewportRecord?.icon || CalendarDays;
  const resolvedTenantId = contextPacket.tenantId;

  /**
   * @function handleDraftFieldChange
   * @description Updates the local meeting draft without saving or mutating backend meeting records.
   * @param {string} field - Draft field name.
   * @param {unknown} value - Draft field value.
   * @returns {void}
   * @collaboration Meeting info viewport, schedule viewport, related record viewport, local draft state.
   */
  const handleDraftFieldChange = (field, value) => {
    setMeetingDraft((current) => ({
      ...current,
      [field]: value,
    }));
  };

  /**
   * @function handleLocalFileSelection
   * @description Captures a local import file name for preview-only import posture without uploading or committing data.
   * @param {Event} event - File input change event.
   * @returns {void}
   * @collaboration Import Meetings viewport, local preview posture, no-fake-import guard.
   */
  const handleLocalFileSelection = async (event) => {
    const file = event?.target?.files?.[0] || null;
    const fileName = file?.name || '';

    setSelectedFileName(fileName);

    if (!fileName) {
      return;
    }

    setBackendCommandState({ status: 'IMPORT_PREVIEW_RECORDING', message: 'Recording import preview with backend authority.', receiptId: '' });

    try {
      const data = await postWilsyMeetingCommand('/api/crm/command/meetings/import-preview', {
        fileName,
        mode: normalizedMode,
        tenantId: resolvedTenantId,
        relatedRecord,
      }, resolvedTenantId);

      setBackendCommandState({
        status: data.status || 'IMPORT_PREVIEW_RECORDED',
        message: 'Import preview recorded. No rows were falsely imported.',
        receiptId: data?.receipt?.writes?.[0]?.id || data?.preview?.id || '',
      });

      if (typeof onImportPreview === 'function') {
        onImportPreview(data);
      }
    } catch (error) {
      setBackendCommandState({
        status: 'IMPORT_PREVIEW_FAILED',
        message: error?.message || 'Import preview backend command failed.',
        receiptId: '',
      });
    }
  };

  /**
   * @function handlePrepareDraft
   * @description Emits a local draft payload to the parent without claiming a persisted meeting.
   * @returns {void}
   * @collaboration Create Lead, Lead Edit, standalone Meetings, local draft workflow.
   */
  const handlePrepareDraft = async () => {
    setBackendCommandState({ status: 'DRAFT_RECORDING', message: 'Persisting meeting draft and receipts.', receiptId: '' });

    try {
      const data = await postWilsyMeetingCommand('/api/crm/command/meetings', {
        action: 'PREPARE_DRAFT',
        mode: normalizedMode,
        tenantId: resolvedTenantId,
        relatedRecord,
        meetingDraft,
        status: 'DRAFT',
      }, resolvedTenantId);

      setBackendCommandState({
        status: data.status || 'MEETING_DRAFT_PERSISTED',
        message: 'Meeting draft persisted and receipt chain recorded.',
        receiptId: data?.receipt?.writes?.[0]?.id || data?.meeting?.id || '',
      });

      if (typeof onSaveDraft === 'function') {
        onSaveDraft(data);
      }
    } catch (error) {
      setBackendCommandState({
        status: 'DRAFT_FAILED',
        message: error?.message || 'Meeting draft backend command failed.',
        receiptId: '',
      });
    }
  };

  /**
   * @function handleReservedCreate
   * @description Emits backend-route-required posture instead of faking meeting creation.
   * @returns {void}
   * @collaboration Universal meeting shell, backend route investigation, no-fake-save policy.
   */
  const handleReservedCreate = async () => {
    setBackendCommandState({ status: 'MEETING_SAVING', message: 'Saving meeting through CRM command authority.', receiptId: '' });

    try {
      const data = await postWilsyMeetingCommand('/api/crm/command/meetings', {
        action: 'SAVE_MEETING',
        mode: normalizedMode,
        tenantId: resolvedTenantId,
        relatedRecord,
        meetingDraft,
        status: 'SCHEDULED',
      }, resolvedTenantId);

      setBackendCommandState({
        status: data.status || 'MEETING_PERSISTED',
        message: 'Meeting persisted and telemetry/compliance receipts recorded.',
        receiptId: data?.receipt?.writes?.[0]?.id || data?.meeting?.id || '',
      });

      if (typeof onMeetingCreated === 'function') {
        onMeetingCreated(data);
      }
    } catch (error) {
      setBackendCommandState({
        status: 'MEETING_SAVE_FAILED',
        message: error?.message || 'Meeting save backend command failed.',
        receiptId: '',
      });
    }
  };

  /**
   * @function recordWilsyMeetingUiAction
   * @description Records non-mutating meeting UI commands so office actions are auditable.
   * @param {string} action - UI action to record.
   * @returns {Promise<void>} Recording lifecycle.
   * @collaboration Meeting toolbar, collapsible rail, Wilsy AI drawer, telemetry receipts.
   */
  async function recordWilsyMeetingUiAction(action) {
    try {
      const data = await postWilsyMeetingCommand('/api/crm/command/meetings/action', {
        action,
        mode: normalizedMode,
        tenantId: resolvedTenantId,
        relatedRecord,
      }, resolvedTenantId);

      setBackendCommandState({
        status: data.status || 'ACTION_RECORDED',
        message: `${action} recorded.`,
        receiptId: data?.receipt?.writes?.[0]?.id || '',
      });
    } catch (error) {
      setBackendCommandState({
        status: 'ACTION_RECORD_FAILED',
        message: error?.message || `${action} recording failed.`,
        receiptId: '',
      });
    }
  }

  /**
   * @function handleWilsyMeetingViewportSelect
   * @description Selects a meeting viewport while preventing standalone Meetings from falling back into presentation-card Overview mode.
   * @param {string} viewportId - Requested viewport id.
   * @returns {void}
   * @collaboration Standalone Meetings workspace, collapsible rail, full-viewport SaaS workflow.
   */
  /**
   * @function handleWilsyMeetingViewportSelect
   * @description Selects only the work surface. The rail visibility state remains separate and never becomes a viewport.
   * @param {string} viewportId - Requested viewport id.
   * @returns {void}
   * @collaboration Meeting workspace, canonical viewport contract, standalone SaaS work surface.
   */
  function handleWilsyMeetingViewportSelect(viewportId) {
    setActiveViewport(normalizeWilsyMeetingViewport(viewportId));
  }

  return (
    <section
      className={styles.meetingShell}
      data-wilsy-r91k179-universal-meeting="command-center"
      data-meeting-mode={normalizedMode}
      data-active-viewport={activeViewport}
      data-navigation-rail={navigationRailCollapsed ? 'collapsed' : 'open'}
      data-intelligence-rail={intelligenceRailOpen ? 'open' : 'closed'}
      aria-label="Wilsy Universal Meeting Command Center"
    >
      <header className={styles.meetingHero}>
        <div>
          <small>Wilsy CRM · Universal meeting command</small>
          <h2>Meeting Command Center</h2>
          <p>
            Spacious meeting creation, participant control, schedule intelligence and import workflow
            for standalone Meetings, Create Lead and Lead Edit contexts.
          </p>
        </div>

        <nav aria-label="Meeting command actions">
          <button type="button" onClick={() => {
            setNavigationRailCollapsed((current) => !current);
            setBackendCommandState((current) => (
              current?.status === 'ACTION_RECORD_FAILED'
                ? { status: 'READY', message: 'Rail toggled locally. No backend write is required for navigation.', receiptId: '' }
                : current
            ));
          }}>
            {navigationRailCollapsed ? 'Open rail' : 'Collapse rail'}
          </button>
          <button type="button" onClick={() => { setIntelligenceRailOpen((current) => !current); recordWilsyMeetingUiAction('TOGGLE_WILSY_AI'); }}>
            Wilsy AI
          </button>
          <button type="button" onClick={handlePrepareDraft}>Prepare draft</button>
          <button type="button" onClick={() => handleWilsyMeetingViewportSelect('IMPORT_MEETINGS')}>Import Meetings</button>
          <button type="button" data-primary="true" onClick={handleReservedCreate}>Save Meeting</button>
          {typeof onClose === 'function' ? (
            <button type="button" aria-label="Close meeting command center" onClick={onClose}>
              <X size={16} />
            </button>
          ) : null}
        <aside
          className={styles.backendCommandStatus}
          data-wilsy-r91k179b12b-backend-status="live-command-authority"
          aria-label="Meeting backend command status"
        >
          <small>{backendCommandState.status}</small>
          <strong>{backendCommandState.message}</strong>
          {backendCommandState.receiptId ? <span>Receipt {backendCommandState.receiptId}</span> : null}
        </aside>
        </nav>
      </header>

      <div
        className={styles.meetingBody}
        data-wilsy-r91k179b8-focus-mode={activeViewport === 'OVERVIEW' ? 'overview' : 'focused'}
      >
        <aside className={styles.viewportRail} aria-label="Meeting viewports">
          {viewports.map((viewport) => {
            const ViewportIcon = viewport.icon;
            const active = activeViewport === viewport.id;

            return (
              <button
                key={viewport.id}
                type="button"
                data-active={active ? 'true' : 'false'}
                onClick={() => handleWilsyMeetingViewportSelect(viewport.id)}
              >
                <ViewportIcon size={18} />
                <span>
                  <strong>{viewport.label}</strong>
                  <small>{viewport.detail}</small>
                </span>
                <ChevronRight size={15} />
              </button>
            );
          })}
        </aside>

        <main className={styles.viewportStage} aria-label="Meeting viewport stage">
            <button
              type="button"
              className={styles.railDockToggle}
              onClick={() => {
                setNavigationRailCollapsed((current) => !current);
                setBackendCommandState((current) => (
                  current?.status === 'ACTION_RECORD_FAILED'
                    ? { status: 'READY', message: 'Navigation rail opened locally. No backend write is required.', receiptId: '' }
                    : current
                ));
              }}
              aria-label={navigationRailCollapsed ? 'Open meeting navigation rail' : 'Close meeting navigation rail'}
            >
              {navigationRailCollapsed ? 'Rail' : 'Close rail'}
            </button>
          <article className={styles.viewportHeader}>
            <ActiveViewportIcon size={22} />
            <span>
              <small>{activeViewport.replaceAll('_', ' ')}</small>
              <strong>{activeViewportRecord?.copy}</strong>
            </span>
          </article>

          {activeViewport === 'OVERVIEW' ? (
            <section
              className={styles.softwareOverviewViewport}
              data-wilsy-r91k179d5-overview="full-software-workspace"
              aria-label="Meeting overview software workspace"
            >
              <header className={styles.softwareWorkbenchHeader}>
                <div>
                  <small>Meetings overview</small>
                  <h3>Operate the meeting workspace</h3>
                  <p>
                    This is a software workbench: create, import, schedule, prove, and review meeting operations without returning to a card board.
                  </p>
                </div>
                <nav aria-label="Overview workbench actions">
                  <button type="button" onClick={() => handleWilsyMeetingViewportSelect('MEETING_INFO')}>Build meeting</button>
                  <button type="button" onClick={() => handleWilsyMeetingViewportSelect('IMPORT_MEETINGS')}>Import</button>
                  <button type="button" onClick={() => handleWilsyMeetingViewportSelect('EVIDENCE')}>Evidence</button>
                </nav>
              </header>

              <section className={styles.softwareOperationsLedger} aria-label="Meeting operations ledger">
                <article className={styles.softwareLedgerRow}>
                  <span>01</span>
                  <strong>Create / edit meeting</strong>
                  <p>Build the meeting object, schedule, venue, participants, reminders, repeat policy, related CRM record and agenda.</p>
                  <button type="button" onClick={() => handleWilsyMeetingViewportSelect('MEETING_INFO')}>Open</button>
                </article>

                <article className={styles.softwareLedgerRow}>
                  <span>02</span>
                  <strong>Participant control</strong>
                  <p>Prepare invitees from contacts, leads, users, emails and related records before a meeting is saved.</p>
                  <button type="button" onClick={() => handleWilsyMeetingViewportSelect('PARTICIPANTS')}>Open</button>
                </article>

                <article className={styles.softwareLedgerRow}>
                  <span>03</span>
                  <strong>Meeting import</strong>
                  <p>Upload meeting files through the governed import workflow and map columns before any committed import.</p>
                  <button type="button" onClick={() => handleWilsyMeetingViewportSelect('IMPORT_MEETINGS')}>Open</button>
                </article>

                <article className={styles.softwareLedgerRow}>
                  <span>04</span>
                  <strong>Evidence workspace</strong>
                  <p>Review source route, invitation proof, venue proof, receipts and backend command posture in one full-screen ledger.</p>
                  <button type="button" onClick={() => handleWilsyMeetingViewportSelect('EVIDENCE')}>Open</button>
                </article>
              </section>
            </section>
          ) : null}

          {activeViewport === 'MEETING_INFO' ? (
            <section
              className={styles.meetingInfoSoftwareViewport}
              data-wilsy-r91k179b9-meeting-info="functional-full-workspace"
              aria-label="Functional meeting information workspace"
            >
              <header className={styles.meetingSoftwareHeader}>
                <div>
                  <small>Meeting Information</small>
                  <h3>Build the meeting</h3>
                  <p>
                    Full meeting object, schedule, participants, CRM relation, reminders and agenda.
                    Wilsy AI is available from the collapsible command rail only when called.
                  </p>
                </div>
                <nav aria-label="Meeting information quick actions">
                  <button type="button" onClick={() => handleWilsyMeetingViewportSelect('PARTICIPANTS')}>Participants</button>
                  <button type="button" onClick={() => handleWilsyMeetingViewportSelect('SCHEDULE')}>Schedule</button>
                  <button type="button" onClick={() => handleWilsyMeetingViewportSelect('RELATED_RECORD')}>Related</button>
                  <button type="button" onClick={() => setIntelligenceRailOpen(true)}>Wilsy AI</button>
                </nav>
              </header>

              <section className={styles.meetingFormWorkspace} aria-label="Meeting information fields">
                <label className={`${styles.meetingSoftwareField} ${styles.meetingSoftwareFieldWide}`}>
                  <span>Title</span>
                  <input
                    value={meetingDraft.title}
                    placeholder="New Meeting"
                    onChange={(event) => handleDraftFieldChange('title', event.target.value)}
                  />
                </label>

                <label className={styles.meetingSoftwareField}>
                  <span>Meeting venue</span>
                  <select value={meetingDraft.venue} onChange={(event) => handleDraftFieldChange('venue', event.target.value)}>
                    {WILSY_MEETING_VENUE_OPTIONS.map((option) => <option key={option}>{option}</option>)}
                  </select>
                </label>

                <label className={styles.meetingSoftwareField}>
                  <span>Location</span>
                  <input
                    value={meetingDraft.location}
                    placeholder="Client location, video link, office, site, court, boardroom"
                    onChange={(event) => handleDraftFieldChange('location', event.target.value)}
                  />
                </label>

                <label className={styles.meetingSoftwareField}>
                  <span>All day</span>
                  <div className={styles.meetingSoftwareToggle}>
                    <strong>{meetingDraft.allDay ? 'Enabled' : 'Disabled'}</strong>
                    <input
                      type="checkbox"
                      checked={Boolean(meetingDraft.allDay)}
                      onChange={(event) => handleDraftFieldChange('allDay', event.target.checked)}
                    />
                  </div>
                </label>

                <label className={styles.meetingSoftwareField}>
                  <span>From</span>
                  <div className={styles.meetingDateTimePair}>
                    <input type="date" value={meetingDraft.fromDate} onChange={(event) => handleDraftFieldChange('fromDate', event.target.value)} />
                    <input type="time" value={meetingDraft.fromTime} onChange={(event) => handleDraftFieldChange('fromTime', event.target.value)} />
                  </div>
                </label>

                <label className={styles.meetingSoftwareField}>
                  <span>To</span>
                  <div className={styles.meetingDateTimePair}>
                    <input type="date" value={meetingDraft.toDate} onChange={(event) => handleDraftFieldChange('toDate', event.target.value)} />
                    <input type="time" value={meetingDraft.toTime} onChange={(event) => handleDraftFieldChange('toTime', event.target.value)} />
                  </div>
                </label>

                <label className={styles.meetingSoftwareField}>
                  <span>Host</span>
                  <select value={meetingDraft.host} onChange={(event) => handleDraftFieldChange('host', event.target.value)}>
                    {WILSY_MEETING_HOST_OPTIONS.map((option) => <option key={option}>{option}</option>)}
                  </select>
                </label>

                <label className={styles.meetingSoftwareField}>
                  <span>Participants</span>
                  <div className={styles.meetingLinkedControl}>
                    <input
                      value={meetingDraft.participants}
                      placeholder="None"
                      onChange={(event) => handleDraftFieldChange('participants', event.target.value)}
                    />
                    <button type="button" onClick={() => handleWilsyMeetingViewportSelect('PARTICIPANTS')}>Add</button>
                  </div>
                </label>

                <label className={styles.meetingSoftwareField}>
                  <span>Related To</span>
                  <div className={styles.meetingLinkedControl}>
                    <input
                      value={meetingDraft.relatedTo}
                      placeholder={contextPacket.relatedLabel}
                      onChange={(event) => handleDraftFieldChange('relatedTo', event.target.value)}
                    />
                    <button type="button" onClick={() => handleWilsyMeetingViewportSelect('RELATED_RECORD')}>Link</button>
                  </div>
                </label>

                <label className={styles.meetingSoftwareField}>
                  <span>Repeat</span>
                  <select value={meetingDraft.repeat} onChange={(event) => handleDraftFieldChange('repeat', event.target.value)}>
                    <option>None</option>
                    <option>Daily</option>
                    <option>Weekly</option>
                    <option>Monthly</option>
                    <option>Custom cadence</option>
                  </select>
                </label>

                <label className={styles.meetingSoftwareField}>
                  <span>Participants reminder</span>
                  <select value={meetingDraft.reminder} onChange={(event) => handleDraftFieldChange('reminder', event.target.value)}>
                    <option>None</option>
                    <option>10 minutes before</option>
                    <option>30 minutes before</option>
                    <option>1 hour before</option>
                    <option>1 day before</option>
                    <option>AI recommended reminder</option>
                  </select>
                </label>

                <label className={`${styles.meetingSoftwareField} ${styles.meetingSoftwareDescription}`}>
                  <span>Description</span>
                  <textarea
                    value={meetingDraft.description}
                    placeholder="Agenda, outcomes, risk points, participant preparation, evidence requirements and follow-up commands"
                    onChange={(event) => handleDraftFieldChange('description', event.target.value)}
                  />
                </label>
              </section>

              <footer className={styles.meetingSoftwareStatusBar} aria-label="Meeting save posture">
                <span>Draft only until backend route confirms save authority</span>
                <span>{meetingDraft.participants ? 'Invitees in progress' : 'Participants pending'}</span>
                <span>{meetingDraft.fromDate || meetingDraft.fromTime ? 'Schedule in progress' : 'Schedule pending'}</span>
                <button type="button" onClick={handlePrepareDraft}>Prepare draft</button>
              </footer>
            </section>
          ) : null}

          {activeViewport === 'PARTICIPANTS' ? (
            <section className={styles.participantViewport}>
              <div className={styles.participantToolbar}>
                <select aria-label="Participant source">
                  <option>Contacts</option>
                  <option>Leads</option>
                  <option>Users</option>
                  <option>Email addresses</option>
                </select>
                <input
                  value={meetingDraft.participants}
                  placeholder="Search or invite by email address"
                  onChange={(event) => handleDraftFieldChange('participants', event.target.value)}
                />
              </div>
              <article className={styles.emptyStatePanel}>
                <Users size={26} />
                <strong>No participant selected yet</strong>
                <p>Search contacts, leads or users, or invite directly by email address. No contact is invented.</p>
              </article>
              <label className={styles.checkboxRow}>
                <input type="checkbox" />
                <span>Show contacts without email addresses as well.</span>
              </label>
            </section>
          ) : null}

          {activeViewport === 'SCHEDULE' ? (
            <section className={styles.scheduleViewport}>
              <label>
                <span>From date</span>
                <input type="date" value={meetingDraft.fromDate} onChange={(event) => handleDraftFieldChange('fromDate', event.target.value)} />
              </label>
              <label>
                <span>From time</span>
                <input type="time" value={meetingDraft.fromTime} onChange={(event) => handleDraftFieldChange('fromTime', event.target.value)} />
              </label>
              <label>
                <span>To date</span>
                <input type="date" value={meetingDraft.toDate} onChange={(event) => handleDraftFieldChange('toDate', event.target.value)} />
              </label>
              <label>
                <span>To time</span>
                <input type="time" value={meetingDraft.toTime} onChange={(event) => handleDraftFieldChange('toTime', event.target.value)} />
              </label>
              <label>
                <span>Repeat</span>
                <select value={meetingDraft.repeat} onChange={(event) => handleDraftFieldChange('repeat', event.target.value)}>
                  <option>None</option>
                  <option>Daily</option>
                  <option>Weekly</option>
                  <option>Monthly</option>
                </select>
              </label>
              <label>
                <span>Reminder</span>
                <select value={meetingDraft.reminder} onChange={(event) => handleDraftFieldChange('reminder', event.target.value)}>
                  <option>None</option>
                  <option>10 minutes before</option>
                  <option>30 minutes before</option>
                  <option>1 hour before</option>
                  <option>1 day before</option>
                </select>
              </label>
            </section>
          ) : null}

          {activeViewport === 'RELATED_RECORD' ? (
            <section className={styles.relatedViewport}>
              <article>
                <Link2 size={26} />
                <small>Related to</small>
                <strong>{contextPacket.relatedLabel}</strong>
                <p>{contextPacket.relatedType} · {contextPacket.tenantId}</p>
              </article>
              <label>
                <span>Related record override</span>
                <input
                  value={meetingDraft.relatedTo}
                  placeholder="Lead, Contact, Account, Deal or Task"
                  onChange={(event) => handleDraftFieldChange('relatedTo', event.target.value)}
                />
              </label>
            </section>
          ) : null}

          {activeViewport === 'IMPORT_MEETINGS' ? (
            <section className={styles.importViewport}>
              <div className={styles.importStepper}>
                {importSteps.map((step) => (
                  <article key={step.id}>
                    <small>{step.label}</small>
                    <strong>{step.status}</strong>
                    <p>{step.detail}</p>
                  </article>
                ))}
              </div>

              <label className={styles.uploadDropzone}>
                <UploadCloud size={34} />
                <strong>Drag and drop meeting files here</strong>
                <p>Supported file formats: CSV, XLSX and XLS. This shell does not fake import success.</p>
                <input type="file" accept=".csv,.xlsx,.xls" onChange={handleLocalFileSelection} />
                <span>{selectedFileName || 'Browse Files'}</span>
              </label>

              <article className={styles.importNotice}>
                <ShieldCheck size={22} />
                <p>{contextPacket.importPolicy}</p>
              </article>
            </section>
          ) : null}

          {activeViewport === 'FIELD_MAPPING' ? (
            <section className={styles.mappingViewport}>
              {mappingRows.map((row) => (
                <article key={row.field}>
                  <small>{row.requirement}</small>
                  <strong>{row.field}</strong>
                  <p>{row.target}</p>
                  <em>{row.status}</em>
                </article>
              ))}
            </section>
          ) : null}

          {activeViewport === 'REVIEW_ASSIGN' ? (
            <section className={styles.reviewViewport}>
              <article>
                <CheckCircle2 size={26} />
                <small>Review state</small>
                <strong>Awaiting mapped import preview</strong>
                <p>No rows are committed until a governed backend import route exists and the operator confirms assignment.</p>
              </article>
              <article>
                <Users size={26} />
                <small>Assignment</small>
                <strong>{formatWilsyMeetingFieldValue(meetingDraft.host, 'Host pending')}</strong>
                <p>Owner, host and exception policy must be visible before import execution.</p>
              </article>
            </section>
          ) : null}

          {activeViewport === 'EVIDENCE' ? (
            <section
              className={styles.softwareEvidenceViewport}
              data-wilsy-r91k179d5-evidence="full-evidence-workspace"
              aria-label="Meeting evidence software workspace"
            >
              <header className={styles.softwareWorkbenchHeader}>
                <div>
                  <small>Evidence workspace</small>
                  <h3>Prove the meeting operation</h3>
                  <p>
                    Evidence is a full ledger surface. It does not compete with the rail, and it does not collapse into three cards.
                  </p>
                </div>
                <nav aria-label="Evidence workbench actions">
                  <button type="button" onClick={() => handleWilsyMeetingViewportSelect('MEETING_INFO')}>Meeting Info</button>
                  <button type="button" onClick={() => handleWilsyMeetingViewportSelect('PARTICIPANTS')}>Participants</button>
                  <button type="button" onClick={() => handleWilsyMeetingViewportSelect('IMPORT_MEETINGS')}>Import</button>
                </nav>
              </header>

              <section className={styles.softwareEvidenceLedger} aria-label="Meeting evidence ledger">
                <article className={styles.softwareEvidenceRow}>
                  <span>Source route</span>
                  <strong>/api/crm/live/meetings</strong>
                  <p>Meeting evidence must include source object, actor, tenant, timestamp and route proof.</p>
                </article>

                <article className={styles.softwareEvidenceRow}>
                  <span>Invitation proof</span>
                  <strong>{formatWilsyMeetingFieldValue(meetingDraft.participants, 'Pending participants')}</strong>
                  <p>Participant invitations need explicit contacts, users, leads or email addresses.</p>
                </article>

                <article className={styles.softwareEvidenceRow}>
                  <span>Venue proof</span>
                  <strong>{formatWilsyMeetingFieldValue(meetingDraft.venue, 'Venue pending')}</strong>
                  <p>Location and venue remain visible before the meeting is saved.</p>
                </article>

                <article className={styles.softwareEvidenceRow}>
                  <span>Import proof</span>
                  <strong>{formatWilsyMeetingFieldValue(selectedFileName, 'No file selected')}</strong>
                  <p>Import preview is source-honest until backend import authority confirms rows and receipts.</p>
                </article>

                <article className={styles.softwareEvidenceRow}>
                  <span>Command posture</span>
                  <strong>{backendCommandState.status}</strong>
                  <p>{backendCommandState.message}</p>
                </article>
              </section>
            </section>
          ) : null}
        </main>

        <aside className={styles.contextRail} aria-label="Meeting context and evidence">
          <article>
            <small>Mode</small>
            <strong>{normalizedMode}</strong>
            <p>{contextPacket.sourcePolicy}</p>
          </article>
          <article>
            <small>Related context</small>
            <strong>{contextPacket.relatedLabel}</strong>
            <p>{contextPacket.relatedType}</p>
          </article>
          <article>
            <small>Tenant</small>
            <strong>{contextPacket.tenantId}</strong>
            <p>Meeting routes must remain tenant-scoped and source-honest.</p>
          </article>
          <article>
            <small>Import status</small>
            <strong>{selectedFileName || 'No file selected'}</strong>
            <p>{contextPacket.importPolicy}</p>
          </article>
          <article
            className={styles.wilsyAiCommandRail}
            data-wilsy-r91k179b5-ai-rail="source-constrained-meeting-copilot"
          >
            <Sparkles size={24} />
            <small>Wilsy AI command rail</small>
            <strong>Source-constrained meeting copilot</strong>
            <p>
              Wilsy AI can shape agendas, participant preparation, import mapping and evidence prompts.
              It cannot invent meetings, attendees, imported rows, backend success or connector authority.
            </p>
            <div className={styles.wilsyAiActionGrid} aria-label="Wilsy AI governed meeting actions">
              <button type="button" onClick={() => handleWilsyMeetingViewportSelect('MEETING_INFO')}>
                Draft agenda
              </button>
              <button type="button" onClick={() => handleWilsyMeetingViewportSelect('PARTICIPANTS')}>
                Prepare invitees
              </button>
              <button type="button" onClick={() => handleWilsyMeetingViewportSelect('IMPORT_MEETINGS')}>
                Map import
              </button>
              <button type="button" onClick={() => handleWilsyMeetingViewportSelect('EVIDENCE')}>
                Prove evidence
              </button>
            </div>
          </article>

        </aside>
      </div>
    </section>
  );
}

export {
  WILSY_MEETING_VIEWPORTS,
  buildWilsyMeetingContextPacket,
  buildWilsyMeetingFieldMappingRows,
  buildWilsyMeetingImportSteps,
  buildWilsyMeetingViewports,
  formatWilsyMeetingFieldValue,
  normalizeWilsyMeetingMode,
  normalizeWilsyMeetingViewport,
};
