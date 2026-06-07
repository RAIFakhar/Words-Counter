"""
utils/export_utils.py
───────────────────────────────────────────────────────────────
ExportUtils — serialise an analysis result to several formats.

Available formats:
  to_json(text, analysis) -> bytes   (UTF-8 JSON)
  to_txt(text, analysis)  -> bytes   (UTF-8 plain-text report)
  to_pdf(text, analysis)  -> bytes   (PDF via ReportLab)
"""
from __future__ import annotations

import io
import json
from datetime import datetime


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _fmt(seconds: int) -> str:
    """Compact human-readable duration (avoids importing TextAnalyzer)."""
    if seconds <= 0:
        return "0s"
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s}s" if s else f"{m}m"
    h, rem = divmod(seconds, 3600)
    m, s   = divmod(rem, 60)
    return f"{h}h {m}m" if m else f"{h}h"


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ─── ExportUtils ─────────────────────────────────────────────────────────────

class ExportUtils:

    # ── JSON ──────────────────────────────────────────────────────────────────

    @staticmethod
    def to_json(text: str, analysis: dict) -> bytes:
        """Serialise full analysis to indented JSON bytes."""
        basic      = analysis.get("basic", {})
        time_data  = analysis.get("time", {})
        readability = analysis.get("readability", {})
        advanced   = analysis.get("advanced", {})
        keywords   = analysis.get("keywords", [])

        payload = {
            "metadata": {
                "tool":      "TextLens v1.0",
                "generated": _now(),
                "text_preview": (text[:500] + "…") if len(text) > 500 else text,
            },
            "basic_metrics": {
                "words":                     basic.get("words", 0),
                "unique_words":              basic.get("unique_words", 0),
                "characters_with_spaces":    basic.get("characters_with_spaces", 0),
                "characters_no_spaces":      basic.get("characters_without_spaces", 0),
                "sentences":                 basic.get("sentences", 0),
                "paragraphs":                basic.get("paragraphs", 0),
            },
            "time_estimates": {
                "reading_time":  _fmt(time_data.get("reading_seconds", 0)),
                "speaking_time": _fmt(time_data.get("speaking_seconds", 0)),
                "reading_seconds_raw":  time_data.get("reading_seconds", 0),
                "speaking_seconds_raw": time_data.get("speaking_seconds", 0),
            },
            "readability": {
                "flesch_reading_ease": readability.get("fre_score", 0.0),
                "flesch_kincaid_grade": readability.get("fk_grade", 0.0),
                "difficulty_label": readability.get("label", "N/A"),
            },
            "advanced_metrics": {
                "avg_word_length_chars":   advanced.get("avg_word_length", 0.0),
                "avg_sentence_length_words": advanced.get("avg_sentence_length", 0.0),
                "longest_word":            advanced.get("longest_word", ""),
                "longest_sentence_words":  advanced.get("longest_sentence_words", 0),
                "lexical_diversity_pct":   advanced.get("lexical_diversity", 0.0),
            },
            "top_keywords": [
                {"rank": i + 1, **kw}
                for i, kw in enumerate(keywords[:10])
            ],
        }
        return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")

    # ── Plain-Text ────────────────────────────────────────────────────────────

    @staticmethod
    def to_txt(text: str, analysis: dict) -> bytes:
        """Generate a formatted plain-text analytics report."""
        basic       = analysis.get("basic", {})
        time_data   = analysis.get("time", {})
        readability = analysis.get("readability", {})
        advanced    = analysis.get("advanced", {})
        keywords    = analysis.get("keywords", [])

        SEP  = "═" * 62
        THIN = "─" * 62

        lines = [
            SEP,
            "  TEXTLENS  ·  COMPREHENSIVE TEXT ANALYSIS REPORT",
            f"  Generated : {_now()}",
            SEP,
            "",
            "  📊  BASIC METRICS",
            THIN,
            f"  {'Words':<32}  {basic.get('words', 0):>10,}",
            f"  {'Unique Words':<32}  {basic.get('unique_words', 0):>10,}",
            f"  {'Characters (with spaces)':<32}  {basic.get('characters_with_spaces', 0):>10,}",
            f"  {'Characters (no spaces)':<32}  {basic.get('characters_without_spaces', 0):>10,}",
            f"  {'Sentences':<32}  {basic.get('sentences', 0):>10,}",
            f"  {'Paragraphs':<32}  {basic.get('paragraphs', 0):>10,}",
            "",
            "  ⏱   TIME ESTIMATES",
            THIN,
            f"  {'Reading Time  (200 WPM)':<32}  {_fmt(time_data.get('reading_seconds', 0)):>10}",
            f"  {'Speaking Time (130 WPM)':<32}  {_fmt(time_data.get('speaking_seconds', 0)):>10}",
            "",
            "  📖  READABILITY",
            THIN,
            f"  {'Flesch Reading Ease':<32}  {readability.get('fre_score', 0.0):>9.1f}",
            f"  {'Flesch-Kincaid Grade':<32}  {'Grade ' + str(readability.get('fk_grade', 0.0)):>10}",
            f"  {'Difficulty':<32}  {readability.get('label', 'N/A'):>10}",
            "",
            "  🧠  ADVANCED METRICS",
            THIN,
            f"  {'Avg Word Length':<32}  {str(advanced.get('avg_word_length', 0)) + ' chars':>10}",
            f"  {'Avg Sentence Length':<32}  {str(advanced.get('avg_sentence_length', 0)) + ' words':>10}",
            f"  {'Longest Word':<32}  {advanced.get('longest_word', 'N/A'):>10}",
            f"  {'Longest Sentence':<32}  {str(advanced.get('longest_sentence_words', 0)) + ' words':>10}",
            f"  {'Lexical Diversity':<32}  {str(advanced.get('lexical_diversity', 0)) + '%':>10}",
            "",
            "  🔑  TOP KEYWORDS",
            THIN,
            f"  {'#':<4}  {'Word':<22}  {'Count':>6}  {'Density':>8}",
            THIN,
        ]

        for i, kw in enumerate(keywords[:10], 1):
            bar = "█" * int(kw["density"] * 5)
            lines.append(
                f"  {i:<4}  {kw['word']:<22}  {kw['count']:>6,}  {kw['density']:>7.2f}%  {bar}"
            )

        lines += [
            "",
            SEP,
            "  TEXT PREVIEW (first 600 chars)",
            THIN,
            *["  " + line for line in (text[:600] + ("…" if len(text) > 600 else "")).splitlines()],
            SEP,
            "",
        ]

        return "\n".join(lines).encode("utf-8")

    # ── PDF ───────────────────────────────────────────────────────────────────

    @staticmethod
    def to_pdf(text: str, analysis: dict) -> bytes:
        """
        Generate a styled PDF report using ReportLab.
        Raises ImportError if reportlab is not installed.
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.lib.enums import TA_LEFT, TA_RIGHT
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table,
            TableStyle, HRFlowable,
        )

        basic       = analysis.get("basic", {})
        time_data   = analysis.get("time", {})
        readability = analysis.get("readability", {})
        advanced    = analysis.get("advanced", {})
        keywords    = analysis.get("keywords", [])

        INDIGO  = colors.HexColor("#6366f1")
        SLATE_D = colors.HexColor("#1e293b")
        SLATE_M = colors.HexColor("#475569")
        SLATE_L = colors.HexColor("#64748b")
        WHITE   = colors.white
        BG      = colors.HexColor("#f8fafc")
        BG_ALT  = colors.HexColor("#ffffff")
        BORDER  = colors.HexColor("#e2e8f0")

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=1.8 * cm,
            rightMargin=1.8 * cm,
            topMargin=1.8 * cm,
            bottomMargin=1.8 * cm,
        )
        styles = getSampleStyleSheet()

        def _style(name, parent="Normal", **kw):
            return ParagraphStyle(name, parent=styles[parent], **kw)

        H1 = _style("H1", "Title",
                    fontSize=20, fontName="Helvetica-Bold",
                    textColor=SLATE_D, spaceAfter=2)
        SUB = _style("SUB", fontSize=9, fontName="Helvetica",
                     textColor=SLATE_L, spaceAfter=14)
        SEC = _style("SEC", "Heading2",
                     fontSize=11, fontName="Helvetica-Bold",
                     textColor=INDIGO, spaceBefore=12, spaceAfter=6)
        BODY = _style("BODY", fontSize=9, fontName="Helvetica",
                      textColor=SLATE_M, spaceAfter=3)
        PREVIEW = _style("PREVIEW", fontSize=8, fontName="Courier",
                         textColor=SLATE_M, spaceAfter=0, leading=12)

        def _table(data, col_widths, header_row=True):
            t = Table(data, colWidths=col_widths)
            style = [
                ("FONTSIZE",    (0, 0), (-1, -1), 9),
                ("FONTNAME",    (0, 0), (-1, -1), "Helvetica"),
                ("ALIGN",       (1, 0), (-1, -1), "RIGHT"),
                ("ALIGN",       (0, 0), (0, -1),  "LEFT"),
                ("GRID",        (0, 0), (-1, -1), 0.4, BORDER),
                ("PADDING",     (0, 0), (-1, -1), 6),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BG_ALT, BG]),
            ]
            if header_row:
                style += [
                    ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
                    ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
                    ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            t.setStyle(TableStyle(style))
            return t

        W = doc.width

        story = [
            Paragraph("🔍 TextLens Analysis Report", H1),
            Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", SUB),
            HRFlowable(width="100%", thickness=1.5, color=INDIGO),
            Spacer(1, 10),

            Paragraph("📊 Basic Metrics", SEC),
            _table([
                ["Metric", "Value"],
                ["Total Words",             f"{basic.get('words', 0):,}"],
                ["Unique Words",            f"{basic.get('unique_words', 0):,}"],
                ["Characters (with spaces)", f"{basic.get('characters_with_spaces', 0):,}"],
                ["Characters (no spaces)",  f"{basic.get('characters_without_spaces', 0):,}"],
                ["Sentences",               f"{basic.get('sentences', 0):,}"],
                ["Paragraphs",              f"{basic.get('paragraphs', 0):,}"],
            ], [W * 0.65, W * 0.35]),
            Spacer(1, 6),

            Paragraph("⏱  Time Estimates", SEC),
            _table([
                ["Metric", "Estimate"],
                ["Reading Time  (200 WPM)", _fmt(time_data.get("reading_seconds", 0))],
                ["Speaking Time (130 WPM)", _fmt(time_data.get("speaking_seconds", 0))],
            ], [W * 0.65, W * 0.35]),
            Spacer(1, 6),

            Paragraph("📖 Readability", SEC),
            _table([
                ["Metric", "Score"],
                ["Flesch Reading Ease",    f"{readability.get('fre_score', 0.0):.1f} / 100"],
                ["Flesch-Kincaid Grade",   f"Grade {readability.get('fk_grade', 0.0):.1f}"],
                ["Difficulty Level",       readability.get("label", "N/A")],
            ], [W * 0.65, W * 0.35]),
            Spacer(1, 6),

            Paragraph("🧠 Advanced Metrics", SEC),
            _table([
                ["Metric", "Value"],
                ["Avg Word Length",      f"{advanced.get('avg_word_length', 0):.1f} chars"],
                ["Avg Sentence Length",  f"{advanced.get('avg_sentence_length', 0):.1f} words"],
                ["Longest Word",         advanced.get("longest_word", "N/A")],
                ["Longest Sentence",     f"{advanced.get('longest_sentence_words', 0)} words"],
                ["Lexical Diversity",    f"{advanced.get('lexical_diversity', 0):.1f}%"],
            ], [W * 0.65, W * 0.35]),
        ]

        if keywords:
            story += [
                Spacer(1, 6),
                Paragraph("🔑 Top Keywords", SEC),
                _table(
                    [["#", "Keyword", "Count", "Density"]]
                    + [[str(i + 1), kw["word"], str(kw["count"]), f"{kw['density']:.2f}%"]
                       for i, kw in enumerate(keywords[:10])],
                    [W * 0.08, W * 0.52, W * 0.2, W * 0.2],
                ),
            ]

        # Text preview
        preview_text = (text[:700] + "…") if len(text) > 700 else text
        preview_text = preview_text.replace("&", "&amp;").replace("<", "&lt;")
        story += [
            Spacer(1, 10),
            HRFlowable(width="100%", thickness=0.5, color=BORDER),
            Spacer(1, 6),
            Paragraph("Text Preview", SEC),
            Paragraph(preview_text, PREVIEW),
        ]

        doc.build(story)
        buf.seek(0)
        return buf.getvalue()
