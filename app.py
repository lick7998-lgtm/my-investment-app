import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="ETF 投資監控助手", layout="wide")

st.title("📊 ETF 趨勢監控 App")

# 1. 自行輸入初始金額
with st.sidebar:
    st.header("參數設定")
    initial_capital = st.number_input("請輸入初始投資金額 (USD)", min_value=0, value=10000, step=1000)
    st.write(f"當前總預算：${initial_capital:,.0f}")

# 定義標的
tickers = ["NDX", "SOX"] # 註：yfinance 常用代碼，若為特定券商代碼請自行更換

def get_status(ticker):
    # 抓取歷史數據 (至少需要一年以上來計算年線)
    data = yf.download(ticker, period="1y")
    if data.empty:
        return None
    
    current_price = data['Close'].iloc[-1]
    ma60 = data['Close'].rolling(window=60).mean().iloc[-1]
    ma240 = data['Close'].rolling(window=240).mean().iloc[-1]
    
    # 燈號邏輯
    if current_price > ma60:
        status = "🟢 綠燈 (強勢：季線之上)"
    elif current_price > ma240:
        status = "🟡 黃燈 (警戒：跌破季線)"
    else:
        status = "🔴 紅燈 (危險：跌破年線)"
        
    return {
        "現價": round(current_price, 2),
        "季線": round(ma60, 2),
        "年線": round(ma240, 2),
        "狀態": status
    }

# 2. 顯示兩檔佔比 (假設目前採平均分配 50/50，可依需求調整)
st.subheader("📈 資產配置佔比")
col1, col2 = st.columns(2)
with col1:
    st.metric("NDX 預計投入", f"${initial_capital * 0.5:,.0f}", "50%")
with col2:
    st.metric("SOX 預計投入", f"${initial_capital * 0.5:,.0f}", "50%")

# 3. 查股價位置與燈號
st.divider()
st.subheader("🔍 標的趨勢監控")

for t in tickers:
    info = get_status(t)
    if info:
        with st.expander(f"查看 {t} 詳細數據", expanded=True):
            c1, c2, c3, c4 = st.columns(4)
            c1.write(f"**標的: {t}**")
            c2.write(f"目前股價: {info['現價']}")
            c3.write(f"燈號狀態: {info['狀態']}")
            c4.progress(100 if "🟢" in info['狀態'] else (50 if "🟡" in info['狀態'] else 10))
    else:
        st.error(f"無法取得 {t} 的數據，請檢查代碼是否正確。")

