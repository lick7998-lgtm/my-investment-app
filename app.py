import yfinance as yf
import math

# -----------------------------
# Helper: 安全抓取 Yahoo 價格
# -----------------------------
def safe_price(ticker):
    """
    安全抓取 Yahoo 最新成交價，加入 fallback
    """
    try:
        data = yf.Ticker(ticker).fast_info

        # 第一優先：即時價格
        price = data.get("lastPrice")
        if price is not None:
            return price

        # 第二優先：收盤價
        price = data.get("regularMarketPreviousClose")
        if price is not None:
            return price

        # fallback：用 history
        hist = yf.Ticker(ticker).history(period="1d")
        if not hist.empty:
            return hist["Close"].iloc[-1]

    except Exception as e:
        print(f"抓取 {ticker} 失敗：", e)
        return None

    return None

# -----------------------------
# Helper: 計算移動平均線
# -----------------------------
def moving_average(ticker, period):
    """
    計算指定期間的移動平均線
    """
    try:
        hist = yf.Ticker(ticker).history(period=f"{period}d")
        if hist.empty:
            return None
        ma = hist["Close"].tail(period).mean()
        return ma
    except Exception as e:
        print(f"計算 {ticker} MA{period} 失敗：", e)
        return None

# -----------------------------
# 計算 XAUD
# -----------------------------
def get_XAUD():
    XAUUSD = safe_price("XAUUSD=X")
    AUDUSD = safe_price("AUDUSD=X")  # Yahoo 沒有 USDAUD=X

    if XAUUSD is None or AUDUSD is None:
        return None, "XAUUSD 或 AUDUSD 抓取失敗"

    USDAUD = 1 / AUDUSD
    XAUD = XAUUSD * USDAUD
    return int(XAUD), None

# -----------------------------
# 計算單一標的資訊
# -----------------------------
def get_stock_info(ticker):
    price = safe_price(ticker)
    ma60 = moving_average(ticker, 60)
    ma240 = moving_average(ticker, 240)

    if price is None or ma60 is None or ma240 is None:
        return None

    # 判斷綠燈 / 黃燈
    if price >= ma60:
        light = "綠燈 (季線之上)"
        dist_ma = (price - ma60) / ma60 * 100
    else:
        light = "黃燈 (跌破季線)"
        dist_ma = (price - ma60) / ma60 * 100

    return {
        "price": price,
        "MA60": ma60,
        "MA240": ma240,
        "light": light,
        "dist_ma": dist_ma
    }

# -----------------------------
# 主程式
# -----------------------------
def main():
    # 費城半導體 ETF (SOX)
    sox_info = get_stock_info("SOXX")  # Yahoo ticker: SOXX
    if sox_info:
        print("費城半導體 (SOX)")
        print(f"當前報價：{sox_info['price']}")
        print(f"季線 MA60：{sox_info['MA60']:.2f}")
        print(f"年線 MA240：{sox_info['MA240']:.2f}")
        print(f"{sox_info['light']} 距季線：{sox_info['dist_ma']:.2f}%")
    else:
        print("SOX 資料抓取失敗")

    print("\n------------------\n")

    # 黃金礦業 ETF (GDX)
    gdx_info = get_stock_info("GDX")
    if gdx_info:
        print("黃金礦業 ETF (GDX)")
        print(f"當前報價：{gdx_info['price']}")
        print(f"季線 MA60：{gdx_info['MA60']:.2f}")
        print(f"年線 MA240：{gdx_info['MA240']:.2f}")
        print(f"{gdx_info['light']} 距季線：{gdx_info['dist_ma']:.2f}%")
    else:
        print("GDX 資料抓取失敗")

    print("\n------------------\n")

    # 黃金現貨對澳幣 (XAUD)
    xaud_price, xaud_err = get_XAUD()
    if xaud_err:
        print("XAUD 計算失敗：", xaud_err)
    else:
        print("黃金現貨 (XAUD)")
        print(f"當前報價：{xaud_price}")

# -----------------------------
# 執行
# -----------------------------
if __name__ == "__main__":
    main()
