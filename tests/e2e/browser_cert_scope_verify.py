"""WILSY OS Suite-scoped durable browser certification verifier.

TITLE: WILSY OS Suite-Scoped Durable Browser Certificate
VERSION: v1.0.0-DAILY-SOURCE-PERSISTENCE-SCOPE
AUTHORITY: Disposable certification verifier; Python EOS owns business truth.
EPITOME: Verify the durable consequences of independently selected test suites.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/browser_cert_scope_verify.py
COLLABORATION / OWNERSHIP: browser_cert_fixture.py, run-browser-cert.mjs,
                            existing Legal and SYSTEM certification suites.
CERTIFICATION / UPDATE DATE: 2026-11-09
CHANGELOG: v1.0.0 adds strict daily-work source-owned durable cardinality,
           idempotency keys, tenant/principal binding, and completed-record
           rehydration without weakening Legal or SYSTEM verification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Test-only UUID database; never logs row content.
TENANT BOUNDARY: Exact synthetic tenant and principal checked on every record.
AUTHORITY BOUNDARY: Verifier cannot issue, complete or grant any work command.
TRANSACTION BOUNDARY: Read-only snapshot, no mutations to owner registry.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""

import argparse
import json
from hashlib import sha3_256
from pathlib import Path
from pymongo import MongoClient
from tools.eos.workspaces.persistence.tenant_module_work_registry import TenantModuleWorkRegistry
from browser_cert_fixture import (
    _owned_database,
    _uri,
    LEGAL_WORKFLOW_INSTANCE_COLLECTION,
    LEGAL_WORKFLOW_TRANSITION_COLLECTION,
    LEGAL_WORK_MATERIALIZATION_RECEIPT_COLLECTION,
    LEGAL_WORK_ITEM_COLLECTION,
    LEGAL_WORK_DEPENDENCY_COLLECTION,
    LEGAL_WORK_ASSIGNMENT_COLLECTION,
)


def verify_specialist_workflows(database, state):
    """Verify canonical durable workflow, receipt, dependency and assignment lineage."""
    workflows = state.get("specialist_workflows")
    required_actors = {"partner", "attorney", "paralegal", "secretary"}
    if not isinstance(workflows, dict) or set(workflows) != required_actors:
        raise RuntimeError("BROWSER_CERT_SPECIALIST_WORKFLOW_STATE_INVALID")

    for actor_key in sorted(required_actors):
        evidence = workflows[actor_key]
        actor = state["actors"][actor_key]
        tenant_id = state["tenant_id"]
        work_ids = evidence["work_item_ids"]
        assignment_ids = evidence["assignment_ids"]
        if len(work_ids) != 2 or len(assignment_ids) != 2:
            raise RuntimeError("BROWSER_CERT_SPECIALIST_WORK_CARDINALITY_INVALID")

        instance = database[LEGAL_WORKFLOW_INSTANCE_COLLECTION].find_one({
            "tenant_id": tenant_id,
            "workflow_instance_id": evidence["workflow_instance_id"],
            "case_matter_id": evidence["matter_id"],
            "workflow_definition_id": evidence["workflow_definition_id"],
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
        foreign_assignee_rows = database[LEGAL_WORK_ASSIGNMENT_COLLECTION].count_documents({
            "tenant_id": tenant_id,
            "work_item_id": {"$in": work_ids},
            "assignee_principal_id": {"$ne": actor["principal_id"]},
        })
        receipt_outputs = {
            row.get("work_item_id"): row.get("work_item_fingerprint")
            for row in (receipt or {}).get("outputs", [])
        }
        if (
            instance is None
            or transition is None
            or receipt is None
            or len(work_rows) != 2
            or dependency is None
            or len(assignment_rows) != 2
            or foreign_assignee_rows != 0
            or {row["work_item_id"] for row in assignment_rows} != set(work_ids)
            or {row["work_item_id"] for row in work_rows} != set(work_ids)
            or receipt_outputs != dict(zip(work_ids, evidence["work_item_fingerprints"]))
            or any(row.get("tenant_id") != tenant_id for row in work_rows)
        ):
            raise RuntimeError(
                "BROWSER_CERT_SPECIALIST_DURABLE_LINEAGE_INVALID:" + actor_key
            )

def verify_broad(database, state):
    verify_specialist_workflows(database, state)
    screening_count = database["legal_conflict_screenings"].count_documents(
        {"tenant_id": state["tenant_id"], "screening_id": state["screening_id"]}
    )
    review_count = database["legal_conflict_reviews"].count_documents(
        {"tenant_id": state["tenant_id"], "screening_id": state["screening_id"]}
    )
    if screening_count != 1 or review_count != 1:
        raise RuntimeError("BROWSER_CERT_DURABLE_REVIEW_CARDINALITY_INVALID")

def verify_daily(database, state):
    """Require exactly two independently completed desktop/mobile Operations tasks.

    The browser suite proves authenticated command routing and tenant denial.
    This read-only companion certifies that each result actually persisted
    under the owning Operations registry, with the expected exact principal,
    idempotency key and completion evidence. It never runs Legal review or
    SYSTEM responder assertions that were not exercised by the selected suite.
    """
    tenant_id = state["tenant_id"]
    principal_id = state["actors"]["tenant_owner"]["principal_id"]
    collection = database["tenant_operations_work_items"]
    rows = list(collection.find({
        "tenant_id": tenant_id,
        "description": "Disposable calendar acceptance",
        "title": {"$regex": "^Calendar source work calendar-browser-"},
    }))
    if len(rows) != 2:
        raise RuntimeError("BROWSER_CERT_DAILY_WORK_CARDINALITY_INVALID")

    work_ids = {row.get("work_item_id") for row in rows}
    request_keys = {row.get("idempotency_key") for row in rows}
    if (
        len(work_ids) != 2
        or not all(isinstance(value, str) and value for value in work_ids)
        or len(request_keys) != 2
        or not all(isinstance(value, str) and value.startswith("calendar-browser-") for value in request_keys)
    ):
        raise RuntimeError("BROWSER_CERT_DAILY_WORK_IDENTITY_INVALID")

    reader = TenantModuleWorkRegistry(collection)
    with database.client.start_session() as session:
        session.start_transaction()
        try:
            for row in rows:
                if (
                    row.get("created_by_principal_id") != principal_id
                    or row.get("tenant_id") != tenant_id
                    or row.get("idempotency_key") != row.get("title", "").removeprefix("Calendar source work ")
                ):
                    raise RuntimeError("BROWSER_CERT_DAILY_WORK_OWNER_BINDING_INVALID")
                current = reader.get(
                    tenant_id=tenant_id,
                    work_item_id=row["work_item_id"],
                    session=session,
                )
                if (
                    current.status.value != "COMPLETED"
                    or current.completion_note != "Source-owned calendar completion evidence"
                    or current.completed_at is None
                    or current.created_by_principal_id != principal_id
                    or current.tenant_id != tenant_id
                ):
                    raise RuntimeError("BROWSER_CERT_DAILY_WORK_COMPLETION_INVALID")
        finally:
            session.abort_transaction()

    if collection.count_documents({
        "tenant_id": {"$ne": tenant_id},
        "work_item_id": {"$in": sorted(work_ids)},
    }):
        raise RuntimeError("BROWSER_CERT_DAILY_WORK_FOREIGN_COPY_INVALID")


def verify_system(database, state):
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


def main():
    parser = argparse.ArgumentParser(description="Suite-scoped durable browser certificate verifier")
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--scope", choices=("system", "broad", "combined", "daily"), default="combined")
    args = parser.parse_args()
    state = json.loads(args.state.read_text(encoding="utf-8"))
    client = MongoClient(_uri(), serverSelectionTimeoutMS=5000)
    try:
        database = _owned_database(client)
        if args.scope in ("broad", "combined"):
            verify_broad(database, state)
        if args.scope in ("system", "combined"):
            verify_system(database, state)
        if args.scope == "daily":
            verify_daily(database, state)
    finally:
        client.close()
    print("BROWSER_CERT_DURABLE_VERIFICATION_PASSED:" + args.scope)

if __name__ == "__main__":
    main()

# ARTIFACT: tests/e2e/browser_cert_scope_verify.py
# VERSION: v1.0.0-DAILY-SOURCE-PERSISTENCE-SCOPE
# AUTHORITY BOUNDARY: Disposable read-only source verification only.
# TENANT POSTURE: Exact tenant, principal, two durable source work records.
# FAIL-CLOSED POSTURE: Missing/partial/foreign work never passes certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
