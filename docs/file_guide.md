# AirFusion AI File Guide

這份文件說明 AirFusion AI 專案中每個主要檔案在做什麼。讀完後，你應該能知道：

- 前端畫面在哪裡改。
- API endpoint 在哪裡。
- AirBox / CWA / MOENV / OpenAI 分別在哪裡串接。
- Arduino 之後要接到哪個入口。
- 測試檔各自保護哪些功能。

## 專案總覽

```text
AirFusion_AI/
  app/                         Python 後端與前端靜態頁
    api/                       FastAPI 路由
    core/                      設定、地理計算、AQI 閾值
    providers/                 外部資料來源串接
    schemas/                   API request/response 格式
    services/                  資料融合、OpenAI 回覆、prompt
    web/                       90s 風格前端頁面
  docs/                        專案文件
  firmware/                    ESP32 / MicroPython 範例
  tests/                       單元測試
  .env                         本機金鑰與環境設定，不要上傳
  .env.example                 環境變數範本
  pyproject.toml               Python 專案依賴與套件設定
  README.md                    使用說明
```

## 核心執行流程

目前前端按下 `Send Report` 後，流程是：

```text
app/web/static/app.js
  -> POST /sensor/report
  -> app/api/routes.py
  -> AirBoxProvider / MoenvProvider / CwaProvider
  -> FusionService
  -> build_air_quality_prompt
  -> AdvisorService 呼叫 OpenAI
  -> 回傳 message 給前端
```

也就是：

```text
本地感測器資料
  + AirBox 即時資料
  + MOENV 官方 AQI / PM2.5
  + CWA 即時氣象
  -> 資料融合
  -> OpenAI 多語言文字建議
```

## 根目錄檔案

### `.env`

本機環境變數檔，存放 API key 和設定。

目前重要欄位：

```text
OPENAI_API_KEY=
OPENAI_MODEL=
MOENV_API_KEY=
CWA_API_KEY=
```

注意：這個檔案含敏感資訊，不應提交到 GitHub。

### `.env.example`

環境變數範本。給其他環境或之後重新部署時參考用。裡面不應放真的 key。

### `.gitignore`

告訴 Git 哪些檔案不要追蹤，例如：

- `.env`
- `.venv/`
- `__pycache__/`
- build / cache 檔案

### `pyproject.toml`

Python 專案設定，定義：

- 專案名稱 `airfusion-ai`
- Python 版本需求
- 後端依賴：FastAPI、Uvicorn、httpx、OpenAI SDK、pydantic、dotenv、paho-mqtt
- 開發依賴：ruff

如果未來要新增 Python 套件，通常會加在這裡。

### `README.md`

主要使用說明。包含：

- 如何啟動 server
- 如何測試 `/sensor/report`
- 目前哪些資料是真實串接
- API 測試範例

### `整合多維度數據進行空氣品質分析.txt`

最初的需求與研究文件。專案架構就是從這份文件延伸出來的，包括：

- Local：Arduino / ESP32 感測器
- Neighborhood：AirBox
- Regional：MOENV / CWA
- AI：OpenAI 產生使用者建議

## `app/`

後端主程式、資料模型、服務邏輯、前端靜態頁都在這裡。

### `app/main.py`

FastAPI app 入口。

主要負責：

- 建立 FastAPI app
- 掛上 API router
- 掛上 `/static` 靜態檔
- 提供 `/` 前端首頁

重要路由：

```text
GET /
GET /static/*
```

如果前端首頁打不開，通常先看這個檔案。

### `app/domain.py`

核心資料模型，使用 Python dataclass。

主要類別：

- `AirReading`：空氣品質讀值，例如 PM2.5、PM10、AQI、溫濕度、位置、距離。
- `WeatherReading`：氣象讀值，例如風速、風向、降水量、濕度、氣象站位置。
- `FusionResult`：資料融合後的結果，例如情境、信心分數、建議、推理理由。

這裡是後端內部邏輯共用的資料格式。

### `app/cli.py`

命令列 demo。

用途：

- 不啟動 server 也能跑一次資料融合範例。
- 測試 `FusionService` 和 prompt 產生是否正常。

執行：

```powershell
python -m app.cli
```

### `app/simulate_sensor.py`

本地模擬感測器資料的腳本。

用途：

- 在 Arduino 還沒接上之前，用假 PM2.5 測後端分析。
- 會建立 local / neighborhood / regional / weather 範例資料並輸出結果。

執行：

```powershell
python -m app.simulate_sensor
```

### `app/__init__.py`

讓 `app` 成為 Python package。通常不需要修改。

## `app/api/`

FastAPI 路由層，負責接 HTTP request。

### `app/api/routes.py`

目前最重要的 API 檔案。

提供：

```text
GET /health
POST /analyze
POST /sensor/report
```

其中 `/sensor/report` 是目前前端和之後 Arduino 要打的主要 endpoint。

`/sensor/report` 做的事情：

1. 讀取本地感測器資料。
2. 呼叫 AirBox live provider 找最近 AirBox。
3. 呼叫 MOENV live provider 找最近官方 AQI 測站。
4. 呼叫 CWA live provider 找最近氣象站。
5. 用 `FusionService` 判斷污染情境。
6. 用 `build_air_quality_prompt` 產生 prompt。
7. 用 `AdvisorService` 呼叫 OpenAI 產生多語言文字。
8. 回傳前端需要顯示的所有欄位。

如果要接 Arduino，通常就是讓 Arduino POST 到這裡。

### `app/api/__init__.py`

讓 `api` 成為 package。通常不需要修改。

## `app/core/`

基礎工具與設定。

### `app/core/config.py`

讀取 `.env` 的設定。

主要函式：

```python
get_settings()
```

會讀：

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `MOENV_API_KEY`
- `CWA_API_KEY`
- `MQTT_BROKER_URL`
- `MQTT_TOPIC`
- 預設座標與半徑

如果改了 `.env`，通常要重啟 server 才會生效。

### `app/core/geo.py`

地理計算工具。

主要功能：

- `Location`：經緯度資料類別。
- `haversine_distance_km()`：計算兩個經緯度點的距離。
- `nearest_station()`：從站點列表找最近站。

AirBox、MOENV、CWA 找最近站都依賴這裡的 Haversine 邏輯。

### `app/core/thresholds.py`

AQI 風險分級與 PM2.5 估算 AQI。

主要功能：

- `AQI_BANDS`：good、moderate、unhealthy_sensitive 等分級。
- `band_for_aqi()`：AQI 轉風險級距。
- `estimate_aqi_from_pm25()`：沒有官方 AQI 時，用 PM2.5 粗估 AQI。

### `app/core/__init__.py`

Package marker。通常不需要修改。

## `app/providers/`

外部資料來源串接。每個 provider 負責一種資料源。

### `app/providers/airbox.py`

AirBox / LASS 開放資料串接。

資料來源：

```text
https://pm25.lass-net.org/data/last-all-airbox.json
```

主要功能：

- 下載所有 AirBox feed。
- 解析 `gps_lat`、`gps_lon`、`s_d0`、`s_t0`、`s_h0`。
- 用使用者經緯度找最近 AirBox。
- 回傳 `AirReading`。

注意：這裡特別處理了 `PM2.5 = 0.0`，不能把它當成沒有資料。

### `app/providers/moenv.py`

環境部官方 AQI / PM2.5 串接。

資料來源：

```text
https://data.moenv.gov.tw/api/v2/AQX_P_432
```

主要功能：

- 使用 `.env` 裡的 `MOENV_API_KEY`。
- 抓官方測站 AQI 資料。
- 解析 `sitename`、`aqi`、`pm2.5`、`pm10`、`longitude`、`latitude`。
- 找離使用者最近的官方測站。
- 回傳 `AirReading`。

曾修過的重點：

- 環境部 API 實際回傳是 list，不一定是 `{ records: [...] }`，所以程式同時支援兩種格式。

### `app/providers/cwa.py`

中央氣象署即時觀測資料串接。

資料來源：

```text
https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001
```

主要功能：

- 使用 `.env` 裡的 `CWA_API_KEY`。
- 抓所有即時氣象觀測站。
- 解析站點座標、風速、風向、氣溫、濕度、目前降水量。
- 找離使用者最近的氣象站。
- 回傳 `WeatherReading`。

注意：

- 目前抓的是即時觀測，不是預報。
- `precipitation` 是目前降水量，不是未來降雨機率。

### `app/providers/mqtt_ingest.py`

MQTT 資料接收骨架。

用途：

- 未來如果 Arduino / ESP32 不是用 HTTP POST，而是用 MQTT 發資料，可以用這個檔案接。
- 目前主要流程還是 `/sensor/report` HTTP API。

### `app/providers/__init__.py`

Package marker。通常不需要修改。

## `app/schemas/`

API request / response 格式。

### `app/schemas/air_quality.py`

Pydantic schema 定義。

主要類別：

- `LocationPayload`
- `AirReadingPayload`
- `WeatherPayload`
- `AnalysisRequest`
- `AnalysisResponse`
- `SensorReportRequest`
- `SensorReportResponse`

目前多語言也在這裡定義：

```python
SupportedLanguage = Literal["zh-Hant", "en", "ko", "th", "vi"]
```

如果之後要新增語言，例如日文，就要在這裡加。

### `app/schemas/__init__.py`

Package marker。通常不需要修改。

## `app/services/`

商業邏輯層，也就是「資料拿到後要怎麼判斷、怎麼產生回答」。

### `app/services/fusion.py`

資料融合與污染情境判斷。

主要類別：

```python
FusionService
```

目前會判斷：

- `indoor_source`：室內 PM2.5 明顯高於室外。
- `neighborhood_hotspot`：local 和 AirBox 都高，但官方站較低。
- `regional_pollution`：三層資料都偏高。
- `official_alert`：官方 AQI 達警示。
- `normal`：沒有明顯異常。

也會產生：

- `summary`
- `recommendations`
- `reasoning`
- `confidence`
- `risk_aqi`
- `risk_band`

如果你覺得判斷邏輯不符合現場經驗，通常改這個檔案。

### `app/services/prompting.py`

把融合結果轉成給 OpenAI 的結構化 prompt。

主要函式：

```python
build_air_quality_prompt(result, language="zh-Hant")
```

prompt 內包含：

- target language
- local data
- neighborhood AirBox data
- regional MOENV data
- CWA weather data
- fusion result
- output format

如果 OpenAI 回覆內容需要更穩、更短、更專業，通常改這裡和 `advisor.py`。

### `app/services/advisor.py`

OpenAI 回覆服務。

主要類別：

```python
AdvisorService
```

主要功能：

- 如果有 `OPENAI_API_KEY`，呼叫 OpenAI Responses API。
- 如果沒有 key 或 OpenAI 失敗，退回本地規則文字。
- 支援多語言：
  - 繁體中文 `zh-Hant`
  - 英文 `en`
  - 韓語 `ko`
  - 泰文 `th`
  - 越南文 `vi`

重要函式：

```python
create_user_message()
build_rule_based_message()
```

### `app/services/__init__.py`

Package marker。通常不需要修改。

## `app/web/`

前端頁面，不需要 npm build，直接由 FastAPI 提供。

### `app/web/index.html`

前端 HTML 結構。

目前包含：

- 90s marquee 跑馬燈
- Windows 95 風格 title bar
- 語言切換按鈕
- local sensor 表單
- live sources 狀態列
- AI 回覆顯示區
- AirBox / MOENV / CWA 結果表格
- API docs 連結

如果要增減前端欄位，通常先改這裡。

### `app/web/static/styles.css`

前端樣式檔。

設計風格：

- Windows 95 / 90s nostalgia
- bevel 邊框
- 純色高彩度 palette
- tiled background
- rainbow text
- hit counter
- construction stripe

設計 token 都在 `:root`，例如：

```css
--background: #c0c0c0;
--accent: #0000ff;
--title-bar: #000080;
```

如果要調整外觀，主要改這裡。

### `app/web/static/app.js`

前端互動邏輯。

主要功能：

- 語言切換 UI 字典。
- 收集表單資料。
- POST 到 `/sensor/report`。
- 把回傳的 message、AirBox、MOENV、CWA 結果顯示到畫面。
- 支援語言：
  - `zh-Hant`
  - `en`
  - `ko`
  - `th`
  - `vi`

如果要改前端送出的 JSON 或多語 UI 文字，通常改這裡。

## `docs/`

專案文件。

### `docs/architecture.md`

系統架構說明。

內容包含：

- Local / Neighborhood / Regional 三層資料
- Fusion flow
- Mermaid 架構圖
- 情境判斷規則

### `docs/file_guide.md`

本文件。說明每個檔案的用途。

## `firmware/`

硬體端範例。

### `firmware/esp32_micropython/main.py`

ESP32 MicroPython 範例。

目前是 MQTT 發送 PMS5003 資料的版本。

主要做：

- 連 Wi-Fi
- 讀 PMS5003 UART
- 發 MQTT payload

注意：目前主系統前端和後端主要走 HTTP `/sensor/report`。之後如果要 Arduino 直接 HTTP POST，可以再新增一份 Arduino HTTP 範例。

### `firmware/esp32_micropython/secrets.example.py`

ESP32 Wi-Fi / MQTT 設定範本。

包含：

- `WIFI_SSID`
- `WIFI_PASSWORD`
- `MQTT_BROKER`
- `MQTT_CLIENT_ID`
- `MQTT_TOPIC`

不要把真的 Wi-Fi 密碼提交。

## `tests/`

測試檔。用來防止改程式時把核心功能弄壞。

執行：

```powershell
python -m unittest discover -s tests
```

### `tests/test_geo.py`

測 Haversine 距離計算。

確保木柵與古亭距離落在合理範圍。

### `tests/test_fusion.py`

測資料融合情境判斷。

目前測：

- local 高、室外低時判斷為 `indoor_source`
- local 與 AirBox 高、官方站低時判斷為 `neighborhood_hotspot`

### `tests/test_advisor.py`

測本地 fallback 建議文字是否可讀。

如果沒有 OpenAI key，系統會靠這個 fallback 回覆。

### `tests/test_airbox_provider.py`

測 AirBox provider 解析。

重點保護：

- `PM2.5 = 0.0` 不可以被誤判成沒有資料。
- 站名要使用 `SiteName`。

### `tests/test_moenv_provider.py`

測 MOENV provider 解析。

重點保護：

- AQI、PM2.5、經緯度解析正確。
- API 回傳是 list 或 `{ records: [...] }` 都能處理。

### `tests/test_cwa_provider.py`

測 CWA provider 解析。

重點保護：

- 風向角度轉方位，例如 45 度轉 `NE`。
- 風速、濕度、降水量、站點距離解析正確。

### `tests/test_frontend_static.py`

測前端靜態檔存在，且 90s 風格關鍵元素存在。

包含：

- marquee
- rainbow text
- hit counter
- construction zone
- border-radius: 0

## 現在什麼是真的，什麼還是模擬

目前真實資料：

- OpenAI：真實 API。
- AirBox：真實 live API。
- CWA 氣象：真實 live API。
- MOENV 官方 AQI / PM2.5：真實 live API。

目前模擬資料：

- Local sensor：前端表單模擬。

也就是下一步如果要接硬體，只需要讓 Arduino / ESP32 把本地感測資料送到：

```text
POST /sensor/report
```

## 常見修改位置

### 我要改前端外觀

改：

```text
app/web/static/styles.css
```

### 我要改前端欄位或排版

改：

```text
app/web/index.html
app/web/static/app.js
```

### 我要改 OpenAI 回覆語氣或格式

改：

```text
app/services/advisor.py
app/services/prompting.py
```

### 我要改污染情境判斷邏輯

改：

```text
app/services/fusion.py
```

### 我要改 AirBox / MOENV / CWA 串接

改：

```text
app/providers/airbox.py
app/providers/moenv.py
app/providers/cwa.py
```

### 我要改 API 回傳格式

改：

```text
app/schemas/air_quality.py
app/api/routes.py
```

### 我要接 Arduino HTTP POST

主要會動：

```text
app/api/routes.py
app/schemas/air_quality.py
firmware/
```

## 開發時的安全提醒

- 不要把 `.env` 上傳。
- 修改 `.env` 後要重啟 server。
- 改 provider 後請跑 tests。
- 改前端後請重新整理瀏覽器，必要時按 `Ctrl + F5`。
- 如果 API 回傳中文在 PowerShell 亂碼，通常是 PowerShell 顯示編碼問題，不一定是 API 本身錯。
