import streamlit as st
import yfinance as yf
import pandas as pd

st.title("黃金現貨自動換算工具（支援 USD 與 AUD）")

# === 1. 讓使用者選擇黃金計價貨幣 ===
option = st.selectbox("選擇黃金報價類型：", [
    "XAUUSD（黃金 / 美元）",
    "XAUAUD（黃金 / 澳幣）"
])

if option.startswith("XAUUSD"):
    ticker_code = "XAUUSD=X"
    currency = "USD"
else:
    ticker_code = "XAUAUD=X"
    currency = "AUD"

st.write(f"正在取得黃金報價（{currency} 計價）...")

# === 2. 下載黃金現貨 ===
ticker = yf.Ticker(ticker_code)
data = ticker.history(period="1d")

if data.empty:
    st.error("無法取得黃金現貨資料，請稍後再試。")
    st.stop()

xau_price = data["Close"].iloc[-1]   # 黃金每盎司（以 USD 或 AUD 計價）
st.subheader(f"最新黃金報價：{xau_price:,.2f} {currency} / oz")

# === 3. 取得匯率（轉成 TWD） ===

if currency == "USD":
    fx_code = "TWD=X"        # USD → TWD
else:
    fx_code = "AUDTWD=X"     # AUD → TWD（Yahoo Finance 正確代碼）

fx = yf.Ticker(fx_code)
fx_data = fx.history(period="1d")

if fx_data.empty:
    st.error("無法取得匯率資料")
    st.stop()

rate_to_twd = fx_data["Close"].iloc[-1]
st.write(f"目前 {currency} → TWD 匯率：{rate_to_twd:.2f}")

# === 4. 換算為台幣 ===
price_twd_oz = xau_price * rate_to_twd
price_twd_g = price_twd_oz / 31.1034768
price_twd_tael = price_twd_g * 37.5

st.subheader("📌 換算結果（新台幣）")
st.write(f"每盎司（oz）：NT$ {price_twd_oz:,.0f}")
st.write(f"每克（g）：NT$ {price_twd_g:,.2f}")
st.write(f"每台兩：NT$ {price_twd_tael:,.0f}")

# 表格
result = pd.DataFrame({
    "單位": ["盎司(oz)", "克(g)", "台兩"],
    "價格 (TWD)": [price_twd_oz, price_twd_g, price_twd_tael]
})

st.table(result)
