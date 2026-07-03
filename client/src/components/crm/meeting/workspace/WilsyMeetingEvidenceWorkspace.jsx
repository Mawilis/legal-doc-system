/* eslint-disable */
import React from 'react';
import styles from './WilsyMeetingsWorkspace.module.css';

/**
 * @function WilsyMeetingEvidenceWorkspace
 * @description Renders the Meetings evidence ledger as a full-page CRM proof workspace.
 * @param {Object} props - Component props.
 * @returns {JSX.Element} Meeting evidence page.
 * @collaboration WilsyMeetingsWorkspace, CRM proof posture, meeting command receipts.
 */
export default function WilsyMeetingEvidenceWorkspace({ onBackToOverview, onCreateMeeting, onImportMeetings }) {
  const rows = [
    ['Source route', '/api/crm/live/meetings', 'Meeting evidence must include source object, actor, tenant, timestamp and route proof.'],
    ['Invitation proof', 'Pending participants', 'Participant invitations need explicit contacts, users, leads or email addresses.'],
    ['Venue proof', 'Client location', 'Location and venue remain visible before the meeting is saved.'],
    ['Import proof', 'No file selected', 'Import preview is source-honest until backend import authority confirms rows and receipts.'],
    ['Command posture', 'READY', 'Backend command authority can be tested after the workspace contract is stable.'],
  ];

  return (
    <section className={styles.pageSurface} data-wilsy-r91k179e2-view="evidence">
      <header className={styles.workHeader}>
        <div>
          <small>Evidence Workspace</small>
          <h2>Prove Meeting Operations</h2>
          <p>One ledger surface for source route, invitation proof, venue proof, import proof, command posture and receipts.</p>
        </div>
        <nav>
          <button type="button" onClick={onBackToOverview}>Back to overview</button>
          <button type="button" onClick={onCreateMeeting}>Create meeting</button>
          <button type="button" onClick={onImportMeetings}>Import</button>
        </nav>
      </header>

      <div className={styles.ledger}>
        {rows.map(([label, value, detail]) => (
          <article key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
            <p>{detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
