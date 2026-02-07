import streamlit as st
import yfinance as yf
import pandas as pd

# ---------------------------
# 全域 CSS — 改成「3D 燈號 + 火焰能量條」
# ---------------------------
st.markdown("""
<style>
* { text-shadow: none !important; }

/* 3D 球狀燈號（強光亮點 + 漸層圓形） */
.signal-dot {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    display: inline-block;
    position: relative;
    margin-right: 8px;
    box-shadow:
        inset -3px -3px 6px rgba(0,0,0,0.45),
        inset 3px 3px 8px rgba(255,255,255,0.55),
        0 0 10px rgba(255,255,255,0.15);
}

.signal-dot::after {
    content: "";
    position: absolute;
    top: 4px;
    left: 6px;
    width: 10px;
    height: 10px;
    background: rgba(255,255,255,0.55);
    border-radius: 50%;
    filter: blur(1px);
}

/* 火焰動態能量條（會微跳動） */
.energy-container {
    width: 100%;
    height: 20px;
    border-radius: 8px;
    overflow: hidden;
    margin-top: 6px;
    margin-bottom: 14px;
    background: #111;
    position: relative;
}

.energy-bar {
    height: 100%;
    width: 100%;
    animation: flame 1.6s ease-in-out infinite alternate;
    background-size: 200% 200%;
}

/* 火焰跳動動畫 */
@keyframes flame {
    0%   { filter: brightness(0.85); transform: scale(1.00); }
    50%  { filter: brightness(1.25); transform: scale(1.02); }
    100% { filter: brightness(1.05); transform: scale(1.01); }
}

/* 佔比字色 */
.red   { color: #ff4d4d; font-weight: 700; }
.green { color: #00cc66; font-weight: 700; }
.white { color: #ffffff; font-weight: 700; }
</style>
""", unsafe_allow_html=True)


# ---------------------------
# 資料抓取 & 計算
# ---------------------------
def get_price_and_ma(symbol):
    df = yf.download(symbol, period="1y", interval="1d")
    df["MA60"] = df["Close"].rolling(60).mean()
    df["MA240"] = df["Close"].rolling(240).mean()
    last = df.iloc[-1]
    return float(last["Close"]), float(last["MA60"]), float(last["MA240"])


def compute_signal(close, ma60, ma240):
    pct_60 = (close - ma60) / ma60 * 100

    if close >= ma60:
        signal = "green"
        label = "季線之上"
    elif close >= ma240:
        signal = "yellow"
        label = "跌破季線"
    else:
        signal = "red"
        label = "跌破年線"

    return signal, label, pct_60


def make_energy_color(signal, pct):
    """ 依照乖離百分比決定亮度強弱（色光 30→250） """
    intensity = min(max(abs(pct) / 12, 0), 1)
    base = int(30 + (250 - 30) * intensity)

    if signal == "green":
        return f"rgb(0,{base},0)"
    elif signal == "yellow":
        return f"rgb({base},{base},0)"
    else:
        return f"rgb({base},0,0)"


# ---------------------------
# APP UI
# ---------------------------
st.title("📈 NDX + SOX 趨勢燈號（3D 圓燈 + 火焰能量條）")

st.subheader("➤ 請輸入投入金額")
col1, col2 = st.columns(2)
with col1:
    amount_ndx = st.number_input("NDX 金額", min_value=0, step=100)
with col2:
    amount_sox = st.number_input("SOX 金額", min_value=0, step=100)

total = amount_ndx + amount_sox
st.write("---")

# ---------------------------
# 投資佔比
# ---------------------------
if total > 0:
    pct_ndx = amount_ndx / total * 100
    pct_sox = amount_sox / total * 100
else:
    pct_ndx = pct_sox = 0

def pct_color(p):
    if p > 50: return "red"
    if p < 50: return "green"
    return "white"

st.subheader("➤ 投資佔比 (%)")
st.markdown(f"NDX：<span class='{pct_color(pct_ndx)}'>{pct_ndx:.2f}%</span>", unsafe_allow_html=True)
st.markdown(f"SOX：<span class='{pct_color(pct_sox)}'>{pct_sox:.2f}%</span>", unsafe_allow_html=True)
st.write("---")


# ---------------------------
# 主體：燈號 + 火焰能量條
# ---------------------------
st.subheader("➤ 趨勢燈號 + 火焰能量條")

for symbol, name in [("^NDX", "NASDAQ 100 (NDX)"), ("^SOX", "Philadelphia SOX")]:
    st.markdown(f"### {name}")

    close, ma60, ma240 = get_price_and_ma(symbol)
    signal, label, pct_60 = compute_signal(close, ma60, ma240)
    color = make_energy_color(signal, pct_60)

    # 3D 圓燈 + 文案
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
            <div class="signal-dot" style="background:{color};"></div>
            <div style="font-size:20px; color:{color}; font-weight:700;">
                {label}
            </div>
            <div style="flex:1;"></div>
            <div style="font-size:20px; color:{color}; font-weight:700;">
                距季線：{pct_60:+.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 火焰能量條（100% 滿）
    st.markdown(
        f"""
        <div class="energy-container">
            <div class="energy-bar"
                style="background: linear-gradient(90deg, {color}, rgb(250,250,250));">
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("---")
