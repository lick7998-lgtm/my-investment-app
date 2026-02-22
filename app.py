import streamlit as st
import yfinance as yf
import pandas as pd

# 設定網頁標題與佈局
st.set_page_config(page_title="投資趨勢監控系統", layout="wide")

# --- 核心 CSS ---
st.markdown("""
<style>
* { text-shadow: none !important; -webkit-font-smoothing: antialiased; }
.metric-title { font-size: 26px; font-weight: 700; margin-bottom: 5px; }
.value-text { font-size: 22px; font-weight: 600; margin-bottom: 5px; }
.energy-bar-container { background-color: #0d0d0d; border-radius: 8px; width: 100%; height: 26px; margin-top: 10px; overflow: hidden; border: 1px solid #333; }
.energy-bar-fill { height: 26px; border-radius: 8px; transition: width 0.6s ease-in-out; }
</style>
""", unsafe_allow_html=True)


# --- 安全抓取資料 ---
def fetch_index_data(symbol):
    try:
        df = yf.download(symbol, period="2y", progress=False)
        if df.empty:
            return None

        # 兼容新版 yfinance
        if isinstance(df.columns, pd.MultiIndex):
            close_series = df['Close'].iloc[:, 0]
        else:
            close_series = df['Close']

        close_series = close_series.dropna()

        # MA 計算
        if len(close_series) < 240:
            return None

        ma60 = close_series.rolling(60).mean().iloc[-1]
        ma240 = close_series.rolling(240).mean().iloc[-1]

        current = close_series.iloc[-1]
        pct = ((current - ma60) / ma60) * 100

        return float(current), float(ma60), float(ma240), float(pct)
    except Exception:
        return None


# --- 抓匯率 ---
def fetch_fx_rate(symbol):
    try:
        df = yf.download(symbol, period="5d", progress=False)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            return float(df['Close'].iloc[-1, 0])
        return float(df['Close'].iloc[-1])
    except:
        return None


# --- 顏色與漸層 ---
def get_style_config(pct, current, ma240):
    if current < ma240:
        return "🔴 紅燈 (跌破年線)", "#FF0000", "linear-gradient(to right, rgb(100,0,0), rgb(250,0,0))"
    elif pct < 0:
        return "🟡 黃燈 (跌破季線)", "#FFFF00", "linear-gradient(to right, rgb(100,100,0), rgb(250,250,0))"
    else:
        return "🟢 綠燈 (季線之上)", "#00FF00", "linear-gradient(to right, rgb(0,100,0), rgb(0,250,0))"


# --- UI ---
st.title("📡 投資趨勢監控系統")

st.subheader("💰 投資金額輸入")
col_in1, col_in2 = st.columns(2)
with col_in1:
    amt_ndx = st.number_input("NDX 投入金額 (USD)", min_value=0, value=0, step=1, format="%d")
with col_in2:
    amt_sox = st.number_input("SOX 投入金額 (USD)", min_value=0, value=0, step=1, format="%d")

total = amt_ndx + amt_sox
p_ndx = (amt_ndx / total * 100) if total > 0 else 0
p_sox = (amt_sox / total * 100) if total > 0 else 0

def ratio_color(v):
    if v > 50: return "#FF0000"
    if v < 50: return "#00FF00"
    return "#FFFFFF"

st.info(f"💵 總預算 (自動加總): **${total:,}**")

c_p1, c_p2 = st.columns(2)
c_p1.markdown(f"NDX 佔比：<span style='color:{ratio_color(p_ndx)}; font-size:24px; font-weight:bold;'>{p_ndx:.1f}%</span>", unsafe_allow_html=True)
c_p2.markdown(f"SOX 佔比：<span style='color:{ratio_color(p_sox)}; font-size:24px; font-weight:bold;'>{p_sox:.1f}%</span>", unsafe_allow_html=True)

st.divider()


# --- 匯率取得 (AUD/USD) ---
audusd_rate = fetch_fx_rate("AUDUSD=X")
if not audusd_rate:
    st.error("⚠️ 無法取得 AUD/USD 匯率，XAUD 轉換將停用。")


# --- 監控表 ---
tickers = {
    "^NDX": "NASDAQ 100 (NDX)",
    "^SOX": "費城半導體 (SOX)",
    "XAUUSD=X": "黃金現貨 (XAUD)",
    "GDX": "黃金礦業 ETF (GDX)"
}

items = list(tickers.items())

for i in range(0, len(items), 2):
    cols = st.columns(2)
    for j in range(2):
        if i + j >= len(items):
            continue

        symbol, name = items[i + j]

        with cols[j]:
            res = fetch_index_data(symbol)
            if not res:
                st.error(f"無法獲取 {name} 數據，請稍後再試。")
                continue

            curr, m60, m240, pct = res

            # 🎯 若是黃金，做 USD → AUD 換算
            if symbol == "XAUUSD=X" and audusd_rate:
                curr = curr / audusd_rate
                m60 = m60 / audusd_rate
                m240 = m240 / audusd_rate

                # ⚠️ 換算後重新計算 pct，不再使用 USD 的 pct
                pct = ((curr - m60) / m60) * 100

            status_text, h_color, bar_grad = get_style_config(pct, curr, m240)

            # 格式化輸出
            if symbol == "GDX":
                fmt = lambda v: f"{v:,.2f}"
            else:
                fmt = lambda v: f"{int(v):,}"

            st.markdown(f"""
            <div class='metric-title' style='color:{h_color};'>{name}</div>
            <div class='value-text' style='color:{h_color};'>當前報價：{fmt(curr)}</div>
            <div class='value-text' style='color:{h_color};'>季線 MA60：{fmt(m60)}</div>
            <div class='value-text' style='color:{h_color};'>年線 MA240：{fmt(m240)}</div>
            <div style='color:{h_color}; font-weight:bold; font-size:20px; margin-top:10px; display:flex; justify-content:space-between;'>
                <span>{status_text}</span>
                <span>距季線：{pct:+.2f}%</span>
            </div>
            """, unsafe_allow_html=True)

            # 能量條
            fill_width = min(max(abs(pct), 5.0), 40.0)
            st.markdown(f"""
            <div class='energy-bar-container'>
                <div class='energy-bar-fill' style='width: {fill_width}%; background: {bar_grad};'></div>
            </div>
            """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)
