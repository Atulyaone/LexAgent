from app.schemas.firac import FiracBrief
from app.services.firac_generator import FiracGenerator, firac_generator


class CaseAnalysisAgent:
    """Generates structured FIRAC briefs from judgment text via Gemini."""

    def __init__(self, generator: FiracGenerator | None = None) -> None:
        self._generator = generator or firac_generator

    def analyze(
        self,
        *,
        filename: str,
        page_count: int,
        judgment_text: str,
    ) -> FiracBrief:
        return self._generator.generate_firac(
            filename=filename,
            page_count=page_count,
            judgment_text=judgment_text,
        )


case_analysis_agent = CaseAnalysisAgent()
