import re
from collections import Counter

WORD_RE = re.compile(r"\w+", re.UNICODE)
SENTENCE_RE = re.compile(r"[.!?]+")
WORDS_PER_MINUTE = 200


def analyze_text(text: str, top_n: int = 5) -> dict:
    """Pure function: easy to test without Celery, Redis or HTTP."""
    words = [w.lower() for w in WORD_RE.findall(text)]
    counts = Counter(words)
    sentences = [s for s in SENTENCE_RE.split(text) if s.strip()]

    # Ordena por frequência (desc) e, em empate, por ordem alfabética
    top_words = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:top_n]

    return {
        "characters": len(text),
        "words": len(words),
        "unique_words": len(counts),
        "sentences": len(sentences),
        "reading_time_seconds": round(len(words) / WORDS_PER_MINUTE * 60),
        "top_words": [{"word": word, "count": count} for word, count in top_words],
    }
