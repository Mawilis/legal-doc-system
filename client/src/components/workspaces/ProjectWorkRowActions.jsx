/**
 * TITLE: WILSY OS Project Work Row Actions
 * VERSION: v1.0.1-MOBILE-DISMISS-FOCUS-CERT
 * AUTHORITY: UI-only projection of existing exact-project task commands.
 * EPITOME: One next lifecycle action, a keyboard-complete desktop overflow
 *          menu, and a mobile action sheet with guarded destructive cancel.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectWorkRowActions.jsx
 * COLLABORATION / OWNERSHIP: ProjectTasksPanel owns EOS commands, permissions,
 *          selection, immutable readback and completion attestation.
 * CERTIFICATION / UPDATE DATE: 2026-11-19
 * CHANGELOG: v1.0.1-MOBILE-DISMISS-FOCUS-CERT focuses first action without
 *          requiring animation-frame shims and supports touch scrim dismissal.
 * CHANGELOG: v1.0.0-RESPONSIVE-ONE-PRIMARY-ACTION separates core action from
 *          secondary actions and never claims success before EOS readback.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: No browser storage or analytic identity leaks.
 * TENANT BOUNDARY: Caller passes only current exact-project verified work.
 * AUTHORITY BOUNDARY: No new action, role, grant, write or bypass is created.
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution or approval authority.
 */
import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { MoreHorizontal } from 'lucide-react';

const nextAction = {
  TODO: ['Start', 'IN_PROGRESS'],
  IN_PROGRESS: ['Complete', 'DONE'],
  BLOCKED: ['Resume', 'IN_PROGRESS'],
};

export default function ProjectWorkRowActions({
  item, busy, onTransition, onComplete, onEdit, onAttachments, onApprovals, onActivity,
}) {
  const [open, setOpen] = useState(false);
  const [confirmCancel, setConfirmCancel] = useState(false);
  const [anchor, setAnchor] = useState({ top: 100, left: 0 });
  const trigger = useRef(null);
  const panel = useRef(null);
  const primary = nextAction[item.status];
  const canChange = ['TODO', 'IN_PROGRESS', 'BLOCKED'].includes(item.status);
  const close = () => {
    setOpen(false);
    setConfirmCancel(false);
    trigger.current?.focus();
  };
  const act = callback => {
    close();
    callback();
  };

  useEffect(() => {
    if (!open) return undefined;
    const onKeyDown = event => {
      if (event.key === 'Escape') {
        event.preventDefault();
        close();
      }
    };
    window.addEventListener('keydown', onKeyDown);
    panel.current?.querySelector('button')?.focus();
    return () => { window.removeEventListener('keydown', onKeyDown); };
  }, [open]);

  const actions = [
    ...(canChange && item.status !== 'BLOCKED'
      ? [{ id: 'block', name: 'Mark blocked', onClick: () => onTransition(item, 'BLOCKED') }]
      : []),
    ...(canChange
      ? [{ id: 'edit', name: 'Edit / assign', onClick: () => onEdit(item) }]
      : []),
    { id: 'attachments', name: 'Attachments', onClick: () => onAttachments(item) },
    { id: 'activity', name: 'Activity & discussion', onClick: () => onActivity(item) },
    { id: 'approvals', name: 'Approvals', onClick: () => onApprovals(item) },
    ...(canChange ? [{ id: 'cancel', name: 'Cancel work', danger: true,
      onClick: () => setConfirmCancel(true) }] : []),
  ];

  return <>
    <div className="flex flex-wrap items-center gap-1.5">
      {primary && <button type="button" disabled={busy}
        aria-label={primary[0] + ': ' + item.title}
        className="wp-button wp-button-primary !min-h-9 !px-3 !text-xs"
        onClick={() => primary[1] === 'DONE' ? onComplete(item) : onTransition(item, primary[1])}>
        {primary[0]}
      </button>}
      <button type="button" ref={trigger} disabled={busy}
        aria-haspopup="dialog" aria-expanded={open}
        aria-label={'More actions for ' + item.title}
        className="inline-flex min-h-10 min-w-10 items-center justify-center rounded-lg border border-slate-300 text-slate-800 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700"
        onClick={event => {
          const bounds = event.currentTarget.getBoundingClientRect();
          setAnchor({
            top: Math.min(window.innerHeight - 345, bounds.bottom + 5),
            left: Math.min(window.innerWidth - 258, Math.max(8, bounds.right - 240)),
          });
          setOpen(old => !old);
        }}>
        <MoreHorizontal size={18} aria-hidden="true"/>
      </button>
    </div>
    {open && createPortal(
      <div className="fixed inset-0 z-[100] bg-slate-950/40 md:bg-transparent"
        onClick={event => { if (event.target === event.currentTarget) close(); }}>
        <div role="dialog" aria-modal="true" ref={panel}
          aria-label={'Actions for ' + item.title}
          className="absolute inset-x-0 bottom-0 max-h-[80vh] overflow-y-auto rounded-t-2xl bg-white p-3 pb-[max(16px,env(safe-area-inset-bottom))] shadow-2xl md:inset-x-auto md:bottom-auto md:w-60 md:rounded-xl md:border md:border-slate-200"
          style={typeof window === 'undefined' || window.innerWidth < 768
            ? undefined : { top: Math.max(8, anchor.top), left: anchor.left }}
          onKeyDown={event => {
            if (event.key !== 'Tab') return;
            const buttons = [...event.currentTarget.querySelectorAll('button:not([disabled])')];
            if (event.shiftKey && document.activeElement === buttons[0]) {
              event.preventDefault(); buttons[buttons.length - 1]?.focus();
            } else if (!event.shiftKey && document.activeElement === buttons[buttons.length - 1]) {
              event.preventDefault(); buttons[0]?.focus();
            }
          }}>
          <div className="mx-auto mb-2 h-1 w-10 rounded-full bg-slate-300 md:hidden"/>
          <p className="truncate px-3 pb-2 text-sm font-semibold text-slate-950">{item.title}</p>
          {!confirmCancel ? <>
            {actions.map(action => <button key={action.id} type="button"
              className={'block min-h-12 w-full rounded-md px-3 text-left text-sm font-medium hover:bg-slate-100 '
                + (action.danger ? 'text-rose-800' : 'text-slate-900')}
              onClick={() => action.danger ? action.onClick() : act(action.onClick)}>
              {action.name}
            </button>)}
            <button type="button" className="mt-2 min-h-12 w-full rounded-lg bg-slate-100 text-sm font-semibold text-slate-800"
              onClick={close}>Close actions</button>
          </> : <>
            <p className="p-3 text-sm text-slate-800">Cancel this item? EOS will retain its immutable transition history.</p>
            <button type="button" disabled={busy}
              className="min-h-12 w-full rounded-lg bg-rose-50 px-3 text-left text-sm font-semibold text-rose-800"
              onClick={() => act(() => onTransition(item, 'CANCELLED'))}>Confirm cancellation</button>
            <button type="button" className="mt-2 min-h-12 w-full rounded-lg bg-slate-100 text-sm font-semibold text-slate-800"
              onClick={() => setConfirmCancel(false)}>Keep work</button>
          </>}
        </div>
      </div>, document.body)}
  </>;
}

// ARTIFACT: ProjectWorkRowActions.jsx
// VERSION: v1.0.1-MOBILE-DISMISS-FOCUS-CERT
// AUTHORITY BOUNDARY: all commands delegated to already-authorized EOS owner panel
// TENANT POSTURE: no project or principal authority inferred by this surface
// FAIL-CLOSED POSTURE: status gates and source callbacks preserve EOS readback
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS only
// END OF WILSY OS SOVEREIGN ARTIFACT
