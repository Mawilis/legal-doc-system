from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.eos.mongodb.index_provisioning_harness import (
    DEFAULT_MANIFEST,
    ManifestError,
    load_manifest,
    target_fingerprint,
    validate_manifest,
)


class EOSIndexProvisioningHarnessTests(unittest.TestCase):
    def test_repository_manifest_is_structurally_valid_and_incomplete(self) -> None:
        manifest = load_manifest(DEFAULT_MANIFEST)
        collections, indexes = validate_manifest(manifest)
        self.assertGreater(collections, 0)
        self.assertGreater(indexes, 0)
        self.assertEqual(manifest["status"], "INVENTORY_INCOMPLETE")
        self.assertFalse(manifest["production_mutation_authorized"])

    def test_duplicate_collection_entry_is_rejected(self) -> None:
        manifest = load_manifest(DEFAULT_MANIFEST)
        manifest["entries"].append(dict(manifest["entries"][0]))
        with self.assertRaisesRegex(ManifestError, "Duplicate collection"):
            validate_manifest(manifest)

    def test_production_target_is_rejected(self) -> None:
        with patch.dict(os.environ, {
            "WILSY_EOS_INDEX_TARGET_ENV": "production",
            "WILSY_EOS_INDEX_APPROVED_TARGET_FINGERPRINT": "a",
            "WILSY_EOS_INDEX_OBSERVED_TARGET_FINGERPRINT": "a",
        }):
            with self.assertRaisesRegex(ManifestError, "explicitly nonproduction"):
                target_fingerprint()

    def test_target_fingerprint_mismatch_is_rejected(self) -> None:
        with patch.dict(os.environ, {
            "WILSY_EOS_INDEX_TARGET_ENV": "nonproduction",
            "WILSY_EOS_INDEX_APPROVED_TARGET_FINGERPRINT": "approved",
            "WILSY_EOS_INDEX_OBSERVED_TARGET_FINGERPRINT": "observed",
        }):
            with self.assertRaisesRegex(ManifestError, "does not match"):
                target_fingerprint()

    def test_matching_nonproduction_fingerprint_returns_digest(self) -> None:
        with patch.dict(os.environ, {
            "WILSY_EOS_INDEX_TARGET_ENV": "nonproduction",
            "WILSY_EOS_INDEX_APPROVED_TARGET_FINGERPRINT": "opaque-target-digest",
            "WILSY_EOS_INDEX_OBSERVED_TARGET_FINGERPRINT": "opaque-target-digest",
        }):
            self.assertEqual(len(target_fingerprint()), 64)


if __name__ == "__main__":
    unittest.main()
