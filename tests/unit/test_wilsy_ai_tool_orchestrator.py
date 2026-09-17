"""C1C bounded planner/tool/synthesis certificate."""
from tools.eos.intelligence.wilsy_ai_tool_orchestrator import *
from tools.eos.intelligence.tools.registry import *
from tools.eos.intelligence.domain.ai_tool_orchestration import *
from tools.eos.intelligence.domain.ai_model_execution import ModelProviderResult
import pytest

class Provider:
    provider_id="test-provider"; model_id="test-model"
    def __init__(self): self.calls=0
    def execute(self, request):
        self.calls += 1
        if "planner" in request.system_policy:
            return ModelProviderResult(provider_id=self.provider_id, model_id=self.model_id, response_text='{"decision":"TOOL","tool_identity":"legal.instruction.read.v1","arguments":{"resource_identity":"instruction-1"}}')
        return ModelProviderResult(provider_id=self.provider_id, model_id=self.model_id, response_text="grounded")

def test_strict_parser_rejects_extra_keys():
    with pytest.raises(C1COrchestrationError): parse_planner_json('{"decision":"FINAL","response_text":"x","extra":1}')

def test_tool_assisted_flow_replays_without_provider_reexecution():
    provider=Provider(); contract=AIToolContract("legal.instruction.read.v1","v1","legal_operations","legal.read.instruction","legal_operations:instruction:read",ToolRiskClass.READ_ONLY,"LEGAL_PII",("resource_identity",))
    reg=ServerOwnedAIToolRegistry((RegisteredAITool(contract, lambda **_: {"instruction_id":"instruction-1","state":"ALLOCATED"}),))
    result=WilsyAIToolOrchestrator(tool_registry=reg, model_provider=provider, egress_policy=AllowTestEgress()).run(tenant_id="tenant1",principal_id="principal1",idempotency_key="key1",prompt="status")
    replay=WilsyAIToolOrchestrator(tool_registry=reg, model_provider=provider, egress_policy=AllowTestEgress())
    assert result.outcome == "TOOL_ASSISTED" and provider.calls == 2
    assert result.sources[0]["tool_identity"] == "legal.instruction.read.v1"


class _Session:
    def __init__(self) -> None:
        self.in_transaction = False
        self.commits = 0
        self.aborts = 0

    def start_transaction(self) -> None:
        self.in_transaction = True

    def commit_transaction(self) -> None:
        self.in_transaction = False
        self.commits += 1

    def abort_transaction(self) -> None:
        self.in_transaction = False
        self.aborts += 1

    def end_session(self) -> None:
        self.in_transaction = False


class _RootRegistry:
    def __init__(self) -> None:
        self.rows = {}
        self.phases = []

    def get(self, *, tenant_id, orchestration_id, session):
        try:
            return self.rows[(tenant_id, orchestration_id)]
        except KeyError as error:
            raise ValueError("C1C_NOT_FOUND") from error

    def create_or_replay(self, item, *, session):
        self.rows[(item.tenant_id, item.orchestration_id)] = item
        self.phases.append(item.phase)
        return item

    def transition(self, item, *, expected_revision, session):
        self.rows[(item.tenant_id, item.orchestration_id)] = item
        self.phases.append(item.phase)
        return item


def _production_fixture():
    provider = Provider()
    contract = AIToolContract("legal.instruction.read.v1", "v1", "legal_operations", "legal.read.instruction", "legal_operations:instruction:read", ToolRiskClass.READ_ONLY, "LEGAL_PII", ("resource_identity",))
    registry = ServerOwnedAIToolRegistry((RegisteredAITool(contract, lambda **_: {"instruction_id": "instruction-1", "state": "ALLOCATED"}),))
    roots = _RootRegistry()
    sessions = []

    def session_factory():
        session = _Session()
        sessions.append(session)
        return session

    accounting_sessions = []

    def accounting_writer(**kwargs):
        accounting_sessions.append(kwargs["session"])
        return "l7b-evidence:c1c-tool"

    return provider, registry, roots, session_factory, accounting_writer, sessions, accounting_sessions


def test_production_durable_phases_and_restart_replay() -> None:
    provider, registry, roots, factory, writer, _, accounting_sessions = _production_fixture()
    first = WilsyAIToolOrchestrator(tool_registry=registry, model_provider=provider, egress_policy=AllowTestEgress(), root_registry=roots, root_session_factory=factory, tool_accounting_writer=writer, production=True).run(tenant_id="tenant1", principal_id="principal1", idempotency_key="key1", prompt="status")
    assert first.outcome == "TOOL_ASSISTED"
    assert [phase.value for phase in roots.phases] == ["STARTED", "PLANNED_TOOL", "TOOL_COMPLETED", "COMPLETED"]
    assert len(accounting_sessions) == 1
    assert provider.calls == 2
    replay_provider, _, _, replay_factory, replay_writer, _, _ = _production_fixture()
    replay_provider.calls = 0
    with pytest.raises(C1COrchestrationError, match="C1C_REPLAY_DURABLE"):
        WilsyAIToolOrchestrator(tool_registry=registry, model_provider=replay_provider, egress_policy=AllowTestEgress(), root_registry=roots, root_session_factory=replay_factory, tool_accounting_writer=replay_writer, production=True).run(tenant_id="tenant1", principal_id="principal1", idempotency_key="key1", prompt="status")
    assert replay_provider.calls == 0


def test_production_accounting_failure_reconciles_without_synthesis() -> None:
    provider, registry, roots, factory, _, _, _ = _production_fixture()

    def failing_writer(**_kwargs):
        raise RuntimeError("usage write failed")

    with pytest.raises(C1COrchestrationError, match="C1C_TOOL_ACCOUNTING_UNAVAILABLE"):
        WilsyAIToolOrchestrator(tool_registry=registry, model_provider=provider, egress_policy=AllowTestEgress(), root_registry=roots, root_session_factory=factory, tool_accounting_writer=failing_writer, production=True).run(tenant_id="tenant1", principal_id="principal1", idempotency_key="key1", prompt="status")
    assert provider.calls == 1
    assert roots.phases[-1].value == "RECONCILIATION_REQUIRED"


def test_unknown_planned_tool_commit_blocks_tool_and_synthesis() -> None:
    provider, registry, roots, _, writer, _, _ = _production_fixture()
    sessions = []

    class UnknownCommitSession(_Session):
        def commit_transaction(self) -> None:
            if len(sessions) == 2:
                self.in_transaction = True
                raise RuntimeError("commit outcome unknown")
            super().commit_transaction()

    def factory() -> UnknownCommitSession:
        session = UnknownCommitSession()
        sessions.append(session)
        return session

    tool_calls = []
    contract = AIToolContract("legal.instruction.read.v1", "v1", "legal_operations", "legal.read.instruction", "legal_operations:instruction:read", ToolRiskClass.READ_ONLY, "LEGAL_PII", ("resource_identity",))
    registry = ServerOwnedAIToolRegistry((RegisteredAITool(contract, lambda **kwargs: tool_calls.append(kwargs) or {"instruction_id": "instruction-1"}),))
    with pytest.raises(C1COrchestrationError, match="C1C_DURABLE_ROOT_UNAVAILABLE"):
        WilsyAIToolOrchestrator(tool_registry=registry, model_provider=provider, egress_policy=AllowTestEgress(), root_registry=roots, root_session_factory=factory, tool_accounting_writer=writer, production=True).run(tenant_id="tenant1", principal_id="principal1", idempotency_key="unknown-commit", prompt="status")
    assert provider.calls == 1
    assert tool_calls == []

# ARTIFACT: test_wilsy_ai_tool_orchestrator.py
# VERSION: v1.1.0-C1C-R1B
# CHANGELOG: v1.1.0-C1C-R1B certifies durable phase ordering, atomic
# accounting failure reconciliation, and restart-safe replay.
# END OF WILSY OS SOVEREIGN ARTIFACT
