# AirFusion AI

AirFusion AI 是一個空氣品質文字建議服務。實際資源設定如下：

- 你只有 `OPENAI_API_KEY`。
- Arduino / ESP32 檢測器會回傳 PM2.5、PM10、溫度、濕度等資料。
- 後端可融合 AirBox、氣象局或測試資料。
- 最後回傳一段可直接顯示給 user 的繁體中文建議。

目前版本可先用本機測試成功；若沒有 OpenAI key，系統會用本地規則產生文字，方便確認 API pipeline 正常。若有 OpenAI key，`message_source` 會顯示 `openai`。

## 快速啟動

```powershell
cd "C:\Users\Hayden Ho\Desktop\coding\AirFusion_AI"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

編輯 `.env`，至少填：

```text
OPENAI_API_KEY=你的 OpenAI API Key
OPENAI_MODEL=gpt-5.4-nano
```

啟動 API：

```powershell
uvicorn app.main:app --reload
```

開啟文件：

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

首頁是一個 90s Retro / Windows 95 風格的測試面板，可直接填 Arduino、AirBox、官方 AQI 與氣象資料，按 `SEND REPORT` 後會呼叫 `/sensor/report` 並顯示給 user 看的文字建議。

目前 `/sensor/report` 會優先使用 `.env` 的 `CWA_API_KEY` 自動抓中央氣象署即時觀測站資料，並依照表單經緯度選擇最近測站。回傳中的 `weather_source` 若出現 `CWA observation ...`，代表氣象資料是真實 CWA 資料；若 CWA 暫時失敗，才會退回手動測試值。

## 不接硬體先測試

```powershell
python -m app.simulate_sensor
```

你會看到：

```json
{
  "ok": true,
  "message_source": "openai",
  "scenario": "indoor_source",
  "message": "..."
}
```

若沒有 OpenAI key，`message_source` 會是 `rule_based`，代表本地融合邏輯正常，但還沒呼叫 OpenAI。

## 用 PowerShell 模擬 Arduino POST

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
    "humidity": 60,
    "neighborhood_pm25": 20,
    "regional_pm25": 18,
    "regional_aqi": 62,
    "wind_speed": 3.2,
    "wind_direction": "NE",
    "rain_probability": 20
  }'
```

回傳會包含：

- `message`：給 user 看的文字。
- `message_source`：`openai`、`rule_based` 或 `fallback`。
- `scenario`：污染情境，例如 `indoor_source`、`neighborhood_hotspot`。
- `recommendations`：系統原始建議清單。
- `llm_prompt`：餵給 OpenAI 的結構化內容，方便 debug。

## Arduino 要送的 JSON

Arduino 只要送到：

```text
POST /sensor/report
```

最小資料：

```json
{
  "device_id": "arduino-sensor01",
  "pm25": 45,
  "temperature": 27,
  "humidity": 60
}
```

若你已經有 AirBox 或氣象資料，也可以一起帶：

```json
{
  "device_id": "arduino-sensor01",
  "pm25": 50,
  "neighborhood_pm25": 52,
  "regional_pm25": 25,
  "regional_aqi": 70,
  "wind_speed": 2.8,
  "wind_direction": "NE"
}
```

## 測試

```powershell
python -m unittest discover -s tests
```

## 專案重點

- `app/api/routes.py`：API endpoint。
- `app/services/fusion.py`：Local / AirBox / 官方資料融合與情境判斷。
- `app/services/advisor.py`：OpenAI 文字產生與本地備援文字。
- `app/services/prompting.py`：低雜訊結構化 prompt。
- `firmware/esp32_micropython/main.py`：ESP32 MQTT 範例，可再改成 HTTP POST。

## 關於氣象局資料

已串接中央氣象署 CWA 即時觀測資料 `O-A0003-001`。後端會取得各測站的座標、風速、風向、溫度、濕度與目前降水量，再用 Haversine 距離挑選離使用者最近的測站。

注意：這是即時觀測資料，因此提供的是目前降水量 `precipitation`，不是未來降雨機率 `rain_probability`。未來若要預報，可再加上 `F-C0032-001` 作為第二個 CWA 資料源。
