# 🔍 TextLens — Professional Text Analyzer

> A portfolio-grade text analytics web app built with Python & Streamlit.  
> Analyse word count, readability, keyword density, and more — in real time.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit&logoColor=white)
![Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?logo=render&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

| Feature | Details |
|---|---|
| **Basic Metrics** | Words, characters (with/without spaces), sentences, paragraphs, unique words |
| **Time Estimates** | Reading & speaking time (configurable WPM) |
| **Readability** | Flesch Reading Ease + Flesch-Kincaid Grade Level |
| **Keyword Density** | Top 10 keywords (stop-words filtered) with inline bar chart |
| **Advanced Metrics** | Avg word/sentence length, longest word, lexical diversity gauge |
| **Case Tools** | UPPER · lower · Title · Sentence case — one click |
| **File Upload** | Supports `.txt` · `.docx` · `.pdf` · `.md` |
| **Export** | Download report as **JSON**, **TXT**, or **PDF** |
| **Dark / Light Mode** | Toggle in sidebar |

---

## 🗂 Project Structure

```
textlens/
├── main.py                  # App entry point — UI + state management
├── core/
│   ├── __init__.py
│   ├── text_analyzer.py     # NLP engine (metrics, keywords, case)
│   └── readability.py       # Flesch-Kincaid algorithms
├── utils/
│   ├── __init__.py
│   ├── file_parser.py       # .txt / .docx / .pdf / .md reader
│   └── export_utils.py      # JSON / TXT / PDF export formatters
├── .streamlit/
│   └── config.toml          # Theme + server config
├── requirements.txt
├── render.yaml              # Render deployment spec
├── .gitignore
└── README.md
```

---

## 🚀 Deploy in 3 Steps

### Step 1 — Push to GitHub

```bash
# 1. Create a new repo on github.com, then:
git init
git add .
git commit -m "feat: initial TextLens release"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/textlens.git
git push -u origin main
```

### Step 2 — Connect to Render

1. Go to **[render.com](https://render.com)** → **New → Web Service**
2. Connect your GitHub account and select the **textlens** repo
3. Render auto-detects `render.yaml` — review and click **Deploy**

> Render reads `render.yaml` automatically. No manual configuration needed.

### Step 3 — Live 🎉

Render gives you a URL like `https://textlens.onrender.com`.  
Every `git push` to `main` triggers an automatic redeploy.

---

## 💻 Run Locally

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/textlens.git
cd textlens

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch
streamlit run main.py
```

App opens at **http://localhost:8501**

---

## 🛠 Tech Stack

| Layer | Library |
|---|---|
| UI Framework | [Streamlit](https://streamlit.io) |
| Charts | [Plotly](https://plotly.com/python/) |
| Data | [Pandas](https://pandas.pydata.org) |
| Word documents | [python-docx](https://python-docx.readthedocs.io) |
| PDF reading | [pdfplumber](https://github.com/jsvine/pdfplumber) |
| PDF export | [ReportLab](https://www.reportlab.com) |
| NLP / Regex | Python stdlib `re` + custom algorithms |

---

## 📐 Readability Scoring

TextLens implements two industry-standard metrics:

**Flesch Reading Ease** (0–100, higher = easier)  
`206.835 − 1.015 × (words/sentences) − 84.6 × (syllables/words)`

**Flesch-Kincaid Grade Level** (US school grade equivalent)  
`0.39 × (words/sentences) + 11.8 × (syllables/words) − 15.59`

| FRE Score | Label |
|---|---|
| 90–100 | Very Easy |
| 80–89 | Easy |
| 70–79 | Fairly Easy |
| 60–69 | Standard |
| 50–59 | Fairly Difficult |
| 30–49 | Difficult |
| 0–29 | Very Difficult |

---

## 📄 License

MIT © 2024 — free to use, fork, and build upon.
