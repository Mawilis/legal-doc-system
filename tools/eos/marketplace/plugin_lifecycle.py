"""
===============================================================================
WILSY OS — FG220 UNIFIED PLUGIN LIFECYCLE & ORCHESTRATOR
===============================================================================

Epitome:
    High-level lifecycle manager for FG220 marketplace plugins. Orchestrates
    the complete operational transition flow: registration -> validation ->
    capability resolution -> sandbox loading -> active execution -> graceful disable.

Biblical Worth Billions:
    "Order my steps in thy word: and let not any iniquity have dominion over me."
    — Psalm 119:133

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/plugin_lifecycle.py
===============================================================================
"""

from typing import Dict, Any, Optional

from tools.eos.marketplace import logger
from tools.eos.marketplace.plugin_descriptor import PluginDescriptor, PluginState
from tools.eos.marketplace.plugin_registry import PluginRegistry
from tools.eos.marketplace.capability_resolver import CapabilityResolver
from tools.eos.marketplace.plugin_loader import PluginLoader
from tools.eos.marketplace.plugin_sandbox import PluginSandbox, SandboxResult


class LifecycleTransitionError(Exception):
    """Exception raised when an invalid lifecycle state transition or activation occurs."""
    pass


class PluginLifecycleManager:
    """
    Unified manager governing plugin state transitions, capability binding,
    and sandboxed execution entrypoints.
    """

    def __init__(
        self,
        registry: PluginRegistry,
        capability_resolver: CapabilityResolver,
        loader: Optional[PluginLoader] = None,
        sandbox: Optional[PluginSandbox] = None
    ) -> None:
        """
        Initializes lifecycle manager with system dependencies.

        Args:
            registry (PluginRegistry): System plugin registry.
            capability_resolver (CapabilityResolver): Platform capability broker.
            loader (Optional[PluginLoader]): Dynamic code loader.
            sandbox (Optional[PluginSandbox]): Execution sandbox.
        """
        self.registry = registry
        self.capability_resolver = capability_resolver
        self.loader = loader or PluginLoader()
        self.sandbox = sandbox or PluginSandbox()

    def activate_plugin(self, plugin_id: str) -> PluginDescriptor:
        """
        Activates an installed and verified plugin by resolving capabilities
        and loading its entrypoint module into runtime memory.

        Args:
            plugin_id (str): Unique plugin identifier.

        Returns:
            PluginDescriptor: Activated descriptor.

        Raises:
            LifecycleTransitionError: If activation preconditions fail.
        """
        logger.info(f"[LIFECYCLE] Initiating activation sequence for plugin '{plugin_id}'...")

        descriptor = self.registry.get(plugin_id)
        if not descriptor:
            raise LifecycleTransitionError(f"Activation failed: Plugin '{plugin_id}' not found in registry.")

        if descriptor.state not in (PluginState.VERIFIED, PluginState.DISABLED):
            raise LifecycleTransitionError(
                f"Cannot activate plugin '{plugin_id}' from state '{descriptor.state.value}'."
            )

        try:
            # 1. Resolve Required Capabilities
            self.capability_resolver.resolve_for_plugin(descriptor)

            # 2. Load Entrypoint Module via Dynamic Loader (Handles LOADING -> ACTIVE transition)
            module = self.loader.load_plugin(descriptor)

            logger.info(f"[LIFECYCLE-SUCCESS] Plugin '{plugin_id}' successfully activated.")
            return descriptor

        except Exception as err:
            error_msg = f"Failed to activate plugin '{plugin_id}': {str(err)}"
            logger.error(f"[LIFECYCLE-ERROR] {error_msg}")
            if descriptor.state != PluginState.ERROR:
                descriptor.transition_to(PluginState.ERROR, error_msg)
            raise LifecycleTransitionError(error_msg) from err

    def deactivate_plugin(self, plugin_id: str) -> PluginDescriptor:
        """
        Gracefully deactivates/disables an active plugin, unloading its module.

        Args:
            plugin_id (str): Unique plugin identifier.

        Returns:
            PluginDescriptor: Disabled descriptor.
        """
        logger.info(f"[LIFECYCLE] Deactivating plugin '{plugin_id}'...")

        descriptor = self.registry.get(plugin_id)
        if not descriptor:
            raise LifecycleTransitionError(f"Deactivation failed: Plugin '{plugin_id}' not found.")

        try:
            if self.loader.is_loaded(plugin_id):
                self.loader.unload_plugin(plugin_id, descriptor)

            if descriptor.state != PluginState.DISABLED:
                descriptor.transition_to(PluginState.DISABLED, "Gracefully deactivated by lifecycle manager")
            logger.info(f"[LIFECYCLE-SUCCESS] Plugin '{plugin_id}' transitioned to DISABLED.")
            return descriptor

        except Exception as err:
            error_msg = f"Error during plugin deactivation '{plugin_id}': {str(err)}"
            logger.error(f"[LIFECYCLE-ERROR] {error_msg}")
            raise LifecycleTransitionError(error_msg) from err

    def execute_plugin_method(
        self,
        plugin_id: str,
        method_name: str,
        *args: Any,
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> SandboxResult:
        """
        Invokes a method on an active plugin within the secure execution sandbox.

        Args:
            plugin_id (str): Target plugin identifier.
            method_name (str): Name of function/method inside the plugin module.
            timeout (Optional[float]): Execution timeout override.

        Returns:
            SandboxResult: Standardized execution output and telemetry.
        """
        descriptor = self.registry.get(plugin_id)
        if not descriptor:
            return SandboxResult(plugin_id=plugin_id, success=False, error=f"Plugin '{plugin_id}' not found.")

        if descriptor.state != PluginState.ACTIVE:
            return SandboxResult(
                plugin_id=plugin_id,
                success=False,
                error=f"Plugin '{plugin_id}' is not active (Current state: {descriptor.state.value})."
            )

        module = self.loader.get_module(plugin_id)
        if not module or not hasattr(module, method_name):
            return SandboxResult(
                plugin_id=plugin_id,
                success=False,
                error=f"Method '{method_name}' not found in plugin '{plugin_id}' entrypoint module."
            )

        target_callable = getattr(module, method_name)
        return self.sandbox.execute_in_sandbox(descriptor, target_callable, *args, timeout=timeout, **kwargs)
