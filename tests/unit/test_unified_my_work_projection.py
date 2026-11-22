"""TITLE: WILSY OS Unified My Work Source Projection Certificate
VERSION: v1.1.0-SOURCE-WORK-AUDIENCE-ENVELOPE-CERT
AUTHORITY: Synthetic read-only EOS source composition and denial tests.
EPITOME: Verify independently admitted Legal, Operations, Intelligence, CRM,
         HR and Projects work shapes, cross-tenant rejection and blocked work.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_unified_my_work_projection.py
COLLABORATION / OWNERSHIP: unified_my_work_projection composes only sources
         already admitted by the canonical authenticated My Work router.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.1.0-SOURCE-WORK-AUDIENCE-ENVELOPE-CERT proves
         work rows remain visible and UNCLASSIFIED without classification
         evidence, accepts exact revision-attested audience metadata and
         fails closed on stale or foreign audience assertions.
CHANGELOG: v1.0.0-PROJECTS-DAILY-ATTENTION-PROJECTION-CERT adds Projects
         delegated/blocked task tests and seals the complete existing artifact.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only, no real users.
TENANT BOUNDARY: All source envelopes and rows require an exact tenant.
AUTHORITY BOUNDARY: Source-specific commands, IAM and approval stay separate.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.workspaces.service.unified_my_work_projection import (
    SCHEMA,
    UnifiedMyWorkProjectionError,
    build_unified_my_work,
)


NOW = datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc)
TENANT = "WILSYTENANT-4CD2FZ4O"
PRINCIPAL = "principal-1"


def item(work_item_id="task-1", *, title="Prepare report", status="OPEN",
         priority="NORMAL", due_at=None):
    return {
        "work_item_id": work_item_id,
        "title": title,
        "status": status,
        "priority": priority,
        "due_at": due_at,
    }


def test_m01_work_audience_is_visible_unclassified_until_source_attests():
    """M01 source owned taxonomy cannot guess a classification from title."""
    row = item("operating-looking-item", title="Weekly operations review")
    result = build_unified_my_work(
        tenant_id=TENANT, principal_id=PRINCIPAL, now=NOW,
        operations={"tenant_id": TENANT, "items": [row]},
    )
    assert result["summary"]["active_count"] == 1
    assert result["items"][0]["audience"] == "UNCLASSIFIED"
    assert result["items"][0]["critical_gate"] is False
    assert result["items"][0]["audience_evidence_ref"] is None


def test_m01_current_source_audience_proof_and_foreign_revision_denial():
    """Only the admitted source's exact item and revision can tag work."""
    row = item("source-item", title="Source classification is not a title regex")
    row["revision"] = 3
    row["audience_evidence"] = {
        "tenant_id": TENANT, "source": "OPERATIONS", "record_id": "source-item",
        "source_revision": 3, "audience": "OPERATING", "source_verified": True,
        "evidence_ref": "source-audit-3", "critical_gate": False,
        "critical_gate_evidence_ref": None,
    }
    result = build_unified_my_work(
        tenant_id=TENANT, principal_id=PRINCIPAL, now=NOW,
        operations={"tenant_id": TENANT, "items": [row]},
    )
    assert result["items"][0]["audience"] == "OPERATING"
    assert result["items"][0]["audience_source_revision"] == 3
    for field, value in (("tenant_id", "FOREIGN"), ("source_revision", 2)):
        malicious = {**row, "audience_evidence": {**row["audience_evidence"], field: value}}
        with pytest.raises(ValueError):
            build_unified_my_work(
                tenant_id=TENANT, principal_id=PRINCIPAL, now=NOW,
                operations={"tenant_id": TENANT, "items": [malicious]},
            )


def test_unifies_authorized_source_reads_and_preserves_source_ownership():
    result = build_unified_my_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        now=NOW,
        legal={
            "tenant_id": TENANT,
            "assigned_work_items": [item("legal-1", priority="HIGH")],
            "supervised_work_items": [item("legal-1", priority="HIGH")],
        },
        operations={"tenant_id": TENANT, "items": [item("ops-1")]},
        intelligence={"tenant_id": TENANT, "items": [item("intel-1")]},
        crm={"tenant_id": TENANT, "items": [item("crm-1")]},
    )

    assert result["schema"] == SCHEMA
    assert result["summary"]["active_count"] == 4
    assert result["summary"]["source_counts"] == {
        "LEGAL": 1, "OPERATIONS": 1, "INTELLIGENCE": 1, "CRM": 1,
    }
    legal = next(row for row in result["items"] if row["source"] == "LEGAL")
    assert legal["visibility_provenance"] == ["LEGAL_ASSIGNED", "LEGAL_SUPERVISED"]
    assert legal["action_authority"] == "SOURCE_SERVICE_ONLY"
    assert legal["completion_route"] is None
    assert result["authority"]["permits_completion"] is False
    assert result["authority"]["permits_approval"] is False


def test_queue_is_deterministic_and_orders_overdue_before_other_work():
    result = build_unified_my_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        now=NOW,
        operations={
            "tenant_id": TENANT,
            "items": [
                item("later", priority="CRITICAL", due_at=(NOW + timedelta(days=1)).isoformat()),
                item("overdue", priority="LOW", due_at=(NOW - timedelta(days=1)).isoformat()),
            ],
        },
    )
    assert [row["work_item_id"] for row in result["items"]] == ["overdue", "later"]
    assert result["summary"]["overdue_count"] == 1


def test_same_work_item_id_in_different_sources_does_not_collide():
    result = build_unified_my_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        now=NOW,
        operations={"tenant_id": TENANT, "items": [item("same")]},
        crm={"tenant_id": TENANT, "items": [item("same")]},
    )
    assert len(result["items"]) == 2
    assert {row["source_key"] for row in result["items"]} == {
        "OPERATIONS:same", "CRM:same",
    }


def test_rejects_foreign_tenant_source_before_projection():
    with pytest.raises(UnifiedMyWorkProjectionError, match="SOURCE_TENANT_MISMATCH"):
        build_unified_my_work(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            now=NOW,
            operations={"tenant_id": "FOREIGN-TENANT", "items": [item()]},
        )


def test_rejects_item_level_foreign_tenant_even_when_source_envelope_matches():
    foreign = {**item(), "tenant_id": "FOREIGN-TENANT"}
    with pytest.raises(UnifiedMyWorkProjectionError, match="SOURCE_ITEM_TENANT_MISMATCH"):
        build_unified_my_work(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            now=NOW,
            operations={"tenant_id": TENANT, "items": [foreign]},
        )


def test_rejects_divergent_duplicate_from_same_authorized_source():
    with pytest.raises(UnifiedMyWorkProjectionError, match="SOURCE_ITEM_DIVERGENCE"):
        build_unified_my_work(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            now=NOW,
            legal={
                "tenant_id": TENANT,
                "assigned_work_items": [item("legal-1", title="Original")],
                "supervised_work_items": [item("legal-1", title="Changed")],
            },
        )


def test_excludes_terminal_items_without_rewriting_source_records():
    result = build_unified_my_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        now=NOW,
        crm={
            "tenant_id": TENANT,
            "items": [item("done", status="COMPLETED"), item("cancelled", status="CANCELLED")],
        },
    )
    assert result["items"] == []
    assert result["summary"]["active_count"] == 0


def test_rejects_naive_or_malformed_due_dates():
    for due_at in ("2026-11-06T12:00:00", "not-a-date"):
        with pytest.raises(UnifiedMyWorkProjectionError, match="SOURCE_DUE_AT_INVALID"):
            build_unified_my_work(
                tenant_id=TENANT,
                principal_id=PRINCIPAL,
                now=NOW,
                operations={"tenant_id": TENANT, "items": [item(due_at=due_at)]},
            )


def test_project_tasks_join_daily_attention_without_inherited_authority():
    """Only independently admitted delegated and blocked project source rows count."""
    project_id = "prj-" + "a" * 48
    result = build_unified_my_work(
        tenant_id=TENANT, principal_id=PRINCIPAL, now=NOW,
        projects={"tenant_id": TENANT, "items": [
            {**item("ptk-" + "b" * 48, title="Deliver current module", status="OPEN"),
             "tenant_id": TENANT, "project_id": project_id,
             "due_date": "2026-11-20", "owner_principal_id": PRINCIPAL},
            {**item("ptk-" + "c" * 48, title="Blocked dependency", status="BLOCKED"),
             "tenant_id": TENANT, "project_id": project_id,
             "due_date": None, "owner_principal_id": PRINCIPAL},
        ]},
    )
    assert result["summary"]["active_count"] == 2
    assert result["summary"]["source_counts"] == {"PROJECTS": 2}
    rows = result["items"]
    assert {row["source_key"] for row in rows} == {
        "PROJECTS:ptk-" + "b" * 48, "PROJECTS:ptk-" + "c" * 48,
    }
    assert any(row["status"] == "BLOCKED" for row in rows)
    assert all(row["completion_route"] is None for row in rows)
    assert all(row["action_authority"] == "SOURCE_SERVICE_ONLY" for row in rows)
    assert rows[0]["project_id"] == project_id
    assert result["authority"]["permits_completion"] is False


@pytest.mark.parametrize("changes", [
    {"owner_principal_id": "other-principal"},
    {"project_id": "wrong"},
    {"status": "DONE"}, {"status": "CANCELLED"},
    {"due_date": 42},
])
def test_project_attention_rejects_forged_work_source(changes):
    """Cannot populate user queue from foreign/terminal or malformed project work."""
    source = {
        **item("ptk-" + "d" * 48, status="BLOCKED"),
        "tenant_id": TENANT, "project_id": "prj-" + "e" * 48,
        "owner_principal_id": PRINCIPAL, "due_date": None,
        **changes,
    }
    with pytest.raises(UnifiedMyWorkProjectionError, match="PROJECTS_SOURCE_ITEM_INVALID"):
        build_unified_my_work(
            tenant_id=TENANT, principal_id=PRINCIPAL, now=NOW,
            projects={"tenant_id": TENANT, "items": [source]},
        )


def test_rejects_malformed_source_item_instead_of_silently_dropping_it():
    with pytest.raises(UnifiedMyWorkProjectionError, match="SOURCE_ITEM_IDENTITY_INVALID"):
        build_unified_my_work(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            now=NOW,
            operations={"tenant_id": TENANT, "items": [{"title": "No source id", "status": "OPEN"}]},
        )

# ARTIFACT: test_unified_my_work_projection.py
# VERSION: v1.1.0-SOURCE-WORK-AUDIENCE-ENVELOPE-CERT
# AUTHORITY BOUNDARY: pure projection checks; no IAM or source mutation
# TENANT POSTURE: exact source envelope and row validation
# FAIL-CLOSED POSTURE: malformed, forged or foreign project work denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
