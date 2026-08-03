"""
PDF Report Generator for Credit Rating Simulator — CORE Rating Criteria v3.0

Renders a complete, multi-page PDF credit rating rationale report using ReportLab.
Includes Executive Summary, CORE Block Scores, Detailed Block Narratives with Tier 2 Sector Context,
Rating Sensitivities (Upward & Downward Drivers), Tier 1/2 Grounded Citations, and Mandatory Academic Disclaimer.
"""

import io
from typing import Dict, Any, List, Optional
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

MANDATORY_DISCLAIMER = (
    "This is an indicative, academic assessment produced for an ICAI AICA Level 2 capstone project. "
    "It is not a credit rating issued by a registered credit rating agency and must not be relied upon as one."
)

def _esc(val: Any) -> str:
    """Escapes XML special characters (&, <, >) for ReportLab Paragraph rendering."""
    if val is None:
        return ""
    return escape(str(val))

def generate_rationale_pdf(project_id: str, project_data: Dict[str, Any], score_result: Dict[str, Any]) -> bytes:
    """
    Generates a PDF credit rating rationale report from project inputs and score results.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A")
    )
    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#2563EB")
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155")
    )
    disclaimer_style = ParagraphStyle(
        "DisclaimerText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748B")
    )

    story = []

    # 1. Header
    p_name = _esc(project_data.get("project_name") or project_id)
    tech = _esc(project_data.get("technology_type", "N/A"))
    cap = _esc(project_data.get("installed_capacity_mw_ac", "N/A"))
    pid_esc = _esc(project_id)

    story.append(Paragraph("CREDIT RATIONALE REPORT", subtitle_style))
    story.append(Paragraph(f"Project: {p_name}", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Technology: {tech} | Installed Capacity: {cap} MW | ID: {pid_esc}", body_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#CBD5E1"), spaceAfter=10))

    # Extract rationale object
    rationale_obj = score_result.get("rationale", {})
    if isinstance(rationale_obj, dict):
        exec_summary = _esc(rationale_obj.get("executive_summary", ""))
        blk_a_narr = _esc(rationale_obj.get("block_a_narrative", ""))
        blk_b_narr = _esc(rationale_obj.get("block_b_narrative", ""))
        blk_c_narr = _esc(rationale_obj.get("block_c_narrative", ""))
        blk_d_narr = _esc(rationale_obj.get("block_d_narrative", ""))
        sensitivities = rationale_obj.get("rating_sensitivities", {})
        citations = rationale_obj.get("citations", [])
    else:
        exec_summary = _esc(str(rationale_obj) if rationale_obj else "")
        blk_a_narr, blk_b_narr, blk_c_narr, blk_d_narr = "", "", "", ""
        sensitivities = {}
        citations = []

    # 2. Executive Summary Block
    if exec_summary:
        story.append(Paragraph("Executive Summary", section_heading))
        story.append(Paragraph(exec_summary, body_style))
        story.append(Spacer(1, 8))

    # 3. Rating Summary Table
    ind_band = _esc(score_result.get("indicative_band", "N/A"))
    final_band = _esc(score_result.get("final_band", "N/A"))
    post_score = score_result.get("post_notching_score")
    raw_score = score_result.get("raw_score")
    confidence = _esc(score_result.get("confidence", "N/A"))
    conf_reason = _esc(score_result.get("confidence_reason", ""))
    cap_notice = _esc(score_result.get("cap_notice")) if score_result.get("cap_notice") else ""

    score_str = f"{post_score:.1f} / 115.0" if post_score is not None else "N/A"
    raw_str = f"{raw_score:.1f}" if raw_score is not None else "N/A"

    summary_data = [
        [
            Paragraph("<b>Final Rating Band</b>", body_style),
            Paragraph(f"<b>{final_band}</b>", body_style),
            Paragraph("<b>Indicative Score</b>", body_style),
            Paragraph(f"<b>{score_str}</b>", body_style),
        ],
        [
            Paragraph("<b>Indicative Band</b>", body_style),
            Paragraph(ind_band, body_style),
            Paragraph("<b>Raw Score</b>", body_style),
            Paragraph(raw_str, body_style),
        ],
        [
            Paragraph("<b>Confidence Level</b>", body_style),
            Paragraph(f"{confidence} ({conf_reason})", body_style),
            Paragraph("<b>Assessment Status</b>", body_style),
            Paragraph("Approved & Scored", body_style),
        ]
    ]

    summary_table = Table(summary_data, colWidths=[130, 120, 130, 124])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 8))

    if cap_notice:
        cap_box = Table(
            [[Paragraph(f"<b>BAND CAP NOTICE:</b> {cap_notice}", body_style)]],
            colWidths=[504]
        )
        cap_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF2F2")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FCA5A5")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(cap_box)
        story.append(Spacer(1, 8))

    # 4. Block Sub-factor Score Breakdown
    story.append(Paragraph("Score Breakdown by CORE Block", section_heading))
    
    blk_a = score_result.get("block_a_score")
    blk_b = score_result.get("block_b_score")
    blk_c = score_result.get("block_c_score")
    blk_d = score_result.get("block_d_score")

    breakdown_data = [
        ["CORE Rating Block", "Max Points", "Score Achieved", "% Score"],
        ["Block A: Business & Asset Risk", "35.0", f"{blk_a:.1f}" if blk_a is not None else "N/A", f"{(blk_a/35.0*100):.1f}%" if blk_a is not None else "N/A"],
        ["Block B: Cash-flow Adequacy & Coverage", "35.0", f"{blk_b:.1f}" if blk_b is not None else "N/A", f"{(blk_b/35.0*100):.1f}%" if blk_b is not None else "N/A"],
        ["Block C: Financial Strength & Liquidity", "25.0", f"{blk_c:.1f}" if blk_c is not None else "N/A", f"{(blk_c/25.0*100):.1f}%" if blk_c is not None else "N/A"],
        ["Block D: Structural & Covenant Protections", "20.0", f"{blk_d:.1f}" if blk_d is not None else "N/A", f"{(blk_d/20.0*100):.1f}%" if blk_d is not None else "N/A"],
        ["Total Post-Notching Score", "115.0", f"{post_score:.1f}" if post_score is not None else "N/A", f"{(post_score/115.0*100):.1f}%" if post_score is not None else "N/A"],
    ]

    breakdown_table = Table(breakdown_data, colWidths=[234, 90, 90, 90])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#F1F5F9")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(breakdown_table)
    story.append(Spacer(1, 10))

    # 5. Detailed CORE Block Narratives
    story.append(Paragraph("Detailed Risk Factor Analysis", section_heading))
    if blk_a_narr:
        story.append(Paragraph(f"<b>Block A — Business & Asset Risk:</b> {blk_a_narr}", body_style))
        story.append(Spacer(1, 5))
    if blk_b_narr:
        story.append(Paragraph(f"<b>Block B — Cash-Flow Adequacy & Coverage:</b> {blk_b_narr}", body_style))
        story.append(Spacer(1, 5))
    if blk_c_narr:
        story.append(Paragraph(f"<b>Block C — Financial Strength & Liquidity:</b> {blk_c_narr}", body_style))
        story.append(Spacer(1, 5))
    if blk_d_narr:
        story.append(Paragraph(f"<b>Block D — Structural Protections:</b> {blk_d_narr}", body_style))
        story.append(Spacer(1, 10))

    # 6. Rating Sensitivities Section (Upward & Downward Drivers)
    pos_factors = [_esc(f) for f in sensitivities.get("positive_factors", [])] if isinstance(sensitivities, dict) else []
    neg_factors = [_esc(f) for f in sensitivities.get("negative_factors", [])] if isinstance(sensitivities, dict) else []

    if pos_factors or neg_factors:
        story.append(Paragraph("Rating Sensitivities — Key Drivers", section_heading))
        
        if pos_factors:
            story.append(Paragraph("<b>Upward Rating Drivers (Factors that could lead to a rating upgrade):</b>", body_style))
            story.append(Spacer(1, 3))
            for f_text in pos_factors:
                story.append(Paragraph(f"• {f_text}", body_style))
                story.append(Spacer(1, 2))
            story.append(Spacer(1, 4))

        if neg_factors:
            story.append(Paragraph("<b>Downward Rating Drivers (Factors that could lead to a rating downgrade):</b>", body_style))
            story.append(Spacer(1, 3))
            for f_text in neg_factors:
                story.append(Paragraph(f"• {f_text}", body_style))
                story.append(Spacer(1, 2))
            story.append(Spacer(1, 8))

    # 7. Grounded Methodology Citations
    if citations:
        story.append(Paragraph("Methodology Citations & Grounding", section_heading))
        for c in citations:
            doc_name = _esc(c.get("source_document", ""))
            sec_name = _esc(c.get("source_section", ""))
            claim_text = _esc(c.get("display_claim") or c.get("claim", ""))
            cit_line = f"• <b>[{doc_name} — {sec_name}]</b>: {claim_text}"
            story.append(Paragraph(cit_line, body_style))
            story.append(Spacer(1, 4))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=8))

    # 8. Mandatory Academic Disclaimer Footer
    story.append(Paragraph(f"<b>DISCLAIMER:</b> {_esc(MANDATORY_DISCLAIMER)}", disclaimer_style))

    doc.build(story)
    return buffer.getvalue()

