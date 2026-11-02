"""Adversarial tests for the end-to-end provider evidence preflight composition."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.eos.auth.tenant_ownership_evidence_validation import (
    OwnershipEvidenceValidationError,
    RecoveryDecisionEnvelope,
    recovery_decision_message,
    signing_message,
)
from tools.eos.auth.tenant_ownership_provider_composition import (
    ProviderEvidenceCompositionError,
    ProviderEvidencePreflight,
    ProviderEvidencePreflightRequest,
    TenantOwnershipProviderEvidenceComposer,
)
from tools.eos.auth.tenant_ownership_provider_ports import (
    RecoveryDecisionLookup,
    RecoveryDecisionReceipt,
    RegistryLookup,
    RegistrySnapshot,
    SigningReceipt,
    SubjectProofingReceipt,
    SubjectProofingRequest,
)
from tools.eos.auth.tenant_ownership_verifier import TenantOwnershipOperation

NOW = datetime.now(timezone.utc)
TENANT = "tenant-1"
ENTITY = "entity-1"
PRINCIPAL = "principal-1"


def fp(value: str) -> str:
    return sha256(value.encode()).hexdigest()


class Registry:
    def __init__(self, history=None, unavailable=False):
        self.history = history or (RegistrySnapshot(
            "registry", ENTITY, "filing-1", "1", "ZA", "company", "ACTIVE",
            NOW - timedelta(seconds=1), NOW - timedelta(days=1),
            fp("source"), fp("attributes"), None,
        ),)
        self.unavailable = unavailable
        self.calls = 0

    def fetch_history(self, lookup: RegistryLookup):
        self.calls += 1
        if self.unavailable:
            raise TimeoutError("registry unavailable")
        return self.history


class Identity:
    def __init__(self, unavailable=False):
        self.unavailable = unavailable
        self.calls = 0

    def verify_subject(self, request: SubjectProofingRequest):
        self.calls += 1
        if self.unavailable:
            raise TimeoutError("identity provider unavailable")
        return SubjectProofingReceipt(
            "identity-provider", "identity-verifier", "IAL2",
            request.subject_reference, "evidence-1", fp("identity-evidence"),
            NOW - timedelta(seconds=1), NOW + timedelta(hours=1), "identity-revocation-1",
        )


class Revocation:
    def __init__(self, revoked=False, unavailable=False):
        self.revoked = revoked
        self.unavailable = unavailable

    def is_revoked(self, revocation_reference: str, at: datetime) -> bool:
        if self.unavailable:
            raise TimeoutError("revocation unavailable")
        return self.revoked


class Binding:
    def __init__(self, subject="subject-1"):
        self.subject = subject

    def subject_reference_for(self, tenant_id: str, principal_id: str) -> str:
        if (tenant_id, principal_id) != (TENANT, PRINCIPAL):
            raise PermissionError("binding denied")
        return self.subject


class Keys:
    def __init__(self):
        self.private = Ed25519PrivateKey.generate()
        self.status = "ACTIVE"

    def key_status(self, key_reference: str, revision: int, at: datetime) -> str:
        return self.status if (key_reference, revision) == ("signing-key", 4) else "UNKNOWN"

    def public_key(self, key_reference: str, revision: int):
        if (key_reference, revision) != ("signing-key", 4):
            raise KeyError(key_reference)
        return self.private.public_key()


class Signer:
    def __init__(self, keys: Keys, unavailable=False):
        self.keys = keys
        self.unavailable = unavailable
        self.last_request = None

    def sign_digest(self, request):
        if self.unavailable:
            raise TimeoutError("signer unavailable")
        self.last_request = request
        return SigningReceipt(
            "hsm-provider", "independent-custodian", request.key_reference,
            request.key_revision, "Ed25519",
            self.keys.private.sign(signing_message(request)).hex(),
            request.payload_digest, request.purpose, NOW - timedelta(seconds=1),
            "audit-1", fp("custody-proof"),
        )


class RecoveryKeys:
    def __init__(self):
        self.private = Ed25519PrivateKey.generate()
        self.status = "ACTIVE"

    def recovery_key_status(self, authority_id, root_ref, root_fp, key_ref, revision, at):
        if (authority_id, root_ref, root_fp, key_ref, revision) != (
            "independent-recovery", "recovery-root", fp("recovery-root"),
            "recovery-key", 2,
        ):
            return "UNTRUSTED"
        return self.status

    def public_key(self, key_reference, revision):
        if (key_reference, revision) != ("recovery-key", 2):
            raise KeyError(key_reference)
        return self.private.public_key()


class Recovery:
    def __init__(self, keys: RecoveryKeys, unavailable=False):
        self.keys = keys
        self.unavailable = unavailable

    def verify_decision(self, lookup: RecoveryDecisionLookup):
        if self.unavailable:
            raise TimeoutError("recovery provider unavailable")
        receipt = RecoveryDecisionReceipt(
            "independent-recovery", "recovery-root", fp("recovery-root"),
            "decision-1", fp("decision"), lookup.recovery_case_reference,
            lookup.recovery_case_fingerprint, lookup.successor_principal_id,
            fp("quorum"), fp("conflicts"), fp("notice"), "RESOLVED",
            NOW - timedelta(seconds=1), NOW + timedelta(hours=1), "recovery-revocation-1",
        )
        message = recovery_decision_message(
            lookup, receipt, "recovery-key", 2, "recovery-nonce"
        )
        return RecoveryDecisionEnvelope(
            receipt, "recovery-key", 2, "Ed25519",
            self.keys.private.sign(message).hex(), "recovery-nonce",
        )


def request(**changes):
    values = {
        "tenant_id": TENANT,
        "legal_entity_reference": ENTITY,
        "jurisdiction": "ZA",
        "principal_id": PRINCIPAL,
        "operation": TenantOwnershipOperation.TENANT_GENESIS,
        "purpose": "TENANT_GENESIS",
        "evaluated_at": NOW,
        "max_registry_age": timedelta(days=1),
        "signing_key_reference": "signing-key",
        "signing_key_revision": 4,
        "recovery_lookup": None,
    }
    values.update(changes)
    return ProviderEvidencePreflightRequest(**values)


def composer(*, registry=None, identity=None, revocation=None, binding=None,
             signer=None, signing_keys=None, recovery=None, recovery_keys=None):
    keys = signing_keys or Keys()
    return TenantOwnershipProviderEvidenceComposer(
        registry=registry or Registry(),
        identity=identity or Identity(),
        subject_revocation=revocation or Revocation(),
        principal_binding=binding or Binding(),
        signer=signer or Signer(keys),
        signing_keys=keys,
        recovery=recovery,
        recovery_keys=recovery_keys,
    )


def test_composition_rejects_pseudo_tenant_and_purpose_operation_substitution():
    with pytest.raises(ProviderEvidenceCompositionError, match="TENANT_OWNERSHIP_TENANT_ID_INVALID"):
        composer().compose(request(tenant_id="default"))
    with pytest.raises(ProviderEvidenceCompositionError, match="PURPOSE_OPERATION_MISMATCH"):
        composer().compose(request(purpose="OWNERSHIP_TRANSFER"))


def test_composition_binds_registry_subject_and_signature_into_one_preflight():
    keys = Keys()
    signer = Signer(keys)
    preflight = composer(signing_keys=keys, signer=signer).compose(request())
    assert type(preflight) is ProviderEvidencePreflight
    assert preflight.registry_assessment.selected_filing_reference == "filing-1"
    assert preflight.subject_reference == "subject-1"
    assert signer.last_request is not None
    assert preflight.signing_payload_digest == signer.last_request.payload_digest
    assert len(preflight.validation_fingerprint) == 64
    with pytest.raises(ProviderEvidenceCompositionError, match="CONSTRUCTOR_DISABLED"):
        ProviderEvidencePreflight()


def test_composition_denies_registry_conflict_before_identity_or_signing():
    history = (
        Registry().history[0],
        Registry().history[0].__class__(
            "registry", ENTITY, "filing-2", "2", "ZA", "company", "ACTIVE",
            NOW - timedelta(seconds=1), NOW, fp("source-2"), fp("attributes-2"), None,
        ),
    )
    identity = Identity()
    keys = Keys()
    signer = Signer(keys)
    with pytest.raises(ProviderEvidenceCompositionError, match="REGISTRY_SOURCE_NOT_CURRENT"):
        composer(registry=Registry(history), identity=identity,
                 signing_keys=keys, signer=signer).compose(request())
    assert identity.calls == 0
    assert signer.last_request is None


def test_composition_rejects_registry_record_for_different_legal_entity():
    row = Registry().history[0]
    wrong_entity = row.__class__(
        row.source_id, "attacker-entity", row.filing_reference, row.filing_revision,
        row.jurisdiction, row.entity_type, row.record_status, row.retrieved_at,
        row.effective_at, row.source_fingerprint, row.attributes_fingerprint,
        row.supersedes_filing_reference,
    )
    with pytest.raises(ProviderEvidenceCompositionError, match="REGISTRY_SELECTED_SOURCE_SCOPE_MISMATCH"):
        composer(registry=Registry((wrong_entity,))).compose(request())


def test_composition_denies_registry_identity_signer_and_revocation_outages():
    with pytest.raises(ProviderEvidenceCompositionError, match="REGISTRY_SOURCE_UNAVAILABLE"):
        composer(registry=Registry(unavailable=True)).compose(request())
    with pytest.raises(ProviderEvidenceCompositionError, match="SUBJECT_IDENTITY_PROVIDER_UNAVAILABLE"):
        composer(identity=Identity(unavailable=True)).compose(request())
    keys = Keys()
    with pytest.raises(ProviderEvidenceCompositionError, match="NON_EXPORTABLE_SIGNING_PROVIDER_UNAVAILABLE"):
        composer(signing_keys=keys, signer=Signer(keys, unavailable=True)).compose(request())
    with pytest.raises(ProviderEvidenceCompositionError, match="REVOCATION_UNAVAILABLE"):
        composer(revocation=Revocation(unavailable=True)).compose(request())


def test_composition_rejects_revoked_identity_and_revoked_signing_key():
    with pytest.raises(ProviderEvidenceCompositionError, match="RECEIPT_REVOKED"):
        composer(revocation=Revocation(revoked=True)).compose(request())
    keys = Keys()
    keys.status = "REVOKED"
    with pytest.raises(ProviderEvidenceCompositionError, match="NOT_CURRENT_OR_REVOKED"):
        composer(signing_keys=keys, signer=Signer(keys)).compose(request())


def test_recovery_composition_requires_exact_scope_and_independent_signed_decision():
    recovery_keys = RecoveryKeys()
    lookup = RecoveryDecisionLookup(
        TENANT, ENTITY, "case-1", fp("case"), PRINCIPAL, NOW,
    )
    recovery = Recovery(recovery_keys)
    result = composer(
        recovery=recovery, recovery_keys=recovery_keys,
    ).compose(request(
        operation=TenantOwnershipOperation.GOVERNED_RECOVERY,
        purpose="GOVERNED_RECOVERY", recovery_lookup=lookup,
    ))
    assert result.recovery_validation is not None
    assert result.recovery_validation.decision_reference == "decision-1"

    with pytest.raises(ProviderEvidenceCompositionError, match="RECOVERY_LOOKUP_SCOPE_MISMATCH"):
        composer(recovery=recovery, recovery_keys=recovery_keys).compose(
            request(operation=TenantOwnershipOperation.GOVERNED_RECOVERY,
                    purpose="GOVERNED_RECOVERY",
                    recovery_lookup=RecoveryDecisionLookup(
                        "other-tenant", ENTITY, "case-1", fp("case"), PRINCIPAL, NOW,
                    ))
        )


class MalformedRecovery:
    def verify_decision(self, lookup: RecoveryDecisionLookup):
        return None


def test_recovery_provider_outage_and_untrusted_key_fail_closed():
    recovery_keys = RecoveryKeys()
    lookup = RecoveryDecisionLookup(TENANT, ENTITY, "case-1", fp("case"), PRINCIPAL, NOW)
    with pytest.raises(ProviderEvidenceCompositionError, match="INDEPENDENT_RECOVERY_PROVIDER_UNAVAILABLE"):
        composer(
            recovery=Recovery(recovery_keys, unavailable=True),
            recovery_keys=recovery_keys,
        ).compose(request(
            operation=TenantOwnershipOperation.GOVERNED_RECOVERY,
            purpose="GOVERNED_RECOVERY", recovery_lookup=lookup,
        ))
    with pytest.raises(ProviderEvidenceCompositionError, match="RECOVERY_DECISION_ENVELOPE_INVALID"):
        composer(recovery=MalformedRecovery(), recovery_keys=recovery_keys).compose(
            request(operation=TenantOwnershipOperation.GOVERNED_RECOVERY,
                    purpose="GOVERNED_RECOVERY", recovery_lookup=lookup)
        )
    recovery_keys.status = "REVOKED"
    with pytest.raises(ProviderEvidenceCompositionError, match="RECOVERY_SIGNING_KEY_NOT_CURRENT"):
        composer(recovery=Recovery(recovery_keys), recovery_keys=recovery_keys).compose(
            request(operation=TenantOwnershipOperation.GOVERNED_RECOVERY,
                    purpose="GOVERNED_RECOVERY", recovery_lookup=lookup)
        )
