/**
 * File: client/src/features/dashboard/components/AuditFeed.jsx
 * Path: client/src/features/dashboard/components/AuditFeed.jsx
 * STATUS: PRODUCTION-READY | FORENSIC LOGGING UI
 * VERSION: 2026-01-14
 *
 * PURPOSE
 * - Chronological feed of system audit logs for administrators.
 * - Forensic-friendly UI: timestamp, severity, action, sanitized details, and optional pagination.
 * - Designed for accessibility (WCAG), privacy (PII redaction), and performance (limited initial render).
 *
 * OWNERSHIP & REVIEW
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @frontend-team
 * - SECURITY OWNER: @security (PII redaction, telemetry)
 * - QA OWNER: @qa (accessibility, contract tests)
 *
 * REVIEW CHECKLIST (PRE-MERGE)
 * - @security: confirm redaction rules and ensure no PII is rendered.
 * - @qa: add RTL + accessibility tests (axe), keyboard navigation tests.
 * - @frontend-team: confirm design tokens and color variants.
 *
 * NOTES
 * - The component expects `logs` to be an array of audit entries with shape:
 *   { _id, timestamp, action, details, severity, actor, tenantId }
 * - The component sanitizes `details` to avoid leaking PII; controllers should already redact sensitive fields.
 * - For very large feeds, callers should implement server-side pagination or streaming and pass `onLoadMore`.
 */

import React, { useMemo, useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { FiList, FiChevronDown, FiCopy, FiExternalLink } from 'react-icons/fi';

/* -------------------------
   Styled primitives
   ------------------------- */

const Container = styled.section`
  background: var(--card-bg, #ffffff);
  border-radius: 12px;
  border: 1px solid var(--card-border, #E2E8F0);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 420px;
  min-height: 160px;
`;

const Header = styled.header`
  padding: 12px 16px;
  border-bottom: 1px solid var(--card-border, #E2E8F0);
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--card-quiet, #F8FAFC);

  h4 {
    margin: 0;
    font-size: 0.95rem;
    color: var(--muted, #475569);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .controls {
    margin-left: auto;
    display: flex;
    gap: 8px;
    align-items: center;
  }

  button {
    background: transparent;
    border: none;
    color: var(--muted, #64748B);
    cursor: pointer;
    padding: 6px;
    border-radius: 8px;
  }
`;

const FeedList = styled.div`
  overflow-y: auto;
  flex: 1;
  padding: 0;
  display: flex;
  flex-direction: column;
`;

const FeedItem = styled.article`
  padding: 12px 16px;
  border-bottom: 1px solid #F1F5F9;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  transition: background 0.12s;
  background: ${(p) => (p.highlight ? 'rgba(37,99,235,0.03)' : 'transparent')};

  &:last-child { border-bottom: none; }
  &:hover { background: #FBFDFF; }

  .time {
    color: var(--muted, #94A3B8);
    font-size: 0.75rem;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "JetBrains Mono", monospace;
    margin-top: 2px;
    min-width: 72px;
    text-align: left;
  }

  .body {
    flex: 1;
    font-size: 0.9rem;
    color: var(--text, #334155);
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .meta {
    display: flex;
    gap: 8px;
    align-items: center;
    color: var(--muted, #64748B);
    font-size: 0.8rem;
  }

  .action {
    font-weight: 700;
    color: var(--text-strong, #0F172A);
  }

  .details {
    color: var(--muted, #475569);
    font-size: 0.9rem;
    word-break: break-word;
    white-space: pre-wrap;
  }

  .severity {
    padding: 4px 8px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
`;

/* Severity color mapping */
const severityMap = {
    INFO: { bg: '#EFF6FF', color: '#2563EB' },
    WARN: { bg: '#FFFBEB', color: '#D97706' },
    ERROR: { bg: '#FEF2F2', color: '#DC2626' },
    CRITICAL: { bg: '#FFF1F2', color: '#B91C1C' },
    DEFAULT: { bg: '#F8FAFC', color: '#64748B' }
};

const EmptyState = styled.div`
  padding: 36px;
  text-align: center;
  color: var(--muted, #94A3B8);
  font-size: 0.9rem;
`;

/* Small utility button */
const SmallButton = styled.button`
  background: transparent;
  border: 1px solid transparent;
  padding: 6px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--muted, #64748B);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  &:hover { background: #F1F5F9; color: #0b3d91; }
`;

/* -------------------------
   Helpers
   ------------------------- */

/**
 * sanitizeDetails
 * - Remove or redact obvious PII patterns (emails, South African ID numbers, phone numbers).
 * - This is a defensive client-side redaction; server must perform authoritative redaction.
 */
function sanitizeDetails(input) {
    if (input == null) return '';
    let s = typeof input === 'string' ? input : JSON.stringify(input);
    // Redact emails
    s = s.replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, '[REDACTED_EMAIL]');
    // Redact phone numbers (simple patterns)
    s = s.replace(/(\+?\d{1,3}[-.\s]?)?(\d{2,4}[-.\s]?){2,4}\d{2,4}/g, (m) => (m.length >= 7 ? '[REDACTED_PHONE]' : m));
    // Redact South African ID-like sequences (simple heuristic)
    s = s.replace(/\b\d{13}\b/g, '[REDACTED_ID]');
    // Truncate very long payloads
    if (s.length > 1000) s = `${s.slice(0, 997)}…`;
    return s;
}

/**
 * formatTime
 * - Returns a short time string and full ISO for tooltip.
 */
function formatTime(ts) {
    const d = ts ? new Date(ts) : new Date();
    const short = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const iso = d.toISOString();
    return { short, iso };
}

/* -------------------------
   Component
   ------------------------- */

export default function AuditFeed({ logs = [], loading = false, limit = 25, onLoadMore = null, autoScroll = false }) {
    const [visible, setVisible] = useState(limit);

    const sliced = useMemo(() => {
        if (!Array.isArray(logs)) return [];
        return logs.slice(0, visible);
    }, [logs, visible]);

    const handleLoadMore = useCallback(() => {
        setVisible((v) => v + limit);
        if (typeof onLoadMore === 'function') onLoadMore();
    }, [limit, onLoadMore]);

    const handleCopy = useCallback((text) => {
        try {
            if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
                navigator.clipboard.writeText(text);
            } else {
                // fallback
                const ta = document.createElement('textarea');
                ta.value = text;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
            }
            // Non-sensitive telemetry hook (caller must ensure no PII)
            try { if (window.WilsyTelemetry && typeof window.WilsyTelemetry.capture === 'function') window.WilsyTelemetry.capture({ event: 'audit.copy' }); } catch { }
        } catch (e) {
            // ignore
        }
    }, []);

    // Auto-scroll to top when logs change if requested
    const listRef = React.useRef(null);
    React.useEffect(() => {
        if (autoScroll && listRef.current) {
            listRef.current.scrollTop = 0;
        }
    }, [logs, autoScroll]);

    return (
        <Container aria-live="polite" aria-atomic="false">
            <Header>
                <FiList color="#64748B" aria-hidden="true" />
                <h4>Recent Activity</h4>

                <div className="controls" role="toolbar" aria-label="Audit controls">
                    <SmallButton
                        title="Export (server-side)"
                        onClick={() => { /* Caller should implement export; do not implement client-side export here */ }}
                        aria-disabled="true"
                    >
                        <FiExternalLink size={14} /> Export
                    </SmallButton>

                    <SmallButton
                        title="Load more"
                        onClick={handleLoadMore}
                        aria-label="Load more audit events"
                    >
                        <FiChevronDown size={14} /> More
                    </SmallButton>
                </div>
            </Header>

            <FeedList ref={listRef}>
                {loading ? (
                    <EmptyState>Loading recent activity…</EmptyState>
                ) : (!sliced || sliced.length === 0) ? (
                    <EmptyState>No recent activity recorded.</EmptyState>
                ) : (
                    sliced.map((log, idx) => {
                        const id = log && (log._id || log.id) ? (log._id || log.id) : `log_${idx}`;
                        const severityKey = (log && log.severity && String(log.severity).toUpperCase()) || 'DEFAULT';
                        const sev = severityMap[severityKey] || severityMap.DEFAULT;
                        const { short, iso } = formatTime(log && log.timestamp ? log.timestamp : Date.now());
                        const details = sanitizeDetails(log && (log.details || log.message || log.meta) ? (log.details || log.message || log.meta) : 'System Event');

                        return (
                            <FeedItem key={id} highlight={severityKey === 'CRITICAL'}>
                                <div className="time" title={iso} aria-hidden="true">{short}</div>

                                <div className="body">
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, justifyContent: 'space-between' }}>
                                        <div>
                                            <div className="action" aria-label={`Action ${log && log.action ? log.action : 'Event'}`}>
                                                {log && log.action ? String(log.action) : 'System Event'}
                                            </div>
                                            <div className="meta" aria-hidden="true">
                                                <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                                                    <span className="severity" style={{ background: sev.bg, color: sev.color }}>{severityKey}</span>
                                                    {log && log.actor && log.actor.userId ? <span>Actor: {String(log.actor.userId)}</span> : null}
                                                    {log && log.tenantId ? <span>Tenant: {String(log.tenantId)}</span> : null}
                                                </span>
                                            </div>
                                        </div>

                                        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                                            <SmallButton aria-label="Copy details" title="Copy details" onClick={() => handleCopy(details)}>
                                                <FiCopy size={14} />
                                            </SmallButton>
                                        </div>
                                    </div>

                                    <div className="details" aria-label="Event details">{details}</div>
                                </div>
                            </FeedItem>
                        );
                    })
                )}
            </FeedList>
        </Container>
    );
}

AuditFeed.propTypes = {
    logs: PropTypes.arrayOf(PropTypes.object),
    loading: PropTypes.bool,
    limit: PropTypes.number,
    onLoadMore: PropTypes.func,
    autoScroll: PropTypes.bool
};

AuditFeed.defaultProps = {
    logs: [],
    loading: false,
    limit: 25,
    onLoadMore: null,
    autoScroll: false
};
