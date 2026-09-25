/**
 * TITLE: WILSY OS Authenticated Tenant Branding Asset Hook
 * VERSION: v1.0.0-D21B12-AUTHENTICATED-BRANDING-ASSET-LIFECYCLE
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Convert one already-admitted D21B8 logo/favicon descriptor into a
 *          transient browser object URL through the certified D21B12 client,
 *          with deterministic replacement/unmount revocation and stale-request
 *          suppression.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/hooks/useAuthenticatedTenantBrandingAsset.js
 * COLLABORATION / OWNERSHIP: AuthContext/D21B8 owns descriptor admission;
 *                            tenantBrandingAssetClient owns authenticated blob
 *                            transport; this hook owns transient presentation
 *                            lifecycle only.
 * CERTIFICATION / UPDATE DATE: 2026-09-25
 * SECURITY / PRIVACY POSTURE: No blob URL is persisted to storage or promoted
 *                             into tenant authority. Replaced/unmounted URLs are
 *                             revoked, and late responses cannot overwrite a
 *                             newer descriptor.
 * TENANT BOUNDARY: This hook receives no tenant selector and sends none.
 * AUTHORITY BOUNDARY: Presentation lifecycle only; no IAM, entitlement,
 *                     profile, upload, legal-command or financial authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
 */

import { useEffect, useMemo, useState } from 'react';
import {
  createTenantBrandingObjectUrl,
  fetchAuthenticatedTenantBrandingAsset,
  revokeTenantBrandingObjectUrl,
} from '../services/tenantBrandingAssetClient.js';

export const VERSION =
  'v1.0.0-D21B12-AUTHENTICATED-BRANDING-ASSET-LIFECYCLE';

const descriptorKey = (descriptor) => {
  if (!descriptor || typeof descriptor !== 'object') return '';
  return [
    descriptor.kind,
    descriptor.reference,
    descriptor.contentFingerprint,
    descriptor.mediaType,
  ].map((value) => String(value ?? '')).join('|');
};

export function useAuthenticatedTenantBrandingAsset(descriptor) {
  const key = useMemo(
    () => descriptorKey(descriptor),
    [
      descriptor?.kind,
      descriptor?.reference,
      descriptor?.contentFingerprint,
      descriptor?.mediaType,
    ],
  );
  const [state, setState] = useState({
    objectUrl: null,
    status: 'ABSENT',
    errorCode: null,
  });

  useEffect(() => {
    let cancelled = false;
    let ownedObjectUrl = null;

    if (!key) {
      setState({
        objectUrl: null,
        status: 'ABSENT',
        errorCode: null,
      });
      return () => {
        cancelled = true;
      };
    }

    setState({
      objectUrl: null,
      status: 'LOADING',
      errorCode: null,
    });

    const load = async () => {
      try {
        const blob = await fetchAuthenticatedTenantBrandingAsset(descriptor);
        const objectUrl = createTenantBrandingObjectUrl(blob);
        ownedObjectUrl = objectUrl;

        if (cancelled) {
          revokeTenantBrandingObjectUrl(objectUrl);
          ownedObjectUrl = null;
          return;
        }

        setState({
          objectUrl,
          status: 'READY',
          errorCode: null,
        });
      } catch (error) {
        if (cancelled) return;
        setState({
          objectUrl: null,
          status: 'UNAVAILABLE',
          errorCode:
            typeof error?.code === 'string' && error.code
              ? error.code
              : 'D21B12_ASSET_DELIVERY_UNAVAILABLE',
        });
      }
    };

    void load();

    return () => {
      cancelled = true;
      if (ownedObjectUrl) {
        revokeTenantBrandingObjectUrl(ownedObjectUrl);
        ownedObjectUrl = null;
      }
    };
  }, [key]);

  return state;
}

export default useAuthenticatedTenantBrandingAsset;


// ARTIFACT: useAuthenticatedTenantBrandingAsset.js
// VERSION: v1.0.0-D21B12-AUTHENTICATED-BRANDING-ASSET-LIFECYCLE
// AUTHORITY BOUNDARY: transient browser object-URL lifecycle only
// TENANT POSTURE: no tenant selector exists; server derives scope
// FAIL-CLOSED POSTURE: absent/error/stale responses produce no renderable URL; owned URLs are revoked
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
