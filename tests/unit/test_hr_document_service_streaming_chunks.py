"""WILSY OS HR Document F6F Streaming-Chunk Compatibility Certificate.

TITLE: HR Document F6F Streaming Chunk Source Certificate
VERSION: v1.0.0-P0-C12F6F-R4A-STREAMING-CHUNK-SOURCE-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Certify that F6F consumes a one-shot iterable of bytes chunks without requiring
the caller to materialize the complete upload as tuple[bytes, ...].

BOUNDARY:
Provider execution remains once. Transaction, reconciliation, provider-delete,
IAM, HTTP and financial authority remain unchanged.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document_service_streaming_chunks.py
"""

from __future__ import annotations

import hashlib
import inspect
from collections.abc import Iterator
from typing import Any, cast

import pytest

from tools.eos.saas.hr.hr_document_service import (
    HrDocumentServiceInputError,
    _provider_write_once,
    orchestrate_hr_document_ingestion,
)
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryChunkEvidence,
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryWriteIntent,
    HrDocumentBinaryWriteSession,
)


VERSION = (
    "v1.0.0-P0-C12F6F-R4A-"
    "STREAMING-CHUNK-SOURCE-CERT"
)


class SinglePassChunks:
    """One-shot source: a second iteration is an explicit contract failure."""

    def __init__(
        self,
        chunks: tuple[bytes, ...],
    ) -> None:
        self._chunks = chunks
        self.iterations = 0
        self.yield_count = 0

    def __iter__(
        self,
    ) -> Iterator[bytes]:

        self.iterations += 1

        assert self.iterations == 1, (
            "P0_C12F6F_STREAM_SOURCE_REPLAYED"
        )

        for chunk in self._chunks:
            self.yield_count += 1
            yield chunk


class FakeStreamingStorage:
    def __init__(self) -> None:
        self.begin_calls = 0
        self.write_calls = 0
        self.complete_calls = 0
        self.inspect_calls = 0
        self.abort_calls = 0
        self.sequences: list[int] = []
        self.payloads: list[bytes] = []

    def begin(
        self,
        intent: HrDocumentBinaryWriteIntent,
    ) -> HrDocumentBinaryWriteSession:

        self.begin_calls += 1

        return HrDocumentBinaryWriteSession(
            provider_name="f6f-stream-cert",
            write_session_reference="write-session-1",
            storage_reference="storage-reference-1",
            write_intent_fingerprint=intent.fingerprint,
        )

    def write_chunk(
        self,
        intent: HrDocumentBinaryWriteIntent,
        session: HrDocumentBinaryWriteSession,
        *,
        sequence: int,
        chunk: bytes,
    ) -> HrDocumentBinaryChunkEvidence:

        del intent
        del session

        self.write_calls += 1
        self.sequences.append(sequence)
        self.payloads.append(chunk)

        return HrDocumentBinaryChunkEvidence(
            sequence=sequence,
            chunk_length=len(chunk),
            provider_part_reference=(
                f"part-{sequence}"
            ),
        )

    def complete(
        self,
        intent: HrDocumentBinaryWriteIntent,
        session: HrDocumentBinaryWriteSession,
        chunks: tuple[
            HrDocumentBinaryChunkEvidence,
            ...,
        ],
        *,
        observed_length: int,
        observed_fingerprint: str,
    ) -> HrDocumentBinaryObjectEvidence:

        del chunks

        self.complete_calls += 1

        return HrDocumentBinaryObjectEvidence(
            provider_name=session.provider_name,
            storage_reference=session.storage_reference,
            object_version_reference="object-version-1",
            provider_integrity_reference="provider-integrity-1",
            write_intent_fingerprint=intent.fingerprint,
            content_length=observed_length,
            content_fingerprint=observed_fingerprint,
        )

    def inspect(
        self,
        intent: HrDocumentBinaryWriteIntent,
        evidence: HrDocumentBinaryObjectEvidence,
    ) -> HrDocumentBinaryObjectEvidence:

        del intent

        self.inspect_calls += 1

        return evidence

    def abort(
        self,
        intent: HrDocumentBinaryWriteIntent,
        session: HrDocumentBinaryWriteSession,
    ) -> None:

        del intent
        del session

        self.abort_calls += 1


def make_intent() -> HrDocumentBinaryWriteIntent:
    return HrDocumentBinaryWriteIntent(
        tenant_id="tenant-f6f-stream",
        employee_id="employee-f6f-stream",
        document_id="document-f6f-stream",
        document_version_id=(
            "document-version-f6f-stream"
        ),
        ingestion_reference="ingestion-f6f-stream",
        media_type="application/pdf",
        original_filename="stream.pdf",
        admitted_max_content_length=4096,
    )


def test_public_and_private_f6f_chunk_contract_is_not_tuple_only() -> None:
    public_annotation = (
        inspect.signature(
            orchestrate_hr_document_ingestion
        )
        .parameters["chunks"]
        .annotation
    )

    private_annotation = (
        inspect.signature(
            _provider_write_once
        )
        .parameters["chunks"]
        .annotation
    )

    public_text = str(public_annotation)
    private_text = str(private_annotation)

    assert "tuple[bytes" not in public_text, (
        "P0_C12F6F_PUBLIC_CHUNKS_STILL_TUPLE_ONLY"
    )

    assert "tuple[bytes" not in private_text, (
        "P0_C12F6F_PRIVATE_CHUNKS_STILL_TUPLE_ONLY"
    )


def test_f6f_accepts_single_pass_iterable_without_tuple_requirement() -> None:
    intent = make_intent()

    source = SinglePassChunks(
        (
            b"%PDF-1.7\n",
            b"streamed-body-",
            b"%%EOF",
        )
    )

    storage = FakeStreamingStorage()

    # cast(Any, ...) is deliberate: the current production annotation is the
    # contract under test. The test file itself must remain Pyright-clean.
    evidence = _provider_write_once(
        intent=intent,
        chunks=cast(
            Any,
            source,
        ),
        storage=storage,
    )

    expected = b"".join(
        (
            b"%PDF-1.7\n",
            b"streamed-body-",
            b"%%EOF",
        )
    )

    assert source.iterations == 1
    assert source.yield_count == 3

    assert storage.begin_calls == 1
    assert storage.write_calls == 3
    assert storage.complete_calls == 1
    assert storage.inspect_calls == 1
    assert storage.abort_calls == 0

    assert storage.sequences == [
        0,
        1,
        2,
    ]

    assert storage.payloads == [
        b"%PDF-1.7\n",
        b"streamed-body-",
        b"%%EOF",
    ]

    assert (
        evidence.content_length
        == len(expected)
    )

    assert (
        evidence.content_fingerprint
        == hashlib.sha3_512(
            expected
        ).hexdigest()
    )


def test_empty_single_pass_source_rejects_before_provider_begin() -> None:
    intent = make_intent()

    source = SinglePassChunks(
        ()
    )

    storage = FakeStreamingStorage()

    with pytest.raises(
        HrDocumentServiceInputError,
        match="P0_C12F6F_CHUNKS_REQUIRED",
    ):
        _provider_write_once(
            intent=intent,
            chunks=cast(
                Any,
                source,
            ),
            storage=storage,
        )

    assert source.iterations == 1
    assert source.yield_count == 0
    assert storage.begin_calls == 0
    assert storage.write_calls == 0
    assert storage.complete_calls == 0


# ARTIFACT: tests/unit/test_hr_document_service_streaming_chunks.py
# VERSION: v1.0.0-P0-C12F6F-R4A-STREAMING-CHUNK-SOURCE-CERT
# INPUT CONTRACT TARGET: single-pass iterable[bytes]
# FULL UPLOAD TUPLE MATERIALIZATION: prohibited
# PROVIDER EXECUTION: once
# CHUNK SOURCE REPLAY: prohibited
# TRANSACTION / RECONCILIATION AUTHORITY: unchanged
# PROVIDER DELETE AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
