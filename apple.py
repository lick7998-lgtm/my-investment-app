import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="投資趨勢監控", layout="centered")

# 自定義 CSS 來達成能量條漸層效果
st.markdown("""
    <style>
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #e0e0e0 , var(--bar-color));
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 ETF 趨勢監控 App")

# 1. 填寫個別金額
st.subheader("💰 投資金額輸入")
col_in1, col_in2 = st.columns(2)
with col_in1:
    amt_ndx = st.number_input("NDX 投入金額", min_value=0.0, value=30.0, step=1.0)
with col_in2:
    amt_sox = st.number_input("SOX 投入金額", min_value=0.0, value=30.0, step=1.0)

# 2. 自動加總
total_sum = amt_ndx + amt_sox
st.info(f"💵 總預算 (自動加總): **${total_sum:,.2f}**")

st.divider()

# 3. 資產配置佔比與顏色邏輯
st.subheader("📈 資產配置佔比")
p_ndx = (amt_ndx / total_sum * 100) if total_sum > 0 else 0
p_sox = (amt_sox / total_sum * 100) if total_sum > 0 else 0

def get_pct_color(val):
    if val > 50: return "#FF4B4B" # 紅色
    if val < 50: return "#00F000" # 綠色
    return "#FFFFFF" # 白色

c1, c2 = st.columns(2)
# 使用 HTML 達成 % 放右邊與顏色自訂
c1.markdown(f"NDX (NASDAQ 100)<br><span style='font-size:24px; font-weight:bold;'>${amt_ndx:,.0f}</span> <span style='color:{get_pct_color(p_ndx)}; font-size:18px;'>{p_ndx:.1f}%</span>", unsafe_allow_html=True)
c2.markdown(f"SOX (費城半導體)<br><span style='font-size:24px; font-weight:bold;'>${amt_sox:,.0f}</span> <span style='color:{get_pct_color(p_sox)}; font-size:18px;'>{p_sox:.1f}%</span>", unsafe_allow_html=True)

st.divider()

# 4. 趨勢監控與能量條
tickers = {"^NDX": "NASDAQ 100 指數", "^SOX": "費城半導體 指數"}

def get_data(symbol):
    df = yf.download(symbol, period="1y")
    if df.empty: return None
    curr = float(df['Close'].iloc[-1])
    m60 = float(df['Close'].rolling(window=60).mean().iloc[-1])
    m240 = float(df['Close'].rolling(window=240).mean().iloc[-1])
    return curr, m60, m240

st.subheader("🔍 標的趨勢監控")
for code, name in tickers.items():
    res = get_data(code)
    if res:
        curr, m60, m240 = res
        st.write(f"### {name}")
        st.write(f"當前點數: **{curr:,.2f}**")
        
        # 判斷燈號與能量條顏色
        if curr > m60:
            lbl, color, hex_c = "🟢 綠燈 (季線之上)", "green", "#008000"
        elif curr > m240:
            lbl, color, hex_c = "🟡 黃燈 (跌破季線)", "orange", "#FFD700"
        else:
            lbl, color, hex_c = "🔴 紅燈 (跌破年線)", "red", "#FF0000"
        
        # 顯示燈號文字
        st.markdown(f"<span style='color:{hex_c}; font-weight:bold;'>{lbl}</span>", unsafe_allow_html=True)
        # 顯示能量條 (模擬 0-30% 漸層)
        st.progress(0.3) # 固定顯示 30% 長度如你要求
    else:
        st.error(f"無法取得 {name} 資料")
    st.write("---")
