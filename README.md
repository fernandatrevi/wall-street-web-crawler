# Wall Street Web Crawler

Python + Streamlit app to explore SEC EDGAR 10-K and 10-Q filings, detect financial topics, highlight matching text and export findings to CSV.

## Run in Codespaces

Open **Code → Codespaces → Create codespace on main**, then in the terminal run:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the forwarded port **8501** to use the app. Enter a ticker (e.g. `AAPL`), a filing type, and your own contact email (required for the SEC User-Agent), then click **Analyze latest filing**.

## Run tests

```bash
python -m pytest -q
```

## Files

- `app.py`: Streamlit user interface
- `src/sec_client.py`: SEC ticker lookup and filing download
- `src/analyzer.py`: keyword-based passage classification and HTML highlighting
- `tests/test_analyzer.py`: unit tests
- `requirements.txt`: Python dependencies

## Topics

Revenue, Competition, Debt & financing, Research & development, Risk, Shares.

## Limitations

This is **keyword matching, not AI semantic analysis**. It can miss synonyms and produce false positives. Text extraction does not preserve original PDF page layout, tables or charts. The app analyzes up to 500 category/passage matches and shows up to 100 excerpts; CSV export contains all filtered matches. The latest filing must appear in the company's recent SEC submissions feed. SEC may limit requests; do not scrape in bulk. Verify findings against the linked original SEC filing. Not investment advice.

## Next improvements

Semantic search, filing-section navigation, historical comparisons, colored in-document annotations and financial charts.

SEC developer guidance: https://www.sec.gov/about/developer-resources
