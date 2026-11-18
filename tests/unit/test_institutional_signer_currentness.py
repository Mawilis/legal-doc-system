"""TITLE: Institutional Signer Currentness Orchestration Certificate.
VERSION: v1.0.1-P12C-INSTITUTIONAL-SIGNER-CURRENTNESS-CERT
AUTHORITY: Direct orchestration certificate for verified enrollment currentness.
EPITOME: Proves active enrollment is read in a short transaction, remote
         evidence is checked outside transactions, and only a successful
         verifier result is persisted through a separate revision-guarded write.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_institutional_signer_currentness.py
COLLABORATION / OWNERSHIP: Exercises the canonical currentness orchestrator,
                           verifier contract, and enrollment registry boundary.
CERTIFICATION / UPDATE DATE: 2026-11-11
CHANGELOG: v1.0.1-P12C-INSTITUTIONAL-SIGNER-CURRENTNESS-CERT asserts that a
           non-active enrollment completes only its short read transaction and
           never invokes remote evidence verification or persistence, and
           narrows the optional persisted-result fixture before dereferencing it.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic references only; no external evidence is
                            fetched or persisted by these tests.
TENANT BOUNDARY: Exact tenant and certificate fingerprint are passed unchanged.
AUTHORITY BOUNDARY: Currentness orchestration does not establish signer approval.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from tools.eos.security.institutional_signer_currentness import (
    reconcile_institutional_signer_currentness,
)
from tools.eos.security.institutional_signer_evidence_verifier import (
    InstitutionalSignerEvidenceVerificationError,
    UnavailableInstitutionalSignerEvidenceVerifier,
)
from tools.eos.security.institutional_signer_enrollment_registry import (
    InstitutionalSignerRegistryConflict,
)


def _enrollment(status="ACTIVE"):
    return {
        "status": status,
        "revision": 7,
        "evidence_provenance_snapshot": {"schema": "enrollment-provenance"},
        "approval_evidence_provenance_snapshot": {"schema": "approval-provenance"},
    }


class _Registry:
    def __init__(self, row):
        self.row = row
        self.persisted = None

    def get_enrollment(self, **_kwargs):
        return self.row

    def record_verified_currentness(self, **kwargs):
        self.persisted = kwargs
        return {"evidence_currentness_status": "CURRENT", "revision": 8}


class _Verifier:
    def __init__(self, calls):
        self.calls = calls

    def verify_currentness(self, **kwargs):
        self.calls.append(("verify", kwargs))
        return SimpleNamespace(expected_enrollment_revision=kwargs["expected_enrollment_revision"])


def _run(registry, verifier, calls):
    def read_transaction(callback):
        result = callback("read-session")
        calls.append(("read-transaction-complete", None))
        return result

    def write_transaction(callback):
        calls.append(("write-transaction-start", None))
        return callback("write-session")

    return reconcile_institutional_signer_currentness(
        registry=registry,
        verifier=verifier,
        tenant_id="WILSYTENANT-4CD2FZ4O",
        certificate_fingerprint_sha256="a" * 64,
        evaluated_at=datetime.now(timezone.utc),
        idempotency_key="currentness-reconcile-7",
        actor_reference="runtime://approved-currentness-worker",
        read_transaction=read_transaction,
        write_transaction=write_transaction,
    )


def test_currentness_orchestration_performs_remote_recheck_between_short_transactions():
    calls = []
    registry = _Registry(_enrollment())
    result = _run(registry, _Verifier(calls), calls)

    assert result["evidence_currentness_status"] == "CURRENT"
    assert [item[0] for item in calls] == [
        "read-transaction-complete", "verify", "write-transaction-start",
    ]
    assert calls[1][1]["expected_enrollment_revision"] == 7
    assert registry.persisted is not None
    assert registry.persisted["session"] == "write-session"


def test_currentness_orchestration_never_checks_sources_for_non_active_enrollment():
    calls = []
    registry = _Registry(_enrollment(status="REVOKED"))
    with pytest.raises(InstitutionalSignerRegistryConflict, match="ACTIVE_ENROLLMENT_REQUIRED"):
        _run(registry, _Verifier(calls), calls)
    assert calls == [("read-transaction-complete", None)]
    assert registry.persisted is None


def test_currentness_source_outage_does_not_open_write_transaction():
    calls = []
    registry = _Registry(_enrollment())
    with pytest.raises(InstitutionalSignerEvidenceVerificationError):
        _run(registry, UnavailableInstitutionalSignerEvidenceVerifier(), calls)
    assert [item[0] for item in calls] == ["read-transaction-complete"]
    assert registry.persisted is None


def test_currentness_orchestration_propagates_revision_conflict_from_persist_phase():
    calls = []
    registry = _Registry(_enrollment())
    def conflict(**_kwargs):
        raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_CURRENTNESS_REVISION_CONFLICT")
    registry.record_verified_currentness = conflict
    with pytest.raises(InstitutionalSignerRegistryConflict, match="CURRENTNESS_REVISION_CONFLICT"):
        _run(registry, _Verifier(calls), calls)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_institutional_signer_currentness.py
# VERSION: v1.0.1-P12C-INSTITUTIONAL-SIGNER-CURRENTNESS-CERT
# AUTHORITY BOUNDARY: enrollment currentness orchestration only
# TENANT POSTURE: exact tenant and certificate fingerprint stay bound
# FAIL-CLOSED POSTURE: inactive, unavailable, incomplete, and conflicting state rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
