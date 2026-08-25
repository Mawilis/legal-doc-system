#!/usr/bin/env python3
"""
WILSY OS — PDF KERNEL CONTRACT & SIGNATURE VERIFICATION SUITE
Enforces absolute signature parity and contract locks on ExecutiveReportBuilder.
"""

import inspect
import pytest
from typing import get_type_hints
from scripts.lib.executive_pdf_kernel import ExecutiveReportBuilder

def test_add_metadata_box_signature():
    """Validates that add_metadata_box requires exactly 1 positional argument (metadata)."""
    sig = inspect.signature(ExecutiveReportBuilder.add_metadata_box)
    params = list(sig.parameters.values())
    
    # Exclude 'self'
    method_params = [p for p in params if p.name != 'self']
    assert len(method_params) == 1, f"Contract Violation: add_metadata_box expects 1 argument, found {len(method_params)}"
    assert method_params[0].name == 'metadata', f"Parameter name mismatch: expected 'metadata', got '{method_params[0].name}'"

def test_add_telemetry_table_signature():
    """Validates add_telemetry_table contract."""
    sig = inspect.signature(ExecutiveReportBuilder.add_telemetry_table)
    params = [p.name for p in sig.parameters.values() if p.name != 'self']
    expected = ['section_title', 'stages']
    assert params == expected, f"Signature drift in add_telemetry_table: expected {expected}, got {params}"

def test_add_cryptographic_proof_block_signature():
    """Validates add_cryptographic_proof_block contract."""
    sig = inspect.signature(ExecutiveReportBuilder.add_cryptographic_proof_block)
    params = [p.name for p in sig.parameters.values() if p.name != 'self']
    expected = ['merkle_root', 'execution_id', 'zk_commitment']
    assert params == expected, f"Signature drift in add_cryptographic_proof_block: expected {expected}, got {params}"

def test_add_signoff_signature():
    """Validates add_signoff contract."""
    sig = inspect.signature(ExecutiveReportBuilder.add_signoff)
    params = [p.name for p in sig.parameters.values() if p.name != 'self']
    expected = ['left_person', 'right_status']
    assert params == expected, f"Signature drift in add_signoff: expected {expected}, got {params}"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
