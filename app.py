import streamlit as st
import yfinance as yf
import pandas as pd

# ==========================
# Utility: Rounded gradient color
# ==========================
def gradient_color(base_color, intensity):
    # intensity 0~1 對應亮度 100~250
    light = int(100 + intensity * 150)
    return f"rgb({base_color[0]},{base_color[1]},{light})"


# ==========================
# Fetch data with fallback
# ==========================
def fetch_price(ticker):
    try:
        data = yf.download(ticker, period="2y")
        data.dropna(inplace=True)
        return data
    except:
        return None


# ==========================
# Moving Average + Signal Color
# ==========================
def compute_signals(df):
    df["MA60"] = df["Close"].rolling(60).mean()
    df["MA240"] = df["Close"].rolling(240).mean()

    price = df["Close"].iloc[-1]
    ma60 = df["MA60"].iloc[-1]
    ma240 = df["MA240"].iloc[-1]

    if price > ma60:
        signal = "green"
        label = "季線之上"
    elif price > ma240:
        signal = "yellow"
        label = "跌破季線"
    else:
        signal = "red"
        label = "跌破年線"

    # 計算與季線距離
    pct_from_ma = (price - ma60) / ma60 * 100 if ma60 > 0 else 0
    pct_from_ma = max(min(pct_from_ma, 50), -50)

    bar_ratio = abs(pct_from_ma) / 50  # 最大 50%

    return price, ma60, ma240, signal, label, pct_from_ma, bar_ratio


# ==========================
# Circular Signal Icon CSS
# ==========================
def render_signal(color):
    return f"""
        <div style="
            width:18px;height:18px;border-radius:50%;
            background:{color};
            display:inline-block;margin-right:6px;
        "></div>
    """


# ==========================
# SECTION: Begin Streamlit UI
# ==========================
st.set_page_config(page_title="Investment Dashboard", layout="wide")
st.markdown("""
    <style>
        * { text-shadow: none !important; }
        .title { font-size:28px; font-weight:700; }
        .block { padding:16px; border-radius:12px; background:#111; margin-bottom:18px; }
        .value { font-size:22px; font-weight:600; }
        .label { font-size:14px; opacity:0.7; }
        .bar {
            height: 22px;
            border-radius: 10px;
            margin-top: 4px;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📈 投資儀表板（自動換算 XAUD → XAUUSD）</div>', unsafe_allow_html=True)
st.write("---")

# ==========================
# Manual Inputs
# ==========================
colA, colB = st.columns(2)
with colA:
    invest_ndx = st.number_input("NDX 投入金額", min_value=0, value=0, step=100)
with colB:
    invest_sox = st.number_input("SOX 投入金額", min_value=0, value=0, step=100)

total = invest_ndx + invest_sox
pct_ndx = invest_ndx / total * 100 if total > 0 else 0
pct_sox = invest_sox / total * 100 if total > 0 else 0

def pct_color(p):
    if p > 50: return "red"
    if p < 50: return "lightgreen"
    return "white"

st.write("### 💰 投資佔比")
st.markdown(f"**NDX：<span style='color:{pct_color(pct_ndx)}'>{pct_ndx:.1f}%</span>**", unsafe_allow_html=True)
st.markdown(f"**SOX：<span style='color:{pct_color(pct_sox)}'>{pct_sox:.1f}%</span>**", unsafe_allow_html=True)
st.write("---")


# ==========================
# Fetch market data
# ==========================
tickers = {
    "^NDX": "NASDAQ 100",
    "^SOX": "費城半導體",
    "XAUUSD=X": "黃金（自動換算 XAUD）"
}

# 取得 AUD/USD 匯率
fx_data = fetch_price("AUDUSD=X")
if fx_data is None:
    audusd = None
else:
    audusd = fx_data["Close"].iloc[-1]

if audusd is None:
    st.error("❌ 無法取得 AUD/USD 匯率，無法換算 XAUD → XAUUSD。")
    st.stop()


# ==========================
# Display Each Index Panel
# ==========================
for ticker, label in tickers.items():

    df = fetch_price(ticker)
    if df is None:
        st.error(f"無法獲取 {label} 資料。")
        continue

    price, ma60, ma240, color, sig_label, pct, ratio = compute_signals(df)

    # 若黃金 → 套用後台自動換算邏輯
    if ticker == "XAUUSD=X":
        xaud_price = price * audusd
        xaud_ma60 = ma60 * audusd
        xaud_ma240 = ma240 * audusd

        display_price = xaud_price
        display_ma60 = xaud_ma60
        display_ma240 = xaud_ma240
    else:
        display_price = price
        display_ma60 = ma60
        display_ma240 = ma240

    base_color = {
        "green": (0, 255, 0),
        "yellow": (255, 255, 0),
        "red": (255, 0, 0)
    }[color]

    grad_start = gradient_color(base_color, 0)
    grad_end = gradient_color(base_color, ratio)

    bar_html = f"""
        <div class="bar" style="
            background: linear-gradient(90deg, {grad_start}, {grad_end});
            width: {ratio*100}%;
        "></div>
    """

    st.markdown(f"""
        <div class="block">
            <div class="value">{render_signal(color)} {label} — {sig_label}</div>

            <div class="label">目前價格:</div>
            <div class="value">{display_price:,.2f}</div>

            <div class="label">季線 MA60:</div>
            <div class="value">{display_ma60:,.2f}</div>

            <div class="label">年線 MA240:</div>
            <div class="value">{display_ma240:,.2f}</div>

            <div class="label">距離季線變化: {pct:.2f}%</div>

            {bar_html}
        </div>
    """, unsafe_allow_html=True)
