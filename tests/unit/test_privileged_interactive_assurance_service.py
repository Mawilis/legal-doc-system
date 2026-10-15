"""
TITLE:
    WILSY OS Privileged Interactive Assurance Service Direct Unit Certificate

VERSION:
    v1.0.1-P3-R3G-C5-R3-HISTORIC-LOOKUP-FIXTURE

AUTHORITY:
    Wilsy OS Sovereign IAM

PURPOSE:
    Certify authoritative currentness derivation, fail-closed behavior,
    idempotency, transaction ownership, transient transaction propagation,
    purpose binding, and absence of activation/financial authority.

CERTIFICATION DATE:
    2026-10-14

CHANGELOG:
    v1.0.1-P3-R3G-C5-R3-HISTORIC-LOOKUP-FIXTURE
        Extends the C5 direct-unit fixture with the production
        get_by_scope_idempotency read seam. Exact replay uses the same
        principal/channel/purpose/idempotency store as create_or_replay.
        Assertions and production authority are unchanged.
    v1.0.0-P3-R3G-C5-R2-DIRECT-UNIT-CERTIFICATE
        Initial C5-R2 direct-unit certificate for interactive assurance
        currentness, fail-closed behavior, idempotency, transaction ownership,
        transient transaction propagation, purpose binding, and authority
        boundaries.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from pymongo.errors import OperationFailure

from tools.eos.auth.principal_authority import (
    PrincipalAuthority,
)
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_status import (
    PrincipalStatus,
)
from tools.eos.auth.privileged_channel_currentness import (
    FactorVerificationStatus,
    InteractiveFactorVerificationEvent,
)
from tools.eos.auth.privileged_factor_verification_currentness_registry import (
    PrivilegedFactorVerificationCurrentnessRegistry,
)
from tools.eos.auth.privileged_interactive_assurance_service import (
    PrivilegedInteractiveAssuranceError,
    PrivilegedInteractiveAssuranceService,
)
from tools.eos.auth.privileged_interactive_security_proof import (
    PrivilegedInteractiveProofStatus,
    PrivilegedInteractiveSecurityProof,
)
from tools.eos.auth.privileged_interactive_security_proof_registry import (
    PrivilegedInteractiveSecurityProofRegistry,
)
from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssurancePurpose,
    PrivilegedAssuranceReason,
)
from tools.eos.auth.privileged_security_assurance_evidence_registry import (
    PrivilegedSecurityAssuranceEvidenceRegistry,
)


NOW = datetime(
    2026,
    10,
    14,
    8,
    0,
    tzinfo=timezone.utc,
)

TENANT = "tenant-c5"
PRINCIPAL = "principal-c5"
SESSION_REFERENCE = "WILSYSESSION-c5"
FACTOR_REFERENCE = "WILSYFACTOR-c5"
PROOF_REFERENCE = "WILSYPROOFREF-c5"
PROOF_ID = "WILSYPROOF-c5"
REVISION = 7

PURPOSE = (
    PrivilegedAssurancePurpose
    .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
)


class Tx:
    in_transaction = True


class InactiveTx:
    in_transaction = False


class AuthReader:
    def __init__(
        self,
        *,
        revision: int = REVISION,
        session_current: bool = True,
    ) -> None:
        self.revision = revision
        self.session_current = session_current
        self.calls: list[
            tuple[str, tuple[object, ...], object]
        ] = []

    def get_credential_revision(
        self,
        tenant_id: str,
        user_id: str,
        *,
        session: Any = None,
    ) -> int:
        self.calls.append(
            (
                "credential",
                (tenant_id, user_id),
                session,
            )
        )
        return self.revision

    def is_session_current(
        self,
        tenant_id: str,
        user_id: str,
        session_reference: str,
        *,
        at: datetime | None = None,
        session: Any = None,
    ) -> bool:
        self.calls.append(
            (
                "session",
                (
                    tenant_id,
                    user_id,
                    session_reference,
                    at,
                ),
                session,
            )
        )
        return self.session_current


def proof(
    *,
    status: PrivilegedInteractiveProofStatus =
        PrivilegedInteractiveProofStatus.VERIFIED,
) -> PrivilegedInteractiveSecurityProof:
    return PrivilegedInteractiveSecurityProof(
        proof_id=PROOF_ID,
        principal_id=PRINCIPAL,
        factor_verification_reference=
            FACTOR_REFERENCE,
        authenticated_at=NOW,
        credential_revision=REVISION,
        session_reference=SESSION_REFERENCE,
        proof_status=status,
        proof_reference=PROOF_REFERENCE,
    )


def factor(
    *,
    authenticated_at: datetime = NOW,
) -> InteractiveFactorVerificationEvent:
    return InteractiveFactorVerificationEvent(
        factor_verification_reference=
            FACTOR_REFERENCE,
        principal_id=PRINCIPAL,
        session_reference=SESSION_REFERENCE,
        credential_revision=REVISION,
        authenticated_at=authenticated_at,
        status=
            FactorVerificationStatus.VERIFIED,
    )


def service(
    monkeypatch: pytest.MonkeyPatch,
    *,
    auth: AuthReader | None = None,
    proof_value:
        PrivilegedInteractiveSecurityProof | None = None,
    factor_value:
        InteractiveFactorVerificationEvent | None = None,
    principal_status:
        PrincipalStatus = PrincipalStatus.ACTIVE,
    evidence_sink: object | None = None,
    evidence_lookup: object | None = None,
) -> tuple[
    PrivilegedInteractiveAssuranceService,
    AuthReader,
]:
    auth_reader = (
        auth
        if auth is not None
        else AuthReader()
    )

    proof_registry = (
        PrivilegedInteractiveSecurityProofRegistry(
            object()
        )
    )

    factor_registry = (
        PrivilegedFactorVerificationCurrentnessRegistry(
            object()
        )
    )

    evidence_registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            object()
        )
    )

    if evidence_lookup is None:
        monkeypatch.setattr(
            evidence_registry,
            "get_by_scope_idempotency",
            lambda *,
            principal_id,
            assurance_channel,
            assurance_purpose,
            idempotency_key,
            session=None:
                None,
        )
    else:
        monkeypatch.setattr(
            evidence_registry,
            "get_by_scope_idempotency",
            evidence_lookup,
        )

    current_proof = (
        proof_value
        if proof_value is not None
        else proof()
    )

    current_factor = (
        factor_value
        if factor_value is not None
        else factor()
    )

    monkeypatch.setattr(
        proof_registry,
        "get_current_by_proof_reference",
        lambda *,
        proof_reference,
        session=None:
            SimpleNamespace(
                proof=current_proof
            ),
    )

    monkeypatch.setattr(
        factor_registry,
        "get",
        lambda *,
        factor_verification_reference,
        session=None:
            current_factor,
    )

    monkeypatch.setattr(
        PrincipalAuthorityRepository,
        "get",
        staticmethod(
            lambda principal_id,
            collection=None,
            *,
            session=None:
                PrincipalAuthority(
                    principal_id,
                    principal_status,
                    0,
                )
        ),
    )

    if evidence_sink is None:
        monkeypatch.setattr(
            evidence_registry,
            "create_or_replay",
            lambda value, *,
            session:
                value,
        )
    else:
        monkeypatch.setattr(
            evidence_registry,
            "create_or_replay",
            evidence_sink,
        )

    return (
        PrivilegedInteractiveAssuranceService(
            auth_registry=auth_reader,
            principal_collection=object(),
            factor_registry=factor_registry,
            proof_registry=proof_registry,
            evidence_registry=evidence_registry,
            maximum_age_seconds=300,
            clock=lambda: NOW,
            evidence_id_factory=lambda:
                "WILSYASSURANCE-c5",
        ),
        auth_reader,
    )


def compose(
    value: PrivilegedInteractiveAssuranceService,
    *,
    tx: object | None = None,
    idempotency_key: str = "idem-c5",
):
    return value.compose(
        tenant_id=TENANT,
        proof_reference=PROOF_REFERENCE,
        assurance_purpose=PURPOSE,
        idempotency_key=idempotency_key,
        session=(
            tx
            if tx is not None
            else Tx()
        ),
    )


def test_complete_current_interactive_proof_is_sufficient(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value, auth = service(monkeypatch)
    tx = Tx()

    result = compose(
        value,
        tx=tx,
    )

    assert result.decision.sufficient is True
    assert (
        result.decision.reason
        is PrivilegedAssuranceReason.SUFFICIENT
    )
    assert result.evidence.principal_id == PRINCIPAL
    assert result.evidence.assurance_purpose is PURPOSE
    assert result.evidence.session_current is True
    assert (
        result.evidence.factor_verification_current
        is True
    )
    assert (
        result.evidence.authentication_recency_current
        is True
    )
    assert result.evidence.workload_proof_current is None
    assert result.evidence.workload_proof_reference is None

    assert auth.calls
    assert all(
        call[2] is tx
        for call in auth.calls
    )


def test_inactive_principal_denies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value, _ = service(
        monkeypatch,
        principal_status=
            PrincipalStatus.SUSPENDED,
    )

    result = compose(value)

    assert result.decision.sufficient is False
    assert (
        result.decision.reason
        is PrivilegedAssuranceReason
        .PRINCIPAL_NOT_CURRENT
    )


def test_missing_principal_denies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value, _ = service(monkeypatch)

    monkeypatch.setattr(
        PrincipalAuthorityRepository,
        "get",
        staticmethod(
            lambda *args, **kwargs:
                (_ for _ in ()).throw(
                    PrincipalAuthorityNotFoundError(
                        "PRINCIPAL_AUTHORITY_NOT_FOUND"
                    )
                )
        ),
    )

    result = compose(value)

    assert result.decision.sufficient is False
    assert (
        result.decision.reason
        is PrivilegedAssuranceReason
        .PRINCIPAL_NOT_CURRENT
    )


def test_stale_credential_denies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value, _ = service(
        monkeypatch,
        auth=AuthReader(
            revision=REVISION + 1,
        ),
    )

    result = compose(value)

    assert (
        result.decision.reason
        is PrivilegedAssuranceReason
        .CREDENTIAL_NOT_CURRENT
    )


def test_stale_session_denies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value, _ = service(
        monkeypatch,
        auth=AuthReader(
            session_current=False,
        ),
    )

    result = compose(value)

    assert (
        result.decision.reason
        is PrivilegedAssuranceReason
        .SESSION_NOT_CURRENT
    )


@pytest.mark.parametrize(
    "status",
    (
        PrivilegedInteractiveProofStatus.REVOKED,
        PrivilegedInteractiveProofStatus.INVALIDATED,
    ),
)
def test_noncurrent_proof_denies(
    monkeypatch: pytest.MonkeyPatch,
    status: PrivilegedInteractiveProofStatus,
) -> None:
    value, _ = service(
        monkeypatch,
        proof_value=proof(
            status=status,
        ),
    )

    result = compose(value)

    assert (
        result.decision.reason
        is PrivilegedAssuranceReason
        .ASSURANCE_PROOF_NOT_CURRENT
    )


def test_missing_factor_denies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value, _ = service(monkeypatch)

    monkeypatch.setattr(
        value._factor_registry,
        "get",
        lambda **kwargs: None,
    )

    result = compose(value)

    assert (
        result.decision.reason
        is PrivilegedAssuranceReason
        .FACTOR_VERIFICATION_NOT_CURRENT
    )


def test_stale_authentication_denies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value, _ = service(
        monkeypatch,
        factor_value=factor(
            authenticated_at=
                NOW - timedelta(
                    seconds=301
                ),
        ),
    )

    result = compose(value)

    assert (
        result.decision.reason
        is PrivilegedAssuranceReason
        .AUTHENTICATION_NOT_RECENT
    )


@pytest.mark.parametrize(
    "session",
    (
        None,
        InactiveTx(),
    ),
)
def test_active_transaction_required(
    monkeypatch: pytest.MonkeyPatch,
    session: object | None,
) -> None:
    value, _ = service(monkeypatch)

    with pytest.raises(
        PrivilegedInteractiveAssuranceError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        value.compose(
            tenant_id=TENANT,
            proof_reference=PROOF_REFERENCE,
            assurance_purpose=PURPOSE,
            idempotency_key="idem",
            session=session,
        )


def test_caller_cannot_assert_security_truth() -> None:
    import inspect

    signature = inspect.signature(
        PrivilegedInteractiveAssuranceService.compose
    )

    assert set(signature.parameters) == {
        "self",
        "tenant_id",
        "proof_reference",
        "assurance_purpose",
        "idempotency_key",
        "session",
    }


def test_same_idempotency_replay_converges(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    persisted: dict[
        tuple[str, str, str, str],
        object,
    ] = {}

    def sink(
        value,
        *,
        session,
    ):
        key = (
            value.principal_id,
            value.assurance_channel.value,
            value.assurance_purpose.value,
            value.idempotency_key,
        )

        existing = persisted.get(key)

        if existing is None:
            persisted[key] = value
            return value

        if existing == value:
            return existing

        raise RuntimeError(
            "DIVERGENT_REPLAY"
        )

    def lookup(
        *,
        principal_id,
        assurance_channel,
        assurance_purpose,
        idempotency_key,
        session=None,
    ):
        return persisted.get(
            (
                principal_id,
                assurance_channel,
                assurance_purpose,
                idempotency_key,
            )
        )

    value, _ = service(
        monkeypatch,
        evidence_sink=sink,
        evidence_lookup=lookup,
    )

    first = compose(
        value,
        idempotency_key="same",
    )

    second = compose(
        value,
        idempotency_key="same",
    )

    assert second.evidence == first.evidence


def test_transient_transaction_error_is_preserved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transient = OperationFailure(
        "transient",
        code=251,
        details={
            "errorLabels": [
                "TransientTransactionError",
            ]
        },
    )

    def sink(
        value,
        *,
        session,
    ):
        raise transient

    value, _ = service(
        monkeypatch,
        evidence_sink=sink,
    )

    with pytest.raises(
        OperationFailure,
    ) as captured:
        compose(value)

    assert (
        captured.value
        .has_error_label(
            "TransientTransactionError"
        )
    )


def test_no_activation_role_or_financial_authority() -> None:
    import inspect
    import tools.eos.auth.privileged_interactive_assurance_service as module

    source = inspect.getsource(
        module
    ).casefold()

    for forbidden in (
        "privileged_activation_registry",
        "role_assignment_repository",
        "financial_execution_repository",
        "start_transaction(",
        "commit_transaction(",
        "abort_transaction(",
    ):
        assert forbidden not in source


# =============================================================================
# WILSY OS TEST ARTIFACT SEAL
# ARTIFACT: test_privileged_interactive_assurance_service.py
# VERSION: v1.0.1-P3-R3G-C5-R3-HISTORIC-LOOKUP-FIXTURE
# PRODUCTION AUTHORITY: NONE
# P4 PRIVILEGED ACTIVATION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS TEST ARTIFACT
