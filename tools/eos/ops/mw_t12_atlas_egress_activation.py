"""TITLE: MW-T12 three-node Atlas outbound CloudFormation activation gate.
VERSION: v1.0.0-EXACT-DNS-AND-CHANGESET-ADMISSION
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Verify fresh Atlas replica DNS and exact reviewed three-rule,
         outbound-only nonproduction CloudFormation change set before optional
         ECS security-group network egress activation. No tasks launched.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_atlas_egress_activation.py
COLLABORATION / OWNERSHIP: Existing MW-T12 CloudFormation dormant foundation,
         Atlas test cluster's three DNS hosts and ECS AWS read helper.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.0.0-EXACT-DNS-AND-CHANGESET-ADMISSION introduces read-only
           preflight by default and separately opted-in narrowly scoped
           CloudFormation execution; independent status and egress readback.
           No Atlas IP access-list mutation, task registration or task launch.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No credentials/URI/secret values disclosed;
                           only approved destination IPv4 and AWS metadata.
TENANT BOUNDARY: Synthetic-only nonproduction test cluster, no tenant data.
AUTHORITY BOUNDARY: Outbound SG changes are NOT Atlas source-IP admission,
                    authenticated EOS or image rollback certification.
FINANCIAL AUTHORITY BOUNDARY: No Fargate launch; Kennel EOS exclusively.
"""
from __future__ import annotations

import argparse
import ipaddress
import socket

from tools.eos.ops import mw_t12_task_definition_admission as aws_authority

VERSION = "v1.0.0-EXACT-DNS-AND-CHANGESET-ADMISSION"
STACK = "wilsy-mwt12-nonproduction-foundation"
CHANGE_SET = "mwt12-three-node-egress-review"
SG_ID = "sg-05bbf379de9a0eee8"
CLUSTER = "wilsy-mwt12-nonproduction"
REGION = "af-south-1"
ACCOUNT = "121014832643"
HOSTS = (
    "ac-nagjjuj-shard-00-00.xmlpwmq.mongodb.net",
    "ac-nagjjuj-shard-00-01.xmlpwmq.mongodb.net",
    "ac-nagjjuj-shard-00-02.xmlpwmq.mongodb.net",
)
REVIEWED = (
    "159.41.89.87/32",
    "159.41.89.104/32",
    "159.41.89.120/32",
)
PARAMS = (
    "ApprovedAtlasEndpointCidr",
    "ApprovedAtlasEndpointCidr2",
    "ApprovedAtlasEndpointCidr3",
)
RESOURCES = frozenset((
    "EosAtlasEndpointEgress",
    "EosAtlasEndpointEgress2",
    "EosAtlasEndpointEgress3",
))


class EgressAdmissionError(RuntimeError):
    """Stable secret-free denial of nonproduction cloud network change."""


def require(condition: bool, code: str) -> None:
    """Reject missing exact network/cloud identity before any mutation."""
    if not condition:
        raise EgressAdmissionError(code)


def aws(profile: str, *args: str) -> dict:
    """Read or invoke exact AWS subcommands via existing bounded AWS helper."""
    return aws_authority.aws(profile, *args)


def fresh_dns() -> tuple[str, str, str]:
    """Resolve each recorded Atlas node now; do not trust cached review data.

    More than one A address for a named node, IPv6-only DNS, changed /32 or
    reuse of one IP for two nodes denies execution until a new review.
    This is a DNS snapshot, not immunity against subsequent DNS changes.
    """
    cidrs = []
    for host in HOSTS:
        try:
            answers = socket.getaddrinfo(
                host, 27017, family=socket.AF_INET,
                type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP,
            )
        except (OSError, socket.gaierror) as exc:
            raise EgressAdmissionError("ATLAS_NODE_DNS_UNAVAILABLE") from exc
        ips = {item[4][0] for item in answers
               if item[4] and isinstance(item[4][0], str)}
        require(len(ips) == 1, "ATLAS_NODE_DNS_AMBIGUOUS")
        ip = next(iter(ips))
        try:
            address = ipaddress.ip_address(ip)
        except ValueError as exc:
            raise EgressAdmissionError("ATLAS_NODE_IPV4_INVALID") from exc
        require(address.version == 4 and address.is_global,
                "ATLAS_NODE_IPV4_INVALID")
        cidrs.append(str(address) + "/32")
    require(len(set(cidrs)) == len(HOSTS), "ATLAS_NODE_IP_COLLISION")
    require(tuple(cidrs) == REVIEWED, "ATLAS_NODE_DNS_CHANGED_REVIEW_REQUIRED")
    return tuple(cidrs)


def exact_change_set(profile: str) -> None:
    """Admit only the three pre-reviewed additions and exact CIDR parameters.

    Existing foundation/VPC parameters must have UsePreviousValue=true;
    egress opt-in must be explicit true. No IAM role, replacement or task
    resource is permitted. The change set must be executable and unexecuted.
    """
    caller = aws(profile, "sts", "get-caller-identity")
    require(caller.get("Account") == ACCOUNT, "AWS_ACCOUNT_MISMATCH")
    result = aws(
        profile, "cloudformation", "describe-change-set",
        "--stack-name", STACK, "--change-set-name", CHANGE_SET,
    )
    require(result.get("StackName") == STACK
            and result.get("ChangeSetName") == CHANGE_SET
            and result.get("Status") == "CREATE_COMPLETE"
            and result.get("ExecutionStatus") == "AVAILABLE"
            and result.get("ChangeSetType") == "UPDATE",
            "CLOUDFORMATION_CHANGE_SET_NOT_EXECUTABLE")
    modifications = result.get("Changes")
    require(isinstance(modifications, list) and len(modifications) == 3,
            "CLOUDFORMATION_CHANGE_COUNT_DRIFT")
    logical_ids = set()
    for change in modifications:
        require(isinstance(change, dict)
                and change.get("Type") == "Resource",
                "CLOUDFORMATION_NONRESOURCE_CHANGE")
        resource = change.get("ResourceChange")
        require(isinstance(resource, dict)
                and resource.get("Action") == "Add"
                and resource.get("ResourceType") == "AWS::EC2::SecurityGroupEgress"
                and resource.get("Replacement") is None,
                "CLOUDFORMATION_CHANGE_TYPE_DRIFT")
        logical_ids.add(resource.get("LogicalResourceId"))
    require(logical_ids == RESOURCES,
            "CLOUDFORMATION_RESOURCE_SET_DRIFT")
    parameters = result.get("Parameters")
    require(isinstance(parameters, list), "CLOUDFORMATION_PARAMETERS_ABSENT")
    by_name = {p.get("ParameterKey"): p for p in parameters
               if isinstance(p, dict)}
    require(len(by_name) == len(parameters)
            and set(by_name) == {
                "EnableDormantFoundation", "ExistingVpcId",
                "EnableAtlasEndpointEgress", *PARAMS,
            }, "CLOUDFORMATION_PARAMETER_SET_DRIFT")
    require(by_name["EnableDormantFoundation"].get("UsePreviousValue") is True
            and by_name["ExistingVpcId"].get("UsePreviousValue") is True
            and by_name["EnableAtlasEndpointEgress"].get("ParameterValue")
            == "true", "CLOUDFORMATION_AUTHORITY_PARAMETER_DRIFT")
    for name, value in zip(PARAMS, REVIEWED, strict=True):
        require(by_name[name].get("ParameterValue") == value,
                "CLOUDFORMATION_ATLAS_CIDR_PARAMETER_DRIFT")
    print("MW_T12_CHANGESET_THREE_EGRESS_RULES=VERIFIED")
    print("MW_T12_CHANGESET_NO_IAM_OR_COMPUTE_CHANGES=VERIFIED")


def no_compute(profile: str) -> None:
    """Require zero existing ECS tasks/services in exact owned cluster."""
    aws_authority.no_compute(profile)
    print("MW_T12_ECS_COMPUTE=ZERO")


def verify_egress(profile: str) -> None:
    """Independently check actual group permissions after stack execution."""
    groups = aws(
        profile, "ec2", "describe-security-groups",
        "--group-ids", SG_ID,
    ).get("SecurityGroups")
    require(isinstance(groups, list) and len(groups) == 1
            and groups[0].get("GroupId") == SG_ID
            and not groups[0].get("IpPermissions", []),
            "CLOSED_SG_OR_INBOUND_DRIFT")
    egress = groups[0].get("IpPermissionsEgress")
    require(isinstance(egress, list), "SG_EGRESS_RESPONSE_INVALID")
    observed = set()
    for permission in egress:
        require(isinstance(permission, dict)
                and permission.get("IpProtocol") == "tcp",
                "SG_EGRESS_PROTOCOL_DRIFT")
        port = permission.get("FromPort")
        require(permission.get("ToPort") == port
                and port in {443, 27017},
                "SG_EGRESS_PORT_DRIFT")
        require(not permission.get("Ipv6Ranges")
                and not permission.get("PrefixListIds")
                and not permission.get("UserIdGroupPairs"),
                "SG_EGRESS_NONIP_DESTINATION_DRIFT")
        ranges = permission.get("IpRanges", [])
        require(isinstance(ranges, list) and ranges,
                "SG_EGRESS_ADDRESS_EMPTY")
        for row in ranges:
            require(isinstance(row, dict), "SG_EGRESS_ADDRESS_INVALID")
            observed.add((port, row.get("CidrIp")))
    require(observed == {
        (443, "0.0.0.0/0"),
        *((27017, cidr) for cidr in REVIEWED),
    } and len(egress) == 4, "SG_EGRESS_EXACT_RULES_DRIFT")
    print("MW_T12_ATLAS_THREE_NODE_EGRESS=VERIFIED")
    print("MW_T12_NO_PUBLIC_INBOUND=VERIFIED")


def run(profile: str, execute: bool) -> None:
    """Validate every read-only gate, then optionally execute one change set.

    No automatic CloudFormation rollback attempted after failed execution;
    the original stack and change set must be inspected before any retry.
    """
    no_compute(profile)
    cidrs = fresh_dns()
    exact_change_set(profile)
    print("MW_T12_ATLAS_DNS_THREE_NODES=FRESH_VERIFIED")
    print("MW_T12_ATLAS_DNS_CIDRS=" + ",".join(cidrs))
    if not execute:
        print("MW_T12_CLOUDFORMATION_EXECUTED=FALSE")
        print("MW_T12_ATLAS_SOURCE_IP_ALLOWLIST=NOT_CERTIFIED")
        return
    # Minimize DNS/CFN time-of-check drift before the sole opt-in mutation.
    require(fresh_dns() == cidrs, "ATLAS_NODE_DNS_CHANGED_REVIEW_REQUIRED")
    no_compute(profile)
    exact_change_set(profile)
    aws(
        profile, "cloudformation", "execute-change-set",
        "--stack-name", STACK, "--change-set-name", CHANGE_SET,
    )
    # Independent readback, fail closed while CloudFormation is updating.
    outcome = aws(
        profile, "cloudformation", "describe-stacks", "--stack-name", STACK,
    ).get("Stacks", [])
    require(isinstance(outcome, list) and len(outcome) == 1
            and outcome[0].get("StackStatus") == "UPDATE_COMPLETE",
            "CLOUDFORMATION_EXECUTION_NOT_YET_COMPLETE")
    verify_egress(profile)
    no_compute(profile)
    print("MW_T12_CLOUDFORMATION_EXECUTED=VERIFIED")
    print("MW_T12_ATLAS_SOURCE_IP_ALLOWLIST=NOT_CERTIFIED")
    print("MW_T12_IMAGE_ROLLBACK_CERTIFIED=FALSE")


def main(argv: list[str] | None = None) -> int:
    """Expose a read-only default and explicit network-only opt-in."""
    parser = argparse.ArgumentParser(
        description="MW-T12 verify or execute exact reviewed Atlas egress")
    parser.add_argument("--profile", default="wilsy-legal-cert")
    parser.add_argument("--execute-reviewed-egress", action="store_true",
                        help="Opt-in exact CloudFormation change-set execution")
    args = parser.parse_args(argv)
    try:
        run(args.profile, args.execute_reviewed_egress)
        return 0
    except (EgressAdmissionError, aws_authority.AdmissionError,
            KeyboardInterrupt) as exc:
        code = "INTERRUPTED" if isinstance(exc, KeyboardInterrupt) else str(exc)
        print("MW_T12_ATLAS_EGRESS_ACTIVATION=FAIL_CLOSED")
        print("MW_T12_ERROR=" + code)
        print("MW_T12_COMPUTE_LAUNCHED=FALSE")
        print("MW_T12_IMAGE_ROLLBACK_CERTIFIED=FALSE")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

# ARTIFACT: tools/eos/ops/mw_t12_atlas_egress_activation.py
# VERSION: v1.0.0-EXACT-DNS-AND-CHANGESET-ADMISSION
# AUTHORITY BOUNDARY: Only optional exact outbound CFN egress change set.
# TENANT POSTURE: Synthetic Atlas network only, no production data.
# FAIL-CLOSED POSTURE: DNS/changeset/SG drift or compute denies activation.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
