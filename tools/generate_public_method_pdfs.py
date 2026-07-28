"""Generate the public methods guide and technical appendix PDFs."""

from __future__ import annotations

from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
PUBLICATIONS = ROOT / "publications"

BLUE = colors.HexColor("#2F83C5")
DEEP_BLUE = colors.HexColor("#174564")
PALE_BLUE = colors.HexColor("#EEF8FF")
SKY = colors.HexColor("#DFF3FF")
INK = colors.HexColor("#24455D")
MUTED = colors.HexColor("#587286")
GRID = colors.HexColor("#C4DFEF")
GOLD = colors.HexColor("#F6C95C")


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=32,
            textColor=DEEP_BLUE,
            alignment=TA_CENTER,
            spaceAfter=16,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leading=17,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "Heading1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=DEEP_BLUE,
            spaceBefore=10,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "Heading2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=BLUE,
            spaceBefore=7,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13.3,
            textColor=INK,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.9,
            leading=12.6,
            textColor=INK,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7.4,
            leading=10,
            textColor=DEEP_BLUE,
            backColor=PALE_BLUE,
            borderPadding=8,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "table": ParagraphStyle(
            "Table",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.3,
            leading=9.5,
            textColor=INK,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=MUTED,
        ),
    }


def page_decor(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(SKY)
    canvas.rect(0, height - 18 * mm, width, 18 * mm, stroke=0, fill=1)
    canvas.setFillColor(DEEP_BLUE)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(18 * mm, height - 11 * mm, "AI BUSINESS INTELLIGENCE LAB")
    canvas.setFont("Helvetica", 7.5)
    canvas.drawRightString(
        width - 18 * mm,
        height - 11 * mm,
        f"{doc.section_label}  |  PAGE {doc.page}",
    )
    canvas.setStrokeColor(GRID)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(
        18 * mm,
        8 * mm,
        "UK Business Data Survey 2026 | Public reproducibility evidence",
    )
    canvas.restoreState()


def document(path: Path, section_label: str) -> BaseDocTemplate:
    doc = BaseDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=25 * mm,
        bottomMargin=19 * mm,
        title=path.stem.replace("_", " "),
        author="AI Business Intelligence Lab",
    )
    doc.section_label = section_label
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="normal",
    )
    doc.addPageTemplates(
        [PageTemplate(id="main", frames=[frame], onPage=page_decor)]
    )
    return doc


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def markdown_story(markdown: str, title: str, subtitle: str):
    style = styles()
    story = [
        Spacer(1, 24 * mm),
        Paragraph(title, style["title"]),
        Paragraph(subtitle, style["subtitle"]),
        Table(
            [[Paragraph("PUBLIC METHODS RELEASE", style["small"])]],
            colWidths=[65 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), GOLD),
                    ("BOX", (0, 0), (-1, -1), 0.25, GOLD),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            ),
            hAlign="CENTER",
        ),
        Spacer(1, 18 * mm),
        Paragraph(
            "Official statistics, explicit denominators, supplied uncertainty "
            "and reproducible code.",
            style["subtitle"],
        ),
        Spacer(1, 30 * mm),
    ]

    lines = markdown.splitlines()
    index = 0
    bullets: list[str] = []

    def flush_bullets() -> None:
        nonlocal bullets
        if bullets:
            story.append(
                ListFlowable(
                    [
                        ListItem(Paragraph(escape(item), style["bullet"]))
                        for item in bullets
                    ],
                    bulletType="bullet",
                    start="circle",
                    leftIndent=16,
                    bulletFontName="Helvetica",
                    bulletFontSize=7,
                    spaceAfter=6,
                )
            )
            bullets = []

    while index < len(lines):
        line = lines[index].rstrip()
        if not line:
            flush_bullets()
            index += 1
            continue
        if line.startswith("# "):
            index += 1
            continue
        if line.startswith("## "):
            flush_bullets()
            story.append(Paragraph(escape(line[3:]), style["h1"]))
            index += 1
            continue
        if line.startswith("### "):
            flush_bullets()
            story.append(Paragraph(escape(line[4:]), style["h2"]))
            index += 1
            continue
        if line.startswith("- "):
            bullets.append(line[2:])
            index += 1
            continue
        if re.match(r"^\d+\. ", line):
            bullets.append(re.sub(r"^\d+\. ", "", line))
            index += 1
            continue
        if line.startswith("```"):
            flush_bullets()
            code_lines = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                code_lines.append(lines[index])
                index += 1
            index += 1
            story.append(Preformatted("\n".join(code_lines), style["code"]))
            continue
        if line.startswith("|") and index + 1 < len(lines):
            flush_bullets()
            table_lines = []
            while index < len(lines) and lines[index].startswith("|"):
                table_lines.append(lines[index])
                index += 1
            rows = [split_table_row(value) for value in table_lines]
            if len(rows) >= 2 and all(
                set(cell) <= {"-", ":"} for cell in rows[1]
            ):
                rows.pop(1)
            cells = [
                [Paragraph(escape(cell), style["table"]) for cell in row]
                for row in rows
            ]
            column_count = max(len(row) for row in cells)
            width = 170 * mm / column_count
            table = Table(cells, colWidths=[width] * column_count, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), SKY),
                        ("TEXTCOLOR", (0, 0), (-1, 0), DEEP_BLUE),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.append(KeepTogether([table, Spacer(1, 6)]))
            continue

        flush_bullets()
        paragraph_lines = [line]
        index += 1
        while (
            index < len(lines)
            and lines[index].strip()
            and not lines[index].startswith(("#", "-", "```", "|"))
            and not re.match(r"^\d+\. ", lines[index])
        ):
            paragraph_lines.append(lines[index].strip())
            index += 1
        story.append(
            Paragraph(escape(" ".join(paragraph_lines)), style["body"])
        )

    flush_bullets()
    return story


def build_pdf(
    source: Path,
    output: Path,
    title: str,
    subtitle: str,
    section_label: str,
) -> None:
    markdown = source.read_text(encoding="utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = document(output, section_label)
    doc.build(markdown_story(markdown, title, subtitle))
    print(f"created: {output}")


def main() -> None:
    build_pdf(
        ROOT / "docs/DATA_AND_METHODS_GUIDE.md",
        PUBLICATIONS / "AI_Business_Intelligence_Lab_Data_and_Methods_Guide.pdf",
        "Data and Methods Guide",
        "A plain-language explanation of the evidence behind the first five reports",
        "DATA AND METHODS",
    )
    build_pdf(
        ROOT / "docs/TECHNICAL_REPRODUCIBILITY_APPENDIX.md",
        PUBLICATIONS
        / "AI_Business_Intelligence_Lab_Technical_Reproducibility_Appendix.pdf",
        "Technical Reproducibility Appendix",
        "Source controls, code structure, validation rules and rerun instructions",
        "TECHNICAL APPENDIX",
    )


if __name__ == "__main__":
    main()
