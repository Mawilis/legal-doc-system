"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE
FILE: tools/eos/documentation/documentation_builder.py
===============================================================================
Epitome:
    Automated metadata extraction builder for Wilsy OS. Inspects Python modules,
    type hints, function signatures, and docstrings at runtime to assemble
    strictly typed DocumentationEntity contracts without human intervention.

Biblical Worth Billions:
    "Through wisdom is an house builded; and by understanding it is established."
    — Proverbs 24:3

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/documentation/documentation_builder.py
===============================================================================
"""

import inspect
import types
from typing import Dict, List, Any, Optional, Type
from tools.eos.documentation.documentation_contract import (
    DocumentationEntity,
    EntityKind,
    InterfaceSpec,
    VerificationStatus,
)


class DocumentationBuilder:
    """
    Builder engine for extracting runtime metadata from Python objects
    and constructing immutable DocumentationEntity contracts.
    """

    @staticmethod
    def build_from_module(
        module: types.ModuleType,
        urn: str,
        kind: EntityKind = EntityKind.ENGINE,
        version: str = "2.0.0",
        lifecycle_stage: str = "PRODUCTION",
        override_title: Optional[str] = None,
        override_purpose: Optional[str] = None,
    ) -> DocumentationEntity:
        """
        Reflects upon a Python module to extract public function signatures, docstrings,
        and module path into a structured DocumentationEntity.

        Args:
            module: Imported Python module.
            urn: Target unique documentation URN.
            kind: EntityKind classification.
            version: Target version string.
            lifecycle_stage: Module execution lifecycle state.
            override_title: Optional custom title override.
            override_purpose: Optional custom purpose override.

        Returns:
            Fully populated DocumentationEntity contract.
        """
        docstring = inspect.getdoc(module) or "No module docstring available."
        lines = [line.strip() for line in docstring.split("\n") if line.strip()]
        
        title = override_title or (lines[0] if lines else module.__name__)
        purpose = override_purpose or (" ".join(lines[1:3]) if len(lines) > 1 else title)

        interfaces: List[InterfaceSpec] = []
        for name, func in inspect.getmembers(module, predicate=inspect.isfunction):
            if not name.startswith("_"):
                try:
                    sig = inspect.signature(func)
                    params = {p.name: str(p.annotation) for p in sig.parameters.values()}
                    ret_type = str(sig.return_annotation)
                    func_doc = inspect.getdoc(func) or "No method description provided."
                    interfaces.append(
                        InterfaceSpec(
                            name=name,
                            description=func_doc,
                            parameters=params,
                            return_type=ret_type,
                            is_async=inspect.iscoroutinefunction(func),
                        )
                    )
                except Exception:
                    continue

        return DocumentationEntity(
            urn=urn,
            kind=kind,
            title=title,
            purpose=purpose,
            module_path=getattr(module, "__file__", module.__name__),
            version=version,
            architecture_summary=f"Automated module extraction for {module.__name__}",
            lifecycle_stage=lifecycle_stage,
            interfaces=interfaces,
            verification_status=VerificationStatus.VERIFIED,
        )

    @staticmethod
    def build_from_class(
        target_cls: Type[Any],
        urn: str,
        kind: EntityKind = EntityKind.CONTRACT,
        version: str = "2.0.0",
    ) -> DocumentationEntity:
        """
        Extracts public methods, signatures, and docstrings from a Python class.

        Args:
            target_cls: Python class object to introspect.
            urn: Target unique documentation URN.
            kind: EntityKind classification.
            version: Target version string.

        Returns:
            Fully populated DocumentationEntity contract.
        """
        docstring = inspect.getdoc(target_cls) or f"Class specification for {target_cls.__name__}"
        interfaces: List[InterfaceSpec] = []

        for name, method in inspect.getmembers(target_cls, predicate=inspect.isfunction):
            if not name.startswith("_"):
                try:
                    sig = inspect.signature(method)
                    params = {p.name: str(p.annotation) for p in sig.parameters.values()}
                    ret_type = str(sig.return_annotation)
                    interfaces.append(
                        InterfaceSpec(
                            name=name,
                            description=inspect.getdoc(method) or "No method docstring",
                            parameters=params,
                            return_type=ret_type,
                            is_async=inspect.iscoroutinefunction(method),
                        )
                    )
                except Exception:
                    continue

        return DocumentationEntity(
            urn=urn,
            kind=kind,
            title=f"{target_cls.__name__} Interface Specification",
            purpose=docstring.split("\n")[0],
            module_path=target_cls.__module__,
            version=version,
            architecture_summary=f"Class introspection contract for {target_cls.__qualname__}",
            lifecycle_stage="PRODUCTION",
            interfaces=interfaces,
            verification_status=VerificationStatus.VERIFIED,
        )
