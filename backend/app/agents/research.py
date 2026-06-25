import re
from typing import List, Dict, Any
from google import genai
from google.genai import types
from app.config import settings
from app.schemas.context import AgentContext, ResearchOutput, StatutoryReference, PrecedentReference, KeyPassage
from app.services.firac_generator import GeminiAPIError, GeminiConfigurationError

SYSTEM_INSTRUCTION = """You are an expert Indian legal research assistant.
Your task is to analyze the provided court judgment text along with candidate statutes and citations to produce a comprehensive, structured legal research package.

Your output must include ALL of the following:
1. **legal_domain**: Identify the primary legal domain (e.g., Constitutional Law, Contract Law, Criminal Law, Consumer Protection, Succession Law, Property Law, Administrative Law, Labour Law).
2. **parties**: List all parties identified in the judgment (petitioner, respondent, appellant, etc.) by their names.
3. **bench**: List all judges on the bench by name (e.g., "Justice Y.V. Chandrachud", "Justice P.N. Bhagwati").
4. **procedural_history**: Summarize the procedural history of the case if identifiable (e.g., which court heard it first, how it reached the current court).
5. **statutes**: Filter the pre-extracted candidate Acts, Sections, Articles, Rules, Orders, and Clauses. Ignore OCR noise, duplicates, and irrelevant provisions. For each relevant provision, explain its context in the judgment.
6. **precedents**: For each relevant landmark case or precedent cited in the judgment, provide the case name, citation (if available), and its relevance.
7. **key_legal_issues**: Identify the core legal issues or questions the court was called upon to decide.
8. **important_holdings**: State the important holdings or legal findings of the court.
9. **key_passages**: Extract at most 10 of the most legally significant passages VERBATIM from the judgment text. Each passage should be approximately 100-150 words. The total combined text across all passages must not exceed approximately 1,500 words. For each passage, you MUST specify:
   - `text`: the verbatim text of the passage.
   - `page_reference`: the page number or range if identifiable from the text.
   - `legal_issue_supported`: which key legal issue/question this passage directly addresses or supports.
   - `reason_for_selection`: why this passage was selected as legally significant.

CRITICAL CONSTRAINTS for key_passages:
- Extract passages VERBATIM (exact quotes from the judgment text).
- Maximum 10 passages.
- Each passage approximately 100-150 words maximum.
- Total combined quoted text must not exceed 1,500 words.
- Prioritize passages that contain the court's core reasoning, legal principles, and decisive holdings.

Output must be valid JSON matching the required schema.
"""


class ResearchAgent:
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

    def _deterministic_extract(self, text: str) -> Dict[str, List[str]]:
        """Extract generic legal structures: Acts/Codes, provisions, and citations using generalized regex."""
        # Detect capitalized words ending with Act, Code or Constitution (e.g. Indian Contract Act, Constitution of India)
        # Make preceding capitalized words optional to support standalone names like "Constitution of India"
        act_pattern = r"\b(?:[A-Z][A-Za-z0-9]*(?:\s+(?:of|and|for|the|in)?\s*[A-Z][A-Za-z0-9]*)*\s+)?(?:Act|Code|Constitution)(?:\s+of\s+India)?\b"
        acts = re.findall(act_pattern, text)
        
        # Detect Sections, Articles, Rules, Orders, Clauses, and their common abbreviations
        provision_pattern = r"\b(?:Section|Sec\.?|Article|Art\.?|Rule|Order|Clause|Cl\.?)\s+\d+(?:\s*[A-Za-z])?\b"
        provisions = re.findall(provision_pattern, text, re.IGNORECASE)
        
        # Detect standard Indian citation structures
        citation_patterns = [
            r"\bAIR\s+\d{4}\s+SC\s+\d+\b",
            r"\(\d{4}\)\s+\d+\s+SCC\s+\d+\b",
            r"\b\d{4}\s+SCC\s+OnLine\s+SC\s+\d+\b",
            r"\b\d{4}\s+\d+\s+SCR\s+\d+\b",
            r"\b\d{4}\s+\d+\s+SCALE\s+\d+\b",
            r"\b\d{4}\s+\d+\s+JT\s+\d+\b"
        ]
        citations = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citations.extend(matches)
            
        return {
            "acts": list(set(acts)),
            "provisions": list(set(provisions)),
            "citations": list(set(citations)),
        }

    async def run(self, context: AgentContext, model_name: str) -> None:
        context.execution_state.current_agent = "ResearchAgent"
        
        # 1. Deterministic extraction
        candidates = self._deterministic_extract(context.extracted_text)
        context.tool_results["deterministic_candidates"] = candidates
        
        candidates_str = (
            f"Candidate Acts/Codes: {', '.join(candidates['acts'])}\n"
            f"Candidate Provisions (Sections/Articles/Rules/Orders/Clauses): {', '.join(candidates['provisions'])}\n"
            f"Candidate Citations: {', '.join(candidates['citations'])}\n"
        )
        
        prompt = (
            f"Analyze the following Indian court judgment and produce a comprehensive research package.\n\n"
            f"Pre-extracted Candidates found in text:\n{candidates_str}\n"
            f"Judgment Text:\n{context.extracted_text}"
        )
        
        try:
            response = self.client.models.generate_content(
                model=model_name or settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_json_schema=ResearchOutput.model_json_schema(),
                    temperature=0.1,
                ),
            )
        except GeminiConfigurationError:
            raise
        except Exception as exc:
            raise GeminiAPIError(f"Gemini API request failed in ResearchAgent: {exc}") from exc
        
        if not response.text:
            raise ValueError("Research Agent returned an empty response")
            
        research_data = ResearchOutput.model_validate_json(response.text)
        context.research_output = research_data
        
        # Capture token usage
        if response.usage_metadata:
            context.metadata["research_prompt_tokens"] = response.usage_metadata.prompt_token_count
            context.metadata["research_completion_tokens"] = response.usage_metadata.candidates_token_count
            context.metadata["research_total_tokens"] = response.usage_metadata.total_token_count


research_agent = ResearchAgent()
