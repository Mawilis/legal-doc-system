"""Safety tests for the isolated Python EOS browser-certification fixture.

TITLE: Browser certification Mongo target guard
VERSION: v1.0.0-BROWSER-CERT-MONGO-URI-GUARD-TEST
AUTHORITY: Test isolation and data-protection verification only.
EPITOME: Prove that browser-cert fixture operations accept only the explicitly
         named local disposable replica-set database and reject remote or
         unauthorized local targets before any database connection is attempted.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_browser_cert_fixture_uri_guard.py
COLLABORATION / OWNERSHIP: Browser-cert fixture contract; no production authority.
CERTIFICATION / UPDATE DATE: 2026-10-27
CHANGELOG: v1.0.0 certifies loopback host, port, database-prefix, and replica-set interlocks.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: All cases validate URI strings only; no connections are opened.
TENANT BOUNDARY: Disposable certification database only.
AUTHORITY BOUNDARY: Test-only safety assertions.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

import importlib.util
from pathlib import Path

import pytest

_fixture_path = Path(__file__).resolve().parents[1] / "e2e" / "browser_cert_fixture.py"
_fixture_spec = importlib.util.spec_from_file_location("wilsy_browser_cert_fixture", _fixture_path)
if _fixture_spec is None or _fixture_spec.loader is None:
    raise RuntimeError("BROWSER_CERT_FIXTURE_MODULE_UNAVAILABLE")
_fixture_module = importlib.util.module_from_spec(_fixture_spec)
_fixture_spec.loader.exec_module(_fixture_module)
_uri = _fixture_module._uri


def test_accepts_only_named_loopback_disposable_replica_set(monkeypatch):
    uri = (
        "mongodb://127.0.0.1:27017/wilsy_l8_8m_r3_test"
        "?replicaSet=wilsyVendorCertRS"
    )
    monkeypatch.setenv("BROWSER_CERT_MONGO_URI", uri)

    assert _uri() == uri


@pytest.mark.parametrize(
    "uri",
    [
        "",
        "mongodb+srv://example.invalid/wilsy_l8_8m_r3_test",
        "mongodb://example.invalid:27017/wilsy_l8_8m_r3_test?replicaSet=wilsyVendorCertRS",
        "mongodb://127.0.0.1:27027/wilsy_l8_8m_r3_test?replicaSet=wilsyVendorCertRS",
        "mongodb://127.0.0.1:27017/wilsy?w=majority",
        "mongodb://127.0.0.1:27017/wilsy_l8_8m_r3_test?replicaSet=other",
        "mongodb://user:password@127.0.0.1:27017/wilsy_l8_8m_r3_test?replicaSet=wilsyVendorCertRS",
    ],
)
def test_rejects_remote_or_non_disposable_targets(monkeypatch, uri):
    monkeypatch.setenv("BROWSER_CERT_MONGO_URI", uri)

    with pytest.raises(RuntimeError):
        _uri()


# ARTIFACT: test_browser_cert_fixture_uri_guard.py
# VERSION: v1.0.0-BROWSER-CERT-MONGO-URI-GUARD-TEST
# AUTHORITY BOUNDARY: fixture target safety only
# TENANT POSTURE: no database connection is opened
# FAIL-CLOSED POSTURE: any non-disposable URI is rejected
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
