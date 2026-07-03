/* eslint-disable */
import React from 'react';
import { UploadCloud } from 'lucide-react';
import styles from './WilsyMeetingsWorkspace.module.css';

/**
 * @function WilsyMeetingImportWorkspace
 * @description Renders the full-page Meetings import workflow with ample mapping workspace.
 * @param {Object} props - Component props.
 * @returns {JSX.Element} Meeting import page.
 * @collaboration WilsyMeetingsWorkspace, meeting overview, meeting editor.
 */
export default function WilsyMeetingImportWorkspace({ onBackToOverview, onCreateMeeting }) {
  return (
    <section className={styles.pageSurface} data-wilsy-r91k179e2-view="import">
      <header className={styles.importHeader}>
        <h2>Import Meetings</h2>
        <ol>
          <li data-active="true">Upload</li>
          <li>Actions</li>
          <li>Module mapping</li>
          <li>Field mapping</li>
          <li>Assign</li>
        </ol>
        <nav>
          <button type="button" onClick={onBackToOverview}>Cancel</button>
          <button type="button" onClick={onCreateMeeting}>Create manually</button>
        </nav>
      </header>

      <div className={styles.importBody}>
        <section className={styles.dropzone}>
          <UploadCloud size={48} />
          <strong>Drag and drop files here</strong>
          <span>or</span>
          <button type="button">Browse Files</button>
          <p>Supported file formats are XLSX, CSV and XLS. Rows are not committed until backend import authority confirms the operation.</p>
        </section>

        <aside className={styles.importNotice}>
          <p>File can be a max of 5 MB.</p>
          <p>Import authority must remain tenant-scoped and source-honest.</p>
          <p>You cannot upload more than 1 file in this workflow.</p>
        </aside>
      </div>
    </section>
  );
}
