"""Trusted server-side verification of commercial agreement execution evidence.

The verifier never accepts signature bytes, certificates, signatory identity or
mandate claims from an HTTP request. Those are loaded through server-owned
evidence, PKI trust, timestamp and signatory-authority adapters. The PKI adapter
must validate the configured trust path and revocation state at signing time.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
from typing import Any, Protocol

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from cryptography.x509.oid import ExtensionOID

from tools.eos.saas.entitlement.commercial_agreement import CommercialAgreement
from tools.eos.saas.entitlement.commercial_bundle_activation import (
    VerifiedCommercialAgreementExecutionEvidence,
)


class CommercialAgreementExecutionVerificationError(RuntimeError):
    """Bounded fail-closed execution verification failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class StoredCommercialExecutionEvidence:
    """Evidence envelope retrieved from a server-controlled evidence store."""

    tenant_id: str
    agreement_id: str
    evidence_reference: str
    contract_reference: str
    contract_version: str
    offer_fingerprint: str
    signed_document: bytes
    signature: bytes
    signature_algorithm: str
    signing_certificate_fingerprint: str
    signatory_principal_id: str
    timestamp_token: bytes


@dataclass(frozen=True, slots=True)
class TrustedSigningCertificate:
    """PKI resolver verdict for one exact certificate at a signing instant."""

    certificate_pem: bytes
    certificate_fingerprint: str
    trust_anchor_reference: str
    trust_anchor_fingerprint: str
    chain_valid: bool
    revocation_status: str


@dataclass(frozen=True, slots=True)
class VerifiedSignatoryMandate:
    tenant_id: str
    agreement_id: str
    principal_id: str
    authority_reference: str
    authority_fingerprint: str
    active: bool


@dataclass(frozen=True, slots=True)
class TrustedExecutionTimestamp:
    signed_at: datetime
    evidence_reference: str
    evidence_fingerprint: str


class ExecutionEvidenceStore(Protocol):
    def load(self, tenant_id: str, agreement_id: str, evidence_reference: str) -> StoredCommercialExecutionEvidence: ...


class SigningCertificateTrustResolver(Protocol):
    def resolve(
        self, *, tenant_id: str, principal_id: str, certificate_fingerprint: str,
        at: datetime,
    ) -> TrustedSigningCertificate: ...


class SignatoryMandateResolver(Protocol):
    def resolve(
        self, *, tenant_id: str, agreement_id: str, principal_id: str, at: datetime,
    ) -> VerifiedSignatoryMandate: ...


class TrustedTimestampVerifier(Protocol):
    def verify(
        self, *, tenant_id: str, agreement_id: str, timestamp_token: bytes,
        signed_payload_fingerprint: str,
    ) -> TrustedExecutionTimestamp: ...


def _sha3(payload: object) -> str:
    return hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False,
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _fingerprint(value: object, code: str) -> str:
    if not isinstance(value, str) or len(value) != 128 or any(
        char not in "0123456789abcdef" for char in value
    ):
        raise CommercialAgreementExecutionVerificationError(code)
    return value


def canonical_execution_document(agreement: CommercialAgreement) -> bytes:
    """Return the exact immutable agreement terms that the signatory must sign."""
    payload = {
        "schema": "WILSY-COMMERCIAL-AGREEMENT-EXECUTION/V1",
        "tenant_id": agreement.tenant_id,
        "agreement_id": agreement.agreement_id,
        "offer_id": agreement.offer_id.value,
        "offer_fingerprint": agreement.offer_fingerprint,
        "contract_reference": agreement.contract_reference,
        "contract_version": agreement.contract_version,
        "counterparty_legal_name": agreement.counterparty_legal_name,
        "effective_at": agreement.effective_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "expires_at": (
            agreement.expires_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            if agreement.expires_at else None
        ),
        "renewal_mode": agreement.renewal_mode.value,
        "notice_days": agreement.notice_days,
        "termination_terms_reference": agreement.termination_terms_reference,
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":")).encode("utf-8")


def _verify_signature(
    certificate: x509.Certificate, signature: bytes, payload: bytes, algorithm: str,
) -> None:
    public_key = certificate.public_key()
    try:
        if algorithm == "RSA-PKCS1v15-SHA256" and isinstance(public_key, rsa.RSAPublicKey):
            public_key.verify(signature, payload, padding.PKCS1v15(), hashes.SHA256())
        elif algorithm == "RSA-PSS-SHA256" and isinstance(public_key, rsa.RSAPublicKey):
            public_key.verify(
                signature, payload,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
        elif algorithm == "ECDSA-SHA256" and isinstance(public_key, ec.EllipticCurvePublicKey):
            public_key.verify(signature, payload, ec.ECDSA(hashes.SHA256()))
        else:
            raise CommercialAgreementExecutionVerificationError(
                "COMMERCIAL_EXECUTION_SIGNATURE_ALGORITHM_UNSUPPORTED"
            )
    except InvalidSignature as error:
        raise CommercialAgreementExecutionVerificationError(
            "COMMERCIAL_EXECUTION_SIGNATURE_INVALID"
        ) from error


class CommercialAgreementExecutionVerifier:
    """Compose independently trusted evidence, PKI, timestamp and mandate sources."""

    def __init__(
        self, *, evidence_store: ExecutionEvidenceStore,
        certificate_trust: SigningCertificateTrustResolver,
        mandate_resolver: SignatoryMandateResolver,
        timestamp_verifier: TrustedTimestampVerifier,
        verifier_id: str,
    ) -> None:
        if not isinstance(verifier_id, str) or not verifier_id.strip():
            raise ValueError("COMMERCIAL_EXECUTION_VERIFIER_ID_REQUIRED")
        self._evidence_store = evidence_store
        self._certificate_trust = certificate_trust
        self._mandate_resolver = mandate_resolver
        self._timestamp_verifier = timestamp_verifier
        self._verifier_id = verifier_id

    def verify(
        self, *, agreement: CommercialAgreement, evidence_reference: str,
    ) -> VerifiedCommercialAgreementExecutionEvidence:
        """Verify exact signed terms, signer trust, mandate and trusted timestamp."""
        if not isinstance(agreement, CommercialAgreement):
            raise CommercialAgreementExecutionVerificationError(
                "COMMERCIAL_EXECUTION_AGREEMENT_REQUIRED"
            )
        if not isinstance(evidence_reference, str) or not evidence_reference or evidence_reference != evidence_reference.strip():
            raise CommercialAgreementExecutionVerificationError(
                "COMMERCIAL_EXECUTION_EVIDENCE_REFERENCE_INVALID"
            )
        try:
            evidence = self._evidence_store.load(
                agreement.tenant_id, agreement.agreement_id, evidence_reference
            )
        except Exception as error:
            raise CommercialAgreementExecutionVerificationError(
                "COMMERCIAL_EXECUTION_EVIDENCE_UNAVAILABLE"
            ) from error
        if type(evidence) is not StoredCommercialExecutionEvidence:
            raise CommercialAgreementExecutionVerificationError(
                "COMMERCIAL_EXECUTION_EVIDENCE_SHAPE_INVALID"
            )
        exact = (
            evidence.tenant_id == agreement.tenant_id
            and evidence.agreement_id == agreement.agreement_id
            and evidence.evidence_reference == evidence_reference
            and evidence.contract_reference == agreement.contract_reference
            and evidence.contract_version == agreement.contract_version
            and hmac.compare_digest(evidence.offer_fingerprint, agreement.offer_fingerprint)
            and evidence.signed_document == canonical_execution_document(agreement)
            and isinstance(evidence.signature, bytes) and bool(evidence.signature)
            and isinstance(evidence.timestamp_token, bytes) and bool(evidence.timestamp_token)
        )
        if not exact:
            raise CommercialAgreementExecutionVerificationError(
                "COMMERCIAL_EXECUTION_DOCUMENT_BINDING_INVALID"
            )
        cert_fp = _fingerprint(
            evidence.signing_certificate_fingerprint,
            "COMMERCIAL_EXECUTION_CERTIFICATE_FINGERPRINT_INVALID",
        )
        payload_fp = hashlib.sha3_512(evidence.signed_document).hexdigest()
        try:
            timestamp = self._timestamp_verifier.verify(
                tenant_id=agreement.tenant_id,
                agreement_id=agreement.agreement_id,
                timestamp_token=evidence.timestamp_token,
                signed_payload_fingerprint=payload_fp,
            )
        except Exception as error:
            raise CommercialAgreementExecutionVerificationError(
                "COMMERCIAL_EXECUTION_TIMESTAMP_UNTRUSTED"
            ) from error
        if type(timestamp) is not TrustedExecutionTimestamp or not isinstance(
            timestamp.signed_at, datetime
        ) or timestamp.signed_at.tzinfo is None or timestamp.signed_at.utcoffset() is None:
            raise CommercialAgreementExecutionVerificationError(
                "COMMERCIAL_EXECUTION_TIMESTAMP_INVALID"
            )
        signed_at = timestamp.signed_at.astimezone(timezone.utc)
        timestamp_fp = _fingerprint(
            timestamp.evidence_fingerprint,
            "COMMERCIAL_EXECUTION_TIMESTAMP_FINGERPRINT_INVALID",
        )
        if not timestamp.evidence_reference:
            raise CommercialAgreementExecutionVerificationError(
                "COMMERCIAL_EXECUTION_TIMESTAMP_REFERENCE_INVALID"
            )
        try:
            trust = self._certificate_trust.resolve(
                tenant_id=agreement.tenant_id,
                principal_id=evidence.signatory_principal_id,
                certificate_fingerprint=cert_fp,
                at=signed_at,
            )
        except Exception as error:
            raise CommercialAgreementExecutionVerificationError(
                "COMMERCIAL_EXECUTION_CERTIFICATE_UNTRUSTED"
            ) from error
        if (
            type(trust) is not TrustedSigningCertificate
            or not trust.chain_valid
            or trust.revocation_status != "GOOD"
            or not trust.trust_anchor_reference
        ):
            raise CommercialAgreementExecutionVerificationError(
                "COMMERCIAL_EXECUTION_CERTIFICATE_UNTRUSTED"
            )
        try:
            certificate = x509.load_pem_x509_certificate(trust.certificate_pem)
            actual_cert_fp = certificate.fingerprint(hashes.SHA256()).hex()
            if not hmac.compare_digest(actual_cert_fp, cert_fp):
                raise ValueError("CERTIFICATE_FINGERPRINT_MISMATCH")
            if not (certificate.not_valid_before_utc <= signed_at <= certificate.not_valid_after_utc):
                raise ValueError("CERTIFICATE_OUTSIDE_VALIDITY")
            usage = certificate.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE).value
            if not usage.digital_signature:
                raise ValueError("CERTIFICATE_KEY_USAGE_INVALID")
            _verify_signature(certificate, evidence.signature, evidence.signed_document,
                              evidence.signature_algorithm)
        except CommercialAgreementExecutionVerificationError:
            raise
        except Exception as error:
            raise CommercialAgreementExecutionVerificationError(
                "COMMERCIAL_EXECUTION_CERTIFICATE_INVALID"
            ) from error
        try:
            mandate = self._mandate_resolver.resolve(
                tenant_id=agreement.tenant_id,
                agreement_id=agreement.agreement_id,
                principal_id=evidence.signatory_principal_id,
                at=signed_at,
            )
        except Exception as error:
            raise CommercialAgreementExecutionVerificationError(
                "COMMERCIAL_EXECUTION_SIGNATORY_AUTHORITY_UNAVAILABLE"
            ) from error
        if (
            type(mandate) is not VerifiedSignatoryMandate
            or not mandate.active
            or mandate.tenant_id != agreement.tenant_id
            or mandate.agreement_id != agreement.agreement_id
            or mandate.principal_id != evidence.signatory_principal_id
        ):
            raise CommercialAgreementExecutionVerificationError(
                "COMMERCIAL_EXECUTION_SIGNATORY_NOT_AUTHORIZED"
            )
        authority_fp = _fingerprint(
            mandate.authority_fingerprint,
            "COMMERCIAL_EXECUTION_SIGNATORY_AUTHORITY_FINGERPRINT_INVALID",
        )
        execution_fp = hashlib.sha3_512(
            evidence.signed_document + evidence.signature + bytes.fromhex(cert_fp)
            + timestamp.timestamp_token if hasattr(timestamp, "timestamp_token") else
            evidence.signed_document + evidence.signature + bytes.fromhex(cert_fp)
        ).hexdigest()
        receipt_payload = {
            "tenant_id": agreement.tenant_id,
            "agreement_id": agreement.agreement_id,
            "execution_evidence_reference": evidence_reference,
            "execution_evidence_fingerprint": execution_fp,
            "signatory_principal_id": evidence.signatory_principal_id,
            "signatory_authority_reference": mandate.authority_reference,
            "signatory_authority_fingerprint": authority_fp,
            "timestamp_reference": timestamp.evidence_reference,
            "timestamp_fingerprint": timestamp_fp,
            "trust_anchor_reference": trust.trust_anchor_reference,
            "trust_anchor_fingerprint": trust.trust_anchor_fingerprint,
            "verifier_id": self._verifier_id,
            "signed_at": signed_at.isoformat(),
        }
        receipt_fp = _sha3(receipt_payload)
        return VerifiedCommercialAgreementExecutionEvidence(
            tenant_id=agreement.tenant_id,
            agreement_id=agreement.agreement_id,
            contract_reference=agreement.contract_reference,
            contract_version=agreement.contract_version,
            offer_fingerprint=agreement.offer_fingerprint,
            execution_evidence_reference=evidence_reference,
            execution_evidence_fingerprint=execution_fp,
            signatory_principal_id=evidence.signatory_principal_id,
            signatory_authority_reference=mandate.authority_reference,
            signatory_authority_fingerprint=authority_fp,
            signed_at=signed_at,
            verified_at=datetime.now(timezone.utc),
            verifier_id=self._verifier_id,
            verification_receipt_reference=f"commercial-execution-verification:{receipt_fp[:48]}",
            verification_receipt_fingerprint=receipt_fp,
        )


__all__ = [
    "CommercialAgreementExecutionVerificationError",
    "CommercialAgreementExecutionVerifier",
    "StoredCommercialExecutionEvidence",
    "TrustedExecutionTimestamp",
    "TrustedSigningCertificate",
    "VerifiedSignatoryMandate",
    "canonical_execution_document",
]
