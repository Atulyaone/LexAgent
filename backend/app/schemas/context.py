from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.schemas.firac import FiracBrief


class WorkflowState(str, Enum):
    INITIALIZED = "INITIALIZED"
    RESEARCH = "RESEARCH"
    ANALYSIS = "ANALYSIS"
    VERIFICATION = "VERIFICATION"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    page_count: int


class StatutoryReference(BaseModel):
    act: str = Field(description="Name of the Act, Code, or Constitution")
    section: str = Field(description="Section, Article, Rule, Order, or Clause identifier")
    context: str = Field(description="Brief explanation of how it relates to the judgment")


class PrecedentReference(BaseModel):
    case_name: str = Field(description="Name of the landmark case/precedent")
    citation: Optional[str] = Field(None, description="Citation of the case, if available")
    relevance: str = Field(description="Brief statement of how this case is relevant to the judgment")


class KeyPassage(BaseModel):
    text: str = Field(description="Verbatim passage extracted from the judgment, approximately 100-150 words")
    page_reference: Optional[str] = Field(None, description="Page number or range if identifiable from the text")
    legal_issue_supported: str = Field(description="The specific legal issue supported or addressed by this passage")
    reason_for_selection: str = Field(description="The reason why this passage was selected as legally significant")


class ResearchOutput(BaseModel):
    legal_domain: Optional[str] = Field(None, description="The identified primary legal domain")
    parties: List[str] = Field(default_factory=list, description="Parties identified in the judgment (petitioner, respondent, etc.)")
    bench: List[str] = Field(default_factory=list, description="Names of judges on the bench")
    procedural_history: Optional[str] = Field(None, description="Procedural history if identifiable from the judgment")
    statutes: List[StatutoryReference] = Field(default_factory=list, description="List of identified statutory provisions")
    precedents: List[PrecedentReference] = Field(default_factory=list, description="List of identified landmark precedents")
    key_legal_issues: List[str] = Field(default_factory=list, description="Core legal issues or questions before the court")
    important_holdings: List[str] = Field(default_factory=list, description="Important holdings or legal findings of the court")
    key_passages: List[KeyPassage] = Field(default_factory=list, description="At most 10 verbatim excerpts from the judgment, each ~100-150 words, total budget ~1500 words")



class AnalysisOutput(BaseModel):
    firac_brief: Optional[FiracBrief] = Field(None, description="The generated structured FIRAC brief")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Analysis-specific metadata")


class CitationVerification(BaseModel):
    citation: str = Field(description="The citation or provision verified")
    found_in_text: bool = Field(description="Whether the citation actually appears in the extracted judgment text")
    is_hallucinated: bool = Field(description="Whether the citation appears to be hallucinated by the model")


class VerificationOutput(BaseModel):
    citations_verified: List[CitationVerification] = Field(default_factory=list)
    confidence_score: float = Field(default=100.0, description="Confidence score from 0.0 to 100.0")
    hallucination_detected: bool = Field(default=False, description="True if any citation is flagged as hallucinated")
    details: str = Field(default="", description="Qualitative summary of verification findings")


class TraceEntry(BaseModel):
    event: str = Field(description="Description of the execution trace event")
    timestamp: float = Field(description="Epoch timestamp of the event")


class AgentMetrics(BaseModel):
    execution_time_ms: float = Field(default=0.0, description="Time spent executing the agent")
    llm_calls: int = Field(default=0, description="Number of LLM calls made by the agent")
    prompt_tokens: int = Field(default=0, description="Input tokens consumed")
    completion_tokens: int = Field(default=0, description="Output tokens generated")
    total_tokens: int = Field(default=0, description="Total tokens consumed")


class ObservabilityMetadata(BaseModel):
    total_latency_ms: float = Field(default=0.0, description="Total execution time for the entire workflow")
    llm_call_count: int = Field(default=0, description="Total number of LLM calls made across all agents")
    total_prompt_tokens: int = Field(default=0, description="Total prompt tokens consumed")
    total_completion_tokens: int = Field(default=0, description="Total completion tokens consumed")
    total_tokens: int = Field(default=0, description="Total tokens consumed")
    agent_metrics: Dict[str, AgentMetrics] = Field(default_factory=dict, description="Execution metrics keyed by agent name")


class ExecutionState(BaseModel):
    current_agent: Optional[str] = Field(None, description="The active agent name")
    status: WorkflowState = Field(default=WorkflowState.INITIALIZED, description="Workflow state enum")
    trace: List[TraceEntry] = Field(default_factory=list, description="Observability trace log")
    errors: List[str] = Field(default_factory=list, description="Captured execution errors")


class AgentContext(BaseModel):
    session_id: str = Field(description="Unique session identifier")
    document: DocumentInfo
    extracted_text: str
    
    # Reusable structural compartments
    research_output: ResearchOutput = Field(default_factory=ResearchOutput)
    analysis_output: AnalysisOutput = Field(default_factory=AnalysisOutput)
    verification_output: VerificationOutput = Field(default_factory=VerificationOutput)
    observability: ObservabilityMetadata = Field(default_factory=ObservabilityMetadata)
    tool_results: Dict[str, Any] = Field(default_factory=dict, description="Intermediate outputs from tools")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="General metadata")
    execution_state: ExecutionState = Field(default_factory=ExecutionState)
