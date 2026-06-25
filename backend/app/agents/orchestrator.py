import time
import uuid
from typing import Dict, Any

from app.agents.research import research_agent
from app.agents.case_analysis import case_analysis_agent
from app.agents.verification import verification_agent
from app.schemas.analysis import AnalysisMetadata, AnalyzeResponse
from app.schemas.context import (
    AgentContext,
    DocumentInfo,
    TraceEntry,
    AgentMetrics,
    ObservabilityMetadata,
    WorkflowState,
)
from app.schemas.firac import FiracBrief
from app.services.document_store import DocumentStore, StoredDocument, document_store


class OrchestratorAgent:
    def __init__(self, store: DocumentStore | None = None) -> None:
        self._store = store or document_store

    def _record_transition(self, context: AgentContext, state: WorkflowState, detail: str) -> None:
        context.execution_state.status = state
        # The trace should simply show the workflow progression.
        # e.g. "Orchestrator Started", "Research Agent Completed", etc.
        context.execution_state.trace.append(
            TraceEntry(event=detail, timestamp=time.time())
        )

    async def run_analysis(self, doc_id: str, *, model_name: str) -> AnalyzeResponse:
        document = self._store.get(doc_id)
        start_total = time.perf_counter()

        # Initialize the shared AgentContext
        context = AgentContext(
            session_id=str(uuid.uuid4()),
            document=DocumentInfo(
                doc_id=document.doc_id,
                filename=document.filename,
                page_count=document.page_count,
            ),
            extracted_text=document.raw_text,
        )

        # Transition: INITIALIZED
        self._record_transition(context, WorkflowState.INITIALIZED, "Orchestrator Started")

        try:
            # Transition: RESEARCH
            self._record_transition(context, WorkflowState.RESEARCH, "Executing Research Agent")
            start_agent = time.perf_counter()
            await research_agent.run(context, model_name)
            research_time = int((time.perf_counter() - start_agent) * 1000)
            
            # Record internal metrics
            context.observability.agent_metrics["ResearchAgent"] = AgentMetrics(
                execution_time_ms=research_time,
                llm_calls=1,
                prompt_tokens=context.metadata.get("research_prompt_tokens", 0),
                completion_tokens=context.metadata.get("research_completion_tokens", 0),
                total_tokens=context.metadata.get("research_total_tokens", 0),
            )
            self._record_transition(context, WorkflowState.RESEARCH, "Research Agent Completed")

            # Transition: ANALYSIS
            self._record_transition(context, WorkflowState.ANALYSIS, "Executing Case Analysis Agent")
            start_agent = time.perf_counter()
            await case_analysis_agent.run(context, model_name)
            analysis_time = int((time.perf_counter() - start_agent) * 1000)
            
            context.observability.agent_metrics["CaseAnalysisAgent"] = AgentMetrics(
                execution_time_ms=analysis_time,
                llm_calls=1,
                prompt_tokens=context.metadata.get("analysis_prompt_tokens", 0),
                completion_tokens=context.metadata.get("analysis_completion_tokens", 0),
                total_tokens=context.metadata.get("analysis_total_tokens", 0),
            )
            self._record_transition(context, WorkflowState.ANALYSIS, "Case Analysis Completed")

            # Transition: VERIFICATION
            self._record_transition(context, WorkflowState.VERIFICATION, "Executing Verification Agent")
            start_agent = time.perf_counter()
            await verification_agent.run(context, model_name)
            verification_time = int((time.perf_counter() - start_agent) * 1000)
            
            context.observability.agent_metrics["VerificationAgent"] = AgentMetrics(
                execution_time_ms=verification_time,
                llm_calls=0,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            )
            self._record_transition(context, WorkflowState.VERIFICATION, "Verification Completed")

            # Transition: COMPLETE
            self._record_transition(context, WorkflowState.COMPLETE, "Workflow Complete")

        except Exception as exc:
            # Transition: FAILED
            self._record_transition(context, WorkflowState.FAILED, f"Workflow Failed: {str(exc)}")
            context.execution_state.errors.append(str(exc))
            self._store.mark_processed(doc_id)
            elapsed_ms = int((time.perf_counter() - start_total) * 1000)
            
            # Aggregate what we can of observability
            context.observability.total_latency_ms = elapsed_ms
            context.observability.llm_call_count = sum(m.llm_calls for m in context.observability.agent_metrics.values())
            context.observability.total_prompt_tokens = sum(m.prompt_tokens for m in context.observability.agent_metrics.values())
            context.observability.total_completion_tokens = sum(m.completion_tokens for m in context.observability.agent_metrics.values())
            context.observability.total_tokens = sum(m.total_tokens for m in context.observability.agent_metrics.values())
            
            # Log trace and observability internally for debugging
            import logging
            logger = logging.getLogger("app.orchestrator")
            trace_strings = [entry.event for entry in context.execution_state.trace]
            logger.error(
                f"Orchestration failed for doc_id {doc_id}. "
                f"Trace: {trace_strings}. "
                f"Observability: {context.observability.model_dump()}. "
                f"Error: {str(exc)}"
            )
            raise exc

        self._store.mark_processed(doc_id)
        elapsed_ms = int((time.perf_counter() - start_total) * 1000)

        # Aggregate total observability metrics
        context.observability.total_latency_ms = elapsed_ms
        context.observability.llm_call_count = sum(m.llm_calls for m in context.observability.agent_metrics.values())
        context.observability.total_prompt_tokens = sum(m.prompt_tokens for m in context.observability.agent_metrics.values())
        context.observability.total_completion_tokens = sum(m.completion_tokens for m in context.observability.agent_metrics.values())
        context.observability.total_tokens = sum(m.total_tokens for m in context.observability.agent_metrics.values())

        # Clean public trace containing only progression events
        trace_strings = [entry.event for entry in context.execution_state.trace if not entry.event.startswith("Executing")]

        if not context.analysis_output.firac_brief:
            raise ValueError("Orchestration completed but no FIRAC brief was generated")

        return AnalyzeResponse(
            doc_id=document.doc_id,
            filename=document.filename,
            status="COMPLETE",
            firac_brief=context.analysis_output.firac_brief,
            metadata=AnalysisMetadata(
                page_count=document.page_count,
                model=model_name,
                processing_time_ms=elapsed_ms,
            ),
            error=None,
            trace=trace_strings,
        )


orchestrator_agent = OrchestratorAgent()
