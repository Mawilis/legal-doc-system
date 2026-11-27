/**
 * TITLE: WILSY OS Authenticated System Footer
 * VERSION: v1.0.0-SHARED-AUTHENTICATED-FOOTER
 * AUTHORITY: WILSY OS shared presentation chrome.
 * EPITOME: One consistent, non-authoritative footer across protected surfaces.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/chrome/WilsySystemFooter.jsx
 * COLLABORATION / OWNERSHIP: AuthenticatedGlobalChrome and WilsyHeadquartersWorkspace.
 * CERTIFICATION / UPDATE DATE: 2026-11-27
 * CHANGELOG: v1.0.0-SHARED-AUTHENTICATED-FOOTER unifies brand, current surface, exact sourced employer, and Python Kennel EOS labeling without duplicate footers.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Display-only; no token, credential, or speculative tenant identity.
 * TENANT BOUNDARY: Employer and tenant are shown together only when verified by the caller's session.
 * AUTHORITY BOUNDARY: Footer navigation and appearance never grant permissions.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
 */
import React from 'react';

export default function WilsySystemFooter({
  surface = 'Headquarters · Enterprise operations',
  employerName = '',
  employerReference = '',
  className = '',
  ariaLabel = 'WILSY OS operating footer',
}) {
  const exactEmployer = typeof employerName === 'string' ? employerName.trim() : '';
  const exactReference = typeof employerReference === 'string' ? employerReference.trim() : '';
  return (
    <footer role="contentinfo" aria-label={ariaLabel} data-wilsy-system-footer="true"
      className={`hq-global-footer flex min-h-[45px] w-full flex-wrap items-center justify-between gap-x-5 gap-y-2 border-t border-[#334e78] bg-[#0e2444] px-4 py-3 text-[11px] leading-normal text-[#c4d4e8] ${className}`}>
      <span><strong className="font-extrabold tracking-wide text-[#f0ce7b]">WILSY OS</strong> · Build. Operate. Grow.</span>
      <span>{surface}</span>
      <span className="hq-footer-tenant flex flex-wrap items-baseline gap-2" aria-label="Current employer tenant">
        {exactEmployer && exactReference
          ? <><strong className="font-bold text-[#f1f5f9]">{exactEmployer}</strong><small className="text-[#e4c580]">{exactReference}</small></>
          : 'Tenant verification pending'}
      </span>
      <span>Python Kennel EOS · Source-owned records</span>
    </footer>
  );
}

// ARTIFACT: client/src/components/chrome/WilsySystemFooter.jsx
// VERSION: v1.0.0-SHARED-AUTHENTICATED-FOOTER
// AUTHORITY BOUNDARY: Presentation only; no authentication or privilege changes.
// TENANT POSTURE: Exact verified tenant and employer pair only.
// FAIL-CLOSED POSTURE: Missing employer evidence displays verification pending.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns financial execution.
// END OF WILSY OS SOVEREIGN ARTIFACT
