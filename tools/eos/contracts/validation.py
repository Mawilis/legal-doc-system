"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Execution Contracts Framework - Validation Engine.
    Verifies institutional compliance and protocol conformance across Wilsy OS contracts.

Biblical Scale & Architecture:
    Production-ready enterprise validation suite. Zero child's place.
    Ensures all subsystem implementations strictly adhere to defined contracts.

Collaboration & Maintenance:
    - [Validation]: Inspects protocol adherence and contract implementation integrity.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Any, Type

from .domain.execution_contract import ExecutionContract
from .domain.repository_contract import RepositoryContract
from .domain.report_contract import ReportContract
from .domain.ai_contract import AIContract
from .domain.review_contract import ReviewContract
from .domain.release_contract import ReleaseContract

logger = logging.getLogger("WilsyContractsValidation")


class ContractValidator:
    """
    Validates institutional contract conformance for Wilsy OS modules.
    """

    @staticmethod
    def validate_contract_implementation(
        instance: Any,
        contract_class: Type[Any],
    ) -> bool:
        """
        Validates that a given instance strictly implements a target institutional contract.

        Args:
            instance (Any): The engine or component instance to validate.
            contract_class (Type[Any]): The target contract base class.

        Returns:
            bool: True if fully compliant; raises TypeError or attribute errors otherwise.
        """
        if not isinstance(instance, contract_class):
            error_msg = (
                f"Institutional Validation Failure: Instance '{type(instance).__name__}' "
                f"does not conform to contract '{contract_class.__name__}'."
            )
            logger.error(error_msg)
            raise TypeError(error_msg)

        # Validate mandatory protocol attributes exist
        for attr in ("name", "version"):
            if not hasattr(instance, attr):
                error_msg = (
                    f"Institutional Validation Failure: Instance '{type(instance).__name__}' "
                    f"is missing required contract attribute '{attr}'."
                )
                logger.error(error_msg)
                raise AttributeError(error_msg)

        logger.info(
            f"Contract Validation Successful: '{type(instance).__name__}' "
            f"conforms to '{contract_class.__name__}' v{getattr(instance, 'version')}."
        )
        return True
