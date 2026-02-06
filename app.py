//@version=5
indicator("雙指數燈號 + 能量條（含漸層）", overlay=true, max_labels_count=500, max_lines_count=500)

//======================
// 參數設定
//======================
symbol1 = input.symbol("TWSE:TAIEX", "指數 1")
symbol2 = input.symbol("TWSE:OTC", "指數 2")

lenQ = input.int(60, "季線天數")
lenY = input.int(240, "年線天數")

//======================
// 讀取資料
//======================
close1 = request.security(symbol1, timeframe.period, close)
close2 = request.security(symbol2, timeframe.period, close)

maQ1 = ta.sma(close1, lenQ)
maY1 = ta.sma(close1, lenY)

maQ2 = ta.sma(close2, lenQ)
maY2 = ta.sma(close2, lenY)

//======================
// 決定燈號顏色（純色）
//======================
fSignalColor(close, maQ, maY) =>
    close >= maQ ? color.green :
    close >= maY ? color.yellow : color.red

signal1 = fSignalColor(close1, maQ1, maY1)
signal2 = fSignalColor(close2, maQ2, maY2)

//======================
// 能量條顏色：跟燈號顏色一致，但做漸層
//======================

// 將乖離壓到 0~1
fNorm(x) =>
    // x 正負都可能，用 tanh 壓縮
    n = math.abs(math.tanh(x * 3))
    math.min(math.max(n, 0), 1)

fEnergyColor(close, base, signalColor) =>
    diff = (close - base) / base
    n = fNorm(diff)  // 0~1

    // 深色光=30 → 淺色光=250
    L = 30 + n * (250 - 30)

    // 根據燈號顏色去建立漸層
    signalColor == color.green  ? color.rgb(0, L, 0) :
    signalColor == color.yellow ? color.rgb(L, L, 0) :
                                  color.rgb(L, 0, 0)

// 能量條：用季線做乖離基準
energyColor1 = fEnergyColor(close1, maQ1, signal1)
energyColor2 = fEnergyColor(close2, maQ2, signal2)

//======================
// 顯示燈號（色塊）
//======================
plotshape(true, title="指數1燈號", style=shape.circle, color=signal1, size=size.large, location=location.top, text="1")
plotshape(true, title="指數2燈號", style=shape.circle, color=signal2, size=size.large, location=location.top, text="2", offset=-1)

//======================
// 能量條（漸層）
//======================
barcolor(energyColor1)

// 第二檔用背景色顯示
bgcolor(energyColor2, transp=80)

//======================
// 額外資訊
//======================
plot(maQ1, "指數1季線", color=color.new(color.green, 50))
plot(maY1, "指數1年線", color=color.new(color.red, 50))

plot(maQ2, "指數2季線", color=color.new(color.green, 80))
plot(maY2, "指數2年線", color=color.new(color.red, 80))
