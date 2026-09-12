import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.decision_agent import EnterpriseOpportunity, run_decision


DATA_FILE = PROJECT_ROOT / "data" / "sample_opportunities.json"


def main() -> None:
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    opportunities = [EnterpriseOpportunity(**item) for item in raw]

    results = []
    for opportunity in opportunities:
        result = run_decision(opportunity)
        results.append(
            {
                "opportunity_name": opportunity.opportunity_name,
                "recommended_action": result.decision.recommended_action,
                "score": result.decision.total_score,
                "human_review_required": result.decision.human_review_required,
                "guardrail_passed": result.explanation_review.passes_guardrail_check,
                "published_explanation": result.published_explanation,
            }
        )

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
