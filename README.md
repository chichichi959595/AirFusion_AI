# AI-Powered Air Quality Interpretation System

## Project Description

AI-Powered Air Quality Interpretation System, also called AirFusion AI, is a multi-source air quality analysis service that turns sensor readings into user-facing health advice.

The project combines three levels of air quality and weather data:

- **Local data**: Arduino Uno or ESP32 sensor readings from a PMS5003/PMS5003T particulate matter sensor, including PM2.5, PM10, temperature, and humidity.
- **Neighborhood data**: nearby AirBox/LASS community sensor readings selected by geographic distance.
- **Regional data**: official MOENV AQI and PM2.5 data plus CWA weather observations such as wind speed, wind direction, humidity, and precipitation.

The system is important because a single PM2.5 number does not explain where pollution is coming from or what the user should do next. AirFusion AI compares local, neighborhood, regional, and weather conditions to identify likely pollution scenarios, estimate health risk, and generate clear recommendations in multiple languages.

The main analytical methods are:

- Haversine distance matching to select the nearest AirBox, MOENV, and CWA stations.
- Rule-based scenario classification for indoor sources, neighborhood hotspots, regional pollution, official alerts, and normal conditions.
- AQI band mapping from official AQI or estimated AQI from PM2.5.
- Structured prompt engineering to convert fused data into concise OpenAI-generated advice.
- Rule-based fallback messaging when an OpenAI API key is unavailable or the LLM call fails.

## Getting Started

### Prerequisites

- Python 3.11 or newer
- Arduino IDE if using the Arduino Uno firmware
- Optional: OpenAI API key for AI-generated advice
- Optional: MOENV API key for official AQI data
- Optional: CWA API key for live weather observation data

### Installation

```powershell
cd "C:\Users\Hayden Ho\Desktop\coding\AirFusion_AI"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Edit `.env` and fill in the keys that are available:

```text
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.4-nano
MOENV_API_KEY=your_moenv_api_key
CWA_API_KEY=your_cwa_api_key
```

The system can still run without an OpenAI key. In that case, the response will use the local rule-based fallback message.

### Run the Web Application

```powershell
uvicorn app.main:app --reload
```

Open the application and API documentation:

- Web interface: http://127.0.0.1:8000/
- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

### Test Without Hardware

Run a simulated sensor report:

```powershell
python -m app.simulate_sensor
```

Or send a manual request to the main endpoint:

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

The response includes the generated user message, message source, selected data sources, scenario, recommendations, and the structured LLM prompt.

### Language Switching / 語言切換

前端提供輸出語言切換功能，使用者可以在頁面右上方的 language selector 選擇回覆語言。目前支援：

- 繁體中文（`zh-Hant`）
- English（`en`）
- 한국어（`ko`）
- ไทย（`th`）
- Tiếng Việt（`vi`）

語言選擇會透過 API request 的 `language` 欄位送到後端。後端會在 `build_air_quality_prompt()` 中加入 `<target_language>`，並在 OpenAI instructions 中要求模型使用指定語言輸出。若 OpenAI 不可用，本地 rule-based fallback 也會依照語言參數產生對應語言的建議文字。

在 Arduino live 模式下，前端會保留最新一筆感測資料。當使用者切換語言時，系統會用同一筆最新感測數據重新呼叫 `/sensor/report`，產生新的語言版本建議，不需要 Arduino 重新送出資料。

### Use Arduino Uno Serial Data

Arduino Uno does not have built-in Wi-Fi, so this project uses USB Serial plus a Python bridge.

1. Upload `firmware/arduino_uno_serial/AirFusionUnoSerial/AirFusionUnoSerial.ino` to the Arduino Uno.
2. Wire the PMS5003T sensor:
   - `PMS5003T VCC -> Uno 5V`
   - `PMS5003T GND -> Uno GND`
   - `PMS5003T TX -> Uno D10`
   - `PMS5003T RX -> leave disconnected`
3. Start the backend with `uvicorn app.main:app --reload --host 0.0.0.0`.
4. List available serial ports:

```powershell
python -m app.serial_bridge --list-ports
```

5. Forward Arduino JSON reports to the backend:

```powershell
python -m app.serial_bridge --port COM7
```

Replace `COM7` with the actual Arduino port.

### Run Tests

```powershell
python -m unittest discover -s tests
```

## File Structure

```text
AirFusion_AI/
  app/
    api/
      routes.py                  FastAPI endpoints, including /sensor/report
    core/
      config.py                  Environment variable and settings loader
      geo.py                     Haversine distance and location utilities
      thresholds.py              AQI bands and PM2.5-to-AQI estimation
    providers/
      airbox.py                  AirBox/LASS live data provider
      cwa.py                     CWA weather observation and forecast provider
      moenv.py                   MOENV official AQI provider
      mqtt_ingest.py             MQTT ingestion helper for ESP32-style data
    schemas/
      air_quality.py             API request and response models
    services/
      fusion.py                  Multi-source data fusion and scenario rules
      prompting.py               Structured LLM prompt builder
      advisor.py                 OpenAI response generation and fallback text
    web/
      index.html                 Frontend page
      static/app.js              Frontend API calls and UI updates
      static/styles.css          Frontend styling
    cli.py                       Local command-line fusion demo
    main.py                      FastAPI application entry point
    serial_bridge.py             Arduino Serial-to-HTTP bridge
    simulate_sensor.py           Sensor simulation script
  docs/
    architecture.md              Architecture notes and data layer diagram
    file_guide.md                Detailed file-by-file project guide
  firmware/
    arduino_uno_serial/          Arduino Uno PMS5003T Serial firmware
    esp32_micropython/           ESP32 MicroPython MQTT example
  tests/                         Unit tests for providers, fusion, geo, advisor, frontend
  .env.example                   Environment variable template
  pyproject.toml                 Python dependencies and project metadata
  README.md                      Project overview and setup instructions
```

The main runtime flow is:

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

## Analysis

AirFusion AI analyzes air quality through a multi-scale fusion process.

### Data Collection

The local layer receives PM2.5, PM10, temperature, and humidity from the Arduino/ESP32 sensor or from manual frontend input during testing. The neighborhood layer uses the AirBox public JSON endpoint and selects nearby stations within a radius. The regional layer uses MOENV official AQI data. The weather layer uses CWA observation station data, including wind speed, wind direction, precipitation, temperature, and humidity.

### Geographic Matching

The project uses the Haversine formula to calculate the distance between the user's latitude/longitude and each available station. The nearest valid station is selected as the best matching external data source.

### Scenario Classification

The scenario engine is implemented in `app/services/fusion.py`. It uses explicit thresholds rather than a machine learning model:

| Scenario | Logic | Confidence |
| --- | --- | --- |
| `indoor_source` | Local PM2.5 is at least 15 higher than the outdoor baseline from AirBox/MOENV. | 0.86 |
| `neighborhood_hotspot` | Local and AirBox PM2.5 are both at least 35, and AirBox is at least 12 higher than MOENV. | 0.82 |
| `regional_pollution` | Local and regional PM2.5 are both at least 35, and neighborhood data is either missing or also high. | 0.78 |
| `official_alert` | Official regional AQI is at least 101. | 0.72 |
| `normal` | No strong cross-scale anomaly is detected. | 0.68 |
| `insufficient_local_data` | Local PM2.5 is missing. | 0.20 |

The confidence values are fixed rule scores. They represent the strength of the rule match, not a statistical probability from a trained model.

### Risk Analysis

Risk is based on official AQI when available. If official AQI is unavailable, the system estimates AQI from local PM2.5 and maps it into bands such as `good`, `moderate`, `unhealthy_sensitive`, `unhealthy`, and `very_unhealthy`.

### Prompt Engineering

The prompt is built in `app/services/prompting.py`. It separates the input into structured tags:

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

This structure gives the LLM context while keeping the output constrained. The model is instructed to write within 120 words, use practical language, and return advice that includes source judgment, health risk, and immediate actions.

## Results

The current project produces a working end-to-end prototype with these results:

- A FastAPI backend that accepts local sensor reports through `/sensor/report`.
- A frontend dashboard that displays live Arduino sensor values, external station data, weather data, and AI-generated advice.
- Arduino Uno firmware that reads PMS5003T frames and prints JSON over USB Serial.
- A Python bridge that forwards Arduino Serial JSON to the backend.
- Live provider integrations for AirBox/LASS, MOENV AQI, and CWA weather observations.
- A rule-based fusion engine that classifies pollution scenarios and generates practical recommendations.
- A structured OpenAI prompt pipeline with rule-based fallback when OpenAI is unavailable.
- A frontend language switcher that regenerates the advice in Traditional Chinese, English, Korean, Thai, or Vietnamese.
- Unit tests covering geographic distance, data providers, fusion logic, advisor fallback text, and frontend static files.

The main conclusion is that combining local sensor readings with neighborhood, regional, and weather data creates more useful advice than showing a single PM2.5 value. The system can distinguish between likely indoor pollution, local neighborhood hotspots, broader regional pollution, and official AQI alerts.

Future improvements could include storing historical readings, adding trend visualizations, calibrating low-cost sensor values, expanding weather forecast support, and replacing fixed scenario rules with a validated predictive model.

## Contributors

| Contributor | Role and Responsibility |
| --- | --- |
| Project team | System design, backend implementation, frontend interface, sensor integration, data fusion, prompt engineering, testing, and documentation. |

Update this section with individual names and responsibilities before final submission.

## Acknowledgments

This project uses public and open data sources from AirBox/LASS, Taiwan's Ministry of Environment, and Taiwan's Central Weather Administration. It also uses open-source software including FastAPI, httpx, Pydantic, Uvicorn, paho-mqtt, pyserial, and the OpenAI Python SDK.

## References

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
