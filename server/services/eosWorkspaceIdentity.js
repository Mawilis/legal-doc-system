/**
 * Resolve PDF-renderer identity through the canonical EOS workspace authority.
 *
 * This adapter deliberately does not decode JWTs or query Mongoose models.
 * EOS verifies the bearer token, current session, tenant membership and role,
 * then returns the current principal profile in workspace-bootstrap.
 */
export async function resolveEosWorkspaceIdentity({
  baseUrl,
  authorization,
  tenantId,
  fetchImpl = globalThis.fetch,
  timeoutMs = 8000,
} = {}) {
  const bearer = typeof authorization === 'string' ? authorization.trim() : '';
  if (!/^Bearer\s+\S+$/i.test(bearer)) {
    return { ok: false, status: 401, code: 'AUTHENTICATION_REQUIRED' };
  }

  const scopedTenantId = typeof tenantId === 'string' ? tenantId.trim() : '';
  if (!scopedTenantId) {
    return { ok: false, status: 400, code: 'TENANT_SCOPE_REQUIRED' };
  }

  const target = typeof baseUrl === 'string' ? baseUrl.trim().replace(/\/+$/, '') : '';
  if (!target || typeof fetchImpl !== 'function') {
    return { ok: false, status: 503, code: 'AUTHORITY_UNAVAILABLE' };
  }

  let response;
  try {
    response = await fetchImpl(`${target}/api/auth/workspace-bootstrap`, {
      method: 'GET',
      headers: {
        Authorization: bearer,
        'X-Tenant-ID': scopedTenantId,
      },
      signal: AbortSignal.timeout(timeoutMs),
    });
  } catch {
    return { ok: false, status: 503, code: 'AUTHORITY_UNAVAILABLE' };
  }

  if (!response || response.ok !== true) {
    if (response?.status === 401) {
      return { ok: false, status: 401, code: 'AUTHENTICATION_REQUIRED' };
    }
    if (response?.status === 403) {
      return { ok: false, status: 403, code: 'WORKSPACE_ACCESS_DENIED' };
    }
    return { ok: false, status: 503, code: 'AUTHORITY_UNAVAILABLE' };
  }

  let payload;
  try {
    payload = await response.json();
  } catch {
    return { ok: false, status: 503, code: 'AUTHORITY_RESPONSE_INVALID' };
  }

  const user = payload?.user;
  const id = typeof user?.id === 'string' ? user.id.trim() : '';
  const email = typeof user?.email === 'string' ? user.email.trim().toLowerCase() : '';
  if (payload?.status !== 'READY' || !id || !email || !email.includes('@')) {
    return { ok: false, status: 503, code: 'AUTHORITY_RESPONSE_INVALID' };
  }

  const firstName = typeof user.firstName === 'string' ? user.firstName.trim() : '';
  const lastName = typeof user.lastName === 'string' ? user.lastName.trim() : '';
  const displayName = [firstName, lastName].filter(Boolean).join(' ');

  return {
    ok: true,
    user: { id, email, firstName, lastName, displayName },
    workspace: payload.workspace && typeof payload.workspace === 'object'
      ? payload.workspace
      : null,
  };
}
