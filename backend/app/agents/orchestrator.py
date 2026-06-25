import time

from app.agents.case_analysis import CaseAnalysisAgent, case_analysis_agent
from app.schemas.analysis import AnalysisMetadata, AnalyzeResponse
from app.schemas.firac import FiracBrief
from app.services.document_store import DocumentStore, StoredDocument, document_store


class OrchestratorAgent:
    """Milestone 1 orchestrator: upload -> extract -> analyze -> return."""

    def __init__(
        self,
        store: DocumentStore | None = None,
        case_analysis: CaseAnalysisAgent | None = None,
    ) -> None:
        self._store = store or document_store
        self._case_analysis = case_analysis or case_analysis_agent

    def run_analysis(self, doc_id: str, *, model_name: str) -> AnalyzeResponse:
        document = self._store.get(doc_id)
        started = time.perf_counter()

        firac_brief = self._case_analysis.analyze(
            filename=document.filename,
            page_count=document.page_count,
            judgment_text=document.raw_text,
        )

        self._store.mark_processed(doc_id)
        elapsed_ms = int((time.perf_counter() - started) * 1000)

        return AnalyzeResponse(
            doc_id=document.doc_id,
            filename=document.filename,
            status="COMPLETE",
            firac_brief=firac_brief,
            metadata=AnalysisMetadata(
                page_count=document.page_count,
                model=model_name,
                processing_time_ms=elapsed_ms,
            ),
            error=None,
        )


orchestrator_agent = OrchestratorAgent()
