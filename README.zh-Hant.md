# AI 空氣品質判讀系統

Language: [English](README.md) | **繁體中文**

## 專案說明

AI 空氣品質判讀系統，也稱為 AirFusion AI，是一個多來源空氣品質分析服務，會把感測器讀值轉換成使用者能理解的健康建議。

本專案整合三個層級的空氣品質與氣象資料：

- **本地資料**：Arduino Uno 或 ESP32 搭配 PMS5003/PMS5003T 微粒感測器，讀取 PM2.5、PM10、溫度與濕度。
- **社區資料**：依照地理距離選擇附近的 AirBox/LASS 社區感測站。
- **區域資料**：環境部 MOENV 官方 AQI 與 PM2.5 資料，以及中央氣象署 CWA 的風速、風向、濕度與降水觀測資料。

單一 PM2.5 數字無法說明污染來源，也無法直接告訴使用者下一步該怎麼做。AirFusion AI 會比較本地、社區、區域與氣象條件，判斷可能的污染情境、估計健康風險，並以多語言產生清楚的建議。

## 主要方法

- 使用 Haversine 距離公式選擇最近的 AirBox、MOENV 與 CWA 測站。
- 以規則判斷室內污染源、社區熱點、區域污染、官方警示與正常情境。
- 以官方 AQI 或由 PM2.5 估算 AQI 風險等級。
- 透過結構化 prompt 將融合後的資料交給 OpenAI 產生建議。
- OpenAI 不可用時，自動使用本地規則 fallback。

## 開始使用

### 需求

- Python 3.11 或更新版本
- 若使用 Arduino Uno 韌體，需安裝 Arduino IDE
- 選用：OpenAI API key
- 選用：MOENV API key
- 選用：CWA API key

### 安裝

```powershell
cd "C:\Users\Hayden Ho\Desktop\coding\AirFusion_AI"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

編輯 `.env` 並填入可用的金鑰：

```text
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1-nano
MOENV_API_KEY=your_moenv_api_key
CWA_API_KEY=your_cwa_api_key
```

沒有 OpenAI key 也可以執行，回應會改用本地規則產生。

### 啟動 Web 應用

```powershell
uvicorn app.main:app --reload
```

開啟應用與 API 文件：

- Web 介面：<http://127.0.0.1:8000/>
- API 文件：<http://127.0.0.1:8000/docs>
- 健康檢查：<http://127.0.0.1:8000/health>

### 不接硬體測試

執行模擬感測器報告：

```powershell
python -m app.simulate_sensor
```

或手動送出主端點請求：

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/sensor/report `
  -ContentType "application/json" `
  -Body '{
    "device_id": "arduino-sensor01",
    "lat": 24.996222,
    "lon": 121.576211,
    "location_label": "Taipei Wenshan",
    "pm25": 45,
    "pm10": 60,
    "temperature": 27,
    "humidity": 60
  }'
```

回應會包含使用者訊息、訊息來源、選定資料來源、情境、建議與結構化 LLM prompt。

### 輸出語言切換

前端語言選單會同時切換 UI 文字和 OpenAI 的回應語言。

- 繁體中文：`zh-Hant`
- 英文：`en`
- 韓文：`ko`
- 泰文：`th`
- 越南文：`vi`

選定語言會在 API request 的 `language` 中傳送。`build_air_quality_prompt()` 也會把 `<target_language>` 設成對應語言，而 OpenAI instructions 會要求模型使用該語言回答。如果 OpenAI 不可用，本地 fallback 也會依同樣的語言設定輸出。

### 使用 Arduino Uno Serial 資料

Arduino Uno 沒有內建 Wi-Fi，所以這個專案使用 USB Serial 加上 Python bridge。

1. 將 `firmware/arduino_uno_serial/AirFusionUnoSerial/AirFusionUnoSerial.ino` 上傳到 Arduino Uno。
2. 接線 PMS5003T：
   - `PMS5003T VCC -> Uno 5V`
   - `PMS5003T GND -> Uno GND`
   - `PMS5003T TX -> Uno D10`
   - `PMS5003T RX -> 不接`
3. 啟動後端：

```powershell
uvicorn app.main:app --reload --host 0.0.0.0
```

4. 列出可用序列埠：

```powershell
python -m app.serial_bridge --list-ports
```

5. 將 Arduino JSON 報告轉送到後端：

```powershell
python -m app.serial_bridge --port COM7
```

請把 `COM7` 換成實際的 Arduino port。

### 執行測試

```powershell
python -m unittest discover -s tests
```

## 檔案結構

```text
AirFusion_AI/
  app/
    api/
      routes.py                  FastAPI endpoints, including /sensor/report
    core/
      config.py                  環境變數與設定載入
      geo.py                     Haversine 距離與地理工具
      thresholds.py              AQI 區間與 PM2.5 轉 AQI 估算
    providers/
      airbox.py                  AirBox/LASS 即時資料來源
      cwa.py                     CWA 氣象觀測與預報資料來源
      moenv.py                   MOENV 官方 AQI 資料來源
      mqtt_ingest.py             ESP32 風格資料的 MQTT 匯入工具
    schemas/
      air_quality.py             API request / response models
    services/
      fusion.py                  多來源資料融合與情境規則
      prompting.py               結構化 LLM prompt 建立器
      advisor.py                 OpenAI 回應產生與 fallback 文字
    web/
      index.html                 前端頁面
      static/app.js              前端 API 呼叫與 UI 更新
      static/styles.css          前端樣式
    cli.py                       本機命令列融合示範
    main.py                      FastAPI application entry point
    serial_bridge.py             Arduino Serial-to-HTTP bridge
    simulate_sensor.py           感測器模擬腳本
  docs/
    architecture.md              架構說明與資料層圖
    file_guide.md                逐檔案說明
  firmware/
    arduino_uno_serial/          Arduino Uno PMS5003T Serial firmware
    esp32_micropython/           ESP32 MicroPython MQTT example
  tests/                         providers、fusion、geo、advisor、frontend 的單元測試
  .env.example                   環境變數範本
  pyproject.toml                 Python dependencies and project metadata
  README.md                      English README
  README.zh-Hant.md              Traditional Chinese README
```

主要執行流程：

```text
Frontend or Arduino bridge
  -> POST /sensor/report
  -> load local sensor data
  -> fetch nearest AirBox, MOENV, and CWA data
  -> FusionService scenario analysis
  -> structured LLM prompt
  -> OpenAI or rule-based fallback message
  -> frontend user advice
```

## 分析方式

AirFusion AI 透過多尺度融合流程分析空氣品質。

### 資料收集

本地層會接收 Arduino/ESP32 感測器或前端手動輸入的 PM2.5、PM10、溫度與濕度。社區層會使用 AirBox 公開 JSON endpoint，並選出半徑內的最近測站。區域層會使用 MOENV 官方 AQI 資料。氣象層則使用 CWA 觀測站資料，包含風速、風向、降水、溫度與濕度。

### 地理比對

專案使用 Haversine 公式計算使用者經緯度與各測站之間的距離，並選出最近且有效的外部資料來源。

### 情境分類

情境引擎在 `app/services/fusion.py` 中實作，使用明確規則，而不是機器學習模型：

| 情境 | 判斷邏輯 | 信心 |
| --- | --- | --- |
| `indoor_source` | 本地 PM2.5 比 AirBox/MOENV 的室外背景高至少 15。 | 0.86 |
| `neighborhood_hotspot` | 本地與 AirBox PM2.5 都至少 35，而且 AirBox 比 MOENV 高至少 12。 | 0.82 |
| `regional_pollution` | 本地與區域 PM2.5 都至少 35，而且社區資料缺失或也偏高。 | 0.78 |
| `official_alert` | 官方區域 AQI 至少 101。 | 0.72 |
| `normal` | 沒有明顯跨尺度異常。 | 0.68 |
| `insufficient_local_data` | 缺少本地 PM2.5。 | 0.20 |

這些信心值是固定規則分數，代表規則命中強度，而不是訓練模型的統計機率。

### 風險分析

風險優先使用官方 AQI；若官方 AQI 不可用，系統會以本地 PM2.5 估算 AQI，並對應到 `good`、`moderate`、`unhealthy_sensitive`、`unhealthy`、`very_unhealthy` 等區間。

### Prompt Engineering

prompt 在 `app/services/prompting.py` 中建立，會以結構化 tag 分隔輸入：

```text
<target_language>Traditional Chinese</target_language>
<role>You are an air-quality and personal exposure risk analyst.</role>
<task>Use multi-scale data to identify likely pollution source, health risk, and immediate actions.</task>
<local>...</local>
<neighborhood>...</neighborhood>
<regional>...</regional>
<weather>...</weather>
<fusion>scenario=... confidence=... risk_aqi=... risk_band=...</fusion>
<output_format>Return three numbered items: source judgment, health risk, and immediate recommendations.</output_format>
```

這樣可以讓 LLM 保持上下文明確，同時限制輸出格式。模型會被要求在 120 字以內，用實際可行的語言，並回傳來源判斷、健康風險與即時建議。

## 結果

目前專案已完成一個可運作的端到端原型，結果包含：

- FastAPI 後端接受 `/sensor/report`
- 前端 dashboard 顯示 Arduino 即時資料、外部測站資料、氣象資料與 AI 建議
- Arduino Uno 韌體讀取 PMS5003T frame，透過 USB Serial 輸出 JSON
- Python bridge 將 Arduino Serial JSON 轉送到後端
- AirBox/LASS、MOENV AQI、CWA 氣象的即時整合
- 使用規則的融合引擎，可分類污染情境並產生實用建議
- 結構化 OpenAI prompt pipeline，OpenAI 不可用時會使用 rule-based fallback
- 前端語言切換器，可重新產生繁體中文、英文、韓文、泰文或越南文建議
- 單元測試涵蓋地理距離、資料來源、融合邏輯、advisor fallback 與前端靜態檔

主要結論是：把本地感測器與社區、區域、氣象資料結合後，會比只看單一 PM2.5 更有幫助。系統可以區分可能的室內污染、局部社區熱點、廣域污染，以及官方 AQI 警示。

未來可以再加入歷史資料儲存、趨勢圖、低成本感測器校正、擴充氣象預報支援，以及以經過驗證的預測模型取代固定規則。

## 貢獻者

| 貢獻者 | 職責 |
| --- | --- |
| Project team | 系統設計、後端實作、前端介面、感測器整合、資料融合、prompt engineering、測試與文件。 |

正式交件前，請在這裡補上個人姓名與責任分工。

## 感謝

本專案使用 AirBox/LASS、台灣環境部、台灣中央氣象署等公開資料，也使用 FastAPI、httpx、Pydantic、Uvicorn、paho-mqtt、pyserial 與 OpenAI Python SDK 等開源軟體。

## 參考資料

- AirBox/LASS PM2.5 Open Data Portal: https://pm25.lass-net.org/
- AirBox status JSON endpoint: https://pm25.lass-net.org/data/last-all-airbox.json
- Taiwan Ministry of Environment AQI open data: https://data.moenv.gov.tw/api/v2/AQX_P_432
- Taiwan Central Weather Administration Open Data Platform: https://opendata.cwa.gov.tw/
- CWA current weather observation dataset `O-A0003-001`: https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001
- CWA forecast dataset `F-C0032-001`: https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001
- Haversine formula reference: https://en.wikipedia.org/wiki/Haversine_formula
- FastAPI documentation: https://fastapi.tiangolo.com/
- OpenAI Python SDK documentation: https://github.com/openai/openai-python
- Plantower PMS5003/PMS5003T particulate matter sensor documentation
