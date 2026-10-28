"""Authenticated Python EOS presentation-only PDF export.

TITLE: WILSY OS Python EOS Artifact PDF Router
VERSION: v1.0.0-PYTHON-EOS-PRESENTATION-PDF
AUTHORITY: Wilsy OS Core Governance; authenticated presentation export only
EPITOME: Renders a bounded caller-supplied artifact payload to PDF while keeping
         source verification, legal issuance, invoice authority, payment truth,
         settlement truth, and tenant membership outside this presentation seam.
ABSOLUTE CANONICAL PATH: tools/eos/api/artifact_pdf_router.py
COLLABORATION / OWNERSHIP: Python EOS API, canonical authenticated identity projection,
                           ReportLab PDF generation, and client artifact export.
CERTIFICATION / UPDATE DATE: 2026-10-27
CHANGELOG: v1.0.0 replaces the Node BFF PDF transport with an authenticated Python EOS
           presentation export. The server hashes the exact request and generated
           artifact; it does not claim caller-supplied business content is verified.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No HTML execution, URL fetch, filesystem asset loading, or
                            arbitrary file attachment is permitted. Payload size and
                            rendered field count are bounded.
TENANT BOUNDARY: Authenticated tenant claim is context only, not membership evidence.
                 A caller-supplied top-level tenantId may not override that context.
AUTHORITY BOUNDARY: PDF presentation only; no legal issuance, signing, source verification,
                    matter disclosure, or institutional decision authority.
FINANCIAL AUTHORITY BOUNDARY: No invoice issuance, payment, execution, or settlement
                              truth is created. Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Invalid or cross-context requests fail closed; integrity digests
                     are labeled as hashes, never as a digital signature.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
import struct
from datetime import datetime, timezone
from io import BytesIO
from typing import Any
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from tools.eos.auth.authentication import get_current_identity
from tools.eos.auth.identity import SovereignIdentity

VERSION = "v1.0.0-PYTHON-EOS-PRESENTATION-PDF"
MAX_REQUEST_BYTES = 10 * 1024 * 1024
MAX_RENDERED_FIELDS = 120
MAX_VALUE_CHARS = 4000

router = APIRouter(tags=["Artifact PDF"])


def _canonical_json(value: Any) -> bytes:
    """Serialize JSON-compatible request data deterministically for hashing only."""
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ARTIFACT_PDF_PAYLOAD_MUST_BE_JSON_COMPATIBLE",
        ) from error


def _enterprise_pdf_parity_required(value: Any, *, depth: int = 0) -> bool:
    """Identify source-backed artifact families that the generic renderer cannot replace.

    This guard deliberately fails closed rather than presenting caller-supplied JSON as
    a verified invoice, CRM proof pack, Knowledge Base export, NDA, or playbook artifact.
    It is not an authorization decision and grants no source-read or issuance authority.
    """
    if depth > 8:
        return isinstance(value, (dict, list))
    if isinstance(value, dict):
        for key, child in value.items():
            normalized_key = re.sub(r"[^a-z0-9]", "", str(key).lower())
            if normalized_key in {"crmproofpack", "knowledgebase", "playbook", "playbookpayload"}:
                return True
            if normalized_key in {"type", "artifacttype", "templatetype", "servicetype", "documenttype", "artifactkind"} and isinstance(child, str):
                discriminator = re.sub(r"[^a-z0-9]", "", child.lower())
                if (
                    "invoice" in discriminator
                    or "crmleadproofpack" in discriminator
                    or "crmproofpack" in discriminator
                    or "knowledgebase" in discriminator
                    or "playbookfg108" in discriminator
                    or "nondisclosureagreement" in discriminator
                    or discriminator == "nda"
                    or discriminator.startswith("ndatemplate")
                ):
                    return True
            if _enterprise_pdf_parity_required(child, depth=depth + 1):
                return True
    elif isinstance(value, list):
        return any(_enterprise_pdf_parity_required(item, depth=depth + 1) for item in value)
    return False


def _text(value: Any, *, limit: int = MAX_VALUE_CHARS) -> str:
    """Return bounded, escaped presentation text without executing markup."""
    if isinstance(value, (dict, list)):
        try:
            rendered = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
        except (TypeError, ValueError):
            rendered = "[unrenderable value]"
    elif value is None:
        rendered = "—"
    elif isinstance(value, bool):
        rendered = "true" if value else "false"
    else:
        rendered = str(value)
    truncated = len(rendered) >= limit
    rendered = rendered[:limit]
    if truncated:
        rendered += "…"
    return escape(rendered).replace("\n", "<br/>")


def _flatten(value: Any, prefix: str = "", depth: int = 0) -> list[tuple[str, str]]:
    """Flatten JSON data to a bounded, readable key/value presentation."""
    if depth > 4:
        return [(prefix or "value", _text(value))]
    rows: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key in sorted(value.keys(), key=lambda item: str(item)):
            label = f"{prefix}.{key}" if prefix else str(key)
            child = value[key]
            if isinstance(child, dict) and child and depth < 3:
                rows.extend(_flatten(child, label, depth + 1))
            elif isinstance(child, list) and child and all(isinstance(item, dict) for item in child[:20]):
                for index, item in enumerate(child[:20]):
                    rows.extend(_flatten(item, f"{label}[{index}]", depth + 1))
            else:
                rows.append((label, _text(child)))
            if len(rows) >= MAX_RENDERED_FIELDS:
                return rows[:MAX_RENDERED_FIELDS]
        return rows
    if isinstance(value, list):
        for index, item in enumerate(value[:MAX_RENDERED_FIELDS]):
            rows.extend(_flatten(item, f"{prefix}[{index}]", depth + 1))
            if len(rows) >= MAX_RENDERED_FIELDS:
                return rows[:MAX_RENDERED_FIELDS]
        return rows
    return [(prefix or "value", _text(value))]


def _page_chrome(canvas: Any, document: Any) -> None:
    """Stamp neutral page chrome; it confers no legal status."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm

    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#1F4E79"))
    canvas.setLineWidth(1.2)
    canvas.line(18 * mm, height - 19 * mm, width - 18 * mm, height - 19 * mm)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(colors.HexColor("#1F4E79"))
    canvas.drawString(18 * mm, height - 15 * mm, "WILSY OS")
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#4B5563"))
    canvas.drawString(18 * mm, 11 * mm, "CONFIDENTIAL · PRESENTATION EXPORT ONLY · SOURCE NOT VERIFIED")
    canvas.drawRightString(width - 18 * mm, 11 * mm, f"Page {document.page}")
    canvas.restoreState()


def render_artifact_pdf(
    body: dict[str, Any],
    identity: SovereignIdentity,
    *,
    generated_at: str | None = None,
) -> tuple[bytes, dict[str, str]]:
    """Render caller-supplied JSON with integrity hashes but no source-authority claim.

    The function does not retrieve or verify an underlying invoice, legal document,
    matter, approval, signature, payment, or settlement record.
    """
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    canonical = _canonical_json(body)
    if len(canonical) > MAX_REQUEST_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="ARTIFACT_PDF_PAYLOAD_TOO_LARGE",
        )
    now = generated_at or datetime.now(timezone.utc).isoformat()
    payload = body.get("data") or body.get("payload") or body.get("artifact")
    if payload is None:
        payload = {key: value for key, value in body.items() if key not in {"tenantId", "signature"}}
    if not isinstance(payload, dict):
        payload = {"content": payload}
    signature_value = body.get("signature")
    if signature_value is None:
        signature_value = payload.get("signature")
    payload = {key: value for key, value in payload.items() if str(key).lower() != "signature"}
    metadata = body.get("metadata") if isinstance(body.get("metadata"), dict) else {}
    artifact_type = str(
        body.get("type") or body.get("artifactType") or body.get("templateType")
        or metadata.get("type") or "WILSY-OS-ARTIFACT"
    )[:160]
    title = str(body.get("title") or metadata.get("title") or artifact_type)[:240]
    trace_candidate = str(body.get("traceId") or body.get("traceID") or metadata.get("traceId") or "")
    trace_id = re.sub(r"[^A-Za-z0-9._-]", "", trace_candidate)[:96]
    if not trace_id:
        trace_id = f"ART-{hashlib.sha256(canonical).hexdigest()[:20].upper()}"
    request_digest = hashlib.sha512(canonical).hexdigest()
    render_context_digest = hashlib.sha3_512(
        b"WILSY-OS-PRESENTATION-PDF-v1\x00"
        + identity.identity_id.encode("utf-8")
        + b"\x00" + identity.tenant_id.encode("utf-8")
        + b"\x00" + trace_id.encode("utf-8")
        + b"\x00" + request_digest.encode("ascii")
    ).hexdigest()

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="WilsyTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=18, leading=22, textColor=colors.HexColor("#1F4E79"),
        alignment=TA_LEFT, spaceAfter=5 * mm,
    ))
    styles.add(ParagraphStyle(
        name="WilsyWarning", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=8, leading=11, textColor=colors.HexColor("#8A2C0D"),
        backColor=colors.HexColor("#FFF3E8"), borderPadding=6, spaceAfter=4 * mm,
    ))
    styles.add(ParagraphStyle(name="WilsyCell", parent=styles["Normal"], fontSize=8, leading=10, wordWrap="CJK"))
    story: list[Any] = [
        Spacer(1, 4 * mm),
        Paragraph(_text(title), styles["WilsyTitle"]),
        Paragraph(
            "PRESENTATION EXPORT ONLY. The payload is caller-supplied and has not been "
            "independently verified. This PDF does not prove issuance, approval, execution, "
            "payment, settlement, legal signature, or institutional ratification.",
            styles["WilsyWarning"],
        ),
        Paragraph(f"<b>Artifact type:</b> {_text(artifact_type)}", styles["Normal"]),
        Paragraph(f"<b>Generated at (UTC):</b> {_text(now)}", styles["Normal"]),
        Paragraph(f"<b>Authenticated principal reference:</b> {_text(identity.identity_id)}", styles["Normal"]),
        Paragraph(
            f"<b>Request tenant context (membership not implied):</b> {_text(identity.tenant_id)}",
            styles["Normal"],
        ),
        Paragraph(f"<b>Trace reference:</b> {_text(trace_id)}", styles["Normal"]),
        Spacer(1, 5 * mm),
        Paragraph("Submitted content", styles["Heading2"]),
    ]
    rows = _flatten(payload) or [("content", "No payload fields supplied.")]
    table_data = [[Paragraph("<b>Field</b>", styles["WilsyCell"]), Paragraph("<b>Value</b>", styles["WilsyCell"])]]
    table_data.extend([
        [Paragraph(_text(key, limit=256), styles["WilsyCell"]), Paragraph(value, styles["WilsyCell"])]
        for key, value in rows[:MAX_RENDERED_FIELDS]
    ])
    table = Table(table_data, colWidths=[48 * mm, 126 * mm], repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(table)
    if signature_value is not None:
        story.extend([
            Spacer(1, 5 * mm),
            Paragraph("Submitted signature", styles["Heading2"]),
            Paragraph(
                "User-supplied signature data. This endpoint does not verify signer identity, "
                "intent, certificate, or legal effect.",
                styles["WilsyWarning"],
            ),
        ])
        if isinstance(signature_value, str) and signature_value.startswith("data:image/"):
            if len(signature_value) > 1_500_000:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="ARTIFACT_PDF_SIGNATURE_IMAGE_TOO_LARGE",
                )
            match = re.fullmatch(
                r"data:image/png;base64,([A-Za-z0-9+/=]+)",
                signature_value,
            )
            if not match:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="ARTIFACT_PDF_SIGNATURE_IMAGE_FORMAT_INVALID",
                )
            try:
                image_bytes = base64.b64decode(match.group(1), validate=True)
            except (binascii.Error, ValueError) as error:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="ARTIFACT_PDF_SIGNATURE_IMAGE_BASE64_INVALID",
                ) from error
            if (
                len(image_bytes) > 1_000_000
                or not image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
                or len(image_bytes) < 24
                or image_bytes[12:16] != b"IHDR"
            ):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="ARTIFACT_PDF_SIGNATURE_IMAGE_BYTES_INVALID",
                )
            width_px, height_px = struct.unpack(">II", image_bytes[16:24])
            if not (1 <= width_px <= 2048 and 1 <= height_px <= 1024):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="ARTIFACT_PDF_SIGNATURE_IMAGE_DIMENSIONS_INVALID",
                )
            story.append(Image(BytesIO(image_bytes), width=65 * mm, height=22 * mm, kind="proportional"))
        else:
            story.append(Paragraph(_text(signature_value, limit=512), styles["WilsyCell"]))
    story.extend([Spacer(1, 5 * mm), Paragraph("Integrity metadata", styles["Heading2"])])
    integrity_rows = [
        [Paragraph("<b>Measure</b>", styles["WilsyCell"]), Paragraph("<b>Value</b>", styles["WilsyCell"])],
        [Paragraph("Request SHA-512 digest (hash only)", styles["WilsyCell"]), Paragraph(request_digest, styles["WilsyCell"])],
        [Paragraph("Render-context SHA3-512 digest (hash only)", styles["WilsyCell"]), Paragraph(render_context_digest, styles["WilsyCell"])],
        [Paragraph("Source verification", styles["WilsyCell"]), Paragraph("NOT PERFORMED", styles["WilsyCell"])],
    ]
    integrity_table = Table(integrity_rows, colWidths=[62 * mm, 112 * mm], repeatRows=1, hAlign="LEFT")
    integrity_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF5")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(integrity_table)

    output = BytesIO()
    document = SimpleDocTemplate(
        output, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=26 * mm, bottomMargin=19 * mm, title=title[:240],
        author="WILSY OS Python EOS presentation export",
        subject="Caller-supplied presentation; source verification not performed",
    )
    document.build(story, onFirstPage=_page_chrome, onLaterPages=_page_chrome)
    pdf = output.getvalue()
    if not pdf.startswith(b"%PDF-"):
        raise RuntimeError("ARTIFACT_PDF_RENDERER_OUTPUT_INVALID")
    pdf_digest = hashlib.sha3_512(pdf).hexdigest()
    return pdf, {
        "trace_id": trace_id,
        "request_digest": request_digest,
        "render_context_digest": render_context_digest,
        "pdf_digest": pdf_digest,
        "artifact_type": artifact_type,
    }


@router.post("/generate/pdf", response_class=Response)
async def generate_artifact_pdf(
    request: Request,
    identity: SovereignIdentity = Depends(get_current_identity),
) -> Response:
    """Render a bounded PDF for the authenticated request without creating authority."""
    raw_chunks: list[bytes] = []
    raw_size = 0
    async for chunk in request.stream():
        raw_size += len(chunk)
        if raw_size > MAX_REQUEST_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="ARTIFACT_PDF_PAYLOAD_TOO_LARGE",
            )
        raw_chunks.append(chunk)
    raw_body = b"".join(raw_chunks)
    try:
        body = json.loads(raw_body)
    except (ValueError, UnicodeDecodeError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ARTIFACT_PDF_JSON_BODY_REQUIRED"
        ) from error
    if not isinstance(body, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="ARTIFACT_PDF_OBJECT_REQUIRED"
        )
    caller_tenant = body.get("tenantId")
    if caller_tenant is not None and str(caller_tenant) != identity.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="ARTIFACT_PDF_TENANT_CONTEXT_MISMATCH"
        )
    if _enterprise_pdf_parity_required(body):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ARTIFACT_PDF_ENTERPRISE_PARITY_UNAVAILABLE",
        )
    pdf, evidence = render_artifact_pdf(body, identity)
    safe_trace = re.sub(r"[^A-Za-z0-9._-]", "", evidence["trace_id"])[:96] or "artifact"
    response = Response(content=pdf, media_type="application/pdf")
    response.headers["Content-Disposition"] = f'attachment; filename="wilsy-artifact-{safe_trace}.pdf"'
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Wilsy-Pdf-Renderer"] = "PYTHON_EOS_PRESENTATION_EXPORT"
    response.headers["X-Wilsy-Trace-ID"] = evidence["trace_id"]
    response.headers["X-Artifact-Proof-Status"] = "SOURCE_UNVERIFIED"
    response.headers["X-Request-Proof"] = evidence["request_digest"]
    response.headers["X-Wilsy-Render-Context-Digest"] = evidence["render_context_digest"]
    response.headers["X-Wilsy-Pdf-SHA3-512"] = evidence["pdf_digest"]
    response.headers["X-Wilsy-Artifact-Type"] = re.sub(
        r"[^A-Za-z0-9._-]", "", evidence["artifact_type"]
    )[:96] or "artifact"
    return response


# ARTIFACT: artifact_pdf_router.py
# VERSION: v1.0.0-PYTHON-EOS-PRESENTATION-PDF
# AUTHORITY BOUNDARY: Authenticated presentation export only; no source verification or issuance.
# TENANT POSTURE: Identity tenant claim is context only; caller cannot override top-level context.
# FAIL-CLOSED POSTURE: Invalid payloads and context mismatch are rejected; hashes are not signatures.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no payment or settlement truth.
# END OF WILSY OS SOVEREIGN ARTIFACT
