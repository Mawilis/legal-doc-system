"""WILSY OS — test-first Legal work-assignment permission certificate.

AUTHORITY: Non-granting canonical IAM vocabulary test.
SCOPE: Own-tenant assignment-command permission identity only.
EXCLUSIONS: No role grants, assignment persistence, IAM mutations,
HTTP commands, financial authority or external network access.
"""

import json

from tools.eos.auth.permission_namespace import (
    canonical_permissions,
)

ASSIGNMENT_PERMISSION = "legal_operations:work_assignment:write"


def test_assignment_write_permission_has_explicit_canonical_identity():
    """Assignment cannot borrow work-item write or completion authority."""
    raw = canonical_permissions()
    assert isinstance(raw, bytes)
    records = json.loads(raw.decode('utf-8'))
    assert isinstance(records, list)
    permissions = {record['permission_id'] for record in records}
    assert 'legal_operations:work_item:write' in permissions
    assert ASSIGNMENT_PERMISSION in permissions, (
        "LEGAL_WORK_ASSIGNMENT_DEDICATED_PERMISSION_ABSENT"
    )
    assert ASSIGNMENT_PERMISSION != "legal_operations:work_item:write"
    assert ASSIGNMENT_PERMISSION != "legal_operations:work_item:complete"
