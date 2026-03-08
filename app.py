import streamlit as st
import yfinance as yf
import pandas as pd

# 設定網頁標題與佈局
st.set_page_config(page_title="投資趨勢監控系統", layout="wide")

# --- 核心 CSS ---
st.markdown("""
<style>
* { text-shadow: none !important; -webkit-font-smoothing: antialiased; }
.metric-title { font-size: 26px; font-weight: 700; margin-bottom: 5px; }
.value-text { font-size: 22px; font-weight: 600; margin-bottom: 5px; }
.energy-bar-container { background-color: #0d0d0d; border-radius: 8px; width: 100%; height: 26px; margin-top: 10px; overflow: hidden; border: 1px solid #333; }
.energy-bar-fill { height: 26px; border-radius: 8px; transition: width 0.6s ease-in-out; }
</style>
""", unsafe_allow_html=True)

# --- 資料抓取與計算 (加入備援機制) ---
@st.cache_data(ttl=300)
def fetch_index_data(symbol, backup_symbol=None):
    try:
        data = yf.download(symbol, period="2y", progress=False)
        # 如果主要符號失敗且有備援符號，嘗試備援
        if (data.empty or len(data) < 240) and backup_symbol:
            data = yf.download(backup_symbol, period="2y", progress=False)
        
        if data.empty: return None
        
        current = float(data["Close"].iloc[-1])
        ma60 = float(data["Close"].rolling(60).mean().iloc[-1])
        ma240 = float(data["Close"].rolling(240).mean().iloc[-1])
        pct = ((current - ma60) / ma60) * 100
        return current, ma60, ma240, pct
    except Exception:
        return None

# --- 顏色與漸層配置 ---
def get_style_config(pct, current, ma240):
    if current < ma240:
        status, color_hex = "🔴 紅燈 (跌破年線)", "#FF0000"
        grad = "linear-gradient(to right, rgb(100,0,0), rgb(250,0,0))"
    elif pct < 0:
        status, color_hex = "🟡 黃燈 (跌破季線)", "#FFFF00"
        grad = "linear-gradient(to right, rgb(100,100,0), rgb(250,250,0))"
    else:
        status, color_hex = "🟢 綠燈 (季線之上)", "#00FF00"
        grad = "linear-gradient(to right, rgb(0,100,0), rgb(0,250,0))"
    return status, color_hex, grad

st.title("📡 投資趨勢監控系統")

# 1. 投資金額輸入
st.subheader("💰 投資金額輸入")
col_in1, col_in2, col_in3, col_in4 = st.columns(4)
with col_in1:
    amt_ndx = st.number_input("NDX 金額 (USD)", min_value=0, value=0, step=100)
with col_in2:
    amt_sox = st.number_input("SOX 金額 (USD)", min_value=0, value=0, step=100)
with col_in3:
    amt_bond = st.number_input("債券金額 (USD)", min_value=0, value=0, step=100)
with col_in4:
    amt_gold = st.number_input("黃金金額 (USD)", min_value=0, value=0, step=100)

# 2. 自動加總與佔比
total = amt_ndx + amt_sox + amt_bond + amt_gold
st.info(f"💵 總投資預算 (自動加總): **${total:,}**")

if total > 0:
    p_ndx, p_sox = (amt_ndx/total)*100, (amt_sox/total)*100
    p_bond, p_gold = (amt_bond/total)*100, (amt_gold/total)*100
    c_p = st.columns(4)
    r_colors = [("#FF4B4B" if p > 40 else "#00FF00") for p in [p_ndx, p_sox, p_bond, p_gold]]
    labels = ["NDX 佔比", "SOX 佔比", "債券 佔比", "黃金 佔比"]
    percents = [p_ndx, p_sox, p_bond, p_gold]
    for i in range(4):
        c_p[i].markdown(f"{labels[i]}<br><span style='color:{r_colors[i]}; font-size:24px; font-weight:bold;'>{percents[i]:.1f}%</span>", unsafe_allow_html=True)

st.divider()

# 4. 指數監控 (2x3 佈局)
# 定義標的與對應的備援符號 (QQQ 為 NDX 備援, SOXX 為 SOX 備援)
tickers = [
    {"sym": "^NDX", "back": "QQQ", "name": "NASDAQ 100 (NDX)"},
    {"sym": "^SOX", "back": "SOXX", "name": "費城半導體 (SOX)"},
    {"sym": "GC=F", "back": None, "name": "國際黃金 (GC=F)"},
    {"sym": "GDX", "back": None, "name": "黃金礦業 ETF (GDX)"},
    {"sym": "CL=F", "back": None, "name": "紐約輕原油 (WTI)"},
    {"sym": "BZ=F", "back": None, "name": "布蘭特原油 (BRENT)"}
]

for i in range(0, len(tickers), 2):
    cols = st.columns(2)
    for j in range(2):
        if i + j < len(tickers):
            t = tickers[i + j]
            with cols[j]:
                res = fetch_index_data(t["sym"], t["back"])
                if res:
                    curr, m60, m240, pct = res
                    status_text, h_color, bar_grad = get_style_config(pct, curr, m240)
                    
                    # 格式化
                    if t["sym"] in ["GC=F", "GDX", "CL=F", "BZ=F"]:
                        v_curr, v_m60, v_m240 = f"{curr:,.2f}", f"{m60:,.2f}", f"{m240:,.2f}"
                    else:
                        v_curr, v_m60, v_m240 = f"{int(curr):,}", f"{int(m60):,}", f"{int(m240):,}"
                    
                    st.markdown(f"<div class='metric-title' style='color:{h_color};'>{t['name']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='value-text' style='color:{h_color};'>當前報價：{v_curr}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='value-text' style='color:{h_color};'>季線 MA60：{v_m60}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='value-text' style='color:{h_color};'>年線 MA240：{v_m240}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='color:{h_color}; font-weight:bold; font-size:20px; margin-top:10px; display:flex; justify-content:space-between;'>"
                                f"<span>{status_text}</span><span>距季線：{pct:+.2f}%</span></div>", unsafe_allow_html=True)
                    fill_width = min(max(abs(pct), 5.0), 40.0) 
                    st.markdown(f"<div class='energy-bar-container'><div class='energy-bar-fill' style='width: {fill_width}%; background: {bar_grad};'></div></div>", unsafe_allow_html=True)
                else:
                    st.error(f"無法獲取 {t['name']} 數據")
    st.write("<br>", unsafe_allow_html=True)
