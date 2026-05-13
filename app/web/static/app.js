const form = document.querySelector("#sensor-form");
const languageSelect = document.querySelector("#language-select");
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
const heroAirbox = document.querySelector("#hero-airbox");
const heroMoenv = document.querySelector("#hero-moenv");
const heroCwa = document.querySelector("#hero-cwa");

let selectedLanguage = "zh-Hant";

const languageLabels = {
  "zh-Hant": "繁中",
  en: "English",
  ko: "한국어",
  th: "ไทย",
  vi: "Tiếng Việt",
};

const translations = {
  "zh-Hant": {
    liveFusion: "即時融合已上線",
    eyebrow: "企業級空氣智慧",
    headlinePlain: "可信任的空氣品質建議，",
    headlineGradient: "不再被雜訊淹沒。",
    heroCopy: "輸入本地感測數值，AirFusion 會自動結合 AirBox、CWA、MOENV 與 OpenAI 建議。",
    languageLabel: "輸出語言",
    formKicker: "本地輸入",
    formTitle: "感測器回報",
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
    outputKicker: "AI 顧問",
    outputTitle: "使用者訊息",
    waiting: "等待報告...",
    placeholder: "按下送出報告，產生給使用者看的空氣品質建議。",
    scenario: "情境",
    confidence: "信心",
    source: "來源",
    officialAqi: "官方 AQI",
    weather: "氣象",
    wind: "風",
    dialing: "正在連線到 /sensor/report...",
    crunching: "AirFusion AI 正在融合感測與外部資料...",
    received: "已收到報告。訊息來源：",
    failed: "報告失敗。",
  },
  en: {
    liveFusion: "Live fusion online",
    eyebrow: "Enterprise air intelligence",
    headlinePlain: "Trusted air quality guidance,",
    headlineGradient: "without visual noise.",
    heroCopy: "Enter local sensor readings; AirFusion automatically combines live AirBox, CWA, MOENV, and OpenAI advice.",
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
    crunching: "AirFusion AI is fusing sensor and external data...",
    received: "Report received. Message source: ",
    failed: "Report failed.",
  },
  ko: {
    liveFusion: "실시간 융합 온라인",
    eyebrow: "엔터프라이즈 공기 인텔리전스",
    headlinePlain: "신뢰할 수 있는 공기질 안내,",
    headlineGradient: "불필요한 정보 없이.",
    heroCopy: "로컬 센서 값을 입력하면 AirFusion이 AirBox, CWA, MOENV, OpenAI 조언을 자동으로 결합합니다.",
    languageLabel: "출력 언어",
    formKicker: "로컬 입력",
    formTitle: "센서 보고",
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
    outputKicker: "AI 자문",
    outputTitle: "사용자 메시지",
    waiting: "보고 대기 중...",
    placeholder: "보고 전송을 눌러 사용자용 공기질 조언을 생성하세요.",
    scenario: "상황",
    confidence: "신뢰도",
    source: "출처",
    officialAqi: "공식 AQI",
    weather: "기상",
    wind: "바람",
    dialing: "/sensor/report에 연결 중...",
    crunching: "AirFusion AI가 센서와 외부 데이터를 융합 중입니다...",
    received: "보고 수신 완료. 메시지 출처: ",
    failed: "보고 실패.",
  },
  th: {
    liveFusion: "ระบบรวมข้อมูลสดพร้อมใช้งาน",
    eyebrow: "ระบบวิเคราะห์อากาศระดับองค์กร",
    headlinePlain: "คำแนะนำคุณภาพอากาศที่เชื่อถือได้",
    headlineGradient: "ไม่มีข้อมูลรบกวนสายตา",
    heroCopy: "ป้อนค่าจากเซนเซอร์ แล้ว AirFusion จะรวม AirBox, CWA, MOENV และคำแนะนำจาก OpenAI ให้โดยอัตโนมัติ",
    languageLabel: "ภาษาเอาต์พุต",
    formKicker: "ข้อมูลท้องถิ่น",
    formTitle: "รายงานเซนเซอร์",
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
    outputKicker: "ที่ปรึกษา AI",
    outputTitle: "ข้อความผู้ใช้",
    waiting: "รอรายงาน...",
    placeholder: "กดส่งรายงานเพื่อสร้างคำแนะนำคุณภาพอากาศสำหรับผู้ใช้",
    scenario: "สถานการณ์",
    confidence: "ความมั่นใจ",
    source: "แหล่งที่มา",
    officialAqi: "AQI ทางการ",
    weather: "อากาศ",
    wind: "ลม",
    dialing: "กำลังติดต่อ /sensor/report...",
    crunching: "AirFusion AI กำลังรวมข้อมูลเซนเซอร์และแหล่งภายนอก...",
    received: "ได้รับรายงานแล้ว แหล่งข้อความ: ",
    failed: "ส่งรายงานไม่สำเร็จ",
  },
  vi: {
    liveFusion: "Hợp nhất dữ liệu trực tiếp",
    eyebrow: "Trí tuệ không khí cho doanh nghiệp",
    headlinePlain: "Khuyến nghị chất lượng không khí đáng tin cậy,",
    headlineGradient: "không nhiễu thị giác.",
    heroCopy: "Nhập chỉ số cảm biến; AirFusion tự động kết hợp AirBox, CWA, MOENV và tư vấn OpenAI.",
    languageLabel: "Ngôn ngữ đầu ra",
    formKicker: "Dữ liệu cục bộ",
    formTitle: "Báo cáo cảm biến",
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
    outputKicker: "Cố vấn AI",
    outputTitle: "Thông điệp người dùng",
    waiting: "Đang chờ báo cáo...",
    placeholder: "Nhấn gửi báo cáo để tạo khuyến nghị chất lượng không khí.",
    scenario: "Kịch bản",
    confidence: "Độ tin cậy",
    source: "Nguồn",
    officialAqi: "AQI chính thức",
    weather: "Thời tiết",
    wind: "Gió",
    dialing: "Đang gọi /sensor/report...",
    crunching: "AirFusion AI đang hợp nhất dữ liệu cảm biến và nguồn ngoài...",
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
  connectionLight.classList.remove("error");
  if (kind === "error") connectionLight.classList.add("error");
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
  heroAirbox.textContent = result.neighborhood_pm25 ?? "Live";
  heroMoenv.textContent = result.regional_aqi ? `AQI ${result.regional_aqi}` : "AQI";
  heroCwa.textContent = result.wind_direction || "Weather";
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

languageSelect.addEventListener("change", () => {
  applyLanguage(languageSelect.value);
});

messageBox.dataset.empty = "true";
connectionText.dataset.state = "waiting";
applyLanguage(selectedLanguage);
