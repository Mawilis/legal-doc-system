"""
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS - STREAM SERIALIZER [V1.0.1-PRODUCTION-GRADE]                                                                               ║
║ [EPITOME: JSON DELTA PAYLOAD SERIALIZATION WITH STRICT FROZEN ENVELOPE STRUCTURING]                                                  ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ VERSION: 1.0.1-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | FROZEN ABI COMPLIANT                                           ║
║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/streaming/stream_serializer.py                                          ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ EPITOME:                                                                                                                               ║
║ High-throughput SSE payload serializer converting dictionary state deltas into frozen JSON envelope structures. Enforces strict     ║
║ UTC ISO 8601 timestamping, Pylance/Pyright zero-warning type safety, and ABI contract schema validation prior to socket dispatch.    ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ BIBLICAL WORTH BILLIONS:                                                                                                               ║
║ "Let all things be done decently and in order." — 1 Corinthians 14:40                                                                 ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
║ • Wilson Khanyezi (Founder/CEO) - Enforced exact structured envelope schema matching client expectations.                            ║
║ • AI Engineering (Gemini) - RECTIFIED: Resolved Pylance reportArgumentType by annotating custom_type as Optional[str].                ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Dual-Mode Import Resolution (Package-relative vs Standalone Execution)
try:
    from .stream_contract import FROZEN_CONTRACT_VERSION, verify_contract_integrity
except (ImportError, ValueError):
    from stream_contract import FROZEN_CONTRACT_VERSION, verify_contract_integrity


def serialize_delta(channel: str, payload: Dict[str, Any], custom_type: Optional[str] = None) -> str:
    """
    Serializes state deltas into standard JSON SSE payload envelopes.

    :param channel: Channel endpoint URI (e.g., '/stream/runtime').
    :param payload: Dictionary slice representing the delta update.
    :param custom_type: Optional override for update type identifier.
    :return: Serialized JSON string enclosed in standard SSE envelope.
    """
    if not isinstance(payload, dict):
        raise TypeError(f"[SERIALIZER-ERROR] Stream payload must be a dict, got {type(payload)}")

    channel_clean = channel.replace("/stream/", "")
    event_type = custom_type if custom_type is not None else f"dashboard.update.{channel_clean}"

    envelope: Dict[str, Any] = {
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": FROZEN_CONTRACT_VERSION,
        "payload": payload
    }

    verify_contract_integrity(envelope["version"])
    return json.dumps(envelope)
