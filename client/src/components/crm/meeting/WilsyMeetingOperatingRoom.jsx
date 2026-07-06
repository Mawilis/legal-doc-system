/* eslint-disable */
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import WilsyLeadOperatingRoom from '../lead/WilsyLeadOperatingRoom.jsx';
import WilsyMeetingEditor from './workspace/WilsyMeetingEditor.jsx';
import meetingRoomStyles from './WilsyMeetingOperatingRoom.module.css';
import WilsyMeetingRecordsIntelligencePanel from './WilsyMeetingRecordsIntelligencePanel.jsx';
import { installWilsyCrmControlRepairBridge } from '../shared/wilsyCrmControlRepairBridge.js';
installWilsyCrmControlRepairBridge('meetings');


/* WILSY_P60K5F5_MEETING_NATIVE_KPI_RESOLVER */

/**
 * @function resolveWilsyMeetingNativeKpiRows
 * @description Resolves the live meeting rows used by the Meetings KPI header without falling back to Lead metrics.
 * @param {Array} rows - Candidate meeting rows.
 * @returns {Array} Meeting rows.
 * @collaboration Meetings Operating Room, CRM live source rows, readiness cards, and Wilsy OS meeting workflow.
 */
function resolveWilsyMeetingNativeKpiRows(rows = []) {
  return Array.isArray(rows) ? rows : [];
}

/**
 * @function resolveWilsyMeetingNativeReadiness
 * @description Resolves a production-safe readiness score from explicit meeting readiness fields.
 * @param {Object} meeting - Meeting row.
 * @returns {number} Readiness score from 0 to 100.
 * @collaboration Meeting readiness, venue proof, participant readiness, CRM link, evidence state, and KPI cards.
 */
function resolveWilsyMeetingNativeReadiness(meeting = {}) {
  const explicit = Number(
    meeting.readiness ??
    meeting.readinessScore ??
    meeting.sourceCompleteness ??
    meeting.completionScore ??
    meeting.score
  );

  if (Number.isFinite(explicit)) {
    return Math.max(0, Math.min(100, explicit));
  }

  const checks = [
    meeting.title || meeting.name || meeting.subject,
    meeting.startAt || meeting.startTime || meeting.time || meeting.scheduledAt,
    meeting.owner || meeting.host || meeting.hostName,
    meeting.participants || meeting.attendees || meeting.participantCount,
    meeting.relatedRecord || meeting.crmLink || meeting.crmContext,
  ];

  const passed = checks.filter(Boolean).length;

  return Math.round((passed / checks.length) * 100);
}

/**
 * @function resolveWilsyMeetingNativeKpiCards
 * @description Builds meeting-native KPI cards for the Meetings operating header.
 * @param {Array} rows - Meeting rows.
 * @returns {Array} Meeting-native KPI card objects.
 * @collaboration Meetings Operating Room, dashboard KPI cards, readiness scoring, and source-backed meeting records.
 */
function resolveWilsyMeetingNativeKpiCards(rows = []) {
  const meetings = resolveWilsyMeetingNativeKpiRows(rows);
  const scheduledMeetings = meetings.filter((meeting) => {
    const status = String(meeting?.status || meeting?.state || '').toUpperCase();

    return !['CANCELLED', 'CANCELED', 'DELETED', 'ARCHIVED'].includes(status);
  }).length || meetings.length;
  const readyMeetings = meetings.filter((meeting) => {
    const status = String(meeting?.status || meeting?.state || '').toUpperCase();

    return resolveWilsyMeetingNativeReadiness(meeting) >= 100 || ['READY', 'SCHEDULED', 'CONFIRMED'].includes(status);
  }).length;
  const readinessRate = meetings.length ? Math.round((readyMeetings / meetings.length) * 100) : 0;
  const averageReadiness = meetings.length
    ? Math.round(meetings.reduce((total, meeting) => total + resolveWilsyMeetingNativeReadiness(meeting), 0) / meetings.length)
    : 0;
  const meetingHealth = readinessRate >= 90 ? 'Excellent' : readinessRate >= 70 ? 'Ready' : 'Needs attention';

  return [
    {
      id: 'meeting-health',
      label: 'Meeting Health',
      value: meetingHealth,
      detail: meetings.length ? `${readinessRate}% ready by meeting readiness` : 'Connect live Meeting rows',
      trend: meetings.length ? `${meetings.length} visible` : 'No meetings yet',
      tone: 'violet',
    },
    {
      id: 'scheduled-meetings',
      label: 'Scheduled Meetings',
      value: String(scheduledMeetings),
      detail: meetings.length ? 'All meeting rows visible' : 'No scheduled meetings yet',
      trend: scheduledMeetings ? `${scheduledMeetings} calendar ready` : 'No meeting rows yet',
      tone: 'blue',
    },
    {
      id: 'ready-meetings',
      label: 'Ready Meetings',
      value: String(readyMeetings),
      detail: meetings.length ? `${readinessRate}% of live meetings` : 'No readiness signal',
      trend: readyMeetings ? `${readyMeetings} ready` : 'Needs readiness evidence',
      tone: 'green',
    },
    {
      id: 'readiness-rate',
      label: 'Readiness Rate',
      value: `${readinessRate}%`,
      detail: meetings.length ? `${readyMeetings} ready from live meetings` : 'No readiness signal',
      trend: meetings.length ? 'Live meeting DB derived' : 'Waiting for meeting records',
      tone: 'cyan',
    },
    {
      id: 'average-readiness-score',
      label: 'Avg. Readiness Score',
      value: String(averageReadiness),
      detail: meetings.length ? 'Meeting readiness score' : 'No readiness score yet',
      trend: averageReadiness >= 70 ? 'Actionable' : 'Needs enrichment',
      tone: 'gold',
    },
  ];
}


const MEETING_OPERATING_COPY = Object.freeze({
  heroEyebrow: 'MEETING OPERATIONS',
  title: 'Meetings',
  createLabel: 'Create Meeting',
  heroDescription: 'Manage schedules, CRM context, participants, venue readiness, evidence and follow-up work.',
  allRecordsLabel: 'All Meetings',
  allRecordsDetail: 'Every source-backed row',
  filterTitle: 'Filter Meetings by',
  pipelineHealthLabel: 'Meeting Health',
  openRecordsLabel: 'Scheduled Meetings',
  qualifiedLabel: 'Ready Meetings',
  conversionLabel: 'Readiness Rate',
  averageScoreLabel: 'Avg. Readiness Score',
  followUpLabel: 'Follow-up Window',
  sourceReadinessLabel: 'Source Readiness',
  recordSingular: 'meeting',
  recordPlural: 'meetings',
  pipelineTabLabel: 'Calendar',
  recordsTabLabel: 'Records',
  signalsTabLabel: 'Signals',
  proofTabLabel: 'Proof',
  sourcesTabLabel: 'Sources',
  selectedRecordLabel: 'selected meeting',
  selectedRecordsLabel: 'selected meetings',
  tableHeaders: {
    name: 'Meeting',
    company: 'CRM Link',
    email: 'Participants / Host',
    phone: 'Time',
    owner: 'Owner',
    status: 'Status',
    score: 'Readiness',
  },
});

/**
 * @function resolveMeetingTenantId
 * @description Resolves the tenant id for live Meeting route reads.
 * @param {Object} props - Meeting operating room props.
 * @returns {string} Tenant id.
 * @collaboration CRMDashboard tenantConfig, CRM live Meeting routes, Lead operating-room shell adapter.
 */
function resolveMeetingTenantId(props = {}) {
  return String(
    props.tenantId ||
    props.tenantConfig?.tenantId ||
    props.tenantConfig?.id ||
    props.tenantConfig?.tenantKey ||
    props.user?.tenantId ||
    props.user?.tenant?.id ||
    'wilsy-sovereign-root'
  ).trim() || 'wilsy-sovereign-root';
}

/**
 * @function resolveMeetingApiBase
 * @description Resolves the Vite API base for CRM live Meeting reads.
 * @returns {string} API base.
 * @collaboration Vite runtime, CRM live routes, Meeting adapter synchronization.
 */
function resolveMeetingApiBase() {
  return String(import.meta?.env?.VITE_API_URL || '').replace(/\/$/, '');
}

/**
 * @function buildMeetingReadHeaders
 * @description Builds tenant-scoped read headers for Meeting route synchronization.
 * @param {string} tenantId - Tenant id.
 * @returns {Object} Request headers.
 * @collaboration CRM tenant middleware, Wilsy live source posture, Meeting records adapter.
 */
function buildMeetingReadHeaders(tenantId = 'wilsy-sovereign-root') {
  return {
    'Content-Type': 'application/json',
    'X-Tenant-Id': tenantId,
    'X-Wilsy-Tenant-ID': tenantId,
    'X-Operator-ID': 'wilsy-meeting-lead-shell-adapter',
    'X-Operator-Role': 'Founder',
  };
}

/**
 * @function normalizeMeetingRecordsPayload
 * @description Normalizes Meeting records from props or live route payload without inventing placeholder rows.
 * @param {unknown} payload - Props or route payload.
 * @returns {Array<Object>} Source-backed Meeting records.
 * @collaboration CRMDashboard props, /api/crm/live/meetings, no-fake-data rendering.
 */
function normalizeMeetingRecordsPayload(payload = {}) {
  if (Array.isArray(payload)) {
    return payload;
  }

  return [
    payload.visibleMeetings,
    payload.meetings,
    payload.records,
    payload.items,
    payload.data,
  ].find((candidate) => Array.isArray(candidate)) || [];
}

/**
 * @function resolveMeetingRecordId
 * @description Resolves a stable Meeting record id.
 * @param {Object|string} meeting - Meeting record or id.
 * @param {number} index - Fallback index.
 * @returns {string} Meeting id.
 * @collaboration Meeting-to-Lead shell adapter, row selection, backend source ids.
 */
function resolveMeetingRecordId(meeting = {}, index = 0) {
  if (typeof meeting === 'string') {
    return meeting;
  }

  return String(meeting._id || meeting.id || meeting.sourceRecordId || meeting.meetingId || `meeting-${index}`);
}

/**
 * @function normalizeMeetingDisplayText
 * @description Normalizes Meeting display fragments without inventing missing CRM facts.
 * @param {*} value - Candidate display value.
 * @param {string} fallback - Fallback display value.
 * @returns {string} Normalized display text.
 * @collaboration Meeting row adapter, CRM live records, shared Lead shell text safety.
 */
function normalizeMeetingDisplayText(value = '', fallback = '') {
  if (Array.isArray(value)) {
    return value.map((item) => normalizeMeetingDisplayText(item)).filter(Boolean).join(', ') || fallback;
  }

  if (value && typeof value === 'object') {
    return String(
      value.title ||
      value.name ||
      value.label ||
      value.fullName ||
      value.displayName ||
      value.email ||
      value.recordId ||
      value.id ||
      fallback ||
      ''
    ).trim();
  }

  return String(value || fallback || '').trim();
}

/**
 * @function truncateMeetingDisplayText
 * @description Truncates dense Meeting evidence copy for compact records-grid cells.
 * @param {string} value - Candidate display text.
 * @param {number} limit - Maximum display length.
 * @returns {string} Truncated display text.
 * @collaboration Meeting row adapter, source detail density, shared CRM records table.
 */
function truncateMeetingDisplayText(value = '', limit = 96) {
  const text = String(value || '').replace(/\s+/g, ' ').trim();
  if (text.length <= limit) return text;

  return `${text.slice(0, Math.max(0, limit - 1)).trim()}…`;
}

/**
 * @function resolveMeetingParticipantRecords
 * @description Resolves source-backed Meeting participants from known backend fields.
 * @param {Object} meeting - Meeting record.
 * @returns {Array<Object>} Normalized participant records.
 * @collaboration CRMMeeting source rows, participant evidence, Meeting records grid.
 */
function resolveMeetingParticipantRecords(meeting = {}) {
  const rawParticipants = [
    meeting.participants,
    meeting.attendees,
    meeting.invitees,
    meeting.guests,
  ].find((candidate) => Array.isArray(candidate)) || [];

  return rawParticipants.map((participant) => {
    if (typeof participant === 'string') {
      return { label: participant.trim(), email: participant.includes('@') ? participant.trim().toLowerCase() : '' };
    }

    if (!participant || typeof participant !== 'object') {
      return null;
    }

    const label = normalizeMeetingDisplayText(
      participant.displayName ||
      participant.fullName ||
      participant.name ||
      participant.label ||
      participant.email ||
      participant.emailAddress ||
      participant.value
    );
    const email = normalizeMeetingDisplayText(participant.email || participant.emailAddress || participant.mail || '').toLowerCase();

    return label || email ? { ...participant, label: label || email, email } : null;
  }).filter(Boolean);
}

/**
 * @function resolveMeetingHostLabel
 * @description Resolves the Meeting host/operator label from persisted schedule fields.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Host label.
 * @collaboration Meeting participant column, CRM owner posture, source-backed row details.
 */
function resolveMeetingHostLabel(meeting = {}) {
  return normalizeMeetingDisplayText(
    meeting.hostName ||
    meeting.host ||
    meeting.ownerDisplayName ||
    meeting.ownerName ||
    meeting.ownerLabel ||
    meeting.owner ||
    meeting.createdByName ||
    meeting.createdBy ||
    '',
    'Host pending'
  );
}

/**
 * @function resolveMeetingParticipantSummary
 * @description Builds the participants/host cell from source-backed attendee records.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Participant summary.
 * @collaboration Meeting records table, participant graph, operator scheduling context.
 */
function resolveMeetingParticipantSummary(meeting = {}) {
  const participants = resolveMeetingParticipantRecords(meeting);
  const host = resolveMeetingHostLabel(meeting);

  if (!participants.length) {
    return `Participants pending · Host: ${host}`;
  }

  const visibleParticipants = participants
    .slice(0, 3)
    .map((participant) => normalizeMeetingDisplayText(participant.label || participant.email))
    .filter(Boolean)
    .join(', ');
  const overflowCount = participants.length > 3 ? ` +${participants.length - 3}` : '';

  return `${participants.length} participant${participants.length === 1 ? '' : 's'} · ${visibleParticipants}${overflowCount} · Host: ${host}`;
}

/**
 * @function resolveMeetingRelatedSummary
 * @description Resolves related CRM context from relatedRecord, relatedTo, or flat CRM relationship fields.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Related CRM summary.
 * @collaboration Meeting CRM Link column, related record evidence, source-backed records grid.
 */
function resolveMeetingRelatedSummary(meeting = {}) {
  const relatedRecord = meeting.relatedRecord || meeting.relatedTo || meeting.related || null;

  if (relatedRecord && typeof relatedRecord === 'object') {
    const type = normalizeMeetingDisplayText(relatedRecord.type || relatedRecord.module || relatedRecord.recordType || '');
    const title = normalizeMeetingDisplayText(relatedRecord.title || relatedRecord.name || relatedRecord.label || relatedRecord.recordId || relatedRecord.id || '');
    const suffix = normalizeMeetingDisplayText(relatedRecord.accountName || relatedRecord.companyName || relatedRecord.email || '');

    return [type, title, suffix].filter(Boolean).join(' · ') || 'Link pending';
  }

  return normalizeMeetingDisplayText(
    meeting.relatedName ||
    meeting.relatedTitle ||
    meeting.relatedAccountName ||
    meeting.relatedLeadName ||
    meeting.relatedContactName ||
    meeting.relatedDealName ||
    meeting.crmLink ||
    meeting.relatedId ||
    meeting.relatedRecordId ||
    meeting.relatedLeadId ||
    meeting.relatedContactId ||
    meeting.relatedAccountId ||
    meeting.relatedDealId,
    'Link pending'
  );
}

/**
 * @function resolveMeetingVenueSummary
 * @description Resolves Meeting venue and location context for row-level readiness.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Venue summary.
 * @collaboration Meeting readiness score, venue proof, CRM records detail density.
 */
function resolveMeetingVenueSummary(meeting = {}) {
  const venue = normalizeMeetingDisplayText(meeting.meetingVenue || meeting.venue || meeting.venueType || meeting.meetingVenueLabel || meeting.locationType || '');
  const location = normalizeMeetingDisplayText(meeting.location || meeting.address || meeting.meetingUrl || meeting.onlineMeetingUrl || '');

  return [venue, location].filter(Boolean).join(' · ') || 'Venue missing';
}

/**
 * @function resolveMeetingAgendaSummary
 * @description Resolves the persisted agenda/description evidence into a compact row detail.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Agenda summary.
 * @collaboration Meeting records detail, agenda persistence, operator scan workflow.
 */
function resolveMeetingAgendaSummary(meeting = {}) {
  return truncateMeetingDisplayText(
    normalizeMeetingDisplayText(meeting.description || meeting.agenda || meeting.notes || meeting.summary || ''),
    110
  ) || 'Agenda pending';
}

/**
 * @function resolveMeetingField
 * @description Resolves Meeting fields into source-backed display values.
 * @param {Object} meeting - Meeting record.
 * @param {string} field - Field key.
 * @returns {string} Field value.
 * @collaboration Meeting source rows, CRMMeeting live route, Lead operating-room row adapter.
 */
function resolveMeetingField(meeting = {}, field = 'title') {
  const values = {
    title: meeting.title || meeting.subject || meeting.name || meeting.sourceRecordId || meeting._id || meeting.id || 'Untitled Meeting',
    crmLink: resolveMeetingRelatedSummary(meeting),
    participants: resolveMeetingParticipantSummary(meeting),
    owner: meeting.ownerDisplayName || meeting.ownerName || meeting.ownerLabel || resolveMeetingHostLabel(meeting) || meeting.ownerId || 'Owner pending',
    status: String(meeting.status || meeting.stage || meeting.outcome || 'SCHEDULED').toUpperCase(),
    venue: resolveMeetingVenueSummary(meeting),
  };

  return String(values[field] || '');
}

/**
 * @function resolveMeetingDate
 * @description Resolves Meeting start date from persisted schedule fields.
 * @param {Object} meeting - Meeting record.
 * @returns {Date|null} Meeting date.
 * @collaboration Meeting time column, CRMMeeting source route, schedule evidence.
 */
function resolveMeetingDate(meeting = {}) {
  const value = meeting.startsAt || meeting.startTime || meeting.scheduledAt || meeting.date || meeting.createdAt;

  if (!value) {
    return null;
  }

  const date = new Date(value);

  return Number.isNaN(date.valueOf()) ? null : date;
}

/**
 * @function formatMeetingTime
 * @description Formats Meeting schedule into the Lead shell phone/time column.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Meeting time label.
 * @collaboration Meeting row adapter, schedule visibility, CRM records grid.
 */
function formatMeetingTime(meeting = {}) {
  const start = resolveMeetingDate(meeting);
  const endValue = meeting.endsAt || meeting.endTime;
  const end = endValue ? new Date(endValue) : null;

  if (!start) {
    return 'Time pending';
  }

  const day = start.toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: 'numeric' });
  const startTime = start.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
  const endTime = end && !Number.isNaN(end.valueOf())
    ? end.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
    : '';

  return [day, [startTime, endTime].filter(Boolean).join(' → ')].filter(Boolean).join(' · ');
}

/**
 * @function formatMeetingScheduleDetail
 * @description Builds a compact time, repeat, and reminder label for the records grid.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Schedule detail label.
 * @collaboration Meeting records time column, reminder posture, repeat policy display.
 */
function formatMeetingScheduleDetail(meeting = {}) {
  const time = formatMeetingTime(meeting);
  const repeat = normalizeMeetingDisplayText(meeting.repeat || meeting.recurrence || meeting.repeatPolicy || '');
  const reminder = normalizeMeetingDisplayText(meeting.reminder || meeting.reminderPolicy || meeting.notification || '');

  return [time, repeat && repeat !== 'None' ? repeat : '', reminder && reminder !== 'None' ? reminder : ''].filter(Boolean).join(' · ') || 'Time pending';
}

/**
 * @function computeMeetingReadiness
 * @description Computes Meeting readiness from explicit score or missing operating requirements.
 * @param {Object} meeting - Meeting record.
 * @returns {number} Readiness score.
 * @collaboration Meeting KPI adapter, Lead score column, venue, CRM link, participants and evidence posture.
 */
function computeMeetingReadiness(meeting = {}) {
  const explicit = Number(meeting.readinessScore ?? meeting.aiReadinessScore ?? meeting.wilsyAiScore ?? meeting.score);

  if (Number.isFinite(explicit) && explicit >= 0) {
    return Math.max(0, Math.min(100, Math.round(explicit)));
  }

  let score = 100;

  if (resolveMeetingField(meeting, 'venue') === 'Venue missing') score -= 24;
  if (resolveMeetingField(meeting, 'crmLink') === 'Link pending') score -= 24;
  if (resolveMeetingField(meeting, 'participants') === 'Participants pending') score -= 18;
  if (!resolveMeetingDate(meeting)) score -= 16;
  if (!meeting.evidence && !meeting.auditTrail && !meeting.metadata) score -= 10;

  return Math.max(0, Math.min(100, score));
}

/**
 * @function mapMeetingToLeadShellRecord
 * @description Maps a Meeting record into the exact field shape consumed by WilsyLeadOperatingRoom.
 * @param {Object} meeting - Meeting record.
 * @param {number} index - Row index.
 * @returns {Object} Lead-shell-compatible record.
 * @collaboration WilsyLeadOperatingRoom, CRMMeeting live route, identical CRM Records outlook.
 */
function mapMeetingToLeadShellRecord(meeting = {}, index = 0) {
  const recordId = resolveMeetingRecordId(meeting, index);
  const title = resolveMeetingField(meeting, 'title');
  const crmLink = resolveMeetingField(meeting, 'crmLink');
  const participants = resolveMeetingField(meeting, 'participants');
  const time = formatMeetingScheduleDetail(meeting);
  const owner = resolveMeetingField(meeting, 'owner');
  const status = resolveMeetingField(meeting, 'status');
  const venue = resolveMeetingField(meeting, 'venue');
  const agenda = resolveMeetingAgendaSummary(meeting);
  const readiness = computeMeetingReadiness(meeting);
  const subtitle = [venue, agenda].filter((value) => value && value !== 'Agenda pending').join(' · ') || status;

  return {
    ...meeting,
    _id: recordId,
    id: recordId,
    sourceRecordId: recordId,
    name: title,
    fullName: title,
    displayName: title,
    title,
    recordSubtitle: subtitle,
    rowSubtitle: subtitle,
    meetingSubtitle: subtitle,
    company: [crmLink, venue !== 'Venue missing' ? venue : ''].filter(Boolean).join(' · '),
    companyName: [crmLink, venue !== 'Venue missing' ? venue : ''].filter(Boolean).join(' · '),
    accountName: crmLink,
    email: participants,
    emailAddress: participants,
    phone: time,
    mobile: time,
    mobileE164: time,
    ownerName: owner,
    ownerDisplayName: owner,
    ownerId: owner,
    status,
    leadStatus: status,
    stage: status,
    score: readiness,
    leadScore: readiness,
    readinessScore: readiness,
    priorityScore: readiness,
    source: 'CRMMeeting',
    sourceModule: 'meetings',
    wilsyMeetingSourceRecord: meeting,
    metadata: {
      ...(meeting.metadata || {}),
      wilsyMeetingAdapter: 'R91K179E24P44B3_LEAD_SHELL_ADAPTER',
      meetingStatus: status,
      meetingTime: time,
      meetingReadiness: readiness,
      meetingVenue: venue,
      meetingAgenda: agenda,
      meetingParticipants: participants,
      meetingCrmLink: crmLink,
    },
  };
}

/**
 * @function dispatchMeetingAction
 * @description Calls the first available Meeting handler without pretending backend mutation success.
 * @param {Array<Function>} handlers - Candidate handlers.
 * @param {unknown} payload - Action payload.
 * @returns {void}
 * @collaboration Meeting create/edit/import/evidence workflows, CRMDashboard handlers, no-fake-action policy.
 */
function dispatchMeetingAction(handlers = [], payload = undefined) {
  const handler = handlers.find((candidate) => typeof candidate === 'function');

  if (handler) {
    handler(payload);
  }
}

/**
 * @function WilsyMeetingOperatingRoom
 * @description Renders Meetings through the real WilsyLeadOperatingRoom shell so Meetings and Leads share one identical CRM records outlook.
 * @param {Object} props - Meeting operating room props.
 * @returns {JSX.Element} Meeting records mounted through the canonical Lead operating-room shell.
 * @collaboration CRMDashboard, WilsyLeadOperatingRoom, CRMMeeting live route, Wilsy OS identical module doctrine.
 */
export default function WilsyMeetingOperatingRoom(props = {}) {
  const tenantId = resolveMeetingTenantId(props);
  const initialRecords = useMemo(() => normalizeMeetingRecordsPayload(props), [
    props.visibleMeetings,
    props.meetings,
    props.records,
    props.items,
    props.data,
  ]);

  const [meetingRecords, setMeetingRecords] = useState(initialRecords);
  const [routeState, setRouteState] = useState({ loading: false, message: '', status: 'READY' });
  const [searchTerm, setSearchTerm] = useState(String(props.searchTerm || ''));
  const [meetingWorkflowMode, setMeetingWorkflowMode] = useState('records');
  const [activeMeetingDraft, setActiveMeetingDraft] = useState(null);

  /**
   * @function loadMeetingRecords
   * @description Loads source-backed Meeting records from the live CRM route.
   * @returns {Promise<Object>} Sync response packet.
   * @collaboration CRM live Meetings route, tenant headers, Lead shell adapter.
   */
  const loadMeetingRecords = useCallback(async () => {
    setRouteState({ loading: true, message: 'Syncing Meeting records.', status: 'SYNCING' });

    try {
      const response = await fetch(`${resolveMeetingApiBase()}/api/crm/live/meetings`, {
        method: 'GET',
        headers: buildMeetingReadHeaders(tenantId),
      });

      const data = await response.json().catch(() => ({ ok: false, records: [] }));

      if (!response.ok || data?.ok === false) {
        throw new Error(data?.message || data?.error || `Meetings route failed with HTTP ${response.status}`);
      }

      const records = normalizeMeetingRecordsPayload(data);

      setMeetingRecords(records);
      setRouteState({ loading: false, message: `${records.length} Meeting record${records.length === 1 ? '' : 's'} loaded.`, status: 'LIVE' });

      return {
        ok: true,
        activeModule: 'meetings',
        records,
        count: records.length,
      };
    } catch (error) {
      setRouteState({ loading: false, message: error?.message || 'Meeting route sync failed.', status: 'ROUTE_WARNING' });
      setMeetingRecords((current) => current.length ? current : initialRecords);

      return {
        ok: false,
        activeModule: 'meetings',
        message: error?.message || 'Meeting route sync failed.',
      };
    }
  }, [initialRecords, tenantId]);

  useEffect(() => {
    if (initialRecords.length) {
      setMeetingRecords(initialRecords);
    }

    loadMeetingRecords();
  }, [initialRecords, loadMeetingRecords]);

  const leadShellRecords = useMemo(() => (
    meetingRecords.map((meeting, index) => mapMeetingToLeadShellRecord(meeting, index))
  ), [meetingRecords]);


  /**
   * @function openWilsyR91K179E24P49BMeetingCreateWorkflow
   * @description Opens the real Meeting editor instead of allowing the shared Lead shell to enter Lead create mode.
   * @param {Object} context - Delegated create context from the Lead shell.
   * @returns {boolean} True when Meeting create is handled.
   * @collaboration WilsyLeadOperatingRoom create delegation, WilsyMeetingEditor, CRMMeeting command route.
   */
  function openWilsyR91K179E24P49BMeetingCreateWorkflow(context = {}) {
    void context;
    setActiveMeetingDraft(null);
    setMeetingWorkflowMode('create');

    return true;
  }

  /**
   * @function openWilsyR91K179E26MeetingEditWorkflow
   * @description Opens the Meeting editor from a shared Lead-shell row without falling back to Lead CRUD.
   * @param {Object} context - Delegated edit context from the shared records shell.
   * @returns {boolean} True when Meeting edit was handled.
   * @collaboration WilsyLeadOperatingRoom row actions, WilsyMeetingEditor, CRMMeeting live records.
   */
  function openWilsyR91K179E26MeetingEditWorkflow(context = {}) {
    const selectedMeeting = context.record?.wilsyMeetingSourceRecord || context.record || null;

    if (!selectedMeeting) {
      return false;
    }

    setActiveMeetingDraft(selectedMeeting);
    setMeetingWorkflowMode('edit');

    return true;
  }

  /**
   * @function closeWilsyR91K179E24P49BMeetingWorkflow
   * @description Returns from the Meeting editor to the Meeting records board without mutating data.
   * @returns {void}
   * @collaboration Meeting editor cancel action, Lead-shell records view, Meeting adapter state.
   */
  function closeWilsyR91K179E24P49BMeetingWorkflow() {
    setActiveMeetingDraft(null);
    setMeetingWorkflowMode('records');
  }

  /**
   * @function handleWilsyR91K179E24P49BMeetingSaved
   * @description Handles Meeting editor save receipts, refreshes live Meetings, and returns to records view.
   * @param {Object} receipt - Meeting command receipt.
   * @returns {Promise<void>} Meeting refresh completion.
   * @collaboration WilsyMeetingEditor, /api/crm/live/meetings, Meeting records board.
   */
  async function handleWilsyR91K179E24P49BMeetingSaved(receipt = {}) {
    const savedMeeting = receipt.meeting || receipt.record || receipt.data || null;

    if (savedMeeting) {
      setMeetingRecords((current) => {
        const savedId = resolveMeetingRecordId(savedMeeting, 0);
        const nextRecords = Array.isArray(current) ? [...current] : [];
        const existingIndex = nextRecords.findIndex((record, index) => resolveMeetingRecordId(record, index) === savedId);

        if (existingIndex >= 0) {
          nextRecords[existingIndex] = savedMeeting;
          return nextRecords;
        }

        return [savedMeeting, ...nextRecords];
      });
    }

    if (typeof props.onMeetingSaved === 'function') {
      props.onMeetingSaved(receipt);
    }

    await loadMeetingRecords();
    setActiveMeetingDraft(null);
    setMeetingWorkflowMode('records');
  }


  if (meetingWorkflowMode === 'create' || meetingWorkflowMode === 'edit') {
    return (
      <section
        data-wilsy-r91k179e24p49b-meeting-workflow="editor"
        aria-label={meetingWorkflowMode === 'edit' ? 'Edit Meeting workflow' : 'Create Meeting workflow'}
      >
        <WilsyMeetingEditor
          tenantConfig={props.tenantConfig || { tenantId }}
          initialMeeting={activeMeetingDraft}
          editorMode={meetingWorkflowMode}
          onBackToOverview={closeWilsyR91K179E24P49BMeetingWorkflow}
          onImportMeetings={props.onImportMeetings || props.openImportMeetings}
          onMeetingSaved={handleWilsyR91K179E24P49BMeetingSaved}
        />
      </section>
    );
  }

  return (
    <div className={meetingRoomStyles.meetingRecordsCommandSuite} data-wilsy-r91k179e24p57f5="meeting-records-command-suite">
      <div className={meetingRoomStyles.meetingRecordsShellHost}>
        <WilsyLeadOperatingRoom
          leads={leadShellRecords}
          searchTerm={searchTerm}
          loading={props.loading || routeState.loading}
          themeRuntime={props.themeRuntime}
          tenantConfig={props.tenantConfig}
          user={props.user}
          onOpenThemeAuthority={props.onOpenThemeAuthority}
          operatingCopy={MEETING_OPERATING_COPY}
          onOpenOperatingCreate={openWilsyR91K179E24P49BMeetingCreateWorkflow}
          onOpenOperatingEdit={openWilsyR91K179E26MeetingEditWorkflow}
          onSearch={(queryValue) => {
            setSearchTerm(queryValue);
            if (typeof props.onSearch === 'function') {
              props.onSearch(queryValue);
            }
          }}
          onSync={loadMeetingRecords}
          onSaveLead={async (payload) => {
            dispatchMeetingAction([props.onCreateMeeting, props.openCreateMeeting, props.onCreate], payload);
            return {
              ok: true,
              status: 'MEETING_CREATE_DELEGATED_TO_MEETING_WORKFLOW',
              payload,
            };
          }}
        />
      </div>
      <WilsyMeetingRecordsIntelligencePanel
        records={meetingRecords}
        loading={props.loading || routeState.loading}
        onSync={loadMeetingRecords}
      />
    </div>
  );
}
