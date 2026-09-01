"""
===============================================================================
WILSY OS — SOVEREIGN QUOTE ENGINE (GOVERNANCE GUARD)
===============================================================================
Epitome:
    Provides dynamic, enterprise-grade architectural quotes authored by Founder 
    & Chief Architect Wilson Khanyezi. Replaces hardcoded static verses with 
    investor-grade institutional statements engineered for the 0.01% standard.

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/governance/sovereign_quotes.py
===============================================================================
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple


class SovereignQuoteEngine:
    """Central repository and dynamic generator for Wilson Khanyezi's OS quotes."""

    AUTHOR: str = "Wilson Khanyezi"
    TITLE: str = "Founder & Chief Architect, Wilsy OS"

    QUOTES: Dict[str, List[str]] = {
        "ARCHITECTURE": [
            "We do not build software that merely functions; we engineer sovereign architectures that command deterministic trust.",
            "In the top 0.01% of operating systems, human error is not mitigated—it is architecturally rendered impossible.",
            "An enterprise operating system without mathematical attestation is just an illusion of stability. Wilsy OS makes execution immutable.",
            "Architectural elegance is not measured by complexity, but by the absolute absence of unverified operational state.",
            "A billion-dollar codebase is built block by block, assertion by assertion, until failure becomes mathematically impossible."
        ],
        "AUTONOMY": [
            "Autonomous intelligence without deterministic verification is chaos; within Wilsy OS, it is sovereign operational precision.",
            "True autonomy requires no human babysitter. An execution engine must prove its own work before committing state.",
            "Delegating decision-making to software is an enterprise privilege reserved only for platforms with non-repudiable proof chains.",
            "Every autonomous step must leave behind a cryptographic trail that withstands institutional audit."
        ],
        "VERIFICATION": [
            "Verification is not an afterthought of execution; in Wilsy OS, an execution that cannot prove itself never happened.",
            "Zero trust inside the kernel is the prerequisite for unconditional performance at the enterprise edge.",
            "If an action fails invariant verification, it must be halted, quarantined, and erased before it ever touches production memory.",
            "We do not ask investors or clients to trust our logic. We provide the cryptographic proofs so they can verify it."
        ],
        "INVESTOR_STANDARD": [
            "Capital flows to platforms that eliminate operational uncertainty. Wilsy OS is engineered to be the ultimate safe harbor.",
            "Every line of code in Wilsy OS is an institutional asset designed to yield compound enterprise value for decades.",
            "The distance between standard SaaS and Wilsy OS is the difference between temporary software and permanent infrastructure.",
            "We build software worthy of governing nation-state workloads and high-stakes financial telemetry."
        ]
    }

    @classmethod
    def get_quote(cls, category: Optional[str] = None, index: Optional[int] = None) -> str:
        """Retrieves a quote by category/index or returns a default high-impact quote."""
        if category and category.upper() in cls.QUOTES:
            category_quotes = cls.QUOTES[category.upper()]
            if index is not None and 0 <= index < len(category_quotes):
                return category_quotes[index]
            return random.choice(category_quotes)

        all_quotes = [q for quotes in cls.QUOTES.values() for q in quotes]
        if index is not None and 0 <= index < len(all_quotes):
            return all_quotes[index]
        return random.choice(all_quotes)

    @classmethod
    def get_formatted_attribution(cls) -> str:
        """Returns the standardized executive signature for reports."""
        return f"{cls.AUTHOR}, {cls.TITLE}"


def get_sovereign_quote(category: Optional[str] = None) -> Tuple[str, str]:
    """Helper function for external scripts to fetch a quote and its attribution."""
    quote = SovereignQuoteEngine.get_quote(category)
    attribution = SovereignQuoteEngine.get_formatted_attribution()
    return quote, attribution
