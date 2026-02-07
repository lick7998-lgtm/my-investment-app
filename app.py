import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="NDX & SOX Monitor", layout="wide")

# --- CSS：確保字體銳利 + 能量條樣式 ---
st.markdown("""
<style>
* { text-shadow: none !important; -webkit-font-smoothing: antialiased; }
.metric-title { font-size: 24px; font-weight: 700; color: white; }
.value-text { font-size: 20px; font-weight: 500; color: #E0E0E0; }
.energy-bar-container { background-color: #1a1a1a; border-radius: 8px; width: 100%; height: 24px; margin-top: 8px; overflow: hidden; }
.energy-bar-fill { height: 24px; border-radius: 8px; transition: width 0.6s ease-in-out; }
</style>
""", unsafe_allow_html=True)

# --- 資料抓取與計算 ---
def fetch_index_data(symbol):
    try:
        # 抓取足夠資料計算 MA240
        data = yf.download(symbol, period="2y", progress=False)
        if data.empty: return None
        
        # 確保取到最後一個有效的標量值
        current = float(data["Close"].iloc[-1].item())
        ma60 = float(data["Close"].rolling(60).mean().iloc[-1].item())
        ma240 = float(data["Close"].rolling(240).mean().iloc[-1].item())
        
        pct = ((current - ma60) / ma60) * 100
        return current, ma60, ma240, pct
    except Exception as e:
        return None

# --- 顏色與漸層邏輯 (100 -> 250) ---
def get_style_config(pct, current, ma240):
    # 燈號邏輯判斷
    if current < ma240: # 跌破年線 -> 紅燈
        status, color_end = "🔴 紅燈 (跌破年線)", "rgb(250,0,0)"
        grad = "linear-gradient(to right, rgb(100,0,0), rgb(250,0,0))"
    elif pct < 0: # 跌破季線 -> 黃燈
        status, color_end = "🟡 黃燈 (跌破季線)", "rgb(250,250,0)"
        grad = "linear-gradient(to right, rgb(100,100,0), rgb(250,250,0))"
    else: # 季線之上 -> 綠燈
        status, color_end = "🟢 綠燈 (季線之上)", "rgb(0,250,0)"
        grad = "linear-gradient(to right, rgb(0,100,0), rgb(0,250,0))"
    return status, color_end, grad

# --- UI 介面 ---
st.title("📡 NDX & SOX 指數監控系統")

# 1. 投資金額輸入 (整數格式)
st.subheader("💰 投資金額輸入")
col_in1, col_in2 = st.columns(2)
with col_in1:
    amt_ndx = st.number_input("NDX 投入金額 (USD)", min_value=0, value=0, step=1, format="%d")
with col_in2:
    amt_sox = st.number_input("SOX 投入金額 (USD)", min_value=0, value=0, step=1, format="%d")

# 2. 自動加總與比例計算
total = amt_ndx + amt_sox
p_ndx = (amt_ndx / total * 100) if total > 0 else 0
p_sox = (amt_sox / total * 100) if total > 0 else 0

st.info(f"💵 總預算 (自動加總): **${total:,}**")

# 3. 顯示佔比 (顏色邏輯: >50紅, <50綠)
def ratio_color(val):
    if val > 50: return "#FF0000"
    if val < 50: return "#00FF00"
    return "#FFFFFF"

c_p1, c_p2 = st.columns(2)
c_p1.markdown(f"NDX 佔比：<span style='color:{ratio_color(p_ndx)}; font-size:22px; font-weight:bold;'>{p_ndx:.1f}%</span>", unsafe_allow_html=True)
c_p2.markdown(f"SOX 佔比：<span style='color:{ratio_color(p_sox)}; font-size:22px; font-weight:bold;'>{p_sox:.1f}%</span>", unsafe_allow_html=True)

st.divider()

# 4. 指數監控與能量條
tickers = {"^NDX": "NASDAQ 100 (NDX)", "^SOX": "費城半導體 (SOX)"}
col_display1, col_display2 = st.columns(2)

for i, (symbol, display_name) in enumerate(tickers.items()):
    res = fetch_index_data(symbol)
    with (col_display1 if i == 0 else col_display2):
        if res:
            curr, m60, m240, pct = res
            status_text, highlight_color, bar_gradient = get_style_config(pct, curr, m240)
            
            st.markdown(f"<div class='metric-title'>{display_name}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='value-text'>當前點數：{curr:,.2f}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='value-text'>季線 MA60：{m60:,.2f}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='value-text'>年線 MA240：{m240:,.2f}</div>", unsafe_allow_html=True)
            
            # 顯示燈號與距季線百分比
            st.markdown(f"<div style='color:{highlight_color}; font-weight:bold; font-size:18px; margin-top:10px; display:flex; justify-content:space-between;'>"
                        f"<span>{status_text}</span>"
                        f"<span>距季線：{pct:+.2f}%</span></div>", unsafe_allow_html=True)
            
            # 能量條 (長度連動 % 數，上限 40%)
            fill_width = min(abs(pct), 40.0)
            st.markdown(f"""
                <div class='energy-bar-container'>
                    <div class='energy-bar-fill' style='width: {fill_width}%; background: {bar_gradient};'></div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"無法獲取 {display_name} 的即時行情")
