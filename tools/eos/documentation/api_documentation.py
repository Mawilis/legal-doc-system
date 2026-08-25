"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE
FILE: tools/eos/documentation/api_documentation.py
===============================================================================
Epitome:
    Automated REST, FastAPI, and OpenAPI documentation generator for Wilsy OS.
    Parses API endpoint definitions, request/response schemas, path parameters,
    and authentication guardrails into standardized DocumentationEntity
    contracts and OpenAPI 3.0.3 specifications.

Biblical Worth Billions:
    "Let all things be done decently and in order." — 1 Corinthians 14:40

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/documentation/api_documentation.py
===============================================================================
"""

from typing import Dict, List, Any, Optional
from tools.eos.documentation.documentation_contract import (
    DocumentationEntity,
    EntityKind,
    InterfaceSpec,
    VerificationStatus,
)


class APIDocumentationGenerator:
    """
    Specialized documentation builder for Wilsy OS REST & HTTP API endpoints.
    Generates both internal DocumentationEntity instances and external OpenAPI specs.
    """

    @staticmethod
    def generate_endpoint_entity(
        urn: str,
        route_path: str,
        http_method: str,
        summary: str,
        description: str,
        parameters: Dict[str, str],
        response_schema: Dict[str, Any],
        auth_required: bool = True,
        version: str = "2.0.0",
    ) -> DocumentationEntity:
        """
        Constructs a DocumentationEntity specifically representing an HTTP API endpoint contract.

        Args:
            urn: Target unique documentation URN.
            route_path: Endpoint path string (e.g. '/api/v1/health').
            http_method: HTTP verb (GET, POST, PUT, DELETE, etc.).
            summary: Short endpoint purpose.
            description: Detailed technical endpoint description.
            parameters: Key-value dict of parameter names and type descriptions.
            response_schema: Expected response body JSON schema representation.
            auth_required: Flag indicating if sovereign authentication token is enforced.
            version: Target version string.

        Returns:
            Validated DocumentationEntity contract instance.
        """
        interface = InterfaceSpec(
            name=f"{http_method.upper()} {route_path}",
            description=description,
            parameters=parameters,
            return_type=str(response_schema.get("title", "JSONResponse")),
            is_async=True,
        )

        metadata = {
            "route_path": route_path,
            "http_method": http_method.upper(),
            "auth_required": auth_required,
            "response_schema": response_schema,
        }

        return DocumentationEntity(
            urn=urn,
            kind=EntityKind.API,
            title=f"API Endpoint: {http_method.upper()} {route_path}",
            purpose=summary,
            module_path=route_path,
            version=version,
            architecture_summary=f"HTTP API Route contract for {route_path}",
            lifecycle_stage="PRODUCTION",
            interfaces=[interface],
            metadata=metadata,
            verification_status=VerificationStatus.VERIFIED,
        )

    @staticmethod
    def generate_openapi_spec(
        title: str,
        version: str,
        entities: List[DocumentationEntity],
    ) -> Dict[str, Any]:
        """
        Aggregates API DocumentationEntity contracts into a compliant OpenAPI 3.0.3 specification dict.

        Args:
            title: API documentation title.
            version: API specification version.
            entities: List of DocumentationEntity instances (filters kind==EntityKind.API).

        Returns:
            Dictionary matching standard OpenAPI 3.0.3 structure.
        """
        paths: Dict[str, Dict[str, Any]] = {}

        for entity in entities:
            if entity.kind != EntityKind.API:
                continue

            meta = entity.metadata
            route = meta.get("route_path", entity.module_path)
            method = meta.get("http_method", "GET").lower()

            if route not in paths:
                paths[route] = {}

            paths[route][method] = {
                "summary": entity.purpose,
                "description": entity.architecture_summary,
                "operationId": entity.urn.replace(":", "_").replace("-", "_"),
                "responses": {
                    "200": {
                        "description": "Successful execution",
                        "content": {
                            "application/json": {
                                "schema": meta.get("response_schema", {})
                            }
                        },
                    }
                },
            }

        return {
            "openapi": "3.0.3",
            "info": {
                "title": title,
                "version": version,
                "description": "Wilsy OS Self-Documenting Sovereign API Catalog",
            },
            "paths": paths,
        }
