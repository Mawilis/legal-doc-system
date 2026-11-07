"""Offline WILSY EOS private-CA provisioning ceremony helpers.

The root private key is encrypted and must remain offline. This module is
intentionally a command-line provisioning utility, not an application-startup
key generator. A self-created private CA is not externally accredited by this
software; legal/governance approval and operational key custody are separate.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import re
from typing import Iterable

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from .institutional_pki import InstitutionalPKIError


def _safe_component(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip(".-")
    if not normalized or normalized in {".", ".."}:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_NAME_INVALID")
    return normalized[:80]


def _write_private(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise


def _write_public(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise


def _name(common_name: str, organization: str) -> x509.Name:
    return x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])


def create_offline_root(
    *,
    output_directory: Path,
    common_name: str,
    organization: str,
    passphrase: bytes,
    validity_days: int = 3650,
) -> tuple[Path, Path, str]:
    """Create an encrypted RSA-4096 root key and self-signed CA certificate."""
    if not isinstance(passphrase, bytes) or len(passphrase) < 16:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_ROOT_PASSPHRASE_TOO_WEAK")
    if type(validity_days) is not int or not 365 <= validity_days <= 7300:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_ROOT_VALIDITY_INVALID")
    directory = output_directory.expanduser().resolve()
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(directory, 0o700)
    stem = _safe_component(common_name)
    key_path = directory / f"{stem}-root-key.pem"
    cert_path = directory / f"{stem}-root-cert.pem"
    if key_path.exists() or cert_path.exists():
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_OUTPUT_ALREADY_EXISTS")
    key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    now = datetime.now(timezone.utc)
    name = _name(common_name, organization)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(now + timedelta(days=validity_days))
        .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=False, content_commitment=False, key_encipherment=False,
            data_encipherment=False, key_agreement=False, key_cert_sign=True,
            crl_sign=True, encipher_only=False, decipher_only=False,
        ), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .sign(key, hashes.SHA384())
    )
    encrypted = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(passphrase),
    )
    try:
        _write_private(key_path, encrypted)
        _write_public(cert_path, cert.public_bytes(serialization.Encoding.PEM))
    except Exception:
        key_path.unlink(missing_ok=True)
        cert_path.unlink(missing_ok=True)
        raise
    os.chmod(directory, 0o700)
    return key_path, cert_path, cert.fingerprint(hashes.SHA256()).hex()


def issue_intermediate(
    *,
    root_certificate_pem: Path,
    root_private_key_pem: Path,
    root_passphrase: bytes,
    output_directory: Path,
    common_name: str,
    organization: str,
    validity_days: int = 1825,
) -> tuple[Path, Path, str]:
    """Issue an encrypted RSA-3072 subordinate CA from the offline root."""
    if type(validity_days) is not int or not 90 <= validity_days <= 3650:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_INTERMEDIATE_VALIDITY_INVALID")
    try:
        root = x509.load_pem_x509_certificate(root_certificate_pem.read_bytes())
        root_key = serialization.load_pem_private_key(
            root_private_key_pem.read_bytes(), password=root_passphrase
        )
    except Exception as error:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_ROOT_KEY_OR_CERTIFICATE_INVALID") from error
    if not isinstance(root_key, rsa.RSAPrivateKey):
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_ROOT_KEY_ALGORITHM_INVALID")
    if root.public_key().public_numbers() != root_key.public_key().public_numbers():
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_ROOT_KEY_MISMATCH")
    root_constraints = root.extensions.get_extension_for_class(x509.BasicConstraints).value
    if not root_constraints.ca or root_constraints.path_length != 1:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_ROOT_CA_PROFILE_INVALID")
    directory = output_directory.expanduser().resolve()
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(directory, 0o700)
    stem = _safe_component(common_name)
    key_path = directory / f"{stem}-intermediate-key.pem"
    cert_path = directory / f"{stem}-intermediate-cert.pem"
    if key_path.exists() or cert_path.exists():
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_OUTPUT_ALREADY_EXISTS")
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(_name(common_name, organization))
        .issuer_name(root.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(min(now + timedelta(days=validity_days), root.not_valid_after_utc))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=False, content_commitment=False, key_encipherment=False,
            data_encipherment=False, key_agreement=False, key_cert_sign=True,
            crl_sign=True, encipher_only=False, decipher_only=False,
        ), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()), critical=False)
        .sign(root_key, hashes.SHA384())
    )
    encrypted = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(root_passphrase),
    )
    try:
        _write_private(key_path, encrypted)
        _write_public(cert_path, cert.public_bytes(serialization.Encoding.PEM))
    except Exception:
        key_path.unlink(missing_ok=True)
        cert_path.unlink(missing_ok=True)
        raise
    return key_path, cert_path, cert.fingerprint(hashes.SHA256()).hex()


def issue_crl(
    *,
    issuer_certificate_pem: Path,
    issuer_private_key_pem: Path,
    issuer_passphrase: bytes,
    output_path: Path,
    revoked_serial_numbers: Iterable[int] = (),
    validity_hours: int = 24,
) -> tuple[Path, str]:
    """Publish a bounded-lifetime CRL signed by the exact configured issuer."""
    if type(validity_hours) is not int or not 1 <= validity_hours <= 168:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_CRL_VALIDITY_INVALID")
    try:
        issuer = x509.load_pem_x509_certificate(issuer_certificate_pem.read_bytes())
        key = serialization.load_pem_private_key(
            issuer_private_key_pem.read_bytes(), password=issuer_passphrase
        )
    except Exception as error:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_ISSUER_KEY_OR_CERTIFICATE_INVALID") from error
    if issuer.public_key().public_numbers() != key.public_key().public_numbers():
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_ISSUER_KEY_MISMATCH")
    constraints = issuer.extensions.get_extension_for_class(x509.BasicConstraints).value
    usage = issuer.extensions.get_extension_for_class(x509.KeyUsage).value
    if not constraints.ca or not usage.crl_sign:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_ISSUER_CANNOT_SIGN_CRL")
    now = datetime.now(timezone.utc)
    builder = (
        x509.CertificateRevocationListBuilder()
        .issuer_name(issuer.subject)
        .last_update(now - timedelta(minutes=1))
        .next_update(now + timedelta(hours=validity_hours))
    )
    seen: set[int] = set()
    for serial in revoked_serial_numbers:
        if type(serial) is not int or serial <= 0 or serial in seen:
            raise InstitutionalPKIError("INSTITUTIONAL_PKI_REVOKED_SERIAL_INVALID")
        seen.add(serial)
        revoked = (
            x509.RevokedCertificateBuilder()
            .serial_number(serial)
            .revocation_date(now)
            .build()
        )
        builder = builder.add_revoked_certificate(revoked)
    crl = builder.sign(private_key=key, algorithm=hashes.SHA384())
    target = output_path.expanduser().resolve()
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    _write_public(target, crl.public_bytes(serialization.Encoding.PEM))
    return target, crl.fingerprint(hashes.SHA256()).hex()
