"""Static safety contract for the Global Principal MFA KMS CloudFormation template."""
from __future__ import annotations

import re
from pathlib import Path


TEMPLATE = (
    Path(__file__).resolve().parents[2]
    / "infra"
    / "aws"
    / "global-principal-mfa-kms.yaml"
)


def _oidc_issuer_host_path_pattern() -> str:
    source = TEMPLATE.read_text(encoding="utf-8")
    parameter = source.split("  EosEksOidcIssuerHostPath:", 1)[1].split(
        "  EosServiceAccountSubject:", 1
    )[0]
    match = re.search(r"AllowedPattern:\s*'([^']+)'", parameter)
    assert match is not None, "EKS OIDC issuer host/path must have an explicit constraint"
    return match.group(1)


def test_real_eks_oidc_issuer_identifier_accepts_alphanumeric_provider_id():
    pattern = _oidc_issuer_host_path_pattern()
    actual_eks_issuer = (
        "oidc.eks.af-south-1.amazonaws.com/"
        "id/EXAMPLED539D4633E53DE1B71EXAMPLE"
    )
    assert re.fullmatch(pattern, actual_eks_issuer)


def test_eks_oidc_issuer_host_path_rejects_scheme_and_untrusted_suffixes():
    pattern = _oidc_issuer_host_path_pattern()
    assert re.fullmatch(
        pattern,
        "oidc.eks.af-south-1.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE",
    )
    assert not re.fullmatch(
        pattern,
        "https://oidc.eks.af-south-1.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE",
    )
    assert not re.fullmatch(
        pattern,
        "oidc.eks.af-south-1.amazonaws.com/id/EXAMPLE/attacker",
    )


def test_production_eks_stack_has_no_local_development_identity_or_grant():
    source = TEMPLATE.read_text(encoding="utf-8")
    assert "LocalDevelopmentPrincipalArn" not in source
    assert "ApprovedLocalDevelopmentMfaEnvelopeUse" not in source
