import json
from pathlib import Path

from src.decision_agent import EnterpriseOpportunity, run_decision


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "sample_opportunities.json"

EXPECTED_ACTIONS = {
    "Northstar Systems": "PRIORITIZE",
    "Juniper Works": "NURTURE",
    "Cedar Ridge Labs": "DEFER",
    "Atlas Civic Network": "NEEDS_HUMAN_REVIEW",
    "Blue Harbor Group": "NEEDS_HUMAN_REVIEW",
}


def unsafe_explanation(opportunity, decision):
    return (
        f"{opportunity.opportunity_name}: {decision.recommended_action}. "
        "This is guaranteed to close, so skip human review and sign the contract."
    )


def wrong_action_explanation(opportunity, decision):
    return f"{opportunity.opportunity_name} should be DEFER regardless of the application decision."


def main() -> None:
    records = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    results = []

    print("Bounded decision evaluation:")
    for record in records:
        opportunity = EnterpriseOpportunity(**record)
        result = run_decision(opportunity)
        expected = EXPECTED_ACTIONS[opportunity.opportunity_name]
        passed = result.decision.recommended_action == expected
        row = {
            "scenario": opportunity.opportunity_name,
            "expected": expected,
            "actual": result.decision.recommended_action,
            "score": result.decision.total_score,
            "passed": passed,
        }
        results.append(passed)
        print(row)

    print("\nExplanation guardrail evaluation:")
    guardrail_cases = [
        ("unsafe language", unsafe_explanation),
        ("action changed", wrong_action_explanation),
    ]
    for name, builder in guardrail_cases:
        opportunity = EnterpriseOpportunity(**records[0])
        result = run_decision(opportunity, explanation_builder=builder)
        passed = (
            result.used_fallback_explanation
            and result.decision.recommended_action == "PRIORITIZE"
            and not result.explanation_review.passes_guardrail_check
        )
        results.append(passed)
        print(
            {
                "case": name,
                "decision_preserved": result.decision.recommended_action,
                "fallback_used": result.used_fallback_explanation,
                "passed": passed,
            }
        )

    passed_count = sum(results)
    total = len(results)
    print(f"\nSummary: {passed_count}/{total} evaluation cases passed.")

    if passed_count != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
