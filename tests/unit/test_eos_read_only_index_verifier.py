from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.eos.mongodb.read_only_index_verifier import _fingerprint, _manifest_entries, verify


class _Collection:
    def __init__(self, indexes):
        self._indexes = indexes

    def list_indexes(self):
        return iter(self._indexes)


class _Database:
    def __init__(self, collections):
        self._collections = collections

    def __getitem__(self, name):
        return self._collections[name]


class _Client:
    def __init__(self, database):
        self._database = database

    def __getitem__(self, name):
        return self._database


class ReadOnlyIndexVerifierTests(unittest.TestCase):
    def setUp(self):
        self.entries = [{
            "collection": "records",
            "indexes": [
                {"name": "tenant_record_unique", "keys": [["tenant_id", 1], ["record_id", 1]], "unique": True},
                {"name": "tenant_expiry_ttl", "keys": [["expires_at", 1]], "expireAfterSeconds": 0},
            ],
        }]

    def test_exact_indexes_pass_without_any_mutation_api(self):
        client = _Client(_Database({"records": _Collection([
            {"name": "_id_", "key": {"_id": 1}},
            {"name": "tenant_record_unique", "key": {"tenant_id": 1, "record_id": 1}, "unique": True},
            {"name": "tenant_expiry_ttl", "key": {"expires_at": 1}, "expireAfterSeconds": 0},
        ])}))
        result = verify(client, self.entries, "eos_nonproduction")
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["indexes_checked"], 2)
        self.assertEqual(result["mutations_performed"], 0)

    def test_missing_index_fails(self):
        client = _Client(_Database({"records": _Collection([{"name": "_id_", "key": {"_id": 1}}])}))
        result = verify(client, self.entries, "eos_nonproduction")
        self.assertEqual(result["result"], "DIVERGENCE")
        self.assertIn("MISSING", {item["status"] for item in result["findings"]})

    def test_wrong_ttl_option_fails(self):
        client = _Client(_Database({"records": _Collection([
            {"name": "tenant_record_unique", "key": {"tenant_id": 1, "record_id": 1}, "unique": True},
            {"name": "tenant_expiry_ttl", "key": {"expires_at": 1}, "expireAfterSeconds": 60},
        ])}))
        result = verify(client, self.entries, "eos_nonproduction")
        self.assertIn("OPTIONS_MISMATCH", {item["status"] for item in result["findings"]})

    def test_extra_undeclared_index_is_reported(self):
        client = _Client(_Database({"records": _Collection([
            {"name": "_id_", "key": {"_id": 1}},
            {"name": "tenant_record_unique", "key": {"tenant_id": 1, "record_id": 1}, "unique": True},
            {"name": "tenant_expiry_ttl", "key": {"expires_at": 1}, "expireAfterSeconds": 0},
            {"name": "unexpected", "key": {"other": 1}},
        ])}))
        result = verify(client, self.entries, "eos_nonproduction")
        self.assertIn("UNDECLARED_EXTRA", {item["status"] for item in result["findings"]})


    def test_business_database_pass_skips_separate_audit_database(self):
        manifest = {
            "status": "COMPLETE",
            "production_mutation_authorized": False,
            "entries": [
                {"database": "canonical_eos_business_database", "collection": "records", "indexes": []},
                {"database": "platform_authorization_audit_database", "collection": "audit", "indexes": []},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            entries = _manifest_entries(path, "eos_nonproduction")
        self.assertEqual([entry["collection"] for entry in entries], ["records"])
        self.assertEqual(entries[0]["database"], "eos_nonproduction")

    def test_fingerprint_is_stable_and_database_scoped(self):
        hello = {"setName": "rs0", "hosts": ["b.example:27017", "a.example:27017"], "setVersion": 3}
        self.assertEqual(_fingerprint(hello, "eos_test"), _fingerprint(hello, "eos_test"))
        self.assertNotEqual(_fingerprint(hello, "eos_test"), _fingerprint(hello, "other_db"))


if __name__ == "__main__":
    unittest.main()
