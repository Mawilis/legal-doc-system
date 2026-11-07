"""Fail-closed institutional PKI trust and X.509 revocation runtime.

Trust anchors are provisioned out-of-band by a controlled offline ceremony.
This module never creates or silently trusts a root, never downloads trust
material, and never treats a self-signed certificate as trusted merely because
it is presented by a caller. CRLs are mandatory for every issuing CA in the
validated path. Verification receipts are technical evidence only; they do
not establish legal authority, accreditation, or a signatory mandate.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import os
from pathlib import Path
import re
from threading import RLock
from typing import Iterable

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import dsa, ec, ed25519, ed448, padding, rsa
from cryptography.x509.oid import ExtensionOID, ExtendedKeyUsageOID, ObjectIdentifier


class InstitutionalPKIError(RuntimeError):
    """Stable, content-free PKI configuration or verification failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class InstitutionalPKISettings:
    trust_anchors_pem: Path
    issuer_certificates_pem: Path
    crl_bundle_pem: Path
    trusted_root_sha256: frozenset[str]
    required_eku_oid: str
    max_chain_depth: int = 8
    max_crl_age_seconds: int = 86_400

    def __post_init__(self) -> None:
        if not self.trusted_root_sha256:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_TRUSTED_ROOT_FINGERPRINTS_REQUIRED")
        for value in self.trusted_root_sha256:
            if not re.fullmatch(r"[0-9a-f]{64}", value):
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_ROOT_FINGERPRINT_INVALID")
        if not re.fullmatch(r"[0-2](?:\.(?:0|[1-9][0-9]*))+", self.required_eku_oid):
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_REQUIRED_EKU_INVALID")
        try:
            ObjectIdentifier(self.required_eku_oid)
        except ValueError as error:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_REQUIRED_EKU_INVALID") from error
        if type(self.max_chain_depth) is not int or not 1 <= self.max_chain_depth <= 16:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_CHAIN_DEPTH_INVALID")
        if type(self.max_crl_age_seconds) is not int or not 60 <= self.max_crl_age_seconds <= 604800:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_AGE_POLICY_INVALID")


@dataclass(frozen=True, slots=True)
class InstitutionalCertificateVerification:
    leaf_fingerprint_sha256: str
    root_fingerprint_sha256: str
    issuer_common_name: str
    serial_number_hex: str
    verified_at: datetime
    chain_depth: int
    revocation_sources: tuple[str, ...]
    verification_fingerprint: str


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_TIME_MUST_BE_AWARE")
    return value.astimezone(timezone.utc)


def _pem_certificates(raw: bytes) -> tuple[x509.Certificate, ...]:
    blocks = re.findall(
        rb"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
        raw,
        flags=re.DOTALL,
    )
    if not blocks:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_CERTIFICATE_BUNDLE_EMPTY")
    try:
        return tuple(x509.load_pem_x509_certificate(block) for block in blocks)
    except Exception as error:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_CERTIFICATE_BUNDLE_INVALID") from error


def _pem_crls(raw: bytes) -> tuple[x509.CertificateRevocationList, ...]:
    blocks = re.findall(
        rb"-----BEGIN X509 CRL-----.*?-----END X509 CRL-----",
        raw,
        flags=re.DOTALL,
    )
    if not blocks:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_BUNDLE_EMPTY")
    try:
        return tuple(x509.load_pem_x509_crl(block) for block in blocks)
    except Exception as error:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_BUNDLE_INVALID") from error


def _verify_signature(signed_object: object, issuer_key: object) -> None:
    try:
        signature = signed_object.signature
        data = signed_object.tbs_certificate_bytes if isinstance(signed_object, x509.Certificate) else signed_object.tbs_certlist_bytes
        algorithm = signed_object.signature_hash_algorithm
        if isinstance(issuer_key, rsa.RSAPublicKey):
            oid = signed_object.signature_algorithm_oid.dotted_string
            # RSA-PSS requires parameter-aware verification; reject rather than
            # silently treating it as PKCS#1 v1.5.
            if oid == "1.2.840.113549.1.1.10":
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_RSA_PSS_NOT_SUPPORTED")
            issuer_key.verify(signature, data, padding.PKCS1v15(), algorithm)
        elif isinstance(issuer_key, ec.EllipticCurvePublicKey):
            issuer_key.verify(signature, data, ec.ECDSA(algorithm))
        elif isinstance(issuer_key, dsa.DSAPublicKey):
            issuer_key.verify(signature, data, algorithm)
        elif isinstance(issuer_key, (ed25519.Ed25519PublicKey, ed448.Ed448PublicKey)):
            issuer_key.verify(signature, data)
        else:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_ISSUER_KEY_ALGORITHM_UNSUPPORTED")
    except InstitutionalPKIError:
        raise
    except Exception as error:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_CERTIFICATE_SIGNATURE_INVALID") from error


def _extension(cert: x509.Certificate, oid: x509.ObjectIdentifier, code: str):
    try:
        return cert.extensions.get_extension_for_oid(oid).value
    except x509.ExtensionNotFound as error:
        raise InstitutionalPKIError(code) from error


def _is_ca(cert: x509.Certificate) -> x509.BasicConstraints:
    constraints = _extension(cert, ExtensionOID.BASIC_CONSTRAINTS, "INSTITUTIONAL_PKI_CA_CONSTRAINTS_MISSING")
    if not constraints.ca:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_ISSUER_NOT_CA")
    usage = _extension(cert, ExtensionOID.KEY_USAGE, "INSTITUTIONAL_PKI_CA_KEY_USAGE_MISSING")
    if not usage.key_cert_sign or not usage.crl_sign:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_CA_KEY_USAGE_INVALID")
    return constraints


def _valid_at(cert: x509.Certificate, instant: datetime) -> None:
    not_before = cert.not_valid_before_utc if hasattr(cert, "not_valid_before_utc") else cert.not_valid_before.replace(tzinfo=timezone.utc)
    not_after = cert.not_valid_after_utc if hasattr(cert, "not_valid_after_utc") else cert.not_valid_after.replace(tzinfo=timezone.utc)
    if instant < not_before or instant >= not_after:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_CERTIFICATE_OUTSIDE_VALIDITY")


def _subject_common_name(cert: x509.Certificate) -> str:
    values = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
    return values[0].value if values else "UNNAMED_ISSUER"


class InstitutionalPKIVerifier:
    """Immutable trust-anchor and CRL snapshot for one EOS process lifetime."""

    def __init__(
        self,
        *,
        anchors: Iterable[x509.Certificate],
        crls: Iterable[x509.CertificateRevocationList],
        settings: InstitutionalPKISettings,
        issuer_certificates: Iterable[x509.Certificate] = (),
    ) -> None:
        self._settings = settings
        self._crl_bundle_path = settings.crl_bundle_pem
        self._crls_lock = RLock()
        self._crl_number_high_water: dict[str, tuple[int, str]] = {}
        self._anchors = tuple(anchors)
        self._issuer_certificates = tuple(issuer_certificates) + self._anchors
        self._crls = tuple(crls)
        if not self._anchors or not self._crls:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_TRUST_AND_CRL_REQUIRED")
        fingerprints = {item.fingerprint(hashes.SHA256()).hex() for item in self._anchors}
        if fingerprints != set(settings.trusted_root_sha256):
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_ROOT_PIN_SET_MISMATCH")
        anchor_fingerprints = {item.fingerprint(hashes.SHA256()) for item in self._anchors}
        for anchor in self._anchors:
            _valid_at(anchor, datetime.now(timezone.utc))
            _is_ca(anchor)
            if anchor.subject != anchor.issuer:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_ROOT_NOT_SELF_ISSUED")
            _verify_signature(anchor, anchor.public_key())
        issuer_fingerprints = {item.fingerprint(hashes.SHA256()) for item in self._issuer_certificates}
        if len(issuer_fingerprints) != len(self._issuer_certificates):
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_ISSUER_CERTIFICATE_DUPLICATE")
        configured_intermediates = tuple(
            item for item in self._issuer_certificates
            if item.fingerprint(hashes.SHA256()) not in anchor_fingerprints
        )
        for issuer_certificate in configured_intermediates:
            _valid_at(issuer_certificate, datetime.now(timezone.utc))
            _is_ca(issuer_certificate)
            current = issuer_certificate
            visited = {current.fingerprint(hashes.SHA256())}
            for _ in range(settings.max_chain_depth):
                parents = [
                    item for item in self._issuer_certificates
                    if current.issuer == item.subject
                    and item.fingerprint(hashes.SHA256()) not in visited
                ]
                if len(parents) != 1:
                    raise InstitutionalPKIError("INSTITUTIONAL_PKI_CONFIGURED_ISSUER_CHAIN_INVALID")
                parent = parents[0]
                _valid_at(parent, datetime.now(timezone.utc))
                constraints = _is_ca(parent)
                _verify_signature(current, parent.public_key())
                visited.add(parent.fingerprint(hashes.SHA256()))
                if parent.fingerprint(hashes.SHA256()) in anchor_fingerprints:
                    break
                if constraints.path_length is not None:
                    subordinate_count = sum(
                        1 for fingerprint in visited
                        if fingerprint not in anchor_fingerprints
                    )
                    if subordinate_count > constraints.path_length:
                        raise InstitutionalPKIError("INSTITUTIONAL_PKI_CONFIGURED_ISSUER_PATH_LENGTH_EXCEEDED")
                current = parent
            else:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_CONFIGURED_ISSUER_CHAIN_DEPTH_EXCEEDED")
        self._validate_crls(self._crls)

    def _validate_crls(self, crls: tuple[x509.CertificateRevocationList, ...]) -> None:
        if not crls:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_BUNDLE_EMPTY")
        observed: dict[str, tuple[int, str]] = {}
        now = datetime.now(timezone.utc)
        for crl in crls:
            issuers = [item for item in self._issuer_certificates if item.subject == crl.issuer]
            if len(issuers) != 1:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_ISSUER_NOT_FOUND_OR_AMBIGUOUS")
            issuer = issuers[0]
            issuer_reference = sha256(issuer.subject.public_bytes()).hexdigest()
            if issuer_reference in observed:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_DUPLICATE_ISSUER")
            try:
                crl.extensions.get_extension_for_class(x509.DeltaCRLIndicator)
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_DELTA_CRL_NOT_SUPPORTED")
            except x509.ExtensionNotFound:
                pass
            try:
                distribution = crl.extensions.get_extension_for_class(x509.IssuingDistributionPoint).value
                if distribution.indirect_crl:
                    raise InstitutionalPKIError("INSTITUTIONAL_PKI_INDIRECT_CRL_NOT_SUPPORTED")
            except x509.ExtensionNotFound:
                pass
            _verify_signature(crl, issuer.public_key())
            try:
                crl_authority_key_id = crl.extensions.get_extension_for_class(x509.AuthorityKeyIdentifier).value.key_identifier
            except x509.ExtensionNotFound:
                crl_authority_key_id = None
            try:
                issuer_subject_key_id = issuer.extensions.get_extension_for_class(x509.SubjectKeyIdentifier).value.digest
            except x509.ExtensionNotFound:
                issuer_subject_key_id = None
            if crl_authority_key_id is not None and issuer_subject_key_id is not None and crl_authority_key_id != issuer_subject_key_id:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_AUTHORITY_KEY_IDENTIFIER_MISMATCH")
            try:
                number = crl.extensions.get_extension_for_class(x509.CRLNumber).value.crl_number
            except x509.ExtensionNotFound as error:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_NUMBER_REQUIRED") from error
            this_update = crl.last_update_utc if hasattr(crl, "last_update_utc") else crl.last_update.replace(tzinfo=timezone.utc)
            next_update = crl.next_update_utc if hasattr(crl, "next_update_utc") else crl.next_update.replace(tzinfo=timezone.utc) if crl.next_update else None
            if next_update is None or this_update > now or next_update <= now:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_NOT_CURRENT")
            if (now - this_update).total_seconds() > self._settings.max_crl_age_seconds:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_TOO_OLD")
            observed[issuer_reference] = (number, crl.fingerprint(hashes.SHA256()).hex())
        expected_issuers = {
            sha256(item.subject.public_bytes()).hexdigest()
            for item in self._issuer_certificates
        }
        if set(observed) != expected_issuers:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_SET_INCOMPLETE")
        for issuer_reference, (number, fingerprint) in observed.items():
            previous = self._crl_number_high_water.get(issuer_reference)
            if previous is not None and (
                number < previous[0] or (number == previous[0] and fingerprint != previous[1])
            ):
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_ROLLBACK_OR_NUMBER_REUSE")
        self._crl_number_high_water.update(observed)

    def refresh_crls(self) -> tuple[x509.CertificateRevocationList, ...]:
        """Atomically reload the externally published CRL bundle on each use."""
        if self._crl_bundle_path is None:
            return self._crls
        try:
            current = _pem_crls(self._crl_bundle_path.read_bytes())
        except OSError as error:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_BUNDLE_UNAVAILABLE") from error
        self._validate_crls(current)
        with self._crls_lock:
            self._crls = current
            return self._crls

    @classmethod
    def from_settings(cls, settings: InstitutionalPKISettings) -> "InstitutionalPKIVerifier":
        try:
            anchors = _pem_certificates(settings.trust_anchors_pem.read_bytes())
            issuers = _pem_certificates(settings.issuer_certificates_pem.read_bytes())
            crls = _pem_crls(settings.crl_bundle_pem.read_bytes())
        except OSError as error:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_TRUST_MATERIAL_UNAVAILABLE") from error
        return cls(anchors=anchors, crls=crls, settings=settings, issuer_certificates=issuers)

    @classmethod
    def from_environment(cls) -> "InstitutionalPKIVerifier":
        anchors_path = os.getenv("WILSY_EOS_PKI_TRUST_ANCHORS_PEM", "").strip()
        issuer_path = os.getenv("WILSY_EOS_PKI_ISSUER_CERTIFICATES_PEM", "").strip()
        crl_path = os.getenv("WILSY_EOS_PKI_CRL_BUNDLE_PEM", "").strip()
        fingerprints = os.getenv("WILSY_EOS_PKI_TRUSTED_ROOT_SHA256", "").strip()
        eku = os.getenv("WILSY_EOS_PKI_REQUIRED_SIGNING_EKU_OID", "").strip()
        if not all((anchors_path, issuer_path, crl_path, fingerprints, eku)):
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_RUNTIME_CONFIGURATION_INCOMPLETE")
        pins = frozenset(value.strip().lower() for value in fingerprints.split(",") if value.strip())
        try:
            max_chain_depth = int(os.getenv("WILSY_EOS_PKI_MAX_CHAIN_DEPTH", "8"))
            max_crl_age_seconds = int(os.getenv("WILSY_EOS_PKI_MAX_CRL_AGE_SECONDS", "86400"))
        except ValueError as error:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_NUMERIC_POLICY_CONFIGURATION_INVALID") from error
        return cls.from_settings(InstitutionalPKISettings(
            trust_anchors_pem=Path(anchors_path),
            issuer_certificates_pem=Path(issuer_path),
            crl_bundle_pem=Path(crl_path),
            trusted_root_sha256=pins,
            required_eku_oid=eku,
            max_chain_depth=max_chain_depth,
            max_crl_age_seconds=max_crl_age_seconds,
        ))

    def crl_der_for_issuer_subject_sha256(self, issuer_subject_sha256: str) -> bytes:
        """Return one currently valid DER CRL selected by issuer subject fingerprint."""
        if not re.fullmatch(r"[0-9a-f]{64}", issuer_subject_sha256):
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_ISSUER_REFERENCE_INVALID")
        crls = self.refresh_crls()
        matches = [
            crl for crl in crls
            if sha256(crl.issuer.public_bytes()).hexdigest() == issuer_subject_sha256
        ]
        if len(matches) != 1:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_ISSUER_NOT_FOUND_OR_AMBIGUOUS")
        crl = matches[0]
        issuer = next((item for item in self._issuer_certificates if item.subject == crl.issuer), None)
        if issuer is None:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_ISSUER_NOT_FOUND_OR_AMBIGUOUS")
        _verify_signature(crl, issuer.public_key())
        this_update = crl.last_update_utc if hasattr(crl, "last_update_utc") else crl.last_update.replace(tzinfo=timezone.utc)
        next_update = crl.next_update_utc if hasattr(crl, "next_update_utc") else crl.next_update.replace(tzinfo=timezone.utc) if crl.next_update else None
        now = datetime.now(timezone.utc)
        if next_update is None or this_update > now or next_update <= now:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_NOT_CURRENT")
        return crl.public_bytes(serialization.Encoding.DER)

    def verify(
        self,
        *,
        leaf_pem: bytes,
        intermediate_pems: Iterable[bytes],
        verified_at: datetime,
    ) -> InstitutionalCertificateVerification:
        instant = _utc(verified_at)
        current_crls = self.refresh_crls()
        try:
            leaf = x509.load_pem_x509_certificate(leaf_pem)
            supplied = tuple(x509.load_pem_x509_certificate(item) for item in intermediate_pems)
        except Exception as error:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_PRESENTED_CERTIFICATE_INVALID") from error
        _valid_at(leaf, instant)
        eku = _extension(leaf, ExtensionOID.EXTENDED_KEY_USAGE, "INSTITUTIONAL_PKI_SIGNING_EKU_MISSING")
        required_oid = ObjectIdentifier(self._settings.required_eku_oid)
        if required_oid not in eku:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_SIGNING_EKU_MISMATCH")
        usage = _extension(leaf, ExtensionOID.KEY_USAGE, "INSTITUTIONAL_PKI_LEAF_KEY_USAGE_MISSING")
        if not usage.digital_signature:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_LEAF_KEY_USAGE_INVALID")
        if _is_ca_leaf(leaf):
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_SIGNER_CERTIFICATE_IS_CA")

        anchor_fingerprints = {item.fingerprint(hashes.SHA256()) for item in self._anchors}
        supplied_fingerprints = {item.fingerprint(hashes.SHA256()) for item in supplied}
        configured_intermediate_fingerprints = {
            item.fingerprint(hashes.SHA256()) for item in self._issuer_certificates
            if item.fingerprint(hashes.SHA256()) not in anchor_fingerprints
        }
        if (
            len(supplied_fingerprints) != len(supplied)
            or supplied_fingerprints & anchor_fingerprints
            or not supplied_fingerprints.issubset(configured_intermediate_fingerprints)
        ):
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_PRESENTED_CHAIN_NOT_IN_CONFIGURED_ISSUERS")
        candidates = supplied + self._anchors
        chain = [leaf]
        current = leaf
        seen = {leaf.fingerprint(hashes.SHA256())}
        root: x509.Certificate | None = None
        for _ in range(self._settings.max_chain_depth):
            matching_issuers = [
                candidate for candidate in candidates
                if current.issuer == candidate.subject
                and candidate.fingerprint(hashes.SHA256()) not in seen
            ]
            if len(matching_issuers) != 1:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_CHAIN_ISSUER_NOT_FOUND_OR_AMBIGUOUS")
            issuer = matching_issuers[0]
            try:
                authority_key_id = current.extensions.get_extension_for_class(x509.AuthorityKeyIdentifier).value.key_identifier
            except x509.ExtensionNotFound:
                authority_key_id = None
            try:
                subject_key_id = issuer.extensions.get_extension_for_class(x509.SubjectKeyIdentifier).value.digest
            except x509.ExtensionNotFound:
                subject_key_id = None
            if authority_key_id is not None and subject_key_id is not None and authority_key_id != subject_key_id:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_AUTHORITY_KEY_IDENTIFIER_MISMATCH")
            _valid_at(issuer, instant)
            constraints = _is_ca(issuer)
            _verify_signature(current, issuer.public_key())
            seen.add(issuer.fingerprint(hashes.SHA256()))
            chain.append(issuer)
            if issuer in self._anchors:
                root = issuer
                break
            if constraints.path_length is not None:
                subordinate_ca_count = sum(
                    1 for item in chain[1:-1]
                    if _is_ca(item).ca
                )
                if subordinate_ca_count > constraints.path_length:
                    raise InstitutionalPKIError("INSTITUTIONAL_PKI_PATH_LENGTH_EXCEEDED")
            current = issuer
        if root is None:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_CHAIN_DEPTH_EXCEEDED")
        if not supplied_fingerprints.issubset(seen):
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_UNRELATED_CHAIN_CERTIFICATE_PRESENTED")

        revocation_sources: list[str] = []
        for child, issuer in zip(chain[:-1], chain[1:]):
            matching = [
                crl for crl in current_crls
                if crl.issuer == issuer.subject
            ]
            if len(matching) != 1:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_ISSUER_CRL_MISSING_OR_AMBIGUOUS")
            crl = matching[0]
            try:
                crl.extensions.get_extension_for_class(x509.DeltaCRLIndicator)
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_DELTA_CRL_NOT_SUPPORTED")
            except x509.ExtensionNotFound:
                pass
            try:
                distribution = crl.extensions.get_extension_for_class(x509.IssuingDistributionPoint).value
                if distribution.indirect_crl:
                    raise InstitutionalPKIError("INSTITUTIONAL_PKI_INDIRECT_CRL_NOT_SUPPORTED")
            except x509.ExtensionNotFound:
                pass
            try:
                crl_authority_key_id = crl.extensions.get_extension_for_class(x509.AuthorityKeyIdentifier).value.key_identifier
            except x509.ExtensionNotFound:
                crl_authority_key_id = None
            try:
                issuer_subject_key_id = issuer.extensions.get_extension_for_class(x509.SubjectKeyIdentifier).value.digest
            except x509.ExtensionNotFound:
                issuer_subject_key_id = None
            if crl_authority_key_id is not None and issuer_subject_key_id is not None and crl_authority_key_id != issuer_subject_key_id:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_AUTHORITY_KEY_IDENTIFIER_MISMATCH")
            _verify_signature(crl, issuer.public_key())
            this_update = crl.last_update_utc if hasattr(crl, "last_update_utc") else crl.last_update.replace(tzinfo=timezone.utc)
            next_update = crl.next_update_utc if hasattr(crl, "next_update_utc") else crl.next_update.replace(tzinfo=timezone.utc) if crl.next_update else None
            if next_update is None or this_update > instant or next_update <= instant:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_NOT_CURRENT")
            if (instant - this_update).total_seconds() > self._settings.max_crl_age_seconds:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_TOO_OLD")
            if crl.get_revoked_certificate_by_serial_number(child.serial_number) is not None:
                raise InstitutionalPKIError("INSTITUTIONAL_PKI_CERTIFICATE_REVOKED")
            revocation_sources.append(f"CRL:{issuer.fingerprint(hashes.SHA256()).hex()}")

        leaf_fingerprint = leaf.fingerprint(hashes.SHA256()).hex()
        root_fingerprint = root.fingerprint(hashes.SHA256()).hex()
        issuer_name = _subject_common_name(chain[1])
        material = "|".join((
            leaf_fingerprint, root_fingerprint, format(leaf.serial_number, "x"),
            instant.isoformat(), *revocation_sources,
        )).encode()
        return InstitutionalCertificateVerification(
            leaf_fingerprint_sha256=leaf_fingerprint,
            root_fingerprint_sha256=root_fingerprint,
            issuer_common_name=issuer_name,
            serial_number_hex=format(leaf.serial_number, "x"),
            verified_at=instant,
            chain_depth=len(chain) - 1,
            revocation_sources=tuple(revocation_sources),
            verification_fingerprint=sha256(material).hexdigest(),
        )


def _is_ca_leaf(cert: x509.Certificate) -> bool:
    try:
        return cert.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS).value.ca
    except x509.ExtensionNotFound:
        return False
