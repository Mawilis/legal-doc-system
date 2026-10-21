"""Regression: one practitioner/matter must not have competing active grants."""
from pathlib import Path
import runpy
import pytest

from tools.eos.legal_operations.registry import (
    legal_practitioner_matter_binding_registry as registry,
)

ROOT = Path(__file__).resolve().parents[2]
fixture = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_matter_binding.py")
)
fake = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_matter_binding_registry.py")
)
make = fixture["make"]
Collection = fake["Collection"]
Session = fake["Session"]


def test_second_active_binding_same_practitioner_matter_rejected():
    """Different binding IDs must not create simultaneous active authority."""
    col = Collection()
    tx = Session()
    first = make(binding_id="binding-one")
    competing = make(binding_id="binding-two")

    assert first.binding_id != competing.binding_id
    assert first.tenant_id == competing.tenant_id
    assert first.case_matter_id == competing.case_matter_id
    assert (
        first.practitioner_principal_id
        == competing.practitioner_principal_id
    )

    registry.append_binding(
        binding=first, collection=col, session=tx,
    )
    with pytest.raises(registry.BindingConflict):
        registry.append_binding(
            binding=competing, collection=col, session=tx,
        )

    assert len(col.rows) == 1


# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P6-R7B-P4-R2A
# END OF WILSY OS SOVEREIGN ARTIFACT
