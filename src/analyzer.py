"""Transparent keyword-based discovery of financial filing passages.

This is a baseline information retrieval tool, not a trained AI classifier.
"""
import re
from collections import Counter

CATEGORIES = {
    "Revenue": ["net sales", "net revenue", "total revenue", "revenue growth", "sales increased", "sales decreased"],
    "Competition": ["competition", "competitors", "competitive pressure", "market share", "compete with"],
    "Debt & financing": ["long-term debt", "credit facility", "borrowings", "indebtedness", "interest expense", "debt obligations"],
    "Research & development": ["research and development", "r&d", "product development", "innovation"],
    "Risk": ["risk factors", "material adverse", "cybersecurity", "regulatory risk", "supply chain disruption"],
    "Shares": ["common stock", "share repurchase", "stockholders", "dividends", "outstanding shares"],
}
PATTERNS = {
    name: re.compile(r"(?<!\w)(?:" + "|".join(re.escape(term) for term in terms) + r")(?!\w)", re.I)
    for name, terms in CATEGORIES.items()
}


def split_passages(text: str, max_chars: int = 850) -> list[str]:
    """Split a filing into readable overlapping windows at sentence boundaries."""
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text)
    chunks, current = [], ""
    for sentence in sentences:
        if len(sentence) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(sentence[i:i + max_chars] for i in range(0, len(sentence), max_chars))
        elif len(current) + len(sentence) + 1 <= max_chars:
            current = f"{current} {sentence}".strip()
        else:
            if current:
                chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    return chunks


def analyze(text: str, max_results: int = 500) -> list[dict]:
    results = []
    for position, passage in enumerate(split_passages(text), start=1):
        for category, pattern in PATTERNS.items():
            matches = list(pattern.finditer(passage))
            if matches:
                results.append({
                    "passage": position,
                    "category": category,
                    "matches": len(matches),
                    "keywords": ", ".join(sorted({m.group(0).lower() for m in matches})),
                    "text": passage,
                })
                if len(results) >= max_results:
                    return results
    return results


def category_counts(results: list[dict]) -> dict[str, int]:
    counts = Counter(row["category"] for row in results)
    return {name: counts.get(name, 0) for name in CATEGORIES}


def highlighted_html(text: str, category: str) -> str:
    """Escape all filing content before adding trusted HTML highlight tags."""
    import html
    pattern = PATTERNS[category]
    pieces = []
    start = 0
    for match in pattern.finditer(text):
        pieces.append(html.escape(text[start:match.start()]))
        pieces.append("<mark>" + html.escape(match.group(0)) + "</mark>")
        start = match.end()
    pieces.append(html.escape(text[start:]))
    return "".join(pieces)
