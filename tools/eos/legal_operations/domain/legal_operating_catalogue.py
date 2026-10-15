"""TITLE: WILSY OS Global Legal Operating Catalogue.

VERSION: v1.0.1-G7A-GLOBAL-LEGAL-OPERATING-CATALOGUE

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

EPITOME:
    Defines the immutable tenant-neutral vocabulary used to describe global
    Legal operating-model choices without granting tenant activation,
    professional status, regulatory appointment, IAM authority, entitlement,
    subscription, browser routing, legal execution, billing, payment,
    settlement, or financial execution authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_operating_catalogue.py

COLLABORATION / OWNERSHIP:
    G7A owns the canonical tenant-neutral vocabulary. Tenant operating-model,
    workflow, and role-binding layers may consume catalogue facts but retain
    ownership of activation, composition, occupancy, scope, and currentness.

CERTIFICATION / UPDATE DATE:
    2026-10-15.

CHANGELOG:
    v1.0.1 completes sovereign metadata, public authority documentation, and
    the fail-closed end seal without changing catalogue entries or semantics.

COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.

SECURITY / PRIVACY POSTURE:
    Contains no tenant data, principal data, credentials, permissions, client
    data, matter data, personal information, or mutable operational state.

TENANT BOUNDARY:
    Catalogue facts are global and tenant-neutral. Catalogue membership never
    proves that any tenant has activated an item.

AUTHORITY BOUNDARY:
    Descriptive operating-model vocabulary only. Catalogue items do not grant
    identity, membership, business role, authorization role, professional
    qualification, regulatory appointment, matter capacity, permission,
    entitlement, route admission, or execution authority.

COMMERCIAL BOUNDARY:
    Catalogue membership is not plan, subscription, product entitlement,
    feature ownership, pricing, purchase, or billing truth.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains the exclusive financial execution and settlement
    authority.

FAIL-CLOSED POSTURE:
    Unknown dimensions, identifiers, malformed values, duplicate identifiers,
    and caller-supplied invalid descriptors or evidence flags reject without
    aliases, coercion, or defaults.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha3_512
import json
from types import MappingProxyType
from typing import Final, Mapping


VERSION: Final[str] = "v1.0.1-G7A-GLOBAL-LEGAL-OPERATING-CATALOGUE"
SCHEMA: Final[str] = "WILSY-GLOBAL-LEGAL-OPERATING-CATALOGUE/V1"
CATALOGUE_IDENTITY: Final[str] = "WILSY_GLOBAL_LEGAL_OPERATING_CATALOGUE"


class LegalOperatingCatalogueError(ValueError):
    """Stable fail-closed pure-domain catalogue validation failure.

    The error discloses only a bounded code, performs no mutation, and grants
    no tenant, IAM, professional, commercial, or financial authority.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalOperatingDimension(StrEnum):
    """Canonical tenant-neutral dimensions for descriptive Legal vocabulary.

    A dimension is classification metadata only. It is not tenant activation,
    principal occupancy, scope, authorization, entitlement, or execution.
    """

    ORGANIZATIONAL_PERSONA = "ORGANIZATIONAL_PERSONA"
    SENIORITY_POSITION = "SENIORITY_POSITION"
    PROFESSIONAL_QUALIFICATION = "PROFESSIONAL_QUALIFICATION"
    TRAINING_STATUS = "TRAINING_STATUS"
    REGULATORY_APPOINTMENT = "REGULATORY_APPOINTMENT"
    LEADERSHIP_APPOINTMENT = "LEADERSHIP_APPOINTMENT"
    PRACTICE_FUNCTION = "PRACTICE_FUNCTION"
    LEGAL_OPERATIONS_FUNCTION = "LEGAL_OPERATIONS_FUNCTION"
    RISK_COMPLIANCE_FUNCTION = "RISK_COMPLIANCE_FUNCTION"
    KNOWLEDGE_FUNCTION = "KNOWLEDGE_FUNCTION"
    FINANCE_COMMERCIAL_FUNCTION = "FINANCE_COMMERCIAL_FUNCTION"
    TECHNOLOGY_DATA_FUNCTION = "TECHNOLOGY_DATA_FUNCTION"
    PEOPLE_FUNCTION = "PEOPLE_FUNCTION"
    BUSINESS_DEVELOPMENT_FUNCTION = "BUSINESS_DEVELOPMENT_FUNCTION"
    INFORMATION_DELIVERY_FUNCTION = "INFORMATION_DELIVERY_FUNCTION"
    FIRM_OPERATIONS_FUNCTION = "FIRM_OPERATIONS_FUNCTION"
    EXTERNAL_ECOSYSTEM_PERSONA = "EXTERNAL_ECOSYSTEM_PERSONA"
    JURISDICTION_OVERLAY = "JURISDICTION_OVERLAY"


@dataclass(frozen=True, slots=True)
class LegalOperatingCatalogueItem:
    """One immutable descriptive catalogue item with evidence indicators.

    Construction validates canonical shape only and performs no persistence,
    transaction, authorization, entitlement, or financial mutation.
    """

    item_id: str
    dimension: LegalOperatingDimension
    label: str
    description: str
    requires_professional_evidence: bool = False
    requires_appointment_evidence: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.item_id, str) or not self.item_id:
            raise LegalOperatingCatalogueError(
                "G7A_ITEM_ID_INVALID"
            )
        if self.item_id != self.item_id.strip():
            raise LegalOperatingCatalogueError(
                "G7A_ITEM_ID_INVALID"
            )
        if self.item_id.upper() != self.item_id:
            raise LegalOperatingCatalogueError(
                "G7A_ITEM_ID_INVALID"
            )
        if not isinstance(self.dimension, LegalOperatingDimension):
            raise LegalOperatingCatalogueError(
                "G7A_DIMENSION_INVALID"
            )
        for value in (self.label, self.description):
            if (
                not isinstance(value, str)
                or not value.strip()
                or value != value.strip()
            ):
                raise LegalOperatingCatalogueError(
                    "G7A_DESCRIPTOR_INVALID"
                )
        for value in (
            self.requires_professional_evidence,
            self.requires_appointment_evidence,
        ):
            if not isinstance(value, bool):
                raise LegalOperatingCatalogueError(
                    "G7A_EVIDENCE_FLAG_INVALID"
                )

    def semantic_dict(self) -> dict[str, object]:
        """Return the deterministic fingerprint payload for this item.

        The returned copy carries descriptive fields only and cannot activate
        a tenant, bind a principal, grant access, or authorize execution.
        """
        return {
            "item_id": self.item_id,
            "dimension": self.dimension.value,
            "label": self.label,
            "description": self.description,
            "requires_professional_evidence":
                self.requires_professional_evidence,
            "requires_appointment_evidence":
                self.requires_appointment_evidence,
        }


_CANONICAL_ITEMS: Final[
    tuple[LegalOperatingCatalogueItem, ...]
] = (
    # Existing WILSY Legal operating personas.
    LegalOperatingCatalogueItem(
        "PERSONA_PARTNER",
        LegalOperatingDimension.ORGANIZATIONAL_PERSONA,
        "Partner",
        "Law-firm partner organisational persona.",
    ),
    LegalOperatingCatalogueItem(
        "PERSONA_ATTORNEY",
        LegalOperatingDimension.ORGANIZATIONAL_PERSONA,
        "Attorney",
        "Law-firm legal-practitioner organisational persona.",
    ),
    LegalOperatingCatalogueItem(
        "PERSONA_PARALEGAL",
        LegalOperatingDimension.ORGANIZATIONAL_PERSONA,
        "Paralegal",
        "Paralegal organisational persona.",
    ),
    LegalOperatingCatalogueItem(
        "PERSONA_LEGAL_SECRETARY",
        LegalOperatingDimension.ORGANIZATIONAL_PERSONA,
        "Legal Secretary",
        "Legal secretarial organisational persona.",
    ),
    LegalOperatingCatalogueItem(
        "PERSONA_LEGAL_FINANCE",
        LegalOperatingDimension.ORGANIZATIONAL_PERSONA,
        "Legal Finance",
        "Law-firm finance organisational persona.",
    ),
    LegalOperatingCatalogueItem(
        "PERSONA_SHERIFF",
        LegalOperatingDimension.ORGANIZATIONAL_PERSONA,
        "Sheriff",
        "Process-service sheriff organisational persona.",
    ),
    LegalOperatingCatalogueItem(
        "PERSONA_DEPUTY",
        LegalOperatingDimension.ORGANIZATIONAL_PERSONA,
        "Deputy",
        "Process-service deputy organisational persona.",
    ),
    LegalOperatingCatalogueItem(
        "PERSONA_CLIENT",
        LegalOperatingDimension.EXTERNAL_ECOSYSTEM_PERSONA,
        "Legal Client",
        "External legal-client ecosystem persona.",
    ),

    # Representative seniority / organisational position.
    LegalOperatingCatalogueItem(
        "SENIORITY_MANAGING_PARTNER",
        LegalOperatingDimension.SENIORITY_POSITION,
        "Managing Partner",
        "Firm-wide managing-partner position.",
    ),
    LegalOperatingCatalogueItem(
        "SENIORITY_EQUITY_PARTNER",
        LegalOperatingDimension.SENIORITY_POSITION,
        "Equity Partner",
        "Equity-partner position.",
    ),
    LegalOperatingCatalogueItem(
        "SENIORITY_NON_EQUITY_PARTNER",
        LegalOperatingDimension.SENIORITY_POSITION,
        "Non-Equity Partner",
        "Non-equity-partner position.",
    ),
    LegalOperatingCatalogueItem(
        "SENIORITY_COUNSEL",
        LegalOperatingDimension.SENIORITY_POSITION,
        "Counsel",
        "Counsel or equivalent senior lawyer position.",
    ),
    LegalOperatingCatalogueItem(
        "SENIORITY_SENIOR_ASSOCIATE",
        LegalOperatingDimension.SENIORITY_POSITION,
        "Senior Associate",
        "Senior-associate position.",
    ),
    LegalOperatingCatalogueItem(
        "SENIORITY_ASSOCIATE",
        LegalOperatingDimension.SENIORITY_POSITION,
        "Associate",
        "Associate position.",
    ),

    # Qualification archetypes. These never prove qualification by catalogue.
    LegalOperatingCatalogueItem(
        "QUALIFICATION_ATTORNEY",
        LegalOperatingDimension.PROFESSIONAL_QUALIFICATION,
        "Attorney",
        "Attorney qualification archetype.",
        requires_professional_evidence=True,
    ),
    LegalOperatingCatalogueItem(
        "QUALIFICATION_SOLICITOR",
        LegalOperatingDimension.PROFESSIONAL_QUALIFICATION,
        "Solicitor",
        "Solicitor qualification archetype.",
        requires_professional_evidence=True,
    ),
    LegalOperatingCatalogueItem(
        "QUALIFICATION_ADVOCATE",
        LegalOperatingDimension.PROFESSIONAL_QUALIFICATION,
        "Advocate",
        "Advocate qualification archetype.",
        requires_professional_evidence=True,
    ),
    LegalOperatingCatalogueItem(
        "QUALIFICATION_BARRISTER",
        LegalOperatingDimension.PROFESSIONAL_QUALIFICATION,
        "Barrister",
        "Barrister qualification archetype.",
        requires_professional_evidence=True,
    ),
    LegalOperatingCatalogueItem(
        "QUALIFICATION_REGISTERED_FOREIGN_LAWYER",
        LegalOperatingDimension.PROFESSIONAL_QUALIFICATION,
        "Registered Foreign Lawyer",
        "Foreign-lawyer qualification or registration archetype.",
        requires_professional_evidence=True,
    ),
    LegalOperatingCatalogueItem(
        "QUALIFICATION_CONVEYANCER",
        LegalOperatingDimension.PROFESSIONAL_QUALIFICATION,
        "Conveyancer",
        "Conveyancer qualification archetype.",
        requires_professional_evidence=True,
    ),
    LegalOperatingCatalogueItem(
        "QUALIFICATION_NOTARY",
        LegalOperatingDimension.PROFESSIONAL_QUALIFICATION,
        "Notary",
        "Notarial qualification archetype.",
        requires_professional_evidence=True,
    ),

    # Training status.
    LegalOperatingCatalogueItem(
        "TRAINING_TRAINEE_SOLICITOR",
        LegalOperatingDimension.TRAINING_STATUS,
        "Trainee Solicitor",
        "Trainee-solicitor status archetype.",
        requires_professional_evidence=True,
    ),
    LegalOperatingCatalogueItem(
        "TRAINING_CANDIDATE_LEGAL_PRACTITIONER",
        LegalOperatingDimension.TRAINING_STATUS,
        "Candidate Legal Practitioner",
        "Candidate legal-practitioner status archetype.",
        requires_professional_evidence=True,
    ),
    LegalOperatingCatalogueItem(
        "TRAINING_ARTICLED_STUDENT",
        LegalOperatingDimension.TRAINING_STATUS,
        "Articled Student",
        "Articled-student status archetype.",
        requires_professional_evidence=True,
    ),
    LegalOperatingCatalogueItem(
        "TRAINING_PUPIL",
        LegalOperatingDimension.TRAINING_STATUS,
        "Pupil",
        "Pupil or pupil-barrister status archetype.",
        requires_professional_evidence=True,
    ),

    # Regulatory appointments.
    LegalOperatingCatalogueItem(
        "APPOINTMENT_COLP",
        LegalOperatingDimension.REGULATORY_APPOINTMENT,
        "COLP",
        "Compliance Officer for Legal Practice appointment archetype.",
        requires_appointment_evidence=True,
    ),
    LegalOperatingCatalogueItem(
        "APPOINTMENT_COFA",
        LegalOperatingDimension.REGULATORY_APPOINTMENT,
        "COFA",
        "Compliance Officer for Finance and Administration appointment archetype.",
        requires_appointment_evidence=True,
    ),
    LegalOperatingCatalogueItem(
        "APPOINTMENT_MLRO",
        LegalOperatingDimension.REGULATORY_APPOINTMENT,
        "MLRO",
        "Money Laundering Reporting Officer appointment archetype.",
        requires_appointment_evidence=True,
    ),
    LegalOperatingCatalogueItem(
        "APPOINTMENT_DPO",
        LegalOperatingDimension.REGULATORY_APPOINTMENT,
        "Data Protection Officer",
        "Data-protection regulatory appointment archetype.",
        requires_appointment_evidence=True,
    ),
    LegalOperatingCatalogueItem(
        "APPOINTMENT_TRUST_SIGNATORY",
        LegalOperatingDimension.REGULATORY_APPOINTMENT,
        "Trust Signatory",
        "Trust-account signatory appointment archetype.",
        requires_appointment_evidence=True,
    ),

    # Leadership.
    LegalOperatingCatalogueItem(
        "LEADERSHIP_PRACTICE_GROUP_HEAD",
        LegalOperatingDimension.LEADERSHIP_APPOINTMENT,
        "Practice Group Head",
        "Practice-group leadership appointment.",
    ),
    LegalOperatingCatalogueItem(
        "LEADERSHIP_OFFICE_MANAGING_PARTNER",
        LegalOperatingDimension.LEADERSHIP_APPOINTMENT,
        "Office Managing Partner",
        "Office-level managing-partner appointment.",
    ),
    LegalOperatingCatalogueItem(
        "LEADERSHIP_MATTER_PARTNER",
        LegalOperatingDimension.LEADERSHIP_APPOINTMENT,
        "Matter Partner",
        "Matter leadership appointment archetype.",
    ),
    LegalOperatingCatalogueItem(
        "LEADERSHIP_SUPERVISING_LAWYER",
        LegalOperatingDimension.LEADERSHIP_APPOINTMENT,
        "Supervising Lawyer",
        "Supervising-lawyer appointment archetype.",
    ),

    # Legal practice / delivery functions.
    LegalOperatingCatalogueItem(
        "PRACTICE_DISPUTES",
        LegalOperatingDimension.PRACTICE_FUNCTION,
        "Disputes",
        "Disputes and litigation practice function.",
    ),
    LegalOperatingCatalogueItem(
        "PRACTICE_CORPORATE",
        LegalOperatingDimension.PRACTICE_FUNCTION,
        "Corporate",
        "Corporate legal practice function.",
    ),
    LegalOperatingCatalogueItem(
        "PRACTICE_M_AND_A",
        LegalOperatingDimension.PRACTICE_FUNCTION,
        "Mergers and Acquisitions",
        "Mergers-and-acquisitions practice function.",
    ),
    LegalOperatingCatalogueItem(
        "PRACTICE_EMPLOYMENT",
        LegalOperatingDimension.PRACTICE_FUNCTION,
        "Employment",
        "Employment and labour practice function.",
    ),
    LegalOperatingCatalogueItem(
        "PRACTICE_REAL_ESTATE",
        LegalOperatingDimension.PRACTICE_FUNCTION,
        "Real Estate",
        "Real-estate and property practice function.",
    ),
    LegalOperatingCatalogueItem(
        "PRACTICE_INTELLECTUAL_PROPERTY",
        LegalOperatingDimension.PRACTICE_FUNCTION,
        "Intellectual Property",
        "Intellectual-property practice function.",
    ),

    # Legal operations.
    LegalOperatingCatalogueItem(
        "LEGAL_OPS_MANAGEMENT",
        LegalOperatingDimension.LEGAL_OPERATIONS_FUNCTION,
        "Legal Operations",
        "Legal-operations management function.",
    ),
    LegalOperatingCatalogueItem(
        "LEGAL_OPS_PROJECT_MANAGEMENT",
        LegalOperatingDimension.LEGAL_OPERATIONS_FUNCTION,
        "Legal Project Management",
        "Legal project-management function.",
    ),
    LegalOperatingCatalogueItem(
        "LEGAL_OPS_RESOURCE_MANAGEMENT",
        LegalOperatingDimension.LEGAL_OPERATIONS_FUNCTION,
        "Resource Management",
        "Legal resource-management function.",
    ),

    # Risk/compliance.
    LegalOperatingCatalogueItem(
        "RISK_CONFLICTS",
        LegalOperatingDimension.RISK_COMPLIANCE_FUNCTION,
        "Conflicts",
        "Conflict-checking and conflict-risk function.",
    ),
    LegalOperatingCatalogueItem(
        "RISK_CLIENT_INTAKE",
        LegalOperatingDimension.RISK_COMPLIANCE_FUNCTION,
        "Client Intake",
        "Client and matter intake risk function.",
    ),
    LegalOperatingCatalogueItem(
        "RISK_AML_KYC",
        LegalOperatingDimension.RISK_COMPLIANCE_FUNCTION,
        "AML / KYC",
        "Anti-money-laundering and know-your-client function.",
    ),
    LegalOperatingCatalogueItem(
        "RISK_SANCTIONS",
        LegalOperatingDimension.RISK_COMPLIANCE_FUNCTION,
        "Sanctions",
        "Sanctions-screening and compliance function.",
    ),
    LegalOperatingCatalogueItem(
        "RISK_PROFESSIONAL",
        LegalOperatingDimension.RISK_COMPLIANCE_FUNCTION,
        "Professional Risk",
        "Professional-risk function.",
    ),

    # Knowledge.
    LegalOperatingCatalogueItem(
        "KNOWLEDGE_PSL",
        LegalOperatingDimension.KNOWLEDGE_FUNCTION,
        "Knowledge Lawyer / PSL",
        "Professional-support or knowledge-lawyer function.",
    ),
    LegalOperatingCatalogueItem(
        "KNOWLEDGE_RESEARCH",
        LegalOperatingDimension.KNOWLEDGE_FUNCTION,
        "Legal Research",
        "Legal research and library function.",
    ),
    LegalOperatingCatalogueItem(
        "KNOWLEDGE_MANAGEMENT",
        LegalOperatingDimension.KNOWLEDGE_FUNCTION,
        "Knowledge Management",
        "Legal knowledge-management function.",
    ),

    # Finance / commercial.
    LegalOperatingCatalogueItem(
        "FINANCE_BILLING",
        LegalOperatingDimension.FINANCE_COMMERCIAL_FUNCTION,
        "Billing",
        "Billing administration function.",
    ),
    LegalOperatingCatalogueItem(
        "FINANCE_PRICING",
        LegalOperatingDimension.FINANCE_COMMERCIAL_FUNCTION,
        "Pricing",
        "Legal pricing function.",
    ),
    LegalOperatingCatalogueItem(
        "FINANCE_COLLECTIONS",
        LegalOperatingDimension.FINANCE_COMMERCIAL_FUNCTION,
        "Collections",
        "Collections administration function.",
    ),
    LegalOperatingCatalogueItem(
        "FINANCE_TRUST_ACCOUNTING",
        LegalOperatingDimension.FINANCE_COMMERCIAL_FUNCTION,
        "Trust Accounting",
        "Trust-account administration function; no execution authority.",
    ),

    # Technology / data.
    LegalOperatingCatalogueItem(
        "TECH_LEGAL_TECH",
        LegalOperatingDimension.TECHNOLOGY_DATA_FUNCTION,
        "Legal Technology",
        "Legal-technology function.",
    ),
    LegalOperatingCatalogueItem(
        "TECH_SECURITY",
        LegalOperatingDimension.TECHNOLOGY_DATA_FUNCTION,
        "Cybersecurity",
        "Cybersecurity function.",
    ),
    LegalOperatingCatalogueItem(
        "TECH_DATA",
        LegalOperatingDimension.TECHNOLOGY_DATA_FUNCTION,
        "Data",
        "Data and analytics function.",
    ),
    LegalOperatingCatalogueItem(
        "TECH_AI_INNOVATION",
        LegalOperatingDimension.TECHNOLOGY_DATA_FUNCTION,
        "AI and Innovation",
        "AI and innovation operating function.",
    ),

    # People.
    LegalOperatingCatalogueItem(
        "PEOPLE_HR",
        LegalOperatingDimension.PEOPLE_FUNCTION,
        "People / HR",
        "People and human-resources function.",
    ),
    LegalOperatingCatalogueItem(
        "PEOPLE_RECRUITMENT",
        LegalOperatingDimension.PEOPLE_FUNCTION,
        "Recruitment",
        "Recruitment function.",
    ),
    LegalOperatingCatalogueItem(
        "PEOPLE_LEARNING",
        LegalOperatingDimension.PEOPLE_FUNCTION,
        "Learning and Development",
        "Learning and professional-development function.",
    ),

    # Business development.
    LegalOperatingCatalogueItem(
        "BD_MARKETING",
        LegalOperatingDimension.BUSINESS_DEVELOPMENT_FUNCTION,
        "Marketing",
        "Marketing function.",
    ),
    LegalOperatingCatalogueItem(
        "BD_CLIENT_RELATIONSHIP",
        LegalOperatingDimension.BUSINESS_DEVELOPMENT_FUNCTION,
        "Client Relationship",
        "Client-relationship management function.",
    ),
    LegalOperatingCatalogueItem(
        "BD_BUSINESS_DEVELOPMENT",
        LegalOperatingDimension.BUSINESS_DEVELOPMENT_FUNCTION,
        "Business Development",
        "Business-development function.",
    ),

    # Information delivery.
    LegalOperatingCatalogueItem(
        "INFO_RECORDS",
        LegalOperatingDimension.INFORMATION_DELIVERY_FUNCTION,
        "Records",
        "Records-management function.",
    ),
    LegalOperatingCatalogueItem(
        "INFO_DOCUMENT_PRODUCTION",
        LegalOperatingDimension.INFORMATION_DELIVERY_FUNCTION,
        "Document Production",
        "Document-production function.",
    ),
    LegalOperatingCatalogueItem(
        "INFO_EDISCOVERY",
        LegalOperatingDimension.INFORMATION_DELIVERY_FUNCTION,
        "eDiscovery",
        "Electronic-discovery function.",
    ),
    LegalOperatingCatalogueItem(
        "INFO_LITIGATION_SUPPORT",
        LegalOperatingDimension.INFORMATION_DELIVERY_FUNCTION,
        "Litigation Support",
        "Litigation-support function.",
    ),

    # Firm operations.
    LegalOperatingCatalogueItem(
        "OPERATIONS_COO",
        LegalOperatingDimension.FIRM_OPERATIONS_FUNCTION,
        "Chief Operating Officer",
        "Firm COO operating function.",
    ),
    LegalOperatingCatalogueItem(
        "OPERATIONS_PRACTICE_MANAGER",
        LegalOperatingDimension.FIRM_OPERATIONS_FUNCTION,
        "Practice Manager",
        "Practice-management function.",
    ),
    LegalOperatingCatalogueItem(
        "OPERATIONS_OFFICE_MANAGER",
        LegalOperatingDimension.FIRM_OPERATIONS_FUNCTION,
        "Office Manager",
        "Office-management function.",
    ),
    LegalOperatingCatalogueItem(
        "OPERATIONS_PROCUREMENT",
        LegalOperatingDimension.FIRM_OPERATIONS_FUNCTION,
        "Procurement",
        "Procurement function.",
    ),
)

_items_by_id: dict[str, LegalOperatingCatalogueItem] = {}
_items_by_dimension: dict[
    LegalOperatingDimension,
    tuple[LegalOperatingCatalogueItem, ...],
] = {}

for _item in _CANONICAL_ITEMS:
    if _item.item_id in _items_by_id:
        raise LegalOperatingCatalogueError(
            "G7A_DUPLICATE_ITEM_ID"
        )
    _items_by_id[_item.item_id] = _item

for _dimension in LegalOperatingDimension:
    _items_by_dimension[_dimension] = tuple(
        item
        for item in _CANONICAL_ITEMS
        if item.dimension is _dimension
    )

ITEMS_BY_ID: Final[
    Mapping[str, LegalOperatingCatalogueItem]
] = MappingProxyType(_items_by_id)

ITEMS_BY_DIMENSION: Final[
    Mapping[
        LegalOperatingDimension,
        tuple[LegalOperatingCatalogueItem, ...],
    ]
] = MappingProxyType(_items_by_dimension)


def _catalogue_fingerprint() -> str:
    payload = {
        "schema": SCHEMA,
        "identity": CATALOGUE_IDENTITY,
        "version": VERSION,
        "items": [
            item.semantic_dict()
            for item in _CANONICAL_ITEMS
        ],
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return sha3_512(
        canonical.encode("utf-8")
    ).hexdigest()


CATALOGUE_FINGERPRINT: Final[str] = _catalogue_fingerprint()


def list_legal_operating_items(
) -> tuple[LegalOperatingCatalogueItem, ...]:
    """Return all immutable catalogue items in canonical fingerprint order."""
    return _CANONICAL_ITEMS


def list_legal_operating_dimensions(
) -> tuple[LegalOperatingDimension, ...]:
    """Return every descriptive dimension in deterministic declaration order."""
    return tuple(LegalOperatingDimension)


def list_items_for_dimension(
    dimension: LegalOperatingDimension | str,
) -> tuple[LegalOperatingCatalogueItem, ...]:
    """Return immutable items for one exact dimension or fail closed.

    The lookup is global and tenant-neutral, performs no mutation, and does not
    infer aliases, tenant activation, entitlement, permission, or authority.
    """
    try:
        normalized = LegalOperatingDimension(dimension)
    except (TypeError, ValueError) as error:
        raise LegalOperatingCatalogueError(
            "G7A_UNKNOWN_DIMENSION"
        ) from error
    return ITEMS_BY_DIMENSION[normalized]


def get_legal_operating_item(
    item_id: str,
) -> LegalOperatingCatalogueItem:
    """Resolve one exact canonical item identifier or fail closed.

    Resolution proves catalogue membership only; it does not prove tenant
    activation, professional evidence, appointment, IAM, scope, or execution.
    """
    if not isinstance(item_id, str):
        raise LegalOperatingCatalogueError(
            "G7A_UNKNOWN_ITEM"
        )
    value = ITEMS_BY_ID.get(item_id)
    if value is None:
        raise LegalOperatingCatalogueError(
            "G7A_UNKNOWN_ITEM"
        )
    return value


__all__ = [
    "CATALOGUE_FINGERPRINT",
    "CATALOGUE_IDENTITY",
    "ITEMS_BY_DIMENSION",
    "ITEMS_BY_ID",
    "LegalOperatingCatalogueError",
    "LegalOperatingCatalogueItem",
    "LegalOperatingDimension",
    "SCHEMA",
    "VERSION",
    "get_legal_operating_item",
    "list_items_for_dimension",
    "list_legal_operating_dimensions",
    "list_legal_operating_items",
]

# ARTIFACT: legal_operating_catalogue.py
# VERSION: v1.0.1-G7A-GLOBAL-LEGAL-OPERATING-CATALOGUE
# AUTHORITY BOUNDARY: immutable global Legal operating vocabulary only
# TENANT POSTURE: catalogue membership never proves tenant activation
# COMMERCIAL POSTURE: catalogue membership never proves plan/subscription/entitlement
# FAIL-CLOSED POSTURE: invalid construction and unknown exact lookups reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
