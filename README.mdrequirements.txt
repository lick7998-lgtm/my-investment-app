# NDX & SOX Streamlit Monitor

此專案為可部屬於 Streamlit Cloud 的即時指數監控工具。

## 功能特色

### 📡 指數資料
- NDX（NASDAQ 100）
- SOX（費城半導體）
- 顯示：
  - 目前價格
  - MA60（季線）
  - MA240（年線）
  - 距離季線百分比

### 🎨 極致能量條（100 → 250 色光）
- 依照燈號（綠 / 黃 / 紅）產生動態漸層
- 漸層亮度從 100 → 250
- 能量條長度 = 距季線 %（最高 40%）
- 無任何 text-shadow，手機觀看極致銳利

### 💰 投資比例
- 手動輸入 NDX / SOX 投資額
- 自動計算比例
- 顏色規則：
  - >50% → 紅色
  - <50% → 綠色
  - =50% → 白色

## 部署方式（Streamlit Cloud）

1. Fork 或 Clone 專案
2. Push 到 GitHub
3. 開啟 https://share.streamlit.io
4. 選擇此 repo 部署即可
