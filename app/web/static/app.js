const $ = (selector) => document.querySelector(selector);

const form = $("#sensor-form");
const languageSelect = $("#language-select");
const messageBox = $("#user-message");
const scenarioCell = $("#scenario-cell");
const confidenceCell = $("#confidence-cell");
const sourceCell = $("#source-cell");
const airboxCell = $("#airbox-cell");
const regionalCell = $("#regional-cell");
const weatherCell = $("#weather-cell");
const windCell = $("#wind-cell");
const connectionLight = $("#connection-light");
const connectionText = $("#connection-text");
const heroAirbox = $("#hero-airbox");
const heroMoenv = $("#hero-moenv");
const heroCwa = $("#hero-cwa");
const projectTextType = $("#project-text-type");
const liveSensorLight = $("#live-sensor-light");
const liveSensorStatus = $("#live-sensor-status");
const livePm25 = $("#live-pm25");
const livePm10 = $("#live-pm10");
const liveTemperature = $("#live-temperature");
const liveHumidity = $("#live-humidity");

let selectedLanguage = "zh-Hant";
let textTypeController = null;
const LATEST_SENSOR_POLL_MS = 10000;
let latestReport = null;

const languageLabels = {
  "zh-Hant": "\u7e41\u4e2d",
  en: "English",
  ko: "\ud55c\uad6d\uc5b4",
  th: "\u0e44\u0e17\u0e22",
  vi: "Ti\u1ebfng Vi\u1ec7t",
};

const translations = {
  "zh-Hant": {
    typedTexts: ["AirFusion AI"],
    heroCopy:
      "\u6574\u5408 PMS5003T \u672c\u5730\u611f\u6e2c\u3001AirBox \u793e\u5340\u8cc7\u6599\u3001MOENV \u5b98\u65b9 AQI\u3001CWA \u6c23\u8c61\u8207 OpenAI\uff0c\u7522\u751f\u5373\u6642\u5065\u5eb7\u5efa\u8b70\u3002",
    languageLabel: "\u8f38\u51fa\u8a9e\u8a00",
    formKicker: "\u672c\u5730\u8f38\u5165",
    formTitle: "\u611f\u6e2c\u5668\u56de\u5831",
    deviceId: "\u88dd\u7f6e ID",
    locationLabel: "\u4f4d\u7f6e\u540d\u7a31",
    latitude: "\u7def\u5ea6",
    longitude: "\u7d93\u5ea6",
    temperature: "\u6eab\u5ea6",
    humidity: "\u6fd5\u5ea6",
    liveNote: "AirBox\u3001CWA \u6c23\u8c61\u3001MOENV AQI \u90fd\u662f\u5373\u6642\u8cc7\u6599\u3002\u6b64\u8868\u55ae\u53ea\u6a21\u64ec\u672c\u5730\u611f\u6e2c\u5668\u3002",
    sendReport: "\u9001\u51fa\u5831\u544a",
    indoorPreset: "\u5ba4\u5167\u4f86\u6e90",
    hotspotPreset: "\u9ad8 PM2.5",
    reset: "\u91cd\u8a2d",
    outputKicker: "AI \u5efa\u8b70",
    outputTitle: "\u4f7f\u7528\u8005\u8a0a\u606f",
    waiting: "\u7b49\u5f85\u5831\u544a...",
    placeholder: "\u6309\u4e0b\u9001\u51fa\u5831\u544a\u5f8c\uff0c\u9019\u88e1\u6703\u986f\u793a\u7d66\u4f7f\u7528\u8005\u770b\u7684\u7a7a\u6c23\u54c1\u8cea\u5efa\u8b70\u3002",
    scenario: "\u60c5\u5883",
    confidence: "\u4fe1\u5fc3",
    source: "\u4f86\u6e90",
    officialAqi: "\u5b98\u65b9 AQI",
    weather: "\u6c23\u8c61",
    wind: "\u98a8",
    dialing: "\u6b63\u5728\u9023\u7dda\u5230 /sensor/report...",
    crunching: "\u6b63\u5728\u601d\u8003\u4e2d...",
    received: "\u5df2\u6536\u5230\u5831\u544a\u3002\u8a0a\u606f\u4f86\u6e90\uff1a",
    failed: "\u5831\u544a\u5931\u6557\u3002",
  },
  en: {
    typedTexts: ["AirFusion AI"],
    heroCopy:
      "AirFusion combines PMS5003T local sensing, AirBox community readings, MOENV AQI, CWA weather, and OpenAI advice.",
    languageLabel: "Output language",
    formKicker: "Local input",
    formTitle: "Sensor report",
    deviceId: "Device ID",
    locationLabel: "Location label",
    latitude: "Latitude",
    longitude: "Longitude",
    temperature: "Temperature",
    humidity: "Humidity",
    liveNote: "AirBox, CWA weather, and MOENV AQI are live. This form only simulates the local sensor.",
    sendReport: "Send report",
    indoorPreset: "Indoor source",
    hotspotPreset: "High PM2.5",
    reset: "Reset",
    outputKicker: "Advisor",
    outputTitle: "User message",
    waiting: "Waiting for report...",
    placeholder: "Press Send report to generate the user-facing air quality message.",
    scenario: "Scenario",
    confidence: "Confidence",
    source: "Source",
    officialAqi: "Official AQI",
    weather: "Weather",
    wind: "Wind",
    dialing: "Dialing /sensor/report...",
    crunching: "Thinking...",
    received: "Report received. Message source: ",
    failed: "Report failed.",
  },
  ko: {
    typedTexts: ["AirFusion AI"],
    heroCopy:
      "PMS5003T 로컬 센서, AirBox 지역 데이터, MOENV 공식 AQI, CWA 날씨와 OpenAI 조언을 통합해 실시간 건강 조언을 제공합니다.",
    languageLabel: "출력 언어",
    formKicker: "로컬 입력",
    formTitle: "센서 보고",
    deviceId: "장치 ID",
    locationLabel: "위치 이름",
    latitude: "위도",
    longitude: "경도",
    temperature: "온도",
    humidity: "습도",
    liveNote: "AirBox, CWA 날씨, MOENV AQI는 실시간 데이터입니다. 이 양식은 로컬 센서만 시뮬레이션합니다.",
    sendReport: "보고서 보내기",
    indoorPreset: "실내 오염원",
    hotspotPreset: "높은 PM2.5",
    reset: "초기화",
    outputKicker: "AI 조언",
    outputTitle: "사용자 메시지",
    waiting: "보고서를 기다리는 중...",
    placeholder: "보고서 보내기를 누르면 사용자용 공기질 조언이 표시됩니다.",
    scenario: "상황",
    confidence: "신뢰도",
    source: "출처",
    officialAqi: "공식 AQI",
    weather: "날씨",
    wind: "바람",
    dialing: "/sensor/report에 연결 중...",
    crunching: "생각 중...",
    received: "보고서를 받았습니다. 메시지 출처: ",
    failed: "보고서 전송 실패.",
  },
  th: {
    typedTexts: ["AirFusion AI"],
    heroCopy:
      "รวมข้อมูลจากเซนเซอร์ PMS5003T, AirBox, AQI ทางการจาก MOENV, สภาพอากาศ CWA และคำแนะนำจาก OpenAI เพื่อให้คำแนะนำสุขภาพแบบเรียลไทม์",
    languageLabel: "ภาษาที่แสดงผล",
    formKicker: "ข้อมูลจากพื้นที่",
    formTitle: "รายงานเซนเซอร์",
    deviceId: "รหัสอุปกรณ์",
    locationLabel: "ชื่อสถานที่",
    latitude: "ละติจูด",
    longitude: "ลองจิจูด",
    temperature: "อุณหภูมิ",
    humidity: "ความชื้น",
    liveNote: "AirBox, สภาพอากาศ CWA และ AQI จาก MOENV เป็นข้อมูลสด แบบฟอร์มนี้จำลองเฉพาะเซนเซอร์ท้องถิ่น",
    sendReport: "ส่งรายงาน",
    indoorPreset: "แหล่งกำเนิดในอาคาร",
    hotspotPreset: "PM2.5 สูง",
    reset: "รีเซ็ต",
    outputKicker: "คำแนะนำ AI",
    outputTitle: "ข้อความสำหรับผู้ใช้",
    waiting: "กำลังรอรายงาน...",
    placeholder: "กดส่งรายงานเพื่อสร้างคำแนะนำคุณภาพอากาศสำหรับผู้ใช้",
    scenario: "สถานการณ์",
    confidence: "ความมั่นใจ",
    source: "แหล่งที่มา",
    officialAqi: "AQI ทางการ",
    weather: "สภาพอากาศ",
    wind: "ลม",
    dialing: "กำลังเชื่อมต่อ /sensor/report...",
    crunching: "กำลังคิด...",
    received: "ได้รับรายงานแล้ว แหล่งข้อความ: ",
    failed: "ส่งรายงานไม่สำเร็จ",
  },
  vi: {
    typedTexts: ["AirFusion AI"],
    heroCopy:
      "Kết hợp cảm biến PMS5003T, dữ liệu AirBox, AQI chính thức từ MOENV, thời tiết CWA và tư vấn OpenAI để tạo khuyến nghị sức khỏe theo thời gian thực.",
    languageLabel: "Ngôn ngữ đầu ra",
    formKicker: "Dữ liệu cục bộ",
    formTitle: "Báo cáo cảm biến",
    deviceId: "ID thiết bị",
    locationLabel: "Tên vị trí",
    latitude: "Vĩ độ",
    longitude: "Kinh độ",
    temperature: "Nhiệt độ",
    humidity: "Độ ẩm",
    liveNote: "Dữ liệu AirBox, CWA và MOENV là thực tế; biểu mẫu này chỉ mô phỏng cảm biến cục bộ.",
    sendReport: "Gửi báo cáo",
    indoorPreset: "Nguồn trong nhà",
    hotspotPreset: "PM2.5 cao",
    reset: "Đặt lại",
    outputKicker: "Tư vấn AI",
    outputTitle: "Thông điệp người dùng",
    waiting: "Đang chờ báo cáo...",
    placeholder: "Nhấn gửi báo cáo để tạo khuyến nghị chất lượng không khí cho người dùng.",
    scenario: "Tình huống",
    confidence: "Độ tin cậy",
    source: "Nguồn",
    officialAqi: "AQI chính thức",
    weather: "Thời tiết",
    wind: "Gió",
    dialing: "Đang gọi /sensor/report...",
    crunching: "Đang suy nghĩ...",
    received: "Đã nhận báo cáo. Nguồn thông điệp: ",
    failed: "Gửi báo cáo thất bại.",
  },
};

const presets = {
  indoor: { pm25: 45, pm10: 60, temperature: 27, humidity: 60 },
  hotspot: { pm25: 88, pm10: 120, temperature: 29, humidity: 72 },
};

function dictionary() {
  return translations[selectedLanguage] || translations.en;
}

function t(key) {
  return dictionary()[key] || translations.en[key] || key;
}

function setText(element, text) {
  if (element) element.textContent = text;
}

function setShimmer(element, text) {
  if (!element) return;
  element.innerHTML = "";
  const span = document.createElement("span");
  span.className = "text-shimmer";
  span.textContent = text;
  element.appendChild(span);
}

function startTextType(texts) {
  if (!projectTextType) return;
  if (textTypeController) textTypeController.stop();

  const content = projectTextType.querySelector(".text-type__content");
  if (!content) return;

  let textIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  let timeoutId = null;
  let stopped = false;

  function tick() {
    if (stopped) return;

    const currentText = texts[0] || "AirFusion AI";
    charIndex = Math.min(currentText.length, charIndex + 1);
    content.textContent = currentText.slice(0, charIndex);
    if (charIndex === currentText.length) {
      // Done — stay, no loop
      return;
    }
    timeoutId = window.setTimeout(tick, 75);
  }

  content.textContent = "";
  timeoutId = window.setTimeout(tick, 250);
  textTypeController = {
    stop() {
      stopped = true;
      window.clearTimeout(timeoutId);
    },
  };
}

function applyLanguage(language) {
  selectedLanguage = translations[language] ? language : "en";
  document.documentElement.lang = selectedLanguage;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  startTextType(t("typedTexts"));
  if (messageBox?.dataset.empty === "true") setText(messageBox, t("placeholder"));
  if (connectionText?.dataset.state === "waiting") setText(connectionText, t("waiting"));
}

function numberOrNull(value) {
  if (value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function payloadFromForm() {
  const data = new FormData(form);
  return {
    language: selectedLanguage,
    device_id: data.get("device_id") || "arduino-sensor01",
    lat: numberOrNull(data.get("lat")),
    lon: numberOrNull(data.get("lon")),
    location_label: data.get("location_label") || "Taipei Wenshan",
    pm25: numberOrNull(data.get("pm25")),
    pm10: numberOrNull(data.get("pm10")),
    temperature: numberOrNull(data.get("temperature")),
    humidity: numberOrNull(data.get("humidity")),
  };
}

function payloadFromReport(report) {
  return {
    language: selectedLanguage,
    device_id: report.device_id || "arduino-uno-sensor01",
    lat: numberOrNull(form?.elements.lat?.value) ?? 24.996222,
    lon: numberOrNull(form?.elements.lon?.value) ?? 121.576211,
    location_label: form?.elements.location_label?.value || "Taipei Wenshan",
    pm25: report.local_pm25,
    pm10: report.local_pm10,
    temperature: report.local_temperature,
    humidity: report.local_humidity,
  };
}

function setStatus(kind, text, state = "") {
  connectionLight?.classList.remove("error");
  if (kind === "error") connectionLight?.classList.add("error");
  setText(connectionText, text);
  if (connectionText) connectionText.dataset.state = state;
}

function formatKm(value) {
  return value === null || value === undefined ? "---" : `${value} km`;
}

function updateResult(result) {
  if (messageBox) messageBox.dataset.empty = "false";
  setText(messageBox, result.message || "No message returned.");
  setText(scenarioCell, result.scenario || "---");
  setText(confidenceCell, typeof result.confidence === "number" ? `${Math.round(result.confidence * 100)}%` : "---");
  setText(sourceCell, `${result.message_source || "---"} / ${languageLabels[result.language] || result.language}`);
  setText(
    airboxCell,
    result.neighborhood_source
      ? `${result.neighborhood_source} / PM2.5 ${result.neighborhood_pm25 ?? "---"} / ${formatKm(result.neighborhood_distance_km)}`
      : "---",
  );
  setText(
    regionalCell,
    result.regional_source
      ? `${result.regional_source} / AQI ${result.regional_aqi ?? "---"} / PM2.5 ${result.regional_pm25 ?? "---"} / ${formatKm(result.regional_distance_km)}`
      : "---",
  );
  setText(weatherCell, result.weather_source ? `${result.weather_source}${result.weather_station ? ` / ${result.weather_station}` : ""}` : "---");
  setText(
    windCell,
    result.wind_speed !== null && result.wind_speed !== undefined ? `${result.wind_speed} m/s ${result.wind_direction || ""}`.trim() : "---",
  );
  setText(heroAirbox, result.neighborhood_pm25 ?? "Live");
  setText(heroMoenv, result.regional_aqi ? `AQI ${result.regional_aqi}` : "AQI");
  setText(heroCwa, result.wind_direction || "Weather");
}

function formatSensorValue(value, unit = "") {
  if (value === null || value === undefined) return "---";
  return `${value}${unit}`;
}

function updateLiveSensor(result) {
  liveSensorLight?.classList.remove("error");
  setText(liveSensorStatus, `${result.message_source || "---"} / ${result.scenario || "---"}`);
  setText(livePm25, formatSensorValue(result.local_pm25, " ug/m3"));
  setText(livePm10, formatSensorValue(result.local_pm10, " ug/m3"));
  setText(liveTemperature, formatSensorValue(result.local_temperature, " C"));
  setText(liveHumidity, formatSensorValue(result.local_humidity, "%"));
}

function syncFormWithReport(result) {
  if (!form) return;
  const values = {
    device_id: result.device_id,
    pm25: result.local_pm25,
    pm10: result.local_pm10,
    temperature: result.local_temperature,
    humidity: result.local_humidity,
  };
  Object.entries(values).forEach(([name, value]) => {
    const field = form.elements[name];
    if (field && value !== null && value !== undefined) field.value = value;
  });
}

async function requestReport(payload) {
  const response = await fetch("/sensor/report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `HTTP ${response.status}`);
  }

  return response.json();
}

async function translateLatestReport() {
  if (!latestReport) return;
  setStatus(null, t("dialing"));
  if (messageBox) messageBox.dataset.empty = "false";
  setShimmer(messageBox, t("crunching"));
  const result = await requestReport(payloadFromReport(latestReport));
  latestReport = result;
  updateResult(result);
  updateLiveSensor(result);
  setStatus("ok", `${t("received")}${result.message_source}`);
}

async function pollLatestSensorReport() {
  try {
    const response = await fetch("/sensor/latest", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const latest = await response.json();
    if (!latest.has_report || !latest.report) {
      setText(liveSensorStatus, "Waiting for bridge...");
      return;
    }

    latestReport = latest.report;
    syncFormWithReport(latest.report);
    updateLiveSensor(latest.report);
    if (latest.report.language === selectedLanguage) {
      updateResult(latest.report);
      setStatus("ok", `Arduino live / ${latest.report.message_source}`);
    }
  } catch (error) {
    liveSensorLight?.classList.add("error");
    setText(liveSensorStatus, "Live update unavailable");
  }
}

async function submitReport() {
  setStatus(null, t("dialing"));
  if (messageBox) messageBox.dataset.empty = "false";
  setShimmer(messageBox, t("crunching"));

  const response = await fetch("/sensor/report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payloadFromForm()),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `HTTP ${response.status}`);
  }

  const result = await response.json();
  latestReport = result;
  updateResult(result);
  updateLiveSensor(result);
  setStatus("ok", `${t("received")}${result.message_source}`);
}

form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await submitReport();
  } catch (error) {
    setStatus("error", t("failed"));
    if (messageBox) messageBox.dataset.empty = "false";
    setText(messageBox, `SYSTEM ERROR: ${error.message}`);
    [scenarioCell, confidenceCell, sourceCell, airboxCell, regionalCell, weatherCell, windCell].forEach((cell) => setText(cell, "---"));
  }
});

document.querySelectorAll("[data-preset]").forEach((button) => {
  button.addEventListener("click", () => {
    const preset = presets[button.dataset.preset];
    Object.entries(preset).forEach(([name, value]) => {
      const field = form?.elements[name];
      if (field) field.value = value;
    });
    setStatus(null, `${button.textContent} preset loaded.`);
  });
});

languageSelect?.addEventListener("change", async () => {
  applyLanguage(languageSelect.value);
  try {
    await translateLatestReport();
  } catch (error) {
    setStatus("error", t("failed"));
    setText(messageBox, `SYSTEM ERROR: ${error.message}`);
  }
});

if (messageBox) messageBox.dataset.empty = "true";
if (connectionText) connectionText.dataset.state = "waiting";
applyLanguage(selectedLanguage);
pollLatestSensorReport();
window.setInterval(pollLatestSensorReport, LATEST_SENSOR_POLL_MS);
