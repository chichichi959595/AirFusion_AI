const form = document.querySelector("#sensor-form");
const messageBox = document.querySelector("#user-message");
const scenarioCell = document.querySelector("#scenario-cell");
const confidenceCell = document.querySelector("#confidence-cell");
const sourceCell = document.querySelector("#source-cell");
const airboxCell = document.querySelector("#airbox-cell");
const regionalCell = document.querySelector("#regional-cell");
const weatherCell = document.querySelector("#weather-cell");
const windCell = document.querySelector("#wind-cell");
const connectionLight = document.querySelector("#connection-light");
const connectionText = document.querySelector("#connection-text");
const counterLanguage = document.querySelector("#counter-language");

let selectedLanguage = "zh-Hant";

const languageLabels = {
  "zh-Hant": "ZH-HANT",
  en: "ENGLISH",
  ko: "KOREAN",
  th: "THAI",
  vi: "VIETNAMESE",
};

const translations = {
  "zh-Hant": {
    eyebrow: "Windows 95 環境控制中心",
    heroCopy: "本地感測資料結合 AirBox、CWA 氣象、MOENV AQI 與 OpenAI 建議。",
    languageLabel: "輸出語言",
    localTile: "表單模擬感測器",
    airboxTile: "最近 AirBox 即時站",
    cwaTile: "氣象局即時觀測",
    moenvTile: "環境部官方 AQI",
    formTitle: "本地感測器回報",
    deviceId: "裝置 ID",
    locationLabel: "位置名稱",
    latitude: "緯度",
    longitude: "經度",
    temperature: "溫度",
    humidity: "濕度",
    liveNote: "AirBox、CWA 氣象、MOENV AQI 都是即時資料。此表單只模擬本地感測器。",
    sendReport: "送出報告",
    indoorPreset: "室內來源",
    hotspotPreset: "高 PM2.5",
    reset: "重設",
    outputTitle: "使用者訊息輸出",
    waiting: "等待報告...",
    placeholder: "按下 SEND REPORT 產生給使用者看的空氣品質建議。",
    scenario: "情境",
    confidence: "信心",
    source: "來源",
    officialAqi: "官方 AQI",
    weather: "氣象",
    wind: "風",
    fusionTitle: "融合層",
    localLayer: "目前表單模擬，之後接 Arduino",
    airboxLayer: "AirBox 即時站",
    regionalLayer: "MOENV AQI + CWA 氣象",
    outputLayer: "OpenAI 多語建議",
    languageTitle: "語言切換板",
    languageNote: "先選語言再送出報告。介面會立即切換，OpenAI 會用該語言回覆。",
    constructionTitle: "真系統，復古外皮",
    constructionCopy: "AirBox、CWA、MOENV、OpenAI 已串接。之後 Arduino 只要 POST 到 /sensor/report。",
    openDocs: "開啟 API 文件",
    dialing: "正在撥號到 /sensor/report...",
    crunching: "AirFusion AI 正在計算感測與外部資料...",
    received: "已收到報告。訊息來源：",
    failed: "報告失敗。",
  },
  en: {
    eyebrow: "Windows 95 Environmental Command Center",
    heroCopy: "Local sensor data meets live AirBox, CWA weather, MOENV AQI, and OpenAI guidance.",
    languageLabel: "Output language",
    localTile: "Form sensor simulation",
    airboxTile: "Live nearest AirBox",
    cwaTile: "Live CWA weather",
    moenvTile: "Live MOENV AQI",
    formTitle: "Local Sensor Report",
    deviceId: "Device ID",
    locationLabel: "Location Label",
    latitude: "Latitude",
    longitude: "Longitude",
    temperature: "Temperature",
    humidity: "Humidity",
    liveNote: "AirBox, CWA weather, and MOENV AQI are live. This form only simulates the local sensor.",
    sendReport: "Send Report",
    indoorPreset: "Indoor Source",
    hotspotPreset: "High PM2.5",
    reset: "Reset",
    outputTitle: "User Message Output",
    waiting: "Waiting for report...",
    placeholder: "Press SEND REPORT to generate the user-facing air quality message.",
    scenario: "Scenario",
    confidence: "Confidence",
    source: "Source",
    officialAqi: "Official AQI",
    weather: "Weather",
    wind: "Wind",
    fusionTitle: "Fusion Layers",
    localLayer: "Sensor simulation now, Arduino later",
    airboxLayer: "Live AirBox station",
    regionalLayer: "MOENV AQI + CWA weather",
    outputLayer: "OpenAI multilingual advice",
    languageTitle: "Language Switch Board",
    languageNote: "Choose a language, then send a report. The UI changes instantly; OpenAI replies in that language.",
    constructionTitle: "Live System, Retro Skin",
    constructionCopy: "AirBox, CWA, MOENV, and OpenAI are live. Connect Arduino later by posting to /sensor/report.",
    openDocs: "Open API Docs",
    dialing: "Dialing /sensor/report...",
    crunching: "AirFusion AI is crunching sensor and external data...",
    received: "Report received. Message source: ",
    failed: "Report failed.",
  },
  ko: {
    eyebrow: "Windows 95 환경 제어 센터",
    heroCopy: "로컬 센서 데이터에 AirBox, CWA 기상, MOENV AQI, OpenAI 조언을 결합합니다.",
    languageLabel: "출력 언어",
    localTile: "센서 폼 시뮬레이션",
    airboxTile: "가장 가까운 AirBox",
    cwaTile: "CWA 실시간 기상",
    moenvTile: "MOENV 공식 AQI",
    formTitle: "로컬 센서 보고",
    deviceId: "장치 ID",
    locationLabel: "위치 이름",
    latitude: "위도",
    longitude: "경도",
    temperature: "온도",
    humidity: "습도",
    liveNote: "AirBox, CWA 기상, MOENV AQI는 실시간입니다. 이 폼은 로컬 센서만 시뮬레이션합니다.",
    sendReport: "보고 전송",
    indoorPreset: "실내 오염원",
    hotspotPreset: "높은 PM2.5",
    reset: "초기화",
    outputTitle: "사용자 메시지 출력",
    waiting: "보고 대기 중...",
    placeholder: "SEND REPORT를 눌러 사용자용 공기질 조언을 생성하세요.",
    scenario: "상황",
    confidence: "신뢰도",
    source: "출처",
    officialAqi: "공식 AQI",
    weather: "기상",
    wind: "바람",
    fusionTitle: "융합 레이어",
    localLayer: "현재는 폼 시뮬레이션, 이후 Arduino 연결",
    airboxLayer: "실시간 AirBox 관측소",
    regionalLayer: "MOENV AQI + CWA 기상",
    outputLayer: "OpenAI 다국어 조언",
    languageTitle: "언어 전환 보드",
    languageNote: "언어를 선택한 뒤 보고를 전송하세요. UI는 즉시 바뀌고 OpenAI도 해당 언어로 답합니다.",
    constructionTitle: "실시간 시스템, 복고 스킨",
    constructionCopy: "AirBox, CWA, MOENV, OpenAI가 연결되어 있습니다. Arduino는 나중에 /sensor/report로 POST하면 됩니다.",
    openDocs: "API 문서 열기",
    dialing: "/sensor/report에 연결 중...",
    crunching: "AirFusion AI가 센서와 외부 데이터를 계산 중입니다...",
    received: "보고 수신 완료. 메시지 출처: ",
    failed: "보고 실패.",
  },
  th: {
    eyebrow: "ศูนย์ควบคุมสิ่งแวดล้อม Windows 95",
    heroCopy: "รวมข้อมูลเซนเซอร์กับ AirBox, CWA, MOENV AQI และคำแนะนำจาก OpenAI",
    languageLabel: "ภาษาเอาต์พุต",
    localTile: "จำลองเซนเซอร์จากฟอร์ม",
    airboxTile: "AirBox ใกล้สุดแบบสด",
    cwaTile: "สภาพอากาศ CWA สด",
    moenvTile: "AQI ทางการจาก MOENV",
    formTitle: "รายงานเซนเซอร์ท้องถิ่น",
    deviceId: "รหัสอุปกรณ์",
    locationLabel: "ชื่อสถานที่",
    latitude: "ละติจูด",
    longitude: "ลองจิจูด",
    temperature: "อุณหภูมิ",
    humidity: "ความชื้น",
    liveNote: "AirBox, CWA และ MOENV AQI เป็นข้อมูลสด ฟอร์มนี้จำลองเฉพาะเซนเซอร์ท้องถิ่น",
    sendReport: "ส่งรายงาน",
    indoorPreset: "แหล่งภายในอาคาร",
    hotspotPreset: "PM2.5 สูง",
    reset: "รีเซ็ต",
    outputTitle: "ข้อความสำหรับผู้ใช้",
    waiting: "รอรายงาน...",
    placeholder: "กด SEND REPORT เพื่อสร้างคำแนะนำคุณภาพอากาศสำหรับผู้ใช้",
    scenario: "สถานการณ์",
    confidence: "ความมั่นใจ",
    source: "แหล่งที่มา",
    officialAqi: "AQI ทางการ",
    weather: "อากาศ",
    wind: "ลม",
    fusionTitle: "ชั้นข้อมูล",
    localLayer: "ตอนนี้จำลองเซนเซอร์ ต่อไปเชื่อม Arduino",
    airboxLayer: "สถานี AirBox สด",
    regionalLayer: "MOENV AQI + CWA",
    outputLayer: "คำแนะนำหลายภาษาจาก OpenAI",
    languageTitle: "แผงเปลี่ยนภาษา",
    languageNote: "เลือกภาษาแล้วส่งรายงาน UI จะเปลี่ยนทันที และ OpenAI จะตอบเป็นภาษานั้น",
    constructionTitle: "ระบบสดในสไตล์ย้อนยุค",
    constructionCopy: "AirBox, CWA, MOENV และ OpenAI เชื่อมแล้ว Arduino ส่ง POST ไปที่ /sensor/report ได้ภายหลัง",
    openDocs: "เปิดเอกสาร API",
    dialing: "กำลังติดต่อ /sensor/report...",
    crunching: "AirFusion AI กำลังประมวลผลข้อมูลเซนเซอร์และภายนอก...",
    received: "ได้รับรายงานแล้ว แหล่งข้อความ: ",
    failed: "ส่งรายงานไม่สำเร็จ",
  },
  vi: {
    eyebrow: "Trung tâm môi trường Windows 95",
    heroCopy: "Dữ liệu cảm biến kết hợp AirBox, thời tiết CWA, AQI MOENV và tư vấn OpenAI.",
    languageLabel: "Ngôn ngữ đầu ra",
    localTile: "Mô phỏng cảm biến bằng biểu mẫu",
    airboxTile: "AirBox gần nhất trực tiếp",
    cwaTile: "Thời tiết CWA trực tiếp",
    moenvTile: "AQI chính thức MOENV",
    formTitle: "Báo cáo cảm biến cục bộ",
    deviceId: "ID thiết bị",
    locationLabel: "Tên vị trí",
    latitude: "Vĩ độ",
    longitude: "Kinh độ",
    temperature: "Nhiệt độ",
    humidity: "Độ ẩm",
    liveNote: "AirBox, thời tiết CWA và AQI MOENV là dữ liệu trực tiếp. Biểu mẫu này chỉ mô phỏng cảm biến cục bộ.",
    sendReport: "Gửi báo cáo",
    indoorPreset: "Nguồn trong nhà",
    hotspotPreset: "PM2.5 cao",
    reset: "Đặt lại",
    outputTitle: "Thông điệp cho người dùng",
    waiting: "Đang chờ báo cáo...",
    placeholder: "Nhấn SEND REPORT để tạo khuyến nghị chất lượng không khí.",
    scenario: "Kịch bản",
    confidence: "Độ tin cậy",
    source: "Nguồn",
    officialAqi: "AQI chính thức",
    weather: "Thời tiết",
    wind: "Gió",
    fusionTitle: "Các lớp hợp nhất",
    localLayer: "Hiện mô phỏng, sau này kết nối Arduino",
    airboxLayer: "Trạm AirBox trực tiếp",
    regionalLayer: "MOENV AQI + thời tiết CWA",
    outputLayer: "Tư vấn đa ngôn ngữ OpenAI",
    languageTitle: "Bảng đổi ngôn ngữ",
    languageNote: "Chọn ngôn ngữ rồi gửi báo cáo. UI đổi ngay; OpenAI trả lời bằng ngôn ngữ đó.",
    constructionTitle: "Hệ thống thật, giao diện hoài cổ",
    constructionCopy: "AirBox, CWA, MOENV và OpenAI đã hoạt động. Arduino sau này chỉ cần POST tới /sensor/report.",
    openDocs: "Mở tài liệu API",
    dialing: "Đang gọi /sensor/report...",
    crunching: "AirFusion AI đang xử lý dữ liệu cảm biến và nguồn ngoài...",
    received: "Đã nhận báo cáo. Nguồn thông điệp: ",
    failed: "Gửi báo cáo thất bại.",
  },
};

const presets = {
  indoor: { pm25: 45, pm10: 60, temperature: 27, humidity: 60 },
  hotspot: { pm25: 88, pm10: 120, temperature: 29, humidity: 72 },
};

function t(key) {
  return translations[selectedLanguage][key] || translations.en[key] || key;
}

function applyLanguage(language) {
  selectedLanguage = language;
  document.documentElement.lang = language;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll(".lang-btn").forEach((button) => {
    const active = button.dataset.language === language;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", active ? "true" : "false");
  });
  counterLanguage.textContent = languageLabels[language];
  if (messageBox.dataset.empty === "true") {
    messageBox.textContent = t("placeholder");
  }
  if (connectionText.dataset.state === "waiting") {
    connectionText.textContent = t("waiting");
  }
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

function setStatus(kind, text, state = "") {
  connectionLight.classList.remove("ok", "error");
  if (kind) connectionLight.classList.add(kind);
  connectionText.textContent = text;
  connectionText.dataset.state = state;
}

function formatKm(value) {
  return value === null || value === undefined ? "---" : `${value} km`;
}

function updateResult(result) {
  messageBox.dataset.empty = "false";
  messageBox.textContent = result.message || "No message returned.";
  scenarioCell.textContent = result.scenario || "---";
  confidenceCell.textContent =
    typeof result.confidence === "number" ? `${Math.round(result.confidence * 100)}%` : "---";
  sourceCell.textContent = `${result.message_source || "---"} / ${languageLabels[result.language] || result.language}`;
  airboxCell.textContent = result.neighborhood_source
    ? `${result.neighborhood_source} / PM2.5 ${result.neighborhood_pm25 ?? "---"} / ${formatKm(
        result.neighborhood_distance_km,
      )}`
    : "---";
  regionalCell.textContent = result.regional_source
    ? `${result.regional_source} / AQI ${result.regional_aqi ?? "---"} / PM2.5 ${
        result.regional_pm25 ?? "---"
      } / ${formatKm(result.regional_distance_km)}`
    : "---";
  weatherCell.textContent = result.weather_source
    ? `${result.weather_source}${result.weather_station ? ` / ${result.weather_station}` : ""}`
    : "---";
  windCell.textContent =
    result.wind_speed !== null && result.wind_speed !== undefined
      ? `${result.wind_speed} m/s ${result.wind_direction || ""}`.trim()
      : "---";
}

async function submitReport() {
  setStatus(null, t("dialing"));
  messageBox.dataset.empty = "false";
  messageBox.textContent = t("crunching");

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
  updateResult(result);
  setStatus("ok", `${t("received")}${result.message_source}`);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await submitReport();
  } catch (error) {
    setStatus("error", t("failed"));
    messageBox.dataset.empty = "false";
    messageBox.textContent = `SYSTEM ERROR: ${error.message}`;
    scenarioCell.textContent = "---";
    confidenceCell.textContent = "---";
    sourceCell.textContent = "---";
    airboxCell.textContent = "---";
    regionalCell.textContent = "---";
    weatherCell.textContent = "---";
    windCell.textContent = "---";
  }
});

document.querySelectorAll("[data-preset]").forEach((button) => {
  button.addEventListener("click", () => {
    const preset = presets[button.dataset.preset];
    Object.entries(preset).forEach(([name, value]) => {
      const field = form.elements[name];
      if (field) field.value = value;
    });
    setStatus(null, `${button.textContent} preset loaded.`);
  });
});

document.querySelectorAll(".lang-btn").forEach((button) => {
  button.addEventListener("click", () => {
    applyLanguage(button.dataset.language);
  });
});

messageBox.dataset.empty = "true";
connectionText.dataset.state = "waiting";
applyLanguage(selectedLanguage);
