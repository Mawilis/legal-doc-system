"""
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS - STREAM HEARTBEAT GENERATOR [V1.0.0-PRODUCTION-GRADE]                                                                      ║
║ [EPITOME: SSE CONNECTION KEEPALIVE PULSE WITH ZERO DOWNTIME TIMEOUT PROTECTION]                                                      ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ VERSION: 1.0.0-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | FROZEN ABI COMPLIANT                                           ║
║ ABSOLUTE PATH: server/streaming/heartbeat.py                                                                                         ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
║ • Wilson Khanyezi (Founder/CEO) - Demanded continuous keepalives to prevent proxy idle drops in global deployments.                  ║
║ • AI Engineering (Codex) - IMPLEMENTED: RFC-Compliant SSE heartbeat formatter returning data-framed pulses.                         ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import json
from datetime import datetime, timezone

def generate_heartbeat() -> str:
    """
    Generates an SSE-formatted keepalive ping to maintain active socket connection.
    
    :return: SSE string formatted as 'data: {...}\n\n'
    """
    pulse_payload = {
        "type": "system.heartbeat",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "ALIVE",
        "kernel_ping": "PONG"
    }
    return f"data: {json.dumps(pulse_payload)}\n\n"
