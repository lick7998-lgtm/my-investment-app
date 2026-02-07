import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="NDX & SOX Monitor", layout="wide")

# --- CSS：移除 text-shadow + 能量條樣式 ---
st.markdown("""
<style>
* { text-shadow: none !important; }

.metric-title {
    font-size: 24px;
    font-weight: 700;
}

.value-text {
    font-size: 22px;
    font-weight: 600;
}

.energy-bar {
    height: 22px;
    border-radius: 8px;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)


# --- 抓資料函式 ---
def fetch_index_data(symbol):
    data = yf.download(symbol, period="400d")
    data["MA60"] = data["Close"].rolling(60).mean()
    data["MA240"] = data["Close"].rolling(240).mean()
    current = data["Close"].iloc[-1]
    ma60 = data["MA60"].iloc[-1]
    ma240 = data["MA240"].iloc[-1]
    pct_from_ma60 = (current - ma60) / ma60 * 100
    return current, ma60, ma240, pct_from_ma60


# --- 顏色決定：燈號 ---
def signal_color(pct):
    if pct > 0:
        return "green"
    elif pct < 0:
        return "red"
    return "yellow"


# --- 色光漸層：亮度從 100 → 250 ---
def gradient_color(base_color, intensity_pct):
    # intensity_pct：0 → 深 (100)；100 → 亮 (250)
    brightness = int(100 + (150 * (intensity_pct / 100)))
    brightness = min(brightness, 250)

    if base_color == "green":
        return f"rgb(0,{brightness},0)"
    elif base_color == "red":
        return f"rgb({brightness},0,0)"
    else:
        return f"rgb({brightness},{brightness},0)"


# --- 能量條 HTML ---
def render_energy_bar(base_color, pct):
    pct = max(min(pct, 40), -40)     # 限制 -40% 到 +40%
    width = abs(pct)

    intensity = (abs(pct) / 40) * 100
    start_color = gradient_color(base_color, 0)
    end_color = gradient_color(base_color, intensity)

    return f"""
    <div class="energy-bar" style="
        width: {width}%;
        background: linear-gradient(to right, {start_color}, {end_color});
    "></div>
    """


# --- UI ---
st.title("📡 NDX & SOX 指數監控（含能量條）")


# --- 抓 NDX 與 SOX ---
current_ndx, ndx_ma60, ndx_ma240, ndx_pct = fetch_index_data("^NDX")
current_sox, sox_ma60, sox_ma240, sox_pct = fetch_index_data("^SOX")


# --- 手動輸入投資金額 ---
st.subheader("💰 投資金額輸入")
col1, col2 = st.columns(2)
with col1:
    invest_ndx = st.number_input("投入金額：NDX", min_value=0, value=0, step=100)
with col2:
    invest_sox = st.number_input("投入金額：SOX", min_value=0, value=0, step=100)

total = invest_ndx + invest_sox
ndx_ratio = (invest_ndx / total * 100) if total > 0 else 0
sox_ratio = (invest_sox / total * 100) if total > 0 else 0


def ratio_color(r):
    if r > 50:
        return "red"
    elif r < 50:
        return "green"
    return "white"


# --- 顯示兩個指數區塊 ---
def render_index_block(name, price, ma60, ma240, pct):
    c = signal_color(pct)

    st.markdown(f"<div class='metric-title'>{name}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value-text'>目前價格：{price:,.2f}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value-text'>季線 MA60：{ma60:,.2f}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value-text'>年線 MA240：{ma240:,.2f}</div>", unsafe_allow_html=True)

    st.write(f"距季線變化： {pct:+.2f}%")
    st.markdown(render_energy_bar(c, pct), unsafe_allow_html=True)


st.subheader("📈 指數資料 + 能量條")

c1, c2 = st.columns(2)

with c1:
    render_index_block("NASDAQ 100 (NDX)", current_ndx, ndx_ma60, ndx_ma240, ndx_pct)

with c2:
    render_index_block("PHLX 半導體 (SOX)", current_sox, sox_ma60, sox_ma240, sox_pct)


# --- 投資比例 ---
st.subheader("📊 投資佔比 (%)")
st.write(f"NDX： **{ndx_ratio:.2f}%**", unsafe_allow_html=True)
st.write(f"SOX： **{sox_ratio:.2f}%**", unsafe_allow_html=True)
