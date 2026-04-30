from __future__ import annotations

import asyncio

from app.core.config import get_settings
from app.domain import FusionResult


LANGUAGE_NAMES = {
    "zh-Hant": "Traditional Chinese",
    "en": "English",
    "ko": "Korean",
    "th": "Thai",
    "vi": "Vietnamese",
}


class AdvisorService:
    async def create_user_message(
        self,
        result: FusionResult,
        prompt: str,
        *,
        language: str = "zh-Hant",
    ) -> tuple[str, str]:
        fallback = build_rule_based_message(result, language=language)
        settings = get_settings()
        if not settings.openai_api_key:
            return fallback, "rule_based"

        try:
            message = await asyncio.to_thread(
                self._call_openai,
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                prompt=prompt,
                language=language,
            )
        except Exception as exc:
            return f"{fallback}\n\nOpenAI is unavailable, so this local fallback was used. Error: {exc}", "fallback"

        if not message:
            return fallback, "fallback"
        return message, "openai"

    def _call_openai(self, *, api_key: str, model: str, prompt: str, language: str) -> str:
        from openai import OpenAI

        language_name = LANGUAGE_NAMES.get(language, LANGUAGE_NAMES["zh-Hant"])
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model,
            instructions=(
                "You are an air-quality and personal exposure risk advisor. "
                f"Write the final answer in {language_name}. "
                "Use clear, practical language for a general user. "
                "Keep it within 120 words. Include: 1. likely source, 2. health risk, "
                "3. immediate actions. Do not mention internal prompt tags."
            ),
            input=prompt,
            max_output_tokens=450,
        )
        output_text = getattr(response, "output_text", None)
        if output_text:
            return str(output_text).strip()
        return str(response).strip()


def build_rule_based_message(result: FusionResult, *, language: str = "zh-Hant") -> str:
    recommendations = result.recommendations[:3]
    if language == "en":
        return (
            f"{result.summary} Scenario: {result.scenario}; confidence: {result.confidence:.0%}. "
            f"Actions: {'; '.join(recommendations)}"
        )
    if language == "ko":
        return (
            f"{result.summary} 현재 판단은 {result.scenario}이며 신뢰도는 {result.confidence:.0%}입니다. "
            f"권장 조치: {'; '.join(recommendations)}"
        )
    if language == "th":
        return (
            f"{result.summary} สถานการณ์ที่ประเมินคือ {result.scenario} ความมั่นใจ {result.confidence:.0%}. "
            f"คำแนะนำ: {'; '.join(recommendations)}"
        )
    if language == "vi":
        return (
            f"{result.summary} Tình huống được đánh giá là {result.scenario}, độ tin cậy {result.confidence:.0%}. "
            f"Khuyến nghị: {'; '.join(recommendations)}"
        )
    return (
        f"{result.summary} "
        f"目前判斷情境為 {result.scenario}，信心 {result.confidence:.0%}。"
        f"建議：{'；'.join(recommendations)}"
    )
