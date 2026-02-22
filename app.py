import streamlit as st
import yfinance as yf
import pandas as pd

# 設定網頁標題與佈局
st.set_page_config(page_title="投資趨勢監控系統", layout="wide")

# --- 核心 CSS：確保字體絕對銳利 + 能量條寬度控制 ---
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

# --- 資料抓取與安全計算 (解決 ValueError) ---
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

# --- 單純取得最新報價 (加入空值剔除，徹底解決週末報錯) ---
def fetch_latest_price(symbol):
    try:
        # 區間拉長到 1個月，確保一定有資料
        df = yf.download(symbol, period="1mo", progress=False)
        if df.empty: return None
        
        if isinstance(df.columns, pd.MultiIndex):
            close_series = df['Close'].iloc[:, 0]
        else:
            close_series = df['Close']
            
        # 關鍵除錯點：徹底剔除週末產生的 NaN 空值
        close_series = close_series.dropna()
        if close_series.empty: return None
        
        return float(close_series.iloc[-1])
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

# 4. 指數監控與能量條
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
                # 🟡 針對 XAUD 的特製邏輯 (顯示算式、無小數點、無均線/能量條)
                # ==========================================
                if symbol == "XAUD_CUSTOM":
                    gold_usd = fetch_latest_price("XAUUSD=X")
                    aud_usd = fetch_latest_price("AUDUSD=X")
                    
                    if gold_usd and aud_usd:
                        # 換算公式：黃金/美元 ÷ 澳幣/美元 = 黃金/澳幣，並強制轉為整數
                        xaud_val = int(gold_usd / aud_usd)
                        
                        st.markdown(f"<div class='metric-title' style='color:#FFD700;'>{name}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='formula-text'>算式：XAUUSD ({gold_usd:,.2f}) ÷ AUDUSD ({aud_usd:.4f})</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='value-text' style='color:#FFD700; font-size: 28px;'>當前報價：{xaud_val:,}</div>", unsafe_allow_html=True)
                    else:
                        st.error("無法獲取計算 XAUD 所需的美元黃金或匯率數據。")
                        
                # ==========================================
                # 🟢 針對 NDX, SOX, GDX 的標準邏輯
                # ==========================================
                else:
                    res = fetch_index_data(symbol)
                    if res:
                        curr, m60, m240, pct = res
                        status_text, h_color, bar_grad = get_style_config(pct, curr, m240)
                        
                        if symbol == "GDX":
                            v_curr, v_m60, v_m240 = f"{curr:,.2f}", f"{m60:,.2f}", f"{m240:,.2f}"
                        else:
                            v_curr, v_m60, v_m240 = f"{int(curr):,}", f"{int(m60):,}", f"{int(m240):,}"
                        
                        html_content = f"""
                        <div class='metric-title' style='color:{h_color};'>{name}</div>
                        <div class='value-text' style='color:{h_color};'>當前報價：{v_curr}</div>
                        <div class='value-text' style='color:{h_color};'>季線 MA60：{v_m60}</div>
                        <div class='value-text' style='color:{h_color};'>年線 MA240：{v_m240}</div>
                        <div style='color:{h_color}; font-weight:bold; font-size:20px; margin-top:10px; display:flex; justify-content:space-between;'>
                            <span>{status_text}</span>
                            <span>距季線：{pct:+.2f}%</span>
                        </div>
                        """
                        st.markdown(html_content, unsafe_allow_html=True)
                        
                        fill_width = min(max(abs(pct), 5.0), 40.0) 
                        bar_html = f"""
                        <div class='energy-bar-container'>
                            <div class='energy-bar-fill' style='width: {fill_width}%; background: {bar_grad};'></div>
                        </div>
                        """
                        st.markdown(bar_html, unsafe_allow_html=True)
                    else:
                        st.error(f"無法獲取 {name} 數據，請稍後再試。")
    
    st.write("<br>", unsafe_allow_html=True)
