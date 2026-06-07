"""
core/text_analyzer.py
───────────────────────────────────────────────────────────────
TextAnalyzer — central NLP engine.

Public API:
    analyzer = TextAnalyzer(reading_wpm=200, speaking_wpm=130)
    result   = analyzer.analyze(text: str) -> dict
    time_str = TextAnalyzer.format_time(seconds: int) -> str
"""
import re
from collections import Counter
from .readability import flesch_reading_ease, flesch_kincaid_grade, get_readability_label


# ─── Stop-Word Corpus ─────────────────────────────────────────────────────────

STOP_WORDS: set[str] = {
    # Articles / determiners
    "a", "an", "the", "this", "that", "these", "those",
    # Conjunctions
    "and", "or", "but", "nor", "for", "yet", "so", "both", "either", "neither",
    "although", "because", "since", "unless", "until", "though", "after",
    "before", "while", "when", "where", "if", "as", "than", "while",
    # Prepositions
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "up", "about",
    "into", "through", "during", "about", "above", "below", "between",
    "out", "off", "over", "under", "around", "near", "upon", "within",
    "without", "along", "across", "behind", "beyond", "plus", "except",
    "down", "per",
    # Pronouns
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
    "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself", "she", "her", "hers", "herself",
    "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
    "what", "which", "who", "whom", "us",
    # Auxiliary / modal verbs
    "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might",
    "must", "shall", "can", "need", "used",
    # Common verbs (too generic to be keywords)
    "get", "got", "make", "made", "come", "go", "see", "know", "take",
    "give", "think", "say", "said", "like", "want", "use", "find",
    "tell", "ask", "seem", "feel", "try", "leave", "call", "keep",
    "let", "begin", "show", "hear", "play", "run", "move", "live",
    "hold", "bring", "write", "sit", "stand", "lose", "pay", "meet",
    "set", "learn", "change", "speak", "read", "open", "walk", "appear",
    # Adverbs / qualifiers
    "not", "no", "just", "also", "very", "even", "only", "too", "quite",
    "rather", "well", "back", "still", "more", "most", "much", "less",
    "now", "here", "there", "how", "why", "again", "further", "once",
    "always", "never", "often", "then", "actually",
    # Quantifiers / indefinites
    "some", "any", "all", "each", "every", "few", "many", "other",
    "such", "same", "own", "another",
    # Contractions residue (after tokenisation)
    "ve", "re", "ll", "d", "s", "t", "m", "n",
    # Numbers as words
    "one", "two", "three", "four", "five",
    # Common filler
    "new", "old", "first", "last", "next", "right", "real", "good",
    "best", "free", "high", "long", "great", "big", "large", "small",
    "little", "public", "per", "whether",
}


# ─── TextAnalyzer ─────────────────────────────────────────────────────────────

class TextAnalyzer:
    """
    Full-featured text analysis engine.

    Args:
        reading_wpm  : Average adult reading speed (words per minute).
        speaking_wpm : Average speaking speed (words per minute).
    """

    def __init__(self, reading_wpm: int = 200, speaking_wpm: int = 130) -> None:
        self.reading_wpm = reading_wpm
        self.speaking_wpm = speaking_wpm

    # ── Public entry-point ────────────────────────────────────────────────────

    def analyze(self, text: str) -> dict:
        """
        Run full analysis pipeline on ``text``.

        Returns a structured dict with keys:
          basic, time, keywords, readability, advanced, case_options
        """
        if not text or not text.strip():
            return self._empty_result()

        return {
            "basic":        self._basic_metrics(text),
            "time":         self._time_estimates(text),
            "keywords":     self._keyword_density(text, top_n=10),
            "readability":  self._readability_metrics(text),
            "advanced":     self._advanced_metrics(text),
            "case_options": self._case_options(text),
        }

    # ── Basic metrics ─────────────────────────────────────────────────────────

    def _basic_metrics(self, text: str) -> dict:
        words = self._tokenize_words(text)
        sentences = self._tokenize_sentences(text)
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

        return {
            "words":                     len(words),
            "characters_with_spaces":    len(text),
            "characters_without_spaces": len(re.sub(r"\s", "", text)),
            "sentences":                 len(sentences),
            "paragraphs":                max(len(paragraphs), 1 if text.strip() else 0),
            "unique_words":              len({w.lower() for w in words}),
        }

    # ── Time estimates ────────────────────────────────────────────────────────

    def _time_estimates(self, text: str) -> dict:
        wc = len(self._tokenize_words(text))
        return {
            "reading_seconds":  round((wc / self.reading_wpm) * 60),
            "speaking_seconds": round((wc / self.speaking_wpm) * 60),
        }

    # ── Keyword density ───────────────────────────────────────────────────────

    def _keyword_density(self, text: str, top_n: int = 10) -> list[dict]:
        words = self._tokenize_words(text)
        total_words = len(words)
        if not total_words:
            return []

        filtered = [
            w.lower()
            for w in words
            if w.lower() not in STOP_WORDS and len(w) > 2 and w.isalpha()
        ]
        if not filtered:
            return []

        return [
            {
                "word":    word,
                "count":   count,
                "density": round((count / total_words) * 100, 2),
            }
            for word, count in Counter(filtered).most_common(top_n)
        ]

    # ── Readability ───────────────────────────────────────────────────────────

    def _readability_metrics(self, text: str) -> dict:
        fre = flesch_reading_ease(text)
        fk  = flesch_kincaid_grade(text)
        label, emoji, color = get_readability_label(fre)
        return {
            "fre_score": fre,
            "fk_grade":  fk,
            "label":     label,
            "emoji":     emoji,
            "color":     color,
        }

    # ── Advanced metrics ──────────────────────────────────────────────────────

    def _advanced_metrics(self, text: str) -> dict:
        words     = self._tokenize_words(text)
        sentences = self._tokenize_sentences(text)

        if not words:
            return {
                "avg_word_length":       0.0,
                "avg_sentence_length":   0.0,
                "longest_word":          "",
                "longest_sentence_words": 0,
                "lexical_diversity":     0.0,
            }

        avg_word_len = round(sum(len(w) for w in words) / len(words), 1)
        avg_sent_len = round(len(words) / max(len(sentences), 1), 1)
        longest_word = max(words, key=len) if words else ""

        sent_word_counts = [
            len(re.findall(r"\b[a-zA-Z']+\b", s)) for s in sentences
        ]
        longest_sent = max(sent_word_counts, default=0)

        unique_ratio = len({w.lower() for w in words}) / len(words)

        return {
            "avg_word_length":        avg_word_len,
            "avg_sentence_length":    avg_sent_len,
            "longest_word":           longest_word,
            "longest_sentence_words": longest_sent,
            "lexical_diversity":      round(unique_ratio * 100, 1),
        }

    # ── Case transformations ──────────────────────────────────────────────────

    def _case_options(self, text: str) -> dict:
        return {
            "upper":    text.upper(),
            "lower":    text.lower(),
            "title":    text.title(),
            "sentence": self._sentence_case(text),
        }

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _tokenize_words(text: str) -> list[str]:
        """Extract alphabetic words + contractions."""
        return re.findall(r"\b[a-zA-Z']+\b", text)

    @staticmethod
    def _tokenize_sentences(text: str) -> list[str]:
        """Split on sentence-ending punctuation; filter empties."""
        raw = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s for s in raw if s.strip() and re.search(r"[a-zA-Z]", s)]

    @staticmethod
    def _sentence_case(text: str) -> str:
        """Capitalise the first letter of each sentence, lower-case the rest."""
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        cased = []
        for s in sentences:
            if s:
                cased.append(s[0].upper() + s[1:].lower())
        return " ".join(cased)

    # ── Static utilities ──────────────────────────────────────────────────────

    @staticmethod
    def format_time(seconds: int) -> str:
        """Convert a number of seconds to a compact human-readable string."""
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

    # ── Empty fallback ────────────────────────────────────────────────────────

    @staticmethod
    def _empty_result() -> dict:
        return {
            "basic": {
                "words": 0, "characters_with_spaces": 0,
                "characters_without_spaces": 0, "sentences": 0,
                "paragraphs": 0, "unique_words": 0,
            },
            "time":        {"reading_seconds": 0, "speaking_seconds": 0},
            "keywords":    [],
            "readability": {
                "fre_score": 0.0, "fk_grade": 0.0,
                "label": "N/A", "emoji": "⚪", "color": "#64748b",
            },
            "advanced": {
                "avg_word_length": 0.0, "avg_sentence_length": 0.0,
                "longest_word": "", "longest_sentence_words": 0,
                "lexical_diversity": 0.0,
            },
            "case_options": {},
        }
