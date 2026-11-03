"""Tests for tenant-neutral global principal password verification."""
from types import SimpleNamespace

import bcrypt
import pytest

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_credential import PrincipalCredential
from tools.eos.auth.principal_credential_authentication import (
    GlobalPrincipalAuthenticationUnavailable,
    authenticate_global_principal,
)
from tools.eos.auth.principal_credential_repository import (
    PrincipalCredentialNotFoundError,
    PrincipalCredentialRepositoryError,
)
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepositoryError


class CredentialRepository:
    def __init__(self, credential=None, failure=None):
        self.credential = credential
        self.failure = failure
        self.session = None
        self.email = None

    def get_by_email(self, email, *, session=None):
        self.email = email
        self.session = session
        if self.failure:
            raise self.failure
        if self.credential is None:
            raise PrincipalCredentialNotFoundError("not found")
        return self.credential


class PrincipalRepository:
    def __init__(self, status=PrincipalStatus.ACTIVE, failure=None):
        self.status = status
        self.failure = failure
        self.session = None

    def get(self, principal_id, *, session=None):
        self.session = session
        if self.failure:
            raise self.failure
        return SimpleNamespace(principal_id=principal_id, status=self.status)


@pytest.fixture()
def credential():
    password_hash = bcrypt.hashpw(b"correct horse battery staple", bcrypt.gensalt(rounds=4)).decode()
    return PrincipalCredential(
        principal_id="principal-global-1",
        normalized_email="owner@example.com",
        password_hash=password_hash,
        credential_revision=12,
        mfa_enabled=True,
    )


def test_authenticates_global_principal_without_tenant_or_membership_scope(credential):
    credentials = CredentialRepository(credential)
    principals = PrincipalRepository()
    result = authenticate_global_principal(
        email="OWNER@example.com",
        password="correct horse battery staple",
        credential_repository=credentials,
        principal_repository=principals,
    )
    assert result is not None
    assert result.principal_id == "principal-global-1"
    assert result.normalized_email == "owner@example.com"
    assert result.credential_revision == 12
    assert result.mfa_enabled is True
    assert "tenant_id" not in result.__dataclass_fields__
    assert credentials.email == "owner@example.com"


def test_wrong_password_unknown_email_and_inactive_principal_are_denied(credential):
    assert authenticate_global_principal(
        email="owner@example.com",
        password="wrong",
        credential_repository=CredentialRepository(credential),
        principal_repository=PrincipalRepository(),
    ) is None
    assert authenticate_global_principal(
        email="missing@example.com",
        password="wrong",
        credential_repository=CredentialRepository(),
        principal_repository=PrincipalRepository(),
    ) is None
    assert authenticate_global_principal(
        email="owner@example.com",
        password="correct horse battery staple",
        credential_repository=CredentialRepository(credential),
        principal_repository=PrincipalRepository(PrincipalStatus.SUSPENDED),
    ) is None


def test_authority_outages_are_not_reported_as_bad_credentials(credential):
    with pytest.raises(GlobalPrincipalAuthenticationUnavailable):
        authenticate_global_principal(
            email="owner@example.com",
            password="correct horse battery staple",
            credential_repository=CredentialRepository(failure=PrincipalCredentialRepositoryError("down")),
            principal_repository=PrincipalRepository(),
        )
    with pytest.raises(GlobalPrincipalAuthenticationUnavailable):
        authenticate_global_principal(
            email="owner@example.com",
            password="correct horse battery staple",
            credential_repository=CredentialRepository(credential),
            principal_repository=PrincipalRepository(failure=PrincipalAuthorityRepositoryError("down")),
        )


def test_caller_session_is_forwarded_to_both_global_authorities(credential):
    token = object()
    credentials = CredentialRepository(credential)
    principals = PrincipalRepository()
    result = authenticate_global_principal(
        email="owner@example.com",
        password="correct horse battery staple",
        credential_repository=credentials,
        principal_repository=principals,
        session=token,
    )
    assert result is not None
    assert credentials.session is token
    assert principals.session is token
