/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM MEETING NOTIFICATION SERVICE [R91K179E28]                                         ║
 * ║ CALENDAR INVITES | TENANT-BRANDED EMAIL | SMS NUDGE | RESCHEDULE LINKS | RECEIPT EVIDENCE        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: R91K179E28-PRODUCTION-BRIDGE | MEETING SAVE TO CALENDAR/EVENT NOTIFICATION AUTHORITY    ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/wilsyMeetingNotificationService.js ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                             ║
 * ║ - Wilson Khanyezi (Founder/CEO) mandated Meetings that dispatch branded invites immediately.      ║
 * ║ - AI Engineering (Codex) wired CRM Meeting persistence to calendar/email/SMS invitation receipts. ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import emailService from './emailService.js';
import { sendSMS } from './smsService.js';
import loggerRaw from '../utils/logger.js';

const logger = loggerRaw.default || loggerRaw;

const WILSY_MEETING_NOTIFICATION_VERSION = 'R91K179E28_MEETING_NOTIFICATION_COMMAND';

/**
 * @function normalizeWilsyR91K179E28Text
 * @description Normalizes Meeting notification text without inventing business data.
 * @param {*} value - Raw value.
 * @param {string} fallback - Fallback text.
 * @returns {string} Normalized text.
 * @collaboration Meeting invite rendering, calendar serialization, SMS copy.
 */
function normalizeWilsyR91K179E28Text(value, fallback = '') {
  const cleaned = String(value || '')
    .replace(/\s+/g, ' ')
    .trim();
  return cleaned || fallback;
}

/**
 * @function escapeWilsyR91K179E28Html
 * @description Escapes user-controlled Meeting fields before tenant-branded email rendering.
 * @param {*} value - Raw value.
 * @returns {string} HTML-safe value.
 * @collaboration Email invite template, meeting description safety, tenant branding.
 */
function escapeWilsyR91K179E28Html(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * @function escapeWilsyR91K179E28IcsText
 * @description Escapes Meeting text for RFC 5545 iCalendar fields.
 * @param {*} value - Raw value.
 * @returns {string} ICS-safe value.
 * @collaboration Calendar invite VEVENT, participant email clients, Meeting workspace.
 */
function escapeWilsyR91K179E28IcsText(value) {
  return normalizeWilsyR91K179E28Text(value)
    .replace(/\\/g, '\\\\')
    .replace(/\n/g, '\\n')
    .replace(/,/g, '\\,')
    .replace(/;/g, '\\;');
}

/**
 * @function foldWilsyR91K179E28IcsLine
 * @description Folds long iCalendar lines for broad email client compatibility.
 * @param {string} line - Raw ICS line.
 * @returns {string} Folded ICS line.
 * @collaboration RFC 5545 formatting, calendar attachment generation.
 */
function foldWilsyR91K179E28IcsLine(line = '') {
  const text = String(line || '');
  if (text.length <= 74) return text;

  const chunks = [];
  for (let index = 0; index < text.length; index += 74) {
    chunks.push((index === 0 ? '' : ' ') + text.slice(index, index + 74));
  }

  return chunks.join('\r\n');
}

/**
 * @function formatWilsyR91K179E28IcsDate
 * @description Converts a JavaScript date into UTC iCalendar timestamp format.
 * @param {Date} date - Date candidate.
 * @returns {string} iCalendar UTC timestamp.
 * @collaboration VEVENT DTSTART, VEVENT DTEND, email calendar clients.
 */
function formatWilsyR91K179E28IcsDate(date) {
  return date
    .toISOString()
    .replace(/[-:]/g, '')
    .replace(/\.\d{3}Z$/, 'Z');
}

/**
 * @function parseWilsyR91K179E28Date
 * @description Parses persisted Meeting date values safely.
 * @param {*} value - Date value.
 * @returns {Date|null} Valid date or null.
 * @collaboration Meeting command payload, calendar invite generation.
 */
function parseWilsyR91K179E28Date(value) {
  if (!value) return null;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

/**
 * @function buildWilsyR91K179E28DateTime
 * @description Builds a Date from separate date and time fields when possible.
 * @param {string} dateValue - Date input.
 * @param {string} timeValue - Time input.
 * @returns {Date|null} Parsed date or null.
 * @collaboration Meeting editor fields, calendar invite generation.
 */
function buildWilsyR91K179E28DateTime(dateValue = '', timeValue = '') {
  const date = String(dateValue || '').trim();
  const time = String(timeValue || '').trim();
  if (!date || !time) return null;

  const parsed = new Date(`${date}T${time}`);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

/**
 * @function resolveWilsyR91K179E28MeetingId
 * @description Resolves the stable Meeting id for URLs, UID and receipts.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Stable Meeting id.
 * @collaboration CRM command route, calendar UID, invitation evidence.
 */
function resolveWilsyR91K179E28MeetingId(meeting = {}) {
  return normalizeWilsyR91K179E28Text(
    meeting.recordId || meeting.meetingId || meeting.id || meeting._id || '',
    crypto.randomUUID()
  );
}

/**
 * @function resolveWilsyR91K179E28PublicBaseUrl
 * @description Resolves the public app URL used by meeting action links.
 * @param {Object} request - Express request.
 * @returns {string} Public base URL.
 * @collaboration Tenant email links, reschedule action links, CRM frontend.
 */
function resolveWilsyR91K179E28PublicBaseUrl(request = {}) {
  const configured = normalizeWilsyR91K179E28Text(
    process.env.WILSY_PUBLIC_APP_URL ||
      process.env.CLIENT_URL ||
      process.env.FRONTEND_URL ||
      process.env.APP_URL ||
      ''
  );

  if (configured) return configured.replace(/\/+$/, '');

  const proto = normalizeWilsyR91K179E28Text(
    request.headers?.['x-forwarded-proto'] || request.protocol || 'http',
    'http'
  ).split(',')[0];
  const host = normalizeWilsyR91K179E28Text(
    request.headers?.['x-forwarded-host'] || request.headers?.host || 'localhost:3000',
    'localhost:3000'
  ).split(',')[0];

  return `${proto}://${host}`.replace(/\/+$/, '');
}

/**
 * @function resolveWilsyR91K179E28Branding
 * @description Resolves tenant branding from command payload and environment defaults.
 * @param {Object} args - Branding arguments.
 * @returns {Object} Branding configuration.
 * @collaboration Tenant config, Wilsy OS email identity, CRM command receipts.
 */
function resolveWilsyR91K179E28Branding({ command = {}, request = {} } = {}) {
  const bodyBranding = command.body?.tenantBranding || command.body?.branding || {};
  const headerBranding = command.institutionalHeaders?.tenantBranding || {};
  const branding = { ...headerBranding, ...bodyBranding };
  const brandName = normalizeWilsyR91K179E28Text(
    branding.brandName ||
      branding.name ||
      command.body?.tenantName ||
      command.institutionalHeaders?.tenantName ||
      process.env.WILSY_TENANT_BRAND_NAME ||
      process.env.EMAIL_NAME ||
      'Wilsy OS'
  );

  return {
    brandName,
    legalName: normalizeWilsyR91K179E28Text(
      branding.legalName || process.env.WILSY_TENANT_LEGAL_NAME || brandName
    ),
    logoUrl: normalizeWilsyR91K179E28Text(
      branding.logoUrl || branding.logo || process.env.WILSY_TENANT_LOGO_URL || ''
    ),
    primaryColor: normalizeWilsyR91K179E28Text(
      branding.primaryColor || process.env.WILSY_TENANT_PRIMARY_COLOR || '#31e981'
    ),
    accentColor: normalizeWilsyR91K179E28Text(
      branding.accentColor || process.env.WILSY_TENANT_ACCENT_COLOR || '#d8c779'
    ),
    supportEmail: normalizeWilsyR91K179E28Text(
      branding.supportEmail ||
        command.institutionalHeaders?.operatorEmail ||
        process.env.WILSY_SUPPORT_EMAIL ||
        process.env.EMAIL_FROM ||
        'support@wilsyos.com'
    ),
    appUrl: resolveWilsyR91K179E28PublicBaseUrl(request),
  };
}

/**
 * @function normalizeWilsyR91K179E28Participant
 * @description Normalizes one Meeting participant for email and SMS notification routing.
 * @param {*} participant - Raw participant value.
 * @returns {Object|null} Normalized participant or null.
 * @collaboration Participant resolver, Meeting save payload, invitation dispatcher.
 */
function normalizeWilsyR91K179E28Participant(participant) {
  if (typeof participant === 'string') {
    const cleaned = normalizeWilsyR91K179E28Text(participant);
    if (!cleaned) return null;
    return {
      name: cleaned.includes('@') ? cleaned.split('@')[0] : cleaned,
      email: cleaned.includes('@') ? cleaned.toLowerCase() : '',
      phone: '',
      sourceType: cleaned.includes('@') ? 'EMAIL' : 'EXTERNAL',
      raw: participant,
    };
  }

  if (!participant || typeof participant !== 'object') return null;

  const email = normalizeWilsyR91K179E28Text(
    participant.email ||
      participant.normalizedEmail ||
      participant.emailAddress ||
      participant.mail ||
      participant.value ||
      ''
  ).toLowerCase();
  const phone = normalizeWilsyR91K179E28Text(
    participant.phone ||
      participant.phoneNumber ||
      participant.mobile ||
      participant.mobileNumber ||
      participant.telephone ||
      ''
  );
  const name = normalizeWilsyR91K179E28Text(
    participant.displayName ||
      participant.fullName ||
      participant.name ||
      participant.label ||
      participant.title ||
      email ||
      phone ||
      'Meeting participant'
  );

  if (!email && !phone && !name) return null;

  return {
    ...participant,
    name,
    email: email.includes('@') ? email : '',
    phone,
    sourceType: normalizeWilsyR91K179E28Text(
      participant.sourceType || participant.type || participant.source || 'CRM'
    ),
    raw: participant,
  };
}

/**
 * @function resolveWilsyR91K179E28Participants
 * @description Resolves Meeting participants from supported arrays.
 * @param {Object} meeting - Meeting record.
 * @returns {Array<Object>} Normalized participants.
 * @collaboration Participants, attendees, invitees, email/SMS dispatch.
 */
function resolveWilsyR91K179E28Participants(meeting = {}) {
  const rawParticipants = Array.isArray(meeting.participants)
    ? meeting.participants
    : Array.isArray(meeting.attendees)
      ? meeting.attendees
      : Array.isArray(meeting.invitees)
        ? meeting.invitees
        : [];

  const seen = new Set();

  return rawParticipants
    .map((participant) => normalizeWilsyR91K179E28Participant(participant))
    .filter((participant) => {
      if (!participant) return false;
      const key = participant.email || participant.phone || participant.name;
      if (!key || seen.has(key)) return false;
      seen.add(key);
      return true;
    });
}

/**
 * @function resolveWilsyR91K179E28Schedule
 * @description Resolves the Meeting schedule for email and calendar invites.
 * @param {Object} meeting - Meeting record.
 * @returns {Object} Schedule result.
 * @collaboration Meeting date fields, calendar invite attachment, email details.
 */
function resolveWilsyR91K179E28Schedule(meeting = {}) {
  const startsAt =
    parseWilsyR91K179E28Date(meeting.startsAt || meeting.startAt) ||
    buildWilsyR91K179E28DateTime(meeting.fromDate, meeting.fromTime);
  const endsAt =
    parseWilsyR91K179E28Date(meeting.endsAt || meeting.endAt) ||
    buildWilsyR91K179E28DateTime(meeting.toDate, meeting.toTime) ||
    (startsAt ? new Date(startsAt.getTime() + 30 * 60 * 1000) : null);

  return {
    startsAt,
    endsAt,
    hasCalendarSlot: Boolean(startsAt && endsAt),
    displayDate: startsAt
      ? new Intl.DateTimeFormat('en-ZA', { dateStyle: 'medium', timeStyle: 'short' }).format(
          startsAt
        )
      : 'Date and time pending',
    displayEnd: endsAt
      ? new Intl.DateTimeFormat('en-ZA', { dateStyle: 'medium', timeStyle: 'short' }).format(endsAt)
      : 'End time pending',
  };
}

/**
 * @function inferWilsyR91K179E28MeetingTemplate
 * @description Uses Wilsy AI-style deterministic routing to select an email structure from the meeting description.
 * @param {Object} meeting - Meeting record.
 * @returns {Object} Template intelligence profile.
 * @collaboration Meeting description, agenda intelligence, email template selection.
 */
function inferWilsyR91K179E28MeetingTemplate(meeting = {}) {
  const description = normalizeWilsyR91K179E28Text(
    meeting.description || meeting.agenda
  ).toLowerCase();
  const title = normalizeWilsyR91K179E28Text(
    meeting.title || meeting.subject || meeting.meetingTitle,
    'Meeting'
  );
  const rules = [
    {
      id: 'revenue',
      label: 'Revenue command meeting',
      words: ['sales', 'deal', 'pipeline', 'proposal', 'revenue', 'client'],
      focus: 'commercial outcomes and next-step ownership',
    },
    {
      id: 'legal',
      label: 'Legal evidence meeting',
      words: ['court', 'legal', 'evidence', 'contract', 'matter', 'compliance'],
      focus: 'evidence, obligations and decision traceability',
    },
    {
      id: 'support',
      label: 'Client success meeting',
      words: ['support', 'issue', 'ticket', 'resolve', 'customer', 'service'],
      focus: 'resolution path and client confidence',
    },
    {
      id: 'risk',
      label: 'Risk command meeting',
      words: ['risk', 'incident', 'security', 'audit', 'breach', 'urgent'],
      focus: 'risk posture, containment and escalation clarity',
    },
  ];
  const matched = rules.find((rule) => rule.words.some((word) => description.includes(word))) || {
    id: 'general',
    label: 'Executive meeting command',
    focus: 'agenda clarity, preparation and follow-up accountability',
  };

  return {
    ...matched,
    subjectPrefix: matched.id === 'general' ? 'Meeting invite' : matched.label,
    agendaHeadline: `Wilsy AI structured this invite for ${matched.focus}.`,
    title,
    generatedAt: new Date().toISOString(),
    engine: WILSY_MEETING_NOTIFICATION_VERSION,
  };
}

/**
 * @function buildWilsyR91K179E28MeetingUrls
 * @description Builds attendee action URLs for open and reschedule actions.
 * @param {Object} args - URL build arguments.
 * @returns {Object} Meeting action URLs.
 * @collaboration Email CTA buttons, reschedule requests, calendar description.
 */
function buildWilsyR91K179E28MeetingUrls({ branding, meetingId, participant, receiptToken }) {
  const encodedParticipant = encodeURIComponent(
    participant.email || participant.phone || participant.name || 'participant'
  );
  const encodedToken = encodeURIComponent(receiptToken);
  const encodedMeetingId = encodeURIComponent(meetingId);

  return {
    openUrl: `${branding.appUrl}/crm/meetings/${encodedMeetingId}?invite=${encodedToken}`,
    rescheduleUrl: `${branding.appUrl}/crm/meetings/${encodedMeetingId}/reschedule?participant=${encodedParticipant}&token=${encodedToken}`,
  };
}

/**
 * @function buildWilsyR91K179E28CalendarInvite
 * @description Builds a request-mode .ics calendar invite for Meeting attendees.
 * @param {Object} args - Calendar invite arguments.
 * @returns {Object} Calendar invite packet.
 * @collaboration RFC 5545 VEVENT, Nodemailer icalEvent, Meeting CRM evidence.
 */
function buildWilsyR91K179E28CalendarInvite({
  meeting,
  participants,
  branding,
  schedule,
  calendarUid,
  sequence,
  rescheduleUrl,
}) {
  if (!schedule.hasCalendarSlot) {
    return {
      uid: calendarUid,
      sequence,
      method: 'REQUEST',
      hasAttachment: false,
      filename: 'wilsy-meeting.ics',
      content: '',
      reason: 'SCHEDULE_PENDING',
    };
  }

  const title = normalizeWilsyR91K179E28Text(
    meeting.title || meeting.subject || meeting.meetingTitle,
    'Wilsy OS Meeting'
  );
  const location = normalizeWilsyR91K179E28Text(
    [meeting.meetingVenue || meeting.venue || meeting.locationType, meeting.location]
      .filter(Boolean)
      .join(' - '),
    'Location pending'
  );
  const description = [
    normalizeWilsyR91K179E28Text(meeting.description || meeting.agenda, 'Agenda pending.'),
    `Reschedule request: ${rescheduleUrl}`,
    `Powered by ${branding.brandName}`,
  ].join('\\n\\n');
  const organizerEmail = branding.supportEmail || 'support@wilsyos.com';
  const lines = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//Wilsy OS//CRM Meetings//EN',
    'CALSCALE:GREGORIAN',
    'METHOD:REQUEST',
    'BEGIN:VEVENT',
    `UID:${escapeWilsyR91K179E28IcsText(calendarUid)}`,
    `SEQUENCE:${Number(sequence) || 0}`,
    `DTSTAMP:${formatWilsyR91K179E28IcsDate(new Date())}`,
    `DTSTART:${formatWilsyR91K179E28IcsDate(schedule.startsAt)}`,
    `DTEND:${formatWilsyR91K179E28IcsDate(schedule.endsAt)}`,
    `SUMMARY:${escapeWilsyR91K179E28IcsText(title)}`,
    `DESCRIPTION:${escapeWilsyR91K179E28IcsText(description)}`,
    `LOCATION:${escapeWilsyR91K179E28IcsText(location)}`,
    `ORGANIZER;CN=${escapeWilsyR91K179E28IcsText(branding.brandName)}:mailto:${organizerEmail}`,
    ...participants
      .filter((participant) => participant.email)
      .map(
        (participant) =>
          `ATTENDEE;CN=${escapeWilsyR91K179E28IcsText(participant.name)};ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:mailto:${participant.email}`
      ),
    'STATUS:CONFIRMED',
    'TRANSP:OPAQUE',
    'END:VEVENT',
    'END:VCALENDAR',
  ];

  return {
    uid: calendarUid,
    sequence,
    method: 'REQUEST',
    hasAttachment: true,
    filename: 'wilsy-meeting.ics',
    content: `${lines.map(foldWilsyR91K179E28IcsLine).join('\r\n')}\r\n`,
    reason: '',
  };
}

/**
 * @function buildWilsyR91K179E28MeetingEmail
 * @description Builds the tenant-branded Meeting invitation email body and text fallback.
 * @param {Object} args - Email arguments.
 * @returns {Object} Email packet.
 * @collaboration Wilsy AI email structure, tenant branding, participant invite.
 */
function buildWilsyR91K179E28MeetingEmail({
  meeting,
  participant,
  branding,
  schedule,
  aiTemplate,
  urls,
}) {
  const title = normalizeWilsyR91K179E28Text(
    meeting.title || meeting.subject || meeting.meetingTitle,
    'Meeting'
  );
  const venue = normalizeWilsyR91K179E28Text(
    meeting.meetingVenue || meeting.venue || meeting.locationType,
    'Venue pending'
  );
  const location = normalizeWilsyR91K179E28Text(meeting.location, 'Location pending');
  const host = normalizeWilsyR91K179E28Text(
    meeting.host || meeting.owner || meeting.createdBy,
    branding.brandName
  );
  const agenda = normalizeWilsyR91K179E28Text(
    meeting.description || meeting.agenda,
    'Agenda pending. Wilsy OS will update this invite when the agenda is captured.'
  );
  const safeBrand = escapeWilsyR91K179E28Html(branding.brandName);
  const logo = branding.logoUrl
    ? `<img src="${escapeWilsyR91K179E28Html(branding.logoUrl)}" alt="${safeBrand}" style="max-height:44px; margin-bottom:18px;" />`
    : `<div style="font-size:13px; letter-spacing:5px; text-transform:uppercase; color:${branding.accentColor}; margin-bottom:16px;">${safeBrand}</div>`;
  const details = [
    ['Meeting', title],
    ['When', `${schedule.displayDate} to ${schedule.displayEnd}`],
    ['Venue', venue],
    ['Location', location],
    ['Host', host],
    ['Focus', aiTemplate.focus],
  ];
  const detailRows = details
    .map(
      ([label, value]) => `
    <tr>
      <td style="padding:10px 12px; color:#d8c779; font-size:12px; letter-spacing:2px; text-transform:uppercase; border-bottom:1px solid #1e2a38;">${escapeWilsyR91K179E28Html(label)}</td>
      <td style="padding:10px 12px; color:#f8fafc; font-weight:700; border-bottom:1px solid #1e2a38;">${escapeWilsyR91K179E28Html(value)}</td>
    </tr>
  `
    )
    .join('');

  const html = `
    <div style="margin:0; padding:0; background:#02060d; color:#f8fafc; font-family:Inter, Segoe UI, Arial, sans-serif;">
      <div style="max-width:720px; margin:0 auto; padding:34px 22px;">
        <div style="border:1px solid #203247; border-radius:18px; overflow:hidden; background:#07111f;">
          <div style="padding:30px; background:linear-gradient(135deg, rgba(49,233,129,.18), rgba(216,199,121,.10));">
            ${logo}
            <div style="font-size:12px; letter-spacing:3px; text-transform:uppercase; color:${branding.accentColor};">Wilsy AI Meeting Command</div>
            <h1 style="margin:10px 0 8px; font-size:30px; line-height:1.15; color:#ffffff;">${escapeWilsyR91K179E28Html(title)}</h1>
            <p style="margin:0; color:#c6d1e0; font-size:16px;">${escapeWilsyR91K179E28Html(aiTemplate.agendaHeadline)}</p>
          </div>
          <div style="padding:28px 30px;">
            <table role="presentation" style="width:100%; border-collapse:collapse; background:#050b14; border:1px solid #1e2a38; border-radius:12px; overflow:hidden;">
              ${detailRows}
            </table>
            <div style="margin-top:24px; padding:20px; border-left:4px solid ${branding.primaryColor}; background:#050b14;">
              <div style="font-size:12px; letter-spacing:3px; text-transform:uppercase; color:${branding.accentColor}; margin-bottom:8px;">Agenda</div>
              <p style="margin:0; white-space:pre-line; color:#d9e2ef; line-height:1.55;">${escapeWilsyR91K179E28Html(agenda)}</p>
            </div>
            <div style="margin-top:26px;">
              <a href="${escapeWilsyR91K179E28Html(urls.openUrl)}" style="display:inline-block; padding:13px 18px; margin-right:10px; border-radius:10px; text-decoration:none; color:#02110a; background:${branding.primaryColor}; font-weight:900;">Open Meeting</a>
              <a href="${escapeWilsyR91K179E28Html(urls.rescheduleUrl)}" style="display:inline-block; padding:13px 18px; border-radius:10px; text-decoration:none; color:#f8fafc; border:1px solid ${branding.accentColor}; font-weight:900;">Request Reschedule</a>
            </div>
            <p style="margin:22px 0 0; color:#94a3b8; font-size:13px; line-height:1.5;">If the date changes, Wilsy OS will issue an updated calendar invite with a higher sequence number so attendee calendars receive the new time.</p>
          </div>
        </div>
      </div>
    </div>
  `;

  const text = [
    `${branding.brandName} Meeting Invite: ${title}`,
    `When: ${schedule.displayDate} to ${schedule.displayEnd}`,
    `Venue: ${venue}`,
    `Location: ${location}`,
    `Host: ${host}`,
    `Agenda: ${agenda}`,
    `Open: ${urls.openUrl}`,
    `Reschedule: ${urls.rescheduleUrl}`,
  ].join('\n');

  return {
    subject: `${aiTemplate.subjectPrefix}: ${title}`,
    html,
    text,
  };
}

/**
 * @function buildWilsyR91K179E28MeetingSms
 * @description Builds a compact Meeting SMS invite with a reschedule action link.
 * @param {Object} args - SMS arguments.
 * @returns {string} SMS text.
 * @collaboration SMS invite, Twilio provider, reschedule workflow.
 */
function buildWilsyR91K179E28MeetingSms({ meeting, branding, schedule, urls }) {
  const title = normalizeWilsyR91K179E28Text(
    meeting.title || meeting.subject || meeting.meetingTitle,
    'Meeting'
  );
  return `${branding.brandName}: ${title} on ${schedule.displayDate}. Open ${urls.openUrl}. Reschedule ${urls.rescheduleUrl}`;
}

/**
 * @function buildWilsyR91K179E28ReceiptToken
 * @description Builds a compact token for invite action URLs and receipts.
 * @param {Object} args - Token source arguments.
 * @returns {string} Receipt token.
 * @collaboration Email action URLs, reschedule request link, audit receipts.
 */
function buildWilsyR91K179E28ReceiptToken({ meetingId, participant, tenantId }) {
  return crypto
    .createHash('sha256')
    .update(
      [
        WILSY_MEETING_NOTIFICATION_VERSION,
        tenantId,
        meetingId,
        participant.email || participant.phone || participant.name,
        Date.now(),
      ].join('|')
    )
    .digest('hex')
    .slice(0, 24);
}

/**
 * @function dispatchWilsyMeetingInvitations
 * @description Dispatches Meeting invitation email/SMS notifications and returns persisted receipt fields.
 * @param {Object} args - Dispatch arguments.
 * @returns {Promise<Object>} Notification packet.
 * @collaboration Meeting command routes, emailService, smsService, calendar invite evidence.
 */
export async function dispatchWilsyMeetingInvitations({
  meeting = {},
  command = {},
  tenantId = '',
  operatorId = '',
  request = {},
  saveMode = 'create',
} = {}) {
  const effectiveTenantId = normalizeWilsyR91K179E28Text(
    tenantId || command.tenantId || meeting.tenantId,
    'wilsy-sovereign-root'
  );
  const meetingId = resolveWilsyR91K179E28MeetingId(meeting);
  const participants = resolveWilsyR91K179E28Participants(meeting);
  const branding = resolveWilsyR91K179E28Branding({ command, request });
  const schedule = resolveWilsyR91K179E28Schedule(meeting);
  const aiTemplate = inferWilsyR91K179E28MeetingTemplate(meeting);
  const generatedAt = new Date().toISOString();
  const calendarUid = normalizeWilsyR91K179E28Text(
    meeting.calendarUid,
    `wilsy-meeting-${effectiveTenantId}-${meetingId}@wilsyos.com`
  ).replace(/\s+/g, '-');
  const sequence = Number.isFinite(Number(meeting.calendarSequence))
    ? Number(meeting.calendarSequence) + (saveMode === 'edit' ? 1 : 0)
    : saveMode === 'edit'
      ? 1
      : 0;
  const previewToken = crypto.randomBytes(8).toString('hex');
  const previewUrls = buildWilsyR91K179E28MeetingUrls({
    branding,
    meetingId,
    participant: { email: 'preview@wilsyos.com', name: 'preview' },
    receiptToken: previewToken,
  });
  const calendarInvite = buildWilsyR91K179E28CalendarInvite({
    meeting,
    participants,
    branding,
    schedule,
    calendarUid,
    sequence,
    rescheduleUrl: previewUrls.rescheduleUrl,
  });

  const emailInvitationReceipts = [];
  const smsInvitationReceipts = [];

  for (const participant of participants.filter((entry) => entry.email)) {
    const receiptToken = buildWilsyR91K179E28ReceiptToken({
      meetingId,
      participant,
      tenantId: effectiveTenantId,
    });
    const urls = buildWilsyR91K179E28MeetingUrls({
      branding,
      meetingId,
      participant,
      receiptToken,
    });
    const emailPacket = buildWilsyR91K179E28MeetingEmail({
      meeting,
      participant,
      branding,
      schedule,
      aiTemplate,
      urls,
    });
    const startedAt = new Date().toISOString();

    try {
      const result = await emailService.send({
        to: participant.email,
        subject: emailPacket.subject,
        html: emailPacket.html,
        text: emailPacket.text,
        replyTo: branding.supportEmail,
        icalEvent: calendarInvite.hasAttachment
          ? {
              filename: calendarInvite.filename,
              method: calendarInvite.method,
              content: calendarInvite.content,
            }
          : undefined,
        attachments: calendarInvite.hasAttachment
          ? [
              {
                filename: calendarInvite.filename,
                content: calendarInvite.content,
                contentType: 'text/calendar; method=REQUEST; charset=UTF-8',
              },
            ]
          : [],
        headers: {
          'X-Wilsy-Meeting-ID': meetingId,
          'X-Wilsy-Tenant-ID': effectiveTenantId,
          'X-Wilsy-Calendar-UID': calendarUid,
          'X-Wilsy-Invite-Token': receiptToken,
        },
      });

      emailInvitationReceipts.push({
        channel: 'email',
        participant: participant.name,
        to: participant.email,
        success: Boolean(result?.success),
        provider: result?.provider || (result?.devMode ? 'dev-mode' : ''),
        messageId: result?.messageId || '',
        devMode: Boolean(result?.devMode),
        status: result?.success ? 'SENT' : 'FAILED',
        error: result?.error || '',
        calendarAttached: calendarInvite.hasAttachment,
        receiptToken,
        startedAt,
        completedAt: new Date().toISOString(),
      });
    } catch (error) {
      logger.warn(
        `[MEETING-NOTIFY] Email invite failed for ${participant.email}: ${error.message}`
      );
      emailInvitationReceipts.push({
        channel: 'email',
        participant: participant.name,
        to: participant.email,
        success: false,
        provider: '',
        messageId: '',
        devMode: false,
        status: 'FAILED',
        error: error?.message || 'Email invite failed.',
        calendarAttached: false,
        receiptToken,
        startedAt,
        completedAt: new Date().toISOString(),
      });
    }
  }

  for (const participant of participants.filter((entry) => entry.phone)) {
    const receiptToken = buildWilsyR91K179E28ReceiptToken({
      meetingId,
      participant,
      tenantId: effectiveTenantId,
    });
    const urls = buildWilsyR91K179E28MeetingUrls({
      branding,
      meetingId,
      participant,
      receiptToken,
    });
    const smsMessage = buildWilsyR91K179E28MeetingSms({ meeting, branding, schedule, urls });
    const startedAt = new Date().toISOString();

    try {
      const result = await sendSMS({
        to: participant.phone,
        message: smsMessage,
        ip: request.ip,
        metadata: {
          type: 'meeting-invite',
          meetingId,
          tenantId: effectiveTenantId,
          receiptToken,
        },
      });

      smsInvitationReceipts.push({
        channel: 'sms',
        participant: participant.name,
        to: participant.phone,
        success: Boolean(result?.success),
        provider: result?.provider || '',
        messageId: result?.messageId || '',
        mock: Boolean(result?.mock),
        status: result?.success ? 'SENT' : 'FAILED',
        error: result?.error || '',
        receiptToken,
        startedAt,
        completedAt: new Date().toISOString(),
      });
    } catch (error) {
      logger.warn(`[MEETING-NOTIFY] SMS invite failed for ${participant.phone}: ${error.message}`);
      smsInvitationReceipts.push({
        channel: 'sms',
        participant: participant.name,
        to: participant.phone,
        success: false,
        provider: '',
        messageId: '',
        mock: false,
        status: 'FAILED',
        error: error?.message || 'SMS invite failed.',
        receiptToken,
        startedAt,
        completedAt: new Date().toISOString(),
      });
    }
  }

  const allReceipts = [...emailInvitationReceipts, ...smsInvitationReceipts];
  const sentCount = allReceipts.filter((receipt) => receipt.success).length;
  const failedCount = allReceipts.filter((receipt) => !receipt.success).length;
  const invitationStatus =
    participants.length === 0
      ? 'NO_INVITEES'
      : allReceipts.length === 0
        ? 'NO_DELIVERABLE_CHANNEL'
        : failedCount === 0
          ? 'INVITES_DISPATCHED'
          : sentCount > 0
            ? 'INVITES_PARTIAL'
            : 'INVITES_FAILED';
  const notificationSummary = {
    version: WILSY_MEETING_NOTIFICATION_VERSION,
    invitationStatus,
    generatedAt,
    tenantId: effectiveTenantId,
    operatorId: normalizeWilsyR91K179E28Text(
      operatorId || command.operatorId || command.document?.updatedBy || ''
    ),
    saveMode,
    participantCount: participants.length,
    emailCount: emailInvitationReceipts.length,
    smsCount: smsInvitationReceipts.length,
    sentCount,
    failedCount,
    calendarAttached: calendarInvite.hasAttachment,
  };
  const persistedFields = {
    calendarUid,
    calendarSequence: sequence,
    calendarInvite: {
      uid: calendarInvite.uid,
      method: calendarInvite.method,
      sequence,
      filename: calendarInvite.filename,
      hasAttachment: calendarInvite.hasAttachment,
      reason: calendarInvite.reason,
      generatedAt,
      startsAt: schedule.startsAt,
      endsAt: schedule.endsAt,
      attendeeCount: participants.filter((participant) => participant.email).length,
      rescheduleBaseUrl: previewUrls.rescheduleUrl,
    },
    invitationStatus,
    lastInviteSentAt: generatedAt,
    emailInvitationReceipts,
    smsInvitationReceipts,
    notificationReceipts: [notificationSummary],
    meetingNotificationIntelligence: aiTemplate,
    wilsyMeetingNotificationContract: WILSY_MEETING_NOTIFICATION_VERSION,
  };

  return {
    ok: failedCount === 0,
    ...notificationSummary,
    calendarInvite: persistedFields.calendarInvite,
    aiTemplate,
    emailInvitationReceipts,
    smsInvitationReceipts,
    notificationReceipts: persistedFields.notificationReceipts,
    persistedFields,
  };
}

export default {
  dispatchWilsyMeetingInvitations,
};
