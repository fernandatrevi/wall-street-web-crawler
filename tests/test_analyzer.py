from src.analyzer import analyze, category_counts, highlighted_html, split_passages


def test_detects_categories():
    results = analyze("The company reported net sales growth. Research and development increased.")
    categories = {row["category"] for row in results}
    assert "Revenue" in categories
    assert "Research & development" in categories


def test_empty_text():
    assert analyze("") == []
    assert all(value == 0 for value in category_counts([]).values())


def test_highlight_escapes_untrusted_html():
    html = highlighted_html("<script>alert(1)</script> net sales", "Revenue")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "<mark>net sales</mark>" in html


def test_split_long_text():
    assert all(len(x) <= 100 for x in split_passages("x" * 240, max_chars=100))
