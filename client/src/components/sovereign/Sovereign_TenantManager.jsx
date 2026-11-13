/**
 * TITLE: WILSY OS Authenticated Tenant Workspace
 * VERSION: v58.0.0-PYTHON-EOS-C2-DENY-BOUNDARY
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Shows only the authenticated workspace projection while cross-tenant
 *          tenant listing and lifecycle commands remain outside governed C2.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/Sovereign_TenantManager.jsx
 * COLLABORATION / OWNERSHIP: App.jsx mounts this view at /tms; TenantProvider
 *                            receives the Python EOS workspace-bootstrap projection.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG:
 *   v58.0.0-PYTHON-EOS-C2-DENY-BOUNDARY removes calls to global tenant listing,
 *     provisioning and suspension endpoints; exposes only the authenticated
 *     current-tenant projection and an explicit C2 availability state.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No tenant directory query, browser-created tenant,
 *                             or caller-selected tenant authority is used.
 * TENANT BOUNDARY: The displayed record is TenantProvider's current authenticated
 *                  workspace projection. No cross-tenant read or mutation occurs.
 * AUTHORITY BOUNDARY: Frontend visibility grants no lifecycle authority. Python
 *                     EOS remains deny-by-default outside governed C2.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for execution
 *                               and settlement truth.
 */

import React, { useCallback, useMemo, useState } from 'react';
import { AlertTriangle, Check, Copy, Database, ShieldCheck } from 'lucide-react';
import { useTenants } from '../../contexts/tenantContext';
import styles from './Sovereign_TenantManager.module.css';

const displayValue = (value) => (
  typeof value === 'string' && value.trim() ? value.trim() : 'Not provided by workspace bootstrap'
);

const tenantIdentifier = (tenant) => String(
  tenant?.tenant_id || tenant?.tenantId || tenant?.id || tenant?._id || '',
).trim();

/**
 * @description Renders the authenticated tenant projection and governed lifecycle availability.
 * @collaboration Mounted by App.jsx at /tms; consumes TenantProvider, which accepts
 *                only the Python EOS authenticated workspace-bootstrap projection.
 * @institutional Prevents browser roles or retired Node routes from appearing to
 *                 authorize cross-tenant tenant-directory or lifecycle commands.
 * @returns {JSX.Element} Read-only current-tenant status and C2 availability notice.
 * @throws Never converts absent or mismatched workspace state into tenant truth.
 */
export default function Sovereign_TenantManager() {
  const {
    activeTenant,
    loading,
    error,
    bootstrapReady,
    authorityMismatch,
  } = useTenants();
  const [copyState, setCopyState] = useState('');

  const tenantId = tenantIdentifier(activeTenant);
  const sealReference = useMemo(() => {
    const value = activeTenant?.proof_hash || activeTenant?.proofHash || activeTenant?.sealHash;
    return typeof value === 'string' && /^[A-Fa-f0-9]{128}$/.test(value) ? value : '';
  }, [activeTenant]);

  const copySealReference = useCallback(async () => {
    if (!sealReference) return;
    try {
      await navigator.clipboard.writeText(sealReference);
      setCopyState('Available seal reference copied. It has not been independently verified.');
    } catch {
      setCopyState('Clipboard access is unavailable. The reference remains visible in the authenticated projection.');
    }
  }, [sealReference]);

  const workspaceState = !bootstrapReady || loading
    ? 'AUTHENTICATED_WORKSPACE_LOADING'
    : authorityMismatch
      ? 'AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH'
      : tenantId
        ? 'AUTHENTICATED_WORKSPACE_AVAILABLE'
        : 'AUTHENTICATED_WORKSPACE_UNAVAILABLE';

  return (
    <main className={styles.module} aria-labelledby="tenant-management-heading">
      <header className={styles.header}>
        <div className={styles.titleGroup}>
          <div className={styles.iconBezel} aria-hidden="true">
            <ShieldCheck className={styles.goldIcon} size={22} />
          </div>
          <div>
            <h1 id="tenant-management-heading" className={styles.title}>Tenant workspace</h1>
            <p className={styles.subtitle}>Authenticated workspace projection from Python EOS</p>
          </div>
        </div>
      </header>

      <section
        className={styles.errorBanner}
        role="note"
        aria-label="Cross-tenant lifecycle availability"
        data-testid="tms-lifecycle-availability"
      >
        <AlertTriangle size={18} aria-hidden="true" />
        <div>
          <strong>Cross-tenant lifecycle commands are unavailable pending governed C2 authority.</strong>
          <p>
            Global tenant listing, tenant creation, and tenant suspension remain disabled.
            Frontend roles and legacy Node permissions do not grant these operations.
          </p>
        </div>
      </section>

      <div className={styles.directoryStatus} role="status" aria-live="polite" data-testid="tms-workspace-state">
        Workspace state: {workspaceState}
      </div>

      {error && (
        <p className={styles.errorBanner} role="alert" data-testid="tms-workspace-error">
          Authenticated workspace projection is unavailable: {error}
        </p>
      )}

      {tenantId ? (
        <section className={`${styles.tenantCard} ${styles.currentTenant}`} aria-labelledby="current-tenant-heading">
          <div className={styles.cardHeader}>
            <h2 id="current-tenant-heading" className={styles.tenantName}>
              {displayValue(activeTenant?.name || activeTenant?.organization_name || activeTenant?.organizationName)}
            </h2>
            <span className={styles.currentTenantBadge}>AUTHENTICATED WORKSPACE</span>
          </div>
          <div className={styles.cardBody}>
            <dl className={styles.cardMeta}>
              <div>
                <dt>Tenant identifier</dt>
                <dd>{tenantId}</dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd>{displayValue(activeTenant?.status)}</dd>
              </div>
              <div>
                <dt>Region</dt>
                <dd>{displayValue(activeTenant?.region)}</dd>
              </div>
              <div>
                <dt>Industry</dt>
                <dd>{displayValue(activeTenant?.industry)}</dd>
              </div>
            </dl>
          </div>
          {sealReference && (
            <div className={styles.sealSection}>
              <span className={styles.sealLabel}>Source-provided SHA3-512 reference</span>
              <code className={styles.sealHash}>{sealReference}</code>
              <button
                type="button"
                className={styles.copyBtn}
                onClick={copySealReference}
                aria-label="Copy source-provided seal reference"
              >
                {copyState.startsWith('Available') ? <Check size={14} /> : <Copy size={14} />}
              </button>
              <span className="sr-only" role="status">{copyState}</span>
            </div>
          )}
        </section>
      ) : (
        <section className={styles.emptyState} data-testid="tms-empty-workspace">
          <Database size={30} className={styles.emptyIcon} aria-hidden="true" />
          <h2>Authenticated tenant workspace unavailable</h2>
          <p>
            No tenant directory fallback is used. Sign-in must provide a current
            Python EOS workspace projection before tenant-scoped information is shown.
          </p>
        </section>
      )}

      <footer className={styles.footer}>
        <div className={styles.footerLeft}>
          <span className={styles.engineStatus}>Tenant lifecycle authority: GOVERNED C2 REQUIRED</span>
        </div>
        <div className={styles.footerRight}>
          <span>Read-only projection</span>
          <span className={styles.divider}>|</span>
          <span>Kennel EOS :9095</span>
        </div>
      </footer>
    </main>
  );
}

/**
 * ARTIFACT: WILSY OS Authenticated Tenant Workspace
 * VERSION: v58.0.0-PYTHON-EOS-C2-DENY-BOUNDARY
 * AUTHORITY BOUNDARY: Projection only; cross-tenant lifecycle remains governed C2.
 * TENANT POSTURE: Exact authenticated current workspace only.
 * FAIL-CLOSED POSTURE: Missing or mismatched workspace data stays unavailable.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
