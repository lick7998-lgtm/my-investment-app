import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="投資趨勢監控系統", layout="wide")

st.markdown("""
<style>
* { text-shadow: none !important; }
.title { font-size: 26px; font-weight: 700; margin-bottom: 5px; }
.val { font-size: 22px; font-weight: 600; margin-bottom: 5px; }
.sub { font-size: 16px; color: #AAA; margin-bottom: 8px; }
.bar-bg { background: #111; border-radius: 8px; height: 24px; margin-top: 8px; }
.bar-fill { height: 24px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# 🚀 放棄花俏寫法，全部改用與 NDX 完全相同的最穩 yf.download
def fetch_latest_price(symbol):
    try:
        df = yf.download(symbol, period="5d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            s = df['Close'].iloc[:, 0]
        else:
            s = df['Close']
        s = s.dropna()
        if s.empty: return None
        return float(s.iloc[-1])
    except:
        return None

def fetch_data(sym):
    try:
        d = yf.download(sym, period="2y", progress=False)
        if d.empty: return None
        if isinstance(d.columns, pd.MultiIndex):
            s = d['Close'].iloc[:, 0]
        else:
            s = d['Close']
        s = s.dropna()
        if s.empty: return None
        cur = float(s.iloc[-1])
        m60 = float(s.rolling(60).mean().dropna().iloc[-1])
        m240 = float(s.rolling(240).mean().dropna().iloc[-1])
        pct = ((cur - m60) / m60) * 100
        return cur, m60, m240, pct
    except:
        return None

def get_style(p, c, m240):
    if c < m240: return "🔴 紅燈 (跌破年線)", "#FF0000", "linear-gradient(90deg, #640000, #FF0000)"
    elif p < 0: return "🟡 黃燈 (跌破季線)", "#FFFF00", "linear-gradient(90deg, #646400, #FFFF00)"
    else: return "🟢 綠燈 (季線之上)", "#00FF00", "linear-gradient(90deg, #006400, #00FF00)"

st.title("📡 投資趨勢監控系統")

st.subheader("💰 資金佔比試算")
c1, c2 = st.columns(2)
with c1: v_ndx = st.number_input("NDX 金額", value=0, format="%d")
with c2: v_sox = st.number_input("SOX 金額", value=0, format="%d")

tot = v_ndx + v_sox
r_n = (v_ndx / tot * 100) if tot > 0 else 0
r_s = (v_sox / tot * 100) if tot > 0 else 0
st.info(f"💵 總計: **${tot:,}**")

k1, k2 = st.columns(2)
k1.markdown(f"NDX: **<span style='color: {'#FF0000' if r_n>50 else '#00FF00'}'>{r_n:.1f}%</span>**", unsafe_allow_html=True)
k2.markdown(f"SOX: **<span style='color: {'#FF0000' if r_s>50 else '#00FF00'}'>{r_s:.1f}%</span>**", unsafe_allow_html=True)

st.divider()

tickers = [
    ("^NDX", "NASDAQ 100 (NDX)"),
    ("^SOX", "費城半導體 (SOX)"),
    ("XAUD_FIX", "黃金現貨 (XAUD)"),
    ("GDX", "黃金礦業 ETF (GDX)")
]

for i in range(0, 4, 2):
    row = st.columns(2)
    for j in range(2):
        sym, name = tickers[i+j]
        with row[j]:
            if sym == "XAUD_FIX":
                usd = fetch_latest_price("XAUUSD=X")
                aud = fetch_latest_price("AUDUSD=X")
                if usd and aud:
                    val = int(usd / aud)
                    st.markdown(f"<div class='title' style='color:#FFD700'>{name}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='sub'>公式: XAUUSD({usd:,.2f}) ÷ AUDUSD({aud:.4f})</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='val' style='color:#FFD700'>當前報價: {val:,}</div>", unsafe_allow_html=True)
                else:
                    st.error("黃金數據讀取失敗")
            else:
                data = fetch_data(sym)
                if data:
                    cur, m60, m240, pct = data
                    txt, col, grad = get_style(pct, cur, m240)
                    vc = f"{cur:,.2f}" if sym == "GDX" else f"{int(cur):,}"
                    v6 = f"{m60:,.2f}" if sym == "GDX" else f"{int(m60):,}"
                    v2 = f"{m240:,.2f}" if sym == "GDX" else f"{int(m240):,}"

                    st.markdown(f"<div class='title' style='color:{col}'>{name}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='val' style='color:{col}'>報價: {vc}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='val' style='color:{col}'>季線: {v6}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='val' style='color:{col}'>年線: {v2}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='color:{col};font-weight:bold;margin-top:8px;'>{txt} | 距季線: {pct:+.2f}%</div>", unsafe_allow_html=True)
                    
                    w = min(max(abs(pct), 5.0), 40.0)
                    st.markdown(f"<div class='bar-bg'><div class='bar-fill' style='width:{w}%;background:{grad}'></div></div>", unsafe_allow_html=True)
                else:
                    st.error(f"無法取得 {name}")
    st.write("<br>", unsafe_allow_html=True)
