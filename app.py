import streamlit as st
import yfinance as yf
import pandas as pd

# -------------------------------------------------------
#                頁面設定
# -------------------------------------------------------
st.set_page_config(page_title="投資趨勢監控", layout="centered")

# -------------------------------------------------------
#                核心 CSS（修正版）
# -------------------------------------------------------
st.markdown("""
<style>

 /* 進度條外層高度 */
 div[data-testid="stProgress"] {
     height: 22px !important;
 }

 /* 底槽：暗色不透明漸層 */
 div[data-testid="stProgress"] > div > div {
     background: linear-gradient(to right, #0a0a0a, #1a1a1a) !important;
     border-radius: 12px !important;
     height: 20px !important;
     opacity: 0.35 !important;
 }

 /* 填滿進度條：亮色漸層（從 --bar-gradient 注入） */
 div[data-testid="stProgress"] > div > div > div {
     background: var(--bar-gradient) !important;
     border-radius: 12px !important;
     height: 20px !important;
     opacity: 1.0 !important;
 }

 /* 文字 */
 .price-font { font-size: 26px; font-weight: bold; }
 .status-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------
#                     APP 標題
# -------------------------------------------------------
st.title("📊 ETF 趨勢監控 App")


# -------------------------------------------------------
#             1. 使用者輸入投資金額
# -------------------------------------------------------
st.subheader("💰 投資金額輸入")

c_in1, c_in2 = st.columns(2)
with c_in1:
    amt_ndx = st.number_input("NDX 投入金額", min_value=0, value=30, step=1, format="%d")
with c_in2:
    amt_sox = st.number_input("SOX 投入金額", min_value=0, value=20, step=1, format="%d")

total = amt_ndx + amt_sox
st.info(f"💵 總預算 (自動加總): **${total:,}**")

st.divider()


# -------------------------------------------------------
#              2. 資產佔比（大於50%紅，小於50%綠）
# -------------------------------------------------------
st.subheader("📈 資產配置佔比")

p_ndx = (amt_ndx / total * 100) if total > 0 else 0
p_sox = (amt_sox / total * 100) if total > 0 else 0

def get_pct_color(val):
    if val > 50: return "#FF0000"
    if val < 50: return "#00FF00"
    return "#FFFFFF"

col1, col2 = st.columns(2)
with col1:
    st.write("NDX (NASDAQ 100)")
    st.markdown(
        f"<span class='price-font'>${amt_ndx:,}</span> "
        f"<span style='color:{get_pct_color(p_ndx)}; font-size:20px;'>{p_ndx:.1f}%</span>",
        unsafe_allow_html=True
    )

with col2:
    st.write("SOX (費城半導體)")
    st.markdown(
        f"<span class='price-font'>${amt_sox:,}</span> "
        f"<span style='color:{get_pct_color(p_sox)}; font-size:20px;'>{p_sox:.1f}%</span>",
        unsafe_allow_html=True
    )

st.divider()


# -------------------------------------------------------
#                        3. 指數資料
# -------------------------------------------------------
tickers = {
    "^NDX": "NASDAQ 100 指數",
    "^SOX": "費城半導體 指數"
}

def fetch_data(symbol):
    try:
        df = yf.download(symbol, period="1y", progress=False)
        if df.empty:
            return None
        curr = float(df["Close"].iloc[-1])
        m60 = float(df["Close"].rolling(60).mean().iloc[-1])
        m240 = float(df["Close"].rolling(240).mean().iloc[-1])
        diff_pct = (curr - m60) / m60
        return curr, m60, m240, diff_pct
    except:
        return None


# -------------------------------------------------------
#                     4. 趨勢狀態＋進度條
# -------------------------------------------------------
st.subheader("🔍 標的趨勢監控")

for i, (code, name) in enumerate(tickers.items()):
    res = fetch_data(code)

    if res:
        curr, m60, m240, diff = res
        diff_val = diff * 100

        # 燈號判定 + 對應漸層
        if curr > m60:
            status, color = "🟢 綠燈 (季線之上)", "#00FF00"
            grad = "linear-gradient(to right, #003300, #00FF00)"
        elif curr > m240:
            status, color = "🟡 黃燈 (跌破季線)", "#FFFF00"
            grad = "linear-gradient(to right, #333300, #FFFF00)"
        else:
            status, color = "🔴 紅燈 (跌破年線)", "#FF0000"
            grad = "linear-gradient(to right, #330000, #FF0000)"

        # 注入漸層給這條進度條
        st.markdown(
            f"<style>div[data-testid='stProgress']:nth-of-type({i+1}) "
            f"{{ --bar-gradient: {grad}; }}</style>",
            unsafe_allow_html=True
        )

        st.write(f"### {name}")
        st.write(f"當前點數: **{curr:,.2f}**")

        st.markdown(
            f"""
            <div class="status-header">
                <span style="color:{color}; font-weight:bold; font-size:20px;">{status}</span>
                <span style="color:{color}; font-size:18px;">距季線: {diff_val:+.2f}%</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 能量條填滿比例（強制最少 10%）
        progress_val = min(max(abs(diff_val) / 30.0, 0.1), 1.0)
        st.progress(progress_val)

    else:
        st.error(f"無法取得 {name} 資料")

    st.write("---")
