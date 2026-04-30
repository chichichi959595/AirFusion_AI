from __future__ import annotations

from app.core.geo import Location
from app.core.thresholds import band_for_aqi, estimate_aqi_from_pm25
from app.domain import AirReading, FusionResult, WeatherReading


class FusionService:
    indoor_delta = 15.0
    hotspot_delta = 12.0
    high_pm25 = 35.0

    def analyze(
        self,
        *,
        location: Location,
        local: AirReading,
        neighborhood: AirReading | None = None,
        regional: AirReading | None = None,
        weather: WeatherReading | None = None,
    ) -> FusionResult:
        scenario, confidence, reasoning = self._classify(local, neighborhood, regional, weather)
        risk_aqi = regional.aqi if regional and regional.aqi is not None else estimate_aqi_from_pm25(local.pm25)
        risk = band_for_aqi(risk_aqi)
        summary = self._summary(scenario, local, neighborhood, regional)
        recommendations = self._recommendations(scenario, risk.name, weather)

        return FusionResult(
            location=location,
            local=local,
            neighborhood=neighborhood,
            regional=regional,
            weather=weather,
            scenario=scenario,
            confidence=confidence,
            risk_aqi=risk_aqi,
            risk_band=risk.name,
            summary=summary,
            recommendations=recommendations,
            reasoning=reasoning,
        )

    def _classify(
        self,
        local: AirReading,
        neighborhood: AirReading | None,
        regional: AirReading | None,
        weather: WeatherReading | None,
    ) -> tuple[str, float, list[str]]:
        local_pm25 = local.pm25
        neighborhood_pm25 = neighborhood.pm25 if neighborhood else None
        regional_pm25 = regional.pm25 if regional else None
        outdoor_values = [v for v in (neighborhood_pm25, regional_pm25) if v is not None]

        reasoning: list[str] = []
        if local_pm25 is None:
            return "insufficient_local_data", 0.2, ["Local PM2.5 is missing."]

        if outdoor_values:
            outdoor_baseline = max(outdoor_values)
            reasoning.append(f"Local PM2.5 is {local_pm25}; outdoor baseline is {outdoor_baseline}.")
            if local_pm25 - outdoor_baseline >= self.indoor_delta:
                return "indoor_source", 0.86, reasoning + [
                    "Local PM2.5 is much higher than nearby outdoor data."
                ]

        if (
            neighborhood_pm25 is not None
            and regional_pm25 is not None
            and local_pm25 >= self.high_pm25
            and neighborhood_pm25 >= self.high_pm25
            and neighborhood_pm25 - regional_pm25 >= self.hotspot_delta
        ):
            return "neighborhood_hotspot", 0.82, reasoning + [
                "Local and neighborhood readings are elevated while official station remains lower."
            ]

        if (
            regional_pm25 is not None
            and local_pm25 >= self.high_pm25
            and regional_pm25 >= self.high_pm25
            and (neighborhood_pm25 is None or neighborhood_pm25 >= self.high_pm25)
        ):
            return "regional_pollution", 0.78, reasoning + [
                "All available scales show elevated PM2.5."
            ]

        if regional and regional.aqi and regional.aqi >= 101:
            note = "Official AQI is unhealthy for sensitive groups or worse."
            if weather and weather.wind_speed and weather.wind_speed >= 5:
                note += " Wind may transport pollution quickly."
            return "official_alert", 0.72, reasoning + [note]

        return "normal", 0.68, reasoning + ["No strong cross-scale anomaly is detected."]

    def _summary(
        self,
        scenario: str,
        local: AirReading,
        neighborhood: AirReading | None,
        regional: AirReading | None,
    ) -> str:
        labels = {
            "indoor_source": "室內 PM2.5 明顯高於室外背景，較像室內污染源或通風不足。",
            "neighborhood_hotspot": "局部與社區數值同步偏高，較像附近施工、焚燒或街區污染事件。",
            "regional_pollution": "三個尺度皆偏高，較像大範圍污染或氣象擴散條件不佳。",
            "official_alert": "官方 AQI 已達警示等級，需以健康防護為優先。",
            "normal": "目前未偵測到明顯跨尺度異常。",
            "insufficient_local_data": "缺少局部感測資料，暫時無法完成個人暴露判斷。",
        }
        values = [f"Local {local.pm25}"]
        if neighborhood:
            values.append(f"Neighborhood {neighborhood.pm25}")
        if regional:
            values.append(f"Regional {regional.pm25}/AQI {regional.aqi}")
        return f"{labels.get(scenario, labels['normal'])} ({', '.join(values)})"

    def _recommendations(
        self,
        scenario: str,
        risk_band: str,
        weather: WeatherReading | None,
    ) -> list[str]:
        if scenario == "indoor_source":
            items = [
                "短暫開窗或開啟排風設備，快速排出室內污染源。",
                "找出室內來源，例如烹飪、焚香、吸菸、清潔劑或列印設備。",
                "數值下降後關窗並開啟 HEPA 空氣清淨機。",
            ]
        elif scenario == "neighborhood_hotspot":
            items = [
                "先關閉面向污染源的窗戶，避免街區污染進入室內。",
                "觀察 AirBox 或附近站點是否在 30 到 60 分鐘內回落。",
                "外出時減少高強度活動，敏感族群可配戴 N95 等級口罩。",
            ]
        elif scenario in {"regional_pollution", "official_alert"}:
            items = [
                "關閉門窗並啟動 HEPA 空氣清淨機。",
                "延後戶外運動，敏感族群避免長時間外出。",
                "持續追蹤官方 AQI 與未來幾小時風向變化。",
            ]
        else:
            items = [
                "維持一般通風與日常活動。",
                "保留局部感測器趨勢，以便偵測突發污染。",
            ]

        if risk_band in {"unhealthy", "very_unhealthy"}:
            items.append("若出現咳嗽、喘鳴或胸悶，請降低活動量並考慮就醫諮詢。")
        if weather and weather.rain_probability and weather.rain_probability >= 70:
            items.append("預期降雨可能協助沉降懸浮微粒，可在雨後重新評估通風。")
        return items
