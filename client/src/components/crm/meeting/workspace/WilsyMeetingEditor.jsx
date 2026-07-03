/* eslint-disable */
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { CalendarDays, Link, Save, Users } from 'lucide-react';
import styles from './WilsyMeetingsWorkspace.module.css';
import WilsyMeetingParticipantResolver from './WilsyMeetingParticipantResolver';
import { getMeetings } from '../../../../services/crmService.js';

/**
 * @function resolveWilsyR91K179E15RApiBase
 * @description Resolves the CRM API base for Meeting editor command requests.
 * @returns {string} API base URL.
 * @collaboration Vite runtime, CRM command routes, Meeting editor.
 */
function resolveWilsyR91K179E15RApiBase() {
  return import.meta.env.VITE_API_URL || 'http://localhost:5050';
}

/**
 * @function resolveWilsyR91K179E15RTenantId
 * @description Resolves tenant id for Meeting editor command requests.
 * @param {Object} tenantConfig - Tenant configuration.
 * @returns {string} Tenant id.
 * @collaboration tenantConfig, CRM command routes, Meeting editor.
 */
function resolveWilsyR91K179E15RTenantId(tenantConfig = {}) {
  return String(tenantConfig.tenantId || tenantConfig.id || tenantConfig.slug || tenantConfig.name || 'wilsy-sovereign-root').trim() || 'wilsy-sovereign-root';
}

/**
 * @function resolveWilsyR91K179E15ROperator
 * @description Builds operator context for Meeting command evidence.
 * @param {Object} tenantConfig - Tenant configuration.
 * @returns {Object} Operator context.
 * @collaboration WilsyMeetingEditor, CRM command evidence, tenant context.
 */
function resolveWilsyR91K179E15ROperator(tenantConfig = {}) {
  const tenantId = resolveWilsyR91K179E15RTenantId(tenantConfig);

  return {
    tenantId,
    operatorId: tenantConfig.operatorId || tenantConfig.userId || tenantConfig.ownerId || 'wilsy-local-operator',
    operatorEmail: tenantConfig.operatorEmail || tenantConfig.email || '',
    operatorRole: tenantConfig.operatorRole || tenantConfig.role || 'OPERATOR',
  };
}

/**
 * @function buildWilsyR91K179E15RInitialDraft
 * @description Builds a default Meeting draft for create mode.
 * @param {Object} tenantConfig - Tenant configuration.
 * @returns {Object} Meeting draft.
 * @collaboration WilsyMeetingEditor, CRM command payload.
 */
function buildWilsyR91K179E15RInitialDraft(tenantConfig = {}) {
  return {
    title: 'New Meeting',
    meetingVenue: 'Client location',
    location: '',
    host: tenantConfig.operatorName || tenantConfig.name || 'Wilsy',
    allDay: false,
    fromDate: '',
    fromTime: '',
    toDate: '',
    toTime: '',
    participants: [],
    relatedRecord: {
      module: 'Meetings',
      type: 'CRM Meetings',
      title: 'Standalone Meetings workspace',
      recordId: '',
    },
    repeat: 'None',
    reminder: 'None',
    description: '',
    tenantId: resolveWilsyR91K179E15RTenantId(tenantConfig),
  };
}

/**
 * @function normalizeWilsyR91K179E15RMeetingDraft
 * @description Converts an existing Meeting record into editable draft state.
 * @param {Object} tenantConfig - Tenant configuration.
 * @param {Object|null} initialMeeting - Existing Meeting record.
 * @returns {Object} Meeting draft.
 * @collaboration Meetings records overview, Meeting editor update mode.
 */
function normalizeWilsyR91K179E15RMeetingDraft(tenantConfig = {}, initialMeeting = null) {
  const fallback = buildWilsyR91K179E15RInitialDraft(tenantConfig);

  if (!initialMeeting || typeof initialMeeting !== 'object') return fallback;

  const recordId = String(initialMeeting.recordId || initialMeeting.meetingId || initialMeeting.id || initialMeeting._id || '').trim();

  return {
    ...fallback,
    ...initialMeeting,
    recordId,
    id: recordId,
    meetingId: recordId,
    title: initialMeeting.title || initialMeeting.subject || initialMeeting.meetingTitle || fallback.title,
    meetingVenue: initialMeeting.meetingVenue || initialMeeting.venue || fallback.meetingVenue,
    location: initialMeeting.location || '',
    host: initialMeeting.host || fallback.host,
    participants: Array.isArray(initialMeeting.participants)
      ? initialMeeting.participants
      : Array.isArray(initialMeeting.attendees)
        ? initialMeeting.attendees
        : [],
    relatedRecord: initialMeeting.relatedRecord || initialMeeting.relatedTo || fallback.relatedRecord,
    repeat: initialMeeting.repeat || fallback.repeat,
    reminder: initialMeeting.reminder || fallback.reminder,
    description: initialMeeting.description || initialMeeting.agenda || '',
    tenantId: initialMeeting.tenantId || fallback.tenantId,
  };
}

/**
 * @function buildWilsyR91K179E15RDateTime
 * @description Converts date and time into ISO timestamp when both are present.
 * @param {string} dateValue - Date input.
 * @param {string} timeValue - Time input.
 * @returns {string|null} ISO timestamp or null.
 * @collaboration Meeting editor, CRMMeeting command payload.
 */
function buildWilsyR91K179E15RDateTime(dateValue, timeValue) {
  if (!dateValue || !timeValue) return null;

  const parsed = new Date(`${dateValue}T${timeValue}`);

  return Number.isNaN(parsed.getTime()) ? null : parsed.toISOString();
}

/**
 * @function resolveWilsyR91K179E15RMeetingIdentity
 * @description Resolves a stable Meeting identity from supported record fields.
 * @param {Object|null} meeting - Meeting record.
 * @returns {string} Stable Meeting identity.
 * @collaboration Meeting editor reset guard, backend refresh guard, draft preservation.
 */
function resolveWilsyR91K179E15RMeetingIdentity(meeting = null) {
  return String(meeting?.recordId || meeting?.meetingId || meeting?.id || meeting?._id || '').trim();
}

/**
 * @function resolveWilsyR91K179E15RMeetingResetKey
 * @description Builds a stable reset key so parent object churn cannot erase operator typing.
 * @param {string} tenantId - Tenant id.
 * @param {string} editorMode - Editor mode.
 * @param {Object|null} initialMeeting - Initial Meeting record.
 * @returns {string} Reset key.
 * @collaboration WilsyMeetingEditor, live meeting refreshes, production-safe controlled inputs.
 */
function resolveWilsyR91K179E15RMeetingResetKey(tenantId = '', editorMode = 'create', initialMeeting = null) {
  const recordIdentity = resolveWilsyR91K179E15RMeetingIdentity(initialMeeting);
  return [tenantId || 'wilsy-sovereign-root', editorMode || 'create', recordIdentity || 'new'].join(':');
}

/**
 * @function buildWilsyR91K179E15RCommandPayload
 * @description Builds the Meeting command payload with venue integrity and Wilsy institutional evidence for create and edit modes.
 * @param {Object} meetingDraft - Meeting draft.
 * @param {Object} tenantConfig - Tenant configuration.
 * @param {string} saveMode - create or edit.
 * @returns {Object} Command payload.
 * @collaboration WilsyMeetingEditor, CRM command routes, DB_PERSISTED meeting evidence, venue integrity loop.
 */
function buildWilsyR91K179E15RCommandPayload(meetingDraft = {}, tenantConfig = {}, saveMode = 'create') {
  const operator = resolveWilsyR91K179E15ROperator(tenantConfig);
  const generatedAt = new Date().toISOString();
  const recordId = String(meetingDraft.recordId || meetingDraft.meetingId || meetingDraft.id || meetingDraft._id || '').trim();
  const venue = String(
    meetingDraft.meetingVenue ||
      meetingDraft.venue ||
      meetingDraft.venueType ||
      meetingDraft.meetingVenueLabel ||
      meetingDraft.locationType ||
      ''
  ).trim();

  const institutionalHeaders = {
    tenantId: operator.tenantId,
    operatorId: operator.operatorId,
    operatorEmail: operator.operatorEmail,
    operatorRole: operator.operatorRole,
    actor: operator.operatorId,
    actorEmail: operator.operatorEmail,
    actorRole: operator.operatorRole,
    commandSurface: saveMode === 'edit' ? 'R91K179E22B1_MEETING_EDITOR_UPDATE_VENUE_INTEGRITY' : 'R91K179E22B1_MEETING_EDITOR_CREATE_VENUE_INTEGRITY',
    sourceRoute: recordId ? `/api/crm/command/meetings/${recordId}` : '/api/crm/command/meetings',
    liveRoute: '/api/crm/live/meetings',
    evidenceRoute: '/api/crm/live/evidence',
    recordId,
    meetingId: recordId,
    generatedAt,
  };

  const meeting = {
    recordId,
    id: recordId,
    meetingId: recordId,
    title: meetingDraft.title,
    subject: meetingDraft.title,
    meetingTitle: meetingDraft.title,
    meetingVenue: venue,
    venue,
    venueType: venue,
    meetingVenueLabel: venue,
    locationType: venue,
    venueProof: 'R91K179E22B1_MEETING_EDITOR_VENUE_INTEGRITY_PAYLOAD',
    location: meetingDraft.location,
    host: meetingDraft.host,
    allDay: Boolean(meetingDraft.allDay),
    fromDate: meetingDraft.fromDate,
    fromTime: meetingDraft.fromTime,
    toDate: meetingDraft.toDate,
    toTime: meetingDraft.toTime,
    startsAt: buildWilsyR91K179E15RDateTime(meetingDraft.fromDate, meetingDraft.fromTime),
    endsAt: buildWilsyR91K179E15RDateTime(meetingDraft.toDate, meetingDraft.toTime),
    participants: Array.isArray(meetingDraft.participants) ? meetingDraft.participants : [],
    attendees: Array.isArray(meetingDraft.participants) ? meetingDraft.participants : [],
    relatedRecord: meetingDraft.relatedRecord,
    relatedTo: meetingDraft.relatedRecord,
    repeat: meetingDraft.repeat,
    reminder: meetingDraft.reminder,
    description: meetingDraft.description,
    agenda: meetingDraft.description,
    tenantId: operator.tenantId,
    createdBy: meetingDraft.createdBy || operator.operatorId,
    updatedBy: operator.operatorId,
    wilsyVenuePersistence: {
      captured: Boolean(venue),
      venue,
      location: meetingDraft.location || '',
      source: 'R91K179E22B1_MEETING_EDITOR_VENUE_INTEGRITY_PAYLOAD',
      capturedAt: generatedAt,
      recordId,
    },
  };

  return {
    action: saveMode === 'edit' ? 'UPDATE' : 'CREATE',
    commandSurface: institutionalHeaders.commandSurface,
    tenantId: operator.tenantId,
    recordId,
    meetingId: recordId,
    meetingVenue: venue,
    venue,
    venueType: venue,
    meetingVenueLabel: venue,
    locationType: venue,
    operatorContext: operator,
    institutionalHeaders,
    strikePayload: {
      headers: institutionalHeaders,
      institutionalHeaders,
      action: saveMode === 'edit' ? 'UPDATE' : 'CREATE',
      meeting,
      tenantId: operator.tenantId,
      recordId,
      meetingId: recordId,
      meetingVenue: venue,
      venue,
      venueType: venue,
      meetingVenueLabel: venue,
      locationType: venue,
      location: meetingDraft.location || '',
      generatedAt,
    },
    meeting,
  };
}


/**
 * @function normalizeWilsyR91K179E15RParticipantEmail
 * @description Normalizes Meeting participant email addresses to lowercase for storage and display.
 * @param {*} value - Raw participant email value.
 * @returns {string} Lowercase email value or empty string.
 * @collaboration Meeting participant resolver, CRMMeeting save payload, Wilsy OS evidence surfaces.
 */
function normalizeWilsyR91K179E15RParticipantEmail(value = '') {
  const cleaned = String(value || '').trim();
  return cleaned.includes('@') ? cleaned.toLowerCase() : '';
}

/**
 * @function normalizeWilsyR91K179E15RParticipantRecord
 * @description Normalizes one Meeting participant record without mutating non-email identity labels.
 * @param {*} participant - Participant value from resolver, manual input, or backend.
 * @returns {Object|null} Normalized participant record.
 * @collaboration Meeting editor participant dock, CRM command payload, invitation evidence.
 */
function normalizeWilsyR91K179E15RParticipantRecord(participant = {}) {
  if (typeof participant === 'string') {
    const cleaned = participant.trim();
    if (!cleaned) return null;

    const email = normalizeWilsyR91K179E15RParticipantEmail(cleaned);

    return {
      label: email || cleaned,
      email,
      source: email ? 'email-string' : 'name-string',
    };
  }

  if (!participant || typeof participant !== 'object') return null;

  const email = normalizeWilsyR91K179E15RParticipantEmail(
    participant.email ||
    participant.emailAddress ||
    participant.mail ||
    participant.value ||
    ''
  );

  const rawLabel = String(
    participant.label ||
    participant.name ||
    participant.fullName ||
    participant.displayName ||
    participant.title ||
    email ||
    ''
  ).trim();

  const label = normalizeWilsyR91K179E15RParticipantEmail(rawLabel) || rawLabel;

  return {
    ...participant,
    label,
    email,
  };
}

/**
 * @function normalizeWilsyR91K179E15RParticipantList
 * @description Normalizes all Meeting participants and removes empty participant entries.
 * @param {*} participants - Candidate participants list.
 * @returns {Object[]} Normalized participant records.
 * @collaboration Meeting editor state, save payload builder, participant evidence dock.
 */
function normalizeWilsyR91K179E15RParticipantList(participants = []) {
  if (!Array.isArray(participants)) return [];

  return participants
    .map((participant) => normalizeWilsyR91K179E15RParticipantRecord(participant))
    .filter((participant) => participant && (participant.label || participant.email));
}


const R91K179E24P56B_RELATED_CRM_MODULES = [
  { id: 'leads', label: 'Lead', route: '/api/crm/live/leads' },
  { id: 'meetings', label: 'Meeting', route: '/api/crm/live/meetings' },
];

/**
 * @function resolveWilsyR91K179E24P56BRecordId
 * @description Resolves a stable CRM record id from live CRM source records.
 * @param {Object} record - Live CRM record.
 * @returns {string} Stable CRM record id.
 * @collaboration Related CRM linker, live CRM source routes, Meeting evidence payload.
 */
function resolveWilsyR91K179E24P56BRecordId(record = {}) {
  return String(
    record._id ||
    record.id ||
    record.recordId ||
    record.leadId ||
    record.meetingId ||
    record.sourceRecordId ||
    ''
  ).trim();
}

/**
 * @function resolveWilsyR91K179E24P56BRecordTitle
 * @description Resolves a human-readable title for a related CRM candidate.
 * @param {Object} moduleConfig - CRM module configuration.
 * @param {Object} record - Live CRM record.
 * @returns {string} Candidate display title.
 * @collaboration Related CRM linker, source-backed candidate list, operator review surface.
 */
function resolveWilsyR91K179E24P56BRecordTitle(moduleConfig = {}, record = {}) {
  const fullName = String(record.fullName || [record.firstName, record.surname].filter(Boolean).join(' ') || '').trim();
  const leadName = fullName || String(record.name || record.title || record.companyName || record.company || '').trim();
  const meetingTitle = String(record.title || record.subject || record.name || '').trim();

  return moduleConfig.id === 'meetings'
    ? meetingTitle || 'Untitled Meeting'
    : leadName || 'Untitled CRM Record';
}

/**
 * @function normalizeWilsyR91K179E24P56BCrmCandidate
 * @description Converts a live CRM record into a selectable related-record command candidate.
 * @param {Object} moduleConfig - CRM module configuration.
 * @param {Object} record - Live CRM record.
 * @param {string} tenantId - Active tenant id.
 * @returns {Object|null} Normalized CRM candidate or null.
 * @collaboration CRM live source routes, Meeting related-record modal, command payload evidence.
 */
function normalizeWilsyR91K179E24P56BCrmCandidate(moduleConfig = {}, record = {}, tenantId = '') {
  const recordId = resolveWilsyR91K179E24P56BRecordId(record);
  if (!recordId) return null;

  const title = resolveWilsyR91K179E24P56BRecordTitle(moduleConfig, record);
  const company = String(record.companyName || record.company || record.accountName || record.relatedAccount || '').trim();
  const email = String(record.email || record.primaryEmail || '').trim().toLowerCase();
  const status = String(record.status || record.stage || record.leadStatus || record.meetingType || 'LIVE').trim();
  const sourceSystem = String(record.sourceSystem || record.source || 'wilsy-live-crm').trim();

  return {
    id: moduleConfig.id + ':' + recordId,
    module: moduleConfig.id,
    type: moduleConfig.label,
    recordId,
    title,
    subtitle: [company, email].filter(Boolean).join(' · '),
    status,
    sourceSystem,
    tenantId: record.tenantId || tenantId,
    route: moduleConfig.route,
    raw: record,
    evidence: {
      linkedBy: 'R91K179E24P56B_LIVE_RELATED_CRM_LINKER',
      sourceRoute: moduleConfig.route,
      sourceSystem,
      tenantId: record.tenantId || tenantId,
      recordId,
      recordType: moduleConfig.label,
      recordTitle: title,
      generatedAt: new Date().toISOString(),
      noFreeTextGuess: true,
    },
  };
}

/**
 * @function filterWilsyR91K179E24P56BCrmCandidates
 * @description Filters live CRM candidates by operator search input.
 * @param {Array<Object>} candidates - Related CRM candidates.
 * @param {string} query - Search query.
 * @returns {Array<Object>} Filtered candidates.
 * @collaboration Related CRM linker search, live source-backed modal.
 */
function filterWilsyR91K179E24P56BCrmCandidates(candidates = [], query = '') {
  const normalizedQuery = String(query || '').trim().toLowerCase();
  if (!normalizedQuery) return candidates.slice(0, 24);

  return candidates.filter((candidate) => [
    candidate.type,
    candidate.title,
    candidate.subtitle,
    candidate.status,
    candidate.recordId,
    candidate.sourceSystem,
  ].some((value) => String(value || '').toLowerCase().includes(normalizedQuery))).slice(0, 24);
}

/**
 * @function WilsyMeetingEditor
 * @description Renders the Meeting create/update editor with DB_PERSISTED save workflow.
 * @param {Object} props - Component props.
 * @returns {JSX.Element} Meeting editor.
 * @collaboration WilsyMeetingsWorkspace, CRM command routes, Meeting records overview.
 */
export default function WilsyMeetingEditor({
  tenantConfig = {},
  initialMeeting = null,
  editorMode = 'create',
  onBackToOverview,
  onImportMeetings,
  onMeetingSaved,
}) {
  const tenantId = resolveWilsyR91K179E15RTenantId(tenantConfig);
  const meetingResetKey = useMemo(
    () => resolveWilsyR91K179E15RMeetingResetKey(tenantId, editorMode, initialMeeting),
    [
      tenantId,
      editorMode,
      initialMeeting?.recordId,
      initialMeeting?.meetingId,
      initialMeeting?.id,
      initialMeeting?._id,
    ]
  );
  const [meetingDraft, setMeetingDraft] = useState(() => normalizeWilsyR91K179E15RMeetingDraft(tenantConfig, initialMeeting));
  const [commandState, setCommandState] = useState({ saving: false, status: '', message: '', receipt: null });
  const [participantModalOpen, setParticipantModalOpen] = useState(false);
  const [participantInput, setParticipantInput] = useState('');
  const [relatedModalOpen, setRelatedModalOpen] = useState(false);
  const [relatedInput, setRelatedInput] = useState('');
  const [relatedCandidates, setRelatedCandidates] = useState([]);
  const [selectedRelatedCandidateId, setSelectedRelatedCandidateId] = useState('');
  const [relatedSearchState, setRelatedSearchState] = useState({ loading: false, error: '', loadedAt: '' });
  const [loadingBackendData, setLoadingBackendData] = useState(false);
  const draftDirtyRef = useRef(false);
  const backendLoadedRecordRef = useRef('');

  const apiBase = resolveWilsyR91K179E15RApiBase();
  const recordId = String(meetingDraft.recordId || meetingDraft.meetingId || meetingDraft.id || meetingDraft._id || '').trim();
  const saveMode = recordId || editorMode === 'edit' ? 'edit' : 'create';
  const visibleRelatedCandidates = useMemo(
    () => filterWilsyR91K179E24P56BCrmCandidates(relatedCandidates, relatedInput),
    [relatedCandidates, relatedInput]
  );
  const displayRelatedCandidates = useMemo(() => {
    if (visibleRelatedCandidates.length) return visibleRelatedCandidates;
    if (!String(relatedInput || '').trim()) return relatedCandidates.slice(0, 24);
    return [];
  }, [visibleRelatedCandidates, relatedCandidates, relatedInput]); /* R91K179E24P56E_VISIBLE_CANDIDATE_FALLBACK */
  const selectedRelatedCandidate = useMemo(
    () => relatedCandidates.find(candidate => candidate.id === selectedRelatedCandidateId) || null,
    [relatedCandidates, selectedRelatedCandidateId]
  );
  const renderedRelatedCandidates = useMemo(() => {
    if (displayRelatedCandidates.length) return displayRelatedCandidates;
    if (selectedRelatedCandidate) return [selectedRelatedCandidate];
    return [];
  }, [displayRelatedCandidates, selectedRelatedCandidate]); /* R91K179E24P56E4_RENDERED_CANDIDATE_AUTHORITY */

  /**
   * @function handleWilsyR91K179E24P56D2RelatedModalAutoload
   * @description Loads live CRM candidates when the visible Related CRM modal opens.
   * @returns {void}
   * @collaboration Related CRM linker modal, /api/crm/live/leads, /api/crm/live/meetings, evidence preview.
   */
  useEffect(() => {
    if (!relatedModalOpen || relatedCandidates.length || relatedSearchState.loading) return;
    loadRelatedCrmCandidates();
  }, [relatedModalOpen, relatedCandidates.length, relatedSearchState.loading]); /* R91K179E24P56D2_RELATED_MODAL_AUTOLOAD */

  useEffect(() => {
    draftDirtyRef.current = false;
    backendLoadedRecordRef.current = '';
    setMeetingDraft(normalizeWilsyR91K179E15RMeetingDraft(tenantConfig, initialMeeting));
    setCommandState({ saving: false, status: '', message: '', receipt: null });
  }, [meetingResetKey]);

  useEffect(() => {
    if (saveMode !== 'edit' || !recordId || backendLoadedRecordRef.current === recordId) return;

    backendLoadedRecordRef.current = recordId;
    loadMeetingDataFromBackend(recordId);
  }, [recordId, saveMode]);

  /**
   * @function loadMeetingDataFromBackend
   * @description Refreshes an existing Meeting draft from the live CRM backend when edit mode opens.
   * @param {string} targetRecordId - Meeting record id to refresh.
   * @returns {Promise<void>} Meeting refresh completion.
   * @collaboration WilsyMeetingEditor, crmService.getMeetings, DB_PERSISTED edit workflow.
   */
  const loadMeetingDataFromBackend = async (targetRecordId = recordId) => {
    try {
      setLoadingBackendData(true);
      const meetings = await getMeetings(tenantId, { recordId: targetRecordId, limit: 1 });
      if (Array.isArray(meetings) && meetings.length > 0) {
        const meeting = meetings[0];
        if (draftDirtyRef.current || backendLoadedRecordRef.current !== targetRecordId) return;

        setMeetingDraft((current) => ({
          ...current,
          ...meeting,
          participants: normalizeWilsyR91K179E15RParticipantList(
            Array.isArray(meeting.participants) ? meeting.participants : current.participants
          ),
          relatedRecord: meeting.relatedRecord || meeting.relatedTo || current.relatedRecord,
        }));
      }
    } catch (error) {
      console.error('Failed to load meeting from backend:', error);
    } finally {
      setLoadingBackendData(false);
    }
  };

  /**
   * @function updateDraftField
   * @description Updates one Meeting draft field.
   * @param {string} field - Field name.
   * @param {*} value - Field value.
   * @returns {void}
   * @collaboration Meeting form inputs, command payload builder.
   */
  const updateDraftField = (field, value) => {
    draftDirtyRef.current = true;
    setCommandState((current) => (
      current.saving || !current.status
        ? current
        : { saving: false, status: '', message: '', receipt: null }
    ));
    setMeetingDraft((current) => ({
      ...current,
      [field]: field === 'participants' ? normalizeWilsyR91K179E15RParticipantList(value) : value,
    }));
  };

  /**
   * @function addParticipant
   * @description Adds a participant email/name to the Meeting draft.
   * @returns {void}
   * @collaboration Meeting participants workflow, command payload.
   */
  const addParticipant = () => {
    setParticipantInput('');
    setParticipantModalOpen(true);
  };

  /**
   * @function confirmParticipantSelection
   * @description Confirms participant capture through Wilsy OS in-app command modal instead of browser prompt.
   * @returns {void}
   * @collaboration Meeting editor, participant evidence workflow, CRM command payload.
   */
  const confirmParticipantSelection = () => {
    const cleaned = String(participantInput || '').trim();

    if (!cleaned) return;

    const participantEmail = normalizeWilsyR91K179E15RParticipantEmail(cleaned);

    draftDirtyRef.current = true;
    setCommandState((current) => (
      current.saving || !current.status
        ? current
        : { saving: false, status: '', message: '', receipt: null }
    ));
    setMeetingDraft((current) => ({
      ...current,
      participants: [
        ...(Array.isArray(current.participants) ? current.participants : []),
        {
          label: participantEmail || cleaned,
          email: participantEmail,
          source: 'wilsy-command-modal',
        },
      ],
    }));

    setParticipantInput('');
    setParticipantModalOpen(false);
  };

  /**
   * @function loadRelatedCrmCandidates
   * @description Loads live CRM records for the Related CRM linker modal.
   * @returns {Promise<void>} Related CRM candidate load completion.
   * @collaboration /api/crm/live/leads, /api/crm/live/meetings, Meeting related-record evidence workflow.
   */
  const loadRelatedCrmCandidates = async () => {
    setRelatedSearchState({ loading: true, error: '', loadedAt: '' });

    try {
      const settledResults = await Promise.allSettled(
        R91K179E24P56B_RELATED_CRM_MODULES.map(async (moduleConfig) => {
          const response = await fetch(`${apiBase}${moduleConfig.route}?limit=24`, {
            method: 'GET',
            headers: {
              Accept: 'application/json',
              'X-Tenant-Id': tenantId,
              'X-Wilsy-Command-Surface': 'R91K179E24P56B_LIVE_RELATED_CRM_LINKER',
            },
          });

          if (!response.ok) {
            throw new Error(`${moduleConfig.label} route returned HTTP ${response.status}`);
          }

          const payload = await response.json();
          const records = Array.isArray(payload?.records)
            ? payload.records
            : (Array.isArray(payload?.data) ? payload.data : []);

          return records
            .map(record => normalizeWilsyR91K179E24P56BCrmCandidate(moduleConfig, record, tenantId))
            .filter(Boolean);
        })
      );

      const candidates = settledResults
        .flatMap((result) => (result.status === 'fulfilled' ? result.value : []))
        .filter(candidate => !(candidate.module === 'meetings' && candidate.recordId === recordId));

      const routeErrors = settledResults
        .filter(result => result.status === 'rejected')
        .map(result => result.reason?.message || 'CRM route unavailable');

      setRelatedCandidates(candidates);
      setSelectedRelatedCandidateId((current) => (
        current && candidates.some(candidate => candidate.id === current)
          ? current
          : (candidates[0]?.id || '')
      ));
      setRelatedSearchState({
        loading: false,
        error: candidates.length ? '' : (routeErrors[0] || 'No live CRM records available to link.'),
        loadedAt: new Date().toISOString(),
      });
    } catch (error) {
      setRelatedCandidates([]);
      setSelectedRelatedCandidateId('');
      setRelatedSearchState({
        loading: false,
        error: error?.message || 'Related CRM records failed to load.',
        loadedAt: '',
      });
    }
  };

  /**
   * @function linkRelatedRecord
   * @description Opens the source-backed Related CRM linker modal.
   * @returns {void}
   * @collaboration CRM live source routes, Meeting update command, related-record evidence.
   */
  const linkRelatedRecord = () => {
    setRelatedInput(''); /* R91K179E24P56E_CLEAR_STALE_RELATED_SEARCH */
    setRelatedModalOpen(true);
    if (!relatedCandidates.length && !relatedSearchState.loading) {
      loadRelatedCrmCandidates();
    }
  };

  /**
   * @function confirmRelatedRecordLink
   * @description Confirms related CRM record linkage from a live candidate or explicit evidence fallback.
   * @returns {void}
   * @collaboration Meeting editor, CRM relation workflow, related-record evidence.
   */
  const confirmRelatedRecordLink = () => {
    const cleaned = String(relatedInput || '').trim();
    const selectedCandidate = selectedRelatedCandidate
      || displayRelatedCandidates.find(candidate => candidate.recordId === cleaned)
      || displayRelatedCandidates.find(candidate => candidate.title.toLowerCase() === cleaned.toLowerCase())
      || null;

    if (!selectedCandidate && !cleaned) return;

    const generatedAt = new Date().toISOString();
    const relatedRecord = selectedCandidate
      ? {
          module: selectedCandidate.module,
          type: selectedCandidate.type,
          title: selectedCandidate.title,
          recordId: selectedCandidate.recordId,
          sourceSystem: selectedCandidate.sourceSystem,
          sourceRoute: selectedCandidate.route,
          tenantId: selectedCandidate.tenantId,
          evidence: {
            ...(selectedCandidate.evidence || {}),
            generatedAt,
          },
          linkedBy: 'R91K179E24P56B_LIVE_RELATED_CRM_LINKER',
        }
      : {
          module: 'CRM',
          type: 'Manual Evidence Reference',
          title: cleaned,
          recordId: cleaned,
          sourceSystem: 'wilsy-manual-evidence-fallback',
          sourceRoute: 'operator-entered-reference',
          tenantId,
          evidence: {
            linkedBy: 'R91K179E24P56B_MANUAL_RELATED_REFERENCE',
            generatedAt,
            tenantId,
            recordId: cleaned,
            recordTitle: cleaned,
            noLiveCandidateSelected: true,
          },
          linkedBy: 'R91K179E24P56B_MANUAL_RELATED_REFERENCE',
        };

    draftDirtyRef.current = true;
    setCommandState((current) => (
      current.saving || !current.status
        ? current
        : { saving: false, status: '', message: '', receipt: null }
    ));
    setMeetingDraft((current) => ({
      ...current,
      relatedRecord,
      relatedType: relatedRecord.type,
      relatedId: relatedRecord.recordId,
      relatedRecordId: relatedRecord.recordId,
      relatedRecordType: relatedRecord.type,
      relatedRecordTitle: relatedRecord.title,
      relatedRecordSource: relatedRecord.sourceSystem,
      relatedRecordEvidence: relatedRecord.evidence,
    }));

    setRelatedInput('');
    setSelectedRelatedCandidateId('');
    setRelatedModalOpen(false);
  };

  /**
   * @function saveMeeting
   * @description Saves the Meeting through POST or PATCH command authority.
   * @returns {Promise<void>} Save completion.
   * @collaboration POST/PATCH CRM Meeting command routes, DB_PERSISTED record workspace.
   */
  const saveMeeting = async () => {
    setCommandState({ saving: true, status: 'SAVING', message: 'Saving meeting through CRM command authority.', receipt: null });

    try {
      const payload = buildWilsyR91K179E15RCommandPayload(meetingDraft, tenantConfig, saveMode);
      const route = saveMode === 'edit' && recordId ? `/api/crm/command/meetings/${encodeURIComponent(recordId)}` : '/api/crm/command/meetings';
      const method = saveMode === 'edit' && recordId ? 'PATCH' : 'POST';

      const response = await fetch(`${apiBase}${route}`, {
        method,
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          'X-Tenant-Id': resolveWilsyR91K179E15RTenantId(tenantConfig),
          'X-Wilsy-Tenant-ID': resolveWilsyR91K179E15RTenantId(tenantConfig),
        },
        credentials: 'include',
        body: JSON.stringify(payload),
      });

      const receipt = await response.json().catch(() => ({}));

      if (!response.ok || receipt?.ok === false) {
        const rateLimitedMessage =
          response.status === 429
            ? 'CRM command authority is rate-limited locally. Wait a moment, refresh live records, then save again.'
            : '';
        throw new Error(rateLimitedMessage || receipt?.message || receipt?.error || `Meeting save failed with HTTP ${response.status}`);
      }

      const savedMeeting = receipt.meeting || receipt.record || {};
      const savedRecordId = String(receipt.recordId || receipt.meetingId || savedMeeting._id || savedMeeting.id || savedMeeting.meetingId || recordId || '').trim();

      draftDirtyRef.current = false;
      setMeetingDraft((current) => ({
        ...current,
        ...savedMeeting,
        participants: normalizeWilsyR91K179E15RParticipantList(
          Array.isArray(savedMeeting.participants) ? savedMeeting.participants : current.participants
        ),
        recordId: savedRecordId,
        id: savedRecordId,
        meetingId: savedRecordId,
      }));

      setCommandState({
        saving: false,
        status: receipt.status || 'DB_PERSISTED',
        message: receipt.message || 'Meeting persisted through CRM command authority.',
        receipt,
      });

      if (typeof onMeetingSaved === 'function') {
        onMeetingSaved(receipt);
      }

      if (typeof onBackToOverview === 'function') {
        window.setTimeout(() => {
          onBackToOverview({ source: 'R91K179E15R_MEETING_EDITOR_SAVE_EXIT', status: receipt.status || 'DB_PERSISTED', receipt });
        }, 850);
      }
    } catch (error) {
      setCommandState({
        saving: false,
        status: String(error?.message || '').includes('rate-limited') ? 'RATE_LIMITED' : 'SAVE_FAILED',
        message: error?.message || 'Meeting save failed.',
        receipt: null,
      });
    }
  };

  /**
   * @function renderRelatedCrmCandidateList
   * @description Renders live CRM candidates inside the Related CRM linker modal without contradictory empty/evidence states.
   * @returns {JSX.Element} Candidate picker surface.
   * @collaboration Related CRM linker modal, source-backed candidate selection, evidence preview.
   */
  function renderRelatedCrmCandidateList() {
    const hasRenderedCandidates = Array.isArray(renderedRelatedCandidates) && renderedRelatedCandidates.length > 0;
    const showEmptyState = !hasRenderedCandidates && !selectedRelatedCandidate;

    return (
      <section className={styles.relatedCandidateSurface} data-wilsy-r91k179e24p56b-related-candidates="live">
        <header className={styles.relatedCandidateHeader}>
          <span>Live CRM candidates</span>
          <button type="button" onClick={loadRelatedCrmCandidates} disabled={relatedSearchState.loading}>
            {relatedSearchState.loading ? 'Syncing…' : 'Refresh'}
          </button>
        </header>

        {relatedSearchState.error ? (
          <p className={styles.relatedCandidateError}>{relatedSearchState.error}</p>
        ) : null}

        <div className={styles.relatedCandidateList} role="listbox" aria-label="Live CRM records available for linking">
          {hasRenderedCandidates ? renderedRelatedCandidates.map((candidate) => {
            const selected = selectedRelatedCandidateId === candidate.id;

            return (
              <button
                key={candidate.id}
                type="button"
                className={styles.relatedCandidateCard}
                data-selected={selected ? 'true' : 'false'}
                onClick={() => {
                  setSelectedRelatedCandidateId(candidate.id);
                  setRelatedInput(candidate.title);
                }}
              >
                <span>{candidate.type}</span>
                <strong>{candidate.title}</strong>
                <small>{candidate.subtitle || candidate.recordId}</small>
                <em>{candidate.status} · {candidate.sourceSystem}</em>
              </button>
            );
          }) : null}

          {showEmptyState ? (
            <p className={styles.relatedCandidateEmpty}>
              No live CRM candidate matches this search. Clear the search or refresh live CRM routes.
            </p>
          ) : null}
        </div>

        {selectedRelatedCandidate ? (
          <aside className={styles.relatedEvidencePreview} aria-label="Selected related CRM evidence">
            <span>Evidence preview</span>
            <strong>{selectedRelatedCandidate.type} · {selectedRelatedCandidate.recordId}</strong>
            <p>{selectedRelatedCandidate.route} · {selectedRelatedCandidate.tenantId}</p>
          </aside>
        ) : null}
      </section>
    );
  }

  return (
    <section className={styles.pageSurface} data-wilsy-r91k179e15r-view="editor">
      <header className={styles.editorHeader}>
        <div>
          <small>Meeting Information</small>
          <h2>{saveMode === 'edit' ? 'Edit Meeting' : 'Create Meeting'}</h2>
          <p>Capture and update the meeting object, schedule, participants, related record, reminders, repeat policy and agenda.</p>
        </div>

        <nav>
          <button type="button" onClick={onBackToOverview}>Back to overview</button>
          <button type="button" onClick={onImportMeetings}>Import Meetings</button>
          <button type="button" onClick={saveMeeting} disabled={commandState.saving}><Save size={18} />{commandState.saving ? 'Saving' : saveMode === 'edit' ? 'Save Changes' : 'Save Meeting'}</button>
        </nav>
      </header>

      <div
        className={styles.commandBanner}
        data-status={commandState.status || 'IDLE'}
        data-visible={commandState.status ? 'true' : 'false'}
        role={commandState.status ? 'status' : 'presentation'}
        aria-hidden={commandState.status ? 'false' : 'true'}
      >
        {commandState.status ? (
          <>
          <strong>{commandState.status}</strong>
          <span>{commandState.message}</span>
          </>
        ) : null}
      </div>

      <div
        className={styles.editorBodyViewport}
        data-has-participants={Array.isArray(meetingDraft.participants) && meetingDraft.participants.length > 0 ? 'true' : 'false'}
      >
        <div className={styles.editorCommandDeck}>
          <div className={styles.editorFormGrid}>
            <label><span>Title</span><input name="meetingTitle" autoComplete="off" value={meetingDraft.title || ''} onChange={(event) => updateDraftField('title', event.target.value)} /></label>
            <label><span>Meeting Venue</span><select name="meetingVenue" value={meetingDraft.meetingVenue || 'Client location'} onChange={(event) => updateDraftField('meetingVenue', event.target.value)}><option>Client location</option><option>Wilsy Offices</option><option>Video meeting</option><option>Court / site</option></select></label>
            <label><span>Location</span><input name="meetingLocation" autoComplete="off" value={meetingDraft.location || ''} onChange={(event) => updateDraftField('location', event.target.value)} /></label>
            <label><span>Host</span><input name="meetingHost" autoComplete="off" value={meetingDraft.host || ''} onChange={(event) => updateDraftField('host', event.target.value)} /></label>
            <label className={styles.editorDateField}><span>From Date</span><input name="meetingFromDate" type="date" value={meetingDraft.fromDate || ''} onChange={(event) => updateDraftField('fromDate', event.target.value)} /></label>
            <label className={styles.editorTimeField}><span>From Time</span><input name="meetingFromTime" type="time" step="60" value={meetingDraft.fromTime || ''} onChange={(event) => updateDraftField('fromTime', event.target.value)} /></label>
            <label className={styles.editorDateField}><span>To Date</span><input name="meetingToDate" type="date" value={meetingDraft.toDate || ''} onChange={(event) => updateDraftField('toDate', event.target.value)} /></label>
            <label className={styles.editorTimeField}><span>To Time</span><input name="meetingToTime" type="time" step="60" value={meetingDraft.toTime || ''} onChange={(event) => updateDraftField('toTime', event.target.value)} /></label>
            <label className={styles.participantResolverSummary} data-wilsy-r91k179e23p1w-summary="participant-resolver">
                <span>Participants</span>
                <strong>{Array.isArray(meetingDraft.participants) ? meetingDraft.participants.length : 0} selected</strong>
                {Array.isArray(meetingDraft.participants) && meetingDraft.participants.length > 0 && <p>{meetingDraft.participants.map((participant) => (typeof participant === 'string' ? participant : participant.displayName || participant.email || participant.label || 'Participant')).join(', ')}</p>}
                <button type="button" onClick={addParticipant}><Users size={16} />Resolve</button>
              </label>
            <label><span>Related To</span><strong>{meetingDraft.relatedRecord?.title || meetingDraft.relatedRecord?.name || ''}</strong><button type="button" onClick={linkRelatedRecord}><Link size={16} />Link</button></label>
            <label><span>Repeat</span><select name="meetingRepeat" value={meetingDraft.repeat || 'None'} onChange={(event) => updateDraftField('repeat', event.target.value)}><option>None</option><option>Daily</option><option>Weekly</option><option>Monthly</option></select></label>
            <label><span>Reminder</span><select name="meetingReminder" value={meetingDraft.reminder || 'None'} onChange={(event) => updateDraftField('reminder', event.target.value)}><option>None</option><option>10 minutes before</option><option>30 minutes before</option><option>1 hour before</option></select></label>
          </div>
        </div>

        <aside className={styles.editorAgendaPanel} aria-label="Meeting description and agenda">
          <header>
            <small>Agenda Command</small>
            <strong>Description / Agenda</strong>
            <p>Capture outcomes, risks, preparation, evidence requirements and follow-up commands without leaving the visible workspace.</p>
          </header>
          <textarea
            name="meetingDescription"
            value={meetingDraft.description || ''}
            onChange={(event) => updateDraftField('description', event.target.value)}
            placeholder="Agenda, outcomes, risks, participant preparation, evidence requirements and follow-up commands"
          />
          <div className={styles.editorAgendaMeta}>
            <span>{(meetingDraft.description || '').length} characters</span>
            <span>{Array.isArray(meetingDraft.participants) ? meetingDraft.participants.length : 0} participants</span>
          </div>
        </aside>

        {Array.isArray(meetingDraft.participants) && meetingDraft.participants.length > 0 ? (
          <section className={styles.participantSelectedTray} data-wilsy-r91k179e23p1w-selected="participant-tray">
            <header>
              <small>Selected participant graph</small>
              <strong>{meetingDraft.participants.length} participant{meetingDraft.participants.length === 1 ? '' : 's'} bound</strong>
            </header>
            <div>
              {meetingDraft.participants.map((participant, index) => (
                <button
                  type="button"
                  key={`${typeof participant === 'string' ? participant : participant.normalizedEmail || participant.email || participant.participantId || participant.displayName || 'participant'}-${index}`}
                  onClick={() => {
                    draftDirtyRef.current = true;
                    setCommandState((state) => (
                      state.saving || !state.status
                        ? state
                        : { saving: false, status: '', message: '', receipt: null }
                    ));
                    setMeetingDraft((current) => {
                      const currentParticipants = Array.isArray(current.participants) ? current.participants : [];
                      const nextParticipants = currentParticipants.filter((_, participantIndex) => participantIndex !== index);
                      return { ...current, participants: normalizeWilsyR91K179E15RParticipantList(nextParticipants), attendees: nextParticipants };
                    });
                  }}
                  title="Remove participant"
                >
                  <span>{typeof participant === 'string' ? 'EXTERNAL' : participant.sourceType || 'EXTERNAL'}</span>
                  <strong>{typeof participant === 'string' ? participant : participant.displayName || participant.email || participant.label || 'Participant'}</strong>
                  <small>{typeof participant === 'string' ? participant : participant.email || 'No email on source record'}</small>
                  <em>×</em>
                </button>
              ))}
            </div>
          </section>
        ) : null}
        {/* R91K179E23P1W_SELECTED_PARTICIPANT_TRAY */}
      </div>

        {participantModalOpen ? (
          <WilsyMeetingParticipantResolver
            tenantConfig={tenantConfig}
            selectedParticipants={Array.isArray(meetingDraft.participants) ? meetingDraft.participants : []}
            onParticipantsChange={(participants) => {
              draftDirtyRef.current = true;
              setCommandState((current) => (
                current.saving || !current.status
                  ? current
                  : { saving: false, status: '', message: '', receipt: null }
              ));
              setMeetingDraft((current) => ({
                ...current,
                participants,
                attendees: participants,
              }));
            }}
            onClose={() => setParticipantModalOpen(false)}
          />
        ) : null}
        {/* R91K179E23P1W_PARTICIPANT_RESOLVER_MOUNT */}

      {relatedModalOpen ? (
        <div className={styles.wilsyModalBackdrop} data-wilsy-r91k179e18-modal="related-record">
          <section className={styles.wilsyCommandModal} role="dialog" aria-modal="true" aria-label="Link related CRM record">
            <header>
              <small>Related CRM Command</small>
              <h3>Link related CRM record</h3>
              <p>Search and attach this meeting to a verified live CRM record. The selected record id, type, source and evidence remain in the meeting command payload.</p>
            </header>

            <label className={styles.modalField}>
              <span>SEARCH LIVE CRM RECORDS</span>
              <input
                value={relatedInput}
                onChange={(event) => setRelatedInput(event.target.value)}
                placeholder="Search lead, meeting, account, deal or CRM id"
                autoFocus
              />
            </label>

            
            <section data-wilsy-r91k179e24p56d2-related-visible="true">
              {renderRelatedCrmCandidateList()}
            </section>
<div className={styles.wilsyModalActions} data-wilsy-r91k179e19-modal-actions="visible">
              <button type="button" className={styles.modalSecondary} onClick={() => setRelatedModalOpen(false)}>Cancel</button>
              <button type="button" className={styles.modalPrimary} onClick={confirmRelatedRecordLink}>Link record</button>
            </div>
          </section>
        </div>
      ) : null}

      <footer className={styles.editorEvidenceStrip}>
        <span><CalendarDays size={17} />{saveMode === 'edit' ? 'Update mode' : 'Create mode'}</span>
        <span>{recordId ? `Record ${recordId}` : 'New record'}</span>
      </footer>
    </section>
  );
}

/* R91K179E18_WILSY_EDITOR_MODALS */
