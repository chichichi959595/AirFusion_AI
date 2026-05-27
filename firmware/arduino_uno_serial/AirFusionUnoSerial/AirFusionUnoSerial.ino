#include <SoftwareSerial.h>

// Arduino Uno wiring:
// PMS5003T VCC -> 5V
// PMS5003T GND -> GND
// PMS5003T TX  -> Uno D10
// PMS5003T RX  -> leave disconnected for read-only use
static const int PMS_RX_PIN = 10;
static const int PMS_TX_PIN = 11;
static const unsigned long REPORT_INTERVAL_MS = 60000;
static const unsigned long STATUS_INTERVAL_MS = 5000;
static const unsigned long DEBUG_INTERVAL_MS = 5000;

SoftwareSerial pmsSerial(PMS_RX_PIN, PMS_TX_PIN);
unsigned long lastReportAt = REPORT_INTERVAL_MS;
unsigned long lastStatusAt = 0;
unsigned long lastDebugAt = 0;
unsigned int badHeaderCount = 0;
unsigned int shortFrameCount = 0;
unsigned int checksumFailCount = 0;

struct PmsReading {
  bool ok;
  unsigned int pm25;
  unsigned int pm10;
  float temperature;
  float humidity;
};

unsigned int wordAt(const byte *frame, int index) {
  return (static_cast<unsigned int>(frame[index]) << 8) | frame[index + 1];
}

bool readPmsFrame(byte *frame) {
  while (pmsSerial.available() >= 32) {
    if (pmsSerial.read() != 0x42) {
      badHeaderCount++;
      continue;
    }
    if (pmsSerial.peek() != 0x4D) {
      badHeaderCount++;
      continue;
    }

    frame[0] = 0x42;
    frame[1] = pmsSerial.read();
    size_t readCount = pmsSerial.readBytes(frame + 2, 30);
    if (readCount != 30) {
      shortFrameCount++;
      return false;
    }

    unsigned int checksum = 0;
    for (int i = 0; i < 30; i++) {
      checksum += frame[i];
    }
    if (checksum != wordAt(frame, 30)) {
      checksumFailCount++;
      return false;
    }
    return true;
  }
  return false;
}

PmsReading readPms5003t() {
  byte frame[32];
  if (!readPmsFrame(frame)) {
    return {false, 0, 0, 0.0, 0.0};
  }

  return {
    true,
    wordAt(frame, 12),
    wordAt(frame, 14),
    wordAt(frame, 24) / 10.0,
    wordAt(frame, 26) / 10.0,
  };
}

void printJsonReport(const PmsReading &reading) {
  Serial.print("{\"device_id\":\"arduino-uno-sensor01\",");
  Serial.print("\"pm25\":");
  Serial.print(reading.pm25);
  Serial.print(",\"pm10\":");
  Serial.print(reading.pm10);
  Serial.print(",\"temperature\":");
  Serial.print(reading.temperature, 1);
  Serial.print(",\"humidity\":");
  Serial.print(reading.humidity, 1);
  Serial.println("}");
}

void setup() {
  Serial.begin(115200);
  pmsSerial.begin(9600);
  pmsSerial.setTimeout(1200);
  delay(1200);
  Serial.println("{\"status\":\"uno_ready\"}");
}

void loop() {
  PmsReading reading = readPms5003t();
  if (reading.ok && millis() - lastReportAt >= REPORT_INTERVAL_MS) {
    printJsonReport(reading);
    lastReportAt = millis();
    lastStatusAt = millis();
  }

  if (!reading.ok && millis() - lastStatusAt >= STATUS_INTERVAL_MS) {
    Serial.println("{\"status\":\"waiting_for_pms5003t\"}");
    lastStatusAt = millis();
  }

  if (millis() - lastDebugAt >= DEBUG_INTERVAL_MS) {
    Serial.print("{\"debug\":\"pms_serial\",");
    Serial.print("\"available\":");
    Serial.print(pmsSerial.available());
    Serial.print(",\"bad_header\":");
    Serial.print(badHeaderCount);
    Serial.print(",\"short_frame\":");
    Serial.print(shortFrameCount);
    Serial.print(",\"checksum_fail\":");
    Serial.print(checksumFailCount);
    Serial.println("}");
    lastDebugAt = millis();
  }

  delay(200);
}
