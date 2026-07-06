/* eslint-disable */
import mongoose from 'mongoose';

/**
 * @function coerceWilsyCalendarText
 * @description Safely coerces calendar bridge input into bounded business text.
 * @param {unknown} value - Raw value.
 * @param {number} limit - Maximum length.
 * @returns {string} Bounded text.
 * @collaboration Wilsy Calendar Execution Bridge, tenant-safe request handling, and connector payload preparation.
 */
function coerceWilsyCalendarText(value = '', limit = 1400) {
  return String(value || '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, limit);
}

/**
 * @function buildWilsyCalendarId
 * @description Builds a stable calendar draft/event identifier for CRM calendar links.
 * @param {string} prefix - Identifier prefix.
 * @returns {string} Stable id.
 * @collaboration CRM Calendar draft links, calendar execution receipts, and operator proof harness.
 */
function buildWilsyCalendarId(prefix = 'cal') {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

/**
 * @function extractWilsyCalendarEmails
 * @description Extracts participant email addresses from a meeting request.
 * @param {string} question - Operator request.
 * @returns {Array<string>} Unique email addresses.
 * @collaboration Calendar participants, meeting draft validation, and connector payload preparation.
 */
function extractWilsyCalendarEmails(question = '') {
  const matches = coerceWilsyCalendarText(question, 2400).match(
    /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi
  );

  return [...new Set(matches || [])];
}

/**
 * @function parseWilsyCalendarTimeParts
 * @description Parses a likely meeting time from the operator request.
 * @param {string} question - Operator request.
 * @returns {{hour: number|null, minute: number, label: string|null}} Parsed time parts.
 * @collaboration Calendar scheduling, business-English meeting drafts, and connector start/end payloads.
 */
function parseWilsyCalendarTimeParts(question = '') {
  const text = coerceWilsyCalendarText(question, 2000);
  const match = text.match(/\b(?:at\s+)?([01]?\d|2[0-3])(?::([0-5]\d))?\s*(am|pm)?\b/i);

  if (!match) {
    return { hour: null, minute: 0, label: null };
  }

  let hour = Number(match[1]);
  const minute = Number(match[2] || 0);
  const meridiem = match[3]?.toLowerCase();

  if (meridiem === 'pm' && hour < 12) {
    hour += 12;
  }

  if (meridiem === 'am' && hour === 12) {
    hour = 0;
  }

  return {
    hour,
    minute,
    label: `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`,
  };
}

/**
 * @function parseWilsyCalendarDurationMinutes
 * @description Parses meeting duration from the operator request.
 * @param {string} question - Operator request.
 * @returns {number} Duration in minutes.
 * @collaboration Calendar draft validation, connector end-time calculation, and governed scheduling commands.
 */
function parseWilsyCalendarDurationMinutes(question = '') {
  const text = coerceWilsyCalendarText(question, 2000);
  const hourMatch = text.match(/(?:duration\s*)?(\d+(?:\.\d+)?)\s*(hour|hours|hr|hrs)\b/i);
  const minuteMatch = text.match(/(?:duration\s*)?(\d+)\s*(minute|minutes|min|mins)\b/i);

  if (hourMatch) {
    return Math.max(15, Math.round(Number(hourMatch[1]) * 60));
  }

  if (minuteMatch) {
    return Math.max(15, Number(minuteMatch[1]));
  }

  return 60;
}

/**
 * @function parseWilsyCalendarDate
 * @description Parses a calendar date from natural meeting language.
 * @param {string} question - Operator request.
 * @param {Date} now - Current date.
 * @returns {{isoDate: string|null, label: string, partial: boolean}} Parsed date metadata.
 * @collaboration Calendar draft preparation, date evidence, and approval-ready command payloads.
 */
function parseWilsyCalendarDate(question = '', now = new Date()) {
  const text = coerceWilsyCalendarText(question, 2200);
  const lower = text.toLowerCase();
  const monthNames = [
    'january',
    'february',
    'march',
    'april',
    'may',
    'june',
    'july',
    'august',
    'september',
    'october',
    'november',
    'december',
  ];
  const monthPattern = monthNames.join('|');
  const dayMonth = new RegExp(
    `\\b(?:on\\s+)?(?:the\\s+)?(\\d{1,2})(?:st|nd|rd|th)?\\s+(?:of\\s+)?(${monthPattern})\\b`,
    'i'
  );
  const monthDay = new RegExp(`\\b(${monthPattern})\\s+(\\d{1,2})(?:st|nd|rd|th)?\\b`, 'i');
  const isoMatch = text.match(/\b(20\d{2})-(\d{2})-(\d{2})\b/);
  const yearMatch = text.match(/\b(20\d{2})\b/);

  if (isoMatch) {
    return {
      isoDate: isoMatch[0],
      label: isoMatch[0],
      partial: false,
    };
  }

  if (lower.includes('today')) {
    return {
      isoDate: now.toISOString().slice(0, 10),
      label: 'today',
      partial: false,
    };
  }

  if (lower.includes('tomorrow')) {
    const value = new Date(now);
    value.setDate(value.getDate() + 1);

    return {
      isoDate: value.toISOString().slice(0, 10),
      label: 'tomorrow',
      partial: false,
    };
  }

  const dayMonthMatch = text.match(dayMonth);
  const monthDayMatch = text.match(monthDay);
  const match = dayMonthMatch || monthDayMatch;

  if (match) {
    const day = Number(dayMonthMatch ? match[1] : match[2]);
    const monthName = String(dayMonthMatch ? match[2] : match[1]).toLowerCase();
    const monthIndex = monthNames.indexOf(monthName);
    let year = Number(yearMatch?.[1] || now.getFullYear());
    let value = new Date(Date.UTC(year, monthIndex, day));

    if (
      !yearMatch &&
      value < new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()))
    ) {
      year += 1;
      value = new Date(Date.UTC(year, monthIndex, day));
    }

    return {
      isoDate: value.toISOString().slice(0, 10),
      label: `${day} ${monthName.replace(/\b\w/g, (letter) => letter.toUpperCase())} ${year}`,
      partial: false,
    };
  }

  if (lower.includes('next week')) {
    return {
      isoDate: null,
      label: 'next week',
      partial: true,
    };
  }

  return {
    isoDate: null,
    label: 'Date not specified',
    partial: true,
  };
}

/**
 * @function buildWilsyCalendarDateTime
 * @description Builds connector-ready date-time values from parsed meeting fields.
 * @param {Object} draft - Calendar draft.
 * @returns {{startDateTime: string|null, endDateTime: string|null}} Date-time payload.
 * @collaboration Google Calendar adapter, Microsoft Graph adapter, and CRM Calendar event storage.
 */
function buildWilsyCalendarDateTime(draft = {}) {
  if (!draft.isoDate || draft.timeParts?.hour === null || draft.timeParts?.hour === undefined) {
    return {
      startDateTime: null,
      endDateTime: null,
    };
  }

  const start = new Date(
    `${draft.isoDate}T${String(draft.timeParts.hour).padStart(2, '0')}:${String(draft.timeParts.minute).padStart(2, '0')}:00`
  );
  const end = new Date(start.getTime() + Number(draft.durationMinutes || 60) * 60 * 1000);

  return {
    startDateTime: `${draft.isoDate}T${String(draft.timeParts.hour).padStart(2, '0')}:${String(draft.timeParts.minute).padStart(2, '0')}:00`,
    endDateTime: `${end.getFullYear()}-${String(end.getMonth() + 1).padStart(2, '0')}-${String(end.getDate()).padStart(2, '0')}T${String(end.getHours()).padStart(2, '0')}:${String(end.getMinutes()).padStart(2, '0')}:00`,
  };
}

/**
 * @function extractWilsyMeetingAgenda
 * @description Extracts a business meeting agenda from the request.
 * @param {string} question - Operator request.
 * @returns {string} Agenda.
 * @collaboration Meeting memo preparation, calendar description, and business-English scheduling replies.
 */
function extractWilsyMeetingAgenda(question = '') {
  const text = coerceWilsyCalendarText(question, 2200);
  const match = text.match(/(?:discuss|discussion|agenda|about)\s+(.+)$/i);

  if (match) {
    return coerceWilsyCalendarText(match[1], 360);
  }

  return 'Agenda not specified';
}

/**
 * @function extractWilsyMeetingSubject
 * @description Extracts a business meeting subject from the request.
 * @param {string} question - Operator request.
 * @returns {string} Meeting subject.
 * @collaboration Calendar draft naming, connector payloads, and tenant-facing meeting responses.
 */
function extractWilsyMeetingSubject(question = '') {
  const text = coerceWilsyCalendarText(question, 2200);
  const match = text.match(
    /meeting\s+with\s+(.+?)(?:\s+on\s+|\s+at\s+|\s+duration|\s+participants|\s+participant|\.|$)/i
  );

  if (match) {
    return `Meeting with ${coerceWilsyCalendarText(match[1], 140)}`;
  }

  return 'Business meeting';
}

/**
 * @function buildWilsyCalendarDescription
 * @description Builds the calendar event description with governance evidence.
 * @param {Object} draft - Calendar draft.
 * @returns {string} Event description.
 * @collaboration Calendar connectors, institutional evidence, and operator approval receipts.
 */
function buildWilsyCalendarDescription(draft = {}) {
  return [
    `Agenda: ${draft.agenda}`,
    `Prepared by: Wilsy OS Operator Kernel`,
    `Execution status: ${draft.executionStatus}`,
    `Governance: Calendar execution requires tenant/operator approval.`,
  ].join('\n');
}

/**
 * @function buildWilsyCalendarDraft
 * @description Builds a validated calendar draft from the operator request.
 * @param {Object} params - Draft params.
 * @param {string} params.question - Operator request.
 * @param {string} params.tenantId - Tenant id.
 * @param {string} params.operatorId - Operator id.
 * @param {string} params.timezone - Timezone.
 * @returns {Object} Calendar draft.
 * @collaboration Meeting scheduling, CRM Calendar draft links, and connector execution readiness.
 */
export function buildWilsyCalendarDraft({
  question = '',
  tenantId = 'MASTER',
  operatorId = 'WILSY_OPERATOR',
  timezone = process.env.WILSY_DEFAULT_TIMEZONE || 'Africa/Johannesburg',
} = {}) {
  const date = parseWilsyCalendarDate(question);
  const timeParts = parseWilsyCalendarTimeParts(question);
  const durationMinutes = parseWilsyCalendarDurationMinutes(question);
  const participants = extractWilsyCalendarEmails(question);
  const draftId = buildWilsyCalendarId('calendar_draft');
  const subject = extractWilsyMeetingSubject(question);
  const agenda = extractWilsyMeetingAgenda(question);
  const timing = buildWilsyCalendarDateTime({
    isoDate: date.isoDate,
    timeParts,
    durationMinutes,
  });
  const missingFields = [];

  if (!date.isoDate) {
    missingFields.push(date.partial ? 'exact meeting date' : 'meeting date');
  }

  if (!timeParts.label) {
    missingFields.push('meeting time');
  }

  if (participants.length === 0) {
    missingFields.push('participant email address');
  }

  return {
    draftId,
    tenantId,
    operatorId,
    subject,
    dateLabel: date.label,
    isoDate: date.isoDate,
    timeLabel: timeParts.label || 'Time not specified',
    timeParts,
    timezone,
    durationMinutes,
    durationLabel: `${durationMinutes} minutes`,
    participants,
    agenda,
    missingFields,
    readyForApproval: missingFields.length === 0,
    startDateTime: timing.startDateTime,
    endDateTime: timing.endDateTime,
    crmCalendarDraftLink: `/crm/calendar/drafts/${draftId}`,
    executionStatus:
      missingFields.length === 0
        ? 'Draft ready for approval. No calendar event has been created yet.'
        : 'Draft incomplete. Missing details must be supplied before approval.',
  };
}

/**
 * @function isWilsyCalendarExecutionApproved
 * @description Verifies whether a calendar execution request has explicit approval.
 * @param {Object} params - Approval params.
 * @param {Object} params.req - Request object.
 * @returns {boolean} Whether execution is approved.
 * @collaboration Human-in-the-loop governance, calendar write safety, and tenant command approval.
 */
function isWilsyCalendarExecutionApproved({ req = {} } = {}) {
  const mode = String(req.query?.executionMode || req.body?.executionMode || '').toUpperCase();
  const approval = String(
    req.query?.approvalToken ||
      req.body?.approvalToken ||
      req.headers?.['x-wilsy-calendar-approval'] ||
      ''
  );

  if (mode !== 'APPROVED_EXECUTE') {
    return false;
  }

  const expected =
    process.env.WILSY_CALENDAR_EXECUTION_APPROVAL_TOKEN || 'P60K5Q10AP_APPROVE_CALENDAR_WRITE';

  return approval === expected;
}

/**
 * @function buildWilsyCalendarHeaders
 * @description Builds institutional headers for calendar execution evidence.
 * @param {Object} params - Header params.
 * @returns {Object} Institutional headers.
 * @collaboration Calendar execution bridge, Wilsy evidence receipts, and tenant/operator proof.
 */
function buildWilsyCalendarHeaders({
  tenantId = 'MASTER',
  operatorId = 'WILSY_OPERATOR',
  route = '/api/source-registry/health',
  commandSurface = 'WILSY_CALENDAR_EXECUTION_BRIDGE',
} = {}) {
  return {
    tenantId,
    operatorId,
    generatedAt: new Date().toISOString(),
    route,
    commandSurface,
    mutation: true,
    contractVersion: 'P60K5Q10AP_CALENDAR_EXECUTION_BRIDGE',
  };
}

/**
 * @function executeWilsyCrmCalendarEvent
 * @description Creates a CRM Calendar event when explicit approval is present and MongoDB is connected.
 * @param {Object} params - Execution params.
 * @param {Object} params.draft - Calendar draft.
 * @param {Object} params.institutionalHeaders - Institutional headers.
 * @returns {Promise<Object>} Execution result.
 * @collaboration CRM Calendar, MongoDB event storage, evidence receipts, and tenant calendar links.
 */
async function executeWilsyCrmCalendarEvent({ draft = {}, institutionalHeaders = {} } = {}) {
  const db = mongoose.connection?.db;

  if (!db) {
    return {
      connector: 'CRM Calendar',
      status: 'CONNECTOR_UNAVAILABLE',
      statusLabel: 'CRM Calendar unavailable',
      eventLink: draft.crmCalendarDraftLink,
      message:
        'CRM Calendar could not create the event because the database connection is unavailable.',
    };
  }

  const eventId = buildWilsyCalendarId('calendar_event');
  const document = {
    eventId,
    tenantId: draft.tenantId,
    operatorId: draft.operatorId,
    subject: draft.subject,
    agenda: draft.agenda,
    participants: draft.participants,
    startDateTime: draft.startDateTime,
    endDateTime: draft.endDateTime,
    timezone: draft.timezone,
    durationMinutes: draft.durationMinutes,
    status: 'SCHEDULED',
    createdAt: new Date(),
    updatedAt: new Date(),
    institutionalHeaders,
    strikePayload: {
      institutionalHeaders,
      commandType: 'CRM_CALENDAR_EVENT_CREATED',
      mutation: true,
    },
  };

  const result = await db.collection('crm_calendar_events').insertOne(document);
  const id = result.insertedId?.toString?.() || eventId;

  return {
    connector: 'CRM Calendar',
    status: 'EVENT_CREATED',
    statusLabel: 'Event created',
    eventId: id,
    eventLink: `/crm/calendar/events/${id}`,
    message: 'The meeting has been created in CRM Calendar.',
  };
}

/**
 * @function executeWilsyGoogleCalendarEvent
 * @description Creates a Google Calendar event when a server-side access token is configured.
 * @param {Object} params - Execution params.
 * @param {Object} params.draft - Calendar draft.
 * @returns {Promise<Object>} Execution result.
 * @collaboration Google Calendar API, tenant calendar connector, and returned event links.
 */
async function executeWilsyGoogleCalendarEvent({ draft = {} } = {}) {
  const token = process.env.WILSY_GOOGLE_CALENDAR_ACCESS_TOKEN;
  const calendarId = process.env.WILSY_GOOGLE_CALENDAR_ID || 'primary';

  if (!token) {
    return {
      connector: 'Google Calendar',
      status: 'CONNECTOR_UNAVAILABLE',
      statusLabel: 'Google Calendar unavailable',
      eventLink: null,
      message: 'Google Calendar token is not configured on the server.',
    };
  }

  const response = await fetch(
    `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(calendarId)}/events`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        summary: draft.subject,
        description: buildWilsyCalendarDescription(draft),
        start: {
          dateTime: draft.startDateTime,
          timeZone: draft.timezone,
        },
        end: {
          dateTime: draft.endDateTime,
          timeZone: draft.timezone,
        },
        attendees: draft.participants.map((email) => ({ email })),
      }),
    }
  );

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    return {
      connector: 'Google Calendar',
      status: 'CONNECTOR_FAILED',
      statusLabel: 'Google Calendar failed',
      eventLink: null,
      message: payload?.error?.message || 'Google Calendar rejected the event creation request.',
    };
  }

  return {
    connector: 'Google Calendar',
    status: 'EVENT_CREATED',
    statusLabel: 'Event created',
    eventId: payload.id,
    eventLink: payload.htmlLink || null,
    message: 'The meeting has been created in Google Calendar.',
  };
}

/**
 * @function executeWilsyMicrosoftCalendarEvent
 * @description Creates a Microsoft Graph calendar event when a server-side access token is configured.
 * @param {Object} params - Execution params.
 * @param {Object} params.draft - Calendar draft.
 * @returns {Promise<Object>} Execution result.
 * @collaboration Microsoft Graph Calendar, tenant calendar connector, and returned event links.
 */
async function executeWilsyMicrosoftCalendarEvent({ draft = {} } = {}) {
  const token = process.env.WILSY_MICROSOFT_GRAPH_ACCESS_TOKEN;
  const calendarUser = process.env.WILSY_MICROSOFT_GRAPH_USER_ID || 'me';

  if (!token) {
    return {
      connector: 'Microsoft Graph Calendar',
      status: 'CONNECTOR_UNAVAILABLE',
      statusLabel: 'Microsoft Graph Calendar unavailable',
      eventLink: null,
      message: 'Microsoft Graph calendar token is not configured on the server.',
    };
  }

  const response = await fetch(`https://graph.microsoft.com/v1.0/${calendarUser}/events`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      subject: draft.subject,
      body: {
        contentType: 'Text',
        content: buildWilsyCalendarDescription(draft),
      },
      start: {
        dateTime: draft.startDateTime,
        timeZone: draft.timezone,
      },
      end: {
        dateTime: draft.endDateTime,
        timeZone: draft.timezone,
      },
      attendees: draft.participants.map((email) => ({
        emailAddress: {
          address: email,
        },
        type: 'required',
      })),
    }),
  });

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    return {
      connector: 'Microsoft Graph Calendar',
      status: 'CONNECTOR_FAILED',
      statusLabel: 'Microsoft Graph Calendar failed',
      eventLink: null,
      message: payload?.error?.message || 'Microsoft Graph rejected the event creation request.',
    };
  }

  return {
    connector: 'Microsoft Graph Calendar',
    status: 'EVENT_CREATED',
    statusLabel: 'Event created',
    eventId: payload.id,
    eventLink: payload.webLink || null,
    message: 'The meeting has been created in Microsoft Graph Calendar.',
  };
}

/**
 * @function executeWilsyCalendarBridge
 * @description Prepares or executes a calendar event through CRM, Google, or Microsoft calendar connectors.
 * @param {Object} params - Bridge params.
 * @param {Object} params.req - Request object.
 * @param {string} params.question - Operator request.
 * @param {string} params.tenantId - Tenant id.
 * @param {string} params.operatorId - Operator id.
 * @returns {Promise<Object>} Calendar bridge result.
 * @collaboration Wilsy Operator Kernel, Calendar Execution Bridge, connector execution, evidence receipts, and proof harness.
 */
export async function executeWilsyCalendarBridge({
  req = {},
  question = '',
  tenantId = 'MASTER',
  operatorId = 'WILSY_OPERATOR',
} = {}) {
  const draft = buildWilsyCalendarDraft({
    question,
    tenantId,
    operatorId,
    timezone:
      req.query?.timezone ||
      req.body?.timezone ||
      process.env.WILSY_DEFAULT_TIMEZONE ||
      'Africa/Johannesburg',
  });
  const institutionalHeaders = buildWilsyCalendarHeaders({
    tenantId,
    operatorId,
  });
  const approvalGranted = isWilsyCalendarExecutionApproved({ req });
  const connectorPreference = String(
    req.query?.calendarConnector ||
      req.body?.calendarConnector ||
      process.env.WILSY_CALENDAR_CONNECTOR ||
      'crm'
  ).toLowerCase();

  if (!draft.readyForApproval) {
    return {
      tool: 'calendar_execution_bridge',
      label: 'Calendar execution bridge',
      domain: 'meetings',
      status: 'DRAFT_INCOMPLETE',
      statusLabel: 'Draft incomplete',
      mutation: false,
      draft,
      crmCalendarLink: draft.crmCalendarDraftLink,
      eventLink: null,
      missingFields: draft.missingFields,
      connector: 'Approval gate',
      message: `I need ${draft.missingFields.join(', ')} before this meeting can be approved.`,
      institutionalHeaders: {
        ...institutionalHeaders,
        mutation: false,
      },
      strikePayload: {
        institutionalHeaders: {
          ...institutionalHeaders,
          mutation: false,
        },
        commandType: 'CALENDAR_DRAFT_INCOMPLETE',
        mutation: false,
      },
    };
  }

  if (!approvalGranted) {
    return {
      tool: 'calendar_execution_bridge',
      label: 'Calendar execution bridge',
      domain: 'meetings',
      status: 'APPROVAL_REQUIRED',
      statusLabel: 'Approval required',
      mutation: false,
      draft,
      crmCalendarLink: draft.crmCalendarDraftLink,
      eventLink: draft.crmCalendarDraftLink,
      missingFields: [],
      connector: 'Approval gate',
      message:
        'The meeting draft is ready. Calendar booking requires operator approval before any event is created.',
      institutionalHeaders: {
        ...institutionalHeaders,
        mutation: false,
      },
      strikePayload: {
        institutionalHeaders: {
          ...institutionalHeaders,
          mutation: false,
        },
        commandType: 'CALENDAR_DRAFT_READY_FOR_APPROVAL',
        mutation: false,
      },
    };
  }

  let execution;

  if (connectorPreference === 'google') {
    execution = await executeWilsyGoogleCalendarEvent({ draft });
  } else if (connectorPreference === 'microsoft') {
    execution = await executeWilsyMicrosoftCalendarEvent({ draft });
  } else {
    execution = await executeWilsyCrmCalendarEvent({
      draft,
      institutionalHeaders,
    });
  }

  return {
    tool: 'calendar_execution_bridge',
    label: 'Calendar execution bridge',
    domain: 'meetings',
    status: execution.status,
    statusLabel: execution.statusLabel,
    mutation: execution.status === 'EVENT_CREATED',
    draft,
    crmCalendarLink: execution.eventLink || draft.crmCalendarDraftLink,
    eventLink: execution.eventLink,
    missingFields: [],
    connector: execution.connector,
    message: execution.message,
    eventId: execution.eventId,
    institutionalHeaders: {
      ...institutionalHeaders,
      mutation: execution.status === 'EVENT_CREATED',
    },
    strikePayload: {
      institutionalHeaders: {
        ...institutionalHeaders,
        mutation: execution.status === 'EVENT_CREATED',
      },
      commandType:
        execution.status === 'EVENT_CREATED'
          ? 'CALENDAR_EVENT_CREATED'
          : 'CALENDAR_CONNECTOR_NOT_AVAILABLE',
      mutation: execution.status === 'EVENT_CREATED',
    },
  };
}

export default executeWilsyCalendarBridge;
