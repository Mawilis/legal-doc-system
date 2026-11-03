# EOS mounted-router dependency closure — tranche 7

**Scope:** legal-operations command routes, role revocation, deadlines, client acceptance, owner commercial workspace, tenant branding and AI advisory/gateway composition.  
**Status:** source-import and composition closure; not a completed collection CRUD/index manifest.  
**No production changes.**

## 1. Legal Operations command router

`tools/eos/api/legal_operations_command_router.py` is not one repository. It composes multiple independently governed registries under one API-owned Mongo session/transaction. The request boundary obtains tenant authorization from server context; tenant, principal, role and authority are not accepted as body authority.

Directly imported persistence families include:

### IAM and authorization evidence
- `principal_authorities` — current principal authority.
- `tenant_memberships` — current tenant membership.
- `tenant_business_roles` — current business-role projection.
- `role_assignments` — role assignment currentness.
- `tenant_authorization_decision_evidence` — durable request authorization proof.

### Legal Operations lifecycle and process service
- `legal_operations_lifecycle` — canonical lifecycle journal.
- `process_service_allocation_receipts` and allocation-current projection (exact constants owned by process-service allocation registry).
- `process_service_attempt_authority_receipts` — cross-role attempt authority bridge.
- `process_service_attempt_transitions` — transition evidence.
- `process_service_attempt_outcomes` — terminal outcome evidence.
- `process_service_field_evidence` — Deputy field/device evidence.
- `process_service_returns` — return evidence.
- `process_service_location_observations`, permission grants and revocations — Deputy location evidence.

### Directory, workflow, conflict and notification
- Deputy principal bindings and device-provenance challenges.
- Legal conflict screening and human review evidence.
- Workflow definition, topology, stage, instance, gate-satisfaction and transition registries.
- Legal notification recipient bindings and binding lifecycle.
- Legal work item, assignment and completion-event registries.

The router resolves collections through a dynamic `database.get_collection(name)` helper. Therefore the actual least-privilege contract must be built from the imported registry constants and each registry's methods, not from a single router-level collection label.

**Operation/transaction contract:** the router itself does not issue the collection CRUD calls directly. It injects collection handles into orchestrators/registries, passes one caller-owned session, and performs the route transaction. Source-level collection action closure remains to be completed for each imported registry. In particular, do not infer all imported collections are writable: several are immutable append-only evidence or read-only IAM currentness authorities.

## 2. Ordinary authorization role revocation

`authorization_role_revocation_router.py` composes:
- role-assignment currentness;
- principal authority;
- tenant membership and business role;
- durable tenant authorization decision evidence;
- `authorization_role_revocation_evidence`.

The route starts one Mongo session/transaction and passes it to the certified command. The command owns current re-authorization, replay, target currentness, ordinary revocation policy, role-assignment CAS and immutable revocation evidence. Enterprise-admin and sovereign-architect roles are explicitly outside ordinary revocation authority. This is a distinct command capability; it must not be folded into generic IAM CRUD.

## 3. Legal matter deadlines

`legal_matter_deadline_router.py` composes:
- `legal_matter_deadlines` registry;
- `legal_operations_lifecycle` current matter lifecycle;
- deadline intelligence projection.

Routes create, list, read and project deadline intelligence for a case matter. The router delegates persistence to the deadline service and resolves collections dynamically. Exact registry CRUD, indexes and any scheduler/notification consumers remain to be inventoried before a role is designed.

## 4. Legal client acceptance instruments

`legal_client_acceptance_router.py` imports the following persistence authorities:
- tenant authorization decision evidence;
- legal client acceptance context;
- legal client acceptance records;
- acting-capacity evidence;
- instrument approval;
- instrument lifecycle;
- instrument definition;
- instrument content;
- matter visibility;
- matter parties;
- canonical legal matter lifecycle.

The router also composes content readers and provisioning/acceptance orchestrators. The HTTP source alone does not expose every persistence operation because registry calls are delegated. Treat content storage/read as a separate sensitivity boundary from acceptance mutation. Complete exact methods, indexes and object-storage use at the registry/service layer before role design.

## 5. Owner commercial workspace

`owner_commercial_workspace_router.py` composes:
- owner commercial work items;
- owner work assignment/history;
- tenant product entitlement current and history.

The router invokes the work registry's `ensure_indexes` during composition. This is another runtime DDL dependency that must move behind the dedicated index provisioner. Work item creation/completion is not entitlement administration; the current entitlement check is a separate read authority.

## 6. Tenant branding

`tenant_branding_router.py` composes current tenant branding profile, selected profile, asset records, branding entitlement, principal authority, membership and role assignments. Its current entitlement query is tenant-filtered and bounded. Branding asset object storage must be audited separately from Mongo metadata; no storage bucket or AWS identity should be inferred from collection use.

## 7. AI legal gateway and advisory

### Legal gateway
`wilsy_ai_legal_gateway_router.py` composes:
- `legal_ai_tool_invocations` — invocation evidence;
- `legal_operations_lifecycle` — legal matter currentness;
- process-service billing eligibility;
- process-service tariff assessment;
- AI entitlement;
- AI usage observation;
- role assignment, principal authority and membership repositories.

It authenticates/authorizes and completes commercial admission before materializing the domain read. The route owns the transaction; the invocation registry persists post-read evidence. Listing tools does not itself create invocation evidence.

### Legal services
`wilsy_ai_legal_services_router.py` composes AI entitlement and usage capacity/observation plus the server-owned C1C orchestrator. Its route's durable orchestration/invocation records are separate from the gateway's legal read invocation records. The route must not be granted provider credential, model billing or legal mutation authority merely because it can orchestrate allowlisted reads.

### Advisory
`wilsy_ai_advisory_router.py` delegates to `WilsyAIAdvisoryService`. The service imports:
- `ai_tool_orchestrations`;
- `legal_ai_tool_invocations`;
- `next_best_action_advisories`;
- principal authority, membership and role-assignment currentness;
- legal operations read adapter and domain adapter.

POST generation and GET retrieval have separate permission constants. Exact per-registry operations, index options, and transaction/uncertain-commit behavior remain to be closed at the service/registry level. Do not assume the advisory service is persistence-free because the router has no direct collection calls.

## 8. Explicit closure gaps

This tranche resolves source composition and names additional persistence authorities; it does **not** close:
- exact CRUD methods and session requirements for every imported registry;
- exact index key order, uniqueness, partial filters, TTL and collation options for these collections;
- transitive helper imports and indirect collections behind each orchestrator;
- deadline schedulers, notification delivery workers and cleanup consumers;
- object storage and KMS authorities for HR, Legal Evidence and branding assets;
- every billing, payroll, webhook and legacy tenant route;
- whether each source-tree worker/CLI is deployed or invoked.

The index manifest must not be marked complete from this document. All collection action and index entries need registry-source verification and tests.
