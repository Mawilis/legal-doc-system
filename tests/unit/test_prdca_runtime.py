"""Direct certificate for the PRDCA runtime composition boundary.

TITLE: PRDCA Runtime Composition Direct Certificate
VERSION: v1.0.0-M11-R8-R3B-P8-P3K
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves explicit dependency wiring, caller-owned persistence, exact
         call ordering, and the absence of runtime transaction control.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_prdca_runtime.py
COLLABORATION / OWNERSHIP: Direct certificate for tools/eos/governance/prdca_runtime.py.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3K certifies the designated PRDCA runtime
           composition owner and its caller-owned transaction boundary.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Callable, cast
import pytest

import tools.eos.governance.prdca_runtime as module


class _Signer:
    def sign(self, message: bytes) -> bytes:
        return b"s" * 64


class _Resolver:
    def resolve(self, authority_key_id: str) -> Callable[[bytes, bytes], bool]:
        return lambda message, signature: True


class _Ledger:
    def append_batch(self, batch: object, session: object) -> None:
        return None


class _FakeAuthority:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def issue_platform_registration_certificate(self, **kwargs: object) -> object:
        self.calls.append(("prc", kwargs))
        return "prc"

    def issue_deployment_certification_certificate(self, **kwargs: object) -> object:
        self.calls.append(("dcc", kwargs))
        return "dcc"

    def verify_descriptor_binding(self, **kwargs: object) -> object:
        self.calls.append(("receipt", kwargs))
        return "receipt"

    def persist_certificate_batch(self, **kwargs: object) -> None:
        self.calls.append(("persist", kwargs))


def _runtime() -> module.PRDCARuntimeComposition:
    runtime = object.__new__(module.PRDCARuntimeComposition)
    runtime._authority = _FakeAuthority()  # type: ignore[attr-defined]
    return runtime


def test_constructor_requires_explicit_ledger() -> None:
    with pytest.raises(module.PRDCACompositionError):
        module.compose_prdca_runtime(
            signer=_Signer(),
            key_resolver=_Resolver(),
            deployment_evidence_key_resolver=_Resolver(),
            ledger=None,  # type: ignore[arg-type]
        )


def test_factory_wires_stateless_core_without_external_side_effects(tmp_path: Path) -> None:
    runtime = module.compose_prdca_runtime(
        signer=_Signer(),
        key_resolver=_Resolver(),
        deployment_evidence_key_resolver=_Resolver(),
        ledger=_Ledger(),
        artifact_root=tmp_path,
    )
    assert runtime.authority.__class__.__name__ == "PRDCAAuthority"
    assert module.PRDCA_RUNTIME_COMPOSITION_OWNER.endswith("CERTIFICATION_AUTHORITY")


def test_issue_and_persist_uses_exact_core_order_and_same_caller_session() -> None:
    runtime = _runtime()
    fake = cast(_FakeAuthority, runtime._authority)  # type: ignore[attr-defined]
    session = SimpleNamespace(active=True)
    batch = runtime.issue_and_persist_certificate_batch(
        source_identity="source",
        source_contract_version="v1",
        implementation_identity="impl:source",
        capability_class="credential-metadata",
        campaign_identity="campaign",
        authority_key_id="prdca-key:test",
        deployment_evidence=SimpleNamespace(),  # type: ignore[arg-type]
        descriptor=SimpleNamespace(),  # type: ignore[arg-type]
        session=session,  # type: ignore[arg-type]
    )
    assert batch.platform_registration == "prc"
    assert batch.deployment_certification == "dcc"
    assert batch.descriptor_receipt == "receipt"
    assert [name for name, _ in fake.calls] == ["prc", "dcc", "receipt", "persist"]
    persist_kwargs = fake.calls[-1][1]
    assert isinstance(persist_kwargs, dict)
    assert persist_kwargs["session"] is session


def test_individual_methods_delegate_without_transaction_control() -> None:
    runtime = _runtime()
    fake = cast(_FakeAuthority, runtime._authority)  # type: ignore[attr-defined]
    runtime.persist_certificate_batch(batch="batch", session="caller-session")  # type: ignore[arg-type]
    assert fake.calls == [("persist", {"batch": "batch", "session": "caller-session"})]


def test_runtime_has_no_transaction_lifecycle_methods() -> None:
    public_names = set(module.PRDCARuntimeComposition.__dict__)
    assert "start_transaction" not in public_names
    assert "commit" not in public_names
    assert "abort" not in public_names


# ARTIFACT: test_prdca_runtime.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3K
# AUTHORITY BOUNDARY: direct certificate for PRDCA runtime composition only
# TENANT POSTURE: platform governance scope; no tenant authorization
# FAIL-CLOSED POSTURE: explicit ledger and caller transaction are mandatory
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
