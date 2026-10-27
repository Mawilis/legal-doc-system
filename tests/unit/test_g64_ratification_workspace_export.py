"""G64 repository export is deterministic evidence, never ratification."""
import hashlib
import json
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.g64_ratification_workspace_evidence import (
    G64RatificationWorkspaceRecord,
    G64RecordState,
    G64WorkspaceEvidenceError,
    new_pending_decisions,
)
from tools.eos.legal_operations.domain.g64_ratification_workspace_export import (
    build_repository_export_bytes,
)

NOW = datetime(2026, 10, 27, tzinfo=timezone.utc)


def record():
    return G64RatificationWorkspaceRecord(
        record_id="g64-record-001",
        institution_id="institution-001",
        ratifier_principal_id="principal-pending-verification",
        contract_version="v1.0.0-P47-R95-G62-DRAFT",
        contract_sha3_512_fingerprint="a" * 128,
        created_at=NOW,
        state=G64RecordState.DRAFT,
        decisions=new_pending_decisions(),
    )


def test_export_is_deterministic_and_explicitly_non_authorizing():
    first = build_repository_export_bytes(tenant_id="tenant-001", record=record())
    second = build_repository_export_bytes(tenant_id="tenant-001", record=record())
    assert first == second
    manifest = json.loads(first)
    assert manifest["export_status"] == "DECISIONS_UNRESOLVED"
    assert manifest["ratification_complete"] is False
    assert manifest["permits_operational_access"] is False
    assert manifest["constitutes_ratification"] is False
    assert manifest["repository_commit_is_signature"] is False
    assert manifest["record"]["decisions"][0]["disposition"] is None
    digest = manifest.pop("manifest_sha3_512")
    canonical = json.dumps(
        manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False,
    ).encode("ascii")
    assert digest == hashlib.sha3_512(canonical).hexdigest()


def test_export_requires_exact_record_domain_type_and_valid_tenant_scope():
    with pytest.raises(G64WorkspaceEvidenceError, match="TENANT_ID_INVALID"):
        build_repository_export_bytes(tenant_id=" tenant-001 ", record=record())
