import re
from typing import List
from app.schemas.context import AgentContext, VerificationOutput, CitationVerification


class VerificationAgent:
    def _extract_references_from_brief(self, context: AgentContext) -> List[str]:
        """Extract citations and statutory sections from the generated brief."""
        brief = context.analysis_output.firac_brief
        if not brief:
            return []
            
        combined_text = " ".join([
            brief.facts,
            brief.issues,
            brief.rule,
            brief.analysis,
            brief.conclusion
        ])
        
        # Capture provisions (Sections, Articles, Rules, Orders, Clauses)
        provision_pattern = r"\b(?:Section|Sec\.?|Article|Art\.?|Rule|Order|Clause|Cl\.?)\s+\d+(?:\s*[A-Za-z])?\b"
        
        # Capture standard Indian citation patterns
        citation_patterns = [
            r"\bAIR\s+\d{4}\s+SC\s+\d+\b",
            r"\(\d{4}\)\s+\d+\s+SCC\s+\d+\b",
            r"\b\d{4}\s+SCC\s+OnLine\s+SC\s+\d+\b",
            r"\b\d{4}\s+\d+\s+SCR\s+\d+\b",
            r"\b\d{4}\s+\d+\s+SCALE\s+\d+\b",
            r"\b\d{4}\s+\d+\s+JT\s+\d+\b"
        ]
        
        found_refs = re.findall(provision_pattern, combined_text, re.IGNORECASE)
        for pattern in citation_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            found_refs.extend(matches)
            
        return list(set(found_refs))

    async def run(self, context: AgentContext, model_name: str = "") -> None:
        context.execution_state.current_agent = "VerificationAgent"
        
        references = self._extract_references_from_brief(context)
        if not references:
            context.verification_output = VerificationOutput(
                citations_verified=[],
                confidence_score=100.0,
                hallucination_detected=False,
                details="No legal references found in the generated brief to verify."
            )
            return
            
        verified_list = []
        found_count = 0
        cleaned_text = "".join(context.extracted_text.lower().split())
        
        for ref in references:
            cleaned_ref = "".join(ref.lower().split())
            found = cleaned_ref in cleaned_text
            if found:
                found_count += 1
                
            verified_list.append(
                CitationVerification(
                    citation=ref,
                    found_in_text=found,
                    is_hallucinated=not found
                )
            )
            
        confidence = (found_count / len(references)) * 100.0
        hallucination_detected = found_count < len(references)
        
        details = (
            f"Verified {len(references)} references. "
            f"Grounded: {found_count}. "
            f"Hallucinations flagged: {len(references) - found_count}."
        )
        
        context.verification_output = VerificationOutput(
            citations_verified=verified_list,
            confidence_score=round(confidence, 2),
            hallucination_detected=hallucination_detected,
            details=details
        )


verification_agent = VerificationAgent()
