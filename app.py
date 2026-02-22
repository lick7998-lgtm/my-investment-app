import streamlit as st
import yfinance as yf
import pandas as pd

# 設定網頁標題與佈局
st.set_page_config(page_title="投資趨勢監控系統", layout="wide")

# --- 核心 CSS：確保字體絕對銳利 + 佈局控制 ---
st.markdown("""
<style>
* { text-shadow: none !important; -webkit-font-smoothing: antialiased; }
.metric-title { font-size: 26px; font-weight: 700; margin-bottom: 5px; }
.value-text { font-size: 22px; font-weight: 600; margin-bottom: 5px; }
.formula-text { font-size: 16px; font-weight: 500; color: #AAAAAA; margin-bottom: 8px; }
/* 能量條底槽：深色背景 */
.energy-bar-container { background-color: #0d0d0d; border-radius: 8px; width: 100%; height: 26px; margin-top: 10px; overflow: hidden; border: 1px solid #333; }
/* 能量條填充：色光 100 -> 250 漸層 */
.energy-bar-fill { height: 26px; border-radius: 8px; transition: width 0.6s ease-in-out; }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 🚀 模組 1：極速抓取最新價 (專為 XAUD 設計)
# ==========================================
def safe_price(ticker):
    """安全抓取 Yahoo 最新成交價，加入 fallback (取自您的建議)"""
    try:
        data = yf.Ticker(ticker).fast_info
        
        # 第一優先：即時價格
        price = data.get("lastPrice")
        if price is not None: return price
        
        # 第二優先：收盤價
        price = data.get("regularMarketPreviousClose")
        if price is not None: return price
        
        # fallback：用 history
        hist = yf.Ticker(ticker).history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception:
        return None
    return None


# ==========================================
# 📊 模組 2：抓取含均線的歷史資料 (NDX, SOX, GDX)
# ==========================================
def fetch_index_data(symbol):
    try:
        df = yf.download(symbol, period="2y", progress=False)
        if df.empty: return None
        
        # 兼容新版 yfinance
        if isinstance(df.columns, pd.MultiIndex):
            close_series = df['Close'].iloc[:, 0]
        else:
            close_series = df['Close']
            
        close_series = close_series.dropna()
        if close_series.empty: return None
        
        current = float(close_series.iloc[-1])
        ma60 = float(close_series.rolling(60).mean().dropna().iloc[-1])
        ma240 = float(close_series.rolling(240).mean().dropna().iloc[-1])
        
        pct = ((current - ma60) / ma60) * 100
        return current, ma60, ma240, pct
    except Exception:
        return None


# --- 顏色與漸層配置 (100 -> 250) ---
def get_style_config(pct, current, ma240):
    if current < ma240: 
        return "🔴 紅燈 (跌破年線)", "#FF0000", "linear-gradient(to right, rgb(100,0,0), rgb(250,0,0))"
    elif pct < 0: 
        return "🟡 黃燈 (跌破季線)", "#FFFF00", "linear-gradient(to right, rgb(100,100,0), rgb(250,250,0))"
    else: 
        return "🟢 綠燈 (季線之上)", "#00FF00", "linear-gradient(to right, rgb(0,100,0), rgb(0,250,0))"


# ==========================================
# 🖥️ 網頁 UI 開始
# ==========================================
st.title("📡 投資趨勢監控系統")

# 1. 投資金額輸入
st.subheader("💰 投資金額輸入")
col_in1, col_in2 = st.columns(2)
with col_in1:
    amt_ndx = st.number_input("NDX 投入金額 (USD)", min_value=0, value=0, step=1, format="%d")
with col_in2:
    amt_sox = st.number_input("SOX 投入金額 (USD)", min_value=0, value=0, step=1, format="%d")

# 2. 自動加總
total = amt_ndx + amt_sox
p_ndx = (amt_ndx / total * 100) if total > 0 else 0
p_sox = (amt_sox / total * 100) if total > 0 else 0
st.info(f"💵 總預算 (自動加總): **${total:,}**")

# 3. 顯示佔比
def ratio_color(val):
    if val > 50: return "#FF0000"
    if val < 50: return "#00FF00"
    return "#FFFFFF"

c_p1, c_p2 = st.columns(2)
c_p1.markdown(f"NDX 佔比：<span style='color:{ratio_color(p_ndx)}; font-size:24px; font-weight:bold;'>{p_ndx:.1f}%</span>", unsafe_allow_html=True)
c_p2.markdown(f"SOX 佔比：<span style='color:{ratio_color(p_sox)}; font-size:24px; font-weight:bold;'>{p_sox:.1f}%</span>", unsafe_allow_html=True)

st.divider()

# 4. 指數監控 (自動化 2x2 網格佈局)
tickers = [
    ("^NDX", "NASDAQ 100 (NDX)"), 
    ("^SOX", "費城半導體 (SOX)"),
    ("XAUD_CUSTOM", "黃金現貨 (XAUD)"),
    ("GDX", "黃金礦業 ETF (GDX)")
]

for i in range(0, len(tickers), 2):
    cols = st.columns(2)
    for j in range(2):
        if i + j < len(tickers):
            symbol, name = tickers[i + j]
            with cols[j]:
                
                # ==========================================
                # 🟡 專屬 XAUD 區塊 (無均線、無能量條、顯示算式)
                # ==========================================
                if symbol == "XAUD_CUSTOM":
                    # 使用 GPT 建議的極速抓價法
                    gold_usd = safe_
