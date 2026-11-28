"""TITLE: WILSY OS MW-T12 Isolated Replica Initialization Certificate
VERSION: v1.0.0-MW-T12-MONGO7-HOSTNAME-INIT-CERT
AUTHORITY: WILSY OS release recovery governance.
EPITOME: Ensure the synthetic restore drill uses a MongoDB 7-compliant
         localhost replica identity and rejects bad initiation receipts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_mw_t12_replica_hostname_primary.py
COLLABORATION / OWNERSHIP: Python EOS recovery programme.
CERTIFICATION / UPDATE DATE: 2026-11-28
CHANGELOG: v1.0.0-MW-T12-MONGO7-HOSTNAME-INIT-CERT covers success, invalid
           and rejected initiation with isolated synthetic shell mocks.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No real Mongo, Docker, URI or secrets.
TENANT BOUNDARY: Does not touch any tenant or database.
AUTHORITY BOUNDARY: Source-only CI test; cannot certify full EOS recovery.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
import pytest
from tools.eos.ops import mw_t12_disposable_mongo_recovery as subject


def test_recovery_replicaset_uses_hostname_and_verifies_primary(monkeypatch):
    """Accept only successful DNS-hostname initiation and actual primary."""
    calls = []
    monkeypatch.setattr(subject.time, "sleep", lambda _: None)

    def observed(container, expression):
        calls.append((container, expression))
        if expression == "db.adminCommand({ping:1}).ok":
            return "1"
        if expression.startswith("JSON.stringify(rs.initiate"):
            assert 'host:"localhost:27017"' in expression
            assert 'host:"127.0.0.1:27017"' not in expression
            return '{"ok":1}'
        if expression == "db.hello().isWritablePrimary":
            return "true"
        raise AssertionError("Unexpected synthetic shell command")

    monkeypatch.setattr(subject, "mongo", observed)
    subject.primary("synthetic-owned-container")
    assert len(calls) == 3


@pytest.mark.parametrize("receipt,expected", [
    ('{"ok":0,"code":93}', "MONGO_REPLICA_INIT_REJECTED"),
    ("not-json", "MONGO_REPLICA_INIT_INVALID"),
    ('{"ok":"1"}', "MONGO_REPLICA_INIT_REJECTED"),
])
def test_recovery_rejects_unverified_replica_init(monkeypatch,receipt,expected):
    """Malformed, non-success and misleading string ok must fail closed."""
    monkeypatch.setattr(subject.time,"sleep",lambda _: None)
    def observed(_container,expression):
        if expression == "db.adminCommand({ping:1}).ok":
            return "1"
        if expression.startswith("JSON.stringify(rs.initiate"):
            return receipt
        raise AssertionError("Primary polling must not follow rejected initiation")
    monkeypatch.setattr(subject,"mongo",observed)
    with pytest.raises(subject.RecoveryGateError) as denied:
        subject.primary("synthetic-owned-container")
    assert denied.value.code == expected


# ARTIFACT: tests/unit/test_mw_t12_replica_hostname_primary.py
# VERSION: v1.0.0-MW-T12-MONGO7-HOSTNAME-INIT-CERT
# AUTHORITY BOUNDARY: Synthetic replica test only, not EOS recovery.
# TENANT POSTURE: No persistent or external tenant state.
# FAIL-CLOSED POSTURE: Invalid Mongo init receipts reject before primary poll.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
