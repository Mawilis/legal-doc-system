"""WILSY OS — R95 exact-matter operational authority fail-closed tests.

VERSION: v1.0.0-P47-R95-G5-EXACT-MATTER-AUTHORITY-RED
AUTHORITY: Test-only contract; no access or assignment permission issued.
TENANT BOUNDARY: Exact tenant/matter/principal, never global defaults.
FINANCIAL AUTHORITY: None.
"""

import pytest

from tools.eos.legal_operations.service.legal_work_exact_matter_authority import (
    LegalWorkExactMatterAuthorityUnavailable,
    authorize_actor_for_exact_matter,
    validate_assignment_recipient_for_exact_matter,
)


@pytest.mark.parametrize(
    "principal_id",
    ["actor-001", "recipient-001"],
)
def test_actor_cannot_be_admitted_without_authority_source(principal_id):
    with pytest.raises(LegalWorkExactMatterAuthorityUnavailable):
        authorize_actor_for_exact_matter(
            tenant_id="tenant-001",
            case_matter_id="matter-001",
            actor_principal_id=principal_id,
            authority_source=None,
            session=None,
        )


def test_recipient_cannot_be_admitted_without_authority_source():
    with pytest.raises(LegalWorkExactMatterAuthorityUnavailable):
        validate_assignment_recipient_for_exact_matter(
            tenant_id="tenant-001",
            case_matter_id="matter-001",
            recipient_principal_id="recipient-001",
            authority_source=None,
            session=None,
        )


@pytest.mark.parametrize(
    "untrusted_source",
    [
        {"decision": "ALLOW_UNVERIFIED"},
        {"permits_access": True},
        {"authorizes_matter_access": True},
        True,
    ],
)
def test_untrusted_evidence_does_not_admit_actor(untrusted_source):
    with pytest.raises(LegalWorkExactMatterAuthorityUnavailable):
        authorize_actor_for_exact_matter(
            tenant_id="tenant-001",
            case_matter_id="matter-001",
            actor_principal_id="actor-001",
            authority_source=untrusted_source,
            session=None,
        )


@pytest.mark.parametrize(
    "untrusted_source",
    [
        {"decision": "ALLOW_UNVERIFIED"},
        {"permits_access": True},
        {"authorizes_matter_access": True},
        True,
    ],
)
def test_untrusted_evidence_does_not_admit_recipient(untrusted_source):
    with pytest.raises(LegalWorkExactMatterAuthorityUnavailable):
        validate_assignment_recipient_for_exact_matter(
            tenant_id="tenant-001",
            case_matter_id="matter-001",
            recipient_principal_id="recipient-001",
            authority_source=untrusted_source,
            session=None,
        )


def test_source_cannot_be_replaced_by_business_role():
    with pytest.raises(LegalWorkExactMatterAuthorityUnavailable):
        authorize_actor_for_exact_matter(
            tenant_id="tenant-001",
            case_matter_id="matter-001",
            actor_principal_id="actor-001",
            authority_source="LEGAL_PARTNER",
            session=None,
        )
