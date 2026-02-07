import streamlit as st
import yfinance as yf
import pandas as pd

# ---------------------------
# UI 設定：手機字體要銳利（移除 text-shadow）
# ---------------------------
st.markdown("""
<style>
/* 移除所有文字陰影，讓手機字體銳利 */
* {
    text-shadow: none !important;
}

/* 投資佔比顏色 */
.red   { color: #ff4d4d; font-weight: 700; }
.green { color: #00cc66; font-weight: 700; }
.white { color: #ffffff; font-weight: 700; }

/* 能量條容器 */
.energy-container {
    width: 100%;
    height: 18px;
    border-radius: 6px;
    overflow: hidden;
    margin-top: 4px;
    margin-bottom: 16px;
}

/* 能量條本體（寬度固定為 100% → 代表永遠全滿）*/
.energy-bar {
    height: 100%;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------
# 功能：抓價格 + 季線、年線
# ---------------------------
def get_price_and_ma(symbol):
    df = yf.download(symbol, period="1y", interval="1d")
    df["MA60"] = df["Close"].rolling(60).mean()
    df["MA240"] = df["Close"].rolling(240).mean()
    last = df.iloc[-1]
    return float(last["Close"]), float(last["MA60"]), float(last["MA240"])


def compute_signal(close, ma60, ma240):
    """
    回傳燈號顏色、距離季線的百分比、距離年線的百分比
    """
    pct_60 = (close - ma60) / ma60 * 100
    pct_240 = (close - ma240) / ma240 * 100

    if close >= ma60:
        signal = "green"   # 季線之上
    elif close >= ma240:
        signal = "yellow"  # 季線下、年線上
    else:
        signal = "red"     # 跌破年線

    return signal, pct_60, pct_240


def make_energy_color(signal, intensity):
    """
    intensity：0~1 之間
    色光從 30 → 250 的漸層
    """
    base = int(30 + (250 - 30) * intensity)

    if signal == "green":
        return f"rgb(0,{base},0)"
    elif signal == "yellow":
        return f"rgb({base},{base},0)"
    else:
        return f"rgb({base},0,0)"


# ---------------------------
# APP 標題
# ---------------------------
st.title("📈 NDX + SOX 投資比例檢視（含能量條）")


# ---------------------------
# Data Input
# ---------------------------
st.subheader("➤ 請輸入你的投入金額")

col1, col2 = st.columns(2)
with col1:
    amount_ndx = st.number_input("NDX 投入金額", min_value=0, step=100)
with col2:
    amount_sox = st.number_input("SOX 投入金額", min_value=0, step=100)

total = amount_ndx + amount_sox

st.write("---")

# ---------------------------
# 顯示佔比（依規則變色）
# ---------------------------
st.subheader("➤ 投資佔比 (%)")

if total > 0:
    pct_ndx = amount_ndx / total * 100
    pct_sox = amount_sox / total * 100
else:
    pct_ndx = pct_sox = 0

def pct_color(p):
    if p > 50:
        return "red"
    elif p < 50:
        return "green"
    else:
        return "white"

st.markdown(f"NDX：<span class='{pct_color(pct_ndx)}'>{pct_ndx:.2f}%</span>", unsafe_allow_html=True)
st.markdown(f"SOX：<span class='{pct_color(pct_sox)}'>{pct_sox:.2f}%</span>", unsafe_allow_html=True)

st.write("---")

# ---------------------------
# 抓股價 + 計算燈號 + 能量條
# ---------------------------
st.subheader("➤ 指標燈號 + 極致能量條")

for symbol, name in [("^NDX", "NASDAQ 100 (NDX)"), ("^SOX", "Philadelphia SOX")]:
    st.markdown(f"### {name}")

    close, ma60, ma240 = get_price_and_ma(symbol)
    signal, pct_60, pct_240 = compute_signal(close, ma60, ma240)

    # 強度：距季線的距離百分比 → 壓成 0~1
    intensity = min(max(abs(pct_60) / 15, 0), 1)
    color = make_energy_color(signal, intensity)

    # 顯示燈號
    st.write(f"📌 目前價格：{close:.2f}")
    st.write(f"📌 季線 MA60：{ma60:.2f}")
    st.write(f"📌 年線 MA240：{ma240:.2f}")

    st.markdown(f"**燈號： `{signal.upper()}`**")

    # 能量條（永遠 100% 滿格）
    st.markdown(
        f"""
        <div class='energy-container'>
            <div class='energy-bar' style='background: linear-gradient(90deg, {color}, rgb(250,250,250));'></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 距離季線百分比
    st.write(f"📊 距離季線：**{pct_60:.2f}%**")

    st.write("---")
