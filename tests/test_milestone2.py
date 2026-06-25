import asyncio
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.agents.research import research_agent
from app.agents.case_analysis import case_analysis_agent
from app.agents.verification import verification_agent
from app.agents.orchestrator import orchestrator_agent, WorkflowState
from app.schemas.context import (
    AgentContext,
    DocumentInfo,
    ResearchOutput,
    AnalysisOutput,
    StatutoryReference,
    PrecedentReference,
    KeyPassage,
    WorkflowState,
)
from app.schemas.firac import FiracBrief
from app.services.document_store import StoredDocument
from app.services.firac_generator import GeminiAPIError, GeminiConfigurationError


# 1. Test Research Agent deterministic extraction
def test_research_agent_deterministic_extraction():
    sample_text = """
    This appeal arises out of a contract dispute. The respondent relies on Section 56 of the Indian Contract Act, 1872.
    The petitioner cited the landmark decision in Satyabrata Ghose v. Mugneeram Bangur & Co., AIR 1954 SC 44.
    Alternatively, Article 21 of the Constitution of India was discussed in the context of personal liberty.
    Also, see Rule 4 of the Civil Rules and Order 39 of CPC.
    Another citation is (2020) 9 SCC 1.
    """
    
    # We can invoke the private extraction helper directly
    extracted = research_agent._deterministic_extract(sample_text)
    
    # Verify Acts (generic extraction extracts the core name before numbers/commas)
    assert "Indian Contract Act" in extracted["acts"]
    assert "Constitution of India" in extracted["acts"]
    
    # Verify provisions
    assert any("Section 56" in p for p in extracted["provisions"])
    assert any("Article 21" in p for p in extracted["provisions"])
    assert any("Rule 4" in p for p in extracted["provisions"])
    assert any("Order 39" in p for p in extracted["provisions"])
    
    # Verify citations
    assert "AIR 1954 SC 44" in extracted["citations"]
    assert "(2020) 9 SCC 1" in extracted["citations"]


# 2. Test Verification Agent citation validation (no LLM)
def test_verification_agent_deterministic_matching():
    async def run_test():
        brief = FiracBrief(
            facts="The parties entered into a lease agreement.",
            issues="Does Section 56 apply?",
            rule="Section 56 of the Indian Contract Act, 1872 and Satyabrata Ghose, AIR 1954 SC 44. Also Article 21.",
            analysis="The court analyzed the applicability of Section 56 and the ruling in Satyabrata Ghose.",
            conclusion="Article 21 was not violated."
        )
        
        # Case 1: All references exist in judgment text
        judgment_text_all = """
        This case deals with Section 56 of the Indian Contract Act, 1872.
        We refer to Satyabrata Ghose, AIR 1954 SC 44.
        Article 21 of the Constitution was also touched upon.
        """
        
        context_all = AgentContext(
            session_id="test_session_1",
            document=DocumentInfo(doc_id="doc_1", filename="case.pdf", page_count=5),
            extracted_text=judgment_text_all,
        )
        context_all.analysis_output = AnalysisOutput(firac_brief=brief)
        
        await verification_agent.run(context_all)
        
        assert context_all.verification_output.confidence_score == 100.0
        assert not context_all.verification_output.hallucination_detected
        
        # Case 2: Some references are missing (hallucinated)
        judgment_text_partial = """
        This case deals with Section 56.
        Satyabrata Ghose is not mentioned here.
        """
        context_partial = AgentContext(
            session_id="test_session_2",
            document=DocumentInfo(doc_id="doc_2", filename="case.pdf", page_count=5),
            extracted_text=judgment_text_partial,
        )
        context_partial.analysis_output = AnalysisOutput(firac_brief=brief)
        
        await verification_agent.run(context_partial)
        
        # Some references are missing, so confidence < 100
        assert context_partial.verification_output.confidence_score < 100.0
        assert context_partial.verification_output.hallucination_detected
        
        # Verify that the specific hallucinated reference is flagged
        hallucinated_citations = [
            c.citation for c in context_partial.verification_output.citations_verified if c.is_hallucinated
        ]
        assert len(hallucinated_citations) > 0

    asyncio.run(run_test())


# 3. Test Orchestrator State Machine and Trace Logging
def test_orchestrator_state_machine():
    async def run_test():
        # Mock document store returning a valid document
        mock_doc = StoredDocument(
            doc_id="doc_test_123",
            filename="test_judgment.pdf",
            file_path=Path("/tmp/test_judgment.pdf"),
            page_count=3,
            raw_text="Judgment text containing Section 56 and AIR 1954 SC 44.",
            status="PROCESSED"
        )
        
        mock_store = MagicMock()
        mock_store.get.return_value = mock_doc
        
        orchestrator = orchestrator_agent.__class__(store=mock_store)
        
        async def mock_research_run(context, model_name):
            context.research_output = ResearchOutput(
                legal_domain="Contract Law",
                parties=["Appellant Ltd.", "Respondent Corp."],
                bench=["Justice A", "Justice B"],
                procedural_history="Appeal from High Court",
                statutes=[StatutoryReference(act="Indian Contract Act, 1872", section="Section 56", context="Frustration")],
                precedents=[PrecedentReference(case_name="Satyabrata Ghose", citation="AIR 1954 SC 44", relevance="Frustration")],
                key_legal_issues=["Whether contract was frustrated"],
                important_holdings=["Contract not frustrated by temporary difficulty"],
                key_passages=[
                    KeyPassage(
                        text="Performance did not become impossible in the absolute sense.",
                        page_reference="4",
                        legal_issue_supported="Whether contract was frustrated",
                        reason_for_selection="Key reasoning on impossibility"
                    )
                ]
            )
            context.metadata["research_prompt_tokens"] = 120
            context.metadata["research_completion_tokens"] = 60
            context.metadata["research_total_tokens"] = 180
            
        async def mock_analysis_run(context, model_name):
            context.analysis_output = AnalysisOutput(
                firac_brief=FiracBrief(
                    facts="Facts of lease.",
                    issues="Issues regarding Section 56.",
                    rule="Section 56 and AIR 1954 SC 44.",
                    analysis="Analysis of frustration.",
                    conclusion="Lease not frustrated."
                )
            )
            context.metadata["analysis_prompt_tokens"] = 250
            context.metadata["analysis_completion_tokens"] = 150
            context.metadata["analysis_total_tokens"] = 400

        with patch.object(research_agent, "run", side_effect=mock_research_run), \
             patch.object(case_analysis_agent, "run", side_effect=mock_analysis_run):
             
            response = await orchestrator.run_analysis("doc_test_123", model_name="gemini-3.5-flash")
            
            # Verify response attributes
            assert response.doc_id == "doc_test_123"
            assert response.status == "COMPLETE"
            assert response.firac_brief.conclusion == "Lease not frustrated."
            
            # Verify trace progression
            assert response.trace == [
                "Orchestrator Started",
                "Research Agent Completed",
                "Case Analysis Completed",
                "Verification Completed",
                "Workflow Complete"
            ]

    asyncio.run(run_test())


# 4. Test API Backward Compatibility with TestClient (Success Case)
def test_api_analyze_backward_compatibility():
    client = TestClient(app)
    
    # We mock run_analysis to return our mock response
    async def mock_run_analysis(*args, **kwargs):
        # Return a valid AnalyzeResponse object matching the schema
        from app.schemas.analysis import AnalysisMetadata, AnalyzeResponse
        return AnalyzeResponse(
            doc_id="doc_api_123",
            filename="api_judgment.pdf",
            status="COMPLETE",
            firac_brief=FiracBrief(
                facts="Factual narrative.",
                issues="Legal questions.",
                rule="Section 56.",
                analysis="Applying rule to facts.",
                conclusion="Disposition."
            ),
            metadata=AnalysisMetadata(
                page_count=4,
                model="gemini-3.5-flash",
                processing_time_ms=1500
            ),
            error=None,
            trace=[
                "Orchestrator Started",
                "Research Agent Completed",
                "Case Analysis Completed",
                "Verification Completed",
                "Workflow Complete"
            ]
        )

    with patch.object(orchestrator_agent, "run_analysis", side_effect=mock_run_analysis):
        response = client.post(
            "/api/agents/analyze",
            json={"doc_id": "doc_api_123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["doc_id"] == "doc_api_123"
        assert data["status"] == "COMPLETE"
        assert data["firac_brief"]["conclusion"] == "Disposition."
        assert "trace" in data
        assert data["trace"] == [
            "Orchestrator Started",
            "Research Agent Completed",
            "Case Analysis Completed",
            "Verification Completed",
            "Workflow Complete"
        ]
        assert "observability" not in data


# 5. Test API Error Mapping (HTTP 502, 503, 500)
def test_api_analyze_error_mapping():
    client = TestClient(app)
    
    # Scenario A: Upstream Gemini Failure (HTTP 502)
    async def mock_run_analysis_502(*args, **kwargs):
        raise GeminiAPIError("Upstream API error: connection timeout")
        
    with patch.object(orchestrator_agent, "run_analysis", side_effect=mock_run_analysis_502):
        response = client.post(
            "/api/agents/analyze",
            json={"doc_id": "doc_api_502"}
        )
        assert response.status_code == 502
        assert "connection timeout" in response.json()["detail"]

    # Scenario B: Quota / Rate Limit Exhaustion (HTTP 503)
    async def mock_run_analysis_503(*args, **kwargs):
        raise GeminiAPIError("Gemini API error: 429 Resource exhausted (quota exceeded)")
        
    with patch.object(orchestrator_agent, "run_analysis", side_effect=mock_run_analysis_503):
        response = client.post(
            "/api/agents/analyze",
            json={"doc_id": "doc_api_503"}
        )
        assert response.status_code == 503
        assert "quota exhausted" in response.json()["detail"].lower()

    # Scenario C: Generic Internal Exception (HTTP 500)
    async def mock_run_analysis_500(*args, **kwargs):
        raise ValueError("Something went wrong internally during processing")
        
    with patch.object(orchestrator_agent, "run_analysis", side_effect=mock_run_analysis_500):
        response = client.post(
            "/api/agents/analyze",
            json={"doc_id": "doc_api_500"}
        )
        assert response.status_code == 500
        assert "internally" in response.json()["detail"].lower()


# 6. Test Case Analysis Agent does not receive full judgment text in prompt
def test_case_analysis_agent_no_judgment_in_prompt():
    async def run_test():
        # Create a dummy AgentContext
        context = AgentContext(
            session_id="test_session_no_judgment",
            document=DocumentInfo(doc_id="doc_no_judgment", filename="test.pdf", page_count=1),
            extracted_text="THIS IS THE FULL JUDGMENT TEXT THAT SHOULD NOT BE IN THE PROMPT"
        )
        # Populate the research output with some dummy data
        context.research_output = ResearchOutput(
            legal_domain="Constitutional Law",
            parties=["A v. B"],
            bench=["Justice X"],
            procedural_history="History of appeal",
            statutes=[StatutoryReference(act="Constitution of India", section="Article 21", context="Right to life")],
            precedents=[PrecedentReference(case_name="Gopalan", citation="AIR 1950 SC 27", relevance="Life and liberty")],
            key_legal_issues=["Is there a violation of Article 21?"],
            important_holdings=["No violation of Article 21"],
            key_passages=[
                KeyPassage(
                    text="Verbatim quote here",
                    page_reference="12",
                    legal_issue_supported="Is there a violation of Article 21?",
                    reason_for_selection="Core reasoning"
                )
            ]
        )
        
        agent = case_analysis_agent.__class__()
        mock_client = MagicMock()
        
        # Mock generate_content response
        mock_response = MagicMock()
        mock_response.text = '{"facts": "F", "issues": "I", "rule": "R", "analysis": "A", "conclusion": "C"}'
        mock_response.usage_metadata = MagicMock(prompt_token_count=100, candidates_token_count=50, total_token_count=150)
        mock_client.models.generate_content.return_value = mock_response
        
        agent._client = mock_client
        
        with patch("app.agents.case_analysis.settings.gemini_api_key", "dummy_key"):
            await agent.run(context, model_name="gemini-3.5-flash")
        
        # Inspect the prompt passed to generate_content
        args, kwargs = mock_client.models.generate_content.call_args
        prompt_content = kwargs["contents"]
        
        # Assert that the full judgment text is not in the prompt
        assert "THIS IS THE FULL JUDGMENT TEXT THAT SHOULD NOT BE IN THE PROMPT" not in prompt_content
        # Assert that the structured research package contents are in the prompt
        assert "Constitutional Law" in prompt_content
        assert "Article 21" in prompt_content
        assert "Gopalan" in prompt_content
        assert "Verbatim quote here" in prompt_content

    asyncio.run(run_test())

