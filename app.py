import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(
    page_title="投資趨勢監控系統",
    layout="wide"
)

# 縮短 CSS 長度，分行寫避免被截斷
CSS = """
<style>
* { text-shadow: none !important; }
.title { font-size: 26px; font-weight: bold; }
.val { font-size: 22px; font-weight: bold; }
.form { font-size: 16px; color: #AAA; }
.bar-bg {
    background: #0d0d0d;
    border-radius: 8px;
    width: 100%;
    height: 26px;
    margin-top: 10px;
}
.bar-fill {
    height: 26px;
    border-radius: 8px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def safe_price(ticker):
    try:
        tk = yf.Ticker(ticker)
        try:
            if hasattr(tk, 'fast_info'):
                info = tk.fast_info
                if hasattr(info, 'get'):
                    p = info.get("lastPrice")
                else:
                    p = getattr(info, 'last_price', None)
                if p: return float(p)
        except:
            pass
        
        hist = tk.history(period="5d")
        if not hist.empty and 'Close' in hist.columns:
            clean = hist['Close'].dropna()
            if not clean.empty:
                return float(clean.iloc[-1])
    except:
        return None
    return None

def fetch_data(symbol):
    try:
        df = yf.download(symbol, period="2y", progress=False)
        if df.empty: return None
        
        if isinstance(df.columns, pd.MultiIndex):
            s = df['Close'].iloc[:, 0]
        else:
            s = df['Close']
            
        s = s.dropna()
        if s.empty: return None
        
        curr = float(s.iloc[-1])
        m60 = float(s.rolling(60).mean().dropna().iloc[-1])
        m240 = float(s.rolling(240).mean().dropna().iloc[-1])
        
        pct = ((curr - m60) / m60) * 100
        return curr, m60, m240, pct
    except:
        return None

def get_style(pct, curr, m240):
    # 這裡原本太長導致您截圖報錯，我已將其分成極短的行
    if curr < m240:
        return (
            "🔴 紅燈 (跌破年線)",
            "#FF0000",
            "linear-gradient(90deg, #640000, #FA0000)"
        )
    elif pct < 0:
        return (
            "🟡 黃燈 (跌破季線)",
            "#FFFF00",
            "linear-gradient(90deg, #646400, #FAFA00)"
        )
    else:
        return (
            "🟢 綠燈 (季線之上)",
            "#00FF00",
            "linear-gradient(90deg, #006400, #00FA00)"
        )

st.title("📡 投資趨勢監控系統")

st.subheader("💰 投資金額輸入")
c1, c2 = st.columns(2)
with c1:
    amt_n = st.number_input("NDX", value=0, format="%d")
with c2:
    amt_s = st.number_input("SOX", value=0, format="%d")

tot = amt_n + amt_s
pn = (amt_n / tot * 100) if tot > 0 else 0
ps = (amt_s / tot * 100) if tot > 0 else 0
st.info(f"💵 總預算: **${tot:,}**")

def c_pct(v):
    if v > 50: return "#FF0000"
    if v < 50: return "#00FF00"
    return "#FFFFFF"

cp1, cp2 = st.columns(2)
html_n = f"<span style='color:{c_pct(pn)};'>{pn:.1f}%</span>"
cp1.markdown(f"NDX: **{html_n}**", unsafe_allow_html=True)

html_s = f"<span style='color:{c_pct(ps)};'>{ps:.1f}%</span>"
cp2.markdown(f
