"""TITLE: WILSY G72 Practitioner Content Admission Certificate.
VERSION: v1.0.0-P47-R95-G72
CHANGELOG: Test-first content-admission denial and scope invariants.
AUTHORITY: No affirmative practitioner matter-content permission.
"""
import inspect
import pytest

from tools.eos.legal_operations.service.legal_work_practitioner_content_admission import (
    PractitionerContentAdmissionDenied,
    require_practitioner_content_admission,
)

class Session:
    in_transaction = True

class Reader:
    def __init__(self):
        self.calls = 0

    def read(self, *args, **kwargs):
        self.calls += 1
        raise AssertionError("CONFIDENTIAL_BYTES_READER_MUST_NOT_BE_CALLED")

def request(**overrides):
    kwargs = {
        "tenant_id": "tenant-g72",
        "case_matter_id": "matter-g72",
        "practitioner_principal_id": "practitioner-g72",
        "content_reference": "content-g72",
        "session": Session(),
    }
    kwargs.update(overrides)
    return kwargs

def test_valid_scope_still_denied():
    with pytest.raises(
        PractitionerContentAdmissionDenied,
        match="P47_R95_CONTENT_SOURCE_VERIFICATION_UNAVAILABLE",
    ):
        require_practitioner_content_admission(**request())

@pytest.mark.parametrize("field", [
    "tenant_id", "case_matter_id",
    "practitioner_principal_id", "content_reference",
])
def test_missing_or_malformed_scope_denied(field):
    for bad in ("", " ", None, 123, True, " unknown "):
        with pytest.raises(PractitionerContentAdmissionDenied):
            require_practitioner_content_admission(
                **request(**{field: bad})
            )

def test_transaction_required():
    for bad in (None, object(), False):
        session = bad
        with pytest.raises(
            PractitionerContentAdmissionDenied,
            match="P47_R95_CONTENT_ACTIVE_TRANSACTION_REQUIRED",
        ):
            require_practitioner_content_admission(
                **request(session=session)
            )

def test_session_requires_exact_true():
    class Forged:
        in_transaction = 1
    with pytest.raises(PractitionerContentAdmissionDenied):
        require_practitioner_content_admission(
            **request(session=Forged())
        )

def test_caller_cannot_inject_approval_or_reader():
    for injected in (
        {"approved": True},
        {"wall_enforced": True},
        {"reader": Reader()},
        {"reviewer_authorized": True},
        {"clearance_fingerprint": "a" * 128},
    ):
        with pytest.raises(TypeError):
            require_practitioner_content_admission(
                **request(**injected)
            )

def test_no_byte_return_path_in_signature():
    signature = inspect.signature(
        require_practitioner_content_admission
    )
    assert "reader" not in signature.parameters
    assert "collection" not in signature.parameters
    assert "approved" not in signature.parameters
    assert "wall_enforced" not in signature.parameters
    assert "permission" not in signature.parameters
    assert "authorization_decision" not in signature.parameters

def test_repeated_requests_always_fail_closed():
    for _ in range(5):
        with pytest.raises(PractitionerContentAdmissionDenied):
            require_practitioner_content_admission(**request())

# END OF WILSY OS SOVEREIGN ARTIFACT
