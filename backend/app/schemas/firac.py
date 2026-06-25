from pydantic import BaseModel, Field


class FiracBrief(BaseModel):
    facts: str = Field(description="Concise factual narrative of the case")
    issues: str = Field(description="Legal questions the court had to answer")
    rule: str = Field(
        description="Applicable statutes, constitutional articles, and prior precedents"
    )
    analysis: str = Field(
        description="How the court applied the rule to the facts"
    )
    conclusion: str = Field(description="Final ruling and disposition of the case")
