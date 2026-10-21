"""Fetch public company filings from SEC EDGAR.

SEC requests require an identifying User-Agent. Provide your own contact email.
"""
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SEC_BASE = "https://www.sec.gov"
DATA_BASE = "https://data.sec.gov"
TICKERS_URL = f"{SEC_BASE}/files/company_tickers.json"


def sec_session(contact_email: str) -> requests.Session:
    email = contact_email.strip()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise ValueError("Enter a valid contact email for SEC EDGAR requests.")
    session = requests.Session()
    session.headers.update({
        "User-Agent": f"WallStreetResearch educational project {email}",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "application/json, text/html, */*",
    })
    return session


def fetch_json(session: requests.Session, url: str):
    response = session.get(url, timeout=25)
    response.raise_for_status()
    return response.json()


def resolve_cik(session: requests.Session, ticker: str) -> tuple[str, str]:
    symbol = ticker.strip().upper()
    if not re.fullmatch(r"[A-Z0-9.-]{1,12}", symbol):
        raise ValueError("Enter a valid stock ticker.")
    tickers = fetch_json(session, TICKERS_URL)
    for company in tickers.values():
        if company["ticker"].upper() == symbol:
            return str(company["cik_str"]).zfill(10), company["title"]
    raise ValueError(f"Ticker {symbol} not found in SEC company list.")


def latest_filing(session: requests.Session, cik: str, form: str = "10-K") -> dict:
    submissions = fetch_json(session, f"{DATA_BASE}/submissions/CIK{cik}.json")
    recent = submissions["filings"]["recent"]
    for i, filing_form in enumerate(recent["form"]):
        if filing_form == form:
            accession = recent["accessionNumber"][i]
            primary = recent["primaryDocument"][i]
            accession_no_dashes = accession.replace("-", "")
            url = f"{SEC_BASE}/Archives/edgar/data/{int(cik)}/{accession_no_dashes}/{primary}"
            return {"form": form, "date": recent["filingDate"][i], "url": url, "accession": accession}
    raise ValueError(f"No recent {form} found for this company.")


def download_filing(session: requests.Session, url: str) -> str:
    if not url.startswith(f"{SEC_BASE}/Archives/"):
        raise ValueError("Only SEC archive URLs are allowed.")
    time.sleep(0.2)
    response = session.get(url, timeout=45)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "ix:header"]):
        tag.decompose()
    for tag in soup.find_all(style=re.compile(r"display\s*:\s*none", re.I)):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    if len(text) < 1000:
        raise ValueError("This filing did not contain enough extractable text.")
    return text
