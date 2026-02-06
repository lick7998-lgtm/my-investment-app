import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="投資趨勢監控", layout="centered")

# --- 進階 CSS：自定義高亮燈號與漸層能量條 ---
st.markdown("""
    <style>
    .price-font { font-size: 26px; font-weight: bold; }
    .status-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    
    /* 強制修改 Streamlit 進度條樣式 */
    div[data-testid="stProgress"] > div > div > div > div {
        background-image: var(--bar-gradient) !important;
        background-color: transparent !important;
        height: 12px;
        border-radius: 6px;
    }
    /* 進度條底色加深 */
    div[data-testid="stProgress"] > div > div {
        background-color: #333333 !important;
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

# 3. 佔比與顏色邏輯
st.subheader("📈 資產配置佔比")
p_ndx = (amt_ndx / total * 100) if total > 0 else 0
p_sox = (amt_sox / total * 100) if total > 0 else 0

def get_pct_color(val):
    if val > 50: return "#FF0000" # 純紅
    if val < 50: return "#00FF00" # 純綠
    return "#FFFFFF" # 白色

col1, col2 = st.columns(2)
with col1:
    st.write("NDX (NASDAQ 100)")
    st.markdown(f"<span class='price-font'>${amt_ndx:,}</span> <span style='color:{get_pct_color(p_ndx)}; font-size:20px;'>{p_ndx:.1f}%</span>", unsafe_allow_html=True)
with col2:
    st.write("SOX (費城半導體)")
    st.markdown(f"<span class='price-font'>${amt_sox:,}</span> <span style='color:{get_pct_color(p_sox)}; font-size:20px;'>{p_sox:.1f}%</span>", unsafe_allow_html=True)

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
    except: return None

st.subheader("🔍 標的趨勢監控")
for i, (code, name) in enumerate(tickers.items()):
    res = fetch_data(code)
    if res:
        curr, m60, m240, diff = res
        diff_val = diff * 100
        
        # 狀態燈號與「亮色到深色」漸層設定
        if curr > m60:
            status, color = "🟢 綠燈 (季線之上)", "#00FF00" # 螢光綠
            grad = "linear-gradient(to right, #CCFFCC, #00FF00, #006400)" # 淺 -> 亮 -> 深綠
        elif curr > m240:
            status, color = "🟡 黃燈 (跌破季線)", "#FFFF00" # 純黃
            grad = "linear-gradient(to right, #FFFFCC, #FFFF00, #8B8B00)" # 淺 -> 亮 -> 深黃
        else:
            status, color = "🔴 紅燈 (跌破年線)", "#FF0000" # 純紅
            grad = "linear-gradient(to right, #FFCCCC, #FF0000, #8B0000)" # 淺 -> 亮 -> 深紅
        
        # 為進度條注入動態 CSS
        st.markdown(f"<style>div[data-testid='stProgress']:nth-of-type({i+1}) div div div div {{ --bar-gradient: {grad}; }}</style>", unsafe_allow_html=True)

        st.write(f"### {name}")
        st.write(f"當前點數: **{curr:,.2f}**")
        
        # 顯示明亮燈號與距季線 %
        st.markdown(f"""
            <div class="status-header">
                <span style="color:{color}; font-weight:bold; font-size:20px; text-shadow: 0 0 5px {color};">{status}</span>
                <span style="color:{color}; font-size:18px;">距季線: {diff_val:+.2f}%</span>
            </div>
            """, unsafe_allow_html=True)
        
        # 能量條長度 (反映與季線的絕對距離強度)
        progress_val = min(max(abs(diff_val) / 30.0, 0.1), 1.0)
        st.progress(progress_val)
    else:
        st.error(f"無法取得 {name} 資料")
    st.write("---")
