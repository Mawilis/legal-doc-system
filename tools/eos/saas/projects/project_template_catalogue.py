"""TITLE: WILSY OS Governed Project Blueprint Catalogue
VERSION: v1.1.0-SEVENTEEN-INDUSTRY-BLUEPRINTS
AUTHORITY: Read-only platform blueprint definitions; Python EOS creates all business records.
EPITOME: Validated reusable industry starting structures, dependencies, relative
         due dates, role requirements and evidence-based acceptance criteria.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/projects/project_template_catalogue.py
COLLABORATION / OWNERSHIP: Projects router controls IAM, tenant ownership and
         transactional materialisation. Existing Project and ProjectTask
         registries own all persisted records and immutable events.
CERTIFICATION / UPDATE DATE: 2026-11-19
CHANGELOG: v1.1.0-SEVENTEEN-INDUSTRY-BLUEPRINTS adds ten
         validated sector-specific DAGs as neutral platform starters;
         no project, tenant, IAM or payment records are created.
CHANGELOG: v1.0.0-SEVEN-INDUSTRY-BLUEPRINT-CONTRACT seeds seven reviewed
         cross-industry definitions with DAG validation and no implicit grants.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
SECURITY / PRIVACY POSTURE: No personal data, hidden IDs, credentials or remote
         executable content; templates never assign people or finances.
TENANT BOUNDARY: Templates are platform definitions, never tenant authority.
AUTHORITY BOUNDARY: No writes, IAM grants, admission or financial decisions.
FINANCIAL AUTHORITY BOUNDARY: No spending, procurement execution or approvals.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Final

VERSION: Final[str] = "v1.1.0-SEVENTEEN-INDUSTRY-BLUEPRINTS"
SCHEMA: Final[str] = "WILSY-PROJECT-TEMPLATE/V1"

_BLUEPRINTS: Final[tuple[dict[str, object], ...]] = (
    {
      "slug": "legal-litigation",
      "industry": "Legal",
      "title": "Litigation and matter delivery",
      "revision": 1,
      "description": "Governed litigation and matter delivery with evidence-backed acceptance.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Open matter and verify jurisdiction",
          "day": 7,
          "role": "project_lead",
          "acceptance": "Approved scope and dated evidence are linked to the source project.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Assess evidence and pleadings",
          "day": 21,
          "role": "responsible_specialist",
          "acceptance": "Required preparation work is verified and documented.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "File and verify court acknowledgement",
          "day": 35,
          "role": "quality_reviewer",
          "acceptance": "Independent checks, outcomes and exceptions are recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Court readiness and filing",
          "day": 45,
          "role": "project_sponsor",
          "acceptance": "Sponsor verifies recorded acceptance evidence, outstanding risks and stage result.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "construction-delivery",
      "industry": "Construction",
      "title": "Construction project lifecycle",
      "revision": 1,
      "description": "Governed construction project lifecycle with evidence-backed acceptance.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Approve project scope and site requirements",
          "day": 7,
          "role": "project_lead",
          "acceptance": "Approved scope and dated evidence are linked to the source project.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Plan subcontractor work packages",
          "day": 21,
          "role": "responsible_specialist",
          "acceptance": "Required preparation work is verified and documented.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Inspect and certify stage completion",
          "day": 35,
          "role": "quality_reviewer",
          "acceptance": "Independent checks, outcomes and exceptions are recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Site mobilisation and delivery",
          "day": 45,
          "role": "project_sponsor",
          "acceptance": "Sponsor verifies recorded acceptance evidence, outstanding risks and stage result.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "football-season",
      "industry": "Football",
      "title": "Season operations and match preparation",
      "revision": 1,
      "description": "Governed season operations and match preparation with evidence-backed acceptance.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Approve fixture and travel requirements",
          "day": 7,
          "role": "project_lead",
          "acceptance": "Approved scope and dated evidence are linked to the source project.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Prepare training and player availability",
          "day": 21,
          "role": "responsible_specialist",
          "acceptance": "Required preparation work is verified and documented.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Complete matchday safety and operations check",
          "day": 35,
          "role": "quality_reviewer",
          "acceptance": "Independent checks, outcomes and exceptions are recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Matchday readiness",
          "day": 45,
          "role": "project_sponsor",
          "acceptance": "Sponsor verifies recorded acceptance evidence, outstanding risks and stage result.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "imports-clearance",
      "industry": "Imports",
      "title": "Procurement, shipping and customs clearance",
      "revision": 1,
      "description": "Governed procurement, shipping and customs clearance with evidence-backed acceptance.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Verify supplier and purchase requirements",
          "day": 7,
          "role": "project_lead",
          "acceptance": "Approved scope and dated evidence are linked to the source project.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Collect shipping and customs documentation",
          "day": 21,
          "role": "responsible_specialist",
          "acceptance": "Required preparation work is verified and documented.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Reconcile goods receipt and exceptions",
          "day": 35,
          "role": "quality_reviewer",
          "acceptance": "Independent checks, outcomes and exceptions are recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Shipment clearance and receipt",
          "day": 45,
          "role": "project_sponsor",
          "acceptance": "Sponsor verifies recorded acceptance evidence, outstanding risks and stage result.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "software-release",
      "industry": "Software",
      "title": "Product development and release",
      "revision": 1,
      "description": "Governed product development and release with evidence-backed acceptance.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Approve product requirements and acceptance scope",
          "day": 7,
          "role": "project_lead",
          "acceptance": "Approved scope and dated evidence are linked to the source project.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Build and validate release candidates",
          "day": 21,
          "role": "responsible_specialist",
          "acceptance": "Required preparation work is verified and documented.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Certify rollout and rollback readiness",
          "day": 35,
          "role": "quality_reviewer",
          "acceptance": "Independent checks, outcomes and exceptions are recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Release certification",
          "day": 45,
          "role": "project_sponsor",
          "acceptance": "Sponsor verifies recorded acceptance evidence, outstanding risks and stage result.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "healthcare-implementation",
      "industry": "Healthcare",
      "title": "Clinic implementation and compliance",
      "revision": 1,
      "description": "Governed clinic implementation and compliance with evidence-backed acceptance.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Verify licensing and facility requirements",
          "day": 7,
          "role": "project_lead",
          "acceptance": "Approved scope and dated evidence are linked to the source project.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Prepare staff training and operational procedures",
          "day": 21,
          "role": "responsible_specialist",
          "acceptance": "Required preparation work is verified and documented.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Validate patient safety and go-live checks",
          "day": 35,
          "role": "quality_reviewer",
          "acceptance": "Independent checks, outcomes and exceptions are recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Clinic operational readiness",
          "day": 45,
          "role": "project_sponsor",
          "acceptance": "Sponsor verifies recorded acceptance evidence, outstanding risks and stage result.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "strategic-initiative",
      "industry": "General business",
      "title": "Strategic initiative delivery",
      "revision": 1,
      "description": "Governed strategic initiative delivery with evidence-backed acceptance.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Agree objective and measurable outcome",
          "day": 7,
          "role": "project_lead",
          "acceptance": "Approved scope and dated evidence are linked to the source project.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Plan work packages and responsible roles",
          "day": 21,
          "role": "responsible_specialist",
          "acceptance": "Required preparation work is verified and documented.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Review acceptance evidence and report outcome",
          "day": 35,
          "role": "quality_reviewer",
          "acceptance": "Independent checks, outcomes and exceptions are recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Strategic delivery checkpoint",
          "day": 45,
          "role": "project_sponsor",
          "acceptance": "Sponsor verifies recorded acceptance evidence, outstanding risks and stage result.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "marketing-campaign",
      "industry": "Marketing",
      "title": "Campaign strategy and launch",
      "revision": 1,
      "description": "Governed campaign strategy and launch with traceable acceptance evidence.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Define audience, objectives and approved scope",
          "day": 5,
          "role": "project_lead",
          "acceptance": "Scope and dated evidence approved.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Prepare channels, creative and consent evidence",
          "day": 15,
          "role": "responsible_specialist",
          "acceptance": "Prepared work and assigned responsibilities reviewed.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Verify assets, legal review and launch risks",
          "day": 28,
          "role": "quality_reviewer",
          "acceptance": "Independent evidence checks and exceptions recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Campaign launch approved",
          "day": 35,
          "role": "project_sponsor",
          "acceptance": "Sponsor acceptance and unresolved risks documented.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "automotive-parts",
      "industry": "Automotive parts",
      "title": "Parts procurement and inventory",
      "revision": 1,
      "description": "Governed parts procurement and inventory with traceable acceptance evidence.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Confirm branch demand and exact part numbers",
          "day": 5,
          "role": "project_lead",
          "acceptance": "Scope and dated evidence approved.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Verify suppliers, quotations and purchase evidence",
          "day": 15,
          "role": "responsible_specialist",
          "acceptance": "Prepared work and assigned responsibilities reviewed.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Inspect received stock and discrepancies",
          "day": 28,
          "role": "quality_reviewer",
          "acceptance": "Independent evidence checks and exceptions recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Inventory replenishment accepted",
          "day": 35,
          "role": "project_sponsor",
          "acceptance": "Sponsor acceptance and unresolved risks documented.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "vehicle-dealership",
      "industry": "Vehicle dealership",
      "title": "Vehicle acquisition and listing",
      "revision": 1,
      "description": "Governed vehicle acquisition and listing with traceable acceptance evidence.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Verify vehicle identity and provenance",
          "day": 5,
          "role": "project_lead",
          "acceptance": "Scope and dated evidence approved.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Inspect vehicle condition and plan preparation",
          "day": 15,
          "role": "responsible_specialist",
          "acceptance": "Prepared work and assigned responsibilities reviewed.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Review compliance, listing and warranty readiness",
          "day": 28,
          "role": "quality_reviewer",
          "acceptance": "Independent evidence checks and exceptions recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Vehicle approved for listing",
          "day": 35,
          "role": "project_sponsor",
          "acceptance": "Sponsor acceptance and unresolved risks documented.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "mechanical-service",
      "industry": "Workshop",
      "title": "Automotive repair and quality assurance",
      "revision": 1,
      "description": "Governed automotive repair and quality assurance with traceable acceptance evidence.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Record authorised service scope and intake",
          "day": 5,
          "role": "project_lead",
          "acceptance": "Scope and dated evidence approved.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Inspect faults and approve repair work package",
          "day": 15,
          "role": "responsible_specialist",
          "acceptance": "Prepared work and assigned responsibilities reviewed.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Validate repairs, safety and test results",
          "day": 28,
          "role": "quality_reviewer",
          "acceptance": "Independent evidence checks and exceptions recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Vehicle handover approved",
          "day": 35,
          "role": "project_sponsor",
          "acceptance": "Sponsor acceptance and unresolved risks documented.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "agriculture-season",
      "industry": "Agriculture",
      "title": "Crop season and harvest",
      "revision": 1,
      "description": "Governed crop season and harvest with traceable acceptance evidence.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Approve crop and field operations plan",
          "day": 5,
          "role": "project_lead",
          "acceptance": "Scope and dated evidence approved.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Prepare inputs, equipment and safety controls",
          "day": 15,
          "role": "responsible_specialist",
          "acceptance": "Prepared work and assigned responsibilities reviewed.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Review agronomy, field records and harvesting logistics",
          "day": 28,
          "role": "quality_reviewer",
          "acceptance": "Independent evidence checks and exceptions recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Harvest readiness approved",
          "day": 35,
          "role": "project_sponsor",
          "acceptance": "Sponsor acceptance and unresolved risks documented.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "dentistry-clinic",
      "industry": "Dental healthcare",
      "title": "Dental practice operational readiness",
      "revision": 1,
      "description": "Governed dental practice operational readiness with traceable acceptance evidence.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Verify registration, licensing and clinical scope",
          "day": 5,
          "role": "project_lead",
          "acceptance": "Scope and dated evidence approved.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Prepare equipment, sterilisation and staff procedures",
          "day": 15,
          "role": "responsible_specialist",
          "acceptance": "Prepared work and assigned responsibilities reviewed.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Audit consent, safety and emergency protocols",
          "day": 28,
          "role": "quality_reviewer",
          "acceptance": "Independent evidence checks and exceptions recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Dental clinic readiness approved",
          "day": 35,
          "role": "project_sponsor",
          "acceptance": "Sponsor acceptance and unresolved risks documented.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "employee-onboarding",
      "industry": "Workforce",
      "title": "Evidence-gated employee onboarding",
      "revision": 1,
      "description": "Governed evidence-gated employee onboarding with traceable acceptance evidence.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Verify signed offer and admission prerequisites",
          "day": 5,
          "role": "project_lead",
          "acceptance": "Scope and dated evidence approved.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Prepare role training and equipment plans",
          "day": 15,
          "role": "responsible_specialist",
          "acceptance": "Prepared work and assigned responsibilities reviewed.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Review policies and independently approved access",
          "day": 28,
          "role": "quality_reviewer",
          "acceptance": "Independent evidence checks and exceptions recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Onboarding preparations accepted",
          "day": 35,
          "role": "project_sponsor",
          "acceptance": "Sponsor acceptance and unresolved risks documented.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "business-finance-close",
      "industry": "Finance operations",
      "title": "Period-end close and reporting",
      "revision": 1,
      "description": "Governed period-end close and reporting with traceable acceptance evidence.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Confirm reporting period and reviewer assignments",
          "day": 5,
          "role": "project_lead",
          "acceptance": "Scope and dated evidence approved.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Reconcile ledger and supporting schedules",
          "day": 15,
          "role": "responsible_specialist",
          "acceptance": "Prepared work and assigned responsibilities reviewed.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Review exceptions and substantiation evidence",
          "day": 28,
          "role": "quality_reviewer",
          "acceptance": "Independent evidence checks and exceptions recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Management report accepted",
          "day": 35,
          "role": "project_sponsor",
          "acceptance": "Sponsor acceptance and unresolved risks documented.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "customer-rollout",
      "industry": "Customer success",
      "title": "Customer onboarding and service rollout",
      "revision": 1,
      "description": "Governed customer onboarding and service rollout with traceable acceptance evidence.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Confirm service scope and acceptance objectives",
          "day": 5,
          "role": "project_lead",
          "acceptance": "Scope and dated evidence approved.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Prepare user onboarding and training material",
          "day": 15,
          "role": "responsible_specialist",
          "acceptance": "Prepared work and assigned responsibilities reviewed.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Verify handover readiness and outstanding risks",
          "day": 28,
          "role": "quality_reviewer",
          "acceptance": "Independent evidence checks and exceptions recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Customer launch acceptance",
          "day": 35,
          "role": "project_sponsor",
          "acceptance": "Sponsor acceptance and unresolved risks documented.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
    {
      "slug": "export-shipment",
      "industry": "International trading",
      "title": "Export shipping and proof of delivery",
      "revision": 1,
      "description": "Governed export shipping and proof of delivery with traceable acceptance evidence.",
      "steps": [
        {
          "id": "scope",
          "kind": "TASK",
          "title": "Verify customer order and export eligibility",
          "day": 5,
          "role": "project_lead",
          "acceptance": "Scope and dated evidence approved.",
          "depends_on": []
        },
        {
          "id": "prepare",
          "kind": "TASK",
          "title": "Prepare origin, packaging and shipping records",
          "day": 15,
          "role": "responsible_specialist",
          "acceptance": "Prepared work and assigned responsibilities reviewed.",
          "depends_on": [
            "scope"
          ]
        },
        {
          "id": "verify",
          "kind": "TASK",
          "title": "Review carrier clearance and release evidence",
          "day": 28,
          "role": "quality_reviewer",
          "acceptance": "Independent evidence checks and exceptions recorded.",
          "depends_on": [
            "prepare"
          ]
        },
        {
          "id": "milestone",
          "kind": "MILESTONE",
          "title": "Export dispatch accepted",
          "day": 35,
          "role": "project_sponsor",
          "acceptance": "Sponsor acceptance and unresolved risks documented.",
          "depends_on": [
            "verify"
          ]
        }
      ]
    },
)


def _validate_catalogue() -> None:
    if len(_BLUEPRINTS) != 17 or len({item["slug"] for item in _BLUEPRINTS}) != 17:
        raise RuntimeError("PROJECT_TEMPLATE_CATALOGUE_INVALID")
    for template in _BLUEPRINTS:
        steps = template["steps"]
        if not isinstance(steps, list) or not 2 <= len(steps) <= 25:
            raise RuntimeError("PROJECT_TEMPLATE_STEPS_INVALID")
        identifiers = [step["id"] for step in steps]
        if len(identifiers) != len(set(identifiers)):
            raise RuntimeError("PROJECT_TEMPLATE_DUPLICATE_STEP")
        if sum(step["kind"] == "MILESTONE" for step in steps) < 1:
            raise RuntimeError("PROJECT_TEMPLATE_MILESTONE_REQUIRED")
        seen: set[str] = set()
        for step in steps:
            if (step["kind"] not in {"MILESTONE", "TASK"}
                or not isinstance(step["title"], str)
                or not 1 <= len(step["title"]) <= 180
                or not isinstance(step["day"], int) or not 0 <= step["day"] <= 3650
                or not isinstance(step["role"], str) or not step["role"]
                or not isinstance(step["acceptance"], str) or not step["acceptance"]
                or not isinstance(step["depends_on"], list)
                or len(step["depends_on"]) > 25
                or any(dep not in seen for dep in step["depends_on"])):
                raise RuntimeError("PROJECT_TEMPLATE_STEP_INVALID")
            seen.add(step["id"])


def list_blueprints() -> tuple[dict[str, object], ...]:
    """Return detached, strictly reviewed read-only blueprint descriptions."""
    return tuple(deepcopy(item) for item in _BLUEPRINTS)


def get_blueprint(slug: str) -> dict[str, object] | None:
    """Resolve by canonical slug; never accept caller-provided executable steps."""
    if not isinstance(slug, str):
        return None
    return next((deepcopy(item) for item in _BLUEPRINTS if item["slug"] == slug), None)


_validate_catalogue()

# ARTIFACT: project_template_catalogue.py
# VERSION: v1.1.0-SEVENTEEN-INDUSTRY-BLUEPRINTS
# AUTHORITY BOUNDARY: pure validated platform definitions, zero mutations
# TENANT POSTURE: no tenant access or inherited grants
# FAIL-CLOSED POSTURE: malformed DAG or schema prevents catalogue import
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS only
# END OF WILSY OS SOVEREIGN ARTIFACT
