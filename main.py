"""
main.py
───────────────────────────────────────────────────────────────
TextLens — Professional Text Analyzer
Entry point: run with  `streamlit run main.py`

Architecture:
    main.py          ← you are here  (UI orchestration + state)
    core/            ← NLP engine (text_analyzer, readability)
    utils/           ← file parser + export formatters
"""
from __future__ import annotations

import os
import sys

# Ensure project root is on the path before local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import io
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from core.text_analyzer import TextAnalyzer
from utils.file_parser import FileParser
from utils.export_utils import ExportUtils


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="TextLens – Text Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "**TextLens** · Professional Text Analytics Engine · v1.0",
    },
)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

def _init_state() -> None:
    defaults = {
        "dark_mode":    True,
        "text_content": "",
        "analysis":     None,
        "reading_wpm":  200,
        "speaking_wpm": 130,
        "file_name":    None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()


# ═══════════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════════

def _css() -> None:
    dm = st.session_state.dark_mode

    # ── palette ───────────────────────────────────────────────────────────────
    if dm:
        bg_app     = "#0d0d18"
        bg_sidebar = "#0f0f1e"
        bg_card    = "#16162a"
        bg_card2   = "#1c1c32"
        bg_input   = "#111122"
        bd         = "#2a2a45"
        tx_p       = "#e2e8f0"
        tx_s       = "#94a3b8"
        tx_d       = "#64748b"
        accent     = "#6366f1"
        accent_l   = "#818cf8"
        badge_bg   = "#1e1e35"
        hover      = "#1e1e36"
        shadow     = "rgba(99,102,241,0.18)"
    else:
        bg_app     = "#f0f4ff"
        bg_sidebar = "#e8ecf8"
        bg_card    = "#ffffff"
        bg_card2   = "#f8f9ff"
        bg_input   = "#ffffff"
        bd         = "#d4d8f0"
        tx_p       = "#1e293b"
        tx_s       = "#475569"
        tx_d       = "#94a3b8"
        accent     = "#6366f1"
        accent_l   = "#4f46e5"
        badge_bg   = "#e0e7ff"
        hover      = "#eef0fe"
        shadow     = "rgba(99,102,241,0.12)"

    st.markdown(f"""
<style>
/* ── Google Font ────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── App shell ──────────────────────────────────────────────────────────── */
html, body, [class*="css"] {{
    font-family: 'DM Sans', -apple-system, sans-serif !important;
}}
.stApp {{
    background: {bg_app};
    color: {tx_p};
}}
section[data-testid="stSidebar"] > div:first-child {{
    background: {bg_sidebar};
    border-right: 1px solid {bd};
    padding-top: 1.2rem;
}}

/* ── Hide Streamlit chrome ──────────────────────────────────────────────── */
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ display: none; }}

/* ── App header ─────────────────────────────────────────────────────────── */
.tl-header {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding-bottom: 20px;
    border-bottom: 1px solid {bd};
    margin-bottom: 22px;
}}
.tl-logo {{
    width: 46px; height: 46px;
    background: linear-gradient(135deg, {accent} 0%, #a855f7 100%);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; flex-shrink: 0;
    box-shadow: 0 4px 14px {shadow};
}}
.tl-header h1 {{
    margin: 0; font-size: 22px; font-weight: 700;
    color: {tx_p}; letter-spacing: -0.4px;
}}
.tl-header p {{
    margin: 0; font-size: 12px; color: {tx_s};
}}
.tl-badge {{
    margin-left: auto;
    padding: 4px 10px;
    background: {badge_bg};
    border: 1px solid {bd};
    border-radius: 20px;
    font-size: 11px; font-weight: 500;
    color: {accent_l};
    white-space: nowrap;
}}

/* ── Metric cards ───────────────────────────────────────────────────────── */
.tl-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 14px;
}}
.tl-card {{
    background: {bg_card};
    border: 1px solid {bd};
    border-radius: 12px;
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
    transition: transform .15s, box-shadow .15s;
    cursor: default;
}}
.tl-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px {shadow};
    background: {hover};
}}
.tl-card::after {{
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, {accent} 0%, #a855f7 100%);
    border-radius: 3px 0 0 3px;
}}
.tl-card-icon {{
    font-size: 18px; margin-bottom: 6px; display: block;
}}
.tl-card-label {{
    font-size: 10px; font-weight: 600;
    color: {tx_d}; text-transform: uppercase;
    letter-spacing: .9px; margin-bottom: 5px;
}}
.tl-card-value {{
    font-size: 26px; font-weight: 700;
    color: {tx_p}; letter-spacing: -1px;
    line-height: 1;
}}
.tl-card-sub {{
    font-size: 11px; color: {tx_s}; margin-top: 3px;
}}

/* ── Section cards ──────────────────────────────────────────────────────── */
.tl-section {{
    background: {bg_card};
    border: 1px solid {bd};
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 12px;
}}
.tl-section-title {{
    font-size: 11px; font-weight: 600;
    color: {tx_d}; text-transform: uppercase;
    letter-spacing: .9px; margin-bottom: 14px;
    display: flex; align-items: center; gap: 7px;
}}
.tl-section-title span {{
    display: inline-block;
    width: 3px; height: 12px;
    background: linear-gradient(180deg, {accent}, #a855f7);
    border-radius: 2px;
}}

/* ── Readability block ──────────────────────────────────────────────────── */
.tl-read {{
    display: flex; align-items: center; gap: 16px;
}}
.tl-read-circle {{
    width: 68px; height: 68px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; font-weight: 800; color: #fff;
    flex-shrink: 0;
    box-shadow: 0 4px 14px rgba(0,0,0,.25);
}}
.tl-read-meta h3 {{
    margin: 0 0 4px; font-size: 16px; font-weight: 700; color: {tx_p};
}}
.tl-read-meta p {{
    margin: 0 0 2px; font-size: 12px; color: {tx_s};
}}

/* ── Keyword rows ───────────────────────────────────────────────────────── */
.tl-kw {{
    display: flex; align-items: center; gap: 8px;
    padding: 7px 0;
    border-bottom: 1px solid {bd};
}}
.tl-kw:last-child {{ border-bottom: none; }}
.tl-kw-rank {{
    width: 18px; text-align: center;
    font-size: 10px; color: {tx_d};
    font-weight: 600; flex-shrink: 0;
}}
.tl-kw-word {{
    min-width: 90px; font-size: 13px;
    font-weight: 500; color: {tx_p};
}}
.tl-kw-track {{
    flex: 1; height: 5px; background: {badge_bg};
    border-radius: 3px; overflow: hidden;
}}
.tl-kw-fill {{
    height: 100%; border-radius: 3px;
    background: linear-gradient(90deg, {accent} 0%, #a855f7 100%);
    transition: width .3s ease;
}}
.tl-kw-count {{
    font-size: 12px; font-weight: 600; color: {accent};
    min-width: 28px; text-align: right; flex-shrink: 0;
}}
.tl-kw-pct {{
    font-size: 10px; color: {tx_d};
    min-width: 38px; text-align: right; flex-shrink: 0;
}}

/* ── Advanced rows ──────────────────────────────────────────────────────── */
.tl-adv {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 0; border-bottom: 1px solid {bd};
}}
.tl-adv:last-child {{ border-bottom: none; }}
.tl-adv-label {{ font-size: 13px; color: {tx_s}; }}
.tl-adv-value {{
    font-size: 13px; font-weight: 600; color: {tx_p};
    font-family: 'JetBrains Mono', monospace;
}}

/* ── Toolbar buttons ────────────────────────────────────────────────────── */
.stButton > button {{
    background: {bg_card} !important;
    border: 1px solid {bd} !important;
    color: {tx_p} !important;
    border-radius: 8px !important;
    font-size: 12px !important; font-weight: 500 !important;
    padding: 6px 4px !important;
    transition: all .15s !important;
    font-family: 'DM Sans', sans-serif !important;
}}
.stButton > button:hover {{
    border-color: {accent} !important;
    color: {accent} !important;
    background: {hover} !important;
    box-shadow: 0 0 0 2px {shadow} !important;
}}
.stButton > button:active {{
    transform: scale(.97);
}}

/* ── Download buttons ───────────────────────────────────────────────────── */
[data-testid="stDownloadButton"] button {{
    background: linear-gradient(135deg, {accent} 0%, #7c3aed 100%) !important;
    border: none !important; color: #fff !important;
    border-radius: 8px !important;
    font-size: 12px !important; font-weight: 600 !important;
}}
[data-testid="stDownloadButton"] button:hover {{
    opacity: .9 !important;
    box-shadow: 0 4px 14px {shadow} !important;
}}

/* ── Text area ──────────────────────────────────────────────────────────── */
.stTextArea label {{ display: none; }}
.stTextArea textarea {{
    background: {bg_input} !important;
    color: {tx_p} !important;
    border: 1.5px solid {bd} !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    line-height: 1.75 !important;
    padding: 16px !important;
    font-family: 'DM Sans', sans-serif !important;
    caret-color: {accent} !important;
    resize: vertical !important;
    transition: border-color .15s !important;
}}
.stTextArea textarea:focus {{
    border-color: {accent} !important;
    box-shadow: 0 0 0 3px {shadow} !important;
    outline: none !important;
}}
.stTextArea textarea::placeholder {{ color: {tx_d} !important; }}

/* ── File uploader ──────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] > section {{
    background: {bg_card} !important;
    border: 1.5px dashed {bd} !important;
    border-radius: 10px !important;
}}
[data-testid="stFileUploader"] > section:hover {{
    border-color: {accent} !important;
}}
[data-testid="stFileUploader"] label {{ color: {tx_s} !important; }}

/* ── Tabs ────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: {bg_card} !important;
    border-radius: 10px !important;
    padding: 3px !important;
    border: 1px solid {bd} !important;
    gap: 3px !important;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px !important;
    font-size: 12px !important; font-weight: 500 !important;
    color: {tx_s} !important;
    padding: 5px 14px !important;
}}
.stTabs [aria-selected="true"] {{
    background: {accent} !important;
    color: #fff !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    padding-top: 14px !important;
}}

/* ── Sliders ────────────────────────────────────────────────────────────── */
[data-testid="stSlider"] [role="slider"] {{
    background: {accent} !important; border-color: {accent} !important;
}}
[data-testid="stSlider"] [data-testid="stSliderTrack"] > div:first-child {{
    background: {accent} !important;
}}

/* ── Toggle ─────────────────────────────────────────────────────────────── */
[data-testid="stToggle"] [aria-checked="true"] {{
    background-color: {accent} !important;
}}

/* ── Selectbox / expander ───────────────────────────────────────────────── */
[data-testid="stExpander"] {{
    background: {bg_card} !important;
    border: 1px solid {bd} !important;
    border-radius: 10px !important;
}}

/* ── Scrollbar ──────────────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {bg_app}; }}
::-webkit-scrollbar-thumb {{ background: {bd}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {accent}; }}

/* ── Empty state ────────────────────────────────────────────────────────── */
.tl-empty {{
    text-align: center; padding: 52px 24px;
    background: {bg_card};
    border: 1px solid {bd};
    border-radius: 12px;
}}
.tl-empty-icon {{ font-size: 52px; margin-bottom: 16px; }}
.tl-empty-title {{
    font-size: 16px; font-weight: 600; color: {tx_p}; margin-bottom: 8px;
}}
.tl-empty-sub {{ font-size: 13px; color: {tx_s}; line-height: 1.6; }}

/* ── Sidebar labels ─────────────────────────────────────────────────────── */
[data-testid="stSidebar"] .block-container p,
[data-testid="stSidebar"] label {{
    color: {tx_s} !important; font-size: 12px !important;
}}
[data-testid="stSidebar"] h3 {{
    font-size: 12px !important; color: {tx_d} !important;
    text-transform: uppercase !important; letter-spacing: .8px !important;
    font-weight: 600 !important;
}}

/* ── Divider ────────────────────────────────────────────────────────────── */
hr {{ border-color: {bd} !important; margin: 14px 0 !important; }}

/* ── Alert / info ───────────────────────────────────────────────────────── */
[data-testid="stAlert"] {{
    background: {bg_card2} !important;
    border: 1px solid {bd} !important;
    border-radius: 8px !important;
    font-size: 12px !important;
}}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HTML COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def _card(icon: str, label: str, value: str, sub: str = "") -> str:
    sub_html = f'<div class="tl-card-sub">{sub}</div>' if sub else ""
    return f"""
<div class="tl-card">
  <span class="tl-card-icon">{icon}</span>
  <div class="tl-card-label">{label}</div>
  <div class="tl-card-value">{value}</div>
  {sub_html}
</div>"""


def _metric_grid(analysis: dict) -> None:
    basic = analysis.get("basic", {})
    t     = analysis.get("time", {})

    w  = f"{basic.get('words', 0):,}"
    uw = f"{basic.get('unique_words', 0):,}"
    ch = f"{basic.get('characters_with_spaces', 0):,}"
    cn = f"{basic.get('characters_without_spaces', 0):,}"
    se = f"{basic.get('sentences', 0):,}"
    pa = f"{basic.get('paragraphs', 0):,}"
    rt = TextAnalyzer.format_time(t.get("reading_seconds", 0))
    st_ = TextAnalyzer.format_time(t.get("speaking_seconds", 0))

    html = f"""<div class="tl-grid">
  {_card("📝", "Words",         w,   f"{uw} unique")}
  {_card("🔤", "Characters",    ch,  f"{cn} no spaces")}
  {_card("✦",  "Sentences",     se,  f"{pa} paragraphs")}
  {_card("📖", "Reading Time",  rt,  f"at {st.session_state.reading_wpm} WPM")}
  {_card("🎙", "Speaking Time", st_, f"at {st.session_state.speaking_wpm} WPM")}
  {_card("📄", "Paragraphs",    pa,  f"{se} sentences")}
</div>"""
    st.markdown(html, unsafe_allow_html=True)


def _readability_block(analysis: dict) -> None:
    r      = analysis.get("readability", {})
    fre    = r.get("fre_score", 0.0)
    fk     = r.get("fk_grade", 0.0)
    label  = r.get("label", "N/A")
    emoji  = r.get("emoji", "")
    color  = r.get("color", "#6366f1")

    st.markdown(f"""
<div class="tl-section">
  <div class="tl-section-title"><span></span>Readability Analysis</div>
  <div class="tl-read">
    <div class="tl-read-circle"
         style="background:linear-gradient(135deg,{color},{color}99);">
      {int(fre)}
    </div>
    <div class="tl-read-meta">
      <h3>{emoji}&nbsp; {label}</h3>
      <p>Flesch Reading Ease &nbsp;·&nbsp; <strong>{fre}</strong> / 100</p>
      <p>Flesch-Kincaid Grade &nbsp;·&nbsp; <strong>Grade {fk}</strong></p>
    </div>
  </div>
</div>""", unsafe_allow_html=True)


def _keywords_block(analysis: dict) -> None:
    kws = analysis.get("keywords", [])
    if not kws:
        st.info("Not enough content to extract keywords yet.")
        return

    max_count = kws[0]["count"]
    rows = ""
    for i, kw in enumerate(kws, 1):
        bar_pct = int((kw["count"] / max_count) * 100)
        rows += f"""
<div class="tl-kw">
  <span class="tl-kw-rank">{i}</span>
  <span class="tl-kw-word">{kw['word']}</span>
  <div class="tl-kw-track">
    <div class="tl-kw-fill" style="width:{bar_pct}%"></div>
  </div>
  <span class="tl-kw-count">{kw['count']}×</span>
  <span class="tl-kw-pct">{kw['density']}%</span>
</div>"""

    st.markdown(f"""
<div class="tl-section">
  <div class="tl-section-title"><span></span>Keyword Density (stop-words filtered)</div>
  {rows}
</div>""", unsafe_allow_html=True)


def _advanced_block(analysis: dict) -> None:
    adv = analysis.get("advanced", {})

    def row(label, value):
        return f"""
<div class="tl-adv">
  <span class="tl-adv-label">{label}</span>
  <span class="tl-adv-value">{value}</span>
</div>"""

    st.markdown(f"""
<div class="tl-section">
  <div class="tl-section-title"><span></span>Advanced Linguistic Metrics</div>
  {row("Avg Word Length",        f"{adv.get('avg_word_length', 0):.1f} chars")}
  {row("Avg Sentence Length",    f"{adv.get('avg_sentence_length', 0):.1f} words")}
  {row("Longest Word",           f'&ldquo;{adv.get("longest_word", "—")}&rdquo;')}
  {row("Longest Sentence",       f"{adv.get('longest_sentence_words', 0)} words")}
  {row("Lexical Diversity",      f"{adv.get('lexical_diversity', 0):.1f}%")}
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PLOTLY CHARTS
# ═══════════════════════════════════════════════════════════════════════════════

def _keyword_chart(analysis: dict) -> None:
    kws = analysis.get("keywords", [])
    if len(kws) < 2:
        return

    dm  = st.session_state.dark_mode
    df  = pd.DataFrame(kws[:9])

    fig = go.Figure(go.Bar(
        x=df["count"],
        y=df["word"],
        orientation="h",
        marker=dict(
            color=df["count"],
            colorscale=[[0, "#a855f7"], [0.5, "#6366f1"], [1, "#3b82f6"]],
            line=dict(width=0),
        ),
        text=df["count"],
        textposition="outside",
        textfont=dict(
            size=11,
            color="#94a3b8" if dm else "#64748b",
        ),
        hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif",
                  color="#94a3b8" if dm else "#475569", size=12),
        yaxis=dict(
            autorange="reversed",
            gridcolor="rgba(255,255,255,0.04)" if dm else "rgba(0,0,0,0.04)",
            tickfont=dict(size=12),
            tickcolor="rgba(0,0,0,0),
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.05)" if dm else "rgba(0,0,0,0.05)",
            zeroline=False,
        ),
        margin=dict(l=0, r=40, t=8, b=8),
        height=270,
        bargap=0.35,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _diversity_gauge(analysis: dict) -> None:
    adv = analysis.get("advanced", {})
    ld  = adv.get("lexical_diversity", 0.0)
    dm  = st.session_state.dark_mode

    tx_color = "#e2e8f0" if dm else "#1e293b"
    sub_color = "#64748b" if dm else "#94a3b8"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ld,
        number={"suffix": "%", "font": {"size": 28, "color": tx_color,
                                         "family": "DM Sans"}},
        title={"text": "Lexical Diversity",
               "font": {"size": 12, "color": sub_color, "family": "DM Sans"}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#2a2a45" if dm else "#d4d8f0",
                "tickfont": {"size": 10},
            },
            "bar": {"color": "#6366f1", "thickness": 0.22},
            "bgcolor": "#16162a" if dm else "#f0f4ff",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 33],  "color": "#1e1e35" if dm else "#e0e7ff"},
                {"range": [33, 66], "color": "#1a1e35" if dm else "#ddd6fe"},
                {"range": [66, 100],"color": "#161e38" if dm else "#c7d2fe"},
            ],
            "threshold": {
                "line": {"color": "#a855f7", "width": 2},
                "thickness": 0.75,
                "value": ld,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=16, r=16, t=24, b=10),
        height=200,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

def _sidebar() -> None:
    with st.sidebar:
        # Theme
        st.markdown("### 🎨 Appearance")
        dark = st.toggle(
            "Dark Mode",
            value=st.session_state.dark_mode,
            key="theme_toggle",
        )
        if dark != st.session_state.dark_mode:
            st.session_state.dark_mode = dark
            st.rerun()

        st.divider()

        # File upload
        st.markdown("### 📂 Upload Document")
        st.caption("Supported: .txt · .docx · .pdf · .md")

        uploaded = st.file_uploader(
            "drag-and-drop or browse",
            type=["txt", "docx", "pdf", "md"],
            label_visibility="collapsed",
            key="file_upload",
        )
        if uploaded:
            if uploaded.name != st.session_state.file_name:
                with st.spinner(f"Reading {uploaded.name}…"):
                    text, err = FileParser.parse(uploaded, uploaded.name)
                if err:
                    st.error(f"⚠️ {err}")
                else:
                    st.session_state.text_content = text
                    st.session_state.file_name    = uploaded.name
                    st.success(f"✓ Loaded **{uploaded.name}**")
                    st.rerun()

        st.divider()

        # WPM settings
        st.markdown("### ⚙️ Reading Settings")
        st.session_state.reading_wpm = st.slider(
            "Reading WPM", 100, 600,
            st.session_state.reading_wpm, 10,
            help="Average adult: 200–250 WPM",
        )
        st.session_state.speaking_wpm = st.slider(
            "Speaking WPM", 80, 300,
            st.session_state.speaking_wpm, 10,
            help="Average speaking: 120–150 WPM",
        )

        st.divider()

        # About
        st.markdown("""
<div style="font-size:11.5px; line-height:1.7; color:#64748b;">
<strong style="color:#94a3b8;">TextLens v1.0</strong><br>
Python · Streamlit · Plotly<br><br>
Algorithms:<br>
· Flesch-Kincaid (readability)<br>
· Regex NLP tokenisation<br>
· Custom keyword engine<br>
· Lexical diversity score<br><br>
Export: JSON · TXT · PDF
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LAYOUT
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    _css()
    _sidebar()

    # ── Header ─────────────────────────────────────────────────────────────────
    dm_icon = "🌙" if st.session_state.dark_mode else "☀️"
    wc_val  = st.session_state.analysis["basic"]["words"] if st.session_state.analysis else 0
    badge   = f"Live · {wc_val:,} words" if wc_val else "Waiting for input"

    st.markdown(f"""
<div class="tl-header">
  <div class="tl-logo">🔍</div>
  <div>
    <h1>TextLens</h1>
    <p>Professional Text Analytics Engine {dm_icon}</p>
  </div>
  <div class="tl-badge">{badge}</div>
</div>""", unsafe_allow_html=True)

    # ── Two-column split ────────────────────────────────────────────────────────
    col_editor, col_stats = st.columns([11, 9], gap="large")

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║  LEFT — EDITOR                                                           ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    with col_editor:

        # ── Case toolbar ─────────────────────────────────────────────────────
        t1, t2, t3, t4, t5 = st.columns(5)
        has_text = bool(st.session_state.text_content.strip())

        def _apply(fn):
            if has_text:
                st.session_state.text_content = fn(st.session_state.text_content)
                st.rerun()

        with t1:
            if st.button("🔠 UPPER", use_container_width=True, disabled=not has_text):
                _apply(str.upper)
        with t2:
            if st.button("🔡 lower", use_container_width=True, disabled=not has_text):
                _apply(str.lower)
        with t3:
            if st.button("📝 Title", use_container_width=True, disabled=not has_text):
                _apply(str.title)
        with t4:
            if st.button("✏️ Sentence", use_container_width=True, disabled=not has_text):
                _apply(TextAnalyzer._sentence_case)
        with t5:
            if st.button("🗑️ Clear", use_container_width=True, disabled=not has_text):
                st.session_state.text_content = ""
                st.session_state.analysis     = None
                st.session_state.file_name    = None
                st.rerun()

        st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

        # ── Text area ─────────────────────────────────────────────────────────
        new_text = st.text_area(
            "text_input",
            value=st.session_state.text_content,
            height=430,
            key="editor",
            placeholder=(
                "Start typing, paste text, or upload a document from the sidebar…\n\n"
                "TextLens will analyse your writing in real time ✦"
            ),
            label_visibility="collapsed",
        )

        # Sync + re-analyse whenever content changes
        if new_text != st.session_state.text_content:
            st.session_state.text_content = new_text

        # ── Live analysis ─────────────────────────────────────────────────────
        if st.session_state.text_content.strip():
            analyzer = TextAnalyzer(
                reading_wpm=st.session_state.reading_wpm,
                speaking_wpm=st.session_state.speaking_wpm,
            )
            st.session_state.analysis = analyzer.analyze(st.session_state.text_content)
        else:
            st.session_state.analysis = None

        # ── Export panel ──────────────────────────────────────────────────────
        if st.session_state.analysis:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(
                "<div style='font-size:11px;font-weight:600;color:#64748b;"
                "text-transform:uppercase;letter-spacing:.8px;margin-bottom:10px'>"
                "📤 Export Report</div>",
                unsafe_allow_html=True,
            )
            ec1, ec2, ec3 = st.columns(3)
            ts = datetime.now().strftime("%Y%m%d_%H%M")

            with ec1:
                st.download_button(
                    "⬇ JSON",
                    data=ExportUtils.to_json(
                        st.session_state.text_content, st.session_state.analysis
                    ),
                    file_name=f"textlens_{ts}.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with ec2:
                st.download_button(
                    "⬇ TXT",
                    data=ExportUtils.to_txt(
                        st.session_state.text_content, st.session_state.analysis
                    ),
                    file_name=f"textlens_{ts}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with ec3:
                try:
                    pdf_bytes = ExportUtils.to_pdf(
                        st.session_state.text_content, st.session_state.analysis
                    )
                    st.download_button(
                        "⬇ PDF",
                        data=pdf_bytes,
                        file_name=f"textlens_{ts}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except ImportError:
                    st.caption("Install `reportlab` for PDF export")
                except Exception as e:
                    st.caption(f"PDF error: {e}")

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║  RIGHT — ANALYTICS DASHBOARD                                             ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    with col_stats:
        if not st.session_state.analysis:
            st.markdown("""
<div class="tl-empty">
  <div class="tl-empty-icon">✍️</div>
  <div class="tl-empty-title">No text to analyse yet</div>
  <div class="tl-empty-sub">
    Start typing in the editor on the left,<br>
    paste content, or upload a document file<br>
    from the sidebar to see real-time analytics.
  </div>
</div>""", unsafe_allow_html=True)
            return

        analysis = st.session_state.analysis

        # Tabs
        tab_overview, tab_keywords, tab_advanced = st.tabs(
            ["📊  Overview", "🔑  Keywords", "🧠  Advanced"]
        )

        with tab_overview:
            _metric_grid(analysis)
            _readability_block(analysis)

        with tab_keywords:
            _keywords_block(analysis)
            st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)
            _keyword_chart(analysis)

        with tab_advanced:
            _advanced_block(analysis)
            _diversity_gauge(analysis)


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
