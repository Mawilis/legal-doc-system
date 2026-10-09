from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import cast

import pytest
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from tools.eos.legal_operations.service.legal_evidence_provider_delete_execution_port import (
    LegalEvidenceProviderDeleteExecutionPortError,
    LegalEvidenceProviderDeleteExecutionRequest,
)
from tools.eos.legal_operations.service.legal_evidence_s3_provider_delete_adapter import (
    PROVIDER_NAME,
    VERSION,
    LegalEvidenceS3ProviderDeleteAdapter,
    LegalEvidenceS3ProviderDeleteAdapterError,
    LegalEvidenceS3ProviderDeleteExecutionEvidence,
)


def _request(**overrides):
    values = {
        "command_id": "cmd-1",
        "tenant_id": "tenant-1",
        "provider_name": "aws_s3",
        "storage_reference": "opaque-storage-key",
        "object_version_reference": "version-1",
        "cleanup_authorization_id": "auth-1",
        "command_fingerprint": "c" * 128,
        "cleanup_authorization_fingerprint": "d" * 128,
    }
    values.update(overrides)
    return LegalEvidenceProviderDeleteExecutionRequest(**values)


class FakeClient:
    def __init__(self, response=None, error=None):
        self.response = {} if response is None else response
        self.error = error
        self.calls = []

    def delete_object(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.response


def test_version_and_provider_identity():
    assert VERSION.startswith("v1.0.0-L10A2R-A3-P4-P3")
    assert PROVIDER_NAME == "aws_s3"


def test_exact_version_specific_delete_call_and_evidence():
    client = FakeClient({"VersionId": "version-1", "DeleteMarker": False})
    adapter = LegalEvidenceS3ProviderDeleteAdapter(
        client=cast(BaseClient, client),
        bucket="wilsy-legal-evidence",
    )

    evidence = adapter.execute_delete(_request())

    assert client.calls == [{
        "Bucket": "wilsy-legal-evidence",
        "Key": "opaque-storage-key",
        "VersionId": "version-1",
    }]
    assert evidence == LegalEvidenceS3ProviderDeleteExecutionEvidence(
        provider_name="aws_s3",
        storage_reference="opaque-storage-key",
        object_version_reference="version-1",
        delete_marker=False,
        delete_marker_version_reference=None,
    )


def test_delete_marker_evidence_is_bounded():
    client = FakeClient({"VersionId": "version-1", "DeleteMarker": True})
    evidence = LegalEvidenceS3ProviderDeleteAdapter(
        client=cast(BaseClient, client),
        bucket="wilsy-legal-evidence",
    ).execute_delete(_request())

    assert evidence.delete_marker is True
    assert evidence.delete_marker_version_reference == "version-1"


def test_evidence_is_frozen():
    evidence = LegalEvidenceS3ProviderDeleteExecutionEvidence(
        provider_name="aws_s3",
        storage_reference="opaque-storage-key",
        object_version_reference="version-1",
        delete_marker=False,
        delete_marker_version_reference=None,
    )
    with pytest.raises(FrozenInstanceError):
        setattr(evidence, "storage_reference", "changed")


def test_provider_mismatch_rejects_before_provider_call():
    client = FakeClient()
    adapter = LegalEvidenceS3ProviderDeleteAdapter(
        client=cast(BaseClient, client),
        bucket="wilsy-legal-evidence",
    )

    with pytest.raises(
        LegalEvidenceS3ProviderDeleteAdapterError,
        match="PROVIDER_MISMATCH",
    ):
        adapter.execute_delete(_request(provider_name="azure_blob"))

    assert client.calls == []


def test_non_exact_request_rejects_before_provider_call():
    client = FakeClient()
    adapter = LegalEvidenceS3ProviderDeleteAdapter(
        client=cast(BaseClient, client),
        bucket="wilsy-legal-evidence",
    )

    with pytest.raises(
        LegalEvidenceS3ProviderDeleteAdapterError,
        match="DELETE_REQUEST_REQUIRED",
    ):
        adapter.execute_delete(
            cast(LegalEvidenceProviderDeleteExecutionRequest, object())
        )

    assert client.calls == []


def test_aws_failure_is_opaque_and_no_success_evidence():
    error = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "sensitive"}},
        "DeleteObject",
    )
    client = FakeClient(error=error)
    adapter = LegalEvidenceS3ProviderDeleteAdapter(
        client=cast(BaseClient, client),
        bucket="wilsy-legal-evidence",
    )

    with pytest.raises(
        LegalEvidenceS3ProviderDeleteAdapterError,
        match="PROVIDER_DELETE_FAILED",
    ) as captured:
        adapter.execute_delete(_request())

    assert "sensitive" not in str(captured.value)


def test_malformed_provider_response_rejects():
    client = FakeClient(response=[])
    adapter = LegalEvidenceS3ProviderDeleteAdapter(
        client=cast(BaseClient, client),
        bucket="wilsy-legal-evidence",
    )

    with pytest.raises(
        LegalEvidenceS3ProviderDeleteAdapterError,
        match="PROVIDER_RESPONSE_INVALID",
    ):
        adapter.execute_delete(_request())


def test_version_divergence_rejects():
    client = FakeClient({"VersionId": "other-version", "DeleteMarker": False})
    adapter = LegalEvidenceS3ProviderDeleteAdapter(
        client=cast(BaseClient, client),
        bucket="wilsy-legal-evidence",
    )

    with pytest.raises(
        LegalEvidenceS3ProviderDeleteAdapterError,
        match="PROVIDER_VERSION_MISMATCH",
    ):
        adapter.execute_delete(_request())


def test_adapter_has_no_registry_or_mongo_authority():
    source = __import__(
        "inspect"
    ).getsource(LegalEvidenceS3ProviderDeleteAdapter)

    forbidden = (
        "pymongo",
        "insert_one",
        "update_one",
        "delete_one",
        "session=",
        "registry",
        "cleanup_authorization_registry",
    )
    for token in forbidden:
        assert token not in source


def test_request_contract_error_type_is_not_swallowed():
    assert issubclass(
        LegalEvidenceProviderDeleteExecutionPortError,
        Exception,
    )


def test_omitted_optional_provider_headers_remain_unknown():
    client = FakeClient({})
    adapter = LegalEvidenceS3ProviderDeleteAdapter(
        client=cast(BaseClient, client),
        bucket="bucket-1",
    )

    evidence = adapter.execute_delete(_request())

    assert client.calls == [
        {
            "Bucket": "bucket-1",
            "Key": "opaque-storage-key",
            "VersionId": "version-1",
        }
    ]
    assert evidence.object_version_reference == "version-1"
    assert evidence.delete_marker is None
    assert evidence.delete_marker_version_reference is None


@pytest.mark.parametrize(
    "response",
    [
        {"DeleteMarker": None},
        {"DeleteMarker": "false"},
        {"VersionId": None},
        {"VersionId": ""},
        {"VersionId": " version-1"},
    ],
)
def test_present_malformed_optional_provider_headers_reject(response):
    client = FakeClient(response)
    adapter = LegalEvidenceS3ProviderDeleteAdapter(
        client=cast(BaseClient, client),
        bucket="bucket-1",
    )

    with pytest.raises(
        LegalEvidenceS3ProviderDeleteAdapterError,
        match="PROVIDER_RESPONSE_INVALID",
    ):
        adapter.execute_delete(_request())
