from google import genai
from google.genai import types
from pydantic import ValidationError

from app.config import settings
from app.schemas.firac import FiracBrief


class GeminiConfigurationError(Exception):
    """Raised when Gemini is not configured."""


class FiracGenerationError(Exception):
    """Raised when FIRAC generation fails after retries."""


class GeminiAPIError(Exception):
    """Raised when the Gemini API returns an upstream error."""


SYSTEM_INSTRUCTION = """You are an expert Indian legal case analyst for law students.

Your task is to read a judgment and produce a structured FIRAC brief.

Rules:
- Base every statement only on the provided judgment text.
- Do not invent case names, citations, statutory sections, or facts.
- Use precise Indian legal terminology.
- Write clearly for law students preparing FIRAC case briefs.
- If information for a section is unclear in the source, state what is known without speculation.

Output must be valid JSON matching the required schema with these fields:
- facts: concise factual narrative
- issues: legal questions the court answered
- rule: applicable statutes, articles, and precedents cited in the judgment
- analysis: how the court applied the rule to the facts
- conclusion: final holding and disposition
"""


class FiracGenerator:
    def __init__(self) -> None:
        self._client: genai.Client | None = None

    @property
    def client(self) -> genai.Client:
        if not settings.gemini_api_key:
            raise GeminiConfigurationError(
                "GEMINI_API_KEY is not set. Add it to backend/.env before running analysis."
            )
        if self._client is None:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client

    def generate_firac(
        self,
        *,
        filename: str,
        page_count: int,
        judgment_text: str,
    ) -> FiracBrief:
        user_prompt = (
            f"Analyze the following Indian court judgment and produce a FIRAC brief.\n\n"
            f"Document metadata:\n"
            f"- filename: {filename}\n"
            f"- page_count: {page_count}\n\n"
            f"Judgment text:\n{judgment_text}"
        )

        last_error: Exception | None = None
        repair_prompt = user_prompt

        for attempt in range(settings.gemini_max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=settings.gemini_model,
                    contents=repair_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        response_mime_type="application/json",
                        response_json_schema=FiracBrief.model_json_schema(),
                        temperature=0.2,
                    ),
                )

                if not response.text:
                    raise FiracGenerationError("Gemini returned an empty response")

                return FiracBrief.model_validate_json(response.text)
            except (ValidationError, FiracGenerationError) as exc:
                last_error = exc
                if attempt >= settings.gemini_max_retries:
                    break
                repair_prompt = (
                    f"{user_prompt}\n\n"
                    "Your previous response was invalid. "
                    f"Validation error: {exc}. "
                    "Return only valid JSON matching the FIRAC schema."
                )
            except GeminiConfigurationError:
                raise
            except Exception as exc:
                raise GeminiAPIError(f"Gemini API request failed: {exc}") from exc

        raise FiracGenerationError(
            f"Failed to generate valid FIRAC output after retries: {last_error}"
        )


firac_generator = FiracGenerator()
