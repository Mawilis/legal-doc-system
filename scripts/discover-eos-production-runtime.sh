#!/usr/bin/env bash
# TITLE: WILSY EOS Production Runtime Read-Only AWS Discovery
# VERSION: v1.0.1-EOS-PRODUCTION-PREREQUISITE-INVENTORY
# AUTHORITY: Read-only AWS inventory only; no cloud provisioning or deployment authority.
# EPITOME: Enumerate account identity and available regional AWS hosting, workload identity, compute, ingress and CloudFormation metadata to identify candidate EOS production hosting without inferring that discovered resources serve EOS.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/scripts/discover-eos-production-runtime.sh
# COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; production hosting owner must verify actual service ownership and traffic path.
# CERTIFICATION OR UPDATE DATE: 2026-11-09
# CHANGELOG:
#   v1.0.1 adds read-only metadata discovery for candidate production
#   Secrets Manager references, KMS aliases, VPC/subnet/security-group/egress,
#   target groups, ACM certificates and Route 53 hosted zones. Secret values
#   are never read. No infrastructure mutation is introduced.
#   v1.0.0-EOS-PRODUCTION-RUNTIME-DISCOVERY establishes a read-only AWS
#   regional inventory of EKS/OIDC, ECS, Lambda, App Runner, Elastic Beanstalk,
#   Lightsail, EC2, load balancers and CloudFormation metadata.
# COMPLIANCE: AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
# SECURITY / PRIVACY POSTURE: Emits account identity and infrastructure metadata only; never reads secrets, environment values or application data.
# TENANT BOUNDARY: Does not connect to MongoDB or inspect tenant/principal records.
# AUTHORITY BOUNDARY: No assume-role, create, update, delete, change-set, task-launch or deploy operation is performed.
# FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains the exclusive financial execution authority.
# FAIL-CLOSED DECLARATION: AWS CLI or identity/region inventory failures are reported explicitly; incomplete provider inventory is not interpreted as proof of absence.

# Read-only inventory to identify the actual AWS-hosted EOS production target.
# This script never creates, updates, deletes, assumes, or deploys cloud resources.
set -uo pipefail

PROFILE="${WILSY_EOS_AWS_ADMIN_PROFILE:-wilsy-legal-cert}"
SEED_REGION="${AWS_REGION:-af-south-1}"
export AWS_PAGER=""

if ! command -v aws >/dev/null 2>&1; then
  echo "DISCOVERY_ERROR=AWS_CLI_REQUIRED" >&2
  exit 2
fi

aws_read() {
  aws "$@" --profile "$PROFILE" --no-cli-pager
}

echo "=== EOS PRODUCTION RUNTIME DISCOVERY (READ ONLY) ==="
echo "AWS_PROFILE=$PROFILE"
echo "SEED_REGION=$SEED_REGION"

echo
echo "--- ACCOUNT IDENTITY ---"
if ! aws_read sts get-caller-identity --query '{Account:Account,Arn:Arn}' --output json; then
  echo "DISCOVERY_ERROR=AWS_IDENTITY_UNAVAILABLE" >&2
  exit 3
fi

echo
echo "--- GLOBAL IAM OIDC PROVIDERS ---"
aws_read iam list-open-id-connect-providers \
  --query 'OpenIDConnectProviderList[].Arn' --output table || echo "OIDC_INVENTORY=UNAVAILABLE"

echo
echo "--- EOS/WILSY IAM ROLES (NAMES AND ARNS ONLY) ---"
aws_read iam list-roles \
  --query "Roles[?contains(RoleName, 'eos') || contains(RoleName, 'wilsy')].[RoleName,Arn]" \
  --output table || echo "IAM_ROLE_INVENTORY=UNAVAILABLE"

echo
echo "--- ROUTE 53 HOSTED ZONES (NAMES AND IDS ONLY) ---"
aws_read route53 list-hosted-zones \
  --query "HostedZones[].{Name:Name,Id:Id,Private:Config.PrivateZone}" \
  --output table || echo "ROUTE53_INVENTORY=UNAVAILABLE"

echo
echo "--- ENABLED AWS REGIONS ---"
REGIONS="$(aws_read ec2 describe-regions --all-regions \
  --filters Name=opt-in-status,Values=opt-in-not-required,opted-in \
  --query 'Regions[].RegionName' --output text)" || {
  echo "DISCOVERY_ERROR=REGION_INVENTORY_UNAVAILABLE" >&2
  exit 4
}
if [[ -z "$REGIONS" || "$REGIONS" == "None" ]]; then
  echo "DISCOVERY_ERROR=NO_ENABLED_REGIONS_RETURNED" >&2
  exit 5
fi
printf '%s\n' "$REGIONS" | tr '\t' '\n' | while IFS= read -r region; do
  [[ -n "$region" ]] || continue
  echo
  echo "===== REGION: $region ====="

  echo "[EKS CLUSTERS AND OIDC ISSUERS]"
  EKS_CLUSTERS="$(aws_read eks list-clusters --region "$region" --query 'clusters' --output text)" || {
    echo "EKS_INVENTORY=UNAVAILABLE"
    EKS_CLUSTERS=""
  }
  if [[ -n "$EKS_CLUSTERS" && "$EKS_CLUSTERS" != "None" ]]; then
    printf '%s\n' "$EKS_CLUSTERS" | tr '\t' '\n' | while IFS= read -r cluster; do
      [[ -n "$cluster" ]] || continue
      aws_read eks describe-cluster --name "$cluster" --region "$region" \
        --query 'cluster.{Name:name,Arn:arn,Status:status,Version:version,Endpoint:endpoint,OidcIssuer:identity.oidc.issuer}' \
        --output json || echo "EKS_CLUSTER_DETAIL_UNAVAILABLE=$cluster"
    done
  else
    echo "EKS_CLUSTERS=NONE_REPORTED"
  fi

  echo "[ECS CLUSTERS]"
  aws_read ecs list-clusters --region "$region" \
    --query 'clusterArns' --output table || echo "ECS_INVENTORY=UNAVAILABLE"

  echo "[WILSY/EOS SECRET METADATA ONLY — NEVER SECRET VALUES]"
  aws_read secretsmanager list-secrets --region "$region" \
    --filters Key=name,Values=wilsy,eos,ghcr,mongo,atlas \
    --query 'SecretList[].{Name:Name,Arn:ARN,LastChanged:LastChangedDate,KmsKeyId:KmsKeyId}' \
    --output table || echo "SECRETS_MANAGER_METADATA_INVENTORY=UNAVAILABLE"

  echo "[WILSY/EOS KMS ALIASES]"
  aws_read kms list-aliases --region "$region" \
    --query "Aliases[?contains(AliasName, 'wilsy') || contains(AliasName, 'eos')].[AliasName,TargetKeyId]" \
    --output table || echo "KMS_ALIAS_INVENTORY=UNAVAILABLE"

  echo "[VPCS]"
  aws_read ec2 describe-vpcs --region "$region" \
    --query "Vpcs[].{VpcId:VpcId,Cidr:CidrBlock,State:State,Name:Tags[?Key=='Name']|[0].Value}" \
    --output table || echo "VPC_INVENTORY=UNAVAILABLE"

  echo "[SUBNETS]"
  aws_read ec2 describe-subnets --region "$region" \
    --query 'Subnets[].{SubnetId:SubnetId,VpcId:VpcId,AZ:AvailabilityZone,Cidr:CidrBlock,PublicIp:MapPublicIpOnLaunch}' \
    --output table || echo "SUBNET_INVENTORY=UNAVAILABLE"

  echo "[SECURITY GROUP METADATA]"
  aws_read ec2 describe-security-groups --region "$region" \
    --query 'SecurityGroups[].{GroupId:GroupId,Name:GroupName,VpcId:VpcId,Description:Description}' \
    --output table || echo "SECURITY_GROUP_INVENTORY=UNAVAILABLE"

  echo "[AVAILABLE OR PENDING NAT GATEWAYS]"
  aws_read ec2 describe-nat-gateways --region "$region" \
    --filter Name=state,Values=available,pending \
    --query 'NatGateways[].{NatGatewayId:NatGatewayId,VpcId:VpcId,SubnetId:SubnetId,State:State}' \
    --output table || echo "NAT_GATEWAY_INVENTORY=UNAVAILABLE"

  echo "[VPC ENDPOINTS]"
  aws_read ec2 describe-vpc-endpoints --region "$region" \
    --query 'VpcEndpoints[].{VpcEndpointId:VpcEndpointId,VpcId:VpcId,ServiceName:ServiceName,State:State,PrivateDns:PrivateDnsEnabled}' \
    --output table || echo "VPC_ENDPOINT_INVENTORY=UNAVAILABLE"

  echo "[LAMBDA FUNCTIONS]"
  aws_read lambda list-functions --region "$region" \
    --query 'Functions[].{Name:FunctionName,Runtime:Runtime,Handler:Handler,Modified:LastModified}' \
    --output table || echo "LAMBDA_INVENTORY=UNAVAILABLE"

  echo "[APP RUNNER SERVICES]"
  aws_read apprunner list-services --region "$region" \
    --query 'ServiceSummaryList[].{Name:ServiceName,Status:Status,Arn:ServiceArn}' \
    --output table || echo "APP_RUNNER_INVENTORY=UNAVAILABLE"

  echo "[ELASTIC BEANSTALK ENVIRONMENTS]"
  aws_read elasticbeanstalk describe-environments --region "$region" \
    --no-include-deleted \
    --query 'Environments[].{Application:ApplicationName,Environment:EnvironmentName,Status:Status,Endpoint:CNAME}' \
    --output table || echo "ELASTIC_BEANSTALK_INVENTORY=UNAVAILABLE"

  echo "[LIGHTSAIL CONTAINER SERVICES]"
  aws_read lightsail get-container-services --region "$region" \
    --query 'containerServices[].{Name:containerServiceName,State:state,Url:url}' \
    --output table || echo "LIGHTSAIL_INVENTORY=UNAVAILABLE"

  echo "[RUNNING EC2 INSTANCES]"
  aws_read ec2 describe-instances --region "$region" \
    --filters Name=instance-state-name,Values=running \
    --query "Reservations[].Instances[].{Instance:InstanceId,Name:Tags[?Key=='Name']|[0].Value,PrivateDns:PrivateDnsName,PublicDns:PublicDnsName,Vpc:VpcId}" \
    --output table || echo "EC2_INVENTORY=UNAVAILABLE"

  echo "[LOAD BALANCERS]"
  aws_read elbv2 describe-load-balancers --region "$region" \
    --query 'LoadBalancers[].{Name:LoadBalancerName,Type:Type,State:State.Code,DNS:DNSName,Vpc:VpcId}' \
    --output table || echo "LOAD_BALANCER_INVENTORY=UNAVAILABLE"

  echo "[LOAD BALANCER TARGET GROUPS]"
  aws_read elbv2 describe-target-groups --region "$region" \
    --query 'TargetGroups[].{Name:TargetGroupName,Arn:TargetGroupArn,Protocol:Protocol,Port:Port,VpcId:VpcId,TargetType:TargetType}' \
    --output table || echo "TARGET_GROUP_INVENTORY=UNAVAILABLE"

  echo "[ACM CERTIFICATE METADATA]"
  aws_read acm list-certificates --region "$region" \
    --query 'CertificateSummaryList[].{Domain:DomainName,Arn:CertificateArn,Status:Status}' \
    --output table || echo "ACM_INVENTORY=UNAVAILABLE"

  echo "[CLOUDFORMATION STACKS]"
  aws_read cloudformation list-stacks --region "$region" \
    --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE UPDATE_ROLLBACK_COMPLETE IMPORT_COMPLETE \
    --query 'StackSummaries[].{Name:StackName,Status:StackStatus,Updated:LastUpdatedTime}' \
    --output table || echo "CLOUDFORMATION_INVENTORY=UNAVAILABLE"
done

echo
echo "=== DISCOVERY COMPLETE ==="
echo "This inventory does not prove that any discovered resource serves EOS."
echo "Confirm the live deployment's repository, image digest, DNS/ingress, runtime identity, and owner before KMS binding."

# ARTIFACT: scripts/discover-eos-production-runtime.sh
# VERSION: v1.0.1-EOS-PRODUCTION-PREREQUISITE-INVENTORY
# AUTHORITY BOUNDARY: Read-only infrastructure inventory only; no cloud mutation or deployment.
# TENANT POSTURE: No tenant, principal, session or database records are accessed or mutated.
# FAIL-CLOSED POSTURE: Unavailable regional APIs remain explicitly unavailable; discovered resources are not presumed to host EOS.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
