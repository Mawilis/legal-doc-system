import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useAuth } from '../../contexts/authContext.jsx';
import { useTenants } from '../../contexts/tenantContext.jsx';
import WilsyOSDashboardChrome from './WilsyOSDashboardChrome.jsx';
import {
  completeTenantModuleWorkItem,
  createTenantModuleWorkItem,
  readTenantModuleWorkspace,
} from '../../services/tenantModuleWorkspaceService.js';
import styles from './TenantModuleWorkspace.module.css';

const MODULES = Object.freeze({
  OPERATIONS: Object.freeze({
    label: 'Operations OS',
    subtitle: 'Business processes, operational commitments and execution queues.',
    completionNote: 'Completed by authorised Operations operator',
  }),
  INTELLIGENCE: Object.freeze({
    label: 'Intelligence OS',
    subtitle: 'Analysis work, insight follow-ups and decision-support commitments.',
    completionNote: 'Completed by authorised Intelligence operator',
  }),
});

const formatDue = value => {
  if (!value) return 'No due date';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? 'Date unavailable'
    : date.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
};

function failureMessage(error) {
  const status = error?.response?.status;
  if (status === 401) return 'Your authenticated session is unavailable. Sign in again, then re-enter this workspace.';
  if (status === 403) return 'This module is not currently admitted. Check its active tenant entitlement and your separate module permissions.';
  if (status === 503 || status === 502) return 'The module service or entitlement authority is unavailable. No cached or sample tasks are displayed.';
  return 'EOS did not return a valid module workspace. No local or sample tasks are displayed.';
}

export default function TenantModuleWorkspace({ moduleId }) {
  const config = MODULES[moduleId];
  const { user } = useAuth() || {};
  const { activeTenant } = useTenants() || {};
  const titleInputRef = useRef(null);
  const pendingCreateRef = useRef(null);
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [title, setTitle] = useState('');
  const [kind, setKind] = useState('TASK');
  const [priority, setPriority] = useState('NORMAL');
  const [dueAt, setDueAt] = useState('');
  const [actionMessage, setActionMessage] = useState('');

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const next = await readTenantModuleWorkspace(moduleId);
      setSnapshot(next);
      setError('');
      setActionMessage('Workspace refreshed from current EOS records.');
      return true;
    } catch (failure) {
      setSnapshot(null);
      setError(failureMessage(failure));
      return false;
    } finally {
      setLoading(false);
    }
  }, [moduleId]);

  useEffect(() => { refresh(); }, [refresh]);

  const items = snapshot?.items || [];
  const counts = useMemo(() => ({
    open: items.length,
    today: items.filter(item => item.is_due_today).length,
    overdue: items.filter(item => item.is_overdue).length,
  }), [items]);

  const submit = async event => {
    event.preventDefault();
    if (!title.trim() || saving) return;
    setSaving(true);
    setError('');
    setActionMessage('');
    const command = {
      title: title.trim(),
      description: '',
      kind,
      priority,
      due_at: dueAt ? new Date(dueAt).toISOString() : null,
    };
    const fingerprint = JSON.stringify(command);
    if (!pendingCreateRef.current || pendingCreateRef.current.fingerprint !== fingerprint) {
      const key = window.crypto?.randomUUID?.()
        || `module-work-${Date.now()}-${Math.random().toString(16).slice(2)}`;
      pendingCreateRef.current = { fingerprint, key };
    }
    try {
      await createTenantModuleWorkItem(moduleId, command, pendingCreateRef.current.key);
      pendingCreateRef.current = null;
      setTitle('');
      setDueAt('');
      const refreshed = await refresh();
      setActionMessage(refreshed
        ? 'EOS accepted the action and the queue readback is current.'
        : 'EOS accepted the action, but the queue readback is unavailable. Refresh before retrying.');
    } catch (failure) {
      setError(failureMessage(failure));
    } finally {
      setSaving(false);
    }
  };

  const complete = async item => {
    setSaving(true);
    setError('');
    setActionMessage('');
    try {
      await completeTenantModuleWorkItem(moduleId, item.work_item_id, config.completionNote);
      const refreshed = await refresh();
      setActionMessage(refreshed
        ? 'EOS confirmed completion and the queue readback is current.'
        : 'EOS confirmed completion, but the queue readback is unavailable. Refresh before relying on the view.');
    } catch (failure) {
      setError(failureMessage(failure));
    } finally {
      setSaving(false);
    }
  };

  if (!config) return <main className={styles.workspace}><div role="alert">Unsupported tenant module.</div></main>;

  const tenantIdentity = {
    ...(activeTenant && typeof activeTenant === 'object' ? activeTenant : {}),
    tenantId: snapshot?.tenantId || activeTenant?.tenantId || activeTenant?._id || user?.tenantId || '',
  };

  return (
    <WilsyOSDashboardChrome
      dashboardKey={moduleId === 'OPERATIONS' ? 'operations' : 'intelligence'}
      commandLabel={`WILSY OS ${config.label}`}
      title={config.label}
      role={user?.role || user?.accountRole || 'TENANT_OPERATOR'}
      posture={snapshot ? 'LIVE' : error ? 'SOURCE_GAPS' : 'SOURCE_REQUIRED'}
      storyMessages={[config.subtitle]}
      tenant={tenantIdentity}
      operator={user || {}}
      actions={{
        liveSyncLabel: loading ? 'SYNCING' : 'LIVE SYNC',
        onLiveSync: refresh,
        isRefreshing: loading,
        primaryActionLabel: 'NEW ACTION',
        onPrimaryAction: () => titleInputRef.current?.focus(),
        primaryDisabled: saving,
      }}
      metrics={[]}
    >
    <main className={styles.workspace} aria-label={config.label}>
      <header className={styles.header}>
        <div>
          <span className={styles.eyebrow}>WILSY OS / INDEPENDENT TENANT PRODUCT</span>
          <h1>{config.label}</h1>
          <p>{config.subtitle} This workspace reads only its own active product entitlement and queue.</p>
        </div>
        <button type="button" className={styles.refresh} onClick={refresh} disabled={loading}>Refresh EOS</button>
      </header>

      {error ? <div className={styles.error} role="alert">{error}</div> : null}
      {actionMessage ? <p className={styles.status} role="status" aria-live="polite">{actionMessage}</p> : null}

      <section className={styles.metrics} aria-label="Current module priorities">
        <article className={styles.metric}><span>Open actions</span><strong>{loading ? '—' : snapshot ? counts.open : '—'}</strong></article>
        <article className={styles.metric}><span>Due today</span><strong>{loading ? '—' : snapshot ? counts.today : '—'}</strong></article>
        <article className={styles.metric}><span>Overdue</span><strong>{loading ? '—' : snapshot ? counts.overdue : '—'}</strong></article>
      </section>

      <section className={styles.columns}>
        <section className={styles.panel} aria-labelledby="module-queue-title">
          <div className={styles.sectionHeading}>
            <div><span className={styles.eyebrow}>LIVE EOS SOURCE</span><h2 id="module-queue-title">Work queue</h2></div>
            <span>{loading ? 'Loading' : snapshot ? `${items.length} active` : 'Unavailable'}</span>
          </div>
          {loading ? <p className={styles.empty} role="status">Loading tenant-scoped queue…</p> :
            !snapshot ? <p className={styles.empty}>The queue is unavailable. Retry after the authenticated module service recovers.</p> :
            items.length === 0 ? <div className={styles.empty}><strong>No open actions</strong><p>Create a task or reminder to begin. No sample records are used.</p></div> :
            <ol className={styles.queueList}>
              {items.map(item => (
                <li className={styles.queueItem} key={item.work_item_id}>
                  <div>
                    <div className={styles.itemTitle}><strong>{item.title}</strong><span className={styles.priority}>{item.priority}</span></div>
                    <p className={styles.itemMeta}>{item.kind.replace('_', ' ')} · {item.status.replace('_', ' ')}</p>
                    <small className={styles.due}>{formatDue(item.due_at)}</small>
                  </div>
                  <div className={styles.itemActions}>
                    {item.is_overdue ? <span className={styles.flag}>Overdue</span> : null}
                    {item.is_due_today ? <span className={styles.flag}>Due today</span> : null}
                    <button className={styles.complete} type="button" disabled={saving} onClick={() => complete(item)}>Complete</button>
                  </div>
                </li>
              ))}
            </ol>
          }
        </section>

        <aside className={styles.panel} aria-labelledby="module-create-title">
          <span className={styles.eyebrow}>CAPTURE WORK</span>
          <h2 className={styles.formTitle} id="module-create-title">New action</h2>
          <form className={styles.form} onSubmit={submit}>
            <label className={styles.field}>Action title
              <input ref={titleInputRef} value={title} onChange={event => setTitle(event.target.value)} maxLength={240} required placeholder="Describe the next action" />
            </label>
            <label className={styles.field}>Type
              <select value={kind} onChange={event => setKind(event.target.value)}>
                <option value="TASK">Task</option><option value="REMINDER">Reminder</option><option value="FOLLOW_UP">Follow-up</option>
              </select>
            </label>
            <label className={styles.field}>Priority
              <select value={priority} onChange={event => setPriority(event.target.value)}>
                <option value="CRITICAL">Critical</option><option value="HIGH">High</option><option value="NORMAL">Normal</option><option value="LOW">Low</option>
              </select>
            </label>
            <label className={styles.field}>Due date and time
              <input type="datetime-local" value={dueAt} onChange={event => setDueAt(event.target.value)} />
            </label>
            <button className={styles.submit} type="submit" disabled={saving || !title.trim()}>{saving ? 'Submitting to EOS…' : 'Create action'}</button>
          </form>
          <p className={styles.note}>Commands are checked against this module's own tenant permission and active product entitlement. EOS is the only task lifecycle authority.</p>
        </aside>
      </section>
    </main>
    </WilsyOSDashboardChrome>
  );
}
