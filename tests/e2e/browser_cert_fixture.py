"""WILSY OS browser-certificate disposable authority fixture.

TITLE: Authenticated browser certificate fixture
VERSION: v1.4.0-INDEPENDENT-SYSTEM-RESPONSE-ACTORS
AUTHORITY: Test-owned disposable Mongo fixture only.
EPITOME: Seed existing EOS repositories with disposable authenticated Legal
         operators, canonical Legal evidence, and a fully correlated current
         tenant-branding chain so Playwright can certify authenticated branding
         HTTP and browser delivery inside one disposable database.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/browser_cert_fixture.py
COLLABORATION / OWNERSHIP: L8-8M-R3 browser certificate; no production authority.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.2.0 seeds active canonical branding entitlement/profile/selection
           and PNG logo/favicon assets for the authenticated tenant-branding browser
           certificate, and limits seed/verify/cleanup to the runner-owned database.
           v1.3.0 adds a durable Tenant Owner identity and canonical Legal plan/subscription/entitlement for commercial-context browser certification.
           v1.1.1 bounds disposable multi-role passwords below bcrypt's 72-byte
           limit without changing authenticated-session or IAM semantics.
           v1.1.0 adds Partner, Attorney, Paralegal, Secretary and Legal Finance
           authenticated sessions plus one canonical matter for the D6B deadline
           browser certificate; no WILSY AI entitlement or deadline is seeded.
           v1.0.1 adds the canonical ACTIVE D22B5 LEGAL_OPERATIONS product
           entitlement required by the production workspace admission gate.
           v1.0.0 establishes UUID-isolated local-replica-set seeding and
           explicit cleanup. It never targets the configured production URI.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identities, credentials and image
                            bytes only; no token, credential, or image body is
                            printed, and cleanup is name-bounded to the runner DB.
TENANT BOUNDARY: One authenticated tenant/principal plus one foreign tenant
                 without membership; all rows remain within the runner database.
AUTHORITY BOUNDARY: Fixture setup only. It grants no production authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import argparse
import json
import os
import struct
from datetime import datetime, timezone, timedelta
from pathlib import Path
from uuid import uuid4
from typing import Any
from urllib.parse import parse_qs, urlsplit
import zlib

from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from hashlib import sha3_256

from tools.eos.auth.system_permission_assignment import SystemPermissionAssignment
from tools.eos.auth.system_permission_assignment_registry import SystemPermissionAssignmentRegistry
from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
    WorkforceRelationshipType,
    WorkforceScopeKind,
)
from tools.eos.workforce.registry import workforce_relationship_registry
from tools.eos.system_services.runtime import build_system_services_runtime
from tools.eos.system_services.security_incident import (
    SecurityIncident,
    SecurityIncidentCategory,
    SecurityIncidentEvent,
)
from tools.eos.system_services.security_incident_registry import (
    COLLECTION as SYSTEM_INCIDENT_COLLECTION,
    EVENT_COLLECTION as SYSTEM_INCIDENT_EVENT_COLLECTION,
    SecurityIncidentRegistry,
)
from tools.eos.system_services.security_incident_assignment_registry import (
    COLLECTION as SYSTEM_INCIDENT_ASSIGNMENT_COLLECTION,
    EVENT_COLLECTION as SYSTEM_INCIDENT_ASSIGNMENT_EVENT_COLLECTION,
    SecurityIncidentAssignmentRegistry,
)
from tools.eos.system_services.security_incident_escalation_service import (
    SecurityIncidentEscalationService,
)
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.kernel import db as kernel_db
from tools.eos.legal_operations.domain.legal_acceptance import (
    AcceptanceMethod,
    LegalAcceptanceEvidence,
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
    canonical_document_digest,
)
from tools.eos.legal_operations.service.legal_acceptance_service import (
    ADMIN_RESPONSIBILITY_BUSINESS_ROLES,
)
from tools.eos.legal_operations.domain.legal_conflict_screening import (
    LegalConflictMatchKind,
    LegalConflictMatchSignal,
    LegalConflictScreeningResult,
    LegalConflictScreeningStatus,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter

from tools.eos.legal_operations.domain.legal_operating_catalogue import CATALOGUE_FINGERPRINT
from tools.eos.legal_operations.domain.tenant_legal_operating_model import TenantLegalOperatingModel
from tools.eos.legal_operations.domain.tenant_legal_workflow_activation import TenantLegalWorkflowActivation
from tools.eos.legal_operations.domain.legal_workflow_definition import LegalWorkflowDefinition
from tools.eos.legal_operations.domain.legal_workflow_stage import LegalWorkflowStage
from tools.eos.legal_operations.domain.legal_workflow_topology import LegalWorkflowTopology
from tools.eos.legal_operations.domain.legal_matter_workflow_instance import LegalMatterWorkflowInstance
from tools.eos.legal_operations.domain.legal_work_materialization_policy import (
    LegalOperationalDueRule,
    LegalWorkMaterializationPolicy,
    LegalWorkMaterializationTemplate,
)
from tools.eos.legal_operations.domain.legal_work_assignment import LegalWorkAssignment
from tools.eos.legal_operations.registry.tenant_legal_operating_model_registry import (
    COLLECTION_NAME as LEGAL_OPERATING_MODEL_COLLECTION,
    TenantLegalOperatingModelRegistry,
)
from tools.eos.legal_operations.registry.tenant_legal_workflow_activation_registry import (
    COLLECTION_NAME as LEGAL_WORKFLOW_ACTIVATION_COLLECTION,
    TenantLegalWorkflowActivationRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_definition_registry import (
    COLLECTION_NAME as LEGAL_WORKFLOW_DEFINITION_COLLECTION,
    LegalWorkflowDefinitionRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_topology_registry import (
    COLLECTION_NAME as LEGAL_WORKFLOW_TOPOLOGY_COLLECTION,
    LegalWorkflowTopologyRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_stage_registry import (
    COLLECTION_NAME as LEGAL_WORKFLOW_STAGE_COLLECTION,
    LegalWorkflowStageRegistry,
)
from tools.eos.legal_operations.registry.legal_matter_workflow_instance_registry import (
    COLLECTION_NAME as LEGAL_WORKFLOW_INSTANCE_COLLECTION,
    LegalMatterWorkflowInstanceRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_gate_satisfaction_registry import (
    COLLECTION_NAME as LEGAL_WORKFLOW_GATE_COLLECTION,
    LegalWorkflowGateSatisfactionRegistry,
)
from tools.eos.legal_operations.registry.legal_matter_workflow_transition_registry import (
    COLLECTION_NAME as LEGAL_WORKFLOW_TRANSITION_COLLECTION,
    LegalMatterWorkflowTransitionRegistry,
)
from tools.eos.legal_operations.registry.legal_work_materialization_policy_registry import (
    COLLECTION_NAME as LEGAL_WORK_MATERIALIZATION_POLICY_COLLECTION,
    LegalWorkMaterializationPolicyRegistry,
)
from tools.eos.legal_operations.registry.legal_work_item_registry import (
    COLLECTION_NAME as LEGAL_WORK_ITEM_COLLECTION,
    LegalWorkItemRegistry,
)
from tools.eos.legal_operations.registry.legal_transition_work_materialization_receipt_registry import (
    COLLECTION_NAME as LEGAL_WORK_MATERIALIZATION_RECEIPT_COLLECTION,
    LegalTransitionWorkMaterializationReceiptRegistry,
)
from tools.eos.legal_operations.registry.legal_work_dependency_edge_registry import (
    COLLECTION_NAME as LEGAL_WORK_DEPENDENCY_COLLECTION,
    LegalWorkDependencyEdgeRegistry,
)
from tools.eos.legal_operations.registry.legal_work_assignment_registry import (
    COLLECTION_NAME as LEGAL_WORK_ASSIGNMENT_COLLECTION,
    LegalWorkAssignmentRegistry,
)
from tools.eos.legal_operations.service.legal_matter_workflow_transition_command_service import (
    LegalMatterWorkflowTransitionCommandService,
)
from tools.eos.legal_operations.service.legal_transition_work_materialization_service import (
    LegalTransitionWorkMaterializationService,
)
from tools.eos.legal_operations.registry.legal_acceptance_registry import (
    LegalAcceptanceRegistry,
)
from tools.eos.legal_operations.registry.legal_document_registry import (
    LegalDocumentRegistry,
)
from tools.eos.legal_operations.registry.legal_conflict_review_registry import (
    LegalConflictReviewRegistry,
)
from tools.eos.legal_operations.registry.legal_conflict_screening_registry import (
    LegalConflictScreeningRegistry,
)
from tools.eos.legal_operations.registry.legal_matter_deadline_registry import (
    LegalMatterDeadlineRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.entitlement import tenant_product_entitlement_registry as entitlement_registry
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_active_entitlement_composition_service import (
    SubscriptionActiveEntitlementCompositionService,
)
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry
from tools.eos.saas.billing import tenant_branding_asset_registry as branding_asset_registry
from tools.eos.saas.billing import tenant_branding_entitlement_registry as branding_entitlement_registry
from tools.eos.saas.billing import tenant_branding_profile_registry as branding_profile_registry
from tools.eos.saas.billing.tenant_branding_vas_policy import TenantBrandingTier
from tools.eos.saas.domain.tenant_branding_asset import (
    TenantBrandingAssetKind,
    register_tenant_branding_asset,
)
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlementState,
    create_tenant_branding_entitlement,
)
from tools.eos.saas.domain.tenant_branding_profile import (
    approve_tenant_branding_profile,
)
from tools.eos.saas.domain.tenant_branding_profile_selection import (
    select_tenant_branding_profile,
)


DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
STATE_VERSION = "v1.5.0-INDEPENDENT-RESPONSE-GOVERNANCE"
SYSTEM_WORKFORCE_SCOPE_ID = "browser-cert-platform-workforce"
BROWSER_CERT_DATABASE_PREFIX = "wilsy_l8_8m_r3_"
BRANDING_EVIDENCE_FINGERPRINT = "f" * 128


def _png_pixel(red: int, green: int, blue: int) -> bytes:
    """Build a deterministic valid 1x1 RGBA PNG for disposable image evidence."""
    def chunk(kind: bytes, payload: bytes) -> bytes:
        checksum = zlib.crc32(kind + payload) & 0xFFFFFFFF
        return struct.pack("!I", len(payload)) + kind + payload + struct.pack("!I", checksum)

    header = struct.pack("!2I5B", 1, 1, 8, 6, 0, 0, 0)
    pixel = zlib.compress(bytes((0, red, green, blue, 255)))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", pixel)
        + chunk(b"IEND", b"")
    )


def _owned_database(client: MongoClient[Any]) -> Any:
    """Return only the UUID-isolated database created by the browser runner."""
    database = client.get_database()
    if not database.name.startswith(BROWSER_CERT_DATABASE_PREFIX):
        raise RuntimeError("BROWSER_CERT_DATABASE_NOT_OWNED")
    return database


def _uri() -> str:
    value = os.getenv("BROWSER_CERT_MONGO_URI", "").strip()
    parsed = urlsplit(value)
    query = parse_qs(parsed.query)
    if (
        parsed.scheme != "mongodb"
        or parsed.hostname not in {"127.0.0.1", "localhost"}
        or parsed.port is None
        or not 1024 <= parsed.port <= 65535
        or parsed.username is not None
        or parsed.password is not None
        or not (
            query.get("replicaSet") == ["wilsyVendorCertRS"]
            or query.get("directConnection") == ["true"]
        )
    ):
        raise RuntimeError("BROWSER_CERT_LOCAL_REPLICA_SET_URI_REQUIRED")
    return value


def _approved_documents(now: datetime) -> tuple[LegalDocumentVersion, ...]:
    values = (
        (LegalAgreementType.INSTITUTIONAL_CHARTER, "WILSY-OS-INSTITUTIONAL-CHARTER"),
        (LegalAgreementType.USER_TERMS, "WILSY-OS-USER-TERMS"),
        (LegalAgreementType.ACCEPTABLE_USE, "WILSY-OS-ACCEPTABLE-USE"),
        (LegalAgreementType.PRIVACY_NOTICE, "WILSY-OS-PRIVACY-NOTICE"),
        (LegalAgreementType.AI_ASSISTANCE_NOTICE, "WILSY-OS-AI-ASSISTANCE-NOTICE"),
        (
            LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE,
            "WILSY-OS-ADMIN-RESPONSIBILITY-NOTICE",
        ),
    )
    result: list[LegalDocumentVersion] = []
    for agreement_type, document_id in values:
        reference = f"browser-cert://{document_id.lower()}/1.0.0-approved"
        content = (
            f"Synthetic browser certification document for {agreement_type.value}. "
            "It is not production legal text and grants no authority."
        )
        result.append(
            LegalDocumentVersion(
                document_id=document_id,
                agreement_type=agreement_type,
                version="1.0.0-APPROVED",
                title=f"Synthetic {agreement_type.value}",
                jurisdiction="ZA",
                locale="en-ZA",
                effective_from=now,
                status=LegalDocumentStatus.APPROVED,
                content_reference=reference,
                content=content,
                sha3_512=canonical_document_digest(content, reference),
                created_at=now,
            )
        )
    return tuple(result)


def _screening(tenant_id: str, suffix: str, now: datetime) -> LegalConflictScreeningResult:
    source_party_fingerprint = "a" * 128
    subject_fingerprint = "b" * 128
    matched_fingerprint = "c" * 128
    return LegalConflictScreeningResult(
        tenant_id=tenant_id,
        screening_id=f"browser-screening-{suffix}",
        source_party_id=f"browser-source-party-{suffix}",
        source_case_matter_id=f"browser-matter-{suffix}",
        source_party_fingerprint=source_party_fingerprint,
        subject_identity_fingerprint=subject_fingerprint,
        screened_at=now,
        status=LegalConflictScreeningStatus.REVIEW_REQUIRED,
        matches=(
            LegalConflictMatchSignal(
                tenant_id=tenant_id,
                subject_identity_fingerprint=subject_fingerprint,
                source_party_id=f"browser-source-party-{suffix}",
                source_case_matter_id=f"browser-matter-{suffix}",
                source_party_fingerprint=source_party_fingerprint,
                matched_party_id=f"browser-match-party-{suffix}",
                matched_case_matter_id=f"browser-match-matter-{suffix}",
                matched_party_fingerprint=matched_fingerprint,
                match_kind=LegalConflictMatchKind.CROSS_MATTER_EXACT_SUBJECT_MATCH,
            ),
        ),
        source_evidence_reference=f"browser-cert-screening:{suffix}",
        source_evidence_fingerprint=matched_fingerprint,
    )


def _seed_branding_chain(
    *,
    tenant_id: str,
    suffix: str,
    now: datetime,
    session: Any,
    collections: dict[str, Any],
    logo_color: tuple[int, int, int],
) -> dict[str, str]:
    """Persist one canonical current logo/favicon chain in the caller transaction."""
    logo_bytes = _png_pixel(*logo_color)
    favicon_bytes = _png_pixel(245, 158, 11)
    logo_reference = f"asset:{tenant_id}:logo:browser-cert"
    favicon_reference = f"asset:{tenant_id}:favicon:browser-cert"
    pending = create_tenant_branding_entitlement(
        tenant_id=tenant_id,
        entitlement_id=f"branding-entitlement-{suffix}",
        branding_tier=TenantBrandingTier.INSTITUTIONAL,
        source_evidence_reference=f"browser-branding-entitlement:{tenant_id}",
        source_evidence_fingerprint=BRANDING_EVIDENCE_FINGERPRINT,
    )
    logo_asset = register_tenant_branding_asset(
        tenant_id=tenant_id,
        asset_reference=logo_reference,
        asset_kind=TenantBrandingAssetKind.LOGO,
        media_type="image/png",
        content=logo_bytes,
        source_evidence_reference=f"browser-branding-logo:{tenant_id}",
        source_evidence_fingerprint=BRANDING_EVIDENCE_FINGERPRINT,
        registered_at=now,
    )
    favicon_asset = register_tenant_branding_asset(
        tenant_id=tenant_id,
        asset_reference=favicon_reference,
        asset_kind=TenantBrandingAssetKind.FAVICON,
        media_type="image/png",
        content=favicon_bytes,
        source_evidence_reference=f"browser-branding-favicon:{tenant_id}",
        source_evidence_fingerprint=BRANDING_EVIDENCE_FINGERPRINT,
        registered_at=now,
    )
    history = collections["branding_entitlement_history"]
    current = collections["branding_entitlement_current"]
    profiles = collections["branding_profiles"]
    selections = collections["branding_selections"]
    profile_current = collections["branding_profile_current"]
    assets = collections["branding_assets"]

    branding_entitlement_registry.create_or_replay(
        pending, history, current, session=session,
    )
    active = branding_entitlement_registry.transition(
        tenant_id=tenant_id,
        entitlement_id=pending.entitlement_id,
        target_state=TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference=f"browser-branding-activation:{tenant_id}",
        evidence_fingerprint=BRANDING_EVIDENCE_FINGERPRINT,
        occurred_at=now,
        history_collection=history,
        current_collection=current,
        session=session,
    ).entitlement
    branding_asset_registry.create_or_replay(
        logo_asset, logo_bytes, assets, session=session,
    )
    branding_asset_registry.create_or_replay(
        favicon_asset, favicon_bytes, assets, session=session,
    )
    profile = approve_tenant_branding_profile(
        entitlement=active,
        profile_id=f"branding-profile-{suffix}",
        profile_label="Synthetic Browser Certification Brand",
        source_evidence_reference=f"browser-branding-profile:{tenant_id}",
        source_evidence_fingerprint=BRANDING_EVIDENCE_FINGERPRINT,
        approved_at=now,
        approval_evidence_reference=f"browser-branding-approval:{tenant_id}",
        approval_evidence_fingerprint=BRANDING_EVIDENCE_FINGERPRINT,
        logo_asset_reference=logo_reference,
        logo_asset_fingerprint=logo_asset.content_fingerprint,
        primary_color="#2563EB",
        secondary_color="#1E3A8A",
        accent_color="#F59E0B",
        email_display_name="Synthetic Browser Certification Brand",
        favicon_asset_reference=favicon_reference,
        favicon_asset_fingerprint=favicon_asset.content_fingerprint,
    )
    branding_profile_registry.persist_profile(profile, profiles, session=session)
    selection = select_tenant_branding_profile(
        profile=profile,
        current_entitlement=active,
        selection_id=f"branding-selection-{suffix}",
        selection_revision=1,
        selected_at=now,
        selection_evidence_reference=f"browser-branding-selection:{tenant_id}",
        selection_evidence_fingerprint=BRANDING_EVIDENCE_FINGERPRINT,
    )
    branding_profile_registry.persist_selection_and_advance_current(
        selection,
        profiles,
        selections,
        profile_current,
        session=session,
    )
    return {
        "logo_reference": logo_reference,
        "logo_fingerprint": logo_asset.content_fingerprint,
        "favicon_reference": favicon_reference,
        "favicon_fingerprint": favicon_asset.content_fingerprint,
    }



def _seed_canonical_specialist_workflows(
    *,
    client: MongoClient[Any],
    database: Any,
    tenant_id: str,
    actors: dict[str, dict[str, str]],
    now: datetime,
) -> dict[str, dict[str, Any]]:
    """Seed durable workflow → transition → materialization → assignment evidence.

    Every specialist receives two canonical materialized work items. The second
    has a receipt-bound predecessor edge and remains blocked by the deliberately
    unsatisfied stage gate. No browser-only rows or role-derived permissions are
    created.
    """
    operating_models = TenantLegalOperatingModelRegistry(
        database[LEGAL_OPERATING_MODEL_COLLECTION]
    )
    activations = TenantLegalWorkflowActivationRegistry(
        database[LEGAL_WORKFLOW_ACTIVATION_COLLECTION]
    )
    definitions = LegalWorkflowDefinitionRegistry(
        database[LEGAL_WORKFLOW_DEFINITION_COLLECTION]
    )
    topologies = LegalWorkflowTopologyRegistry(
        database[LEGAL_WORKFLOW_TOPOLOGY_COLLECTION],
        definition_registry=definitions,
    )
    stages = LegalWorkflowStageRegistry(
        database[LEGAL_WORKFLOW_STAGE_COLLECTION],
        definition_registry=definitions,
        topology_registry=topologies,
    )
    instances = LegalMatterWorkflowInstanceRegistry(
        database[LEGAL_WORKFLOW_INSTANCE_COLLECTION]
    )
    gates = LegalWorkflowGateSatisfactionRegistry(
        database[LEGAL_WORKFLOW_GATE_COLLECTION],
        instance_registry=instances,
        topology_registry=topologies,
        stage_registry=stages,
    )
    transitions = LegalMatterWorkflowTransitionRegistry(
        database[LEGAL_WORKFLOW_TRANSITION_COLLECTION]
    )
    policies = LegalWorkMaterializationPolicyRegistry(
        database[LEGAL_WORK_MATERIALIZATION_POLICY_COLLECTION]
    )
    work_items = LegalWorkItemRegistry(
        database[LEGAL_WORK_ITEM_COLLECTION]
    )
    receipts = LegalTransitionWorkMaterializationReceiptRegistry(
        database[LEGAL_WORK_MATERIALIZATION_RECEIPT_COLLECTION]
    )
    dependencies = LegalWorkDependencyEdgeRegistry(
        database[LEGAL_WORK_DEPENDENCY_COLLECTION]
    )
    assignments = LegalWorkAssignmentRegistry(
        database[LEGAL_WORK_ASSIGNMENT_COLLECTION]
    )

    for registry_value in (
        operating_models,
        activations,
        definitions,
        topologies,
        stages,
        instances,
        gates,
        transitions,
        policies,
        work_items,
        receipts,
        dependencies,
        assignments,
    ):
        registry_value.ensure_indexes()

    definition = LegalWorkflowDefinition(
        workflow_definition_id="browser-cert-specialist-workflow",
        definition_revision=1,
        owner="PLATFORM",
        owner_tenant_id=None,
        name="Browser Certification Specialist Workflow",
        description_reference="browser-cert-specialist-workflow-description",
        required_operating_item_ids=("PRACTICE_DISPUTES",),
        jurisdiction_references=("ZA",),
        catalogue_fingerprint=CATALOGUE_FINGERPRINT,
    )
    target_stage_ids = {
        key: f"stage-review-{key}"
        for key in ("partner", "attorney", "paralegal", "secretary")
    }
    source = LegalWorkflowStage.from_workflow_definition(
        workflow_definition=definition,
        stage_definition_id="stage-intake",
        name="Matter Intake",
        description_reference="browser-cert-stage-intake",
        is_entry_stage=True,
        is_terminal_stage=False,
        successor_stage_ids=tuple(target_stage_ids.values()),
        work_requirement_references=(),
        completion_gate_references=(),
        automation_references=(),
    )
    target_stages = {
        key: LegalWorkflowStage.from_workflow_definition(
            workflow_definition=definition,
            stage_definition_id=stage_id,
            name=f"{key.title()} Review",
            description_reference=f"browser-cert-stage-review:{key}",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
            work_requirement_references=(),
            completion_gate_references=("gate:review",),
            automation_references=(),
        )
        for key, stage_id in target_stage_ids.items()
    }
    topology = LegalWorkflowTopology.from_definition_and_stages(
        workflow_definition=definition,
        stages=(source, *target_stages.values()),
    )
    operating_model = TenantLegalOperatingModel(
        tenant_id=tenant_id,
        operating_model_id="browser-cert-specialist-operating-model",
        revision=1,
        activated_item_ids=("PRACTICE_DISPUTES",),
        effective_from=now,
        supersedes_operating_model_id=None,
        catalogue_fingerprint=CATALOGUE_FINGERPRINT,
    )
    activation = TenantLegalWorkflowActivation.from_authorities(
        activation_id="browser-cert-specialist-workflow-activation",
        activation_revision=1,
        operating_model=operating_model,
        workflow_definition=definition,
        workflow_topology=topology,
        commercial_eligibility_evidence_reference="browser-cert-commercial-eligibility",
        activation_reason_reference="browser-cert-specialist-workflow-activation",
        effective_from=now,
    )

    transition_service = LegalMatterWorkflowTransitionCommandService(
        definition_registry=definitions,
        instance_registry=instances,
        topology_registry=topologies,
        stage_registry=stages,
        gate_registry=gates,
        transition_registry=transitions,
    )
    materializer = LegalTransitionWorkMaterializationService(
        transition_registry=transitions,
        workflow_instance_registry=instances,
        policy_registry=policies,
        work_item_registry=work_items,
        receipt_registry=receipts,
        dependency_registry=dependencies,
    )

    with client.start_session() as session:
        with session.start_transaction():
            operating_models.create_or_replay(operating_model, session=session)
            activations.create_or_replay(activation, session=session)
            definitions.create_or_replay(definition, session=session)
            topologies.create_or_replay(
                topology,
                owner="PLATFORM",
                owner_tenant_id=None,
                session=session,
            )
            stages.create_or_replay(
                source,
                owner="PLATFORM",
                owner_tenant_id=None,
                session=session,
            )
            for target_stage in target_stages.values():
                stages.create_or_replay(
                    target_stage,
                    owner="PLATFORM",
                    owner_tenant_id=None,
                    session=session,
                )

    seeded: dict[str, dict[str, Any]] = {}
    assignment_authority_principal = actors["tenant_owner"]["principal_id"]
    for actor_key, target_stage in target_stages.items():
        actor = actors[actor_key]
        matter_id = f"browser-specialist-matter-{actor_key}-{tenant_id}"
        instance_id = f"browser-specialist-instance-{actor_key}-{tenant_id}"
        transition_id = f"browser-specialist-transition-{actor_key}-{tenant_id}"
        policy_id = f"browser-specialist-policy-{actor_key}-{tenant_id}"
        instance = LegalMatterWorkflowInstance.from_authorities(
            workflow_instance_id=instance_id,
            case_matter_id=matter_id,
            activation=activation,
            workflow_definition=definition,
            workflow_topology=topology,
            started_at=now,
            started_by_principal_id=actor["principal_id"],
            start_authorization_evidence_reference=f"browser-cert-workflow-start:{actor_key}:{tenant_id}",
        )
        first_template_id = f"template-predecessor-{actor_key}"
        second_template_id = f"template-successor-{actor_key}"
        policy = LegalWorkMaterializationPolicy(
            tenant_id=tenant_id,
            policy_id=policy_id,
            policy_revision=1,
            workflow_definition_id=definition.workflow_definition_id,
            workflow_definition_fingerprint=definition.fingerprint,
            target_stage_definition_id=target_stage.stage_definition_id,
            target_stage_fingerprint=target_stage.fingerprint,
            templates=(
                LegalWorkMaterializationTemplate(
                    work_template_id=first_template_id,
                    title=f"{actor_key.title()} predecessor evidence review",
                    due_rule=LegalOperationalDueRule.NONE,
                    due_offset_seconds=None,
                    dependency_template_ids=(),
                    condition_references=(),
                ),
                LegalWorkMaterializationTemplate(
                    work_template_id=second_template_id,
                    title=f"{actor_key.title()} specialist review",
                    due_rule=LegalOperationalDueRule.NONE,
                    due_offset_seconds=None,
                    dependency_template_ids=(first_template_id,),
                    condition_references=(),
                ),
            ),
        )

        with client.start_session() as session:
            with session.start_transaction():
                instances.create_or_replay(instance, session=session)
                transition = transition_service.execute(
                    tenant_id=tenant_id,
                    transitioned_by_principal_id=actor["principal_id"],
                    transition_id=transition_id,
                    workflow_instance_id=instance_id,
                    target_stage_definition_id=target_stage.stage_definition_id,
                    gate_satisfaction_ids=(),
                    branch_selection_evidence_reference=(
                        f"browser-cert-specialist-branch-selection:{actor_key}:{tenant_id}"
                    ),
                    transitioned_at=now + timedelta(minutes=1),
                    transition_authorization_evidence_reference=(
                        f"browser-cert-transition-authorization:{actor_key}:{tenant_id}"
                    ),
                    session=session,
                )
                policies.create_or_replay(policy, session=session)
                materialized = materializer.materialize(
                    tenant_id,
                    instance_id,
                    transition.transition_id,
                    session=session,
                )
                if materialized.receipt is None or len(materialized.work_items) != 2:
                    raise RuntimeError(
                        f"BROWSER_CERT_SPECIALIST_MATERIALIZATION_INVALID:{actor_key}"
                    )
                assignment_ids: list[str] = []
                for work_item in materialized.work_items:
                    # Keep the durable assignment identity within the domain's
                    # 160-character contract even when a work-item ID is maximal.
                    # Actor + full work-item identity remain collision-resistant.
                    assignment_id = (
                        f"browser-specialist-{actor_key}-"
                        f"{sha3_256(work_item.work_item_id.encode('utf-8')).hexdigest()}"
                    )
                    assignments.persist(
                        LegalWorkAssignment(
                            assignment_id=assignment_id,
                            tenant_id=tenant_id,
                            case_matter_id=matter_id,
                            work_item_id=work_item.work_item_id,
                            assignee_principal_id=actor["principal_id"],
                            assigned_by_principal_id=assignment_authority_principal,
                            assigned_at=now + timedelta(minutes=2),
                            assignment_reason_reference=(
                                f"browser-cert-specialist-responsibility:{actor_key}"
                            ),
                            authorization_evidence_reference=(
                                f"browser-cert-specialist-assignment-evidence:{actor_key}"
                            ),
                            supersedes_assignment_id=None,
                        ),
                        session=session,
                    )
                    assignment_ids.append(assignment_id)

        seeded[actor_key] = {
            "principal_id": actor["principal_id"],
            "matter_id": matter_id,
            "workflow_instance_id": instance_id,
            "workflow_definition_id": definition.workflow_definition_id,
            "workflow_topology_fingerprint": topology.fingerprint,
            "stage_definition_id": target_stage.stage_definition_id,
            "transition_id": transition_id,
            "materialization_receipt_id": materialized.receipt.receipt_id,
            "materialization_receipt_fingerprint": materialized.receipt.fingerprint,
            "work_item_ids": [value.work_item_id for value in materialized.work_items],
            "work_item_fingerprints": [value.fingerprint for value in materialized.work_items],
            "assignment_ids": assignment_ids,
            "predecessor_work_item_id": materialized.work_items[0].work_item_id,
            "successor_work_item_id": materialized.work_items[1].work_item_id,
        }

    return seeded


def seed(state_path: Path) -> None:
    uri = _uri()
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, tz_aware=True)
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or not hello.get("isWritablePrimary"):
            raise RuntimeError("BROWSER_CERT_MONGO_REPLICA_SET_NOT_WRITABLE")
        database = _owned_database(client)
        connected, _ = kernel_db.connect_db(force_reconnect=True)
        if not connected or kernel_db.get_database() is None:
            raise RuntimeError("BROWSER_CERT_KERNEL_DATABASE_UNAVAILABLE")

        suffix = uuid4().hex
        tenant_id = f"browser-tenant-{suffix}"
        actor_specs = (
            ("tenant_owner", "TENANT_OWNER", "tenant_owner", "Owner"),
            ("commercial_admin", "ENTERPRISE_ADMIN", "tenant_owner", "CommercialAdmin"),
            ("partner", "LEGAL_PARTNER", "tenant_legal_partner", "Partner"),
            ("attorney", "LEGAL_ATTORNEY", "tenant_legal_attorney", "Attorney"),
            ("paralegal", "LEGAL_PARALEGAL", "tenant_legal_paralegal", "Paralegal"),
            ("secretary", "LEGAL_SECRETARY", "tenant_legal_secretary", "Secretary"),
            ("finance", "LEGAL_FINANCE", "tenant_legal_finance", "Finance"),
        )
        # BSON stores datetimes at millisecond precision; freeze fixture time
        # to that exact boundary so immutable screening correlation survives
        # the durable write/readback certificate.
        current = datetime.now(timezone.utc)
        now = current.replace(microsecond=(current.microsecond // 1000) * 1000)

        TenantRegistry.create(
            {
                "tenant_id": tenant_id,
                "name": "Synthetic Browser Certification Tenant",
                "alias": f"browser-{suffix}",
                "industry": "Legal",
                "region": "ZA",
                "status": "ACTIVE",
                "verified": True,
            }
        )
        foreign_tenant_id = f"browser-foreign-{suffix}"
        TenantRegistry.create(
            {
                "tenant_id": foreign_tenant_id,
                "name": "Synthetic Foreign Branding Tenant",
                "alias": f"browser-foreign-{suffix}",
                "industry": "Legal",
                "region": "ZA",
                "status": "ACTIVE",
                "verified": True,
            }
        )
        registry = AuthRegistry()
        actors: dict[str, dict[str, str]] = {}
        system_actors: dict[str, dict[str, str]] = {}
        for key, last_name in (
            ("system_triage", "SystemTriage"),
            ("system_responder", "SystemResponder"),
            ("system_requester", "SystemRequester"),
            ("system_approver", "SystemApprover"),
            ("system_executor", "SystemExecutor"),
        ):
            email = f"browser-{key}-{suffix}@example.com"
            user = registry.register_user(
                email=email,
                password=f"Bcert-{key}-{suffix[:12]}!",
                firstName="Synthetic",
                lastName=last_name,
                role="SYSTEM_SERVICES",
                tenantId=tenant_id,
            )
            database["users"].update_one(
                {"user_id": user.id},
                {"$set": {"mfaRegistered": True}},
            )
            system_actors[key] = {
                "principal_id": user.id,
                "email": email,
                "grant_role": "SYSTEM_SERVICES",
            }
        for key, grant_role, business_role, last_name in actor_specs:
            email = f"browser-{key}-{suffix}@example.com"
            user = registry.register_user(
                email=email,
                password=f"Bcert-{key}-{suffix[:12]}!",
                firstName="Synthetic",
                lastName=last_name,
                role=grant_role,
                tenantId=tenant_id,
            )
            database["users"].update_one(
                {"user_id": user.id},
                {"$set": {"mfaRegistered": True}},
            )
            actors[key] = {
                "principal_id": user.id,
                "email": email,
                "grant_role": grant_role,
                "business_role": business_role,
            }

        collections = {
            "principal": database["principal_authorities"],
            "membership": database["tenant_memberships"],
            "business": database["tenant_business_roles"],
            "roles": database["role_assignments"],
            "documents": database["legal_document_versions"],
            "acceptance": database["legal_acceptance_evidence"],
            "screening": database["legal_conflict_screenings"],
            "review": database["legal_conflict_reviews"],
            "lifecycle": database["legal_operations_lifecycle_evidence"],
            "deadline": database["legal_matter_deadlines"],
            "entitlement_history": database["tenant_product_entitlement_history"],
            "entitlement_current": database["tenant_product_entitlement_current"],
            "branding_entitlement_history": database[branding_entitlement_registry.HISTORY_COLLECTION],
            "branding_entitlement_current": database[branding_entitlement_registry.CURRENT_COLLECTION],
            "branding_profiles": database[branding_profile_registry.PROFILE_COLLECTION],
            "branding_selections": database[branding_profile_registry.SELECTION_COLLECTION],
            "branding_profile_current": database[branding_profile_registry.CURRENT_COLLECTION],
            "branding_assets": database[branding_asset_registry.COLLECTION],
        }
        permission_assignment_registry = SystemPermissionAssignmentRegistry(
            database["system_permission_assignments"]
        )
        permission_assignment_registry.ensure_indexes()
        workforce_collection = database[workforce_relationship_registry.COLLECTION_NAME]
        workforce_relationship_registry.ensure_indexes(workforce_collection)
        incident_registry = SecurityIncidentRegistry(
            incidents=database[SYSTEM_INCIDENT_COLLECTION],
            events=database[SYSTEM_INCIDENT_EVENT_COLLECTION],
        )
        incident_registry.ensure_indexes()
        incident_assignment_registry = SecurityIncidentAssignmentRegistry(
            assignments=database[SYSTEM_INCIDENT_ASSIGNMENT_COLLECTION],
            events=database[SYSTEM_INCIDENT_ASSIGNMENT_EVENT_COLLECTION],
        )
        incident_assignment_registry.ensure_indexes()
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business"])
        RoleAssignmentRepository.ensure_indexes(collections["roles"])
        LegalDocumentRegistry.ensure_indexes(collections["documents"])
        LegalAcceptanceRegistry.ensure_indexes(collections["acceptance"])
        LegalConflictScreeningRegistry.ensure_indexes(collections["screening"])
        LegalConflictReviewRegistry.ensure_indexes(collections["review"])
        LegalOperationsLifecycleRegistry.ensure_indexes(collections["lifecycle"])
        LegalMatterDeadlineRegistry.ensure_indexes(collections["deadline"])
        entitlement_registry.ensure_indexes(
            collections["entitlement_history"],
            collections["entitlement_current"],
        )
        branding_entitlement_registry.ensure_indexes(
            collections["branding_entitlement_history"],
            collections["branding_entitlement_current"],
        )
        branding_profile_registry.ensure_indexes(
            collections["branding_profiles"],
            collections["branding_selections"],
            collections["branding_profile_current"],
        )
        branding_asset_registry.ensure_indexes(collections["branding_assets"])

        _, system_authorizer = build_system_services_runtime(
            database,
            platform_workforce_scope_id=SYSTEM_WORKFORCE_SCOPE_ID,
        )

        with client.start_session() as session:
            session.start_transaction(
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
            )
            for actor in actors.values():
                principal_id = actor["principal_id"]
                PrincipalAuthorityRepository.create(
                    PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0),
                    collections["principal"],
                    session=session,
                )
                TenantMembershipRepository.insert(
                    TenantMembershipAuthority(
                        principal_id, tenant_id, TenantMembershipStatus.ACTIVE, 0,
                    ),
                    collections["membership"],
                    session=session,
                )
                TenantBusinessRoleRepository.insert(
                    TenantBusinessRoleAuthority(
                        principal_id, tenant_id, actor["business_role"],
                        TenantBusinessRoleStatus.ACTIVE, 0, now, None,
                    ),
                    collections["business"],
                    session=session,
                )
                RoleAssignmentRepository.insert(
                    RoleAssignmentAuthority(
                        principal_id, tenant_id, actor["grant_role"],
                        RoleAssignmentStatus.ACTIVE, 0,
                    ),
                    collections["roles"],
                    session=session,
                )
            for actor in system_actors.values():
                PrincipalAuthorityRepository.create(
                    PrincipalAuthority(actor["principal_id"], PrincipalStatus.ACTIVE, 0),
                    collections["principal"],
                    session=session,
                )
            for key, permission_ids in (
                ("system_triage", ("system_services:queue:read", "system_services:case:triage")),
                ("system_responder", ("system_services:queue:read", "system_services:incident:escalate")),
                ("system_requester", ("system_services:queue:read", "system_services:incident:escalate")),
                ("system_approver", ("system_services:queue:read", "system_services:incident:response:decide")),
                ("system_executor", (
                    "system_services:queue:read",
                    "system_services:incident:response:execute",
                    "system_permission_assignment:revoke",
                )),
            ):
                principal_id = system_actors[key]["principal_id"]
                for permission_id in permission_ids:
                    permission_assignment_registry.create_or_replay(
                        SystemPermissionAssignment.assign(
                            assignment_id=f"browser-system-permission-{key}-{permission_id.replace(':', '-')}-{suffix}",
                            principal_id=principal_id,
                            permission_id=permission_id,
                            assigned_by_principal_id="browser-cert-independent-iam-issuer",
                            assigned_at=now,
                            assignment_evidence_reference=f"browser-cert-approved:{key}:{permission_id}:{suffix}",
                        ),
                        idempotency_key=f"browser-cert:{key}:{permission_id}:{suffix}",
                        session=session,
                    )
                workforce_relationship_registry.persist_revision(
                    WorkforceRelationship(
                        relationship_id=f"browser-workforce-{key}-{suffix}",
                        revision=1,
                        scope_kind=WorkforceScopeKind.PLATFORM,
                        scope_id=SYSTEM_WORKFORCE_SCOPE_ID,
                        principal_id=principal_id,
                        relationship_type=WorkforceRelationshipType.EMPLOYEE,
                        status=WorkforceRelationshipStatus.ACTIVE,
                        effective_from=now,
                        effective_until=None,
                        status_effective_at=now,
                        reason_reference=f"browser-cert-workforce-approved:{key}:{suffix}",
                        supersedes_fingerprint=None,
                    ),
                    collection=workforce_collection,
                    session=session,
                )
            target_permission_assignment_id = f"browser-target-privileged-activation-{suffix}"
            permission_assignment_registry.create_or_replay(
                SystemPermissionAssignment.assign(
                    assignment_id=target_permission_assignment_id,
                    principal_id=actors["partner"]["principal_id"],
                    permission_id="privileged_activation:issue",
                    assigned_by_principal_id="browser-cert-independent-iam-issuer",
                    assigned_at=now,
                    assignment_evidence_reference=f"browser-cert-target-permission:{suffix}",
                ),
                idempotency_key=f"browser-cert-target-permission:{suffix}",
                session=session,
            )
            branding = _seed_branding_chain(
                tenant_id=tenant_id,
                suffix=suffix,
                now=now,
                session=session,
                collections=collections,
                logo_color=(37, 99, 235),
            )
            foreign_branding = _seed_branding_chain(
                tenant_id=foreign_tenant_id,
                suffix=f"foreign-{suffix}",
                now=now,
                session=session,
                collections=collections,
                logo_color=(220, 38, 38),
            )
            documents = _approved_documents(now)
            for document in documents:
                LegalDocumentRegistry.register(
                    document,
                    collections["documents"],
                    session=session,
                )
            for actor in actors.values():
                principal_id = actor["principal_id"]
                for document in documents:
                    # The server policy requires this sixth document only for
                    # principals whose durable business role carries tenant
                    # administration responsibility. Do not fabricate an
                    # acknowledgement for ordinary Legal practitioners.
                    if (
                        document.agreement_type
                        is LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE
                        and actor["business_role"]
                        not in ADMIN_RESPONSIBILITY_BUSINESS_ROLES
                    ):
                        continue
                    acceptance_method = (
                        AcceptanceMethod.ACKNOWLEDGEMENT
                        if document.agreement_type is LegalAgreementType.INSTITUTIONAL_CHARTER
                        else AcceptanceMethod.ACCEPTANCE
                    )
                    fingerprint = LegalAcceptanceEvidence.fingerprint_payload(
                        tenant_id=tenant_id,
                        principal_id=principal_id,
                        agreement_type=document.agreement_type,
                        document_id=document.document_id,
                        document_version=document.version,
                        document_sha3_512=document.sha3_512,
                        acceptance_method=acceptance_method,
                        locale="en-ZA",
                    )
                    evidence = LegalAcceptanceEvidence(
                        acceptance_id=f"BROWSER-ACCEPT-{uuid4().hex}",
                        tenant_id=tenant_id,
                        principal_id=principal_id,
                        agreement_type=document.agreement_type,
                        document_id=document.document_id,
                        document_version=document.version,
                        document_sha3_512=document.sha3_512,
                        accepted_at=now,
                        acceptance_method=acceptance_method,
                        actor_role_at_acceptance=actor["business_role"],
                        session_id=f"browser-cert:{principal_id}",
                        locale="en-ZA",
                        authority_representation="authenticated_user_acknowledgement_only",
                        evidence_fingerprint=fingerprint,
                        idempotency_key=f"browser-cert:{principal_id}:{document.document_id}",
                    )
                    LegalAcceptanceRegistry.create_or_replay(
                        evidence,
                        collections["acceptance"],
                        idempotency_key=evidence.idempotency_key,
                        session=session,
                    )
            matter_id = f"browser-matter-{suffix}"
            LegalOperationsLifecycleRegistry.create(
                CaseMatter(
                    tenant_id=tenant_id,
                    case_matter_id=matter_id,
                    matter_reference=f"BROWSER-MATTER-{suffix[:12]}",
                    opened_at=now,
                    evidence_reference=f"browser-cert-matter:{matter_id}",
                ),
                collections["lifecycle"],
                session=session,
            )
            screening = _screening(tenant_id, suffix, now)
            LegalConflictScreeningRegistry.persist_screening(
                screening,
                collections["screening"],
                session=session,
            )
            # Create a synthetic tenant-reported incident and assign it through
            # the same EOS authorizer/service used by authenticated HTTP routes.
            reporter = actors["partner"]["principal_id"]
            triage_principal = system_actors["system_triage"]["principal_id"]
            responder_principal = system_actors["system_responder"]["principal_id"]
            incident_fingerprint = sha3_256(
                f"browser-incident:{suffix}".encode("utf-8")
            ).hexdigest()
            incident_id = f"browser-incident-{suffix}"
            incident = SecurityIncident(
                incident_id=incident_id,
                tenant_id=tenant_id,
                reporter_principal_id=reporter,
                idempotency_fingerprint=incident_fingerprint,
                category=SecurityIncidentCategory.SUSPECTED_ACCOUNT_COMPROMISE,
                observed_at=now,
                received_at=now,
            )
            incident_event = SecurityIncidentEvent(
                event_id=f"browser-incident-event-{suffix}",
                incident_id=incident_id,
                tenant_id=tenant_id,
                actor_principal_id=reporter,
                event_type="INCIDENT_REPORTED",
                occurred_at=now,
                fingerprint=sha3_256(f"browser-incident-event:{suffix}".encode("utf-8")).hexdigest(),
            )
            incident_registry.create_or_replay(incident, incident_event, session=session)
            incident_registry.record_platform_audit(
                incident=incident, event=incident_event, session=session,
            )
            escalation = SecurityIncidentEscalationService(
                incidents=incident_registry,
                assignments=incident_assignment_registry,
                authorizer=system_authorizer,
                clock=lambda: now,
            )
            seeded_assignment = escalation.assign(
                actor_principal_id=triage_principal,
                assigned_to_principal_id=responder_principal,
                incident_id=incident_id,
                idempotency_key=f"browser-cert-assignment:{suffix}",
                session=session,
            )
            session.commit_transaction()

        specialist_workflows = _seed_canonical_specialist_workflows(
            client=client,
            database=database,
            tenant_id=tenant_id,
            actors=actors,
            now=now,
        )

        PlanRegistry.provision_indexes()
        plan = PlanRegistry.create(
            {
                "name": "WILSY Legal Enterprise",
                "price": 14400.0,
                "currency": "ZAR",
                "billingFrequency": "annual",
                "planType": "ENTERPRISE",
                "idempotencyKey": f"browser-cert-plan-{tenant_id}",
                "active": True,
                "features": ["legal.core"],
                "metadata": {"certificate": "WILSY-OWNER-BROWSER-CERT"},
                "tags": ["wilsy-owner-browser-cert"],
                "user": "WILSY-OWNER-BROWSER-CERT",
            }
        )
        if plan.get("success") is not True:
            raise RuntimeError("BROWSER_CERT_LEGAL_PLAN_SEED_FAILED")
        commercial_admin = actors["commercial_admin"]
        commercial_admin_identity = SovereignIdentity(
            identity_id=commercial_admin["principal_id"],
            tenant_id=tenant_id,
            username=commercial_admin["email"],
            email=commercial_admin["email"],
            roles=[],
            permissions=[],
            auth_method="BROWSER_CERT",
            status=PrincipalStatus.ACTIVE,
            session_reference=None,
        )
        commercial = SubscriptionActiveEntitlementCompositionService.create(
            {
                "tenantId": tenant_id,
                "planId": plan["plan"].plan_id,
                "startDate": now.isoformat(),
                "idempotencyKey": f"browser-cert-subscription-{tenant_id}",
                "billingMode": "PLATFORM",
                "onboardingRef": f"BROWSER-CERT-{tenant_id}",
                "metadata": {"certificate": "WILSY-OWNER-BROWSER-CERT"},
            },
            commercial_admin_identity,
        )
        if not commercial.legal_entitlement_applicable or commercial.entitlement_issuance_result is None:
            raise RuntimeError("BROWSER_CERT_LEGAL_COMMERCIAL_SEED_FAILED")


        for actor in actors.values():
            user = registry.get_user_by_id(actor["principal_id"])
            if user is None:
                raise RuntimeError("BROWSER_CERT_USER_READBACK_FAILED")
            actor["access_token"] = registry.create_session(user).token
        for actor in system_actors.values():
            user = registry.get_user_by_id(actor["principal_id"])
            if user is None:
                raise RuntimeError("BROWSER_CERT_SYSTEM_USER_READBACK_FAILED")
            actor["access_token"] = registry.create_session(user).token
        partner = actors["partner"]
        state_path.write_text(
            json.dumps(
                {
                    "state_version": STATE_VERSION,
                    "database_name": database.name,
                    "tenant_id": tenant_id,
                    "principal_id": partner["principal_id"],
                    "email": partner["email"],
                    "access_token": partner["access_token"],
                    "actors": actors,
                    "system_actors": system_actors,
                    "system_incident_id": incident_id,
                    "system_assignment_id": seeded_assignment.assignment_id,
                    "system_target_permission_assignment_id": target_permission_assignment_id,
                    "system_workforce_scope_id": SYSTEM_WORKFORCE_SCOPE_ID,
                    "matter_id": matter_id,
                    "screening_id": screening.screening_id,
                    "source_case_matter_id": screening.source_case_matter_id,
                    "foreign_tenant_id": foreign_tenant_id,
                    "branding": branding,
                    "foreign_branding": foreign_branding,
                    "specialist_workflows": specialist_workflows,
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
    finally:
        client.close()


def cleanup() -> None:
    uri = _uri()
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        database = _owned_database(client)
        client.drop_database(database.name)
    finally:
        client.close()


def verify(state_path: Path) -> None:
    uri = _uri()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        database = _owned_database(client)
        specialist_workflows = state.get("specialist_workflows")
        if not isinstance(specialist_workflows, dict) or set(specialist_workflows) != {
            "partner", "attorney", "paralegal", "secretary",
        }:
            raise RuntimeError("BROWSER_CERT_SPECIALIST_WORKFLOW_STATE_INVALID")
        for actor_key, evidence in specialist_workflows.items():
            tenant_id = state["tenant_id"]
            actor = state["actors"][actor_key]
            work_ids = evidence["work_item_ids"]
            assignment_ids = evidence["assignment_ids"]
            instance = database[LEGAL_WORKFLOW_INSTANCE_COLLECTION].find_one({
                "tenant_id": tenant_id,
                "workflow_instance_id": evidence["workflow_instance_id"],
            })
            transition = database[LEGAL_WORKFLOW_TRANSITION_COLLECTION].find_one({
                "tenant_id": tenant_id,
                "transition_id": evidence["transition_id"],
                "workflow_instance_id": evidence["workflow_instance_id"],
                "target_stage_definition_id": evidence["stage_definition_id"],
            })
            receipt = database[LEGAL_WORK_MATERIALIZATION_RECEIPT_COLLECTION].find_one({
                "tenant_id": tenant_id,
                "transition_id": evidence["transition_id"],
                "receipt_id": evidence["materialization_receipt_id"],
                "fingerprint": evidence["materialization_receipt_fingerprint"],
            })
            work_rows = list(database[LEGAL_WORK_ITEM_COLLECTION].find({
                "tenant_id": tenant_id,
                "work_item_id": {"$in": work_ids},
            }))
            dependency = database[LEGAL_WORK_DEPENDENCY_COLLECTION].find_one({
                "tenant_id": tenant_id,
                "source_materialization_receipt_id": evidence["materialization_receipt_id"],
                "predecessor_work_item_id": evidence["predecessor_work_item_id"],
                "successor_work_item_id": evidence["successor_work_item_id"],
            })
            assignment_rows = list(database[LEGAL_WORK_ASSIGNMENT_COLLECTION].find({
                "tenant_id": tenant_id,
                "assignment_id": {"$in": assignment_ids},
                "work_item_id": {"$in": work_ids},
                "assignee_principal_id": actor["principal_id"],
            }))
            if (
                instance is None
                or transition is None
                or receipt is None
                or len(work_rows) != 2
                or dependency is None
                or len(assignment_rows) != 2
                or {row["work_item_id"] for row in assignment_rows} != set(work_ids)
                or any(row.get("tenant_id") != tenant_id for row in work_rows)
                or any(row.get("assignee_principal_id") != actor["principal_id"] for row in assignment_rows)
            ):
                raise RuntimeError(
                    f"BROWSER_CERT_SPECIALIST_DURABLE_LINEAGE_INVALID:{actor_key}"
                )

        screening_count = database["legal_conflict_screenings"].count_documents(
            {"tenant_id": state["tenant_id"], "screening_id": state["screening_id"]}
        )
        review_count = database["legal_conflict_reviews"].count_documents(
            {"tenant_id": state["tenant_id"], "screening_id": state["screening_id"]}
        )
        if screening_count != 1 or review_count != 1:
            raise RuntimeError("BROWSER_CERT_DURABLE_REVIEW_CARDINALITY_INVALID")

        system_actors = state["system_actors"]
        system_actor_ids = [system_actors[key]["principal_id"] for key in (
            "system_requester", "system_approver", "system_executor",
        )]
        if len(set(system_actor_ids)) != 3 or set(system_actor_ids) & {
            state["actors"]["partner"]["principal_id"],
        }:
            raise RuntimeError("BROWSER_CERT_RESPONSE_ACTOR_INDEPENDENCE_INVALID")
        required_permissions = {
            "system_requester": "system_services:incident:escalate",
            "system_approver": "system_services:incident:response:decide",
            "system_executor": "system_services:incident:response:execute",
        }
        for actor_key, permission_id in required_permissions.items():
            principal_id = system_actors[actor_key]["principal_id"]
            permission = database["system_permission_assignments"].find_one({
                "principal_id": principal_id,
                "permission_id": permission_id,
                "status": "ACTIVE",
            })
            workforce = database["workforce_relationship_history"].find_one({
                "principal_id": principal_id,
                "scope_kind": "PLATFORM",
                "scope_id": state["system_workforce_scope_id"],
                "status": "ACTIVE",
            })
            if permission is None or workforce is None:
                raise RuntimeError("BROWSER_CERT_RESPONSE_ACTOR_AUTHORITY_EVIDENCE_INVALID")

        response_request_key = "browser-response-request-" + state["database_name"]
        response_decision_id = "response-" + sha3_256(
            (
                state["system_incident_id"]
                + "\\0"
                + state["system_actors"]["system_requester"]["principal_id"]
                + "\\0"
                + response_request_key
            ).encode("utf-8")
        ).hexdigest()
        decisions = database["system_security_incident_response_decisions"]
        rejection_request_key = "browser-response-rejection-request-" + state["database_name"]
        rejection_decision_id = "response-" + sha3_256(
            (
                state["system_incident_id"]
                + "\\0"
                + system_actors["system_requester"]["principal_id"]
                + "\\0"
                + rejection_request_key
            ).encode("utf-8")
        ).hexdigest()
        rejected = decisions.find_one({"decision_id": rejection_decision_id})
        if (
            rejected is None
            or rejected.get("status") != "REJECTED"
            or rejected.get("revision") != 1
            or rejected.get("requested_by_principal_id") != system_actors["system_requester"]["principal_id"]
            or rejected.get("decided_by_principal_id") != system_actors["system_approver"]["principal_id"]
        ):
            raise RuntimeError("BROWSER_CERT_RESPONSE_REJECTION_BINDING_INVALID")
        decision_events = database["system_security_incident_response_decision_events"]
        rejection_event_keys = [
            f"system-services-response-decision:{rejection_decision_id}:revision:0",
            f"system-services-response-decision:{rejection_decision_id}:revision:1",
        ]
        for revision, event_type in (
            (0, "SECURITY_INCIDENT_RESPONSE_REQUESTED"),
            (1, "SECURITY_INCIDENT_RESPONSE_REJECTED"),
        ):
            event = decision_events.find_one({"decision_id": rejection_decision_id, "revision": revision})
            if event is None or event.get("event_type") != event_type:
                raise RuntimeError("BROWSER_CERT_RESPONSE_REJECTION_EVENT_CHAIN_INVALID")
        if decision_events.count_documents({"decision_id": rejection_decision_id}) != 2:
            raise RuntimeError("BROWSER_CERT_REJECTED_DECISION_MUST_NOT_EXECUTE")
        audit = database["system_platform_audit_events"]
        outbox = database["system_platform_audit_outbox"]
        if audit.count_documents({"event_key": {"$in": rejection_event_keys}}) != 2:
            raise RuntimeError("BROWSER_CERT_RESPONSE_REJECTION_AUDIT_INVALID")
        if outbox.count_documents({
            "event_key": {"$in": rejection_event_keys},
            "status": "PENDING",
            "attempts": 0,
        }) != 2:
            raise RuntimeError("BROWSER_CERT_RESPONSE_REJECTION_OUTBOX_INVALID")

        decision = decisions.find_one({"decision_id": response_decision_id})
        if (
            decision is None
            or decision.get("status") != "APPROVED"
            or decision.get("revision") != 1
            or decision.get("target_principal_id") != state["actors"]["partner"]["principal_id"]
            or decision.get("target_assignment_id") != state["system_target_permission_assignment_id"]
            or decision.get("target_permission_id") != "privileged_activation:issue"
            or decision.get("requested_by_principal_id") != system_actors["system_requester"]["principal_id"]
            or decision.get("decided_by_principal_id") != system_actors["system_approver"]["principal_id"]
            or decision.get("requested_by_principal_id") == decision.get("decided_by_principal_id")
        ):
            raise RuntimeError("BROWSER_CERT_RESPONSE_DECISION_DURABLE_BINDING_INVALID")

        decision_events = database["system_security_incident_response_decision_events"]
        expected_events = {
            0: "SECURITY_INCIDENT_RESPONSE_REQUESTED",
            1: "SECURITY_INCIDENT_RESPONSE_APPROVED",
            2: "SECURITY_INCIDENT_RESPONSE_EXECUTED",
        }
        for revision, event_type in expected_events.items():
            event = decision_events.find_one(
                {"decision_id": response_decision_id, "revision": revision}
            )
            if event is None or event.get("event_type") != event_type:
                raise RuntimeError("BROWSER_CERT_RESPONSE_EVENT_CHAIN_INVALID")
            if revision == 2 and event.get("actor_principal_id") != system_actors["system_executor"]["principal_id"]:
                raise RuntimeError("BROWSER_CERT_RESPONSE_EXECUTOR_EVIDENCE_INVALID")

        event_keys = [
            f"system-services-response-decision:{response_decision_id}:revision:0",
            f"system-services-response-decision:{response_decision_id}:revision:1",
            f"system-services-response-execution:{response_decision_id}:revision:2",
        ]
        audit = database["system_platform_audit_events"]
        outbox = database["system_platform_audit_outbox"]
        if audit.count_documents({"event_key": {"$in": event_keys}}) != 3:
            raise RuntimeError("BROWSER_CERT_RESPONSE_AUDIT_CARDINALITY_INVALID")
        if outbox.count_documents({
            "event_key": {"$in": event_keys},
            "status": "PENDING",
            "attempts": 0,
        }) != 3:
            raise RuntimeError("BROWSER_CERT_RESPONSE_OUTBOX_NOT_PENDING")

        revoked = database["system_permission_assignments"].find_one({
            "assignment_id": state["system_target_permission_assignment_id"],
            "principal_id": state["actors"]["partner"]["principal_id"],
            "permission_id": "privileged_activation:issue",
            "status": "REVOKED",
            "revoked_by_principal_id": state["system_actors"]["system_executor"]["principal_id"],
        })
        if revoked is None:
            raise RuntimeError("BROWSER_CERT_CANONICAL_PERMISSION_REVOCATION_MISSING")
    finally:
        client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Disposable browser-cert fixture")
    parser.add_argument("command", choices=("seed", "verify", "cleanup"))
    parser.add_argument("--state", type=Path)
    args = parser.parse_args()
    if args.command == "seed":
        if args.state is None:
            raise SystemExit("--state is required for seed")
        seed(args.state)
    elif args.command == "verify":
        if args.state is None:
            raise SystemExit("--state is required for verify")
        verify(args.state)
    else:
        cleanup()


if __name__ == "__main__":
    main()


# ARTIFACT: browser_cert_fixture.py
# VERSION: v1.5.0-INDEPENDENT-RESPONSE-GOVERNANCE
# AUTHORITY BOUNDARY: disposable synthetic browser-cert fixture only
# TENANT POSTURE: authenticated tenant and unjoined foreign tenant in a runner-owned disposable database
# FAIL-CLOSED POSTURE: wrong URI, unavailable replica set, and seed failures stop
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
