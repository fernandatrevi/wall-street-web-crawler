# Wall Street Web Crawler 🕷️

A Streamlit app that finds financial keywords in **public SEC company reports** or in **PDF files you upload**. The spider animates a tour through detected terms. Analysis is performed before the animation begins.

## Try the live app

**Live demo (Streamlit Community Cloud):** https://wall-street-web-crawler-h2lubtjvapebqhgglspbg8.streamlit.app/

Open the link in your browser to try the app without installing Python. You can analyze a public SEC filing or upload a text-based PDF. The live deployment may take a moment to wake up after inactivity.

## What does the app search?

**Option 1 — Find a company report (SEC):** Enter a US stock symbol (ticker) such as `AAPL` (Apple), `MSFT` (Microsoft), or `NVDA` (NVIDIA). The app retrieves the company's latest available report from SEC EDGAR:

- **10-K:** Annual report covering the fiscal year, risks, operations, and audited annual financial statements.
- **10-Q:** Quarterly report with interim financial statements and updates. Typically submitted for the first three quarters.

An email is required for SEC requests; it is used in the request User-Agent, not stored by this application.

**Option 2 — Upload my own PDF:** Upload a text-based PDF (up to 15 MB, 200 pages, 1 million extracted characters). It is analyzed locally within the running Streamlit process; it is **not sent to SEC**. Uploaded text is not written to a project file. Do not upload confidential documents to a publicly deployed instance you do not trust. Scanned/image-only and password-protected PDFs are not supported.

Both modes use the same **financial keyword categories**, so a non-financial PDF may return few or no results.

## Run locally in VS Code

```bash
git pull
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://localhost:8501. Select your input mode in the left sidebar.

## Run in Codespaces

Open **Code → Codespaces → Create codespace on main** and run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open forwarded port 8501.

## Tests

```bash
python -m pytest -q
```

## Project files

- `app.py`: Streamlit interface and two document modes
- `src/sec_client.py`: SEC ticker lookup and filing retrieval
- `src/pdf_reader.py`: PDF validation and text extraction
- `src/analyzer.py`: keyword-based financial findings
- `src/filing_reader.py`: animated spider and highlighted reader
- `tests/`: validation and analyzer tests

## Technology stack and spider animation

This project combines **Python for financial document analysis** with **JavaScript and SVG for the animated spider**:

- **Python** handles SEC report retrieval, PDF text extraction, and financial keyword matching.
- **Streamlit** provides the web interface and embeds the document reader.
- **JavaScript** drives the spider's movement, including sequential leg steps, timing, and document scrolling.
- **SVG** draws the spider's body, eight articulated legs, and joints.

GitHub may report **Python 100%** because the JavaScript, HTML, and SVG are currently embedded as a string inside `src/filing_reader.py`. GitHub's language breakdown does **not** mean Python animates the spider.

### How the spider moves

The spider visits selected financial keyword matches in the reconstructed document. Its gait is designed to lift **one leg at a time**, bend that leg at the knee, keep the other feet planted during the step, and advance the body in short increments. The reader scrolls to follow the spider, and matched words are highlighted on arrival. The animation is a visualization of precomputed keyword findings, **not an autonomous web-crawling agent**.

### Why JavaScript instead of R?

**R** is valuable for statistics and data visualization, but **JavaScript + SVG** is better suited to precise, interactive animation inside a browser. Python remains responsible for analysis; changing the animation does not require rewriting the analysis in R.

### Potential frontend improvements

The animation is **currently embedded** in `src/filing_reader.py`; the following structure is a **proposed refactor, not yet implemented**:

```text
frontend/
  spider.js     # gait and scroll animation
  spider.css    # spider and reader styles
  spider.svg    # reusable spider drawing
```

Separating these files would make animation work easier to test and contribute to. A library such as **GSAP** could be evaluated for smoother timing later; **GSAP is not currently a dependency**.

## Financial categories

Revenue, Competition, Debt & financing, Research & development, Risk, Shares.

## Limitations

This is **keyword matching, not a trained AI model or financial recommendation**. The spider is an animated replay of findings; it does not independently read or reason about text. Extracted text is reconstructed for display and does not reproduce PDF tables, graphics, or precise original page positions. The app analyzes up to 500 category/passage matches and shows up to 100 excerpts; CSV export includes filtered findings. SEC may limit requests; avoid bulk scraping and verify findings against original reports.

SEC guidance: https://www.sec.gov/about/developer-resources
