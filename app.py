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
    """安全抓取 Yahoo 最新成交價，加入強效 fallback 防呆機制"""
    try:
        tk = yf.Ticker(ticker)
        
        # 嘗試 1：使用 fast_info 即時報價 (兼容新舊版 yfinance)
        try:
            if hasattr(tk, 'fast_info'):
                info = tk.fast_info
                # 兼容字典取值與屬性取值
                price = info.get("lastPrice") if hasattr(info, 'get') else getattr(info, 'last_price', None)
                if price: return float(price)
        except:
            pass
        
        # 嘗試 2：使用 5天歷史數據保底 (過濾週末 NaN，最穩定)
        hist = tk.history(period="5d")
        if not hist.empty and 'Close' in hist.columns:
            clean_hist = hist['Close'].dropna()
            if not clean_hist.empty:
                return float(clean_hist.iloc[-1])
                
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
        return "🟢 綠燈 (季線之上)", "#00FF00", "linear-gradient(to right, rgb(0,100,0), rgb
