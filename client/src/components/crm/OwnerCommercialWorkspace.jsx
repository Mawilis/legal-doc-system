import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  completeOwnerCommercialWorkItem,
  createOwnerCommercialWorkItem,
  readOwnerCommercialWorkspace,
} from '../../services/ownerCommercialWorkspaceService.js';
import styles from './OwnerCommercialWorkspace.module.css';

const formatDue = value => {
  if (!value) return 'No due date';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? 'Date unavailable'
    : date.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
};

export default function OwnerCommercialWorkspace() {
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [title, setTitle] = useState('');
  const [kind, setKind] = useState('TASK');
  const [priority, setPriority] = useState('NORMAL');
  const [dueAt, setDueAt] = useState('');

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const next = await readOwnerCommercialWorkspace();
      setSnapshot(next);
      setError('');
    } catch (failure) {
      setError(
        failure?.response?.status === 403
          ? 'Your tenant does not currently have authorised Legal workspace access.'
          : 'The EOS owner workspace could not be loaded. No local or sample tasks are shown.',
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const items = snapshot?.items || [];
  const counts = useMemo(() => ({
    overdue: items.filter(item => item.is_overdue).length,
    today: items.filter(item => item.is_due_today).length,
    open: items.length,
  }), [items]);

  const submit = async event => {
    event.preventDefault();
    if (!title.trim()) return;
    setSaving(true);
    try {
      await createOwnerCommercialWorkItem({
        title: title.trim(),
        description: '',
        kind,
        priority,
        due_at: dueAt ? new Date(dueAt).toISOString() : null,
        source_type: null,
        source_id: null,
      });
      setTitle('');
      setDueAt('');
      await refresh();
    } catch (failure) {
      setError(
        failure?.response?.status === 403
          ? 'The Legal subscription or work-item authority did not admit this command.'
          : 'EOS rejected the task command. The task was not shown as saved.',
      );
    } finally {
      setSaving(false);
    }
  };

  const complete = async item => {
    try {
      await completeOwnerCommercialWorkItem(item.work_item_id, 'Completed by authorised tenant operator');
      await refresh();
    } catch {
      setError('EOS did not confirm completion. The item remains unresolved.');
    }
  };

  return (
    <main className={styles.workspace} aria-label="Legal Operations owner workspace">
      <header className={styles.header}>
        <div>
          <span className={styles.eyebrow}>WILSY OS / LEGAL OPERATIONS</span>
          <h1>Owner operating workspace</h1>
          <p>Your daily commercial actions, follow-ups and reminders. Legal matter files remain in the separately governed practice workspace.</p>
        </div>
        <button type="button" onClick={refresh} disabled={loading} className={styles.refresh}>Refresh EOS</button>
      </header>

      <section className={styles.metrics} aria-label="Daily priorities">
        <article><span>Open actions</span><strong>{loading ? '—' : counts.open}</strong></article>
        <article><span>Due today</span><strong>{loading ? '—' : counts.today}</strong></article>
        <article><span>Overdue</span><strong>{loading ? '—' : counts.overdue}</strong></article>
      </section>

      {error && <div className={styles.error} role="alert">{error}</div>}

      <section className={styles.columns}>
        <section className={styles.queue}>
          <div className={styles.sectionHeading}>
            <div><span className={styles.eyebrow}>EXECUTION QUEUE</span><h2>Today's priorities</h2></div>
            <span>{loading ? 'Loading' : `${items.length} active`}</span>
          </div>
          {loading ? <p className={styles.empty}>Loading the tenant-scoped EOS queue…</p> :
            !snapshot ? (
              <p className={styles.empty}>The workspace source is unavailable. No task count or empty-state claim can be made until EOS responds.</p>
            ) : items.length === 0 ? (
              <div className={styles.empty}>
                <h3>No open actions</h3>
                <p>Create your first task, reminder or client follow-up. This queue never invents work or displays sample records.</p>
              </div>
            ) : (
              <ol className={styles.items}>
                {items.map(item => (
                  <li key={item.work_item_id} className={styles.item}>
                    <div className={styles.itemMain}>
                      <div className={styles.itemTitle}>
                        <strong>{item.title}</strong>
                        <span data-priority={item.priority}>{item.priority}</span>
                      </div>
                      <p>{item.kind.replace('_', ' ')} · {item.status.replace('_', ' ')}</p>
                      <small>{formatDue(item.due_at)}</small>
                    </div>
                    <div className={styles.itemActions}>
                      {item.is_overdue && <em>Overdue</em>}
                      {item.is_due_today && <em>Due today</em>}
                      <button type="button" onClick={() => complete(item)}>Complete</button>
                    </div>
                  </li>
                ))}
              </ol>
            )
          }
        </section>

        <aside className={styles.createPanel}>
          <span className={styles.eyebrow}>CAPTURE A COMMITMENT</span>
          <h2>New action</h2>
          <form onSubmit={submit}>
            <label>What needs to happen?
              <input value={title} onChange={event => setTitle(event.target.value)} maxLength={240} required placeholder="e.g. Follow up with new client" />
            </label>
            <label>Action type
              <select value={kind} onChange={event => setKind(event.target.value)}>
                <option value="TASK">Task</option>
                <option value="REMINDER">Reminder</option>
                <option value="FOLLOW_UP">Client follow-up</option>
              </select>
            </label>
            <label>Priority
              <select value={priority} onChange={event => setPriority(event.target.value)}>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="NORMAL">Normal</option>
                <option value="LOW">Low</option>
              </select>
            </label>
            <label>Due date and time
              <input type="datetime-local" value={dueAt} onChange={event => setDueAt(event.target.value)} />
            </label>
            <button type="submit" disabled={saving || !title.trim()}>{saving ? 'Saving in EOS…' : 'Create action'}</button>
          </form>
          <p className={styles.note}>Actions are persisted by Python EOS under the authorised tenant and current Legal subscription. Completion is confirmed by EOS, not by the browser.</p>
        </aside>
      </section>
    </main>
  );
}
