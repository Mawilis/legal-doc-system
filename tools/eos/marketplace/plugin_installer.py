"""
===============================================================================
WILSY OS — FG220 DETERMINISTIC PLUGIN INSTALLER PIPELINE
===============================================================================

Epitome:
    Multi-stage deterministic installation engine for FG220 marketplace plugins.
    Orchestrates the entire onboarding lifecycle: manifest schema validation,
    ABI/version checks, cryptographic signature verification, directory extraction,
    sandbox isolation checks, and atomic registry registration.

Biblical Worth Billions:
    "Let all things be done decently and in order."
    — 1 Corinthians 14:40

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/plugin_installer.py
===============================================================================
"""

import os
import shutil
import tarfile
import zipfile
from typing import Dict, Any, Optional, Final

from tools.eos.marketplace import logger
from tools.eos.marketplace.manifest import PluginManifest, ManifestValidationError
from tools.eos.marketplace.plugin_descriptor import PluginDescriptor, PluginState
from tools.eos.marketplace.plugin_registry import PluginRegistry, PluginAlreadyExistsError
from tools.eos.marketplace.plugin_validator import PluginValidator
from tools.eos.marketplace.plugin_signature import PluginSignatureVerifier, SignatureVerificationError


class InstallationError(Exception):
    """Custom exception raised when any stage of the installation pipeline fails."""
    pass


class PluginInstaller:
    """
    Deterministic installation pipeline manager for Wilsy OS plugins.
    """

    def __init__(
        self,
        registry: PluginRegistry,
        validator: Optional[PluginValidator] = None,
        signature_verifier: Optional[PluginSignatureVerifier] = None,
        install_root_dir: Optional[str] = None
    ) -> None:
        """
        Initializes installer dependencies and target installation directory.

        Args:
            registry (PluginRegistry): System plugin registry instance.
            validator (Optional[PluginValidator]): Pre-flight validator instance.
            signature_verifier (Optional[PluginSignatureVerifier]): Cryptographic signature engine.
            install_root_dir (Optional[str]): Root directory where plugin packages are installed.
        """
        self.registry = registry
        self.validator = validator or PluginValidator()
        self.signature_verifier = signature_verifier or PluginSignatureVerifier()
        self.install_root_dir = install_root_dir or os.path.join(
            os.path.dirname(__file__), "installed_plugins"
        )
        os.makedirs(self.install_root_dir, exist_ok=True)

    def install_from_directory(self, source_dir: str, manifest_dict: Dict[str, Any]) -> PluginDescriptor:
        """
        Installs a plugin directly from a raw source directory using a provided manifest dictionary.

        Pipeline Execution Stages:
            1. Manifest Schema Validation
            2. Pre-flight Compatibility & ABI Verification
            3. Directory Cryptographic Signature Check
            4. Destination Directory Provisioning & Artifact Copy
            5. Descriptor Construction & Lifecycle Registration

        Args:
            source_dir (str): Path to source directory containing plugin code.
            manifest_dict (Dict[str, Any]): Raw manifest payload.

        Returns:
            PluginDescriptor: Fully registered and verified plugin descriptor.

        Raises:
            InstallationError: If any pipeline stage fails.
        """
        logger.info(f"[INSTALLER] Commencing plugin installation pipeline from: '{source_dir}'")

        if not os.path.isdir(source_dir):
            raise InstallationError(f"Source path is not a valid directory: '{source_dir}'")

        # Stage 1: Manifest Parsing
        try:
            manifest = PluginManifest.from_dict(manifest_dict)
        except ManifestValidationError as err:
            raise InstallationError(f"Stage 1 [Manifest Validation] Failed: {str(err)}") from err

        plugin_id = manifest.id

        # Check for duplication
        if self.registry.has(plugin_id):
            raise InstallationError(
                f"Stage 1 [Duplicate Check] Failed: Plugin '{plugin_id}' is already installed."
            )

        # Provision Target Path
        target_install_dir = os.path.join(self.install_root_dir, plugin_id.replace(".", "_"))

        try:
            # Stage 2: Copy artifacts to staging install directory
            if os.path.exists(target_install_dir):
                shutil.rmtree(target_install_dir)
            shutil.copytree(source_dir, target_install_dir)

            descriptor = PluginDescriptor(
                manifest=manifest,
                install_path=target_install_dir,
                entrypoint="main.py"
            )

            # Stage 3: Pre-flight Validation
            val_report = self.validator.validate_descriptor(descriptor)
            if not val_report.is_valid:
                raise InstallationError(
                    f"Stage 3 [Pre-flight Validation] Failed with errors: {val_report.errors}"
                )
            descriptor.transition_to(PluginState.VERIFIED, "Pre-flight validation passed")

            # Stage 4: Signature Verification
            self.signature_verifier.verify_signature(manifest, target_install_dir)

            # Stage 5: Register in Central Registry
            self.registry.register(descriptor)

            logger.info(
                f"[INSTALLER-SUCCESS] Plugin '{plugin_id}' v{manifest.version} "
                f"installed successfully at '{target_install_dir}'."
            )
            return descriptor

        except Exception as err:
            logger.error(f"[INSTALLER-ROLLBACK] Installation failed for '{plugin_id}'. Cleaning up target directory.")
            if os.path.exists(target_install_dir):
                shutil.rmtree(target_install_dir, ignore_errors=True)
            raise InstallationError(f"Installation pipeline aborted: {str(err)}") from err
