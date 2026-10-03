import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Stock Checker", layout="wide")
st.title("เช็กราคาหุ้น")

DEFAULT = ["NVDA", "AAPL", "GOOGL", "MSFT", "TSLA"]

st.sidebar.header("เลือกหุ้น")
picks = []
for i in range(5):
    v = st.sidebar.text_input(f"ตัวที่ {i+1}", DEFAULT[i], key=f"s{i}")
    if v.strip():
        picks.append(v.strip().upper())

@st.cache_data(ttl=300)
def get_data(sym):
    hist = yf.Ticker(sym).history(period="6mo")
    if len(hist) < 2:
        return None
    last = hist["Close"].iloc[-1]
    prev = hist["Close"].iloc[-2]
    return last, (last - prev) / prev * 100, hist

if picks:
    cols = st.columns(len(picks))
    for col, sym in zip(cols, picks):
        d = get_data(sym)
        with col:
            if d is None:
                st.metric(sym, "ไม่พบข้อมูล")
            else:
                price, chg, _ = d
                st.metric(sym, f"{price:,.2f}", f"{chg:+.2f}%")

    st.divider()
    choice = st.selectbox("ดูกราฟย้อนหลัง 6 เดือน", picks)
    d = get_data(choice)
    if d:
        st.line_chart(d[2]["Close"])
        st.dataframe(d[2].tail(10), use_container_width=True)
