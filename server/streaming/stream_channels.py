"""
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS - STREAM CHANNELS REGISTRY [V1.0.0-PRODUCTION-GRADE]                                                                        ║
║ [EPITOME: AUTHORITATIVE 12-CHANNEL ENDPOINT DEFINITIONS FOR ENTIRE SYSTEM]                                                           ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ VERSION: 1.0.0-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | FROZEN ABI COMPLIANT                                           ║
║ ABSOLUTE PATH: server/streaming/stream_channels.py                                                                                   ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
║ • Wilson Khanyezi (Founder/CEO) - Mandated strict 1:1 mapping between console panels and streaming channels.                          ║
║ • AI Engineering (Codex) - IMPLEMENTED: Immutable constant registry containing all 12 system channel URIs.                           ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

class StreamChannels:
    """Authoritative register of streaming channels matching executive console panels."""
    
    DASHBOARD     = "/stream/dashboard"
    RUNTIME       = "/stream/runtime"
    EVENTS        = "/stream/events"
    ARTIFACTS     = "/stream/artifacts"
    REPORTS       = "/stream/reports"
    GOVERNANCE    = "/stream/governance"
    REPOSITORY    = "/stream/repository"
    PREDICTIONS   = "/stream/predictions"
    DOCUMENTATION = "/stream/documentation"
    VERSIONING    = "/stream/versioning"
    COMPATIBILITY = "/stream/compatibility"
    DIGITAL_TWIN  = "/stream/digital-twin"

    @classmethod
    def all_channels(cls) -> list:
        """Returns list of all active streaming channel endpoints."""
        return [
            cls.DASHBOARD,
            cls.RUNTIME,
            cls.EVENTS,
            cls.ARTIFACTS,
            cls.REPORTS,
            cls.GOVERNANCE,
            cls.REPOSITORY,
            cls.PREDICTIONS,
            cls.DOCUMENTATION,
            cls.VERSIONING,
            cls.COMPATIBILITY,
            cls.DIGITAL_TWIN
        ]

    @classmethod
    def validate_channel(cls, channel: str) -> bool:
        """Validates if a requested endpoint string is an authorized streaming channel."""
        return channel in cls.all_channels()
