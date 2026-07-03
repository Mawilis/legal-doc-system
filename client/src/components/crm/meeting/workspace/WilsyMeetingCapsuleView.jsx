/* eslint-disable */
import React from 'react';
import { ArrowLeft, CalendarDays, Edit3, Fingerprint, Link2, MapPin, ShieldCheck, Trash2, Users, Zap } from 'lucide-react';
import styles from './WilsyMeetingsWorkspace.module.css';

/**
 * @function resolveWilsyR91K179E22D3BCapsuleId
 * @description Resolves a persisted Meeting record id for capsule display.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Meeting id.
 * @collaboration WilsyMeetingsWorkspace, WilsyMeetingsOverview, CRM live meetings.
 */
function resolveWilsyR91K179E22D3BCapsuleId(meeting = {}) {
  return String(meeting.recordId || meeting.meetingId || meeting.id || meeting._id || '').trim();
}

/**
 * @function resolveWilsyR91K179E22D3BCapsuleVenue
 * @description Resolves venue from real persisted Meeting fields only.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Venue label.
 * @collaboration Meeting editor, venue integrity loop, Meeting capsule.
 */
function resolveWilsyR91K179E22D3BCapsuleVenue(meeting = {}) {
  return String(
    meeting.meetingVenue ||
      meeting.venue ||
      meeting.venueType ||
      meeting.meetingVenueLabel ||
      meeting.locationType ||
      ''
  ).trim();
}

/**
 * @function resolveWilsyR91K179E22D3BCapsuleParticipants
 * @description Resolves participant arrays from supported persisted Meeting fields.
 * @param {Object} meeting - Meeting record.
 * @returns {Array} Participant records.
 * @collaboration Meeting editor, participant graph, Wilsy AI readiness.
 */
function resolveWilsyR91K179E22D3BCapsuleParticipants(meeting = {}) {
  if (Array.isArray(meeting.participants)) return meeting.participants;
  if (Array.isArray(meeting.attendees)) return meeting.attendees;
  if (Array.isArray(meeting.invitees)) return meeting.invitees;
  return [];
}

/**
 * @function resolveWilsyR91K179E22D3BCapsuleRelated
 * @description Resolves related CRM context without fabricating links.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Related CRM label.
 * @collaboration CRM graph, related record command, Meeting capsule.
 */
function resolveWilsyR91K179E22D3BCapsuleRelated(meeting = {}) {
  const related = meeting.relatedRecord || meeting.relatedTo || meeting.crmRecord || '';

  if (!related) return '';
  if (typeof related === 'string') return related;

  return String(related.title || related.name || related.label || related.recordId || related.id || '').trim();
}

/**
 * @function formatWilsyR91K179E22D3BCapsuleDate
 * @description Formats a Meeting date value for capsule timeline display.
 * @param {string|Date} value - Date value.
 * @returns {string} Formatted date label.
 * @collaboration Meeting timeline, records cockpit, operator daily workflow.
 */
function formatWilsyR91K179E22D3BCapsuleDate(value) {
  if (!value) return 'Not scheduled';

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return 'Not scheduled';

  return parsed.toLocaleString(undefined, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * @function resolveWilsyR91K179E22D3BCapsuleReadiness
 * @description Resolves Meeting readiness from real captured fields.
 * @param {Object} meeting - Meeting record.
 * @returns {Object} Readiness summary.
 * @collaboration Wilsy AI, proof ledger, compliance seal, Meeting capsule.
 */
function resolveWilsyR91K179E22D3BCapsuleReadiness(meeting = {}) {
  const venue = resolveWilsyR91K179E22D3BCapsuleVenue(meeting);
  const participants = resolveWilsyR91K179E22D3BCapsuleParticipants(meeting);
  const related = resolveWilsyR91K179E22D3BCapsuleRelated(meeting);
  const hasSchedule = Boolean(meeting.startsAt || meeting.startAt || meeting.fromDate);
  const hasProof = Boolean(
    meeting.wilsyPersistenceContract ||
      meeting.auditMesh ||
      meeting.receiptId ||
      meeting.merkleRoot ||
      meeting.wilsyVenuePersistence
  );

  const blockers = [
    !venue ? 'Venue missing' : '',
    participants.length === 0 ? 'Participants missing' : '',
    !related ? 'CRM link missing' : '',
    !hasSchedule ? 'Schedule missing' : '',
    !hasProof ? 'Proof pending' : '',
  ].filter(Boolean);

  return {
    venue,
    participants,
    related,
    hasProof,
    score: Math.max(0, 100 - blockers.length * 18),
    nextAction:
      !venue ? 'Repair venue' :
      participants.length === 0 ? 'Add participants' :
      !related ? 'Link CRM record' :
      !hasProof ? 'Review proof ledger' :
      'Ready for execution',
  };
}

/**
 * @function WilsyMeetingCapsuleView
 * @description Renders a real Meeting capsule page for Open actions, with schedule, venue, participant graph, CRM link, proof posture and AI next action.
 * @param {Object} props - Component props.
 * @returns {JSX.Element} Meeting capsule view.
 * @collaboration WilsyMeetingsWorkspace, WilsyMeetingEditor, WilsyMeetingsOverview, CRM command evidence.
 */
export default function WilsyMeetingCapsuleView({
  meeting = {},
  onBack = () => {},
  onEdit = () => {},
  onDelete = () => {},
  onOpenEvidence = () => {},
}) {
  const recordId = resolveWilsyR91K179E22D3BCapsuleId(meeting);
  const readiness = resolveWilsyR91K179E22D3BCapsuleReadiness(meeting);
  const title = meeting.title || meeting.subject || meeting.meetingTitle || 'Untitled meeting';
  const status = meeting.status || meeting.persistenceStatus || 'SCHEDULED';
  const start = meeting.startsAt || meeting.startAt || meeting.fromDate;
  const end = meeting.endsAt || meeting.endAt || meeting.toDate;

  return (
    <section className={styles.r91k22d3bCapsulePage} data-wilsy-r91k179e22d3b-view="meeting-capsule">
      <header className={styles.r91k22d3bCapsuleHeader}>
        <button type="button" onClick={onBack} aria-label="Back to meetings">
          <ArrowLeft size={18} />
        </button>

        <div>
          <small>Meeting capsule</small>
          <h2>{title}</h2>
          <p>Record ID · {recordId || 'not returned'}</p>
        </div>

        <nav>
          <button type="button" onClick={onEdit}><Edit3 size={16} />Edit</button>
          <button type="button" onClick={onOpenEvidence}><Fingerprint size={16} />Evidence</button>
          <button type="button" onClick={onDelete}><Trash2 size={16} />Delete</button>
        </nav>
      </header>

      <section className={styles.r91k22d3bCapsuleGrid}>
        <article>
          <CalendarDays size={20} />
          <span>Timeline</span>
          <strong>{formatWilsyR91K179E22D3BCapsuleDate(start)}</strong>
          <p>Ends · {formatWilsyR91K179E22D3BCapsuleDate(end)}</p>
        </article>

        <article data-risk={readiness.venue ? 'ready' : 'warning'}>
          <MapPin size={20} />
          <span>Venue</span>
          <strong>{readiness.venue || 'Venue not captured'}</strong>
          <p>{readiness.venue ? 'Venue exists on record.' : 'Edit this meeting to repair the venue contract.'}</p>
        </article>

        <article data-risk={readiness.participants.length > 0 ? 'ready' : 'warning'}>
          <Users size={20} />
          <span>Participant graph</span>
          <strong>{readiness.participants.length} participant{readiness.participants.length === 1 ? '' : 's'}</strong>
          <p>{readiness.participants.length > 0 ? 'Attendees are bound.' : 'No participants are bound yet.'}</p>
        </article>

        <article data-risk={readiness.related ? 'ready' : 'warning'}>
          <Link2 size={20} />
          <span>CRM link</span>
          <strong>{readiness.related || 'Link pending'}</strong>
          <p>{readiness.related ? 'Meeting is tied to CRM context.' : 'No CRM record is bound yet.'}</p>
        </article>

        <article data-risk={readiness.hasProof ? 'ready' : 'warning'}>
          <ShieldCheck size={20} />
          <span>Proof posture</span>
          <strong>{readiness.hasProof ? 'Proof detected' : 'Proof pending'}</strong>
          <p>Status · {status}</p>
        </article>

        <article>
          <Zap size={20} />
          <span>Wilsy AI next action</span>
          <strong>{readiness.nextAction}</strong>
          <p>{readiness.score}% readiness from real captured fields.</p>
        </article>
      </section>

      <section className={styles.r91k22d3bCapsuleNotes}>
        <small>Agenda / notes</small>
        <p>{meeting.description || meeting.agenda || 'No agenda captured yet.'}</p>
      </section>
    </section>
  );
}
