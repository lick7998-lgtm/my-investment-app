import streamlit as st
import yfinance as yf
import pandas as pd
import math

# --- 網頁 CSS ---
st.set_page_config(page_title="投資趨勢監控系統", layout="wide")
st.markdown("""
<style>
* { text-shadow: none !important; -webkit-font-smoothing: antialiased; }
.metric-title { font-size: 26px; font-weight: 700; margin-bottom: 5px; }
.value-text { font-size: 22px; font-weight: 600; margin-bottom: 5px; }
.formula-text { font-size: 16px; font-weight: 500; color: #AAAAAA; margin-bottom: 8px; }
.energy-bar-container { background-color: #0d0d0d; border-radius: 8px; width: 100%; height: 26px; margin-top: 10px; overflow: hidden; border: 1px solid #333; }
.energy-bar-fill { height: 26px; border-radius: 8px; transition: width 0.6s ease-in-out; }
</style>
""", unsafe_allow_html=True)

# ===============================
# 🚀 安全抓價
# ===============================
def safe_price(ticker):
    try:
        tk = yf.Ticker(ticker)
        
        # fast_info
        try:
            info = tk.fast_info
            price = getattr(info, "lastPrice", None)
            if price is not None and not pd.isna(price): return float(price)
            price_prev = getattr(info, "previousClose", None)
            if price_prev is not None and not pd.isna(price_prev): return float(price_prev)
        except:
            pass
        
        # history fallback
        hist = tk.history(period="30d", progress=False)
        if not hist.empty and 'Close' in hist.columns:
            clean_hist = hist['Close'].dropna()
            if not clean_hist.empty:
                return float(clean_hist.iloc[-1])
    except:
        return None
    return None

# ===============================
# 🟢 NDX/SOX/GDX 歷史 + 均線
# ===============================
def fetch_index_data(symbol):
    try:
        df = yf.download(symbol, period="2y", progress=False)
        if df.empty: return None
        close_series = df['Close'].dropna()
        current = float(close_series.iloc[-1])
        ma60 = float(close_series.rolling(60).mean().dropna().iloc[-1])
        ma240 = float(close_series.rolling(240).mean().dropna().iloc[-1])
        pct = ((current - ma60) / ma60) * 100
        return current, ma60, ma240, pct
    except:
        return None

def get_style_config(pct, current, ma240):
    if current < ma240: 
        return "🔴 紅燈 (跌破年線)", "#FF0000", "linear-gradient(to right, rgb(100,0,0), rgb(250,0,0))"
    elif pct < 0: 
        return "🟡 黃燈 (跌破季線)", "#FFFF00", "linear-gradient(to right, rgb(100,100,0), rgb(250,250,0))"
    else: 
        return "🟢 綠燈 (季線之上)", "#00FF00", "linear-gradient(to right, rgb(0,100,0), rgb(0,250,0))"

# ===============================
# 🟡 XAUD 計算
# ===============================
def get_XAUD():
    xau_usd = safe_price("XAUUSD=X")
    aud_usd = safe_price("AUDUSD=X")
    
    if xau_usd is None or aud_usd is None:
        return None, "無法取得 XAUUSD 或 AUDUSD"
    
    usdaud = 1 / aud_usd
    xaud = int(xau_usd * usdaud)
    return xaud, None

# ===============================
# UI
# ===============================
st.title("📡 投資趨勢監控系統")

# 投入金額
col1, col2 = st.columns(2)
with col1:
    amt_ndx = st.number_input("NDX 投入金額 (USD)", min_value=0, value=0, step=1)
with col2:
    amt_sox = st.number_input("SOX 投入金額 (USD)", min_value=0, value=0, step=1)
total = amt_ndx + amt_sox
st.info(f"💵 總預算: ${total:,}")

# 指數列表
tickers = [
    ("^NDX", "NASDAQ 100 (NDX)"), 
    ("^SOX", "費城半導體 (SOX)"),
    ("XAUD_CUSTOM", "黃金現貨 (XAUD)"),
    ("GDX", "黃金礦業 ETF (GDX)")
]

for i in range(0, len(tickers), 2):
    cols = st.columns(2)
    for j in range(2):
        if i + j < len(tickers):
            symbol, name = tickers[i + j]
            with cols[j]:
                if symbol == "XAUD_CUSTOM":
                    xaud_val, err = get_XAUD()
                    if err:
                        st.error(err)
                    else:
                        html = f"""
                        <div class='metric-title' style='color:#FFD700;'>{name}</div>
                        <div class='value-text' style='font-size:28px;'>當前報價：{xaud_val:,}</div>
                        """
                        st.markdown(html, unsafe_allow_html=True)
                else:
                    res = fetch_index_data(symbol)
                    if res:
                        curr, m60, m240, pct = res
                        status_text, h_color, bar_grad = get_style_config(pct, curr, m240)
                        html = f"""
                        <div class='metric-title' style='color:{h_color};'>{name}</div>
                        <div class='value-text' style='color:{h_color};'>當前報價：{int(curr):,}</div>
                        <div class='value-text' style='color:{h_color};'>季線 MA60：{int(m60):,}</div>
                        <div class='value-text' style='color:{h_color};'>年線 MA240：{int(m240):,}</div>
                        <div style='color:{h_color}; font-weight:bold; font-size:20px; margin-top:10px; display:flex; justify-content:space-between;'>
                            <span>{status_text}</span>
                            <span>距季線：{pct:+.2f}%</span>
                        </div>
                        <div class='energy-bar-container'>
                            <div class='energy-bar-fill' style='width:{min(max(abs(pct),5),40)}%; background:{bar_grad};'></div>
                        </div>
                        """
                        st.markdown(html, unsafe_allow_html=True)
                    else:
                        st.error(f"無法獲取 {name} 數據，請稍後再試。")
    st.write("<br>", unsafe_allow_html=True)
