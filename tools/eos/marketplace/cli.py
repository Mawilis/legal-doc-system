"""
===============================================================================
WILSY OS — FG220 MARKETPLACE COMMAND LINE INTERFACE (CLI)
===============================================================================

Epitome:
    Command-line management interface for Wilsy OS marketplace plugins.
    Provides administrative commands for installation, uninstallation, updates,
    lifecycle activation/deactivation, and plugin listing.

Biblical Worth Billions:
    "Commit thy works unto the Lord, and thy thoughts shall be established."
    — Proverbs 16:3

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/cli.py
===============================================================================
"""

import sys
import json
import argparse
from typing import List, Optional

from tools.eos.marketplace.marketplace_api import MarketplaceAPI
from tools.eos.marketplace import logger


def create_parser() -> argparse.ArgumentParser:
    """Creates and configures the argument parser for Wilsy Marketplace CLI."""
    parser = argparse.ArgumentParser(
        description="Wilsy OS FG220 Plugin Marketplace CLI",
        prog="wilsy-market"
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Marketplace command")

    # List command
    subparsers.add_parser("list", help="List all registered plugins")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install a plugin package")
    install_parser.add_argument("--source", required=True, help="Path to plugin source directory")
    install_parser.add_argument("--manifest", required=True, help="Path to plugin manifest JSON file")

    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a plugin by ID")
    uninstall_parser.add_argument("--id", required=True, help="Plugin identifier")

    # Activate command
    activate_parser = subparsers.add_parser("activate", help="Activate an installed plugin")
    activate_parser.add_argument("--id", required=True, help="Plugin identifier")

    # Deactivate command
    deactivate_parser = subparsers.add_parser("deactivate", help="Deactivate an active plugin")
    deactivate_parser.add_argument("--id", required=True, help="Plugin identifier")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """
    CLI entrypoint execution handler.

    Args:
        argv (Optional[List[str]]): Command-line arguments.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    api = MarketplaceAPI()

    try:
        if args.command == "list":
            plugins = api.list_plugins()
            print(json.dumps(plugins, indent=2))
            return 0

        elif args.command == "install":
            with open(args.manifest, "r", encoding="utf-8") as f:
                manifest_dict = json.load(f)
            result = api.install_plugin(args.source, manifest_dict)
            print(json.dumps(result, indent=2))
            return 0 if result.get("success") else 1

        elif args.command == "uninstall":
            result = api.uninstall_plugin(args.id)
            print(json.dumps(result, indent=2))
            return 0 if result.get("success") else 1

        elif args.command == "activate":
            result = api.activate_plugin(args.id)
            print(json.dumps(result, indent=2))
            return 0 if result.get("success") else 1

        elif args.command == "deactivate":
            result = api.deactivate_plugin(args.id)
            print(json.dumps(result, indent=2))
            return 0 if result.get("success") else 1

        else:
            parser.print_help()
            return 1

    except Exception as err:
        logger.error(f"[CLI-ERROR] Unhandled exception during execution: {str(err)}")
        print(json.dumps({"success": False, "error": str(err)}, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
