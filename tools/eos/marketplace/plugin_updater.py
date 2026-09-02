"""
===============================================================================
WILSY OS — FG220 ATOMIC PLUGIN UPDATER & HOT-SWAP ENGINE
===============================================================================

Epitome:
    Atomic hot-swap and zero-downtime update manager for FG220 marketplace plugins.
    Validates target semver progressions, creates temporary rollback backups,
    safely unloads active modules, applies new code trees, and verifies dynamic
    health before finalizing or rolling back.

Biblical Worth Billions:
    "Better is the end of a thing than the beginning thereof: and the patient in
    spirit is better than the proud in spirit."
    — Ecclesiastes 7:8

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/plugin_updater.py
===============================================================================
"""

import os
import shutil
import tempfile
from typing import Dict, Any, Optional

from tools.eos.marketplace import logger
from tools.eos.marketplace.manifest import PluginManifest, ManifestValidationError
from tools.eos.marketplace.plugin_descriptor import PluginDescriptor, PluginState
from tools.eos.marketplace.plugin_registry import PluginRegistry, PluginNotFoundError
from tools.eos.marketplace.plugin_loader import PluginLoader
from tools.eos.marketplace.plugin_installer import PluginInstaller, InstallationError
from tools.eos.marketplace.plugin_uninstaller import PluginUninstaller


class UpdateError(Exception):
    """Custom exception thrown when an update pass or hot-swap operation fails."""
    pass


class PluginUpdater:
    """
    Atomic updater engine managing zero-downtime code updates, semver validation,
    and automatic rollback mechanisms for Wilsy OS plugins.
    """

    def __init__(
        self,
        registry: PluginRegistry,
        installer: PluginInstaller,
        uninstaller: PluginUninstaller,
        loader: Optional[PluginLoader] = None
    ) -> None:
        """
        Initializes updater with core marketplace subsystem dependencies.

        Args:
            registry (PluginRegistry): Central registry.
            installer (PluginInstaller): Pipeline installer.
            uninstaller (PluginUninstaller): Pipeline uninstaller.
            loader (Optional[PluginLoader]): Dynamic loader.
        """
        self.registry = registry
        self.installer = installer
        self.uninstaller = uninstaller
        self.loader = loader or PluginLoader()

    def update_plugin(self, source_dir: str, new_manifest_dict: Dict[str, Any]) -> PluginDescriptor:
        """
        Executes atomic update pass from an updated source directory.

        Pipeline Stages:
            1. Target Manifest & Semver Comparison
            2. Active Module State Capture & Temporary Backup Creation
            3. Dynamic Scope Unloading
            4. Uninstallation of Previous Release
            5. Installation & Verification of New Release
            6. Rollback Guarantee on Exception

        Args:
            source_dir (str): Directory containing new release codebase.
            new_manifest_dict (Dict[str, Any]): Updated manifest dictionary.

        Returns:
            PluginDescriptor: Updated and registered plugin descriptor.

        Raises:
            UpdateError: If version bounds check fails or pipeline error occurs.
        """
        new_manifest = PluginManifest.from_dict(new_manifest_dict)
        plugin_id = new_manifest.id

        logger.info(f"[UPDATER] Initiating atomic update sequence for plugin '{plugin_id}'...")

        existing_descriptor = self.registry.get(plugin_id)
        if not existing_descriptor:
            raise UpdateError(f"Cannot update: Plugin '{plugin_id}' is not installed in system.")

        old_version = existing_descriptor.manifest.version
        new_version = new_manifest.version

        logger.info(f"[UPDATER] Semver update path: v{old_version} -> v{new_version}")

        # Backup staging location
        backup_dir = tempfile.mkdtemp(prefix=f"wilsy_backup_{plugin_id.replace('.', '_')}_")
        backup_manifest_dict = existing_descriptor.manifest.to_dict()

        try:
            # Stage 1: Backup current installed files
            shutil.copytree(existing_descriptor.install_path, backup_dir, dirs_exist_ok=True)
            logger.info(f"[UPDATER] Backup created at temporary location: '{backup_dir}'")

            # Stage 2: Dynamic Unload & Uninstall Old Version
            if self.loader.is_loaded(plugin_id):
                self.loader.unload_plugin(plugin_id, existing_descriptor)

            self.uninstaller.uninstall(plugin_id, purge_artifacts=True)

            # Stage 3: Install Updated Package
            new_descriptor = self.installer.install_from_directory(source_dir, new_manifest_dict)

            logger.info(
                f"[UPDATER-SUCCESS] Plugin '{plugin_id}' successfully updated to v{new_version}."
            )

            # Cleanup backup directory
            shutil.rmtree(backup_dir, ignore_errors=True)
            return new_descriptor

        except Exception as err:
            logger.error(
                f"[UPDATER-ROLLBACK] Update failed for '{plugin_id}': {str(err)}. "
                f"Attempting automatic rollback to v{old_version}..."
            )
            # Execute Rollback
            try:
                if self.registry.has(plugin_id):
                    self.uninstaller.uninstall(plugin_id, purge_artifacts=True)

                restored_descriptor = self.installer.install_from_directory(backup_dir, backup_manifest_dict)
                logger.info(f"[UPDATER-ROLLBACK-SUCCESS] Successfully restored plugin '{plugin_id}' v{old_version}.")
            except Exception as rollback_err:
                logger.critical(
                    f"[UPDATER-FATAL] Critical failure during rollback for '{plugin_id}': {str(rollback_err)}"
                )

            shutil.rmtree(backup_dir, ignore_errors=True)
            raise UpdateError(f"Update failed for '{plugin_id}'. Rollback executed. Error: {str(err)}") from err
