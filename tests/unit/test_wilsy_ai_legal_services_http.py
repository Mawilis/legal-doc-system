"""C1C HTTP contract certificate."""
from tools.eos.api.wilsy_ai_legal_services_router import WilsyAILegalServicesRequest
from pydantic import ValidationError
import pytest

def test_prompt_only_body_forbids_authority_fields():
    assert WilsyAILegalServicesRequest(prompt="hello").prompt == "hello"
    with pytest.raises(ValidationError):
        WilsyAILegalServicesRequest.model_validate({"prompt": "hello", "tenant_id": "foreign"})

# ARTIFACT: test_wilsy_ai_legal_services_http.py
# VERSION: v1.1.0-C1C-R1A
# END OF WILSY OS SOVEREIGN ARTIFACT
