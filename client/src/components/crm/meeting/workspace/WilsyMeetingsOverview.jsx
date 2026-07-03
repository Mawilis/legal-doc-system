/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM MEETINGS OVERVIEW                                                                                      ║
 * ║ LIST-FIRST WORK QUEUE | READINESS SIGNALS | ROW ACTIONS | BULK SELECTION | SOURCE-HONEST EMPTY STATE                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/crm/meeting/workspace/WilsyMeetingsOverview.jsx ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION                                                                                                          ║
 * ║ 1. Wilson Khanyezi - Mandated the Meetings module become usable CRM workspace, not a cramped demo panel.               ║
 * ║ 2. AI Engineering - Reframed the overview as a dense meeting work queue with clear row actions and readiness proof.   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview List-first Meetings overview for Wilsy OS CRM.
 */

import React, { useEffect, useMemo, useState } from 'react';
import { CalendarDays, Edit3, Eye, Fingerprint, Plus, RefreshCcw, Trash2, UploadCloud } from 'lucide-react';
import styles from './WilsyMeetingsWorkspace.module.css';

const WILSY_MEETING_PAGE_SIZE_OPTIONS = Object.freeze([10, 20, 50]);

/**
 * @function normalizeWilsyMeetingRecords
 * @description Normalizes overview record props into a source-honest array.
 * @param {Object} props - Overview props.
 * @returns {Array<Object>} Meeting records.
 * @collaboration WilsyMeetingsWorkspace, CRMMeeting live route, list-first work queue.
 */
function normalizeWilsyMeetingRecords(props = {}) {
  const candidates = [props.records, props.visibleMeetings, props.meetings, props.items, props.data];
  return candidates.find((candidate) => Array.isArray(candidate)) || [];
}

/**
 * @function resolveWilsyMeetingRecordId
 * @description Resolves a stable id for a Meeting row.
 * @param {Object} meeting - Meeting record.
 * @param {number} index - Row index fallback.
 * @returns {string} Meeting row id.
 * @collaboration Row keys, row actions, selection and command evidence.
 */
function resolveWilsyMeetingRecordId(meeting = {}, index = 0) {
  return String(
    meeting.recordId ||
      meeting.meetingId ||
      meeting.id ||
      meeting._id ||
      meeting.sourceRecordId ||
      `meeting-${index}`
  ).trim();
}

/**
 * @function resolveWilsyMeetingTitle
 * @description Resolves a Meeting title from persisted fields only.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Meeting title.
 * @collaboration Work queue title column, capsule action, editor launch.
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
 * @function resolveWilsyMeetingParticipants
 * @description Resolves participants from supported Meeting record fields.
 * @param {Object} meeting - Meeting record.
 * @returns {Array} Participant records.
 * @collaboration Participant count, readiness score, source-honest row display.
 */
function resolveWilsyMeetingParticipants(meeting = {}) {
  if (Array.isArray(meeting.participants)) return meeting.participants;
  if (Array.isArray(meeting.attendees)) return meeting.attendees;
  if (Array.isArray(meeting.invitees)) return meeting.invitees;
  return [];
}

/**
 * @function resolveWilsyMeetingVenue
 * @description Resolves a venue label without inventing missing location data.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Venue label.
 * @collaboration Venue repair signals, Meeting editor, row readiness.
 */
function resolveWilsyMeetingVenue(meeting = {}) {
  return String(
    meeting.meetingVenue ||
      meeting.venue ||
      meeting.venueType ||
      meeting.meetingVenueLabel ||
      meeting.locationType ||
      meeting.location ||
      meeting.meetingUrl ||
      meeting.onlineMeetingUrl ||
      ''
  ).trim();
}

/**
 * @function resolveWilsyMeetingRelatedRecord
 * @description Resolves related CRM context from persisted Meeting fields.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Related CRM label.
 * @collaboration Account/contact/deal binding, readiness signal, Meeting capsule.
 */
function resolveWilsyMeetingRelatedRecord(meeting = {}) {
  const related = meeting.relatedRecord || meeting.relatedTo || meeting.crmRecord || meeting.crmLink || '';

  if (!related) {
    return String(
      meeting.relatedRecordName ||
        meeting.relatedRecordId ||
        meeting.relatedLeadId ||
        meeting.relatedContactId ||
        meeting.relatedAccountId ||
        meeting.relatedDealId ||
        ''
    ).trim();
  }

  if (typeof related === 'string') return related.trim();

  return String(related.title || related.name || related.label || related.recordId || related.id || '').trim();
}

/**
 * @function resolveWilsyMeetingStatus
 * @description Resolves a Meeting status label.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Status label.
 * @collaboration Status chip, live route posture, records queue.
 */
function resolveWilsyMeetingStatus(meeting = {}) {
  return String(meeting.status || meeting.stage || meeting.outcome || meeting.persistenceStatus || 'RECORDED').toUpperCase();
}

/**
 * @function resolveWilsyMeetingDate
 * @description Resolves the most useful schedule value from a Meeting record.
 * @param {Object} meeting - Meeting record.
 * @returns {Date|null} Parsed date or null.
 * @collaboration Schedule column, readiness score, calendar scan.
 */
function resolveWilsyMeetingDate(meeting = {}) {
  const value = meeting.startsAt || meeting.startAt || meeting.startTime || meeting.scheduledAt || meeting.date || meeting.fromDate || meeting.createdAt;
  if (!value) return null;

  const parsed = new Date(value);
  return Number.isNaN(parsed.valueOf()) ? null : parsed;
}

/**
 * @function formatWilsyMeetingTime
 * @description Formats Meeting schedule data for compact row scanning.
 * @param {Object} meeting - Meeting record.
 * @returns {string} Schedule label.
 * @collaboration Meeting work queue, calendar posture, operator scanning.
 */
function formatWilsyMeetingTime(meeting = {}) {
  const parsed = resolveWilsyMeetingDate(meeting);
  if (!parsed) {
    const date = [meeting.fromDate, meeting.fromTime].filter(Boolean).join(' ');
    return date || 'Not scheduled';
  }

  return parsed.toLocaleString(undefined, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * @function resolveWilsyMeetingReadiness
 * @description Computes a completion score from real captured Meeting fields.
 * @param {Object} meeting - Meeting record.
 * @returns {Object} Readiness score and gap labels.
 * @collaboration Readiness column, repair prioritization, no-fake-data posture.
 */
function resolveWilsyMeetingReadiness(meeting = {}) {
  const venue = resolveWilsyMeetingVenue(meeting);
  const related = resolveWilsyMeetingRelatedRecord(meeting);
  const participants = resolveWilsyMeetingParticipants(meeting);
  const hasSchedule = Boolean(resolveWilsyMeetingDate(meeting) || meeting.fromDate);
  const hasAgenda = Boolean(meeting.description || meeting.agenda);

  const gaps = [
    venue ? '' : 'venue',
    related ? '' : 'CRM link',
    participants.length > 0 ? '' : 'participants',
    hasSchedule ? '' : 'schedule',
    hasAgenda ? '' : 'agenda',
  ].filter(Boolean);

  return {
    score: Math.max(0, 100 - gaps.length * 18),
    gaps,
    venue,
    related,
    participants,
  };
}

/**
 * @function dispatchWilsyMeetingAction
 * @description Invokes a row handler only when the parent supplied it.
 * @param {Function} handler - Candidate handler.
 * @param {*} payload - Handler payload.
 * @returns {void}
 * @collaboration Row action safety, source-honest UI, command routing.
 */
function dispatchWilsyMeetingAction(handler, payload) {
  if (typeof handler === 'function') {
    handler(payload);
  }
}

/**
 * @function buildWilsyMeetingPaginationModel
 * @description Builds a bounded Meeting records pagination model for the overview footer.
 * @param {Object} input - Pagination input.
 * @returns {Object} Pagination model.
 * @collaboration Meetings work queue, records footer, scalable CRM pagination.
 */
function buildWilsyMeetingPaginationModel({
  totalRecords = 0,
  currentPage = 1,
  pageSize = 20,
} = {}) {
  const safePageSize = WILSY_MEETING_PAGE_SIZE_OPTIONS.includes(Number(pageSize)) ? Number(pageSize) : 20;
  const totalPages = Math.max(1, Math.ceil(Number(totalRecords || 0) / safePageSize));
  const normalizedPage = Math.min(Math.max(1, Number(currentPage || 1)), totalPages);
  const startIndex = totalRecords ? (normalizedPage - 1) * safePageSize : 0;
  const endIndex = totalRecords ? Math.min(startIndex + safePageSize, totalRecords) : 0;
  const pageItems = totalPages <= 5
    ? Array.from({ length: totalPages }, (_, index) => index + 1)
    : normalizedPage <= 3
      ? [1, 2, 3, 'ellipsis-end', totalPages]
      : normalizedPage >= totalPages - 2
        ? [1, 'ellipsis-start', totalPages - 2, totalPages - 1, totalPages]
        : [1, 'ellipsis-start', normalizedPage - 1, normalizedPage, normalizedPage + 1, 'ellipsis-end', totalPages];

  return {
    currentPage: normalizedPage,
    pageSize: safePageSize,
    totalPages,
    startIndex,
    endIndex,
    startRecord: totalRecords ? startIndex + 1 : 0,
    endRecord: endIndex,
    pageItems,
  };
}

/**
 * @function WilsyMeetingsOverview
 * @description Renders a dense Meetings work queue with selection, readiness, row actions and source-honest empty states.
 * @param {Object} props - Overview props.
 * @returns {JSX.Element} Meetings overview.
 * @collaboration WilsyMeetingsWorkspace, CRM live meetings route, Meeting editor, evidence and delete commands.
 */
export default function WilsyMeetingsOverview(props = {}) {
  const records = normalizeWilsyMeetingRecords(props);
  const allRecords = Array.isArray(props.allRecords) ? props.allRecords : records;
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const selectedIds = Array.isArray(props.selectedIds)
    ? props.selectedIds
    : Array.isArray(props.selectedMeetingIds)
      ? props.selectedMeetingIds
      : [];
  const loading = Boolean(props.loading || props.meetingsLoading);
  const error = props.error || props.meetingsError || '';
  const searchTerm = String(props.searchTerm || '').trim();
  const pagination = useMemo(
    () => buildWilsyMeetingPaginationModel({
      totalRecords: records.length,
      currentPage,
      pageSize,
    }),
    [currentPage, pageSize, records.length]
  );
  const paginatedRecords = useMemo(
    () => records.slice(pagination.startIndex, pagination.endIndex),
    [records, pagination.startIndex, pagination.endIndex]
  );

  const visibleIds = useMemo(
    () => paginatedRecords.map(resolveWilsyMeetingRecordId).filter(Boolean),
    [paginatedRecords]
  );
  const allVisibleSelected = visibleIds.length > 0 && visibleIds.every((id) => selectedIds.includes(id));
  const readyCount = records.filter((meeting) => resolveWilsyMeetingReadiness(meeting).score >= 70).length;
  const gapCount = Math.max(0, records.length - readyCount);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, records.length, pageSize]);

  /**
   * @function handleWilsyMeetingPageChange
   * @description Moves the Meeting records footer to a valid page.
   * @param {number} page - Requested page.
   * @returns {void}
   * @collaboration Meetings overview footer, row selection, paged CRM records.
   */
  function handleWilsyMeetingPageChange(page) {
    setCurrentPage(Math.min(Math.max(1, Number(page || 1)), pagination.totalPages));
  }

  /**
   * @function handleWilsyMeetingPageSizeChange
   * @description Updates Meeting records page size and returns to page one.
   * @param {string|number} value - Requested page size.
   * @returns {void}
   * @collaboration Meetings overview footer, record-density controls, CRM list scaling.
   */
  function handleWilsyMeetingPageSizeChange(value) {
    const nextSize = WILSY_MEETING_PAGE_SIZE_OPTIONS.includes(Number(value)) ? Number(value) : 20;
    setPageSize(nextSize);
    setCurrentPage(1);
  }

  /**
   * @function renderWilsyMeetingPaginationControls
   * @description Renders reusable Meeting pagination controls for the visible utility strip and pinned footer.
   * @param {string} surface - Pagination surface id.
   * @returns {JSX.Element} Pagination controls.
   * @collaboration Meetings overview footer, utility strip, Leads-style page navigation.
   */
  function renderWilsyMeetingPaginationControls(surface = 'footer') {
    const utilitySurface = surface === 'utility';

    return (
      <nav
        className={`${styles.meetingFooterPagination} ${utilitySurface ? styles.meetingUtilityPagination : ''}`}
        aria-label={utilitySurface ? 'Meeting records quick pagination' : 'Meeting records pagination'}
      >
        <button type="button" disabled={pagination.currentPage <= 1} aria-label="First page" onClick={() => handleWilsyMeetingPageChange(1)}>|&lt;</button>
        <button type="button" disabled={pagination.currentPage <= 1} aria-label="Previous page" onClick={() => handleWilsyMeetingPageChange(pagination.currentPage - 1)}>&lt;</button>
        {pagination.pageItems.map((item) => (
          typeof item === 'number' ? (
            <button
              key={`${surface}-${item}`}
              type="button"
              aria-current={item === pagination.currentPage ? 'page' : undefined}
              onClick={() => handleWilsyMeetingPageChange(item)}
            >
              {item}
            </button>
          ) : (
            <span key={`${surface}-${item}`} data-wilsy-pagination-ellipsis="true">...</span>
          )
        ))}
        <button type="button" disabled={pagination.currentPage >= pagination.totalPages} aria-label="Next page" onClick={() => handleWilsyMeetingPageChange(pagination.currentPage + 1)}>&gt;</button>
        <button type="button" disabled={pagination.currentPage >= pagination.totalPages} aria-label="Last page" onClick={() => handleWilsyMeetingPageChange(pagination.totalPages)}>&gt;|</button>
        {!utilitySurface ? (
          <label className={styles.meetingFooterPageSize}>
            <select
              value={pagination.pageSize}
              onChange={(event) => handleWilsyMeetingPageSizeChange(event.target.value)}
              aria-label="Meeting records per page"
            >
              {WILSY_MEETING_PAGE_SIZE_OPTIONS.map((option) => (
                <option key={option} value={option}>{option} / page</option>
              ))}
            </select>
          </label>
        ) : null}
      </nav>
    );
  }

  return (
    <section className={styles.meetingsOverview} aria-label="Meetings records work queue">
      <header className={styles.overviewHeader}>
        <div>
          <small>Live Meetings</small>
          <h2>Meeting Work Queue</h2>
          <p>
            {records.length} visible · {allRecords.length} total · {readyCount} ready · {gapCount} need attention
            {searchTerm ? ` · Filter: ${searchTerm}` : ''}
          </p>
        </div>

        <nav>
          <button type="button" onClick={() => dispatchWilsyMeetingAction(props.onRefreshMeetings)}>
            <RefreshCcw size={16} />Sync
          </button>
          <button type="button" onClick={() => dispatchWilsyMeetingAction(props.onCreateMeeting)}>
            <Plus size={16} />Create
          </button>
          <button type="button" onClick={() => dispatchWilsyMeetingAction(props.onImportMeetings)}>
            <UploadCloud size={16} />Import
          </button>
          <button type="button" onClick={() => dispatchWilsyMeetingAction(props.onOpenEvidence)}>
            <Fingerprint size={16} />Evidence
          </button>
          <button type="button" onClick={() => dispatchWilsyMeetingAction(props.onBulkDeleteRequested)} disabled={selectedIds.length === 0}>
            <Trash2 size={16} />Delete selected
          </button>
        </nav>
      </header>

      {error ? (
        <div className={styles.recordsNotice} data-status="error" role="status">
          <strong>LIVE ROUTE</strong>
          <span>{String(error)}</span>
        </div>
      ) : null}

      <div className={styles.recordsUtilityBar}>
        <label className={styles.selectAllControl}>
          <input
            type="checkbox"
            checked={allVisibleSelected}
            onChange={() => dispatchWilsyMeetingAction(props.onToggleAllMeetings, paginatedRecords)}
            disabled={paginatedRecords.length === 0}
          />
          <span>{selectedIds.length} selected</span>
        </label>
        <div className={styles.meetingUtilityPager}>
          <strong>{loading ? 'Syncing live records' : `Page ${pagination.currentPage} of ${pagination.totalPages}`}</strong>
          {renderWilsyMeetingPaginationControls('utility')}
        </div>
      </div>

      <div className={styles.meetingTableShell}>
        <div className={styles.meetingTable} role="table" aria-label="CRM Meetings">
          <div className={styles.meetingTableHead} role="row">
            <span role="columnheader">Meeting</span>
            <span role="columnheader">When</span>
            <span role="columnheader">CRM Link</span>
            <span role="columnheader">Venue</span>
            <span role="columnheader">Readiness</span>
            <span role="columnheader">Actions</span>
          </div>

          <div className={styles.meetingTableBody}>
            {records.length > 0 ? paginatedRecords.map((meeting = {}, index) => {
              const recordId = resolveWilsyMeetingRecordId(meeting, pagination.startIndex + index);
              const selected = selectedIds.includes(recordId);
              const readiness = resolveWilsyMeetingReadiness(meeting);
              const status = resolveWilsyMeetingStatus(meeting);

              return (
                <article className={styles.meetingTableRow} role="row" key={recordId} data-selected={selected ? 'true' : 'false'}>
                  <div className={styles.meetingTitleCell} role="cell">
                    <input
                      type="checkbox"
                      checked={selected}
                      onChange={() => dispatchWilsyMeetingAction(props.onToggleMeetingSelection, meeting)}
                      aria-label={`Select ${resolveWilsyMeetingTitle(meeting)}`}
                    />
                    <div>
                      <strong>{resolveWilsyMeetingTitle(meeting)}</strong>
                      <small>{recordId}</small>
                      <em>{status}</em>
                    </div>
                  </div>

                  <div role="cell">
                    <CalendarDays size={16} />
                    <span>{formatWilsyMeetingTime(meeting)}</span>
                  </div>

                  <div role="cell">
                    <span>{readiness.related || 'Link pending'}</span>
                  </div>

                  <div role="cell">
                    <span>{readiness.venue || 'Venue missing'}</span>
                  </div>

                  <div className={styles.readinessCell} role="cell" data-readiness={readiness.score >= 70 ? 'ready' : 'gap'}>
                    <strong>{readiness.score}%</strong>
                    <span>{readiness.gaps.length ? readiness.gaps.join(', ') : 'Complete'}</span>
                  </div>

                  <nav className={styles.rowActions} role="cell" aria-label={`Actions for ${resolveWilsyMeetingTitle(meeting)}`}>
                    <button type="button" onClick={() => dispatchWilsyMeetingAction(props.onOpenMeeting, meeting)}>
                      <Eye size={15} />Open
                    </button>
                    <button type="button" onClick={() => dispatchWilsyMeetingAction(props.onEditMeeting, meeting)}>
                      <Edit3 size={15} />Edit
                    </button>
                    <button type="button" onClick={() => dispatchWilsyMeetingAction(props.onOpenEvidence, meeting)}>
                      <Fingerprint size={15} />Proof
                    </button>
                    <button type="button" onClick={() => dispatchWilsyMeetingAction(props.onDeleteMeeting, meeting)}>
                      <Trash2 size={15} />Delete
                    </button>
                  </nav>
                </article>
              );
            }) : (
              <section className={styles.meetingsEmptyState} role="row">
                <CalendarDays size={36} />
                <strong>No meeting records found</strong>
                <p>The live Meetings route returned no rows for this filter. Create a meeting or import a schedule when backend import authority is ready.</p>
                <div>
                  <button type="button" onClick={() => dispatchWilsyMeetingAction(props.onCreateMeeting)}>Create meeting</button>
                  <button type="button" onClick={() => dispatchWilsyMeetingAction(props.onImportMeetings)}>Import meetings</button>
                </div>
              </section>
            )}
          </div>
        </div>
      </div>

      <footer className={styles.meetingRecordsFooter} data-wilsy-meetings-footer="LIVE_BACKEND_RECORDS_FOOTER">
        <span className={styles.meetingFooterRecordRange}>
          <strong>{records.length ? `Showing ${pagination.startRecord} to ${pagination.endRecord} of ${records.length} meetings` : 'Showing 0 live meetings'}</strong>
          <em>{selectedIds.length ? `${selectedIds.length} selected` : 'Live backend rows only'}</em>
        </span>
        {renderWilsyMeetingPaginationControls('footer')}
      </footer>
    </section>
  );
}
