"""TITLE: MW-T12 verified Atlas three-node egress admission certificate.
VERSION: v1.0.0-EXACT-THREE-RULE-OUTBOUND-REGRESSION
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Prove exact reviewed CloudFormation changes, DNS/compute denial,
         no-delete network boundary and independent SG permission readback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_mw_t12_atlas_egress_activation.py
COLLABORATION / OWNERSHIP: Existing MW-T12 CloudFormation template and fresh
         node DNS admission operator only.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.0.0-EXACT-THREE-RULE-OUTBOUND-REGRESSION introduces mocked
           DNS, AWS control-plane and guarded execution regression tests;
           no real DNS, AWS, Atlas or financial authority is invoked.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No credentials or external network calls.
TENANT BOUNDARY: Synthetic test-only, no EOS tenant data access.
AUTHORITY BOUNDARY: Tests never execute a real change set.
FINANCIAL AUTHORITY BOUNDARY: No paid compute; Kennel EOS exclusively.
"""
from __future__ import annotations

import socket

import pytest

from tools.eos.ops import mw_t12_atlas_egress_activation as gate


def _change_set():
    """Produce the exact reviewed three-resource nonproduction change set."""
    return {
        "StackName": gate.STACK,
        "ChangeSetName": gate.CHANGE_SET,
        "Status": "CREATE_COMPLETE",
        "ExecutionStatus": "AVAILABLE",
        "ChangeSetType": "UPDATE",
        "Changes": [
            {"Type": "Resource", "ResourceChange": {
                "Action": "Add",
                "ResourceType": "AWS::EC2::SecurityGroupEgress",
                "Replacement": None,
                "LogicalResourceId": resource,
            }}
            for resource in sorted(gate.RESOURCES)
        ],
        "Parameters": [
            {"ParameterKey": "EnableDormantFoundation",
             "UsePreviousValue": True},
            {"ParameterKey": "ExistingVpcId",
             "UsePreviousValue": True},
            {"ParameterKey": "EnableAtlasEndpointEgress",
             "ParameterValue": "true"},
            *[
                {"ParameterKey": name, "ParameterValue": cidr}
                for name, cidr in zip(gate.PARAMS, gate.REVIEWED, strict=True)
            ],
        ],
    }


def test_exact_reviewed_change_set_passes_read_only(monkeypatch) -> None:
    """The verified three-resource SG-only change set admits no ECS writes."""
    commands = []

    def fake_aws(profile, *args):
        commands.append(args)
        return (
            {"Account": gate.ACCOUNT} if args[0] == "sts"
            else _change_set()
        )

    monkeypatch.setattr(gate, "aws", fake_aws)
    gate.exact_change_set("wilsy-legal-cert")
    assert len(commands) == 2
    assert all("execute-change-set" not in command for command in commands)


@pytest.mark.parametrize("wrong", [
    "IAM", "extra", "CIDR", "executed", "replacement",
])
def test_change_set_drift_refused(monkeypatch, wrong: str) -> None:
    """IAM changes, extra changes, CIDR drift and replay fail closed."""
    snapshot = _change_set()
    if wrong == "IAM":
        snapshot["Changes"][0]["ResourceChange"]["ResourceType"] = "AWS::IAM::Role"
    if wrong == "extra":
        snapshot["Changes"].append(snapshot["Changes"][0])
    if wrong == "CIDR":
        snapshot["Parameters"][-1]["ParameterValue"] = "8.8.8.8/32"
    if wrong == "executed":
        snapshot["ExecutionStatus"] = "EXECUTE_COMPLETE"
    if wrong == "replacement":
        snapshot["Changes"][0]["ResourceChange"]["Replacement"] = "True"

    monkeypatch.setattr(gate, "aws", lambda profile, *args:
                        {"Account": gate.ACCOUNT} if args[0] == "sts"
                        else snapshot)
    with pytest.raises(gate.EgressAdmissionError):
        gate.exact_change_set("wilsy-legal-cert")


def test_dns_changed_blocks_without_network_mutation(monkeypatch) -> None:
    """Changed endpoint requires a new review before any CFN execution."""
    def fake_dns(host, port, *, family, type, proto):
        ip = "8.8.8.8" if host == gate.HOSTS[1] else (
            gate.REVIEWED[gate.HOSTS.index(host)].split("/")[0]
        )
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port))]

    monkeypatch.setattr(gate.socket, "getaddrinfo", fake_dns)
    with pytest.raises(gate.EgressAdmissionError,
                       match="ATLAS_NODE_DNS_CHANGED_REVIEW_REQUIRED"):
        gate.fresh_dns()


def test_default_run_never_executes_change_set(monkeypatch, capsys) -> None:
    """Read-only default emits verified DNS/CFN evidence without changing AWS."""
    monkeypatch.setattr(gate, "no_compute", lambda profile: None)
    monkeypatch.setattr(gate, "fresh_dns", lambda: gate.REVIEWED)
    monkeypatch.setattr(gate, "exact_change_set", lambda profile: None)
    monkeypatch.setattr(
        gate.subprocess, "run",
        lambda *a, **k: pytest.fail("MUST_NOT_EXECUTE"),
    )
    gate.run("wilsy-legal-cert", execute=False)
    assert "MW_T12_CLOUDFORMATION_EXECUTED=FALSE" in capsys.readouterr().out


def test_sg_grouped_same_port_rules_read_back(monkeypatch) -> None:
    """AWS may coalesce all three 27017 CIDRs into one permission object."""
    group = {
        "GroupId": gate.SG_ID, "IpPermissions": [],
        "IpPermissionsEgress": [
            {"IpProtocol": "tcp", "FromPort": 443, "ToPort": 443,
             "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
            {"IpProtocol": "tcp", "FromPort": 27017, "ToPort": 27017,
             "IpRanges": [{"CidrIp": cidr} for cidr in gate.REVIEWED]},
        ],
    }
    monkeypatch.setattr(gate, "aws", lambda profile, *args:
                        {"SecurityGroups": [group]})
    gate.verify_egress("wilsy-legal-cert")


def test_sg_inbound_open_refuses_verification(monkeypatch) -> None:
    """Public ingress cannot be certified as closed, even with exact egress."""
    group = {
        "GroupId": gate.SG_ID,
        "IpPermissions": [{"IpProtocol": "-1", "IpRanges": [
            {"CidrIp": "0.0.0.0/0"},
        ]}],
        "IpPermissionsEgress": [],
    }
    monkeypatch.setattr(gate, "aws", lambda profile, *args:
                        {"SecurityGroups": [group]})
    with pytest.raises(gate.EgressAdmissionError,
                       match="CLOSED_SG_OR_INBOUND_DRIFT"):
        gate.verify_egress("wilsy-legal-cert")


# ARTIFACT: tests/unit/test_mw_t12_atlas_egress_activation.py
# VERSION: v1.0.0-EXACT-THREE-RULE-OUTBOUND-REGRESSION
# AUTHORITY BOUNDARY: Offline strict DNS/change-set/SG evidence only.
# TENANT POSTURE: No tenant persistence, identity or production access.
# FAIL-CLOSED POSTURE: Extra permissions, drift or unknown DNS denied.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
