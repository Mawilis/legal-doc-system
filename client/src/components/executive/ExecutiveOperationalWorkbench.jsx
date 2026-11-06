import React, { useMemo, useState } from 'react';
import { AlertTriangle, ArrowUpRight, Clock3, Eye, RefreshCw, ShieldAlert } from 'lucide-react';
import {
  buildDecisionExceptions,
  buildOperationalQueue,
  getOperationalRecordFields
} from '../../services/executiveOperationalQueue';
import styles from './ExecutiveOperationalWorkbench.module.css';

const isStale = (lastSync) => {
  if (!lastSync) return true;
  const timestamp = new Date(lastSync).getTime();
  return !Number.isFinite(timestamp) || Date.now() - timestamp > 15 * 60 * 1000;
};

export default function ExecutiveOperationalWorkbench({ sources = [], onOpenFunction }) {
  const [selectedId, setSelectedId] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [page, setPage] = useState(0);
  const queue = useMemo(() => buildOperationalQueue(sources), [sources]);
  const exceptions = useMemo(() => buildDecisionExceptions(queue), [queue]);
  const statuses = useMemo(() => Array.from(new Set(queue.map((item) => item.status))).sort(), [queue]);
  const filteredQueue = useMemo(() => {
    const needle = searchTerm.trim().toLowerCase();
    return queue.filter((item) => {
      const matchesStatus = statusFilter === 'ALL' || item.status === statusFilter;
      const searchable = [item.title, item.sourceLabel, item.owner, item.recordId, item.status].join(' ').toLowerCase();
      return matchesStatus && (!needle || searchable.includes(needle));
    });
  }, [queue, searchTerm, statusFilter]);
  const pageSize = 12;
  const pageCount = Math.max(1, Math.ceil(filteredQueue.length / pageSize));
  const visibleQueue = filteredQueue.slice(page * pageSize, (page + 1) * pageSize);
  const selected = filteredQueue.find((item) => item.id === selectedId) || filteredQueue[0] || null;
  const selectedSource = selected
    ? sources.find((source) => source.key === selected.sourceKey)
    : null;
  const fields = selected ? getOperationalRecordFields(selected.record) : [];
  const unavailable = sources.filter((source) => !source.live);
  const stale = sources.filter((source) => source.live && isStale(source.lastSync));

  return (
    <section className={styles.workbench} aria-label="Executive operational workbench">
      <header className={styles.heading}>
        <div>
          <span>LIVE OPERATIONS</span>
          <h2>Work requiring executive attention</h2>
          <p>Only actionable records returned by connected tenant systems appear here.</p>
        </div>
        <div className={styles.freshness} aria-live="polite">
          <span><RefreshCw size={13} /> {sources.filter((source) => source.live).length}/{sources.length} sources responding</span>
          {stale.length > 0 && <small><Clock3 size={12} /> {stale.length} source(s) may be stale</small>}
          {unavailable.length > 0 && <small><AlertTriangle size={12} /> {unavailable.length} source(s) unavailable</small>}
        </div>
      </header>

      <div className={styles.columns}>
        <section className={styles.queuePanel} aria-labelledby="executive-queue-title">
          <header>
            <div><span>OPERATIONAL QUEUE</span><h3 id="executive-queue-title">Open work</h3></div>
            <strong>{filteredQueue.length} / {queue.length}</strong>
          </header>
          <div className={styles.queueControls}>
            <input
              type="search"
              aria-label="Search operational work"
              placeholder="Search work, owner or reference"
              value={searchTerm}
              onChange={(event) => { setSearchTerm(event.target.value); setPage(0); }}
            />
            <select
              aria-label="Filter operational work by status"
              value={statusFilter}
              onChange={(event) => { setStatusFilter(event.target.value); setPage(0); }}
            >
              <option value="ALL">All actionable statuses</option>
              {statuses.map((status) => <option key={status} value={status}>{status.replace(/_/g, ' ')}</option>)}
            </select>
          </div>
          {visibleQueue.length ? (
            <ul className={styles.queueList}>
              {visibleQueue.map((item) => (
                <li key={item.id}>
                  <button
                    type="button"
                    className={selected?.id === item.id ? styles.selectedRow : styles.queueRow}
                    onClick={() => setSelectedId(item.id)}
                    aria-pressed={selected?.id === item.id}
                  >
                    <span className={styles.rowMeta}>
                      <span>{item.sourceLabel}</span>
                      <span data-state={item.status}>{item.status.replace(/_/g, ' ')}</span>
                    </span>
                    <strong>{item.title}</strong>
                    <small>{item.owner || 'Owner not supplied'}{item.dueAt ? ` · Due ${item.dueAt}` : ''}</small>
                    <span className={styles.inspect}><Eye size={12} /> Inspect record</span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className={styles.empty}>
              <strong>{queue.length ? 'No records match these filters' : 'No actionable records returned'}</strong>
              <p>{queue.length ? 'Change the search or status filter to broaden the current view.' : 'This is not a zero-work assertion. Check source availability and freshness before concluding the queue is clear.'}</p>
            </div>
          )}
          {filteredQueue.length > pageSize && (
            <footer className={styles.pagination}>
              <button type="button" onClick={() => setPage((value) => Math.max(0, value - 1))} disabled={page === 0}>Previous</button>
              <span>Page {page + 1} of {pageCount}</span>
              <button type="button" onClick={() => setPage((value) => Math.min(pageCount - 1, value + 1))} disabled={page >= pageCount - 1}>Next</button>
            </footer>
          )}
        </section>

        <section className={styles.exceptionPanel} aria-labelledby="executive-exceptions-title">
          <header>
            <div><span>DECISION EXCEPTIONS</span><h3 id="executive-exceptions-title">Needs judgement</h3></div>
            <strong>{exceptions.length}</strong>
          </header>
          {exceptions.length ? (
            <ul className={styles.exceptionList}>
              {exceptions.map((item) => (
                <li key={item.id}>
                  <button type="button" onClick={() => { setSearchTerm(''); setStatusFilter('ALL'); setPage(0); setSelectedId(item.id); }}>
                    <ShieldAlert size={14} />
                    <span><strong>{item.title}</strong><small>{item.sourceLabel} · {item.status.replace(/_/g, ' ')}</small></span>
                    <ArrowUpRight size={13} />
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className={styles.emptyCompact}>No decision exceptions were identified in the currently available actionable records.</div>
          )}
        </section>

        <aside className={styles.inspector} aria-labelledby="executive-inspector-title">
          <header>
            <span>RECORD INSPECTOR</span>
            <h3 id="executive-inspector-title">{selected ? selected.title : 'Select a record'}</h3>
          </header>
          {selected ? (
            <>
              <div className={styles.inspectorState} data-state={selected.status}>
                {selected.status.replace(/_/g, ' ')} · {selected.priority}
              </div>
              <dl>
                {fields.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}
              </dl>
              <div className={styles.sourceProof}>
                <span>Source: {selected.sourceLabel}</span>
                <span>{selectedSource?.live ? 'Connected' : 'Unavailable'} · {selectedSource?.status || selected.sourceStatus}</span>
                <small>Last read: {selected.lastSync ? new Date(selected.lastSync).toLocaleString() : 'Not available'}</small>
              </div>
              <button
                type="button"
                className={styles.openButton}
                onClick={() => onOpenFunction?.(selectedSource)}
                disabled={!selectedSource?.functionKey}
              >
                Open owning workspace <ArrowUpRight size={14} />
              </button>
            </>
          ) : (
            <div className={styles.empty}>
              <Eye size={18} />
              <p>Choose a live operational record to inspect its source, owner, status and available routing.</p>
            </div>
          )}
        </aside>
      </div>
    </section>
  );
}
