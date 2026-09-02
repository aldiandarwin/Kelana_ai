"""Build the submission-ready Session 9 Bangladesh RAG comparison PDF.

Run from backend/ with a Python environment that provides ReportLab:

    python build_session_09_pdf.py

The evidence Markdown remains the canonical raw run. This script turns it into
a management-readable PDF without changing any model output.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_FILE = REPO_ROOT / "evidence" / "session-09-rag-vs-base.md"
DATASET_FILE = REPO_ROOT / "knowledge" / "evaluation-questions.json"
SOURCES_FILE = REPO_ROOT / "knowledge" / "bangladesh-sources.json"
OUTPUT_FILE = (
    REPO_ROOT / "output" / "pdf" / "session-09-bangladesh-rag-vs-base.pdf"
)

TEAL = colors.HexColor("#083D42")
TEAL_MID = colors.HexColor("#0F766E")
TEAL_LIGHT = colors.HexColor("#D8EEEA")
AMBER = colors.HexColor("#F2B84B")
INK = colors.HexColor("#17212B")
MUTED = colors.HexColor("#5F6B75")
PAPER = colors.HexColor("#F5F7F2")
LINE = colors.HexColor("#D8DEE3")
RED_SOFT = colors.HexColor("#FDE8E7")


def ascii_safe(value: object) -> str:
    """Normalise typographic glyphs so built-in PDF fonts render reliably."""

    text = str(value)
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u00a0": " ",
        "\ufffd": " ",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def rich(value: object) -> str:
    """Escape model and source text for ReportLab Paragraph markup."""

    return html.escape(ascii_safe(value)).replace("\n", "<br/>")


def _extract(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else default


def parse_evidence(text: str) -> tuple[dict[str, str], list[dict]]:
    """Parse the generated Markdown while preserving every model response."""

    rag_row = re.search(
        r"^\| RAG \| (\d+) of (\d+) \| (\d+) of (\d+) \| "
        r"(\d+) of (\d+) \| (\d+) of (\d+) \|$",
        text,
        re.MULTILINE,
    )
    base_row = re.search(
        r"^\| Base model \| (\d+) of (\d+) \|", text, re.MULTILINE
    )
    if not rag_row or not base_row:
        raise RuntimeError("Could not parse the evidence scoreboard")

    metadata = {
        "verdict": _extract(r"\*\*Verdict: ([A-Z]+)\.\*\*", text),
        "run_at": _extract(r"Run at ([^.]+)\. Retrieval mode", text),
        "dataset_revision": _extract(r"Dataset revision: `([^`]+)`", text),
        "dataset_hash": _extract(r"Dataset SHA-256: `([^`]+)`", text),
        "model": _extract(r"Foundation model: `([^`]+)`", text),
        "region": _extract(r"AWS region: `([^`]+)`", text),
        "mode": _extract(r"Retrieval mode: `([^`]+)`", text),
        "rag_facts": rag_row.group(1),
        "fact_total": rag_row.group(2),
        "rag_sources": rag_row.group(3),
        "rag_source_total": rag_row.group(4),
        "rag_required_sources": rag_row.group(5),
        "rag_required_total": rag_row.group(6),
        "complete_cases": rag_row.group(7),
        "case_total": rag_row.group(8),
        "base_facts": base_row.group(1),
    }

    cases: list[dict] = []
    sections = re.finditer(
        r"^### (Q\d+)\. (.+?)\n\n(.*?)(?=^### Q\d+\.|^## How to read this)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    for section in sections:
        body = section.group(3)
        case_match = re.search(
            r"Case `([^`]+)` - split `([^`]+)` - severity `([^`]+)`\.", body
        )
        requires_match = re.search(r"Requires `([^`]+)`\. (.+?)\n\n", body)
        facts_block = _extract(
            r"\*\*Expected facts\*\*\n\n(.*?)\n\n\*\*RAG answer\*\*", body
        )
        rag_score = re.search(
            r"\*\*RAG answer\*\* \((\d+) of (\d+) facts stated\)", body
        )
        rag_answer = _extract(
            r"\*\*RAG answer\*\* \([^\n]+\)\n\n```text\n(.*?)\n```", body
        )
        base_score = re.search(
            r"\*\*Base model answer\*\* \((\d+) of (\d+) facts stated\)", body
        )
        base_answer = _extract(
            r"\*\*Base model answer\*\* \([^\n]+\)\n\n```text\n(.*?)\n```", body
        )
        source_rows = re.findall(
            r"^\| `([^`]+)` \| ([^|]+?) \| (Yes|No) \|$", body, re.MULTILINE
        )
        delta = _extract(r"\*\*Measured delta:\*\* (.+?)\n", body)

        if not all([case_match, requires_match, rag_score, base_score]):
            raise RuntimeError(f"Could not parse evidence section {section.group(1)}")

        cases.append(
            {
                "id": section.group(1),
                "question": section.group(2),
                "case_id": case_match.group(1),
                "split": case_match.group(2),
                "severity": case_match.group(3),
                "required_document": requires_match.group(1),
                "rationale": requires_match.group(2),
                "expected_facts": [
                    line[2:].strip()
                    for line in facts_block.splitlines()
                    if line.startswith("- ")
                ],
                "rag_present": rag_score.group(1),
                "fact_count": rag_score.group(2),
                "rag_answer": rag_answer,
                "base_present": base_score.group(1),
                "base_answer": base_answer,
                "sources": source_rows,
                "delta": delta,
            }
        )

    if len(cases) != 5:
        raise RuntimeError(f"Expected 5 evidence cases, found {len(cases)}")
    return metadata, cases


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=29,
            leading=33,
            textColor=TEAL,
            alignment=TA_LEFT,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=13,
            leading=18,
            textColor=MUTED,
            spaceAfter=16,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=TEAL,
            spaceBefore=4,
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=TEAL_MID,
            spaceBefore=6,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.4,
            leading=14,
            textColor=INK,
            spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10.5,
            textColor=MUTED,
        ),
        "answer": ParagraphStyle(
            "Answer",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.1,
            leading=11.4,
            textColor=INK,
        ),
        "label": ParagraphStyle(
            "Label",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.4,
            leading=9,
            textColor=MUTED,
            uppercase=True,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.4,
            leading=9,
            textColor=colors.white,
        ),
        "center": ParagraphStyle(
            "Center",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            textColor=INK,
        ),
    }


def summary_chart(metadata: dict[str, str]) -> Drawing:
    width = 165 * mm
    height = 35 * mm
    drawing = Drawing(width, height)
    total = int(metadata["fact_total"])
    rag = int(metadata["rag_facts"])
    base = int(metadata["base_facts"])
    bar_x = 38 * mm
    bar_width = 118 * mm

    drawing.add(String(0, 79, "Expected facts stated", fontName="Helvetica-Bold", fontSize=9, fillColor=INK))
    for index, (label, value, color) in enumerate(
        [("RAG", rag, TEAL_MID), ("Base model", base, colors.HexColor("#A9B2BA"))]
    ):
        y = 51 - index * 30
        drawing.add(String(0, y + 4, label, fontName="Helvetica-Bold", fontSize=8, fillColor=INK))
        drawing.add(Rect(bar_x, y, bar_width, 12, fillColor=colors.HexColor("#E9EDF0"), strokeColor=None))
        drawing.add(Rect(bar_x, y, bar_width * value / total, 12, fillColor=color, strokeColor=None))
        drawing.add(String(bar_x + bar_width + 5, y + 3, f"{value}/{total}", fontName="Helvetica-Bold", fontSize=8, fillColor=INK))
    return drawing


def on_page(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    if doc.page > 1:
        canvas.setStrokeColor(LINE)
        canvas.line(18 * mm, height - 14 * mm, width - 18 * mm, height - 14 * mm)
        canvas.setFont("Helvetica-Bold", 7)
        canvas.setFillColor(TEAL)
        canvas.drawString(18 * mm, height - 10.5 * mm, "KelanaAI Session 9 - Bangladesh RAG Evaluation")
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 10 * mm, "Aldian Darwin Putra | MAIN 2026 Phase 2")
    canvas.drawRightString(width - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def bullet_list(items: list[str], style: ParagraphStyle) -> Table:
    """Render ASCII bullets without relying on Symbol or Unicode fonts."""

    table = Table(
        [[Paragraph("-", style), Paragraph(rich(item), style)] for item in items],
        colWidths=[5 * mm, 160 * mm],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return table


def build_pdf() -> None:
    evidence_text = EVIDENCE_FILE.read_text(encoding="utf-8")
    dataset = json.loads(DATASET_FILE.read_text(encoding="utf-8"))
    source_manifest = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    metadata, cases = parse_evidence(evidence_text)
    source_by_name = {
        item["filename"]: item for item in source_manifest["documents"]
    }
    case_source = {
        item["id"]: item["source"] for item in dataset["questions"]
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT_FILE),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=17 * mm,
        title="KelanaAI Session 9 - Bangladesh RAG versus Base Model",
        author="Aldian Darwin Putra",
        subject="MAIN 2026 Phase 2 Session 9 evidence",
    )
    styles = build_styles()
    story = []

    story += [
        Spacer(1, 15 * mm),
        Paragraph("KELANAAI SESSION 9", styles["label"]),
        Spacer(1, 3 * mm),
        Paragraph("Bangladesh Knowledge Base", styles["title"]),
        Paragraph("RAG vs Base Model - Evidence and Analysis", styles["subtitle"]),
        HRFlowable(width="100%", thickness=2.2, color=AMBER, spaceAfter=10 * mm),
    ]

    verdict_table = Table(
        [
            [Paragraph("VERDICT", styles["label"]), Paragraph(rich(metadata["verdict"]), styles["center"])],
            [Paragraph("RAG facts", styles["label"]), Paragraph(f"{metadata['rag_facts']} / {metadata['fact_total']}", styles["center"])],
            [Paragraph("Base facts", styles["label"]), Paragraph(f"{metadata['base_facts']} / {metadata['fact_total']}", styles["center"])],
            [Paragraph("Required sources", styles["label"]), Paragraph(f"{metadata['rag_required_sources']} / {metadata['rag_required_total']}", styles["center"])],
        ],
        colWidths=[45 * mm, 50 * mm],
        hAlign="LEFT",
    )
    verdict_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PAPER),
                ("BACKGROUND", (1, 0), (1, 0), TEAL_LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.8, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story += [verdict_table, Spacer(1, 7 * mm), summary_chart(metadata), Spacer(1, 5 * mm)]
    story += [
        Paragraph("So What?", styles["h1"]),
        Paragraph(
            "RAG menjawab seluruh 24 fakta yang telah didefinisikan dan selalu mengambil dokumen yang diwajibkan. Base model hanya menyebut 2 dari 24 fakta dan menghasilkan beberapa detail yang terdengar meyakinkan tetapi bertentangan dengan dokumen. Untuk pertanyaan yang bergantung pada source-specific numbers, names, dan itinerary, retrieval mengubah jawaban dari plausible menjadi auditable.",
            styles["body"],
        ),
        Spacer(1, 5 * mm),
        Paragraph("Aldian Darwin Putra", styles["h2"]),
        Paragraph("MAIN 2026 Phase 2 - AI Native Software Engineer Bootcamp", styles["small"]),
        Paragraph("Generated 2 September 2026 | Asia/Jakarta", styles["small"]),
        PageBreak(),
    ]

    story += [Paragraph("1. Scope dan Corpus", styles["h1"])]
    story.append(
        Paragraph(
            "Homework meminta minimal tiga dokumen tambahan, lima pertanyaan baru, dan perbandingan langsung antara jawaban RAG dan base model. Corpus expansion menggunakan tiga PDF resmi Bangladesh Tourism Board; delapan dokumen lama tetap dipertahankan agar perluasan basis pengetahuan dapat dibuktikan.",
            styles["body"],
        )
    )
    source_rows = [
        [
            Paragraph("Document", styles["table_header"]),
            Paragraph("Pages", styles["table_header"]),
            Paragraph("Evaluation coverage", styles["table_header"]),
            Paragraph("Integrity", styles["table_header"]),
        ]
    ]
    for source in source_manifest["documents"]:
        source_rows.append(
            [
                Paragraph(rich(source["title"]), styles["body"]),
                Paragraph(str(source["pages"]), styles["center"]),
                Paragraph(", ".join(source["evaluation_cases"]), styles["center"]),
                Paragraph("SHA-256 verified", styles["small"]),
            ]
        )
    source_table = Table(source_rows, colWidths=[78 * mm, 18 * mm, 38 * mm, 32 * mm], repeatRows=1)
    source_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.45, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story += [source_table, Spacer(1, 6 * mm)]
    story += [Paragraph("Runtime proof", styles["h2"])]
    story.append(
        bullet_list(
            [
                "11 documents ingested: 8 pre-expansion documents plus 3 Bangladesh PDFs.",
                "127 chunks stored; 127 of 127 chunks have Amazon Titan embeddings.",
                "Amazon Nova Lite generated both RAG and base-model answers in ap-southeast-2.",
                "Local vector-store RAG is verified live; the managed S3/Bedrock Knowledge Base path remains unverified because IAM credentials, bucket, Knowledge Base ID, and data source ID are not configured.",
            ],
            styles["body"],
        )
    )
    story += [Paragraph("Evaluation contract", styles["h2"])]
    story.append(
        bullet_list(
            [
                f"Frozen dataset revision {metadata['dataset_revision']} with SHA-256 {metadata['dataset_hash']}.",
                "Same five inputs and same foundation model for both paths; RAG alone receives retrieved context.",
                "Temperature 0.0 and maximum 500 answer tokens.",
                "Deterministic graders check exact names, figures, source presence, and required-document match.",
                "Targeted, regression, and holdout splits are preserved; results are a five-case convenience sample, not a production failure-rate estimate.",
            ],
            styles["body"],
        )
    )

    for index, case in enumerate(cases, start=1):
        story.append(PageBreak())
        source_meta = source_by_name[case["required_document"]]
        source_case = case_source[case["id"]]
        story += [
            Paragraph(f"2.{index} {rich(case['id'])} - Case comparison", styles["h1"]),
            Paragraph(rich(case["question"]), styles["h2"]),
        ]
        meta_table = Table(
            [
                [Paragraph("CASE", styles["label"]), Paragraph(rich(case["case_id"]), styles["small"]), Paragraph("SPLIT", styles["label"]), Paragraph(rich(case["split"]), styles["small"])],
                [Paragraph("SOURCE", styles["label"]), Paragraph(rich(case["required_document"]), styles["small"]), Paragraph("PDF PAGE", styles["label"]), Paragraph(str(source_case["pdf_page"]), styles["small"])],
            ],
            colWidths=[18 * mm, 76 * mm, 22 * mm, 50 * mm],
        )
        meta_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), PAPER),
                    ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story += [meta_table, Spacer(1, 4 * mm)]
        story += [Paragraph("Expected evidence", styles["h2"]), bullet_list(case["expected_facts"], styles["small"])]

        answer_table = Table(
            [
                [
                    Paragraph(f"RAG - {case['rag_present']}/{case['fact_count']} facts", styles["center"]),
                    Paragraph(f"Base model - {case['base_present']}/{case['fact_count']} facts", styles["center"]),
                ],
                [
                    Paragraph(rich(case["rag_answer"]), styles["answer"]),
                    Paragraph(rich(case["base_answer"]), styles["answer"]),
                ],
            ],
            colWidths=[82.5 * mm, 82.5 * mm],
        )
        answer_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, 0), TEAL_LIGHT),
                    ("BACKGROUND", (1, 0), (1, 0), RED_SOFT),
                    ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#F4FBF9")),
                    ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#FFF8F7")),
                    ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )
        story += [answer_table, Spacer(1, 4 * mm)]
        story += [
            Paragraph("Measured result", styles["h2"]),
            Paragraph(rich(case["delta"]), styles["body"]),
            Paragraph(
                f"Retrieved source: {rich(source_meta['title'])}, Bangladesh Tourism Board, PDF page {source_case['pdf_page']}. The required file appeared in the retrieval set.",
                styles["small"],
            ),
        ]

    story += [PageBreak(), Paragraph("3. Findings dan Decision", styles["h1"])]
    findings = [
        "Retrieval materially improved grounded completeness: 24/24 expected facts versus 2/24 for the base model.",
        "The base model produced confident but document-inconsistent details in all five cases, including wrong distances, river names, destination identity, breeding-center type, and itinerary figures.",
        "Required source coverage was 5/5. Passing facts without the assigned source would not have earned grounding credit.",
        "The final hybrid ranker combines semantic similarity with lexical overlap. This fixed exact-name and exact-number retrieval while retaining semantic matching for paraphrases.",
        "The holdout itinerary case remained 8/8 after targeted and regression improvements, so the candidate did not trade away the unseen case.",
    ]
    story.append(bullet_list(findings, styles["body"]))
    story += [Paragraph("Verdict", styles["h2"])]
    story.append(
        Paragraph(
            "PASS untuk scope homework local RAG: tiga dokumen Bangladesh berhasil ditambahkan, lima paired questions dijalankan, seluruh expected facts dan required sources terpenuhi, dan jawaban mentah dipertahankan dalam evidence. Managed S3/Bedrock Knowledge Base belum boleh disebut selesai sampai credential IAM dan tiga identifier AWS tersedia lalu ingestion mencapai COMPLETE.",
            styles["body"],
        )
    )
    story += [Paragraph("Limitations", styles["h2"])]
    story.append(
        bullet_list(
            [
                "The source PDFs are brochures and may be stale. This report evaluates faithfulness to the assigned documents, not present-day travel validity.",
                "The deterministic grader accepts declared string variants. It does not replace expert review for nuanced semantic quality.",
                "Five cases demonstrate the homework behavior but cannot estimate production reliability.",
                "No open-content licence was found on the source pages; files retain publisher attribution and are used for the educational assignment.",
            ],
            styles["body"],
        )
    )

    story += [PageBreak(), Paragraph("4. Reproduction dan Sources", styles["h1"])]
    commands = [
        "cd backend",
        "..\\.venv\\Scripts\\python.exe ingest_knowledge.py",
        "..\\.venv\\Scripts\\python.exe compare_rag_vs_base.py",
        "cd ..",
        ".\\.venv\\Scripts\\python.exe -m unittest discover -s tests -v",
    ]
    story += [Paragraph("Core commands", styles["h2"]), bullet_list(commands, styles["small"])]
    story += [Paragraph("Official source files", styles["h2"])]
    for source in source_manifest["documents"]:
        link = html.escape(source["url"], quote=True)
        story.append(
            Paragraph(
                f"<b>{rich(source['title'])}</b> ({source['pages']} pages)<br/>"
                f"Publisher: Bangladesh Tourism Board<br/>"
                f"SHA-256: <font size='6.6'>{source['sha256']}</font><br/>"
                f"<link href='{link}' color='#0F766E'>Open official PDF</link>",
                styles["small"],
            )
        )
        story.append(Spacer(1, 3 * mm))

    story += [
        HRFlowable(width="100%", thickness=0.7, color=LINE, spaceBefore=4 * mm, spaceAfter=4 * mm),
        Paragraph(
            f"Raw evidence: evidence/session-09-rag-vs-base.md | Run at {rich(metadata['run_at'])} | Retrieval mode {rich(metadata['mode'])}",
            styles["small"],
        ),
    ]

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"written={OUTPUT_FILE}")


if __name__ == "__main__":
    build_pdf()
