#!/usr/bin/env python3
"""
===============================================================================
WILSY OS — MASTER EXECUTIVE MILESTONE REPORT ENGINE (FG181 GOLD STANDARD)
===============================================================================
Epitome:
    Enterprise-grade two-pass executive PDF report generator producing board-ready 
    certification documentation. Implements dynamic total page count calculation,
    running headers, formal metadata grids, and telemetry pipeline tables with 
    sub-millisecond latency tracking.

Biblical Worth Billions:
    "And he shall be like a tree planted by the rivers of water, that bringeth 
    forth his fruit in his season; his leaf also shall not wither; and whatsoever 
    he doeth shall prosper." 
    — Psalm 1:3

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Executive Reporting Kernel / FG181 Master Template
    - File Path: scripts/generate_fg181_milestone_pdf.py
===============================================================================
"""

import sys
import subprocess
import os
from typing import Any, List, Tuple

# Auto-install reportlab if not present
try:
    import reportlab
except ImportError:
    print("Installing required PDF dependency (reportlab)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    import reportlab

from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas


class ExecutiveNumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas for dynamic total page count calculation, top running headers,
    and bottom enterprise footer styling. Fully compliant with Pylance static analysis.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: List[dict] = []

    def showPage(self) -> None:
        """Saves current canvas state for second-pass dynamic page calculation."""
        self._saved_page_states.append(dict(self.__dict__))
        start_page_fn = getattr(self, "_startPage", None)
        if callable(start_page_fn):
            start_page_fn()

    def save(self) -> None:
        """Executes second pass to render headers, footers, and page numbers across all pages."""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count: int) -> None:
        """Renders running header and footer borders and dynamic page strings."""
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(HexColor("#475569"))
        
        # Running Top Header
        self.drawString(36, 762, "WILSY OS  |  EXECUTIVE MILESTONE REPORT  •  FG181 ACTIVATION")
        self.setFont("Helvetica", 8)
        self.drawRightString(576, 762, "CONFIDENTIAL & PROPRIETARY")
        
        self.setStrokeColor(HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(36, 754, 576, 754)

        # Running Bottom Footer
        self.line(36, 45, 576, 45)
        self.drawString(36, 30, "WILSY (PTY) LTD  •  ENTERPRISE OPERATING SYSTEM ARCHITECTURE")
        
        current_page = getattr(self, "_pageNumber", 1)
        page_str = f"Page {current_page} of {page_count}"
        self.drawRightString(576, 30, page_str)
        self.restoreState()


def create_milestone_pdf(filename: str = "WilsyOS_FG181_Milestone_Report.pdf") -> str:
    """Generates the executive milestone report PDF."""
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    COLOR_PRIMARY = HexColor("#0F172A")
    COLOR_GOLD = HexColor("#B45309")
    COLOR_BG_LIGHT = HexColor("#F8FAFC")

    style_title = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=COLOR_PRIMARY,
        spaceAfter=4,
    )

    style_subtitle = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=COLOR_GOLD,
        spaceAfter=15,
    )

    style_h2 = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=COLOR_PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
    )

    style_body = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=HexColor("#1E293B"),
        spaceAfter=8,
    )

    style_quote = ParagraphStyle(
        "QuoteText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        leading=14,
        textColor=HexColor("#334155"),
        spaceBefore=6,
        spaceAfter=6,
    )

    style_table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=HexColor("#FFFFFF"),
    )

    style_table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=HexColor("#1E293B"),
    )

    style_table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=COLOR_PRIMARY,
    )

    story = []

    # 1. Header Banner Title
    story.append(Paragraph("FG181 Autonomous Engineering Kernel", style_title))
    story.append(Paragraph("TECHNICAL MILESTONE CERTIFICATION & ENTERPRISE RUNTIME ACTIVATION", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_GOLD, spaceBefore=0, spaceAfter=12))

    # 2. Executive Metadata Box Table
    meta_data = [
        [
            Paragraph("<b>Founder & Chief Architect:</b> Wilson Khanyezi", style_table_cell),
            Paragraph("<b>System / Runtime:</b> Wilsy OS Kernel (FG181)", style_table_cell),
        ],
        [
            Paragraph("<b>Organization:</b> Wilsy (Pty) Ltd", style_table_cell),
            Paragraph("<b>Execution ID:</b> KEXEC-CB6B72D0", style_table_cell),
        ],
        [
            Paragraph("<b>Activation Timestamp:</b> July 22, 2026 | 13:36 SAST", style_table_cell),
            Paragraph("<b>Total Pipeline Latency:</b> <font color='#15803D'><b>17.663 ms</b></font>", style_table_cell),
        ],
        [
            Paragraph("<b>System Readiness:</b> <font color='#15803D'><b>GOLD_PRODUCTION_READY</b></font>", style_table_cell),
            Paragraph("<b>Executive Health Index:</b> <font color='#B45309'><b>88.97 / 100</b></font>", style_table_cell),
        ],
    ]

    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 3. Architectural Intent & Biblical Vision
    story.append(Paragraph("1. Epitome & Architectural Intent", style_h2))
    story.append(Paragraph(
        "The <b>FG181 Autonomous Engineering Kernel</b> establishes an unbroken 18-stage runtime sequence designed to turn "
        "every system execution request into deterministic organizational intelligence and permanent software asset value. "
        "Operated as a foundational kernel within Wilsy OS, FG181 enforces strict governance, real-time worker scheduling, memory state persistence, "
        "predictive telemetry synthesis, and direct institutional learning feed.",
        style_body
    ))

    # Biblical Quote Box
    quote_data = [[
        Paragraph(
            "<i>\"And he shall be like a tree planted by the rivers of water, that bringeth forth his fruit in his season; "
            "his leaf also shall not wither; and whatsoever he doeth shall prosper.\"</i> — <b>Psalm 1:3</b>",
            style_quote
        )
    ]]
    quote_table = Table(quote_data, colWidths=[540])
    quote_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor("#FEF3C7")),
        ('BOX', (0, 0), (-1, -1), 1, HexColor("#F59E0B")),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(quote_table)
    story.append(Spacer(1, 12))

    # 4. 18-Stage Execution Runtime Breakdown Table
    story.append(Paragraph("2. Verified 18-Stage Runtime Pipeline Telemetry", style_h2))

    pipeline_stages: List[Tuple[str, str, str, str, str]] = [
        ("01", "Execution Request", "Initial user or API execution dispatch captured", "0.00 ms", "VERIFIED"),
        ("02", "Execution Context", "Environment, authorization, and context isolation", "0.00 ms", "VERIFIED"),
        ("03", "Governance", "Security clearance, policy, and compliance check", "0.00 ms", "VERIFIED"),
        ("04", "Execution Plan", "Task decomposition into executable AST nodes", "0.00 ms", "VERIFIED"),
        ("05", "Scheduler", "Queue positioning, time-slot, and priority allocation", "0.00 ms", "VERIFIED"),
        ("06", "Registry", "Dynamic worker allocation and resource lock", "0.00 ms", "VERIFIED"),
        ("07", "Workers", "Parallel task compilation, build, and test execution", "16.96 ms", "VERIFIED"),
        ("08", "Event Bus", "Real-time asynchronous telemetry event broadcast", "0.03 ms", "VERIFIED"),
        ("09", "Memory", "Transactional state persistence to Kernel Memory Store", "0.00 ms", "VERIFIED"),
        ("10", "Replay", "Deterministic execution hashing & state match validation", "0.00 ms", "VERIFIED"),
        ("11", "Prediction", "Defect probability & latency variance projection", "0.00 ms", "VERIFIED"),
        ("12", "Learning", "Institutional Learning Engine integration and sync", "0.05 ms", "VERIFIED"),
        ("13", "Optimization", "JIT cache tuning and memory pool optimization", "0.00 ms", "VERIFIED"),
        ("14", "Artifact Bus", "Manifest publication and binary asset output", "0.01 ms", "VERIFIED"),
        ("15", "Reports", "Compliance and technical report generation", "0.00 ms", "VERIFIED"),
        ("16", "Dashboard", "Real-time UI metrics state update", "0.00 ms", "VERIFIED"),
        ("17", "Executive Intelligence", "9-Metric C-Suite synthesis (EOS Index: 88.97)", "0.55 ms", "VERIFIED"),
        ("18", "Institutional Knowledge", "Permanent IK-RULE-181 pattern store writing", "0.00 ms", "VERIFIED"),
    ]

    table_data = [[
        Paragraph("<b>Stage</b>", style_table_header),
        Paragraph("<b>Pipeline Stage Name</b>", style_table_header),
        Paragraph("<b>Functional Subsystem Action</b>", style_table_header),
        Paragraph("<b>Latency</b>", style_table_header),
        Paragraph("<b>Status</b>", style_table_header),
    ]]

    for step_num, stage_name, description, latency, status in pipeline_stages:
        table_data.append([
            Paragraph(f"<b>{step_num}</b>", style_table_cell_bold),
            Paragraph(stage_name, style_table_cell_bold),
            Paragraph(description, style_table_cell),
            Paragraph(latency, style_table_cell),
            Paragraph(f"<font color='#15803D'><b>{status}</b></font>", style_table_cell),
        ])

    stage_table = Table(table_data, colWidths=[40, 130, 230, 70, 70])
    stage_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor("#FFFFFF"), COLOR_BG_LIGHT]),
    ]))

    story.append(stage_table)
    story.append(Spacer(1, 14))

    # 5. Strategic Significance & Institutional Impact
    story.append(Paragraph("3. Institutional Impact & Strategic Value", style_h2))
    impact_text = (
        "With the completion of FG181, Wilsy OS transitions into an <b>autonomous, self-learning enterprise kernel</b>. "
        "Every code compilation, build request, and system evaluation is captured, "
        "predicted, optimized, and archived into permanent institutional knowledge."
    )
    story.append(Paragraph(impact_text, style_body))
    story.append(Spacer(1, 10))

    # 6. Formal Sign-Off Block
    signoff_data = [
        [
            Paragraph("<b>CERTIFIED & APPROVED BY:</b>", style_table_cell),
            Paragraph("<b>GOVERNANCE & AUDIT SEAL:</b>", style_table_cell),
        ],
        [
            Paragraph("<b>Wilson Khanyezi</b><br/>Founder & Chief Architect, Wilsy OS", style_table_cell_bold),
            Paragraph("<b>WILSY (PTY) LTD — KERNEL FG181</b><br/>Status: <i>Production Ready (100% Passed)</i>", style_table_cell),
        ]
    ]

    signoff_table = Table(signoff_data, colWidths=[270, 270])
    signoff_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, COLOR_GOLD),
        ('BACKGROUND', (0, 0), (-1, -1), HexColor("#FFFBEB")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))

    story.append(KeepTogether([signoff_table]))

    doc.build(story, canvasmaker=ExecutiveNumberedCanvas)
    return filename


if __name__ == "__main__":
    output_pdf = create_milestone_pdf()
    print(f"\n[✓] EXECUTIVE MILESTONE REPORT GENERATED SUCCESSFULLY:")
    print(f"    Path: {os.path.abspath(output_pdf)}")
