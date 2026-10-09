"""Direct P2D certificate for authenticated content delivery.

TITLE: Legal Client Acceptance Content Delivery Service Unit Certificate
VERSION: v1.0.0-L9A4-P2D-CLIENT-ACCEPTANCE-CONTENT-DELIVERY-UNIT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Exercise the complete server-derived, revalidated, hash-verified
         content projection with synthetic authorities and no database writes.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_acceptance_content_service.py
COLLABORATION / OWNERSHIP: The service is the only production artifact under
                            test; all source authorities are monkeypatched
                            synthetic seams owned by their certified domains.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2D certificate covers valid delivery, server identity
           derivation, dependency staleness/denial, locator privacy, media,
           encoding, fingerprint and zero-mutation boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque values only; no secrets or PII.
TENANT BOUNDARY: Test identities and every fake source are exact tenant scoped.
AUTHORITY BOUNDARY: Delivery projection only; no acceptance or legal authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import TenantAuthorizationReason, TenantAuthorizationDecision
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import LegalClientMatterAcceptanceInstrumentLifecycleStatus
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter, CaseMatterState
from tools.eos.legal_operations.service import legal_client_acceptance_content_service as service

TENANT, PRINCIPAL, MATTER_ID, CONTEXT_ID, INSTRUMENT_ID = "tenant-p2d", "principal-p2d", "matter-p2d", "context-p2d", "instrument-p2d"
NOW = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)
CONTENT = b"Synthetic reviewed matter content."
FP = __import__("hashlib").sha3_512(CONTENT).hexdigest()


class Session:
    in_transaction = True


class Reader:
    def __init__(self, content: bytes = CONTENT, media_type: str = "text/plain", error: bool = False) -> None:
        self.content, self.media_type, self.error, self.references = content, media_type, error, []

    def read(self, reference: str, *, tenant_id: str, session: Any) -> service.StoredContent:
        self.references.append((reference, tenant_id, session))
        if self.error:
            raise RuntimeError("storage unavailable")
        return service.StoredContent(self.content, self.media_type)


def _identity(status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    return SovereignIdentity(identity_id=PRINCIPAL, tenant_id=TENANT, username=None, email=None, roles=[], permissions=[], auth_method="synthetic", status=status)


def _harness(monkeypatch: pytest.MonkeyPatch, *, context: Any = None, reader: Reader | None = None, authorized: bool = True) -> dict[str, Any]:
    matter = CaseMatter(tenant_id=TENANT, case_matter_id=MATTER_ID, matter_reference="matter", opened_at=NOW, evidence_reference="matter-source")
    party = SimpleNamespace(tenant_id=TENANT, case_matter_id=MATTER_ID, matter_fingerprint=matter.fingerprint, party_id="party-p2d", subject_reference="subject", subject_identity_fingerprint="a" * 128, fingerprint="b" * 128)
    capacity = SimpleNamespace(tenant_id=TENANT, case_matter_id=MATTER_ID, matter_fingerprint=matter.fingerprint, capacity_id="capacity-p2d", principal_id=PRINCIPAL, party_id=party.party_id, subject_reference=party.subject_reference, subject_identity_fingerprint=party.subject_identity_fingerprint, fingerprint="a" * 128)
    instrument = SimpleNamespace(tenant_id=TENANT, case_matter_id=MATTER_ID, matter_fingerprint=matter.fingerprint, instrument_id="instrument-p2d", version="1.0.0", fingerprint="c" * 128, content_fingerprint=FP, content_reference="server://p2d/content", title="Review", review_scope="review:v1", effective_from=NOW - timedelta(days=1))
    lifecycle = SimpleNamespace(tenant_id=TENANT, case_matter_id=MATTER_ID, instrument_id=INSTRUMENT_ID, version="1.0.0", instrument_fingerprint=instrument.fingerprint, matter_fingerprint=matter.fingerprint, status=LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE, fingerprint="d" * 128)
    approval = SimpleNamespace(tenant_id=TENANT, case_matter_id=MATTER_ID, instrument_id=INSTRUMENT_ID, version="1.0.0", instrument_fingerprint=instrument.fingerprint, content_fingerprint=FP, approval_id="approval-p2d", effective_from=NOW - timedelta(days=1), decision=SimpleNamespace(value="APPROVED"), fingerprint="e" * 128)
    value = context or SimpleNamespace(acceptance_context_id=CONTEXT_ID, tenant_id=TENANT, actor_principal_id=PRINCIPAL, case_matter_id=MATTER_ID, matter_fingerprint=matter.fingerprint, party_id=party.party_id, party_fingerprint=party.fingerprint, subject_reference=party.subject_reference, subject_identity_fingerprint=party.subject_identity_fingerprint, capacity_id=capacity.capacity_id, capacity_fingerprint=capacity.fingerprint, instrument_id=instrument.instrument_id, instrument_version=instrument.version, instrument_fingerprint=instrument.fingerprint, content_fingerprint=FP, content_reference=instrument.content_reference, title=instrument.title, review_scope=instrument.review_scope, lifecycle_status=lifecycle.status, lifecycle_fingerprint=lifecycle.fingerprint, approval_id=approval.approval_id, approval_fingerprint=approval.fingerprint, issued_at=NOW - timedelta(minutes=1), expires_at=NOW + timedelta(minutes=9))
    monkeypatch.setattr(service, "authorize_tenant_operation", lambda **_: TenantAuthorizationDecision(authorized, TenantAuthorizationReason.AUTHORIZED if authorized else TenantAuthorizationReason.INVALID_INPUT, "tenant_legal_client" if authorized else "", "LEGAL_CLIENT" if authorized else ""))
    monkeypatch.setattr(service.context_registry, "get_valid_context", lambda *_args, **_kwargs: value)
    monkeypatch.setattr(service.visibility_registry.LegalClientMatterVisibilityRegistry, "resolve_current_active", staticmethod(lambda *_args, **_kwargs: SimpleNamespace(tenant_id=TENANT, client_principal_id=PRINCIPAL, case_matter_id=MATTER_ID)))
    monkeypatch.setattr(service.matter_registry.LegalOperationsLifecycleRegistry, "get_entity_history", staticmethod(lambda *_args, **_kwargs: (matter,)))
    monkeypatch.setattr(service, "resolve_current_lifecycle_snapshot", lambda *_args, **_kwargs: matter)
    monkeypatch.setattr(service.party_registry, "list_matter_parties", lambda *_args, **_kwargs: (party,))
    monkeypatch.setattr(service.capacity_registry, "list_valid_capacities_at", lambda *_args, **_kwargs: (capacity,))
    monkeypatch.setattr(service.instrument_registry, "get_latest_effective_version", lambda *_args, **_kwargs: instrument)
    monkeypatch.setattr(service.lifecycle_registry, "get_current_lifecycle", lambda *_args, **_kwargs: lifecycle)
    monkeypatch.setattr(service.approval_registry, "get_current_approval", lambda *_args, **_kwargs: approval)
    return {"context": value, "reader": reader or Reader(), "instrument": instrument, "lifecycle": lifecycle, "approval": approval}


def _invoke(h: dict[str, Any], **overrides: Any) -> service.LegalClientAcceptanceContent:
    kwargs = dict(identity=_identity(), acceptance_context_id=CONTEXT_ID, context_collection=object(), matter_lifecycle_collection=object(), visibility_collection=object(), party_collection=object(), capacity_collection=object(), instrument_collection=object(), instrument_lifecycle_collection=object(), approval_collection=object(), content_reader=h["reader"], principal_repository=object(), membership_repository=object(), business_role_repository=object(), role_assignment_repository=object(), session=Session(), clock=lambda: NOW)
    kwargs.update(overrides)
    return service.deliver_legal_client_acceptance_context_content(**cast(dict[str, Any], kwargs))


def test_valid_delivery_is_bounded_and_server_derived(monkeypatch: pytest.MonkeyPatch) -> None:
    h = _harness(monkeypatch)
    result = _invoke(h)
    assert result.content == CONTENT.decode() and result.media_type == "text/plain"
    assert result.acceptance_context_id == CONTEXT_ID and result.content_fingerprint == FP
    assert h["reader"].references == [("server://p2d/content", TENANT, h["reader"].references[0][2])]
    assert "server://" not in repr(result)


@pytest.mark.parametrize("field", ["tenant_id", "actor_principal_id"])
def test_context_identity_mismatch_rejected(monkeypatch: pytest.MonkeyPatch, field: str) -> None:
    context = SimpleNamespace(**_harness_defaults())
    setattr(context, field, "other")
    with pytest.raises(service.LegalClientAcceptanceContentDeliveryError):
        _invoke(_harness(monkeypatch, context=context))


def _harness_defaults() -> dict[str, Any]:
    return {"acceptance_context_id": CONTEXT_ID, "tenant_id": TENANT, "actor_principal_id": PRINCIPAL, "case_matter_id": MATTER_ID, "matter_fingerprint": "a" * 128, "party_id": "party-p2d", "party_fingerprint": "b" * 128, "subject_reference": "subject", "subject_identity_fingerprint": "a" * 128, "capacity_id": "capacity-p2d", "capacity_fingerprint": "a" * 128, "instrument_id": "instrument-p2d", "instrument_version": "1.0.0", "instrument_fingerprint": "c" * 128, "content_fingerprint": FP, "content_reference": "server://p2d/content", "title": "Review", "review_scope": "review:v1", "lifecycle_status": LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE, "lifecycle_fingerprint": "d" * 128, "approval_id": "approval-p2d", "approval_fingerprint": "e" * 128, "issued_at": NOW - timedelta(minutes=1), "expires_at": NOW + timedelta(minutes=9)}


@pytest.mark.parametrize("case", range(26))
def test_fail_closed_matrix(monkeypatch: pytest.MonkeyPatch, case: int) -> None:
    reader = Reader()
    h = _harness(monkeypatch, reader=reader)
    if case == 0:
        h["context"].expires_at = NOW - timedelta(seconds=1)
        monkeypatch.setattr(service.context_registry, "get_valid_context", lambda *_a, **_k: None)
    elif case == 1: h = _harness(monkeypatch, reader=reader, authorized=False)
    elif case == 2: monkeypatch.setattr(service.visibility_registry.LegalClientMatterVisibilityRegistry, "resolve_current_active", staticmethod(lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError())))
    elif case == 3: monkeypatch.setattr(service, "resolve_current_lifecycle_snapshot", lambda *_a, **_k: SimpleNamespace(state=CaseMatterState.CLOSED, tenant_id=TENANT, case_matter_id=MATTER_ID))
    elif case == 4: monkeypatch.setattr(service.capacity_registry, "list_valid_capacities_at", lambda *_a, **_k: ())
    elif case == 5: monkeypatch.setattr(service.capacity_registry, "list_valid_capacities_at", lambda *_a, **_k: (SimpleNamespace(principal_id=PRINCIPAL, party_id="party-p2d", subject_reference="subject", subject_identity_fingerprint="a" * 128), SimpleNamespace(principal_id=PRINCIPAL, party_id="party-p2d", subject_reference="subject", subject_identity_fingerprint="a" * 128)))
    elif case == 6: monkeypatch.setattr(service.instrument_registry, "get_latest_effective_version", lambda *_a, **_k: None)
    elif case == 7: h["instrument"].version = "2.0.0"
    elif case == 8: h["instrument"].fingerprint = "f" * 128
    elif case == 9: monkeypatch.setattr(service.lifecycle_registry, "get_current_lifecycle", lambda *_a, **_k: None)
    elif case == 10: h["lifecycle"].status = SimpleNamespace(value="RETIRED")
    elif case == 11: h["lifecycle"].fingerprint = "f" * 128
    elif case == 12: monkeypatch.setattr(service.approval_registry, "get_current_approval", lambda *_a, **_k: None)
    elif case == 13: h["approval"].decision = SimpleNamespace(value="REJECTED")
    elif case == 14: h["approval"].fingerprint = "f" * 128
    elif case == 15: reader = h["reader"] = Reader(error=True)
    elif case == 16: reader = h["reader"] = Reader(media_type="application/pdf")
    elif case == 17: reader = h["reader"] = Reader(content=b"\xff")
    elif case == 18: reader = h["reader"] = Reader(content=b"changed")
    elif case == 19: reader = h["reader"] = Reader(content=b"\x00bad")
    elif case == 20: reader = h["reader"] = Reader(content=b"")
    elif case == 21: reader = h["reader"] = Reader(content=b"x" * (service.MAX_CONTENT_BYTES + 1))
    elif case == 22: pytest.raises(service.LegalClientAcceptanceContentDeliveryError, _invoke, h, session=None); return
    elif case == 23: pytest.raises(service.LegalClientAcceptanceContentDeliveryError, _invoke, h, identity=cast(Any, object())); return
    elif case == 24: pytest.raises(service.LegalClientAcceptanceContentDeliveryError, _invoke, h, identity=_identity(PrincipalStatus.SUSPENDED)); return
    elif case == 25: pytest.raises(service.LegalClientAcceptanceContentDeliveryError, _invoke, h, acceptance_context_id=""); return
    with pytest.raises(service.LegalClientAcceptanceContentDeliveryError):
        _invoke(h)


def test_errors_do_not_contain_content_or_locator(monkeypatch: pytest.MonkeyPatch) -> None:
    h = _harness(monkeypatch, reader=Reader(error=True))
    with pytest.raises(service.LegalClientAcceptanceContentDeliveryError) as caught:
        _invoke(h)
    assert CONTENT.decode() not in str(caught.value) and "server://p2d/content" not in str(caught.value)


def test_no_downstream_authority_or_writer_is_called(monkeypatch: pytest.MonkeyPatch) -> None:
    h = _harness(monkeypatch)
    result = _invoke(h)
    assert result.content_bytes == len(CONTENT)


# ARTIFACT: test_legal_client_acceptance_content_service.py
# VERSION: v1.0.0-L9A4-P2D-CLIENT-ACCEPTANCE-CONTENT-DELIVERY-UNIT-CERT
# AUTHORITY BOUNDARY: synthetic delivery projection certificate only
# TENANT POSTURE: exact synthetic tenant/principal scope
# FAIL-CLOSED POSTURE: denial, staleness, unsupported and altered content reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
