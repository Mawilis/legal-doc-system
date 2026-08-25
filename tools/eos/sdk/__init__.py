"""
===============================================================================
WILSY ENGINEERING KERNEL - PLUGIN SDK (FG166)
===============================================================================
"""

import sys
from pathlib import Path

sdk_dir = Path(__file__).parent.resolve()
if str(sdk_dir) not in sys.path:
    sys.path.insert(0, str(sdk_dir))

from plugin import WilsyPlugin  # type: ignore[import]
from plugin_loader import PluginLoader  # type: ignore[import]
from plugin_manifest import PluginManifest  # type: ignore[import]

__all__ = ["WilsyPlugin", "PluginLoader", "PluginManifest"]
