"""
core/readability.py
───────────────────────────────────────────────────────────────
Readability scoring algorithms:
  • Flesch Reading Ease (0–100, higher = easier)
  • Flesch-Kincaid Grade Level
  • Human-readable difficulty labels
"""
import re


# ─── Syllable Counter ─────────────────────────────────────────────────────────

def count_syllables(word: str) -> int:
    """
    Estimate syllable count for a single English word using linguistic heuristics.
    Returns at least 1 for any non-empty word.
    """
    word = word.lower().strip()
    word = re.sub(r"[^a-z]", "", word)

    if not word:
        return 0
    if len(word) <= 3:
        return 1

    # Count vowel groups as syllable nuclei
    count = len(re.findall(r"[aeiouy]+", word))

    # Silent trailing -e (e.g. "make", "love")
    if word.endswith("e") and not word.endswith("le") and count > 1:
        count -= 1

    # -ed at end: usually silent (e.g. "baked" → 1 syl off)
    if word.endswith("ed") and count > 1:
        count -= 1

    # -es at end: usually 1 syllable
    if word.endswith("es") and count > 1:
        count -= 1

    # -le at end (with preceding consonant) adds a syllable (e.g. "table")
    if len(word) > 2 and word.endswith("le") and word[-3] not in "aeiouy":
        count += 1

    # Dipthongs: double-letter vowels that are one sound
    count -= len(re.findall(r"[aeiou]{2}", word)) // 2

    return max(1, count)


# ─── Readability Scores ───────────────────────────────────────────────────────

def _extract_components(text: str) -> tuple[int, int, int]:
    """
    Returns (num_sentences, num_words, num_syllables) for a text block.
    """
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    words = re.findall(r"\b[a-zA-Z']+\b", text)

    num_sentences = max(len(sentences), 1)
    num_words = len(words)
    num_syllables = sum(count_syllables(w) for w in words)

    return num_sentences, num_words, num_syllables


def flesch_reading_ease(text: str) -> float:
    """
    Flesch Reading Ease score: 0–100, higher means more readable.
    Formula: 206.835 − 1.015×(words/sentences) − 84.6×(syllables/words)
    """
    num_sentences, num_words, num_syllables = _extract_components(text)
    if num_words == 0:
        return 0.0

    score = (
        206.835
        - 1.015 * (num_words / num_sentences)
        - 84.6 * (num_syllables / num_words)
    )
    return round(max(0.0, min(100.0, score)), 1)


def flesch_kincaid_grade(text: str) -> float:
    """
    Flesch-Kincaid Grade Level: corresponds to US school grade.
    Formula: 0.39×(words/sentences) + 11.8×(syllables/words) − 15.59
    """
    num_sentences, num_words, num_syllables = _extract_components(text)
    if num_words == 0:
        return 0.0

    grade = (
        0.39 * (num_words / num_sentences)
        + 11.8 * (num_syllables / num_words)
        - 15.59
    )
    return round(max(0.0, grade), 1)


def get_readability_label(fre_score: float) -> tuple[str, str, str]:
    """
    Map Flesch Reading Ease score to (label, emoji, hex_color).
    """
    if fre_score >= 90:
        return "Very Easy", "🟢", "#10b981"
    elif fre_score >= 80:
        return "Easy", "🟢", "#34d399"
    elif fre_score >= 70:
        return "Fairly Easy", "🟡", "#a3e635"
    elif fre_score >= 60:
        return "Standard", "🟡", "#facc15"
    elif fre_score >= 50:
        return "Fairly Difficult", "🟠", "#fb923c"
    elif fre_score >= 30:
        return "Difficult", "🔴", "#f87171"
    else:
        return "Very Difficult", "🔴", "#ef4444"
