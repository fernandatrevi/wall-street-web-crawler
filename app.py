"""Streamlit UI for exploring public SEC 10-K and 10-Q filings."""
import pandas as pd
import requests
from io import BytesIO
from pypdf import PdfReader
import streamlit as st

from src.analyzer import CATEGORIES, analyze, category_counts, highlighted_html
from src.sec_client import download_filing, latest_filing, resolve_cik, sec_session
from src.filing_reader import show_filing_reader
from src.pdf_reader import extract_pdf_text

st.set_page_config(page_title="Wall Street Web Crawler", page_icon="📈", layout="wide")
st.title("📈 Wall Street Web Crawler")
st.caption("Explore public SEC filings and find highlighted passages by financial topic.")
st.info("Educational research tool. Keyword matches are not investment advice or verified financial conclusions.")

with st.sidebar:
    st.header("Choose a document")
    source = st.radio(
        "How do you want to analyze?",
        ["Find a company report (SEC)", "Upload my own PDF"],
        help="SEC mode downloads the latest public company report automatically. PDF mode analyzes a file from your computer.",
    )
    if source == "Find a company report (SEC)":
        st.info("Enter a US stock ticker (e.g. AAPL = Apple). The app finds the latest public 10-K (annual) or 10-Q (quarterly) report on the SEC website. You do not need to upload a file.")
        ticker = st.text_input("Stock ticker (company symbol)", "AAPL").strip().upper()
        form = st.selectbox("Report type", ["10-K", "10-Q"])
        st.caption("10-K = annual company report. 10-Q = quarterly company report.")
        email = st.text_input("Contact email (required by SEC)", placeholder="you@example.com")
        load = st.button("Find and analyze SEC report", type="primary", use_container_width=True)
        st.caption("Your email is used only in the SEC request User-Agent and is not saved by this app.")
    else:
        st.info("Upload a text-based PDF from your computer. The spider will highlight financial keywords it finds. Scanned/image-only PDFs are not supported yet.")
        uploaded = st.file_uploader("Choose a PDF (up to 15 MB)", type=["pdf"])
        load = st.button("Analyze uploaded PDF", type="primary", use_container_width=True, disabled=uploaded is None)

if load:
    try:
        if source == "Find a company report (SEC)":
            if not ticker:
                raise ValueError("Enter a company stock ticker such as AAPL or MSFT.")
            with st.spinner("Downloading and analyzing SEC filing..."):
                session = sec_session(email)
                cik, company = resolve_cik(session, ticker)
                filing = latest_filing(session, cik, form)
                text = download_filing(session, filing["url"])
                results = analyze(text)
                st.session_state["report"] = {"source": "sec", "ticker": ticker, "company": company, **filing, "results": results}
        else:
            with st.spinner("Reading and analyzing your PDF..."):
                text = extract_pdf_text(uploaded.getvalue())
                results = analyze(text)
                st.session_state["report"] = {
                    "source": "upload", "ticker": "UPLOAD", "company": uploaded.name,
                    "form": "PDF", "date": "Uploaded locally", "results": results,
                }
        if not results:
            st.warning("No financial keyword matches found. Try a document with financial terminology.")
    except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
        st.error(f"Could not analyze document: {exc}")

report = st.session_state.get("report")
if not report:
    st.write("Elige **Buscar reporte de empresa (SEC)** o **Subir mi propio PDF** en el menú izquierdo para empezar.")
    st.stop()

st.subheader(report["company"] if report.get("source") == "upload" else f"{report['company']} ({report['ticker']})")
if report.get("source") == "upload":
    st.write("**Origen:** PDF subido desde tu computadora · **Análisis:** palabras clave financieras")
else:
    st.write(f"**Reporte:** {report['form']} · **Presentado:** {report['date']} · [Ver reporte original en SEC]({report['url']})")
st.subheader("🕷️ Análisis visual del documento")
st.caption("Vista reconstruida del texto extraído. La araña recorre las coincidencias financieras; no reproduce exactamente el diseño del PDF original.")
show_filing_reader(report["results"])
counts = category_counts(report["results"])
cols = st.columns(3)
for i, (category, count) in enumerate(counts.items()):
    cols[i % 3].metric(category, count)

st.divider()
selected = st.multiselect("Filter topics", list(CATEGORIES), default=list(CATEGORIES))
search = st.text_input("Search within findings", placeholder="e.g. services")
filtered = [
    row for row in report["results"]
    if row["category"] in selected and search.lower() in row["text"].lower()
]
st.caption(f"Showing {len(filtered)} matches (up to 500 category/passage matches analyzed).")
if filtered:
    st.download_button(
        "Download findings as CSV",
        pd.DataFrame(filtered).to_csv(index=False).encode("utf-8"),
        file_name=f"{report['ticker']}_{report['form']}_findings.csv",
        mime="text/csv",
    )
    for row in filtered[:100]:
        with st.expander(f"{row['category']} · Passage {row['passage']} · {row['matches']} keyword match(es)"):
            st.markdown(highlighted_html(row["text"], row["category"]), unsafe_allow_html=True)
            st.caption(f"Matched terms: {row['keywords']}")
    if len(filtered) > 100:
        st.caption("Only the first 100 results are shown here. Download the CSV for all filtered results.")
else:
    st.warning("No findings match these filters.")
