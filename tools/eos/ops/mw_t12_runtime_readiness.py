"""TITLE: MW-T12 ECS nonproduction runtime readiness and cost admission.
VERSION: v1.3.2-ATLAS-LOCAL-VS-ECS-ADMISSION-DISTINCTION
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Inspect two digest-pinned registered Fargate tasks and their exact
         network, storage, identity and cost gates without launching compute.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_runtime_readiness.py
COLLABORATION / OWNERSHIP: Existing AWS MW-T12 ECR preflight, dormant task
         definitions, CloudFormation foundation and ECS read-only admission.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.3.2-ATLAS-LOCAL-VS-ECS-ADMISSION-DISTINCTION labels
           missing ECS secret delivery separately from independently verified
           local Atlas readWrite login. No AWS/Atlas mutation authority added.
CHANGELOG: v1.3.1-SYNTHETIC-NAME-REGEX-CORRECTION correctly anchors the
           isolated synthetic database name at the string boundary.
CHANGELOG: v1.3.0-SCOPED-ATLAS-CREDENTIAL-READBACK introduces an optional
           hidden-input, TLS-verified read-only scoped Mongo credential audit
           for the existing separate FREE Atlas test cluster; no database or
           user mutation, production authority or Fargate activation.
CHANGELOG: v1.2.1-OPTIONAL-ECS-SECRET-LIST-NORMALIZATION accepts AWS
           omitting the empty secrets array while forbidding real secret refs.
CHANGELOG: v1.2.0-ATLAS-EGRESS-AND-SECRET-ADMISSION explicitly blocks
           Atlas TCP/27017 egress when only HTTPS is allowed, rejects task
           credential and connection misconfiguration, and retains the
           zero-compute independent admission contract.
CHANGELOG: v1.1.0-REAL-SUBNET-AND-BOUNDED-DRILL-PLAN verifies the exact
           nonproduction subnet / main route / IGW configuration and records
           a serial, zero-launch three-phase rehearsal plan with strict limits.
           Routing evidence is not a live container connectivity certificate.
CHANGELOG: v1.0.1-CLOUDFORMATION-SECURITY-GROUP-BINDING looks up the
           CloudFormation-owned group ID rather than assuming a group name.
CHANGELOG: v1.0.0-READ-ONLY-RUNTIME-BLOCKERS validates the recorded AWS
           image identities, both task revisions, zero compute, networking,
           persistent storage and independent verification prerequisites.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: AWS CLI read only; no token, URI, secret or task
                           payload printed; no raw error body disclosed.
TENANT BOUNDARY: No real tenant data or EOS business source writes.
AUTHORITY BOUNDARY: Never starts/stops task, service or deploy; no approval,
                    production readiness or rollback result is inferred.
FINANCIAL AUTHORITY BOUNDARY: No paid compute activated; Kennel EOS exclusively.
"""
from __future__ import annotations

import argparse
from getpass import getpass
import re
import sys
from urllib.parse import parse_qsl, urlsplit

from tools.eos.ops import mw_t12_ecr_publication as published
from tools.eos.ops import mw_t12_task_definition_admission as registered

VERSION = "v1.3.2-ATLAS-LOCAL-VS-ECS-ADMISSION-DISTINCTION"
REVISIONS = (1, 2)
TASK_FAMILY = "wilsy-mwt12-eos-nonproduction"
TEST_ATLAS_HOST = "legal-doc-test.xmlpwmq.mongodb.net"
SYNTHETIC_DB = re.compile(r"wilsy_mwt12_synthetic_[0-9a-f]{12}\Z")



class ReadinessError(RuntimeError):
    """Bounded, secret-free denial with no cloud state mutation."""


def require(value: bool, code: str) -> None:
    """Deny ambiguous infrastructure, ownership or source evidence."""
    if not value:
        raise ReadinessError(code)


def task(profile: str, revision: int) -> dict:
    """Independently read the precise owned ECS task revision."""
    response = registered.aws(
        profile, "ecs", "describe-task-definition", "--task-definition",
        TASK_FAMILY + ":" + str(revision), "--include", "TAGS",
    )
    definition = response.get("taskDefinition", {})
    require(isinstance(definition, dict)
            and definition.get("revision") == revision
            and definition.get("family") == TASK_FAMILY
            and definition.get("status") == "ACTIVE",
            "EXACT_TASK_REVISION_UNVERIFIED")
    require(any(t.get("key") == "Environment"
                and t.get("value") == "nonproduction"
                for t in response.get("tags", []) if isinstance(t, dict)),
            "TASK_ENVIRONMENT_OWNERSHIP_INVALID")
    return definition



EXPECTED_VPC = "vpc-05a3c2c855c4dde26"
EXPECTED_SUBNETS = frozenset({
    "subnet-0a8fb56a15bc956db",
    "subnet-04eac8554980423b3",
    "subnet-0784e8739fcabf0e4",
})
MAX_PHASES = 3
MAX_PHASE_MINUTES = 10
PROPOSED_PHASES = ("CURRENT", "HISTORICAL", "CURRENT")


def network_configuration(profile: str) -> None:
    """Verify only the already-owned VPC's public outbound network *configuration*.

    Three unique subnets must implicitly or explicitly use an active route to
    an attached IGW. Does not authorize public inbound traffic, attest actual
    task connectivity or create paid VPC endpoints / NAT.
    """
    found = registered.aws(
        profile, "ec2", "describe-subnets", "--filters",
        "Name=vpc-id,Values=" + EXPECTED_VPC,
    ).get("Subnets", [])
    require(isinstance(found, list)
            and {x.get("SubnetId") for x in found if isinstance(x, dict)}
            == EXPECTED_SUBNETS
            and len(found) == len(EXPECTED_SUBNETS),
            "EXPECTED_NONPRODUCTION_SUBNETS_DRIFT")
    require(all(x.get("VpcId") == EXPECTED_VPC
                and x.get("State") == "available"
                and x.get("AvailableIpAddressCount", 0) > 0
                for x in found), "SUBNET_CAPACITY_OR_STATE_INVALID")
    routes = registered.aws(
        profile, "ec2", "describe-route-tables", "--filters",
        "Name=vpc-id,Values=" + EXPECTED_VPC,
    ).get("RouteTables", [])
    require(isinstance(routes, list), "ROUTE_TABLES_UNVERIFIED")
    main = [table for table in routes
            if isinstance(table, dict)
            and any(a.get("Main") is True for a in table.get("Associations", [])
                    if isinstance(a, dict))]
    require(len(main) == 1, "MAIN_ROUTE_TABLE_AMBIGUOUS")
    table = main[0]
    # An explicitly associated subnet must have its own verified route to
    # an internet gateway. The existing environment has no such association.
    associated = {a.get("SubnetId") for entry in routes if isinstance(entry, dict)
                  for a in entry.get("Associations", [])
                  if isinstance(a, dict) and a.get("SubnetId")}
    require(not (associated & EXPECTED_SUBNETS),
            "EXPLICIT_SUBNET_ROUTE_REQUIRES_SEPARATE_REVIEW")
    gateways = [r.get("GatewayId") for r in table.get("Routes", [])
                if isinstance(r, dict)
                and r.get("DestinationCidrBlock") == "0.0.0.0/0"
                and r.get("State") == "active"
                and isinstance(r.get("GatewayId"), str)
                and r["GatewayId"].startswith("igw-")]
    require(len(gateways) == 1, "ACTIVE_INTERNET_ROUTE_REQUIRED")
    igws = registered.aws(
        profile, "ec2", "describe-internet-gateways",
        "--internet-gateway-ids", gateways[0],
    ).get("InternetGateways", [])
    require(isinstance(igws, list) and len(igws) == 1
            and any(a.get("VpcId") == EXPECTED_VPC
                    and a.get("State") == "available"
                    for a in igws[0].get("Attachments", [])
                    if isinstance(a, dict)),
            "INTERNET_GATEWAY_ATTACHMENT_INVALID")
    # assignPublicIp must be explicitly ENABLED in the eventual ECS run-task
    # invocation; EC2 subnet's MapPublicIpOnLaunch is not an ECS task promise.


def rehearsal_envelope() -> dict:
    """Return a proposed serial drill contract, not permission to spend.

    Each current->historical->current phase requires an explicit operator
    gate, an external cost monitor, guaranteed task cleanup, and independent
    authenticated evidence against one persisted synthetic data source.
    """
    require(MAX_PHASES == len(PROPOSED_PHASES) == 3
            and 0 < MAX_PHASE_MINUTES <= 10,
            "REHEARSAL_PHASE_BOUND_INVALID")
    return {
        "phases": ",".join(PROPOSED_PHASES),
        "max_tasks_at_once": 1,
        "max_minutes_per_phase": MAX_PHASE_MINUTES,
        "max_total_minutes": MAX_PHASES * MAX_PHASE_MINUTES,
        "persistent_state_required": True,
        "authenticated_readback_required": True,
        "no_public_ingress": True,
        "public_ip_explicit_only": True,
        "cost_approval_required": True,
        "cleanup_readback_required": True,
    }

def check(profile: str) -> tuple[str, ...]:
    """Read exact budget, image, task, network and recovery prerequisites.

    Returns stable blocker codes. No AWS mutation, service start, task start,
    database access, secrets readback or production identity is possible.
    """
    head = published.preflight(profile)
    registered.foundation(profile)
    images = registered.images(profile, head)
    tasks = [task(profile, revision) for revision in REVISIONS]
    expected_images = list(images)
    blockers: list[str] = []
    for index, definition in enumerate(tasks):
        require(definition.get("runtimePlatform") == {
            "cpuArchitecture": "X86_64", "operatingSystemFamily": "LINUX",
        }, "TASK_PLATFORM_DRIFT")
        require(definition.get("cpu") == "256"
                and definition.get("memory") == "512",
                "TASK_COMPUTE_PROFILE_DRIFT")
        require(definition.get("networkMode") == "awsvpc"
                and "FARGATE" in definition.get("requiresCompatibilities", []),
                "TASK_NETWORK_COMPATIBILITY_DRIFT")
        containers = definition.get("containerDefinitions", [])
        require(isinstance(containers, list) and len(containers) == 1
                and containers[0].get("image") == expected_images[index],
                "TASK_IMAGE_IDENTITY_DRIFT")
        require(definition.get("executionRoleArn") == registered.ROLE,
                "TASK_EXECUTION_ROLE_DRIFT")
        require(not definition.get("taskRoleArn"), "TASK_ROLE_UNEXPECTED")
        require(not containers[0].get("secrets"), "TASK_SECRETS_UNEXPECTED")
        require(containers[0].get("readonlyRootFilesystem") is True,
                "TASK_ROOT_WRITABLE")
        require(containers[0].get("user") == "10001:10001",
                "TASK_USER_DRIFT")
        mounts = containers[0].get("mountPoints", [])
        volumes = definition.get("volumes", [])
        require(len(mounts) == 4 and len(volumes) == 4,
                "TASK_MOUNT_CONTRACT_DRIFT")
        require(all(v.get("name") in {m.get("sourceVolume") for m in mounts}
                    and not v.get("efsVolumeConfiguration")
                    for v in volumes), "TASK_STORAGE_CONTRACT_DRIFT")
        # These four mounts are deliberately task-local scratch. Their contents
        # DO NOT survive stop/rollback; this cannot prove persistent recovery.
        if "PERSISTENT_RECOVERY_STORAGE_NOT_VERIFIED" not in blockers:
            blockers.append("PERSISTENT_RECOVERY_STORAGE_NOT_VERIFIED")
        # No database URI, scoped credential, or encrypted secret reference is
        # present in either already-registered task definition. The same
        # database must survive replacement without exposing real tenant data.
        supplied = {item.get("name") for item in
                    containers[0].get("environment", [])
                    if isinstance(item, dict)}
        require(not (supplied & {"MONGODB_URI", "MONGO_URI",
                                 "WILSY_JWT_SECRET"}),
                "UNREVIEWED_TASK_CREDENTIAL_CONFIGURATION")
        require(not containers[0].get("secrets"),
                "UNREVIEWED_TASK_SECRET_CONFIGURATION")
        # Local scoped Atlas authentication can pass independently. Neither
        # already-registered ECS revision contains approved secret delivery.
        if "SCOPED_ATLAS_CREDENTIAL_NOT_CONFIGURED_IN_ECS" not in blockers:
            blockers.append("SCOPED_ATLAS_CREDENTIAL_NOT_CONFIGURED_IN_ECS")
        if "AUTHENTICATED_DATABASE_SOURCE_NOT_CONFIGURED" not in blockers:
            blockers.append("AUTHENTICATED_DATABASE_SOURCE_NOT_CONFIGURED")
    require(tasks[0].get("revision") < tasks[1].get("revision"),
            "TASK_REVISION_ORDER_INVALID")
    require(tasks[0].get("family") == tasks[1].get("family"),
            "TASK_FAMILY_DRIFT")
    # The only existing security group has no ingress, by foundation design.
    stacks = registered.aws(
        profile, "cloudformation", "describe-stacks",
        "--stack-name", published.STACK,
    ).get("Stacks", [])
    require(isinstance(stacks, list) and len(stacks) == 1,
            "FOUNDATION_STACK_NOT_VERIFIED")
    outputs = stacks[0].get("Outputs", [])
    matched = [x.get("OutputValue") for x in outputs
               if isinstance(x, dict) and x.get("OutputKey") == "ClosedSecurityGroup"]
    require(len(matched) == 1 and isinstance(matched[0], str)
            and matched[0].startswith("sg-"),
            "FOUNDATION_SECURITY_GROUP_OUTPUT_INVALID")
    groups = registered.aws(
        profile, "ec2", "describe-security-groups",
        "--group-ids", matched[0],
    ).get("SecurityGroups", [])
    require(isinstance(groups, list) and len(groups) == 1
            and groups[0].get("GroupId") == matched[0]
            and groups[0].get("VpcId") == EXPECTED_VPC,
            "EXACT_SECURITY_GROUP_UNVERIFIED")
    require(groups[0].get("IpPermissions") == [],
            "SECURITY_GROUP_UNEXPECTED_INGRESS")
    rules = groups[0].get("IpPermissionsEgress", [])
    require(len(rules) == 1 and rules[0].get("IpProtocol") == "tcp"
            and rules[0].get("FromPort") == 443
            and rules[0].get("ToPort") == 443,
            "SECURITY_GROUP_EGRESS_DRIFT")
    network_configuration(profile)
    # HTTPS-only egress is sufficient for ECR/CloudWatch control transport,
    # but blocks ordinary Atlas MongoDB TLS connections on TCP port 27017.
    # Do not add an unrestricted 27017 rule, weaken Atlas IP allowlists or
    # count this as a database-connection certificate.
    mongo_allowed = any(
        isinstance(rule, dict)
        and rule.get("IpProtocol") in {"tcp", "-1"}
        and (
            rule.get("IpProtocol") == "-1"
            or (type(rule.get("FromPort")) is int
                and type(rule.get("ToPort")) is int
                and rule["FromPort"] <= 27017 <= rule["ToPort"])
        )
        for rule in rules
    )
    if not mongo_allowed:
        blockers.append("ATLAS_TCP_27017_TASK_EGRESS_DENIED")
    blockers.append("ATLAS_TEST_CLUSTER_NETWORK_ALLOWLIST_NOT_CERTIFIED")
    blockers.append("INDEPENDENT_AUTHENTICATED_HTTP_READBACK_UNAVAILABLE")
    # ECR / CloudWatch logs require private endpoints, NAT, or public egress.
    # Nothing here authorizes a publicly exposed application endpoint.
    blockers.append("TASK_EGRESS_TO_ECR_AND_LOGS_NOT_CERTIFIED")
    registered.no_compute(profile)
    return tuple(blockers)



def verify_scoped_test_database(uri: str) -> str:
    """Read only the dedicated Atlas login authority with verified remote TLS.

    Does not test data continuity or grant an IAM/user role. Database names are
    reserved for new synthetic fixtures; sample and existing test DBs denied.
    """
    try:
        parts = urlsplit(uri)
        options = parse_qsl(parts.query, keep_blank_values=True)
    except (TypeError, ValueError) as exc:
        raise ReadinessError("ATLAS_URI_INVALID") from exc
    require(parts.scheme == "mongodb+srv"
            and parts.hostname == TEST_ATLAS_HOST
            and parts.port is None and parts.username is not None
            and parts.password is not None and parts.fragment == "",
            "EXACT_TEST_CLUSTER_TLS_URI_REQUIRED")
    database = parts.path.lstrip("/")
    require("/" not in database
            and SYNTHETIC_DB.fullmatch(database) is not None,
            "DEDICATED_SYNTHETIC_DATABASE_REQUIRED")
    lower = [(key.lower(), value.lower()) for key, value in options]
    blocked = {"tlsinsecure", "tlsallowinvalidcertificates",
               "tlsallowinvalidhostnames", "sslallowinvalidcertificates",
               "sslallowinvalidhostnames", "directconnection"}
    require(not any(key in blocked for key, _ in lower),
            "ATLAS_TLS_OVERRIDE_DENIED")
    require(not any(key in {"tls", "ssl"} and value != "true"
                    for key, value in lower), "ATLAS_TLS_REQUIRED")
    require(sum(key in {"authsource"} and value == "admin"
                for key, value in lower) <= 1
            and not any(key == "authsource" and value != "admin"
                        for key, value in lower), "ATLAS_AUTH_SOURCE_INVALID")
    require(len(options) == len({key for key, _ in lower}),
            "ATLAS_DUPLICATE_URI_OPTION_DENIED")
    try:
        from pymongo import MongoClient
        from pymongo.errors import PyMongoError

        with MongoClient(
            uri, tls=True, tlsAllowInvalidCertificates=False,
            tlsAllowInvalidHostnames=False,
            serverSelectionTimeoutMS=5000, connectTimeoutMS=5000,
            socketTimeoutMS=5000, retryWrites=False,
        ) as client:
            require(client.get_database(database).command("ping").get("ok") == 1,
                    "ATLAS_PING_UNVERIFIED")
            auth = client.admin.command("connectionStatus").get("authInfo", {})
            roles = auth.get("authenticatedUserRoles")
            require(isinstance(roles, list) and len(roles) == 1
                    and roles[0].get("role") == "readWrite"
                    and roles[0].get("db") == database,
                    "ATLAS_CREDENTIAL_NOT_DATABASE_SCOPED")
    except (PyMongoError, OSError, ValueError) as exc:
        raise ReadinessError("ATLAS_SCOPED_CONNECTION_UNAVAILABLE") from None
    return database

def main(argv: list[str] | None = None) -> int:
    """Report verified registration separately from blocked runtime readiness."""
    parser = argparse.ArgumentParser(description="MW-T12 read-only runtime gate")
    parser.add_argument("--profile", default="wilsy-legal-cert")
    parser.add_argument("--verify-scoped-database", action="store_true")
    args = parser.parse_args(argv)
    try:
        blockers = check(args.profile)
        if args.verify_scoped_database:
            uri = getpass("Scoped synthetic Atlas URI (hidden): ")
            require(bool(uri) and len(uri) <= 4096,
                    "ATLAS_URI_REQUIRED")
            verify_scoped_test_database(uri)
            print("MW_T12_SCOPED_ATLAS_CREDENTIAL=VERIFIED_READ_ONLY")
        print("MW_T12_RUNTIME_METADATA=VERIFIED")
        print("MW_T12_TASK_REVISIONS=1,2")
        print("MW_T12_RUNNING_TASKS=ZERO")
        print("MW_T12_PUBLIC_SUBNET_EGRESS_CONFIG=VERIFIED_NOT_LIVE")
        envelope = rehearsal_envelope()
        print("MW_T12_PLANNED_PHASES=" + envelope["phases"])
        print("MW_T12_MAX_SIMULTANEOUS_TASKS=" + str(envelope["max_tasks_at_once"]))
        print("MW_T12_MAX_PHASE_MINUTES=" + str(envelope["max_minutes_per_phase"]))
        print("MW_T12_MAX_TOTAL_MINUTES=" + str(envelope["max_total_minutes"]))
        print("MW_T12_COST_APPROVAL_REQUIRED=TRUE")
        for code in blockers:
            print("MW_T12_RUNTIME_BLOCKER=" + code)
        print("MW_T12_RUNTIME_RECOVERY_READY=FALSE")
        print("MW_T12_COMPUTE_LAUNCHED=FALSE")
        print("MW_T12_PRODUCTION_AUTHORIZED=FALSE")
        return 2
    except (ReadinessError, registered.AdmissionError,
            published.PublicationError, KeyboardInterrupt) as error:
        code = ("OPERATOR_INTERRUPTED" if isinstance(error, KeyboardInterrupt)
                else str(error))
        print("MW_T12_RUNTIME_GATE=FAIL_CLOSED")
        print("MW_T12_ERROR=" + code)
        print("MW_T12_COMPUTE_LAUNCHED=FALSE")
        print("MW_T12_PRODUCTION_AUTHORIZED=FALSE")
        return 2


if __name__ == "__main__":
    sys.exit(main())

# ARTIFACT: tools/eos/ops/mw_t12_runtime_readiness.py
# VERSION: v1.3.2-ATLAS-LOCAL-VS-ECS-ADMISSION-DISTINCTION
# AUTHORITY BOUNDARY: ECS/AWS read-only; no compute or recovery claims.
# TENANT POSTURE: No real tenant, IAM grant, source write or credential.
# FAIL-CLOSED POSTURE: Missing registration or recovery evidence denies.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
