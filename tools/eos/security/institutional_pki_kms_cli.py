"""Provision a non-exportable KMS subordinate CA key and publish its CRL.

Run on an approved online KMS administration host. Transfer only the CSR to
the offline root ceremony. The KMS private key never leaves AWS KMS.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from .institutional_pki_kms import (
    InstitutionalPKIKMSError,
    create_nonexportable_subordinate_ca_key_and_csr,
    issue_crl_with_kms,
)


def _write_once(path: Path, payload: bytes, mode: int) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise


def _provision(args: argparse.Namespace) -> int:
    output = Path(args.output_dir).expanduser().resolve()
    output.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(output, 0o700)
    csr_path = output / "institutional-subordinate-ca.csr.pem"
    reference_path = output / "institutional-subordinate-ca-kms-reference.json"
    if csr_path.exists() or reference_path.exists():
        raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_OUTPUT_ALREADY_EXISTS")
    policy = Path(args.key_policy).expanduser().read_text(encoding="utf-8")
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    client = session.client("kms", region_name=args.region)
    result = create_nonexportable_subordinate_ca_key_and_csr(
        client,
        region=args.region,
        key_policy_json=policy,
        common_name=args.common_name,
        organization=args.organization,
        organizational_unit=args.organizational_unit,
        country_code=args.country_code,
    )
    reference = {
        "schema": "wilsy.institutional_pki.kms_subordinate_key_reference.v1",
        "key_arn": result.key_arn,
        "region": result.region,
        "subject_common_name": result.subject_common_name,
        "public_key_fingerprint_sha256": result.public_key_fingerprint_sha256,
        "signing_algorithm": result.signing_algorithm,
        "created_at": result.created_at.isoformat(),
        "private_key_exportable": False,
        "private_key_material_included": False,
    }
    _write_once(
        reference_path,
        (json.dumps(reference, sort_keys=True, indent=2) + "\n").encode("utf-8"),
        0o600,
    )
    _write_once(csr_path, result.csr_pem, 0o644)
    print(f"kms_key_arn={result.key_arn}")
    print(f"kms_key_reference={reference_path}")
    print(f"subordinate_csr={csr_path}")
    print(f"public_key_sha256={result.public_key_fingerprint_sha256}")
    print("PRIVATE KEY REMAINS NON-EXPORTABLE INSIDE KMS; TRANSFER ONLY THE CSR TO THE OFFLINE ROOT CEREMONY.")
    return 0


def _publish_crl(args: argparse.Namespace) -> int:
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    client = session.client("kms", region_name=args.region)
    path, fingerprint = issue_crl_with_kms(
        client,
        key_arn=args.key_arn,
        issuer_certificate_pem=Path(args.issuer_certificate).read_bytes(),
        output_path=Path(args.output),
        revoked_serial_numbers=args.revoke_serial,
        crl_number=args.crl_number,
        validity_hours=args.validity_hours,
    )
    print(f"crl={path}")
    print(f"crl_sha256={fingerprint}")
    print("CRL SIGNED BY THE NON-EXPORTABLE KMS SUBORDINATE KEY; REVIEW AND PUBLISH THE COMPLETE ISSUER BUNDLE.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.eos.security.institutional_pki_kms_cli",
        description="Non-exportable KMS subordinate CA key and CRL operations.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    provision = commands.add_parser("provision-subordinate-csr")
    provision.add_argument("--region", required=True)
    provision.add_argument("--profile")
    provision.add_argument("--key-policy", required=True)
    provision.add_argument("--output-dir", required=True)
    provision.add_argument("--common-name", required=True)
    provision.add_argument("--organization", required=True)
    provision.add_argument("--organizational-unit", required=True)
    provision.add_argument("--country-code", required=True)
    provision.set_defaults(handler=_provision)

    publish = commands.add_parser("publish-crl")
    publish.add_argument("--region", required=True)
    publish.add_argument("--profile")
    publish.add_argument("--key-arn", required=True)
    publish.add_argument("--issuer-certificate", required=True)
    publish.add_argument("--output", required=True)
    publish.add_argument("--revoke-serial", type=lambda value: int(value, 0), action="append", default=[])
    publish.add_argument("--crl-number", type=int, required=True)
    publish.add_argument("--validity-hours", type=int, default=24)
    publish.set_defaults(handler=_publish_crl)

    args = parser.parse_args()
    try:
        return args.handler(args)
    except InstitutionalPKIKMSError as error:
        print(error.code, file=sys.stderr)
        if error.key_arn:
            print(f"created_kms_key_requires_reconciliation={error.key_arn}", file=sys.stderr)
        return 2
    except (OSError, ValueError, BotoCoreError, ClientError) as error:
        del error
        print("INSTITUTIONAL_KMS_PROVISIONING_FAILED", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
