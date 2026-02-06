import streamlit as st
import yfinance as yf
import pandas as pd

# 設定網頁標題
st.set_page_config(page_title="投資趨勢監控", layout="centered")

# --- 核心 CSS：實現完整能量條漸層與銳利字體 ---
st.markdown("""
    <style>
    /* 1. 文字銳利化：移除發光陰影 */
    .price-font { font-size: 26px; font-weight: bold; }
    .status-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    
    /* 2. 進度條容器：高度增加，讓漸層更明顯 */
    div[data-testid="stProgress"] {
        height: 30px !important;
    }

    /* 3. 進度條底槽：預設就帶有完整漸層色 (色光 30 -> 250) */
    div[data-testid="stProgress"] > div > div {
        background-color: #050505 !important;
        background-image: var(--bar-gradient) !important;
        height: 20px !important;
        border-radius: 10px !important;
        opacity: 0.3; /* 未達成部分顯示暗色調漸層 */
    }
    
    /* 4. 進度條達成部分：顯示高亮漸層 */
    div[data-testid="stProgress"] > div > div > div > div {
        background-image: var(--bar-gradient) !important;
        background-color: transparent !important;
        height: 20px !important;
        border-radius: 10px !important;
        opacity: 1.0; /* 達成部分顯示全亮漸層 */
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 ETF 趨勢監控 App")

# 1. 金額輸入 (移除小數點)
st.subheader("💰 投資金額輸入")
c_in1, c_in2 = st.columns(2)
with c_in1:
    amt_ndx = st.number_input("NDX 投入金額", min_value=0, value=30, step=1, format="%d")
with c_in2:
    amt_sox = st.number_input("SOX 投入金額", min_value=0, value=20, step=1, format="%d")

# 2. 自動加總
total = amt_ndx + amt_sox
st.info(f"💵 總預算 (自動加總): **${total:,}**")

st.divider()

# 3. 佔比與顏色邏輯 (大於50%紅, 小於50%綠)
st.subheader("📈 資產配置佔比")
p_ndx = (amt_ndx / total * 100) if total > 0 else 0
p_sox = (amt_sox / total * 100) if total > 0 else 0

def get_pct_color(val):
    if val > 50: return "#FF0000" # 色光 250 純紅
    if val < 50: return "#00FF00" # 色光 250 純綠
    return "#FFFFFF" 

col1, col2 = st.columns(2)
with col1:
    st.write("NDX (NASDAQ 100)")
    st.markdown(f"<span class='price-font'>${amt_ndx:,}</span> <span style='color:{get_pct_color(p_ndx)}; font-size:20px;'>{p_ndx:.1f}%</span>", unsafe_allow_html=True)
with col2:
    st.write("SOX (費城半導體)")
    st.markdown(f"<span class='price-font'>${amt_sox:,}</span> <span style='color:{get_pct_color(p_sox)}; font-size:20px;'>{p_sox:.1f}%</span>", unsafe_allow_html=True)

st.divider()

# 4. 趨勢監控 (指數代碼修正)
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
    except: return None

st.subheader("🔍 標的趨勢監控")
for i, (code, name) in enumerate(tickers.items()):
    res = fetch_data(code)
    if res:
        curr, m60, m240, diff = res
        diff_val = diff * 100
        
        # 精準色光漸層定義：色光 30 -> 250
        if curr > m60:
            status, color = "🟢 綠燈 (季線之上)", "#00FF00"
            grad = "linear-gradient(to right, #003300, #00FF00)" 
        elif curr > m240:
            status, color = "🟡 黃燈 (跌破季線)", "#FFFF00"
            grad = "linear-gradient(to right, #333300, #FFFF00)" 
        else:
            status, color = "🔴 紅燈 (跌破年線)", "#FF0000"
            grad = "linear-gradient(to right, #330000, #FF0000)" 
        
        # 注入 CSS：確保整條進度條都套用這個漸層
        st.markdown(f"<style>div[data-testid='stProgress']:nth-of-type({i+1}) {{ --bar-gradient: {grad}; }}</style>", unsafe_allow_html=True)

        st.write(f"### {name}")
        st.write(f"當前點數: **{curr:,.2f}**")
        
        # 文字採用純高飽和色 (色光 250)
        st.markdown(f"""
            <div class="status-header">
                <span style="color:{color}; font-weight:bold; font-size:20px;">{status}</span>
                <span style="color:{color}; font-size:18px;">距季線: {diff_val:+.2f}%</span>
            </div>
            """, unsafe_allow_html=True)
        
        # 能量條長度：映射乖離強度 (若需測試「全滿」，可將此值設為 1.0)
        progress_val = min(max(abs(diff_val) / 30.0, 0.1), 1.0)
        st.progress(progress_val)
    else:
        st.error(f"無法取得 {name} 資料")
    st.write("---")
