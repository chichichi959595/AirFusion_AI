# AI 空氣品質智慧判讀系統

[English](README.md) | **繁體中文**

## 專案說明

AI 空氣品質智慧判讀系統，也稱為 AirFusion AI，是一個多資料來源的空氣品質分析服務。它會把感測器讀值轉換成使用者能理解的健康建議。

本專案整合三個層級的空氣品質與氣象資料：

- **本地資料**：Arduino Uno 或 ESP32 搭配 PMS5003/PMS5003T 感測器，讀取 PM2.5、PM10、溫度與濕度。
- **社區資料**：依照地理距離選擇附近的 AirBox/LASS 社區感測站。
- **區域資料**：環境部 MOENV 官方 AQI / PM2.5 資料，以及中央氣象署 CWA 的風速、風向、濕度、降水等觀測資料。

單一 PM2.5 數字無法說明污染來源，也無法直接告訴使用者該怎麼做。AirFusion AI 會比較本地、社區、官方區域與氣象條件，判斷可能的污染情境、估計健康風險，並以多語言產生清楚的建議。

## 主要功能

- 使用 Haversine 距離公式選擇最近的 AirBox、MOENV、CWA 測站。
- 以規則判斷室內污染源、社區熱點、區域污染、官方警示與正常情境。
- 使用官方 AQI 或由 PM2.5 估算 AQI 風險等級。
- 透過結構化 prompt 將融合後的資料交給 OpenAI 產生建議。
- OpenAI 不可用時，自動使用本地規則 fallback。
- 前端 dashboard 顯示 Arduino 即時資料、外部測站資料、氣象資料與 AI 建議。
- 支援繁體中文、英文、韓文、泰文、越南文輸出。

## 安裝

```powershell
cd "C:\Users\Hayden Ho\Desktop\coding\AirFusion_AI"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

編輯 `.env`：

```text
OPENAI_API_KEY=你的 OpenAI API Key
OPENAI_MODEL=gpt-5.4-nano
MOENV_API_KEY=你的環境部 API Key
CWA_API_KEY=你的中央氣象署 API Key
```

即使沒有 OpenAI key，系統仍可執行；回應會改用本地規則產生。

## 啟動 Web 應用程式

```powershell
uvicorn app.main:app --reload
```

開啟：

- Web 介面：<http://127.0.0.1:8000/>
- API 文件：<http://127.0.0.1:8000/docs>
- 健康檢查：<http://127.0.0.1:8000/health>

## 不接硬體測試

```powershell
python -m app.simulate_sensor
```

或手動送出測試資料：

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

回應會包含使用者訊息、訊息來源、資料來源、情境分類、建議與 LLM prompt。

## Arduino Uno Serial 資料

Arduino Uno 沒有內建 Wi-Fi，因此本專案使用 USB Serial 加上 Python bridge。

1. 將 `firmware/arduino_uno_serial/AirFusionUnoSerial/AirFusionUnoSerial.ino` 上傳到 Arduino Uno。
2. 接線：
   - `PMS5003T VCC -> Uno 5V`
   - `PMS5003T GND -> Uno GND`
   - `PMS5003T TX -> Uno D10`
   - `PMS5003T RX -> 不接`
3. 啟動後端：

```powershell
uvicorn app.main:app --reload --host 0.0.0.0
```

4. 查看可用序列埠：

```powershell
python -m app.serial_bridge --list-ports
```

5. 將 Arduino JSON 轉送到後端：

```powershell
python -m app.serial_bridge --port COM7
```

請將 `COM7` 換成實際的 Arduino port。

## 測試

```powershell
python -m unittest discover -s tests
```

## 專案結構

```text
AirFusion_AI/
  app/
    api/routes.py              FastAPI endpoints
    core/                      設定、地理距離、AQI 閾值
    providers/                 AirBox、CWA、MOENV 資料來源
    schemas/                   API request / response models
    services/                  資料融合、prompt、AI 建議
    web/                       前端 dashboard
    serial_bridge.py           Arduino Serial-to-HTTP bridge
    simulate_sensor.py         感測器模擬
  docs/                        文件
  firmware/                    Arduino / ESP32 韌體
  tests/                       單元測試
```

## 分析方法

AirFusion AI 使用多尺度融合流程：

1. 本地層：Arduino/ESP32 感測器或前端表單輸入 PM2.5、PM10、溫度、濕度。
2. 社區層：AirBox 公開 JSON 資料，依距離選擇附近測站。
3. 區域層：MOENV 官方 AQI 與 CWA 即時氣象觀測。
4. 融合層：`FusionService` 使用明確規則判斷污染情境。
5. 建議層：OpenAI 或本地 fallback 產生使用者可讀的健康建議。

## 情境分類

| 情境 | 判斷邏輯 |
| --- | --- |
| `indoor_source` | 本地 PM2.5 明顯高於室外背景值 |
| `neighborhood_hotspot` | 本地與 AirBox 偏高，但官方站較低 |
| `regional_pollution` | 本地與官方區域資料皆偏高 |
| `official_alert` | 官方 AQI 達到對敏感族群不健康以上 |
| `normal` | 沒有明顯跨尺度異常 |
| `insufficient_local_data` | 缺少本地 PM2.5 |

## 結果

目前專案已完成端到端原型：

- FastAPI 後端接收 `/sensor/report`
- Arduino Uno 讀取 PMS5003T 並透過 USB Serial 輸出 JSON
- Python bridge 將 Arduino 資料轉送到後端
- AirBox、MOENV、CWA 即時資料整合
- 前端即時顯示 Arduino 資料與 AI 建議
- OpenAI 建議與本地 fallback
- 多語言輸出

## 參考資料

- AirBox/LASS PM2.5 Open Data Portal: https://pm25.lass-net.org/
- AirBox status JSON endpoint: https://pm25.lass-net.org/data/last-all-airbox.json
- Taiwan Ministry of Environment AQI open data: https://data.moenv.gov.tw/api/v2/AQX_P_432
- Taiwan Central Weather Administration Open Data Platform: https://opendata.cwa.gov.tw/
- FastAPI documentation: https://fastapi.tiangolo.com/
- OpenAI Python SDK documentation: https://github.com/openai/openai-python
