import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="投資趨勢監控", layout="centered")

# --- 進階 CSS：自定義不同狀態的漸層能量條 ---
st.markdown("""
    <style>
    /* 基礎字體與間距優化 */
    .price-font { font-size: 26px; font-weight: bold; }
    .status-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: -10px; }
    
    /* 移除原生進度條背景，自定義樣式由下方代碼動態注入 */
    .stProgress > div > div > div > div { background-image: var(--bar-gradient); }
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

def get_pct_color(val):
    if val > 50: return "#FF4B4B" # 紅色
    if val < 50: return "#00F000" # 綠色
    return "#FFFFFF" # 白色

col1, col2 = st.columns(2)
with col1:
    st.write("NDX (NASDAQ 100)")
    st.markdown(f"<span class='price-font'>${amt_ndx:,.0f}</span> <span style='color:{get_pct_color(p_ndx)}; font-size:20px;'>{p_ndx:.1f}%</span>", unsafe_allow_html=True)
with col2:
    st.write("SOX (費城半導體)")
    st.markdown(f"<span class='price-font'>${amt_sox:,.0f}</span> <span style='color:{get_pct_color(p_sox)}; font-size:20px;'>{p_sox:.1f}%</span>", unsafe_allow_html=True)

st.divider()

# 4. 趨勢監控
tickers = {"^NDX": "NASDAQ 100 指數", "^SOX": "費城半導體 指數"}

def fetch_data(symbol):
    try:
        df = yf.download(symbol, period="1y", progress=False)
        if df.empty: return None
        curr = float(df['Close'].iloc[-1])
        m60 = float(df['Close'].rolling(window=60).mean().iloc[-1])
        m240 = float(df['Close'].rolling(window=240).mean().iloc[-1])
        diff_pct = (curr - m60) / m60
        return curr, m60, m240, diff_pct
    except:
        return None

st.subheader("🔍 標的趨勢監控")
for code, name in tickers.items():
    res = fetch_data(code)
    if res:
        curr, m60, m240, diff = res
        st.write(f"### {name}")
        st.write(f"當前點數: **{curr:,.2f}**")
        
        # 燈號判定與漸層顏色設定
        diff_val = diff * 100
        if curr > m60:
            status, color, gradient = "🟢 綠燈 (季線之上)", "#00FF00", "linear-gradient(to right, #90EE90, #006400)"
        elif curr > m240:
            status, color, gradient = "🟡 黃燈 (跌破季線)", "#FFD700", "linear-gradient(to right, #FFFACD, #B8860B)"
        else:
            status, color, gradient = "🔴 紅燈 (跌破年線)", "#FF4B4B", "linear-gradient(to right, #FFB6C1, #8B0000)"
        
        # 動態注入該條能量條的漸層色
        st.markdown(f"<style>.stProgress > div > div > div > div {{ --bar-color: {color}; }}</style>", unsafe_allow_html=True)
        
        # 顯示狀態與乖離率
        st.markdown(f"""
            <div class="status-header">
                <span style="color:{color}; font-weight:bold; font-size:18px;">{status}</span>
                <span style="color:{color}; font-size:16px;">距季線: {diff_val:+.2f}%</span>
            </div>
            """, unsafe_allow_html=True)
        
        # 能量條長度邏輯：依照 0%~30% 的強度顯示 (乖離率絕對值越高越長)
        progress_val = min(max(abs(diff_val) / 30.0, 0.05), 1.0)
        st.progress(progress_val)
    else:
        st.error(f"無法取得 {name} 資料")
    st.write("---")
