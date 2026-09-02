import json
import pytest
from tools.eos.governance.public_status import END, START, render_block, validate_text

STATUS={"schema_version":1,"project":"WILSY OS","current_frontier":"X","milestones":[]}
def test_render_is_deterministic():
    assert render_block(STATUS)==render_block(json.loads(json.dumps(STATUS)))
def test_exact_match():
    validate_text("head\n"+render_block(STATUS)+"\ntail",json.dumps(STATUS))
def test_drift_duplicate_and_missing_markers_fail():
    with pytest.raises(ValueError): validate_text(render_block(STATUS).replace('WILSY OS','OTHER'),json.dumps(STATUS))
    with pytest.raises(ValueError): validate_text(render_block(STATUS)+START,json.dumps(STATUS))
    with pytest.raises(ValueError): validate_text('no markers',json.dumps(STATUS))
def test_malformed_schema_fails():
    with pytest.raises(ValueError): validate_text(render_block(STATUS),'{}')
    with pytest.raises(ValueError): validate_text(render_block(STATUS),json.dumps({"schema_version":2,"current_frontier":"X","milestones":[]}))
