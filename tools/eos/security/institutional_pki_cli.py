"""Offline command-line ceremony for the WILSY EOS institutional private PKI.

Run only on an offline, access-controlled administration host. Never run this
module in the EOS web process or CI. Private keys are encrypted at rest and
created with restrictive filesystem permissions.
"""
from __future__ import annotations

import argparse
from getpass import getpass
from pathlib import Path
import sys

from .institutional_pki import InstitutionalPKIError
from .institutional_pki_provisioning import (
    create_offline_root,
    issue_crl,
    issue_intermediate,
)


def _passphrase() -> bytes:
    first = getpass("Private-key passphrase: ")
    second = getpass("Confirm passphrase: ")
    if first != second:
        raise InstitutionalPKIError("INSTITUTIONAL_PKI_PASSPHRASE_CONFIRMATION_MISMATCH")
    return first.encode("utf-8")


def _root(args: argparse.Namespace) -> None:
    key, cert, fingerprint = create_offline_root(
        output_directory=Path(args.output_dir),
        common_name=args.common_name,
        organization=args.organization,
        passphrase=_passphrase(),
        crl_distribution_base_url=args.crl_base_url,
        validity_days=args.validity_days,
    )
    print(f"root_certificate={cert}")
    print(f"encrypted_root_private_key={key}")
    print(f"trusted_root_sha256={fingerprint}")
    print("ROOT PRIVATE KEY MUST REMAIN OFFLINE; NO TRUST IS ACTIVE UNTIL GOVERNED DEPLOYMENT.")


def _intermediate(args: argparse.Namespace) -> None:
    password = getpass("Offline root-key passphrase: ").encode("utf-8")
    key, cert, fingerprint = issue_intermediate(
        root_certificate_pem=Path(args.root_certificate),
        root_private_key_pem=Path(args.root_private_key),
        root_passphrase=password,
        output_directory=Path(args.output_dir),
        common_name=args.common_name,
        organization=args.organization,
        crl_distribution_base_url=args.crl_base_url,
        validity_days=args.validity_days,
    )
    print(f"intermediate_certificate={cert}")
    print(f"encrypted_intermediate_private_key={key}")
    print(f"intermediate_sha256={fingerprint}")
    print("STORE THE ROOT KEY OFFLINE; DEPLOY ONLY THE APPROVED INTERMEDIATE KEY TO AN HSM/KEY SERVICE.")


def _crl(args: argparse.Namespace) -> None:
    password = getpass("Issuer private-key passphrase: ").encode("utf-8")
    path, fingerprint = issue_crl(
        issuer_certificate_pem=Path(args.issuer_certificate),
        issuer_private_key_pem=Path(args.issuer_private_key),
        issuer_passphrase=password,
        output_path=Path(args.output),
        revoked_serial_numbers=args.revoke_serial,
        crl_number=args.crl_number,
        validity_hours=args.validity_hours,
    )
    print(f"crl_bundle={path}")
    print(f"crl_sha256={fingerprint}")
    print("PUBLISH ONLY AFTER REVIEWING THE REVOCATION CHANGE AND VERIFYING THE ISSUER SCOPE.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.eos.security.institutional_pki_cli")
    commands = parser.add_subparsers(dest="command", required=True)
    root = commands.add_parser("init-root", help="Create the offline RSA-4096 root CA")
    root.add_argument("--output-dir", required=True)
    root.add_argument("--common-name", required=True)
    root.add_argument("--organization", required=True)
    root.add_argument("--crl-base-url", required=True, help="Public HTTPS base URL ending in /api/security/pki/crl")
    root.add_argument("--validity-days", type=int, default=3650)
    root.set_defaults(run=_root)

    intermediate = commands.add_parser("issue-intermediate", help="Issue a subordinate RSA-3072 CA")
    intermediate.add_argument("--root-certificate", required=True)
    intermediate.add_argument("--root-private-key", required=True)
    intermediate.add_argument("--output-dir", required=True)
    intermediate.add_argument("--common-name", required=True)
    intermediate.add_argument("--organization", required=True)
    intermediate.add_argument("--crl-base-url", required=True)
    intermediate.add_argument("--validity-days", type=int, default=1825)
    intermediate.set_defaults(run=_intermediate)

    crl = commands.add_parser("publish-crl", help="Issue or renew one issuer's signed CRL")
    crl.add_argument("--issuer-certificate", required=True)
    crl.add_argument("--issuer-private-key", required=True)
    crl.add_argument("--output", required=True)
    crl.add_argument("--revoke-serial", type=lambda value: int(value, 0), action="append", default=[])
    crl.add_argument("--crl-number", type=int, required=True)
    crl.add_argument("--validity-hours", type=int, default=24)
    crl.set_defaults(run=_crl)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        args.run(args)
        return 0
    except InstitutionalPKIError as error:
        print(error.code, file=sys.stderr)
        return 2
    except (OSError, ValueError) as error:
        del error
        print("INSTITUTIONAL_PKI_CEREMONY_FAILED", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
