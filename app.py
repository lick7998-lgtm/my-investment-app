import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="投資趨勢監控", layout="centered")

# CSS 優化介面
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #4facfe 0%, #00f2fe 100%); }
    .price-text { font-size: 28px; font-weight: bold; margin-right: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 ETF 趨勢監控 App")

# 1. 金額輸入
st.subheader("💰 投資金額輸入")
c_in1, c_in2 = st.columns(2)
with c_in1:
    amt_ndx = st.number_input("NDX 投入金額", min_value=0.0, value=30.0, step=1.0)
with c_in2:
    amt_sox = st.number_input("SOX 投入金額", min_value=0.0, value=30.0, step=1.0)

# 2. 自動加總
total = amt_ndx + amt_sox
st.info(f"💵 總預算 (自動加總): **${total:,.2f}**")

st.divider()

# 3. 佔比與顏色邏輯
st.subheader("📈 資產配置佔比")
p_ndx = (amt_ndx / total * 100) if total > 0 else 0
p_sox = (amt_sox / total * 100) if total > 0 else 0

def get_color(val):
    if val > 50: return "#FF4B4B" # 紅色
    if val < 50: return "#00F000" # 綠色
    return "#FFFFFF" # 白色

col1, col2 = st.columns(2)
with col1:
    st.write("NDX (NASDAQ 100)")
    st.markdown(f"<span class='price-text'>${amt_ndx:,.0f}</span><span style='color:{get_color(p_ndx)}; font-size:20px;'>{p_ndx:.1f}%</span>", unsafe_allow_html=True)
with col2:
    st.write("SOX (費城半導體)")
    st.markdown(f"<span class='price-text'>${amt_sox:,.0f}</span><span style='color:{get_color(p_sox)}; font-size:20px;'>{p_sox:.1f}%</span>", unsafe_allow_html=True)

st.divider()

# 4. 趨勢監控 (修正代碼與能量條)
tickers = {"^NDX": "NASDAQ 100 指數", "^SOX": "費城半導體 指數"}

def fetch_data(symbol):
    df = yf.download(symbol, period="1y")
    if df.empty: return None
    curr = float(df['Close'].iloc[-1])
    m60 = float(df['Close'].rolling(window=60).mean().iloc[-1])
    m240 = float(df['Close'].rolling(window=240).mean().iloc[-1])
    diff_pct = ((curr - m60) / m60) # 與季線的差距
    return curr, m60, m240, diff_pct

st.subheader("🔍 標的趨勢監控")
for code, name in tickers.items():
    res = fetch_data(code)
    if res:
        curr, m60, m240, diff = res
        st.write(f"### {name}")
        st.write(f"當前點數: **{curr:,.2f}**")
        
        # 燈號判定
        if curr > m60:
            status, color = "🟢 綠燈 (季線之上)", "#00FF00"
        elif curr > m240:
            status, color = "🟡 黃燈 (跌破季線)", "#FFD700"
        else:
            status, color = "🔴 紅燈 (跌破年線)", "#FF4B4B"
        
        # 顯示燈號與乖離率 %
        st.markdown(f"<div style='display:flex; justify-content:space-between;'><span style='color:{color}; font-weight:bold;'>{status}</span><span style='color:{color};'>乖離率: {diff*100:+.2f}%</span></div>", unsafe_allow_html=True)
        
        # 能量條: 限制在 0-1 之間顯示，這裏模擬強度
        progress_val = min(max((diff + 0.15) / 0.
