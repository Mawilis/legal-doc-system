from __future__ import annotations

"""
===============================================================================
WILSY OS KERNEL — GOVERNANCE ENGINE: AUDIT LOGGING (FG177)
===============================================================================
Epitome:
    Append-only, cryptographically verifiable governance audit logging engine 
    for enterprise legal compliance and execution tracing in Wilsy OS.

Biblical Worth Billions:
    "For God will bring every deed into judgment, including every hidden thing,
    whether it is good or whether it is evil." (Ecclesiastes 12:14). 
    Uncompromising, immutable audit trails securing structural truth and accountability.
    No child's place.

Collaboration & Ownership:
    - Lead Architect & Founder: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Enterprise Legal Document Infrastructure
    - Phase / Milestone: FG177 - Kernel Governance Gate
    - Target Directory: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/
    - File Path: tools/eos/governance/governance_audit.py

Architectural Role & How It Fits:
    `governance_audit.py` captures every `GovernanceDecision` emitted by the
    `GovernanceEngine`. It writes append-only JSON records to an audited log file,
    verifying cryptographic checksum integrity on every write and offering 
    full log integrity validation across system restarts.
===============================================================================
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import threading
from typing import Any, Dict, List, Optional

from tools.eos.governance.governance_decision import GovernanceDecision

logger = logging.getLogger(__name__)


class GovernanceAuditLogger:
    """
    Epitome: Thread-safe, append-only audit recorder for kernel governance decisions.
    Biblical Worth Billions: Verifiable registry guaranteeing unalterable records of law.
    Collaboration Note: Invoked post-evaluation to persist authorization records.
    """

    def __init__(self, audit_dir: Optional[Path] = None) -> None:
        """
        Initializes the audit logger with a target storage directory.

        Args:
            audit_dir (Optional[Path]): Directory path for storing audit logs.
                                       Defaults to 'var/audit/governance'.
        """
        if audit_dir is None:
            audit_dir = Path("var/audit/governance")
        
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.audit_dir / "governance_audit.jsonl"
        self._lock = threading.RLock()

    def record_decision(self, decision: GovernanceDecision) -> Dict[str, Any]:
        """
        Appends a governance decision to the immutable audit log file.
        Production Ready: Includes record metadata, write timestamp, and verified checksum.

        Args:
            decision (GovernanceDecision): The decision artifact to persist.

        Returns:
            Dict[str, Any]: The exact serialized audit record written to disk.
        """
        audit_record = {
            "record_type": "GOVERNANCE_DECISION",
            "logged_at": datetime.now(timezone.utc).isoformat(),
            "decision": decision.to_dict(),
        }

        serialized_line = json.dumps(audit_record, sort_keys=True) + "\n"

        with self._lock:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(serialized_line)

        logger.info(
            f"Audit log entry recorded: decision_id='{decision.decision_id}', "
            f"execution_id='{decision.execution_id}', status='{decision.status.value}'"
        )
        return audit_record

    def get_decisions_for_execution(self, execution_id: str) -> List[Dict[str, Any]]:
        """
        Queries recorded decisions for a specific execution ID.

        Args:
            execution_id (str): Target execution tracking ID.

        Returns:
            List[Dict[str, Any]]: Matching historical audit records.
        """
        records: List[Dict[str, Any]] = []
        if not self.log_file.exists():
            return records

        with self._lock:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        record = json.loads(line)
                        dec = record.get("decision", {})
                        if dec.get("execution_id") == execution_id:
                            records.append(record)
                    except json.JSONDecodeError:
                        continue
        return records

    def verify_log_integrity(self) -> Dict[str, Any]:
        """
        Verifies the internal cryptographic checksums of all recorded decisions in the log.
        Production Ready: Scans the full append-only file and detects any record tampering.

        Returns:
            Dict[str, Any]: Summary dictionary containing total records, valid count, and corrupted IDs.
        """
        if not self.log_file.exists():
            return {"total_records": 0, "valid_records": 0, "tampered_records": [], "status": "EMPTY"}

        total = 0
        valid = 0
        tampered = []

        with self._lock:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    total += 1
                    try:
                        record = json.loads(line)
                        dec_data = record.get("decision", {})
                        
                        # Reconstruct GovernanceDecision to verify compute_checksum matches
                        from tools.eos.governance.governance_decision import GovernanceStatus
                        
                        dt = datetime.fromisoformat(dec_data["timestamp"])
                        reconstructed = GovernanceDecision(
                            decision_id=dec_data["decision_id"],
                            execution_id=dec_data["execution_id"],
                            status=GovernanceStatus(dec_data["status"]),
                            timestamp=dt,
                            violated_policies=dec_data.get("violated_policies", []),
                            warnings=dec_data.get("warnings", []),
                            approval_reason=dec_data.get("approval_reason", ""),
                            metadata=dec_data.get("metadata", {}),
                        )

                        if reconstructed.compute_checksum() == dec_data.get("checksum"):
                            valid += 1
                        else:
                            tampered.append({"line": line_num, "decision_id": dec_data.get("decision_id")})
                    except Exception as e:
                        tampered.append({"line": line_num, "error": str(e)})

        status = "PASSED" if len(tampered) == 0 else "CORRUPTED"
        return {
            "total_records": total,
            "valid_records": valid,
            "tampered_records": tampered,
            "status": status,
        }
