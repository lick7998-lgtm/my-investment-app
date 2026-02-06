import streamlit as st
import yfinance as yf
import pandas as pd

# 設定網頁標題與圖示
st.set_page_config(page_title="投資監控", layout="centered")

st.title("📊 ETF 趨勢監控")

# 1. 自行輸入初始金額 (放在主畫面最上方，方便手機操作)
initial_capital = st.number_input("💰 請輸入總投資預算 (USD)", min_value=0, value=10000, step=1000)

# 2. 顯示佔比 (目前設定各 50%，你可以隨時手動改金額)
st.subheader("📈 資產配置佔比")
col1, col2 = st.columns(2)
with col1:
    st.metric("NDX (50%)", f"${initial_capital * 0.5:,.0f}")
with col2:
    st.metric("SOX (50%)", f"${initial_capital * 0.5:,.0f}")

st.divider()

# 定義標的 (修正代碼：NDX -> QQQ, SOX -> SOXX 較為穩定)
# 你也可以在介面上改成讓你自己輸入代碼
tickers = ["QQQ", "SOXX"] 

def get_status(ticker):
    try:
        # 抓取數據
        df = yf.download(ticker, period="1y", interval="1d")
        if df.empty: return None
        
        # 取得最後一列數據
        current_price = float(df['Close'].iloc[-1])
        # 計算 60日(季線) 與 240日(年線)
        ma60 = float(df['Close'].rolling(window=60).mean().iloc[-1])
        ma240 = float(df['Close'].rolling(window=240).mean().iloc[-1])
        
        if current_price > ma60:
            return "🟢 綠燈 (季線之上)", current_price
        elif current_price > ma240:
            return "🟡 黃燈 (跌破季線)", current_price
        else:
            return "🔴 紅燈 (跌破年線)", current_price
    except:
        return None, None

st.subheader("🔍 標的趨勢監控")

for t in tickers:
    status, price = get_status(t)
    # 使用卡片式設計，更適合手機觀看
    with st.container():
        st.write(f"### {t}")
        if status:
            st.info(f"當前價格: **{price:.2f}**")
            st.success(status) if "🟢" in status else (st.warning(status) if "🟡" in status else st.error(status))
        else:
            st.error(f"暫時無法取得 {t} 數據")
    st.write("")
