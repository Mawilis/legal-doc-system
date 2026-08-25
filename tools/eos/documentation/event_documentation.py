"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE
FILE: tools/eos/documentation/event_documentation.py
===============================================================================
Epitome:
    Automated event documentation and event-driven architecture cataloger for
    Wilsy OS. Maps sovereign event flows, payload schemas, publishing engines,
    and subscriber contracts into immutable DocumentationEntity representations.

Biblical Worth Billions:
    "Their line is gone out through all the earth, and their words to the end
     of the world." — Psalm 19:4

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/documentation/event_documentation.py
===============================================================================
"""

from typing import Dict, List, Any, Optional
from tools.eos.documentation.documentation_contract import (
    DocumentationEntity,
    EntityKind,
    EventSpec,
    VerificationStatus,
)


class EventDocumentationGenerator:
    """
    Specialized documentation builder for Wilsy OS pub/sub event channels,
    event signatures, and event-driven communication pathways.
    """

    @staticmethod
    def generate_event_entity(
        urn: str,
        event_name: str,
        publisher: str,
        subscriber: str,
        purpose: str,
        payload_schema: Dict[str, Any],
        lifecycle_stage: str = "PRODUCTION",
        version: str = "2.0.0",
    ) -> DocumentationEntity:
        """
        Constructs a DocumentationEntity representing a sovereign system event contract.

        Args:
            urn: Target unique documentation URN.
            event_name: Unique event key/topic (e.g. 'tenant.provisioned.v1').
            publisher: Subsystem or engine publishing the event.
            subscriber: Subsystem or engine consuming the event.
            purpose: Functional summary of what the event represents.
            payload_schema: Key-type dictionary schema of the event payload.
            lifecycle_stage: Event lifecycle stage.
            version: Target version string.

        Returns:
            Validated DocumentationEntity contract instance.
        """
        event_spec = EventSpec(
            event_name=event_name,
            publisher=publisher,
            subscriber=subscriber,
            payload_schema=payload_schema,
            lifecycle_stage=lifecycle_stage,
        )

        metadata = {
            "event_name": event_name,
            "publisher": publisher,
            "subscriber": subscriber,
            "payload_schema": payload_schema,
        }

        return DocumentationEntity(
            urn=urn,
            kind=EntityKind.EVENT,
            title=f"Event Contract: {event_name}",
            purpose=purpose,
            module_path=publisher,
            version=version,
            architecture_summary=f"Pub/Sub Event contract published by {publisher} and subscribed by {subscriber}",
            lifecycle_stage=lifecycle_stage,
            events=[event_spec],
            metadata=metadata,
            verification_status=VerificationStatus.VERIFIED,
        )

    @staticmethod
    def generate_event_catalog(entities: List[DocumentationEntity]) -> Dict[str, Any]:
        """
        Aggregates event DocumentationEntity contracts into a structured event catalog.

        Args:
            entities: List of registered DocumentationEntity contracts.

        Returns:
            Dictionary cataloging all registered system events.
        """
        catalog: Dict[str, Any] = {
            "total_events": 0,
            "events": [],
        }

        for entity in entities:
            if entity.kind != EntityKind.EVENT:
                continue

            for evt in entity.events:
                catalog["events"].append({
                    "urn": entity.urn,
                    "event_name": evt.event_name,
                    "publisher": evt.publisher,
                    "subscriber": evt.subscriber,
                    "lifecycle_stage": evt.lifecycle_stage,
                    "payload_schema": evt.payload_schema,
                })

        catalog["total_events"] = len(catalog["events"])
        return catalog
