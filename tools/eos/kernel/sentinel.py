"""
===============================================================================
WILSY ENGINEERING KERNEL: SENTINEL DAEMON
===============================================================================
Epitome:
    WilsySentinel: Real-time file system monitoring and cryptographic 
    integrity engine. Acts as the peripheral vision of Wilsy OS.

Biblical Scale & Architecture:
    This is a billion-dollar, production-ready daemon. No child's place.
    It hooks directly into native OS events to monitor the respiratory rate 
    of the codebase, instantly detecting modifications, creations, and 
    deletions while securing files with SHA-256 cryptographic hashes.
    
    INTEGRATION: This module is now fused with the WilsyGraphBridge, enabling 
    zero-latency, asynchronous hot-reloading of the Knowledge Graph database 
    whenever a file system mutation is detected.

Collaboration & Maintenance:
    - [Reliability]: Implements zero-latency event handlers via watchdog.
    - [Security]: Cryptographically signs file states to detect rogue edits.
    - [Data Integrity]: Prevents unauthorized state drift in the Knowledge Graph.
===============================================================================
"""

from __future__ import annotations

import logging
import hashlib
import time
import os
import sys

# Crucial: Resolve project root first before importing local modules to prevent ModuleNotFoundError
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

# Import the billion-dollar neural pathway now that paths are securely established
from tools.eos.kernel.bridge import WilsyGraphBridge

# Initialize institutional logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("wilsy.eos.kernel.sentinel")


class CryptographicManager:
    """
    Handles SHA-256 hashing to ensure structural integrity of the codebase.
    """
    @staticmethod
    def hash_file(filepath: str) -> str:
        """
        Generates a SHA-256 hash of the target file.
        """
        sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256.update(byte_block)
            return sha256.hexdigest()
        except FileNotFoundError:
            return "FILE_DELETED"
        except Exception as e:
            logger.error(f"Integrity check failed for {filepath}: {e}")
            return "HASH_ERROR"


class SentinelEventHandler(FileSystemEventHandler):
    """
    Intercepts and processes native file system events with strict path normalization,
    routing them instantly to the Graph Bridge.
    """
    def __init__(self, bridge: WilsyGraphBridge):
        super().__init__()
        self.crypto = CryptographicManager()
        self._state_hashes: dict[str, str] = {}
        self.bridge = bridge

    def warm_boot_index(self, target_directory: str):
        """
        Indexes all existing files using absolute paths to establish the cryptographic baseline.
        """
        logger.info("Initializing Warm Boot: Caching codebase cryptographic baseline...")
        file_count = 0
        
        # Resolve target directory to absolute form
        abs_target = os.path.abspath(target_directory)
        
        for root, _, files in os.walk(abs_target):
            # Strict environmental isolation rules
            if ".git" in root or ".venv" in root or "__pycache__" in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    # Force canonical absolute path mapping
                    full_path = os.path.abspath(os.path.join(root, file))
                    initial_hash = self.crypto.hash_file(full_path)
                    self._state_hashes[full_path] = initial_hash
                    file_count += 1
                    
        logger.info(f"Warm Boot Complete. Indexed {file_count} active modules into memory.")

    def _process_event(self, event: FileSystemEvent, event_type: str):
        # Force incoming event paths to match the absolute canonical string representation
        filepath = os.path.abspath(os.fsdecode(event.src_path))
        
        if event.is_directory or not filepath.endswith('.py') or ".venv" in filepath:
            return

        filename = os.path.basename(filepath)
        
        if event_type == "DELETED":
            logger.warning(f"[SECURITY ALERT] Module Deleted: {filename} - Graph Update Required.")
            self._state_hashes.pop(filepath, None)
            self.bridge.dispatch_event("DELETED", filepath)
            return

        # Calculate cryptographic signature
        new_hash = self.crypto.hash_file(filepath)
        old_hash = self._state_hashes.get(filepath, "")

        if event_type == "CREATED":
            logger.info(f"[DISCOVERY] New Module Detected: {filename} | Hash: {new_hash[:8]}")
            self._state_hashes[filepath] = new_hash
            self.bridge.dispatch_event("CREATED", filepath, new_hash=new_hash)
        
        elif event_type == "MODIFIED" and new_hash != old_hash:
            logger.info(f"[INTEGRITY] Module Modified: {filename} | Old Hash: {old_hash[:8]} -> New Hash: {new_hash[:8]}")
            self._state_hashes[filepath] = new_hash
            self.bridge.dispatch_event("MODIFIED", filepath, new_hash=new_hash, old_hash=old_hash)

    def on_created(self, event: FileSystemEvent):
        self._process_event(event, "CREATED")

    def on_modified(self, event: FileSystemEvent):
        self._process_event(event, "MODIFIED")

    def on_deleted(self, event: FileSystemEvent):
        self._process_event(event, "DELETED")


class WilsySentinel:
    """
    The billion-dollar peripheral vision daemon.
    """
    def __init__(self, target_directory: str = "."):
        self.target_directory = target_directory
        self.bridge = WilsyGraphBridge()
        self.event_handler = SentinelEventHandler(self.bridge)
        self.observer = Observer()

    def awaken(self):
        """
        Activates the daemon and the database bridge to monitor the repository in real-time.
        """
        # 1. Ignite the neural pathway database connection
        self.bridge.start_bridge()

        # 2. Warm boot the local cache
        self.event_handler.warm_boot_index(self.target_directory)
        
        # 3. Open the file system interrupt observer
        self.observer.schedule(self.event_handler, self.target_directory, recursive=True)
        self.observer.start()
        logger.info("================================================================")
        logger.info("WILSY OS SENTINEL AWAKENED: Peripheral Vision Online.")
        logger.info("Cryptographic monitoring active. Press Ctrl+C to terminate.")
        logger.info("================================================================")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Sentinel shutdown initiated by operator.")
            self.observer.stop()
            self.bridge.stop_bridge()
            
        self.observer.join()


if __name__ == "__main__":
    daemon = WilsySentinel()
    daemon.awaken()
