/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM MEETINGS WORKSPACE                                                                                     ║
 * ║ LIVE MEETING RECORDS | COMMAND CRUD | IMPORT POSTURE | EVIDENCE RAIL | OPERATOR-FIRST WORKBENCH                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/crm/meeting/workspace/WilsyMeetingsWorkspace.jsx ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION                                                                                                          ║
 * ║ 1. Wilson Khanyezi - Mandated a usable CRM Meetings workspace using the existing backend source and command files.     ║
 * ║ 2. AI Engineering - Consolidated duplicate workspace layers into one live-record workbench with guarded CRUD flows.    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Wilsy OS CRM Meetings workspace.
 * This component keeps meetings as a full CRM module page, reuses the existing live and command routes,
 * and avoids fabricated records or fake import success.
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ArrowLeft,
  CalendarDays,
  FileSpreadsheet,
  Fingerprint,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  RefreshCcw,
  Search,
  Sparkles,
  Trash2,
} from 'lucide-react';
import WilsyMeetingCapsuleView from './WilsyMeetingCapsuleView';
import WilsyMeetingEditor from './WilsyMeetingEditor';
import WilsyMeetingEvidenceWorkspace from './WilsyMeetingEvidenceWorkspace';
import WilsyMeetingImportWorkspace from './WilsyMeetingImportWorkspace';
import WilsyMeetingsOverview from './WilsyMeetingsOverview';
import styles from './WilsyMeetingsWorkspace.module.css';

/**
 * @function buildWilsyMeetingsModuleTabs
 * @description Builds the concise Meetings module rail model.
 * @returns {Array<Object>} Rail tab records.
 * @collaboration CRM Meetings rail, operator navigation, Wilsy OS module surface.
 */
function buildWilsyMeetingsModuleTabs() {
  return [
    { id: 'overview', label: 'Records', icon: CalendarDays },
    { id: 'create', label: 'Create', icon: Plus },
    { id: 'import', label: 'Import', icon: FileSpreadsheet },
    { id: 'evidence', label: 'Evidence', icon: Fingerprint },
  ];
}

/**
 * @function resolveWilsyMeetingsApiBase
 * @description Resolves the API base for Meetings live and command routes.
 * @returns {string} API base URL with no trailing slash.
 * @collaboration Vite runtime, CRM live routes, CRM command routes.
 */
function resolveWilsyMeetingsApiBase() {
  return String(import.meta.env.VITE_API_URL || 'http://localhost:5050').replace(/\/$/, '');
}

/**
 * @function resolveWilsyMeetingsTenantId
 * @description Resolves a tenant id from the current CRM tenant configuration.
 * @param {Object} tenantConfig - Tenant configuration.
 * @returns {string} Tenant id.
 * @collaboration Tenant context, meeting live route, command evidence headers.
 */
function resolveWilsyMeetingsTenantId(tenantConfig = {}) {
  return String(
    tenantConfig.tenantId ||
      tenantConfig.id ||
      tenantConfig.tenantKey ||
      tenantConfig.slug ||
      tenantConfig.name ||
      'wilsy-sovereign-root'
  ).trim() || 'wilsy-sovereign-root';
}

/**
 * @function resolveWilsyMeetingsOperator
 * @description Builds operator evidence used by destructive Meeting commands.
 * @param {Object} tenantConfig - Tenant configuration.
 * @returns {Object} Operator evidence.
 * @collaboration CRM command routes, tenant-scoped delete payloads, audit posture.
 */
function resolveWilsyMeetingsOperator(tenantConfig = {}) {
  const tenantId = resolveWilsyMeetingsTenantId(tenantConfig);

  return {
    tenantId,
    operatorId: tenantConfig.operatorId || tenantConfig.userId || tenantConfig.ownerId || 'wilsy-local-operator',
    operatorEmail: tenantConfig.operatorEmail || tenantConfig.email || '',
    operatorRole: tenantConfig.operatorRole || tenantConfig.role || 'OPERATOR',
  };
}

/**
 * @function normalizeWilsyMeetingsPayload
 * @description Normalizes live Meetings payload variants into record arrays.
 * @param {Object|Array} payload - Live route payload or raw record list.
 * @returns {Array<Object>} Meeting records.
 * @collaboration /api/crm/live/meetings, CRMDashboard preloaded records, source-honest display.
 */
function normalizeWilsyMeetingsPayload(payload = {}) {
  const records = Array.isArray(payload)
    ? payload
    : Array.isArray(payload.records)
      ? payload.records
      : Array.isArray(payload.data)
        ? payload.data
        : Array.isArray(payload.meetings)
          ? payload.meetings
          : [];

  return records.filter((record) => record && typeof record === 'object');
}

/**
 * @function resolveWilsyMeetingRecordId
 * @description Resolves a stable Meeting id from supported backend record variants.
 * @param {Object|string} meeting - Meeting record or id.
 * @returns {string} Meeting id.
 * @collaboration Records list, capsule drill-in, edit, delete and selection state.
 */
function resolveWilsyMeetingRecordId(meeting = {}) {
  if (typeof meeting === 'string') return meeting.trim();
  return String(meeting.recordId || meeting.meetingId || meeting.id || meeting._id || '').trim();
}

/**
 * @function resolveWilsyMeetingTitle
 * @description Resolves the operator-facing title for a Meeting record.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Meeting title.
 * @collaboration Delete verification, selected meeting capsule, user-facing feedback.
 */
function resolveWilsyMeetingTitle(meeting = {}) {
  return String(
    meeting.title ||
      meeting.subject ||
      meeting.meetingTitle ||
      meeting.name ||
      meeting.relatedName ||
      'Untitled Meeting'
  ).trim();
}

/**
 * @function mergeWilsyMeetingRecord
 * @description Upserts a saved Meeting into the current local records array.
 * @param {Array<Object>} records - Current records.
 * @param {Object} meeting - Saved Meeting.
 * @returns {Array<Object>} Updated records.
 * @collaboration Meeting editor save receipts, records list, live refresh fallback.
 */
function mergeWilsyMeetingRecord(records = [], meeting = {}) {
  const recordId = resolveWilsyMeetingRecordId(meeting);
  if (!recordId) return records;

  const nextRecords = Array.isArray(records) ? [...records] : [];
  const index = nextRecords.findIndex((record) => resolveWilsyMeetingRecordId(record) === recordId);

  if (index >= 0) {
    nextRecords[index] = { ...nextRecords[index], ...meeting };
    return nextRecords;
  }

  return [meeting, ...nextRecords];
}

/**
 * @function filterWilsyMeetingsRecords
 * @description Filters Meeting records with one workspace search term.
 * @param {Array<Object>} records - Meeting records.
 * @param {string} searchTerm - Search term.
 * @returns {Array<Object>} Filtered records.
 * @collaboration Topbar search, overview work queue, source-honest scanning.
 */
function filterWilsyMeetingsRecords(records = [], searchTerm = '') {
  const needle = String(searchTerm || '').trim().toLowerCase();
  if (!needle) return records;

  return records.filter((record) => JSON.stringify(record || {}).toLowerCase().includes(needle));
}

/**
 * @function buildWilsyMeetingsCommandHeaders
 * @description Builds tenant and operator headers for Meeting command requests.
 * @param {Object} tenantConfig - Tenant configuration.
 * @returns {Object} Command request headers.
 * @collaboration CORS posture, command route audit, tenant-scoped destructive actions.
 */
function buildWilsyMeetingsCommandHeaders(tenantConfig = {}) {
  const operator = resolveWilsyMeetingsOperator(tenantConfig);

  return {
    Accept: 'application/json',
    'Content-Type': 'application/json',
    'X-Tenant-Id': operator.tenantId,
    'X-Wilsy-Tenant-ID': operator.tenantId,
    'X-Operator-ID': operator.operatorId,
    'X-Operator-Email': operator.operatorEmail,
    'X-Operator-Role': operator.operatorRole,
    'X-Wilsy-Account-Command': 'MEETING_WORKSPACE_COMMAND',
  };
}

/**
 * @function buildWilsyMeetingDeletePayload
 * @description Builds the verified delete payload for one Meeting record.
 * @param {Object} args - Delete payload arguments.
 * @returns {Object} Delete command payload.
 * @collaboration DELETE /api/crm/command/meetings/:id, ProductionHardening bridge, evidence trail.
 */
function buildWilsyMeetingDeletePayload({ tenantConfig = {}, recordId = '', note = '', meeting = {}, bulk = false } = {}) {
  const operator = resolveWilsyMeetingsOperator(tenantConfig);
  const generatedAt = new Date().toISOString();
  const commandSurface = bulk ? 'MEETING_WORKSPACE_BULK_DELETE' : 'MEETING_WORKSPACE_DELETE';

  const institutionalHeaders = {
    tenantId: operator.tenantId,
    operatorId: operator.operatorId,
    operatorEmail: operator.operatorEmail,
    operatorRole: operator.operatorRole,
    actor: operator.operatorId,
    actorEmail: operator.operatorEmail,
    actorRole: operator.operatorRole,
    commandSurface,
    sourceRoute: `/api/crm/command/meetings/${recordId}`,
    liveRoute: '/api/crm/live/meetings',
    evidenceRoute: '/api/crm/live/evidence',
    recordId,
    meetingId: recordId,
    generatedAt,
  };

  return {
    action: bulk ? 'BULK_DELETE_MEETING' : 'DELETE_MEETING',
    commandSurface,
    module: 'meetings',
    tenantId: operator.tenantId,
    recordId,
    meetingId: recordId,
    verificationNote: note,
    operatorContext: operator,
    institutionalHeaders,
    strikePayload: {
      headers: institutionalHeaders,
      institutionalHeaders,
      action: bulk ? 'BULK_DELETE_MEETING' : 'DELETE_MEETING',
      module: 'meetings',
      tenantId: operator.tenantId,
      recordId,
      meetingId: recordId,
      reason: note,
      meeting,
      generatedAt,
    },
    meeting: {
      ...meeting,
      tenantId: operator.tenantId,
      recordId,
      meetingId: recordId,
    },
  };
}

/**
 * @function resolveWilsyMeetingsBackHandler
 * @description Resolves the parent callback for leaving the Meetings module.
 * @param {Object} props - Component props.
 * @returns {Function} Back handler.
 * @collaboration CRMDashboard legacy host, SaaS workbench host, full module host.
 */
function resolveWilsyMeetingsBackHandler(props = {}) {
  return props.onBackToCrm || props.onBackHome || props.onClose || (() => {});
}

/**
 * @function WilsyMeetingsWorkspace
 * @description Renders the CRM Meetings module with live records, create/edit, import posture, evidence and verified delete flows.
 * @param {Object} props - Workspace props.
 * @returns {JSX.Element} Meetings workspace.
 * @collaboration CRMDashboard, CRM live meetings route, Meeting command CRUD routes, source-honest operator workflow.
 */
export default function WilsyMeetingsWorkspace(props = {}) {
  const { tenantConfig = {}, records = [], meetings: propMeetings = [], loading = false, onSync } = props;
  const initialRecords = useMemo(
    () => normalizeWilsyMeetingsPayload(propMeetings.length ? propMeetings : records),
    [propMeetings, records]
  );

  const [activeView, setActiveView] = useState('overview');
  const [railCollapsed, setRailCollapsed] = useState(false);
  const [meetings, setMeetings] = useState(initialRecords);
  const [meetingsLoading, setMeetingsLoading] = useState(Boolean(loading));
  const [meetingsError, setMeetingsError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMeeting, setSelectedMeeting] = useState(null);
  const [selectedMeetingIds, setSelectedMeetingIds] = useState([]);
  const [deleteState, setDeleteState] = useState({
    open: false,
    ids: [],
    note: '',
    busy: false,
    status: '',
    message: '',
  });
  const [wilsyAiOpen, setWilsyAiOpen] = useState(false);

  const tabs = useMemo(() => buildWilsyMeetingsModuleTabs(), []);
  const apiBase = useMemo(() => resolveWilsyMeetingsApiBase(), []);
  const tenantId = resolveWilsyMeetingsTenantId(tenantConfig);
  const tenantName = tenantConfig.name || tenantConfig.tenantName || tenantConfig.companyName || 'Wilsy OS';
  const filteredMeetings = useMemo(
    () => filterWilsyMeetingsRecords(meetings, searchTerm),
    [meetings, searchTerm]
  );
  const backToCrm = resolveWilsyMeetingsBackHandler(props);
  const selectedMeetingTitle = selectedMeeting ? resolveWilsyMeetingTitle(selectedMeeting) : 'No meeting selected';

  useEffect(() => {
    if (initialRecords.length > 0) {
      setMeetings(initialRecords);
    }
  }, [initialRecords]);

  /**
   * @function refreshMeetings
   * @description Refreshes live Meeting records from the backend route.
   * @returns {Promise<void>} Refresh completion.
   * @collaboration /api/crm/live/meetings, source posture, records cockpit.
   */
  const refreshMeetings = useCallback(async () => {
    setMeetingsLoading(true);
    setMeetingsError('');

    try {
      const response = await fetch(`${apiBase}/api/crm/live/meetings`, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
          'X-Tenant-Id': tenantId,
          'X-Wilsy-Tenant-ID': tenantId,
        },
        credentials: 'include',
      });

      const payload = await response.json().catch(() => ({}));

      if (!response.ok || payload?.ok === false) {
        throw new Error(payload?.message || payload?.error || `Meetings live route failed with HTTP ${response.status}`);
      }

      setMeetings(normalizeWilsyMeetingsPayload(payload));
    } catch (error) {
      setMeetingsError(error?.message || 'Meetings live route unavailable.');
    } finally {
      setMeetingsLoading(false);
    }
  }, [apiBase, tenantId]);

  useEffect(() => {
    refreshMeetings();
  }, [refreshMeetings]);

  /**
   * @function openOverview
   * @description Returns the module to the records overview.
   * @returns {void}
   * @collaboration Workspace navigation, editor exit, evidence/import back actions.
   */
  const openOverview = useCallback(() => {
    setActiveView('overview');
    setSelectedMeeting(null);
  }, []);

  /**
   * @function openCreateMeeting
   * @description Opens the Meeting editor in create mode.
   * @returns {void}
   * @collaboration Create command, empty-state action, WilsyMeetingEditor.
   */
  const openCreateMeeting = useCallback(() => {
    setSelectedMeeting(null);
    setActiveView('create');
  }, []);

  /**
   * @function openMeetingCapsule
   * @description Opens a selected Meeting in the capsule view.
   * @param {Object} meeting - Meeting record.
   * @returns {void}
   * @collaboration Records table, Meeting capsule, daily operator drill-in.
   */
  const openMeetingCapsule = useCallback((meeting = {}) => {
    setSelectedMeeting(meeting);
    setActiveView('capsule');
  }, []);

  /**
   * @function editMeeting
   * @description Opens a selected Meeting in editor mode.
   * @param {Object} meeting - Meeting record.
   * @returns {void}
   * @collaboration Records row actions, capsule edit, PATCH command flow.
   */
  const editMeeting = useCallback((meeting = {}) => {
    setSelectedMeeting(meeting);
    setActiveView('edit');
  }, []);

  /**
   * @function handleMeetingSaved
   * @description Refreshes local and live records after a Meeting save receipt.
   * @param {Object} receipt - Backend save receipt.
   * @returns {Promise<void>} Save handling completion.
   * @collaboration WilsyMeetingEditor, DB_PERSISTED response, records cockpit.
   */
  const handleMeetingSaved = useCallback(async (receipt = {}) => {
    const savedMeeting = receipt.meeting || receipt.record || null;

    if (savedMeeting) {
      setMeetings((current) => mergeWilsyMeetingRecord(current, savedMeeting));
    }

    setSelectedMeeting(null);
    setSelectedMeetingIds([]);
    setActiveView('overview');
    await refreshMeetings();
  }, [refreshMeetings]);

  /**
   * @function handleEditorBack
   * @description Returns from editor views and refreshes when a save receipt is supplied.
   * @param {Object} event - Optional editor event.
   * @returns {Promise<void>} Back handling completion.
   * @collaboration Editor back button, create/edit flow, live route refresh.
   */
  const handleEditorBack = useCallback(async (event = {}) => {
    setActiveView('overview');
    setSelectedMeeting(null);

    if (event?.receipt || event?.status === 'DB_PERSISTED') {
      await refreshMeetings();
    }
  }, [refreshMeetings]);

  /**
   * @function toggleMeetingSelection
   * @description Toggles one Meeting id in the bulk selection set.
   * @param {Object|string} meeting - Meeting record or id.
   * @returns {void}
   * @collaboration Records checkboxes, bulk delete verification, operator selection.
   */
  const toggleMeetingSelection = useCallback((meeting = {}) => {
    const recordId = resolveWilsyMeetingRecordId(meeting);
    if (!recordId) return;

    setSelectedMeetingIds((current) =>
      current.includes(recordId)
        ? current.filter((id) => id !== recordId)
        : [...current, recordId]
    );
  }, []);

  /**
   * @function toggleAllVisibleMeetings
   * @description Toggles all currently visible Meeting rows.
   * @param {Array<Object|string>} visibleRecords - Visible records or ids.
   * @returns {void}
   * @collaboration Select-all checkbox, search-filtered rows, bulk command bar.
   */
  const toggleAllVisibleMeetings = useCallback((visibleRecords = []) => {
    const visibleIds = visibleRecords.map(resolveWilsyMeetingRecordId).filter(Boolean);
    if (visibleIds.length === 0) return;

    setSelectedMeetingIds((current) => {
      const currentSet = new Set(current);
      const allSelected = visibleIds.every((id) => currentSet.has(id));

      return allSelected
        ? current.filter((id) => !visibleIds.includes(id))
        : Array.from(new Set([...current, ...visibleIds]));
    });
  }, []);

  /**
   * @function openDeleteVerification
   * @description Opens the verified delete modal for one or more Meeting ids.
   * @param {Array<string>} ids - Meeting ids.
   * @returns {void}
   * @collaboration Single-row delete, bulk delete, destructive command verification.
   */
  const openDeleteVerification = useCallback((ids = []) => {
    const cleanIds = Array.from(new Set(ids.map(resolveWilsyMeetingRecordId).filter(Boolean)));

    if (cleanIds.length === 0) {
      setMeetingsError('Select one or more meeting records before delete.');
      return;
    }

    setDeleteState({
      open: true,
      ids: cleanIds,
      note: '',
      busy: false,
      status: '',
      message: '',
    });
  }, []);

  /**
   * @function requestSingleDelete
   * @description Opens delete verification for one Meeting record.
   * @param {Object} meeting - Meeting record.
   * @returns {void}
   * @collaboration Row delete action, capsule delete action, verified command modal.
   */
  const requestSingleDelete = useCallback((meeting = {}) => {
    const recordId = resolveWilsyMeetingRecordId(meeting);
    if (!recordId) {
      setMeetingsError('Meeting record id is required before delete.');
      return;
    }

    setSelectedMeeting(meeting);
    setSelectedMeetingIds([recordId]);
    openDeleteVerification([recordId]);
  }, [openDeleteVerification]);

  /**
   * @function executeDelete
   * @description Deletes selected Meetings through the existing CRM command route.
   * @returns {Promise<void>} Delete completion.
   * @collaboration DELETE /api/crm/command/meetings/:id, CRM command authority, records refresh.
   */
  const executeDelete = useCallback(async () => {
    const ids = Array.from(new Set(deleteState.ids.map(resolveWilsyMeetingRecordId).filter(Boolean)));
    const note = String(deleteState.note || '').trim();

    if (ids.length === 0) {
      setDeleteState((current) => ({ ...current, status: 'DELETE_BLOCKED', message: 'No meeting records are selected.' }));
      return;
    }

    if (!note) {
      setDeleteState((current) => ({ ...current, status: 'VERIFICATION_REQUIRED', message: 'Enter a verification note before deleting meetings.' }));
      return;
    }

    setDeleteState((current) => ({
      ...current,
      busy: true,
      status: 'DELETING',
      message: `Deleting ${ids.length} meeting record${ids.length === 1 ? '' : 's'} through CRM command authority.`,
    }));

    const headers = buildWilsyMeetingsCommandHeaders(tenantConfig);
    const failures = [];

    for (const id of ids) {
      const meeting = meetings.find((record) => resolveWilsyMeetingRecordId(record) === id) || {};
      const response = await fetch(`${apiBase}/api/crm/command/meetings/${encodeURIComponent(id)}`, {
        method: 'DELETE',
        headers,
        credentials: 'include',
        body: JSON.stringify(
          buildWilsyMeetingDeletePayload({
            tenantConfig,
            recordId: id,
            note,
            meeting,
            bulk: ids.length > 1,
          })
        ),
      });

      const payload = await response.json().catch(() => ({}));

      if (!response.ok || payload?.ok === false) {
        failures.push(`${id}: ${payload?.message || payload?.error || `HTTP ${response.status}`}`);
      }
    }

    if (failures.length > 0) {
      const message = failures.join(' | ');
      setDeleteState((current) => ({ ...current, busy: false, status: 'DELETE_FAILED', message }));
      setMeetingsError(message);
      return;
    }

    setDeleteState({ open: false, ids: [], note: '', busy: false, status: '', message: '' });
    setMeetings((current) => current.filter((record) => !ids.includes(resolveWilsyMeetingRecordId(record))));
    setSelectedMeeting(null);
    setSelectedMeetingIds([]);
    setMeetingsError('');
    setActiveView('overview');
    await refreshMeetings();
  }, [apiBase, deleteState.ids, deleteState.note, meetings, refreshMeetings, tenantConfig]);

  /**
   * @function handleSyncMeetings
   * @description Runs parent sync when available and refreshes live Meeting records.
   * @returns {Promise<void>} Sync completion.
   * @collaboration CRMDashboard sync command, CRM command fabric, live route refresh.
   */
  const handleSyncMeetings = useCallback(async () => {
    setMeetingsError('');

    try {
      if (typeof onSync === 'function') {
        await onSync();
      }
      await refreshMeetings();
    } catch (error) {
      setMeetingsError(error?.message || 'Meetings sync failed.');
    }
  }, [onSync, refreshMeetings]);

  return (
    <section
      className={`${styles.moduleShell} ${railCollapsed ? styles.railCollapsed : ''}`}
      data-wilsy-meetings-workspace="operator-workbench"
      data-rail-state={railCollapsed ? 'collapsed' : 'expanded'}
    
      data-wilsy-r91k179e24p38c-records-surface={['overview', 'records'].includes(String(activeView)) ? 'lead-parity' : 'workspace'}
    >
      <aside className={styles.moduleRail} aria-label="Meetings module rail">
        <header className={styles.railHeader}>
          <div>
            <small>CRM</small>
            <strong>Meetings</strong>
          </div>
          <button
            type="button"
            className={styles.railToggle}
            onClick={() => setRailCollapsed((value) => !value)}
            aria-label={railCollapsed ? 'Expand Meetings rail' : 'Collapse Meetings rail'}
          >
            {railCollapsed ? <PanelLeftOpen size={17} /> : <PanelLeftClose size={17} />}
          </button>
        </header>

        <nav>
          {tabs.map(({ id, label, icon: Icon }) => (
            <button
              type="button"
              key={id}
              className={activeView === id || (id === 'overview' && activeView === 'capsule') ? styles.activeRailItem : ''}
              onClick={() => {
                if (id === 'create') {
                  openCreateMeeting();
                  return;
                }
                if (id === 'overview') {
                  openOverview();
                  return;
                }
                setActiveView(id);
              }}
            >
              <Icon size={18} />
              <span>{label}</span>
            </button>
          ))}
        </nav>

        <button type="button" className={styles.backToCrm} onClick={backToCrm}>
          <ArrowLeft size={17} />
          <span>Back to CRM</span>
        </button>
      </aside>

      <main className={styles.moduleMain}>
        <header className={styles.moduleTopbar}>
          <div>
            <small>{tenantName}</small>
            <strong>Meeting Operations</strong>
            <span>{meetings.length} live record{meetings.length === 1 ? '' : 's'} · {selectedMeetingIds.length} selected</span>
          </div>

          <label className={styles.search}>
            <Search size={18} />
            <input
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search title, participant, venue, account or status"
            />
          </label>

          <nav aria-label="Meetings commands">
            <button type="button" onClick={openCreateMeeting} aria-label="Create meeting" title="Create meeting">
              <Plus size={18} />
            </button>
            <button type="button" onClick={() => setActiveView('import')} aria-label="Import meetings" title="Import meetings">
              <FileSpreadsheet size={18} />
            </button>
            <button type="button" onClick={() => setActiveView('evidence')} aria-label="Meeting evidence" title="Meeting evidence">
              <Fingerprint size={18} />
            </button>
            <button type="button" onClick={() => openDeleteVerification(selectedMeetingIds)} aria-label="Delete selected meetings" title="Delete selected meetings">
              <Trash2 size={18} />
            </button>
            <button type="button" onClick={() => setWilsyAiOpen(true)} aria-label="Wilsy AI meeting command" title="Wilsy AI meeting command">
              <Sparkles size={18} />
            </button>
            <button type="button" onClick={handleSyncMeetings} disabled={meetingsLoading} aria-label="Refresh meetings" title="Refresh meetings">
              <RefreshCcw size={18} />
            </button>
          </nav>
        </header>

        {activeView === 'overview' ? (
          <WilsyMeetingsOverview
            records={filteredMeetings}
            allRecords={meetings}
            loading={meetingsLoading}
            meetingsError={meetingsError}
            searchTerm={searchTerm}
            selectedIds={selectedMeetingIds}
            onToggleMeetingSelection={toggleMeetingSelection}
            onToggleAllMeetings={toggleAllVisibleMeetings}
            onBulkDeleteRequested={() => openDeleteVerification(selectedMeetingIds)}
            onRefreshMeetings={handleSyncMeetings}
            onCreateMeeting={openCreateMeeting}
            onImportMeetings={() => setActiveView('import')}
            onOpenEvidence={() => setActiveView('evidence')}
            onOpenMeeting={openMeetingCapsule}
            onEditMeeting={editMeeting}
            onDeleteMeeting={requestSingleDelete}
          />
        ) : null}

        {activeView === 'capsule' ? (
          <WilsyMeetingCapsuleView
            meeting={selectedMeeting || {}}
            onBack={openOverview}
            onEdit={() => editMeeting(selectedMeeting || {})}
            onDelete={() => requestSingleDelete(selectedMeeting || {})}
            onOpenEvidence={() => setActiveView('evidence')}
          />
        ) : null}

        {activeView === 'create' || activeView === 'edit' ? (
          <WilsyMeetingEditor
            tenantConfig={tenantConfig}
            initialMeeting={activeView === 'edit' ? selectedMeeting : null}
            editorMode={activeView === 'edit' ? 'edit' : 'create'}
            onBackToOverview={handleEditorBack}
            onMeetingSaved={handleMeetingSaved}
            onImportMeetings={() => setActiveView('import')}
          />
        ) : null}

        {activeView === 'import' ? (
          <WilsyMeetingImportWorkspace
            onBackToOverview={openOverview}
            onCreateMeeting={openCreateMeeting}
          />
        ) : null}

        {activeView === 'evidence' ? (
          <WilsyMeetingEvidenceWorkspace
            onBackToOverview={openOverview}
            onCreateMeeting={openCreateMeeting}
            onImportMeetings={() => setActiveView('import')}
          />
        ) : null}

        <footer className={styles.moduleViewportFooter} data-wilsy-meetings-viewport-footer="workspace-closeout">
          <span>
            {activeView === 'overview'
              ? `${filteredMeetings.length} visible of ${meetings.length} live meetings`
              : `${activeView === 'capsule' ? 'record capsule' : activeView} workspace`}
          </span>
          <strong>{meetings.length} live · {selectedMeetingIds.length} selected</strong>
          <em>WILSY OS -- LEGAL SOVEREIGN STANDARD</em>
        </footer>

        {deleteState.open ? (
          <div className={styles.wilsyModalBackdrop} data-wilsy-meetings-modal="delete">
            <section className={styles.wilsyCommandModal} role="dialog" aria-modal="true" aria-label="Delete meeting verification">
              <header>
                <small>Destructive command verification</small>
                <h2>Delete meeting record{deleteState.ids.length === 1 ? '' : 's'}?</h2>
                <p>
                  Wilsy OS will delete {deleteState.ids.length} meeting record{deleteState.ids.length === 1 ? '' : 's'}
                  through CRM command authority with tenant, operator, route and strike payload evidence.
                </p>
              </header>

              <div className={styles.modalWarning}>
                <strong>{deleteState.ids.length === 1 ? selectedMeetingTitle : `${deleteState.ids.length} selected meetings`}</strong>
                <span>{deleteState.ids.join(', ')}</span>
              </div>

              <label className={styles.modalField}>
                <span>Verification note</span>
                <input
                  value={deleteState.note}
                  onChange={(event) => setDeleteState((current) => ({ ...current, note: event.target.value }))}
                  placeholder="Reason for deleting selected meetings"
                  autoFocus
                />
              </label>

              {deleteState.status ? (
                <div className={styles.commandBanner} data-status={deleteState.status}>
                  <strong>{deleteState.status}</strong>
                  <span>{deleteState.message}</span>
                </div>
              ) : null}

              <div className={styles.wilsyModalActions}>
                <button
                  type="button"
                  className={styles.modalSecondary}
                  onClick={() => setDeleteState({ open: false, ids: [], note: '', busy: false, status: '', message: '' })}
                  disabled={deleteState.busy}
                >
                  Cancel
                </button>
                <button type="button" className={styles.modalDanger} onClick={executeDelete} disabled={deleteState.busy}>
                  {deleteState.busy ? 'Deleting' : 'Verify + delete'}
                </button>
              </div>
            </section>
          </div>
        ) : null}

        {wilsyAiOpen ? (
          <aside className={styles.wilsyAiMeetingRail} aria-label="Wilsy AI Meetings command rail">
            <header>
              <small>Wilsy AI · Meetings</small>
              <h3>Command intelligence</h3>
              <button type="button" onClick={() => setWilsyAiOpen(false)} aria-label="Close Wilsy AI">×</button>
            </header>

            <section>
              <strong>Live posture</strong>
              <p>{meetings.length} meeting record{meetings.length === 1 ? '' : 's'} loaded. {meetingsError ? 'Live route needs attention.' : 'Records are ready for operator decisions.'}</p>
            </section>

            <section>
              <strong>Next actions</strong>
              <button type="button" onClick={() => { setWilsyAiOpen(false); openCreateMeeting(); }}>Create next meeting</button>
              <button type="button" onClick={() => { setWilsyAiOpen(false); setActiveView('import'); }}>Open import</button>
              <button type="button" onClick={() => { setWilsyAiOpen(false); setActiveView('evidence'); }}>Review evidence</button>
              <button type="button" onClick={() => { setWilsyAiOpen(false); handleSyncMeetings(); }}>Refresh live records</button>
            </section>
          </aside>
        ) : null}
      </main>
    </section>
  );
}
