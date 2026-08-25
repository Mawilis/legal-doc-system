"""
Wilsy Engineering Kernel
Engineering Constitution Manager

Constitution Validator

Read-only validation contract.
"""

from __future__ import annotations

from typing import List

from .domain.models import Constitution
from .domain.models import ValidationFinding


class ConstitutionValidator:
    """Public validator contract."""

    def validate(
        self,
        constitution: Constitution,
    ) -> List[ValidationFinding]:
        """
        Validate a parsed Constitution model.

        Raises
        ------
        NotImplementedError
            Implemented in FG132C.
        """
        raise NotImplementedError(
            "FG132C implements constitutional validation."
        )