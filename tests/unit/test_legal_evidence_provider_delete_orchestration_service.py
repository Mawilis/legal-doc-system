"""Unit certificate for Legal Evidence provider-delete orchestration.

TITLE: Legal Evidence Provider Delete Orchestration Unit Certificate
VERSION: v1.0.0-L10A2R-A3-P4-P6D5-PROVIDER-DELETE-ORCHESTRATION-UNIT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME:
    Certify fail-closed provider-delete orchestration ordering, execution
    fencing, exact replay, ambiguity classification and authority boundaries.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_evidence_provider_delete_orchestration_service.py
COLLABORATION / OWNERSHIP:
    Python EOS Legal Operations / Legal Evidence.
CERTIFICATION / UPDATE DATE: 2026-10-03
CHANGELOG:
    v1.0.0-L10A2R-A3-P4-P6D5-PROVIDER-DELETE-ORCHESTRATION-UNIT-CERT
    establishes sovereign certificate metadata and explicitly certifies that
    unresolved uncertainty outranks coexisting execution evidence at preflight.
COMPLIANCE:
    WILSY OS Sovereign Governance Contract v1.2.0; deterministic unit seams,
    exact tenant scoping and fail-closed evidence precedence.
SECURITY / PRIVACY POSTURE:
    Synthetic opaque identities only; no credentials or external provider I/O.
TENANT BOUNDARY:
    All command, authorization, claim, evidence and uncertainty observations
    remain bound to one exact synthetic tenant.
AUTHORITY BOUNDARY:
    Certificate-only observations; no cleanup, provider retry, reconciliation
    execution, physical-absence, lifecycle, IAM, billing or settlement authority.
FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains the exclusive financial execution authority.
"""

from datetime import datetime, timedelta, timezone
from hashlib import sha3_512
import json
from types import SimpleNamespace

import pytest

from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_command import (
    SCHEMA as COMMAND_SCHEMA,
    VERSION as COMMAND_VERSION,
    LegalEvidenceProviderCleanupCommand,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_claim import (
    open_legal_evidence_provider_delete_execution_claim,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_evidence import (
    LegalEvidenceProviderDeleteExecutionEvidence,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_uncertainty import (
    open_legal_evidence_provider_delete_execution_uncertainty,
)
from tools.eos.legal_operations.service.legal_evidence_provider_delete_orchestration_service import (
    VERSION,
    LegalEvidenceProviderDeleteOrchestrationError,
    LegalEvidenceProviderDeleteOrchestrationService,
)
from tools.eos.legal_operations.service.legal_evidence_s3_provider_delete_adapter import (
    LegalEvidenceS3ProviderDeleteExecutionEvidence,
)


AT = datetime(2026, 10, 2, 16, 0, tzinfo=timezone.utc)


def _command() -> LegalEvidenceProviderCleanupCommand:
    payload: dict[str, object] = {
        "schema": COMMAND_SCHEMA,
        "command_version": COMMAND_VERSION,
        "command_id": "command-p6d5",
        "tenant_id": "tenant-p6d5",
        "principal_id": "principal-p6d5",
        "provider_name": "aws_s3",
        "storage_reference": "opaque/storage/p6d5",
        "object_version_reference": "version-p6d5",
        "cleanup_authorization_id": "authorization-p6d5",
        "cleanup_authorization_fingerprint": "a" * 128,
        "tenant_authorization_decision_id": "decision-p6d5",
        "tenant_authorization_evidence_fingerprint": "b" * 128,
        "issued_at": AT.isoformat(),
        "reason_reference": "reason-p6d5",
    }

    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    payload["fingerprint"] = sha3_512(raw).hexdigest()

    return LegalEvidenceProviderCleanupCommand.from_dict(
        payload
    )


class _Session:
    def __init__(self, owner) -> None:
        self.owner = owner
        self.in_transaction = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        if self.in_transaction:
            self.abort_transaction()

    def start_transaction(self):
        self.in_transaction = True
        self.owner.active += 1

    def commit_transaction(self):
        self.in_transaction = False
        self.owner.active -= 1

    def abort_transaction(self):
        if self.in_transaction:
            self.in_transaction = False
            self.owner.active -= 1


class _Client:
    def __init__(self) -> None:
        self.active = 0

    def start_session(self):
        return _Session(self)


class _Registry:
    def __init__(
        self,
        *,
        value=None,
        create_error=None,
    ) -> None:
        self.value = value
        self.created = []
        self.create_error = create_error

    def get_by_command_id(self, **_kwargs):
        return self.value

    def get_by_authorization_id(self, **_kwargs):
        return self.value

    def create_or_replay(self, value, **_kwargs):
        if self.create_error is not None:
            raise self.create_error

        self.created.append(value)
        self.value = value
        return value


class _Adapter:
    def __init__(
        self,
        client: _Client,
        *,
        error=None,
    ) -> None:
        self.client = client
        self.error = error
        self.calls = 0
        self.requests = []

    def execute_delete(self, request):
        assert self.client.active == 0
        self.calls += 1
        self.requests.append(request)

        if self.error is not None:
            raise self.error

        return LegalEvidenceS3ProviderDeleteExecutionEvidence(
            provider_name="aws_s3",
            storage_reference="opaque/storage/p6d5",
            object_version_reference="version-p6d5",
            delete_marker=None,
            delete_marker_version_reference=None,
        )


class _Clock:
    def __init__(self) -> None:
        self.index = 0

    def __call__(self):
        self.index += 1
        return AT + timedelta(seconds=self.index)


def _ids(kind: str) -> str:
    return {
        "claim": "claim-p6d5",
        "execution_evidence": "execution-p6d5",
        "uncertainty": "uncertainty-p6d5",
    }[kind]


def _authorization(command):
    return SimpleNamespace(
        authorization_id=command.cleanup_authorization_id,
        tenant_id=command.tenant_id,
        provider_name=command.provider_name,
        storage_reference=command.storage_reference,
        object_version_reference=
            command.object_version_reference,
        fingerprint=
            command.cleanup_authorization_fingerprint,
    )


def _service(
    *,
    command=None,
    authorization=None,
    claim=None,
    evidence=None,
    uncertainty=None,
    evidence_create_error=None,
    adapter_error=None,
):
    command = _command() if command is None else command
    client = _Client()

    command_registry = _Registry(value=command)
    authorization_registry = _Registry(
        value=(
            _authorization(command)
            if authorization is None
            else authorization
        )
    )
    claim_registry = _Registry(value=claim)
    evidence_registry = _Registry(
        value=evidence,
        create_error=evidence_create_error,
    )
    uncertainty_registry = _Registry(value=uncertainty)
    adapter = _Adapter(
        client,
        error=adapter_error,
    )

    service = LegalEvidenceProviderDeleteOrchestrationService(
        client=client,
        command_registry=command_registry,
        cleanup_authorization_registry=
            authorization_registry,
        claim_registry=claim_registry,
        execution_evidence_registry=evidence_registry,
        uncertainty_registry=uncertainty_registry,
        provider_adapter=adapter,
        clock=_Clock(),
        id_factory=_ids,
    )

    return (
        service,
        client,
        claim_registry,
        evidence_registry,
        uncertainty_registry,
        adapter,
        command,
    )


def _evidence(command):
    return LegalEvidenceProviderDeleteExecutionEvidence(
        execution_evidence_id="execution-existing",
        tenant_id=command.tenant_id,
        command_id=command.command_id,
        cleanup_authorization_id=
            command.cleanup_authorization_id,
        provider_name=command.provider_name,
        storage_reference=command.storage_reference,
        object_version_reference=
            command.object_version_reference,
        command_fingerprint=command.fingerprint,
        cleanup_authorization_fingerprint=
            command.cleanup_authorization_fingerprint,
        delete_marker=None,
        delete_marker_version_reference=None,
        executed_at=AT + timedelta(seconds=2),
    )



class _UnknownCommitError(RuntimeError):
    """Deterministic Mongo-style unknown commit acknowledgement."""

    def has_error_label(self, label: str) -> bool:
        return label == "UnknownTransactionCommitResult"


class _UnknownCommitSession(_Session):
    """Inject unknown acknowledgement on execution-evidence commit only."""

    def commit_transaction(self):
        self.owner.commit_count += 1

        if self.owner.commit_count == 3:
            self.in_transaction = False
            self.owner.active -= 1
            self.owner.on_unknown_commit()
            raise _UnknownCommitError(
                "unknown-commit-result"
            )

        super().commit_transaction()


class _UnknownCommitClient(_Client):
    def __init__(self, on_unknown_commit) -> None:
        super().__init__()
        self.commit_count = 0
        self.on_unknown_commit = on_unknown_commit

    def start_session(self):
        return _UnknownCommitSession(self)


class _UnknownCommitEvidenceRegistry(_Registry):
    """Mutable fake durable view used only by unknown-commit certificates."""

    def __init__(self) -> None:
        super().__init__()
        self.readback_error: BaseException | None = None
        self.unknown_commit_seen = False

    def get_by_command_id(self, **_kwargs):
        if (
            self.unknown_commit_seen
            and self.readback_error is not None
        ):
            raise self.readback_error

        return self.value


def _unknown_commit_service(
    *,
    outcome: str,
):
    command = _command()
    evidence_registry = (
        _UnknownCommitEvidenceRegistry()
    )
    uncertainty_registry = _Registry()

    holder = {}

    def on_unknown_commit() -> None:
        evidence_registry.unknown_commit_seen = True

        if outcome == "EXACT":
            # create_or_replay already staged the exact value in the fake
            # registry. Preserve it to model commit success + lost ack.
            return

        if outcome == "ABSENT":
            evidence_registry.value = None
            return

        if outcome == "DIVERGENT":
            evidence_registry.value = _evidence(
                command
            )
            return

        if outcome == "READBACK_FAILURE":
            evidence_registry.value = None
            evidence_registry.readback_error = (
                RuntimeError(
                    "fresh-readback-unavailable"
                )
            )
            return

        raise AssertionError(outcome)

    client = _UnknownCommitClient(
        on_unknown_commit
    )

    command_registry = _Registry(
        value=command
    )
    authorization_registry = _Registry(
        value=_authorization(command)
    )
    claim_registry = _Registry()
    adapter = _Adapter(client)

    service = (
        LegalEvidenceProviderDeleteOrchestrationService(
            client=client,
            command_registry=command_registry,
            cleanup_authorization_registry=
                authorization_registry,
            claim_registry=claim_registry,
            execution_evidence_registry=
                evidence_registry,
            uncertainty_registry=
                uncertainty_registry,
            provider_adapter=adapter,
            clock=_Clock(),
            id_factory=_ids,
        )
    )

    holder["client"] = client

    return (
        service,
        client,
        claim_registry,
        evidence_registry,
        uncertainty_registry,
        adapter,
        command,
    )

def test_version():
    assert VERSION == (
        "v1.3.0-L10A2R-A3-P4-P6D5-"
        "PROVIDER-DELETE-ORCHESTRATION"
    )


def test_happy_path_claim_before_provider_and_evidence_after():
    (
        service,
        client,
        claims,
        evidence,
        uncertainty,
        adapter,
        command,
    ) = _service()

    result = service.execute(
        tenant_id=command.tenant_id,
        command_id=command.command_id,
    )

    assert client.active == 0
    assert adapter.calls == 1
    assert len(claims.created) == 1
    assert len(evidence.created) == 1
    assert uncertainty.created == []
    assert result == evidence.created[0]


def test_existing_execution_evidence_short_circuits_provider():
    command = _command()
    existing = _evidence(command)

    (
        service,
        _client,
        _claims,
        _evidence_registry,
        _uncertainty,
        adapter,
        _returned_command,
    ) = _service(
        command=command,
        evidence=existing,
    )

    result = service.execute(
        tenant_id=command.tenant_id,
        command_id=command.command_id,
    )

    assert result == existing
    assert adapter.calls == 0


def test_existing_claim_without_execution_blocks_provider():
    command = _command()

    claim = (
        open_legal_evidence_provider_delete_execution_claim(
            claim_id="claim-existing",
            command=command,
            claimed_at=AT + timedelta(seconds=1),
        )
    )

    (
        service,
        _client,
        _claims,
        _evidence,
        _uncertainty,
        adapter,
        _returned_command,
    ) = _service(
        command=command,
        claim=claim,
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="PREEXISTING_CLAIM_REQUIRES_RECONCILIATION",
    ) as captured:
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert captured.value.reconciliation_required is True
    assert adapter.calls == 0


def test_existing_uncertainty_blocks_provider():
    command = _command()
    execution = _evidence(command)

    uncertainty = (
        open_legal_evidence_provider_delete_execution_uncertainty(
            uncertainty_id="uncertainty-existing",
            command=command,
            execution_evidence=execution,
            uncertainty_recorded_at=
                execution.executed_at
                + timedelta(seconds=1),
        )
    )

    (
        service,
        _client,
        _claims,
        _evidence_registry,
        _uncertainty,
        adapter,
        _returned_command,
    ) = _service(
        command=command,
        uncertainty=uncertainty,
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="RECONCILIATION_REQUIRED",
    ):
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert adapter.calls == 0


def test_existing_evidence_and_uncertainty_prioritizes_uncertainty():
    command = _command()
    execution = _evidence(command)
    unresolved = open_legal_evidence_provider_delete_execution_uncertainty(
        uncertainty_id="uncertainty-coexisting",
        command=command,
        execution_evidence=execution,
        uncertainty_recorded_at=(
            execution.executed_at
            + timedelta(seconds=1)
        ),
    )
    (
        service,
        _client,
        claims,
        evidence,
        uncertainty,
        adapter,
        _returned_command,
    ) = _service(
        command=command,
        evidence=execution,
        uncertainty=unresolved,
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="RECONCILIATION_REQUIRED",
    ) as captured:
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert captured.value.reconciliation_required is True
    assert adapter.calls == 0
    assert claims.created == []
    assert evidence.created == []
    assert uncertainty.created == []


def test_provider_failure_after_claim_never_retries():
    (
        service,
        _client,
        claims,
        evidence,
        uncertainty,
        adapter,
        command,
    ) = _service(
        adapter_error=RuntimeError("provider-failed")
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match=(
            "PROVIDER_EXECUTION_FAILED_"
            "RECONCILIATION_REQUIRED"
        ),
    ) as captured:
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert captured.value.reconciliation_required is True
    assert len(claims.created) == 1
    assert adapter.calls == 1
    assert evidence.created == []
    assert uncertainty.created == []


def test_post_provider_persistence_failure_records_uncertainty():
    (
        service,
        _client,
        claims,
        evidence,
        uncertainty,
        adapter,
        command,
    ) = _service(
        evidence_create_error=RuntimeError(
            "mongo-ambiguous"
        ),
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="POST_PROVIDER_PERSISTENCE_UNCERTAIN",
    ) as captured:
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert captured.value.reconciliation_required is True
    assert len(claims.created) == 1
    assert adapter.calls == 1
    assert evidence.created == []
    assert len(uncertainty.created) == 1
    assert (
        uncertainty.created[0].command_id
        == command.command_id
    )


def test_authorization_mismatch_rejects_before_provider():
    command = _command()
    invalid = _authorization(command)
    invalid.fingerprint = "f" * 128

    (
        service,
        _client,
        claims,
        evidence,
        uncertainty,
        adapter,
        _returned_command,
    ) = _service(
        command=command,
        authorization=invalid,
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="CLEANUP_AUTHORIZATION_MISMATCH",
    ):
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert claims.created == []
    assert evidence.created == []
    assert uncertainty.created == []
    assert adapter.calls == 0



def test_stale_preflight_exact_claim_blocks_second_provider_call():
    """Exact claim replay after stale preflight never grants fence ownership."""
    command = _command()

    exact_claim = (
        open_legal_evidence_provider_delete_execution_claim(
            claim_id="claim-p6d5",
            command=command,
            claimed_at=AT + timedelta(seconds=1),
        )
    )

    class _StalePreflightClaimRegistry(_Registry):
        """Expose absence once, then another invocation's exact durable claim."""

        def __init__(self) -> None:
            super().__init__()
            self.read_count = 0

        def get_by_command_id(self, **_kwargs):
            self.read_count += 1

            if self.read_count == 1:
                return None

            return exact_claim

    client = _Client()

    command_registry = _Registry(
        value=command
    )
    authorization_registry = _Registry(
        value=_authorization(command)
    )
    claim_registry = (
        _StalePreflightClaimRegistry()
    )
    evidence_registry = _Registry()
    uncertainty_registry = _Registry()
    adapter = _Adapter(client)

    service = (
        LegalEvidenceProviderDeleteOrchestrationService(
            client=client,
            command_registry=command_registry,
            cleanup_authorization_registry=
                authorization_registry,
            claim_registry=claim_registry,
            execution_evidence_registry=
                evidence_registry,
            uncertainty_registry=uncertainty_registry,
            provider_adapter=adapter,
            clock=_Clock(),
            id_factory=_ids,
        )
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="CLAIM_FENCE_NOT_ACQUIRED",
    ) as captured:
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert (
        captured.value.reconciliation_required
        is True
    )

    # First read is preflight absence. Second read is inside the fresh
    # claim transaction and observes the exact claim committed elsewhere.
    assert claim_registry.read_count == 2

    # The stale invocation did not create/replay its own claim and never
    # crossed the provider boundary.
    assert claim_registry.created == []
    assert adapter.calls == 0

    # No fabricated provider result, uncertainty or execution evidence.
    assert evidence_registry.created == []
    assert uncertainty_registry.created == []

    # Every transaction owned by this invocation is closed fail-closed.
    assert client.active == 0


def test_unknown_commit_exact_durable_evidence_reconciles_success():
    (
        service,
        client,
        claims,
        evidence,
        uncertainty,
        adapter,
        command,
    ) = _unknown_commit_service(
        outcome="EXACT",
    )

    result = service.execute(
        tenant_id=command.tenant_id,
        command_id=command.command_id,
    )

    assert adapter.calls == 1
    assert len(claims.created) == 1
    assert len(evidence.created) == 1
    assert evidence.unknown_commit_seen is True

    # The exact durable value is returned after fresh readback rather
    # than converted into contradictory uncertainty.
    assert result == evidence.value
    assert uncertainty.created == []

    # Preflight + claim + ambiguous evidence commit. Fresh readback is
    # aborted and therefore never increments the commit counter.
    assert client.commit_count == 3
    assert client.active == 0


def test_unknown_commit_absent_records_uncertainty_after_readback():
    (
        service,
        client,
        claims,
        evidence,
        uncertainty,
        adapter,
        command,
    ) = _unknown_commit_service(
        outcome="ABSENT",
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="UNKNOWN_COMMIT_READBACK_ABSENT",
    ) as captured:
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert captured.value.reconciliation_required is True
    assert adapter.calls == 1
    assert len(claims.created) == 1
    assert evidence.unknown_commit_seen is True
    assert evidence.value is None

    # Uncertainty is written only after the fresh durable read proves
    # execution evidence absent from that snapshot.
    assert len(uncertainty.created) == 1
    assert (
        uncertainty.created[0].command_id
        == command.command_id
    )

    # Uncertainty persistence is the fourth committed transaction.
    assert client.commit_count == 4
    assert client.active == 0


def test_unknown_commit_divergent_evidence_fails_closed_without_uncertainty():
    (
        service,
        client,
        claims,
        evidence,
        uncertainty,
        adapter,
        command,
    ) = _unknown_commit_service(
        outcome="DIVERGENT",
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="UNKNOWN_COMMIT_READBACK_DIVERGENT",
    ) as captured:
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert captured.value.reconciliation_required is True
    assert adapter.calls == 1
    assert len(claims.created) == 1
    assert evidence.unknown_commit_seen is True
    assert evidence.value is not None

    # Divergent durable state cannot become success and cannot manufacture
    # a second contradictory uncertainty record.
    assert uncertainty.created == []
    assert client.commit_count == 3
    assert client.active == 0


def test_unknown_commit_readback_failure_fails_closed_without_uncertainty():
    (
        service,
        client,
        claims,
        evidence,
        uncertainty,
        adapter,
        command,
    ) = _unknown_commit_service(
        outcome="READBACK_FAILURE",
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="UNKNOWN_COMMIT_READBACK_FAILED",
    ) as captured:
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert captured.value.reconciliation_required is True
    assert adapter.calls == 1
    assert len(claims.created) == 1
    assert evidence.unknown_commit_seen is True

    # Failure to certify durable state does not become success and does
    # not create uncertainty before readback classification completes.
    assert uncertainty.created == []
    assert client.commit_count == 3
    assert client.active == 0


def test_duck_typed_provider_result_rejects_before_durable_execution_evidence():
    """Reject duck-typed provider evidence after I/O and require reconciliation.

    The provider boundary may already have executed when it returns. Only the
    exact certified S3 provider-evidence type may cross into canonical durable
    execution evidence. A lookalike object must therefore fail closed, leave
    the pre-provider claim intact, persist no execution evidence, grant no
    retry authority, and require reconciliation.
    """
    command = _command()
    client = _Client()

    command_registry = _Registry(value=command)
    authorization_registry = _Registry(
        value=_authorization(command)
    )
    claim_registry = _Registry()
    evidence_registry = _Registry()
    uncertainty_registry = _Registry()

    class _DuckTypedAdapter:
        def __init__(self) -> None:
            self.calls = 0

        def execute_delete(self, request):
            assert client.active == 0
            self.calls += 1

            # Deliberately supplies every attribute consumed by orchestration
            # while NOT being the certified provider-evidence domain type.
            return SimpleNamespace(
                provider_name=request.provider_name,
                storage_reference=request.storage_reference,
                object_version_reference=(
                    request.object_version_reference
                ),
                delete_marker=None,
                delete_marker_version_reference=None,
            )

    adapter = _DuckTypedAdapter()

    service = LegalEvidenceProviderDeleteOrchestrationService(
        client=client,
        command_registry=command_registry,
        cleanup_authorization_registry=authorization_registry,
        claim_registry=claim_registry,
        execution_evidence_registry=evidence_registry,
        uncertainty_registry=uncertainty_registry,
        provider_adapter=adapter,
        clock=_Clock(),
        id_factory=_ids,
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match=(
            "PROVIDER_RESULT_INVALID_"
            "RECONCILIATION_REQUIRED"
        ),
    ) as captured:
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert captured.value.reconciliation_required is True

    # Provider I/O already occurred exactly once. The durable claim is the
    # execution fence and must survive to prohibit automatic re-execution.
    assert adapter.calls == 1
    assert len(claim_registry.created) == 1

    # An uncertified duck-typed provider result must never become canonical
    # execution evidence or fabricated uncertainty.
    assert evidence_registry.created == []
    assert uncertainty_registry.created == []

    assert client.active == 0

def test_service_exposes_no_retry_release_or_absence_surface():
    forbidden = {
        "retry",
        "retry_delete",
        "release_claim",
        "prove_absence",
        "reconcile",
    }

    public = {
        name
        for name in dir(
            LegalEvidenceProviderDeleteOrchestrationService
        )
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(public)


# ARTIFACT: test_legal_evidence_provider_delete_orchestration_service.py
# VERSION: v1.0.0-L10A2R-A3-P4-P6D5-PROVIDER-DELETE-ORCHESTRATION-UNIT-CERT
# AUTHORITY BOUNDARY: certificate-only orchestration observations; no cleanup, provider retry, reconciliation execution, physical-absence, lifecycle, IAM, billing, payment or settlement authority
# TENANT POSTURE: exact synthetic tenant scope across command, authorization, claim, execution evidence and uncertainty
# TRANSACTION POSTURE: deterministic fake sessions certify orchestration ownership and provider-outside-transaction ordering
# FAIL-CLOSED POSTURE: uncertainty, claims, provider failures and persistence ambiguity never become retry or success authority
# PROVIDER POSTURE: deterministic fake provider only; no live provider call or physical-absence inference
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
