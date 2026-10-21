"""Streamlit UI for exploring public SEC 10-K and 10-Q filings."""
import pandas as pd
import requests
import streamlit as st

from src.analyzer import CATEGORIES, analyze, category_counts, highlighted_html
from src.sec_client import download_filing, latest_filing, resolve_cik, sec_session
from src.spider import show_crawler

st.set_page_config(page_title="Wall Street Web Crawler", page_icon="📈", layout="wide")
st.title("📈 Wall Street Web Crawler")
st.caption("Explore public SEC filings and find highlighted passages by financial topic.")
st.info("Educational research tool. Keyword matches are not investment advice or verified financial conclusions.")

with st.sidebar:
    st.header("Find a filing")
    ticker = st.text_input("Stock ticker", "AAPL").strip().upper()
    form = st.selectbox("SEC form", ["10-K", "10-Q"])
    email = st.text_input("Your contact email (required by SEC)", placeholder="you@example.com")
    load = st.button("Analyze latest filing", type="primary", use_container_width=True)
    st.caption("The email is used only in the SEC request User-Agent. It is not saved by this app.")

if load:
    try:
        with st.spinner("Downloading and analyzing SEC filing..."):
            session = sec_session(email)
            cik, company = resolve_cik(session, ticker)
            filing = latest_filing(session, cik, form)
            text = download_filing(session, filing["url"])
            results = analyze(text)
            st.session_state["report"] = {"ticker": ticker, "company": company, **filing, "results": results}
    except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
        st.error(f"Could not analyze filing: {exc}")

report = st.session_state.get("report")
if not report:
    st.write("Enter a ticker and your contact email in the sidebar, then click **Analyze latest filing**.")
    st.stop()

st.subheader(f"{report['company']} ({report['ticker']})")
st.write(f"**Form:** {report['form']} · **Filed:** {report['date']} · [Original SEC filing]({report['url']})")
st.subheader("🕷️ Live spider crawl")
st.caption("Animated replay of the findings detected by Python. The spider follows each matching passage; it is a visualization, not a separate AI agent.")
show_crawler(report["results"])
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
