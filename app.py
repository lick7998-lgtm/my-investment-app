import streamlit as st
import yfinance as yf
import pandas as pd

# -------------------------------------------------------
#                頁面設定
# -------------------------------------------------------
st.set_page_config(page_title="投資趨勢監控", layout="centered")

# -------------------------------------------------------
#                核心 CSS（最終版）
# -------------------------------------------------------
st.markdown("""
<style>

 /* 外層高度 */
 div[data-testid="stProgress"] {
     height: 22px !important;
     margin-top: 4px !important;
     margin-bottom: 10px !important;
 }

 /* 背景槽：固定暗色，不用漸層 */
 div[data-testid="stProgress"] > div > div {
     background: rgba(0,0,0,0.35) !important;
     border-radius: 12px !important;
     height: 20px !important;
 }

 /* 填滿條：套用動態注入的 --bar-gradient */
 div[data-testid="stProgress"] > div > div > div {
     background: var(--bar-gradient) !important;
     border-radius: 12px !important;
     height: 20px !important;
 }

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
#              2. 資產佔比顯示
# -------------------------------------------------------
st.subheader("📈 資產配置佔比")

def pct_color(v): return "#FF0000" if v > 50 else "#00FF00" if v < 50 else "#FFFFFF"

p_ndx = (amt_ndx / total * 100) if total > 0 else 0
p_sox = (amt_sox / total * 100) if total > 0 else 0

c1, c2 = st.columns(2)
with c1:
    st.write("NDX (NASDAQ 100)")
    st.markdown(
        f"<span class='price-font'>${amt_ndx:,}</span> "
        f"<span style='color:{pct_color(p_ndx)}; font-size:20px;'>{p_ndx:.1f}%</span>",
        unsafe_allow_html=True
    )
with c2:
    st.write("SOX (費城半導體)")
    st.markdown(
        f"<span class='price-font'>${amt_sox:,}</span> "
        f"<span style='color:{pct_color(p_sox)}; font-size:20px;'>{p_sox:.1f}%</span>",
        unsafe_allow_html=True
    )

st.divider()



# -------------------------------------------------------
#                  3. 指數資料抓取
# -------------------------------------------------------
tickers = {
    "^NDX": "NASDAQ 100 指數",
    "^SOX": "費城半導體 指數"
}

def fetch_data(symbol):
    try:
        df = yf.download(symbol, period="1y", progress=False)
        if df.empty: return None
        curr = float(df["Close"].iloc[-1])
        m60 = float(df["Close"].rolling(60).mean().iloc[-1])
        m240 = float(df["Close"].rolling(240).mean().iloc[-1])
        diff_pct = (curr - m60) / m60
        return curr, m60, m240, diff_pct
    except:
        return None



# -------------------------------------------------------
#      4. 三燈號（綠 / 黃 / 紅）對應「色光 30–250 漸層」
# -------------------------------------------------------
def gradient_for(color):
    """
    color ∈ {"green", "yellow", "red"}
    回傳：色光 L=30 → L=250 漸層
    """

    if color == "green":
        return "linear-gradient(to right, #003300, #00FF00)"   # 深綠(30) → 亮綠(250)

    if color == "yellow":
        return "linear-gradient(to right, #333300, #FFFF00)"   # 深黃(30) → 亮黃(250)

    if color == "red":
        return "linear-gradient(to right, #330000, #FF0000)"   # 深紅(30) → 亮紅(250)"

    return "linear-gradient(to right, #111111, #666666)"



# -------------------------------------------------------
#                  5. 趨勢監控（含能量條）
# -------------------------------------------------------
st.subheader("🔍 標的趨勢監控")

for i, (code, name) in enumerate(tickers.items()):
    res = fetch_data(code)

    if not res:
        st.error(f"無法取得 {name} 資料")
        continue

    curr, m60, m240, diff = res
    diff_val = diff * 100

    # --- 燈號判定 + 漸層 ---
    if curr > m60:
        status = "🟢 綠燈 (季線之上)"
        text_color = "#00FF00"
        grad = gradient_for("green")

    elif curr > m240:
        status = "🟡 黃燈 (跌破季線)"
        text_color = "#FFFF00"
        grad = gradient_for("yellow")

    else:
        status = "🔴 紅燈 (跌破年線)"
        text_color = "#FF0000"
        grad = gradient_for("red")

    # 注入漸層到本條進度條
    st.markdown(
        f"<style>div[data-testid='stProgress']:nth-of-type({i+1}) "
        f"{{ --bar-gradient: {grad}; }}</style>",
        unsafe_allow_html=True
    )

    # --- 顯示文字 ---
    st.write(f"### {name}")
    st.write(f"當前點數: **{curr:,.2f}**")

    st.markdown(
        f"""
        <div class="status-header">
            <span style="color:{text_color}; font-weight:bold; font-size:20px;">{status}</span>
            <span style="color:{text_color}; font-size:18px;">距季線: {diff_val:+.2f}%</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- 能量條填滿度（最少 10%） ---
    progress_val = min(max(abs(diff_val) / 30.0, 0.10), 1.0)
    st.progress(progress_val)

    st.write("---")
