/* eslint-disable */
import React, { useMemo, useState } from 'react';
import {
  Activity,
  CalendarClock,
  ClipboardList,
  Link2,
  PanelRightClose,
  PanelRightOpen,
  ShieldCheck,
  Sparkles,
  UsersRound,
} from 'lucide-react';
import meetingRoomStyles from './WilsyMeetingOperatingRoom.module.css';

/**
 * @function resolveWilsyMeetingIntelText
 * @description Resolves the first non-empty display value from candidate values.
 * @param {...*} values - Candidate values.
 * @returns {string} Resolved text.
 * @collaboration Meeting intelligence panel, live Meeting records, no-fake-data display.
 */
function resolveWilsyMeetingIntelText(...values) {
  const found = values.find((value) => String(value || '').trim());
  return String(found || '').trim();
}

/**
 * @function resolveWilsyMeetingIntelId
 * @description Resolves a stable Meeting row id.
 * @param {Object} meeting - Meeting record.
 * @param {number} index - Fallback index.
 * @returns {string} Stable id.
 * @collaboration Meeting records intelligence, queue selection, live CRM rows.
 */
function resolveWilsyMeetingIntelId(meeting = {}, index = 0) {
  return resolveWilsyMeetingIntelText(
    meeting._id,
    meeting.id,
    meeting.recordId,
    meeting.meetingId,
    meeting.sourceRecordId,
    `meeting-${index}`
  );
}

/**
 * @function resolveWilsyMeetingIntelStart
 * @description Resolves a valid Meeting start date.
 * @param {Object} meeting - Meeting record.
 * @returns {Date|null} Start date.
 * @collaboration Meeting schedule intelligence, action-window posture.
 */
function resolveWilsyMeetingIntelStart(meeting = {}) {
  const value = resolveWilsyMeetingIntelText(
    meeting.startsAt,
    meeting.startAt,
    meeting.startTime,
    meeting.fromDate && meeting.fromTime ? `${meeting.fromDate}T${meeting.fromTime}` : '',
    meeting.fromDate
  );

  if (!value) return null;

  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? null : date;
}

/**
 * @function resolveWilsyMeetingIntelDuration
 * @description Resolves Meeting duration from start/end fields.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Duration label.
 * @collaboration Meeting schedule intelligence, records command panel.
 */
function resolveWilsyMeetingIntelDuration(meeting = {}) {
  const start = resolveWilsyMeetingIntelStart(meeting);
  const endValue = resolveWilsyMeetingIntelText(
    meeting.endsAt,
    meeting.endAt,
    meeting.endTime,
    meeting.toDate && meeting.toTime ? `${meeting.toDate}T${meeting.toTime}` : '',
    meeting.toDate
  );
  const end = endValue ? new Date(endValue) : null;

  if (!start || !end || Number.isNaN(end.valueOf())) return 'Duration pending';

  const minutes = Math.max(0, Math.round((end.getTime() - start.getTime()) / 60000));
  if (!minutes) return 'Duration pending';
  if (minutes < 60) return `${minutes}m`;

  const hours = Math.floor(minutes / 60);
  const remaining = minutes % 60;

  return remaining ? `${hours}h ${remaining}m` : `${hours}h`;
}

/**
 * @function resolveWilsyMeetingIntelUrgency
 * @description Resolves Meeting timing urgency.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Urgency label.
 * @collaboration Meeting schedule intelligence, action queue.
 */
function resolveWilsyMeetingIntelUrgency(meeting = {}) {
  const start = resolveWilsyMeetingIntelStart(meeting);

  if (!start) return 'Schedule pending';

  const deltaHours = Math.round((start.getTime() - Date.now()) / 3600000);

  if (deltaHours < -24) return 'History';
  if (deltaHours < 0) return 'Follow-up due';
  if (deltaHours <= 4) return 'Imminent';
  if (deltaHours <= 24) return 'Today';
  if (deltaHours <= 168) return 'This week';

  return 'Scheduled';
}

/**
 * @function resolveWilsyMeetingIntelRelated
 * @description Resolves related CRM record posture.
 * @param {Object} meeting - Meeting record.
 * @returns {Object} Related posture.
 * @collaboration Meeting intelligence panel, related CRM evidence.
 */
function resolveWilsyMeetingIntelRelated(meeting = {}) {
  const related = meeting.relatedRecord || meeting.relatedTo || {};
  const title = resolveWilsyMeetingIntelText(
    related.title,
    related.name,
    meeting.relatedRecordTitle,
    meeting.relatedTitle,
    meeting.relatedName,
    meeting.relatedId,
    meeting.relatedRecordId
  );
  const type = resolveWilsyMeetingIntelText(
    related.type,
    related.module,
    meeting.relatedRecordType,
    meeting.relatedType,
    'CRM'
  );
  const id = resolveWilsyMeetingIntelText(
    related.recordId,
    related.id,
    meeting.relatedRecordId,
    meeting.relatedId
  );

  return {
    linked: Boolean(title || id),
    label: title || id ? `${type} · ${title || id}` : 'Association pending',
    detail: id ? `Record ${id}` : 'Link source-backed CRM record',
  };
}

/**
 * @function resolveWilsyMeetingIntelParticipants
 * @description Resolves participant and host posture.
 * @param {Object} meeting - Meeting record.
 * @returns {Object} Participant posture.
 * @collaboration Meeting intelligence panel, participant graph, host accountability.
 */
function resolveWilsyMeetingIntelParticipants(meeting = {}) {
  const participants = Array.isArray(meeting.participants)
    ? meeting.participants
    : Array.isArray(meeting.attendees)
      ? meeting.attendees
      : [];
  const host = resolveWilsyMeetingIntelText(
    meeting.host,
    meeting.ownerDisplayName,
    meeting.ownerName,
    meeting.ownerId,
    'Host pending'
  );

  return {
    count: participants.length,
    label: participants.length ? `${participants.length} participant${participants.length === 1 ? '' : 's'}` : 'Participants pending',
    detail: `Host ${host}`,
  };
}

/**
 * @function resolveWilsyMeetingIntelAgenda
 * @description Resolves agenda, venue, type and outcome posture.
 * @param {Object} meeting - Meeting record.
 * @returns {Object} Agenda posture.
 * @collaboration Meeting intelligence panel, agenda command posture.
 */
function resolveWilsyMeetingIntelAgenda(meeting = {}) {
  const agenda = resolveWilsyMeetingIntelText(meeting.description, meeting.agenda, meeting.notes);
  const outcome = resolveWilsyMeetingIntelText(meeting.outcome, meeting.result, meeting.disposition);
  const meetingType = resolveWilsyMeetingIntelText(meeting.meetingType, meeting.type, 'Meeting');
  const venue = resolveWilsyMeetingIntelText(
    meeting.meetingVenue,
    meeting.meetingVenueLabel,
    meeting.venue,
    meeting.location,
    'Venue pending'
  );

  return {
    ready: Boolean(agenda || outcome),
    label: `${meetingType} · ${venue}`,
    detail: outcome || (agenda ? `${agenda.slice(0, 96)}${agenda.length > 96 ? '…' : ''}` : 'Agenda pending'),
  };
}

/**
 * @function resolveWilsyMeetingIntelEvidence
 * @description Resolves Meeting evidence and source posture.
 * @param {Object} meeting - Meeting record.
 * @returns {Object} Evidence posture.
 * @collaboration Meeting intelligence panel, audit/evidence/source posture.
 */
function resolveWilsyMeetingIntelEvidence(meeting = {}) {
  const auditCount = Array.isArray(meeting.auditTrail) ? meeting.auditTrail.length : 0;
  const source = resolveWilsyMeetingIntelText(meeting.sourceSystem, meeting.source, 'wilsy-live-crm');
  const anchored = Boolean(
    meeting.evidence ||
    meeting.metadata ||
    meeting.auditMesh ||
    meeting.wilsyPersistenceContract ||
    auditCount
  );

  return {
    anchored,
    label: anchored ? 'Evidence anchored' : 'Evidence pending',
    detail: `${source} · ${auditCount} audit event${auditCount === 1 ? '' : 's'}`,
  };
}

/**
 * @function buildWilsyMeetingIntelRows
 * @description Builds enriched additive intelligence rows from Meeting records.
 * @param {Array<Object>} records - Meeting records.
 * @returns {Array<Object>} Intelligence rows.
 * @collaboration Meeting records, additive command panel, live CRM route data.
 */
function buildWilsyMeetingIntelRows(records = []) {
  return records.map((meeting, index) => {
    const id = resolveWilsyMeetingIntelId(meeting, index);
    const title = resolveWilsyMeetingIntelText(
      meeting.title,
      meeting.subject,
      meeting.meetingTitle,
      meeting.name,
      id
    );
    const related = resolveWilsyMeetingIntelRelated(meeting);
    const participants = resolveWilsyMeetingIntelParticipants(meeting);
    const agenda = resolveWilsyMeetingIntelAgenda(meeting);
    const evidence = resolveWilsyMeetingIntelEvidence(meeting);
    const start = resolveWilsyMeetingIntelStart(meeting);
    const urgency = resolveWilsyMeetingIntelUrgency(meeting);
    const duration = resolveWilsyMeetingIntelDuration(meeting);
    const readiness = [
      related.linked,
      participants.count > 0,
      agenda.ready,
      evidence.anchored,
      Boolean(start),
    ].filter(Boolean).length * 20;

    return {
      id,
      title,
      related,
      participants,
      agenda,
      evidence,
      start,
      urgency,
      duration,
      readiness,
    };
  });
}

/**
 * @function buildWilsyMeetingIntelMetrics
 * @description Builds compact Meeting intelligence metrics.
 * @param {Array<Object>} rows - Intelligence rows.
 * @returns {Array<Object>} Metric rows.
 * @collaboration Meeting intelligence panel, records overview, operator command posture.
 */
function buildWilsyMeetingIntelMetrics(rows = []) {
  const total = rows.length;
  const linked = rows.filter((row) => row.related.linked).length;
  const people = rows.filter((row) => row.participants.count > 0).length;
  const evidence = rows.filter((row) => row.evidence.anchored).length;
  const actionWindow = rows.filter((row) => ['Follow-up due', 'Imminent', 'Today'].includes(row.urgency)).length;

  return [
    { id: 'total', label: 'Live meetings', value: total, detail: 'source rows' },
    { id: 'action', label: 'Action window', value: actionWindow, detail: 'due / imminent / today' },
    { id: 'linked', label: 'CRM linked', value: linked, detail: `${total - linked} pending` },
    { id: 'people', label: 'People mapped', value: people, detail: 'participant graph' },
    { id: 'proof', label: 'Evidence', value: evidence, detail: 'anchored rows' },
  ];
}

/**
 * @function WilsyMeetingRecordsIntelligencePanel
 * @description Renders additive Meeting records intelligence without mutating shared mapper/resolver functions.
 * @param {Object} props - Component props.
 * @param {Array<Object>} props.records - Meeting records.
 * @param {boolean} props.loading - Loading state.
 * @param {Function} props.onSync - Sync callback.
 * @returns {JSX.Element} Meeting intelligence panel.
 * @collaboration WilsyMeetingOperatingRoom, live Meetings route, shared Lead records shell.
 */
export default function WilsyMeetingRecordsIntelligencePanel({ records = [], loading = false, onSync }) {
  const rows = useMemo(() => buildWilsyMeetingIntelRows(Array.isArray(records) ? records : []), [records]);
  const metrics = useMemo(() => buildWilsyMeetingIntelMetrics(rows), [rows]);
  const nextRow = useMemo(() => (
    rows
      .filter((row) => row.start)
      .sort((a, b) => Math.abs(a.start.getTime() - Date.now()) - Math.abs(b.start.getTime() - Date.now()))[0] ||
    rows[0] ||
    null
  ), [rows]);
  const [selectedId, setSelectedId] = useState('');
  const [collapsed, setCollapsed] = useState(true);
  const selectedRow = rows.find((row) => row.id === selectedId) || nextRow;

  return (
    <aside
      className={meetingRoomStyles.meetingIntelPanel}
      data-wilsy-r91k179e24p57f4="meeting-records-intelligence"
      data-wilsy-r91k179e24p57h="ai-pill-intelligence"
      data-collapsed={collapsed ? 'true' : 'false'}
    >
      <header className={meetingRoomStyles.meetingIntelHeader}>
        <div className={meetingRoomStyles.meetingIntelHeaderBar}>
          <span><Sparkles size={18} /> Meeting Intelligence</span>
          <button
            type="button"
            className={meetingRoomStyles.meetingIntelCollapseButton}
            onClick={() => setCollapsed((previous) => !previous)}
            aria-label={collapsed ? 'Expand Meeting Intelligence panel' : 'Collapse Meeting Intelligence panel'}
          >
            {collapsed ? <PanelRightOpen size={16} /> : <PanelRightClose size={16} />}
          </button>
        </div>
        <strong>{selectedRow ? selectedRow.urgency : 'Awaiting rows'}</strong>
        <p>Live posture for schedule, people, related CRM association, agenda and evidence.</p>
        <button type="button" onClick={onSync} disabled={loading}>
          <Activity size={15} /> {loading ? 'Syncing' : 'Sync live'}
        </button>
      </header>

      {!collapsed ? (
        <>
          <section className={meetingRoomStyles.meetingIntelMetricGrid} aria-label="Meeting intelligence metrics">
            {metrics.map((metric) => (
              <article key={metric.id}>
                <small>{metric.label}</small>
                <strong>{metric.value}</strong>
                <span>{metric.detail}</span>
              </article>
            ))}
          </section>

          {selectedRow ? (
            <section className={meetingRoomStyles.meetingIntelFocus} aria-label="Selected meeting command focus">
              <header>
                <small>Command focus</small>
                <strong>{selectedRow.title}</strong>
                <span>{selectedRow.duration} · {selectedRow.urgency} · {selectedRow.readiness}% ready</span>
              </header>

              <div className={meetingRoomStyles.meetingIntelSignalGrid}>
                <article data-ready={selectedRow.related.linked ? 'true' : 'false'}>
                  <Link2 size={17} />
                  <strong>{selectedRow.related.label}</strong>
                  <span>{selectedRow.related.detail}</span>
                </article>
                <article data-ready={selectedRow.participants.count > 0 ? 'true' : 'false'}>
                  <UsersRound size={17} />
                  <strong>{selectedRow.participants.label}</strong>
                  <span>{selectedRow.participants.detail}</span>
                </article>
                <article data-ready={selectedRow.agenda.ready ? 'true' : 'false'}>
                  <ClipboardList size={17} />
                  <strong>{selectedRow.agenda.label}</strong>
                  <span>{selectedRow.agenda.detail}</span>
                </article>
                <article data-ready={selectedRow.evidence.anchored ? 'true' : 'false'}>
                  <ShieldCheck size={17} />
                  <strong>{selectedRow.evidence.label}</strong>
                  <span>{selectedRow.evidence.detail}</span>
                </article>
              </div>
            </section>
          ) : (
            <section className={meetingRoomStyles.meetingIntelEmpty}>
              <CalendarClock size={22} />
              <strong>No live meeting rows</strong>
              <span>Sync live CRM Meetings to activate the command panel.</span>
            </section>
          )}

          <section className={meetingRoomStyles.meetingIntelQueue} aria-label="Meeting command queue">
            <header>
              <small>Operator queue</small>
              <strong>{rows.length} source-backed meeting{rows.length === 1 ? '' : 's'}</strong>
            </header>
            <div>
              {rows.slice(0, 5).map((row) => (
                <button
                  type="button"
                  key={row.id}
                  data-active={selectedRow?.id === row.id ? 'true' : 'false'}
                  onClick={() => setSelectedId(row.id)}
                >
                  <span>{row.urgency}</span>
                  <strong>{row.title}</strong>
                  <small>{row.agenda.label}</small>
                </button>
              ))}
            </div>
          </section>
        </>
      ) : null}
    </aside>
  );
}
