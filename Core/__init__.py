"""TextLens core analysis package."""
from .text_analyzer import TextAnalyzer
from .readability import flesch_reading_ease, flesch_kincaid_grade, get_readability_label

__all__ = ["TextAnalyzer", "flesch_reading_ease", "flesch_kincaid_grade", "get_readability_label"]
