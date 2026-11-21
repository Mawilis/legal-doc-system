"""Non-generative OpenAI model/key readiness certificate for local EOS development.

TITLE: WILSY OS OpenAI Provider Readiness Certificate
VERSION: v1.0.0-NONGENERATIVE-PROVIDER-PREFLIGHT
AUTHORITY: Wilsy OS Core Governance; local development certification only.
EPITOME: One authenticated GET model retrieval verifies transport and model
         identity without calling Responses or consuming WILSY AI quota.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/providers/openai_readiness_certificate.py
COLLABORATION / OWNERSHIP: Operator supplies an ephemeral API key; OpenAI SDK
                           owns model retrieval; EOS remains owner of all
                           admission, entitlement, usage and identity truth.
CERTIFICATION / UPDATE DATE: 2026-11-21
CHANGELOG: v1.0.0-NONGENERATIVE-PROVIDER-PREFLIGHT establishes an opt-in
           hidden-secret, single-request, no-retry model-access check with
           bounded error classification and no provider generation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Never logs or prints key, vendor error text,
                           HTTP body, auth headers, prompts or personal data.
TENANT BOUNDARY: No tenant access or session/tenant selection occurs.
AUTHORITY BOUNDARY: Model/key reachability ONLY; not billable API entitlement,
                    generation permission or WILSY usage certification.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: No fallback or retry; no Responses call, MongoDB
                         mutation, auth bypass or reservation release.
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import sys
from typing import Any, Callable, Final

VERSION: Final[str] = "v1.0.0-NONGENERATIVE-PROVIDER-PREFLIGHT"
_MODEL_ID = re.compile(r"^gpt-[A-Za-z0-9][A-Za-z0-9._:-]{0,121}$")
_ERROR_CLASS = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,79}$")
_TIMEOUT: Final[float] = 12.0


class OpenAIReadinessRefused(ValueError):
    """Fail-closed local preflight input rejection without secrets."""


def inspect_model(*, client: Any, model_id: str) -> dict[str, object]:
    """Retrieve only a known model ID; no text generation or usage reservation.

    The injected client is scoped to one explicit SDK model retrieval. Even a
    successful lookup does NOT establish external quota/credits or WILSY IAM.
    """
    if not isinstance(model_id, str) or _MODEL_ID.fullmatch(model_id) is None:
        raise OpenAIReadinessRefused("OPENAI_PREFLIGHT_MODEL_ID_INVALID")
    try:
        response = client.models.retrieve(model_id)
    except Exception as error:
        status = getattr(error, "status_code", None)
        safe_status = status if type(status) is int and 100 <= status <= 599 else "UNKNOWN"
        name = type(error).__name__
        safe_class = name if _ERROR_CLASS.fullmatch(name) is not None else "UNCLASSIFIED"
        return {
            "status": "NOT_VERIFIED",
            "check": "MODEL_LOOKUP",
            "failure_class": safe_class,
            "http_status": safe_status,
            "generation_attempted": False,
            "quota_verified": False,
            "wilsy_reservations_written": False,
        }
    resolved = getattr(response, "id", None)
    if resolved != model_id:
        raise OpenAIReadinessRefused("OPENAI_PREFLIGHT_MODEL_ID_MISMATCH")
    return {
        "status": "MODEL_LOOKUP_VERIFIED",
        "check": "MODEL_LOOKUP",
        "generation_attempted": False,
        "quota_verified": False,
        "wilsy_reservations_written": False,
    }


def main(
    argv: list[str] | None = None,
    *,
    client_factory: Callable[..., Any] | None = None,
) -> int:
    """Read a hidden, ephemeral key and perform at most one model GET request.

    No background worker, credential file, provider generation, tenant lookup
    or MongoDB session is opened by this certificate. Failure is observable
    only as bounded classification and numeric HTTP status.
    """
    parser = argparse.ArgumentParser(description="WILSY OpenAI non-generative readiness check")
    parser.add_argument("--model", default="gpt-5-mini")
    args = parser.parse_args(argv)
    if not isinstance(args.model, str) or _MODEL_ID.fullmatch(args.model) is None:
        print(json.dumps({"status": "REFUSED", "code": "OPENAI_PREFLIGHT_MODEL_ID_INVALID"}))
        return 2
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        if not sys.stdin.isatty():
            print(json.dumps({"status": "REFUSED", "code": "OPENAI_PREFLIGHT_TERMINAL_REQUIRED"}))
            return 2
        key = getpass.getpass("OpenAI API key (hidden; never saved): ")
    if not isinstance(key, str) or not key.strip() or len(key) > 4096:
        print(json.dumps({"status": "REFUSED", "code": "OPENAI_PREFLIGHT_CREDENTIAL_INVALID"}))
        return 2
    try:
        if client_factory is None:
            from openai import OpenAI

            client_factory = OpenAI
        client = client_factory(
            api_key=key,
            base_url="https://api.openai.com/v1",
            timeout=_TIMEOUT,
            max_retries=0,
        )
        report = inspect_model(client=client, model_id=args.model)
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
        return 0 if report["status"] == "MODEL_LOOKUP_VERIFIED" else 1
    except OpenAIReadinessRefused as error:
        print(json.dumps({"status": "REFUSED", "code": str(error)}))
        return 2
    except Exception:
        print(json.dumps({"status": "NOT_VERIFIED", "code": "OPENAI_PREFLIGHT_TRANSPORT_OR_SDK_UNAVAILABLE"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["VERSION", "OpenAIReadinessRefused", "inspect_model", "main"]

# ARTIFACT: openai_readiness_certificate.py
# VERSION: v1.0.0-NONGENERATIVE-PROVIDER-PREFLIGHT
# AUTHORITY BOUNDARY: explicit local provider model lookup only
# TENANT POSTURE: no tenant data, membership or privilege grants
# FAIL-CLOSED POSTURE: no generation, no retry and no reservation mutations
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
