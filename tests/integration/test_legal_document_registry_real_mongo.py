"""R1D-B0F-B4-R7 isolated real-Mongo certificate for legal documents.

TITLE: Legal Document Version Registry Real-Mongo Certificate
VERSION: v1.0.1-R1D-B0F-B4-R7-DOCUMENT-RM-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves immutable, server-digested, status-gated document versions
         against an isolated durable Mongo collection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_document_registry_real_mongo.py
TENANT BOUNDARY: Certification database is UUID-isolated and never uses live
                 Wilsy tenant document data.
AUTHORITY BOUNDARY: Document version truth only; no acceptance or signatory
                    authority is created.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
CHANGELOG: v1.0.1 repairs only the corrupt-row fixture identity so unique-index
           enforcement cannot mask digest-corruption hydration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Certification data is isolated and contains no
                            live tenant legal corpus.
"""
from datetime import datetime, timezone
import os
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAcceptanceError,
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
    canonical_document_digest,
)
from tools.eos.legal_operations.registry.legal_document_registry import (
    LegalDocumentRegistry,
    LegalDocumentRegistryError,
)


URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 17, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def mongo_database():
    client = MongoClient(URI, serverSelectionTimeoutMS=3000, replicaSet=REPLICA_SET, retryWrites=True)
    try:
        hello = client.admin.command("hello")
    except PyMongoError as error:
        client.close()
        pytest.skip(f"R7 document Mongo runtime unavailable: {type(error).__name__}")
    if hello.get("setName") != REPLICA_SET or not hello.get("isWritablePrimary", hello.get("ismaster", False)):
        client.close()
        pytest.skip("R7 document certificate requires a writable certified replica set")
    name = "r7_legal_document_" + uuid4().hex
    database = client.get_database(name, read_concern=ReadConcern("majority"), write_concern=WriteConcern(w="majority", j=True))
    try:
        yield client, database
    finally:
        client.drop_database(name)
        client.close()


def _document(
    *,
    family: LegalAgreementType = LegalAgreementType.USER_TERMS,
    status: LegalDocumentStatus = LegalDocumentStatus.APPROVED,
    document_id: str = "DOC-R7-USER-TERMS",
    version: str = "1.0.0",
    content: str = "Approved R7 isolated document",
) -> LegalDocumentVersion:
    reference = f"r7:{family.value}:{version}"
    return LegalDocumentVersion(
        document_id=document_id,
        agreement_type=family,
        version=version,
        title="R7 " + family.value,
        jurisdiction="ZA",
        locale="en-ZA",
        effective_from=NOW,
        status=status,
        content_reference=reference,
        content=content,
        sha3_512=canonical_document_digest(content, reference),
        created_at=NOW,
    )


def test_document_registry_is_durable_immutable_and_status_gated(mongo_database):
    client, database = mongo_database
    collection = database["legal_document_versions"]
    LegalDocumentRegistry.ensure_indexes(collection)
    assert {item["name"] for item in collection.list_indexes()} >= {
        "legal_document_version_unique", "legal_agreement_version_unique"
    }
    original = _document()
    with client.start_session() as session:
        session.start_transaction()
        assert LegalDocumentRegistry.register(original, collection, session=session) == original
        session.commit_transaction()

    assert LegalDocumentRegistry.register(original, collection) == original
    assert collection.count_documents({}) == 1
    assert LegalDocumentRegistry.approved_for(LegalAgreementType.USER_TERMS, collection) == original

    divergent = _document(content="tampered content")
    with pytest.raises(LegalDocumentRegistryError, match="IMMUTABILITY_CONFLICT"):
        LegalDocumentRegistry.register(divergent, collection)

    draft = _document(status=LegalDocumentStatus.DRAFT_REVIEW_REQUIRED, document_id="DOC-R7-DRAFT", version="0.9.0")
    retired = _document(status=LegalDocumentStatus.RETIRED, document_id="DOC-R7-RETIRED", version="0.8.0")
    LegalDocumentRegistry.register(draft, collection)
    LegalDocumentRegistry.register(retired, collection)
    assert LegalDocumentRegistry.approved_for(LegalAgreementType.USER_TERMS, collection) == original

    successor = _document(document_id="DOC-R7-USER-TERMS-2", version="2.0.0", content="Material approved successor")
    LegalDocumentRegistry.register(successor, collection)
    assert LegalDocumentRegistry.get(original.document_id, original.version, collection) == original
    assert LegalDocumentRegistry.get(successor.document_id, successor.version, collection) == successor

    corrupt = _document(
        document_id="DOC-R7-CORRUPT",
        version="9.9.9",
        content="Corrupt durable R7 document",
    )
    collection.insert_one({**corrupt.to_document(), "sha3_512": "0" * 128})
    with pytest.raises(LegalDocumentRegistryError, match="DIGEST_MISMATCH"):
        LegalDocumentRegistry.get(corrupt.document_id, corrupt.version, collection)

    with pytest.raises(LegalAcceptanceError, match="DIGEST_MISMATCH"):
        LegalDocumentVersion(
            document_id=original.document_id,
            agreement_type=original.agreement_type,
            version=original.version,
            title=original.title,
            jurisdiction=original.jurisdiction,
            locale=original.locale,
            effective_from=original.effective_from,
            status=original.status,
            content_reference=original.content_reference,
            content=original.content,
            sha3_512="f" * 128,
            created_at=original.created_at,
        )


# ARTIFACT: test_legal_document_registry_real_mongo.py
# VERSION: v1.0.1-R1D-B0F-B4-R7-DOCUMENT-RM-CERT
# AUTHORITY BOUNDARY: isolated document persistence evidence only
# TENANT POSTURE: UUID-isolated certification database; no live tenant writes
# FAIL-CLOSED POSTURE: unique-index masking and digest corruption are exposed
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
