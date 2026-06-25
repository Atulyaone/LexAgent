from app.schemas.firac import FiracBrief


def test_firac_brief_schema_accepts_valid_payload():
    brief = FiracBrief.model_validate(
        {
            "facts": "The petitioner challenged the impounding of a passport.",
            "issues": "Whether Article 21 protects the right to travel abroad.",
            "rule": "Article 21 of the Constitution of India.",
            "analysis": "The Court held that personal liberty includes travel abroad.",
            "conclusion": "The impounding order was set aside.",
        }
    )

    assert brief.facts.startswith("The petitioner")
    assert "Article 21" in brief.rule
