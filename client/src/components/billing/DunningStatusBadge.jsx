/* eslint-disable */
/**
 * WILSY OS - DUNNING STATUS BADGE [V1.0.0-LEDGER-TRUTH]
 * EPITOME: Presents persisted dunning state and retry metadata without inferring collection activity.
 * BIBLICAL ANCHOR: Psalm 1:3 - "And he shall be like a tree planted by the rivers of water..."
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/billing/DunningStatusBadge.jsx
 * COLLABORATION & OWNERSHIP: Wilson Khanyezi (Founder/CEO) mandated truthful collections visibility; AI Engineering (Codex) implemented it.
 */

import React from 'react';

/**
 * @function DunningStatusBadge
 * @description Displays a normalized dunning label from persisted status and retry count.
 * @param {{dunningStatus?:string,retryCount?:number,maxRetries?:number,nextRetryAt?:string}} props - Dunning state.
 * @returns {JSX.Element|null} Dunning badge or null when no state exists.
 * @collaboration Avoids fabricating retries when upstream data is absent.
 */
const DunningStatusBadge = ({ dunningStatus, retryCount = 0, maxRetries = 3, nextRetryAt }) => {
  const status = String(dunningStatus || '').trim().toUpperCase();
  const count = Number(retryCount) || 0;
  if (!status && !count && !nextRetryAt) return null;
  const suspended = status === 'SUSPENDED' || status === 'FAILED' || status === 'ESCALATED';
  const tone = suspended ? { bg: '#7f1d1d', fg: '#fee2e2' } : { bg: '#78350f', fg: '#fef3c7' };
  const label = suspended ? (status === 'SUSPENDED' ? 'Suspended' : status.replace(/_/g, ' ')) : `Retry ${count} of ${maxRetries}`;
  const retryLabel = nextRetryAt ? ` · next ${new Date(nextRetryAt).toLocaleDateString('en-ZA')}` : '';
  return <span title={`Dunning: ${label}${retryLabel}`} style={{ display: 'inline-flex', padding: '3px 7px', borderRadius: 999, background: tone.bg, color: tone.fg, fontSize: '0.56rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</span>;
};

export default DunningStatusBadge;

/** POST-UPDATE TODO: Wire provider retry events once the dunning service exposes a tenant-scoped history endpoint. */
