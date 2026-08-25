"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    FG168 Distributed Artifact Store Integration Test.
    Validates the end-to-end flow of the checksum, manifest, storage, and registry modules.
===============================================================================
"""

import shutil
import sys
from pathlib import Path

# Ensure module path resolution
artifacts_dir = Path(__file__).parent.resolve()
if str(artifacts_dir) not in sys.path:
    sys.path.insert(0, str(artifacts_dir))

from registry import ArtifactRegistry

def test_fg168_architecture():
    print("===============================================================================")
    print("WILSY OS KERNEL - FG168 DISTRIBUTED ARTIFACT STORE INTEGRATION TEST")
    print("===============================================================================")

    # Setup sandbox paths
    test_root = Path("/Users/wilsonkhanyezi/legal-doc-system/tools/eos/artifacts/test_sandbox")
    source_dir = test_root / "source"
    storage_dir = test_root / "dist"
    
    source_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Create a dummy artifact to ingest
    dummy_file = source_dir / "compiled_contract_v2.bin"
    dummy_payload = b"WILSY_OS_SECURE_PAYLOAD_V2_DATA_BLOB"
    dummy_file.write_bytes(dummy_payload)
    print(f"  -> Created test asset: {dummy_file.name} ({len(dummy_payload)} bytes)")

    # 2. Initialize the Artifact Registry
    registry = ArtifactRegistry(storage_dir=storage_dir)
    print("  -> Initialized Artifact Registry & Storage Engine.")

    # 3. Register the Artifact (triggers Checksum, Manifest, and Storage)
    print("\n  [EXECUTING INGESTION PIPELINE]")
    metadata_tags = {"module": "legal_compiler", "compliance": "pappi_act"}
    result = registry.register_artifact(
        file_path=dummy_file,
        metadata=metadata_tags,
        producer="LegalDocCompilerEngine",
        execution_id="exec-fg168-test-001",
        content_type="application/octet-stream"
    )

    assert result["status"] == "REGISTERED", "Registration failed!"
    artifact_id = result["artifact_id"]
    manifest = result["manifest"]
    
    print(f"  -> Registration Status: {result['status']}")
    print(f"  -> Artifact ID:   {artifact_id}")
    print(f"  -> Checksum:      {result['checksum']}")
    print(f"  -> Producer:      {manifest['producer']}")
    print(f"  -> Execution ID:  {manifest['execution_id']}")
    print(f"  -> Timestamp:     {manifest['created_at']}")
    print(f"  -> Stored Path:   {result['stored_path']}")

    # 4. Consumer Retrieval & Cryptographic Verification
    print("\n  [EXECUTING CONSUMER RETRIEVAL & AUDIT]")
    audit_result = registry.verify_artifact_integrity(artifact_id)
    print(f"  -> Audit Valid:   {audit_result['valid']}")
    print(f"  -> Audit Reason:  {audit_result['reason']}")
    assert audit_result["valid"] is True, "Cryptographic verification failed!"

    # 5. Storage Statistics
    stats = registry.storage.get_storage_stats()
    print("\n  [STORAGE ENGINE STATISTICS]")
    print(f"  -> Total Files:   {stats['total_files']}")
    print(f"  -> Total Bytes:   {stats['total_bytes']} bytes")

    # Cleanup sandbox
    shutil.rmtree(test_root, ignore_errors=True)
    print("===============================================================================")
    print("FG168 DISTRIBUTED ARTIFACT STORE FULL SUITE VERIFIED SUCCESSFULLY.")
    print("===============================================================================")

if __name__ == "__main__":
    test_fg168_architecture()
