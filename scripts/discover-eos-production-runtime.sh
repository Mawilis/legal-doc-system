#!/usr/bin/env bash
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

  echo "[EKS CLUSTERS]"
  aws_read eks list-clusters --region "$region" \
    --query 'clusters' --output table || echo "EKS_INVENTORY=UNAVAILABLE"

  echo "[ECS CLUSTERS]"
  aws_read ecs list-clusters --region "$region" \
    --query 'clusterArns' --output table || echo "ECS_INVENTORY=UNAVAILABLE"

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
