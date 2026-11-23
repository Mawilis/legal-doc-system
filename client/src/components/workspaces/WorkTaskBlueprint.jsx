/**
 * TITLE: WILSY OS Reusable Source-Owned Work Row Blueprint
 * VERSION: v1.0.0-CROSS-SURFACE-EXECUTION-ROW
 * AUTHORITY: WILSY OS UI composition; Python EOS retains all task authority.
 * EPITOME: One readable, compact, keyboard-operable task row shell for
 *          Projects, Work Calendar, My Work and Daily Attention.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/WorkTaskBlueprint.jsx
 * COLLABORATION / OWNERSHIP: WILSY OS UI platform and individual EOS work sources.
 * CERTIFICATION / UPDATE DATE: 2026-11-23
 * CHANGELOG: v1.0.0-CROSS-SURFACE-EXECUTION-ROW centralizes accessible
 *          row, title, metadata and action styling without introducing
 *          duplicate business commands or new data ownership.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Presentation-only; no storage, tokens,
 *          session inference, cached business truth or synthetic records.
 * TENANT BOUNDARY: Caller supplies only its currently admitted EOS rows.
 * AUTHORITY BOUNDARY: No mutation, IAM, completion or approval. Buttons
 *          remain wired to the caller's existing source-owned handlers.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';

export const workTaskBlueprint = Object.freeze({
  list: 'overflow-hidden rounded-xl border border-slate-200 bg-white text-slate-950 divide-y divide-slate-200',
  row: 'group min-w-0 border-l-[3px] border-l-transparent bg-white px-3 py-2.5 text-slate-950 transition-colors hover:bg-slate-50',
  selected: 'border-l-blue-700 bg-slate-50',
  title: 'min-w-0 break-words text-left text-sm font-semibold leading-5 text-slate-950 hover:text-blue-800 focus-visible:rounded-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700',
  meta: 'text-xs leading-5 text-slate-600',
  primary: 'inline-flex min-h-9 shrink-0 items-center justify-center gap-1.5 rounded-md border border-amber-600 bg-amber-400 px-3 text-xs font-semibold text-slate-950 hover:bg-amber-300 disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700',
  secondary: 'inline-flex min-h-9 shrink-0 items-center justify-center gap-1.5 rounded-md border border-slate-300 bg-white px-3 text-xs font-semibold text-slate-800 hover:bg-slate-100 disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700',
});

/**
 * @description Renders a visual row without possessing or mutating work state.
 * @param {object} props - Admitted caller-owned row contents and selection.
 * @returns {JSX.Element} Keyboard-compatible native list item.
 * @institutional Financial execution and EOS work commands are out of scope.
 */
export function WorkTaskBlueprintRow({ children, selected = false, className = '', ...rest }) {
  return <article role="listitem"
    className={workTaskBlueprint.row + (selected ? ' ' + workTaskBlueprint.selected : '')
      + (className ? ' ' + className : '')}
    {...rest}>{children}</article>;
}

// ARTIFACT: WorkTaskBlueprint.jsx
// VERSION: v1.0.0-CROSS-SURFACE-EXECUTION-ROW
// AUTHORITY BOUNDARY: Presentation-only; caller-owned EOS action and readback.
// TENANT POSTURE: Only admitted caller-supplied source records.
// FAIL-CLOSED POSTURE: No implied permissions, work state or execution.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
