"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    FG166 Plugin SDK Integration & Verification Test.
    Validates plugin base contract, manifest parsing, dynamic loading,
    and automatic execution for specialized engines.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready test runner. Zero child's place.
    Colossians 3:23 - "Whatever you do, work heartily, as for the Lord and not for men..."

Collaboration & Maintenance:
    - [Test Harness]: End-to-end SDK verification and sandbox execution test.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

import json
import os
import shutil
import sys
from pathlib import Path

# Ensure sdk directory is registered in sys.path for direct script execution
sdk_dir = Path(__file__).parent.resolve()
if str(sdk_dir) not in sys.path:
    sys.path.insert(0, str(sdk_dir))

from plugin import WilsyPlugin  # type: ignore[import]
from plugin_loader import PluginLoader  # type: ignore[import]
from plugin_manifest import PluginManifest  # type: ignore[import]


# Mock Sample Security Engine Plugin for Testing
SAMPLE_PLUGIN_CODE = '''
from plugin import WilsyPlugin

class SecurityEnginePlugin(WilsyPlugin):
    def __init__(self):
        super().__init__(plugin_id="eos-security-engine", version="1.0.0")

    def initialize(self, context=None) -> bool:
        self._initialized = True
        return True

    def execute(self, payload: dict) -> dict:
        target = payload.get("target", "unknown")
        return {
            "status": "SECURE",
            "target": target,
            "comments": "Security engine scanned target with institutional rigor."
        }

    def shutdown(self) -> bool:
        self._initialized = False
        return True
'''


def test_plugin_sdk() -> None:
    print("===============================================================================")
    print("WILSY OS KERNEL - FG166 PLUGIN SDK & ENGINE VERIFICATION")
    print("===============================================================================")

    plugins_dir = Path("/Users/wilsonkhanyezi/legal-doc-system/tools/eos/sdk/test_plugins")
    plugins_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write sample plugin and manifest files
    plugin_file = plugins_dir / "security_engine.py"
    manifest_file = plugins_dir / "security_engine.json"

    plugin_file.write_text(SAMPLE_PLUGIN_CODE.strip(), encoding="utf-8")
    
    manifest_data = {
        "plugin_id": "eos-security-engine",
        "name": "Security Engine",
        "version": "1.0.0",
        "author": "Wilson Khanyezi",
        "description": "Institutional security compliance engine.",
        "entry_point": "security_engine.py",
        "permissions": ["read_filesystem", "execute_audit"]
    }
    manifest_file.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    # 2. Test PluginManifest parsing
    manifest = PluginManifest.from_file(manifest_file)
    print(f"  -> Parsed manifest ID: {manifest.plugin_id} (Expected: eos-security-engine)")
    assert manifest.plugin_id == "eos-security-engine"
    assert "read_filesystem" in manifest.permissions

    # 3. Test PluginLoader discovery and dynamic loading
    loader = PluginLoader(plugins_dir=plugins_dir)
    discovered = loader.discover_plugins()
    print(f"  -> Discovered plugins count: {len(discovered)} (Expected: 1)")
    assert len(discovered) == 1

    loaded_plugin = loader.load_plugin(plugin_file, context={"mode": "strict"})
    print(f"  -> Plugin loaded successfully? {loaded_plugin is not None}")
    assert loaded_plugin is not None
    assert loaded_plugin.plugin_id == "eos-security-engine"

    # 4. Test Plugin execution
    exec_result = loaded_plugin.execute({"target": "workspace_root"})
    print(f"  -> Plugin execution status: {exec_result['status']} (Expected: SECURE)")
    assert exec_result["status"] == "SECURE"

    # Clean up test directories safely (handling __pycache__ and residual files)
    shutil.rmtree(plugins_dir, ignore_errors=True)

    print("===============================================================================")
    print("FG166 PLUGIN SDK & ENGINES VERIFIED SUCCESSFULLY.")
    print("===============================================================================")


if __name__ == "__main__":
    test_plugin_sdk()
