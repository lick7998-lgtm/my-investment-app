import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="ETF 趨勢監控", layout="centered")

st.title("📊 ETF 趨勢監控 App")

# 1. 讓使用者自行輸入兩標的的金額
st.subheader("💰 投資金額輸入")
col_input1, col_input2 = st.columns(2)

with col_input1:
    amt_ndx = st.number_input("NDX 投入金額", min_value=0.0, value=30.0, step=10.0)
with col_input2:
    amt_sox = st.number_input("SOX 投入金額", min_value=0.0, value=30.0, step=10.0)

# 2. 自動加總並計算佔比
total_capital = amt_ndx + amt_sox
st.info(f"💵 總預算自動加總：**${total_capital:,.2f}**")

st.divider()

# 3. 顯示資產配置佔比
st.subheader("📈 資產配置佔比")
pct_ndx = (amt_ndx / total_capital * 100) if total_capital > 0 else 0
pct_sox = (amt_sox / total_capital * 100) if total_capital > 0 else 0

c1, c2 = st.columns(2)
c1.metric("NDX (NASDAQ 100)", f"${amt_ndx:,.0f}", f"{pct_ndx:.1f}%")
c2.metric("SOX (費城半導體)", f"${amt_sox:,.0f}", f"{pct_sox:.1f}%")

st.divider()

# 4. 趨勢監控 (使用正確的指數代碼)
# NDX 指數代碼為 ^NDX, SOX 指數代碼為 ^SOX
tickers = {
    "^NDX": "NASDAQ 100 指數",
    "^SOX": "費城半導體 指數"
}

def get_status(ticker_code):
    try:
        data = yf.download(ticker_code, period="1y")
        if data.empty: return None
        
        current_price = float(data['Close'].iloc[-1])
        ma60 = float(data['Close'].rolling(window=60).mean().iloc[-1])
        ma240 = float(data['Close'].rolling(window=240).mean().iloc[-1])
        
        if current_price > ma60:
            return "🟢 綠燈 (季線之上)", current_price
        elif current_price > ma240:
            return "🟡 黃燈 (跌破季線)", current_price
        else:
            return "🔴 紅燈 (跌破年線)", current_price
    except:
        return None, None

st.subheader("🔍 標的趨勢監控")
for code, name in tickers.items():
    status, price = get_status(code)
    with st.container():
        st.write(f"### {name} ({code})")
        if status:
            st.write(f"當前點數: **{price:,.2f}**")
            if "🟢" in status: st.success(status)
            elif "🟡" in status: st.warning(status)
            else: st.error(status)
        else:
            st.error(f"無法取得 {name} 數據，請稍後再試")
    st.write("---")
