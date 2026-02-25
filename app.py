import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(
    page_title="投資趨勢監控",
    layout="wide"
)

# 極短行 CSS，防止斷字
CSS = """
<style>
* { text-shadow: none !important; }
.title { font-size: 26px; font-weight: 700; }
.val { font-size: 22px; font-weight: 600; }
.sub { font-size: 16px; color: #AAA; }
.bar-bg {
    background: #111;
    border-radius: 8px;
    height: 24px;
    margin-top: 8px;
}
.bar-fill {
    height: 24px;
    border-radius: 8px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def safe_price(ticker):
    try:
        tk = yf.Ticker(ticker)
        # 嘗試 fast_info
        try:
            if hasattr(tk, 'fast_info'):
                info = tk.fast_info
                # 兼容不同寫法
                if hasattr(info, 'last_price'):
                    p = info.last_price
                else:
                    p = info.get('lastPrice')
                if p: return float(p)
        except:
            pass
        
        # 嘗試歷史數據
        hist = tk.history(period="5d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
    except:
        return None
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
        m60 = float(s.rolling(60).mean().iloc[-1])
        m240 = float(s.rolling(240).mean().iloc[-1])
        pct = ((cur - m60) / m60) * 100
        return cur, m60, m240, pct
    except:
        return None

def get_style(p, c, m240):
    if c < m240:
        return (
            "🔴 紅燈 (跌破年線)",
            "#FF0000",
            "linear-gradient(90deg, #640000, #FF0000)"
        )
    elif p < 0:
        return (
            "🟡 黃燈 (跌破季線)",
            "#FFFF00",
            "linear-gradient(90deg, #646400, #FFFF00)"
        )
    else:
        return (
            "🟢 綠燈 (季線之上)",
            "#00FF00",
            "linear-gradient(90deg, #006400, #00FF00)"
        )

st.title("📡 投資趨勢監控系統")

# 輸入區
st.subheader("💰 資金佔比試算")
c1, c2 = st.columns(2)
with c1:
    v_ndx = st.number_input("NDX 金額", value=0, format="%d")
with c2:
    v_sox = st.number_input("SOX 金額", value=0, format="%d")

tot = v_ndx + v_sox
r_n = (v_ndx / tot * 100) if tot > 0 else 0
r_s = (v_sox / tot * 100) if tot > 0 else 0
st.info(f"💵 總計: **${tot:,}**")

k1, k2 = st.columns(2)
def color(v):
    return "#FF0000" if v > 50 else "#00FF00"

h_n = f"<span style='color:{color(r_n)}'>{r_n:.1f}%</span>"
k1.markdown(f"NDX: **{h_n}**", unsafe_allow_html=True)

h_s = f"<span style='color:{color(r_s)}'>{r_s:.1f}%</span>"
k2.markdown(f"SOX: **{h_s}**", unsafe_allow_html=True)

st.divider()

# 監控列表：確保 NDX 在第一個
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
            # XAUD 特別處理
            if sym == "XAUD_FIX":
                usd = safe_price("XAUUSD=X")
                aud = safe_price("AUDUSD=X")
                if usd and aud:
                    # 換算公式
                    val = int(usd / aud)
                    
                    st.markdown(
                        f"<div class='title' style='color:#FFD700'>"
                        f"{name}</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<div class='sub'>"
                        f"公式: {usd:,.0f} / {aud:.4f}</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<div class='val' style='color:#FFD700'>"
                        f"報價: {val:,}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.error("黃金數據讀取失敗")
            
            # 一般指數 (NDX, SOX, GDX)
            else:
                data = fetch_data(sym)
                if data:
                    cur, m60, m240, pct = data
                    txt, col, grad = get_style(pct, cur, m240)
                    
                    if sym == "GDX":
                        vc = f"{cur:,.2f}"
                        v6 = f"{m60:,.2f}"
                        v2 = f"{m240:,.2f}"
                    else:
                        vc = f"{int(cur):,}"
                        v6 = f"{int(m60):,}"
                        v2 = f"{int(m240):,}"

                    st.markdown(
                        f"<div class='title' style='color:{col}'>"
                        f"{name}</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<div class='val' style='color:{col}'>"
                        f"報價: {vc}</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<div class='val' style='color:{col}'>"
                        f"季線: {v6}</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<div class='val' style='color:{col}'>"
                        f"年線: {v2}</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<div style='color:{col};font-weight:bold'>"
                        f"{txt} | 距季線: {pct:+.2f}%</div>",
                        unsafe_allow_html=True
                    )
                    
                    # 能量條
                    w = min(max(abs(pct), 5.0), 40.0)
                    bar = (
                        f"<div class='bar-bg'>"
                        f"<div class='bar-fill' style='"
                        f"width:{w}%;background:{grad}'>"
                        f"</div></div>"
                    )
                    st.markdown(bar, unsafe_allow_html=True)
                else:
                    st.error(f"無法取得 {name}")
    st.write("<br>", unsafe_allow_html=True)
