"""Streamlit UI for exploring public SEC 10-K and 10-Q filings."""
import pandas as pd
import requests
from io import BytesIO
from pypdf import PdfReader
import streamlit as st

from src.analyzer import CATEGORIES, analyze, category_counts, highlighted_html
from src.sec_client import download_filing, latest_filing, resolve_cik, sec_session
from src.filing_reader import show_filing_reader

st.set_page_config(page_title="Wall Street Web Crawler", page_icon="📈", layout="wide")
st.title("📈 Wall Street Web Crawler")
st.caption("Explore public SEC filings and find highlighted passages by financial topic.")
st.info("Educational research tool. Keyword matches are not investment advice or verified financial conclusions.")

with st.sidebar:
    st.header("¿Qué quieres analizar?")
    mode = st.radio("Origen del documento", ["Buscar reporte de empresa (SEC)", "Subir mi propio PDF"])
    if mode == "Buscar reporte de empresa (SEC)":
        st.info("Escribe el símbolo bursátil de una empresa. La aplicación descarga automáticamente su último reporte público desde la SEC. No necesitas subir ningún archivo.")
        ticker = st.text_input("Símbolo bursátil (ticker)", "AAPL", help="Ejemplos: AAPL = Apple, MSFT = Microsoft, NVDA = NVIDIA.").strip().upper()
        form = st.selectbox("Tipo de reporte SEC", ["10-K", "10-Q"])
        st.caption("10-K = reporte anual completo. 10-Q = reporte trimestral con resultados recientes.")
        email = st.text_input("Correo de contacto (requerido por SEC)", placeholder="tu@correo.com")
        load = st.button("Buscar y analizar reporte", type="primary", use_container_width=True)
        st.caption("El correo se utiliza en la solicitud a la SEC; esta app no lo guarda.")
    else:
        st.info("Sube un PDF con texto seleccionable para que la araña encuentre y resalte términos financieros.")
        uploaded = st.file_uploader("Selecciona tu PDF", type=["pdf"])
        load = st.button("Analizar mi PDF", type="primary", use_container_width=True, disabled=uploaded is None)
        st.caption("Los PDF escaneados como imágenes necesitan OCR, que aún no está incluido.")

if load:
    try:
        if mode == "Buscar reporte de empresa (SEC)":
            with st.spinner("Descargando y analizando el reporte de la SEC..."):
                session = sec_session(email)
                cik, company = resolve_cik(session, ticker)
                filing = latest_filing(session, cik, form)
                text = download_filing(session, filing["url"])
                results = analyze(text)
                st.session_state["report"] = {"ticker": ticker, "company": company, "source": "sec", **filing, "results": results}
        else:
            with st.spinner("Extrayendo y analizando tu PDF..."):
                if uploaded.size > 20 * 1024 * 1024:
                    raise ValueError("El archivo supera el límite de 20 MB.")
                reader = PdfReader(BytesIO(uploaded.getvalue()))
                if reader.is_encrypted:
                    raise ValueError("El PDF está protegido con contraseña.")
                if len(reader.pages) > 250:
                    raise ValueError("El PDF tiene más de 250 páginas.")
                text = "\\n".join(page.extract_text() or "" for page in reader.pages)
                if len(text.strip()) < 80:
                    raise ValueError("No se pudo extraer texto suficiente. Los PDF escaneados requieren OCR.")
                results = analyze(text)
                st.session_state["report"] = {"ticker": "PDF", "company": uploaded.name, "source": "upload", "form": "PDF propio", "date": "—", "url": "", "results": results}
    except Exception as exc:
        st.error(f"No se pudo analizar el documento: {exc}")

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
