"""Shared visual system for DAL research publications.

The helpers change presentation only. Report-specific evidence, claims and
source wording remain in each publication generator.
"""

from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph


DARK = colors.HexColor("#06131D")
PANEL = colors.HexColor("#0B2637")
NAVY = colors.HexColor("#173E5B")
SIGNAL = colors.HexColor("#71DCFF")
SIGNAL_GREEN = colors.HexColor("#6EE7C2")
SIGNAL_VIOLET = colors.HexColor("#9587FF")
SKY = colors.HexColor("#DDF2FF")
WHITE = colors.white
MUTED_LIGHT = colors.HexColor("#A9C0CE")
LINE = colors.HexColor("#C5DFEE")
MUTED = colors.HexColor("#60798B")


def _paragraph(canvas, text: str, style: ParagraphStyle, x: float, top: float, width: float) -> float:
    paragraph = Paragraph(text, style)
    _, height = paragraph.wrap(width, 120 * mm)
    paragraph.drawOn(canvas, x, top - height)
    return height


def draw_signature_cover(
    canvas,
    *,
    page_w: float,
    page_h: float,
    left: float,
    right: float,
    brand: str,
    series: str,
    formal_title: str,
    headline: str,
    subtitle: str,
    report_date: str,
    author: str,
    taxonomy: str,
) -> None:
    """Draw a premium, answer-led cover with an original evidence-sphere motif."""

    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, page_w, page_h, stroke=0, fill=1)

    # Layered tonal fields create depth without a decorative full-page grid.
    canvas.setFillColor(colors.HexColor("#081C29"))
    canvas.rect(0, 0, page_w * 0.72, page_h, stroke=0, fill=1)
    canvas.setFillColor(PANEL)
    canvas.wedge(page_w - 104 * mm, -35 * mm, page_w + 29 * mm, 98 * mm, 0, 360, stroke=0, fill=1)

    # Evidence sphere: a DAL-specific signal rather than borrowed brand artwork.
    cx, cy = page_w - 30 * mm, 66 * mm
    for radius, colour, width in (
        (54 * mm, colors.HexColor("#163E4E"), 0.7),
        (43 * mm, colors.HexColor("#245E68"), 0.7),
        (31 * mm, colors.HexColor("#2D7B78"), 0.8),
        (19 * mm, SIGNAL_GREEN, 0.9),
    ):
        canvas.setStrokeColor(colour)
        canvas.setLineWidth(width)
        canvas.circle(cx, cy, radius, stroke=1, fill=0)
    canvas.setFillColor(colors.HexColor("#0E3C43"))
    canvas.circle(cx, cy, 18 * mm, stroke=0, fill=1)
    canvas.setFillColor(SIGNAL_GREEN)
    canvas.circle(cx - 7 * mm, cy + 8 * mm, 2.1 * mm, stroke=0, fill=1)
    canvas.setFillColor(SIGNAL)
    canvas.circle(cx + 33 * mm, cy + 12 * mm, 1.5 * mm, stroke=0, fill=1)
    canvas.setFillColor(SIGNAL_VIOLET)
    canvas.circle(cx - 25 * mm, cy - 25 * mm, 1.5 * mm, stroke=0, fill=1)

    canvas.setFillColor(SIGNAL_GREEN)
    canvas.rect(0, 0, 3 * mm, page_h, stroke=0, fill=1)
    canvas.setStrokeColor(colors.HexColor("#174052"))
    canvas.line(left, page_h - 28 * mm, page_w - right, page_h - 28 * mm)

    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(left, page_h - 20 * mm, brand.upper())
    canvas.setFillColor(MUTED_LIGHT)
    canvas.setFont("Helvetica", 6.7)
    canvas.drawRightString(page_w - right, page_h - 20 * mm, series.upper())

    canvas.setFillColor(SIGNAL)
    canvas.setFont("Helvetica-Bold", 7.3)
    canvas.drawString(left, page_h - 45 * mm, "EXECUTIVE RESEARCH BRIEF")
    canvas.setFillColor(MUTED_LIGHT)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.drawString(left, page_h - 55 * mm, formal_title.upper())

    title_style = ParagraphStyle(
        "SignatureCoverHeadline",
        fontName="Helvetica-Bold",
        fontSize=27,
        leading=30.5,
        textColor=WHITE,
        alignment=TA_LEFT,
    )
    headline_height = _paragraph(canvas, headline, title_style, left, page_h - 66 * mm, 150 * mm)

    subtitle_style = ParagraphStyle(
        "SignatureCoverSubtitle",
        fontName="Helvetica",
        fontSize=10.4,
        leading=15,
        textColor=SKY,
        alignment=TA_LEFT,
    )
    _paragraph(canvas, subtitle, subtitle_style, left, page_h - 71 * mm - headline_height, 128 * mm)

    canvas.setFillColor(colors.HexColor("#0A202D"))
    canvas.roundRect(left, 28 * mm, 104 * mm, 28 * mm, 3 * mm, stroke=0, fill=1)
    canvas.setStrokeColor(colors.HexColor("#245064"))
    canvas.roundRect(left, 28 * mm, 104 * mm, 28 * mm, 3 * mm, stroke=1, fill=0)
    canvas.setFillColor(SIGNAL_GREEN)
    canvas.setFont("Helvetica-Bold", 6.6)
    canvas.drawString(left + 6 * mm, 47 * mm, "SECONDARY EVIDENCE ONLY")
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 8.2)
    canvas.drawString(left + 6 * mm, 39 * mm, report_date)
    canvas.setFillColor(MUTED_LIGHT)
    canvas.setFont("Helvetica", 7.2)
    canvas.drawString(left + 6 * mm, 33 * mm, f"Prepared by {author}")

    canvas.setFillColor(MUTED_LIGHT)
    canvas.setFont("Helvetica-Bold", 5.9)
    canvas.drawRightString(page_w - right, 16 * mm, taxonomy.upper())
    canvas.restoreState()


def draw_page_frame(
    canvas,
    doc,
    *,
    page_w: float,
    page_h: float,
    left: float,
    right: float,
    brand: str,
    short_title: str,
    footer_note: str,
) -> None:
    """Draw the common publication folio on content pages."""

    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, page_h - 11 * mm, page_w, 11 * mm, stroke=0, fill=1)
    canvas.setFillColor(SIGNAL_GREEN)
    canvas.rect(0, page_h - 11 * mm, 2.2 * mm, 11 * mm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.drawString(left, page_h - 7 * mm, brand)
    canvas.setFillColor(MUTED_LIGHT)
    canvas.setFont("Helvetica", 6.2)
    canvas.drawRightString(page_w - right, page_h - 7 * mm, short_title.upper())

    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(left, 12 * mm, page_w - right, 12 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 6.3)
    canvas.drawString(left, 8 * mm, footer_note)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 6.4)
    canvas.drawRightString(page_w - right, 8 * mm, f"DAL / {doc.page:02d}")
    canvas.restoreState()
