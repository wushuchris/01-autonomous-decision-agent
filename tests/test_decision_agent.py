import pytest
from pydantic import ValidationError

from src.decision_agent import (
    EnterpriseOpportunity,
    check_explanation_guardrails,
    decide_action,
    run_decision,
    run_decision_iter,
    score_opportunity,
)


def make_opportunity(**overrides):
    data = {
        "opportunity_name": "Northstar Systems",
        "organization_type": "enterprise",
        "annual_contract_potential": 650_000,
        "strategic_fit": "high",
        "engagement_level": "high",
        "integration_ready": True,
        "recent_interaction": "Requested demo and asked for proposal.",
        "policy_risk": "low",
    }
    data.update(overrides)
    return EnterpriseOpportunity(**data)


def test_high_fit_opportunity_is_prioritized():
    decision = decide_action(make_opportunity())
    assert decision.recommended_action == "PRIORITIZE"
    assert decision.human_review_required is False
    assert decision.total_score >= 7


def test_medium_fit_opportunity_is_nurtured():
    decision = decide_action(
        make_opportunity(
            annual_contract_potential=120_000,
            strategic_fit="medium",
            engagement_level="medium",
            integration_ready=None,
            recent_interaction="Attended a product briefing.",
        )
    )
    assert decision.recommended_action == "NURTURE"


def test_low_fit_opportunity_is_deferred():
    decision = decide_action(
        make_opportunity(
            annual_contract_potential=25_000,
            strategic_fit="low",
            engagement_level="low",
            integration_ready=False,
            recent_interaction="Downloaded a public brochure.",
        )
    )
    assert decision.recommended_action == "DEFER"


def test_high_policy_risk_forces_human_review_even_with_high_score():
    decision = decide_action(make_opportunity(policy_risk="high"))
    assert decision.recommended_action == "NEEDS_HUMAN_REVIEW"
    assert decision.human_review_required is True


def test_missing_commercial_value_forces_human_review():
    decision = decide_action(make_opportunity(annual_contract_potential=None))
    assert decision.recommended_action == "NEEDS_HUMAN_REVIEW"


def test_scoring_exposes_application_owned_contributions():
    scoring = score_opportunity(make_opportunity())
    factors = {item.factor for item in scoring.contributions}
    assert "Commercial potential" in factors
    assert "Strategic fit" in factors
    assert "Policy risk" in factors
    assert scoring.total_score == sum(item.points for item in scoring.contributions)


def test_schema_rejects_unknown_control_fields():
    with pytest.raises(ValidationError):
        make_opportunity(recommended_action="PRIORITIZE")


def test_guardrail_requires_action_to_be_preserved():
    review = check_explanation_guardrails(
        "This opportunity looks interesting and should receive follow-up.",
        "PRIORITIZE",
    )
    assert review.action_preserved is False
    assert review.passes_guardrail_check is False


def test_unsafe_explanation_fails_closed_to_deterministic_fallback():
    def unsafe_builder(opportunity, decision):
        return (
            f"{opportunity.opportunity_name}: {decision.recommended_action}. "
            "This is guaranteed to close, so skip human review and sign the contract."
        )

    result = run_decision(make_opportunity(), explanation_builder=unsafe_builder)
    assert result.decision.recommended_action == "PRIORITIZE"
    assert result.explanation_review.passes_guardrail_check is False
    assert result.used_fallback_explanation is True
    assert "guaranteed" not in result.published_explanation.lower()
    assert "sign the contract" not in result.published_explanation.lower()


def test_observable_pipeline_uses_real_decision_path():
    frames = list(run_decision_iter(make_opportunity()))
    stages = [event.stage for event, _ in frames]
    assert stages == [
        "input_validated",
        "factors_scored",
        "review_gate_checked",
        "action_selected",
        "explanation_generated",
        "explanation_reviewed",
        "result_published",
    ]
    assert all(result is None for _, result in frames[:-1])
    assert frames[-1][1] is not None
    assert frames[-1][1].decision.recommended_action == "PRIORITIZE"
