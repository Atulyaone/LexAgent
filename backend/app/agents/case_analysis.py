from google import genai
from google.genai import types
from app.config import settings
from app.schemas.context import AgentContext, AnalysisOutput
from app.schemas.firac import FiracBrief
from app.services.firac_generator import GeminiAPIError, GeminiConfigurationError


SYSTEM_INSTRUCTION = """You are an expert Indian legal case analyst for law students.
Your task is to read and synthesize the provided pre-analyzed legal Research Package (including legal domain, parties, bench, procedural history, statutory references, precedents, issues, holdings, and key verbatim passages) to produce a structured FIRAC brief.

Rules:
- Base every statement ONLY on the provided Research Package.
- Do not invent case names, citations, statutory sections, or facts.
- Do not access any external text. Use the provided verbatim key passages to extract concrete factual details and apply legal reasoning.
- Use precise Indian legal terminology.

Output must be valid JSON matching the required schema.
"""


class CaseAnalysisAgent:
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

    async def run(self, context: AgentContext, model_name: str) -> None:
        context.execution_state.current_agent = "CaseAnalysisAgent"
        
        research = context.research_output
        
        parties_str = ", ".join(research.parties)
        bench_str = ", ".join(research.bench)
        issues_str = "\n".join(f"- {issue}" for issue in research.key_legal_issues)
        holdings_str = "\n".join(f"- {holding}" for holding in research.important_holdings)
        
        statutes_str = "\n".join(
            f"- {s.act}, {s.section}: {s.context}" for s in research.statutes
        )
        precedents_str = "\n".join(
            f"- {p.case_name} ({p.citation or 'No citation'}): {p.relevance}" for p in research.precedents
        )
        
        passages_str = "\n".join(
            f"Passage (Page {p.page_reference or 'N/A'}):\n"
            f"Quote: \"{p.text}\"\n"
            f"Legal Issue Supported: {p.legal_issue_supported}\n"
            f"Selection Reason: {p.reason_for_selection}\n"
            for p in research.key_passages
        )
        
        prompt = (
            f"Synthesize the pre-analyzed Research Package to produce a structured FIRAC brief.\n\n"
            f"RESEARCH PACKAGE DETAILS:\n"
            f"- Legal Domain: {research.legal_domain or 'N/A'}\n"
            f"- Parties: {parties_str or 'N/A'}\n"
            f"- Bench: {bench_str or 'N/A'}\n"
            f"- Procedural History: {research.procedural_history or 'N/A'}\n\n"
            f"- Core Legal Issues:\n{issues_str or 'N/A'}\n\n"
            f"- Important Holdings / Findings:\n{holdings_str or 'N/A'}\n\n"
            f"- Relevant Statutory Provisions:\n{statutes_str or 'N/A'}\n\n"
            f"- Cited Precedents / Case Laws:\n{precedents_str or 'N/A'}\n\n"
            f"- Key Verbatim Passages from Judgment:\n{passages_str or 'N/A'}\n"
        )
        
        try:
            response = self.client.models.generate_content(
                model=model_name or settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_json_schema=FiracBrief.model_json_schema(),
                    temperature=0.2,
                ),
            )
        except GeminiConfigurationError:
            raise
        except Exception as exc:
            raise GeminiAPIError(f"Gemini API request failed in CaseAnalysisAgent: {exc}") from exc
        
        if not response.text:
            raise ValueError("Case Analysis Agent returned an empty response")
            
        brief = FiracBrief.model_validate_json(response.text)
        context.analysis_output = AnalysisOutput(firac_brief=brief)
        
        # Capture token usage
        if response.usage_metadata:
            context.metadata["analysis_prompt_tokens"] = response.usage_metadata.prompt_token_count
            context.metadata["analysis_completion_tokens"] = response.usage_metadata.candidates_token_count
            context.metadata["analysis_total_tokens"] = response.usage_metadata.total_token_count


case_analysis_agent = CaseAnalysisAgent()
