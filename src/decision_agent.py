from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


AllowedAction = Literal[
    "PRIORITIZE",
    "NURTURE",
    "DEFER",
    "NEEDS_HUMAN_REVIEW",
]

DecisionStage = Literal[
    "input_validated",
    "factors_scored",
    "review_gate_checked",
    "action_selected",
    "explanation_generated",
    "explanation_reviewed",
    "result_published",
]


class EnterpriseOpportunity(BaseModel):
    """Synthetic B2B opportunity used by the public portfolio demo."""

    model_config = ConfigDict(extra="forbid")

    opportunity_name: str = Field(min_length=1, max_length=100)
    organization_type: Literal[
        "enterprise",
        "mid_market",
        "public_sector",
        "nonprofit",
        "startup",
        "unknown",
    ]
    annual_contract_potential: Optional[float] = Field(default=None, ge=0)
    strategic_fit: Literal["low", "medium", "high", "unknown"]
    engagement_level: Literal["low", "medium", "high", "unknown"]
    integration_ready: Optional[bool] = None
    recent_interaction: Optional[str] = Field(default=None, max_length=500)
    policy_risk: Literal["low", "medium", "high", "unknown"]


class ScoreContribution(BaseModel):
    model_config = ConfigDict(extra="forbid")

    factor: str
    points: int
    explanation: str
    kind: Literal["positive", "negative", "uncertainty", "control"]


class ScoringResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_score: int
    contributions: list[ScoreContribution]
    force_human_review: bool
    review_reasons: list[str]


class DecisionOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommended_action: AllowedAction
    confidence: float = Field(ge=0.0, le=1.0)
    total_score: int
    reasoning_summary: str
    key_factors: list[str]
    risks_or_uncertainties: list[str]
    human_review_required: bool


class ExplanationReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_action: AllowedAction
    action_preserved: bool
    flags: list[dict[str, str]]
    passes_guardrail_check: bool


class DecisionEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: DecisionStage
    message: str


class DecisionRunResult(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    opportunity: EnterpriseOpportunity
    scoring: ScoringResult
    decision: DecisionOutput
    candidate_explanation: str
    published_explanation: str
    explanation_review: ExplanationReview
    used_fallback_explanation: bool


@dataclass(frozen=True)
class DecisionPolicy:
    prioritize_threshold: int = 7
    nurture_threshold: int = 3


DEFAULT_POLICY = DecisionPolicy()
ExplanationBuilder = Callable[[EnterpriseOpportunity, DecisionOutput], str]


def score_opportunity(opportunity: EnterpriseOpportunity) -> ScoringResult:
    score = 0
    contributions: list[ScoreContribution] = []
    review_reasons: list[str] = []
    force_human_review = False

    def add(factor: str, points: int, explanation: str, kind: str) -> None:
        nonlocal score
        score += points
        contributions.append(
            ScoreContribution(
                factor=factor,
                points=points,
                explanation=explanation,
                kind=kind,
            )
        )

    if opportunity.policy_risk == "high":
        force_human_review = True
        review_reasons.append("High policy risk requires a human decision before outreach.")
        add("Policy risk", 0, "High policy risk triggers the review gate.", "control")
    elif opportunity.policy_risk == "medium":
        add("Policy risk", -1, "Medium policy risk reduces priority.", "negative")
    elif opportunity.policy_risk == "low":
        add("Policy risk", 1, "Low policy risk supports normal automated triage.", "positive")
    else:
        add("Policy risk", 0, "Policy risk is unknown.", "uncertainty")

    if opportunity.annual_contract_potential is None:
        force_human_review = True
        review_reasons.append("Commercial potential is missing and should be reviewed by a person.")
        add("Commercial potential", 0, "Commercial potential is missing.", "control")
    elif opportunity.annual_contract_potential >= 500_000:
        add("Commercial potential", 3, "Large potential annual contract value.", "positive")
    elif opportunity.annual_contract_potential >= 200_000:
        add("Commercial potential", 2, "Moderate potential annual contract value.", "positive")
    elif opportunity.annual_contract_potential >= 75_000:
        add("Commercial potential", 1, "Smaller but potentially relevant contract value.", "positive")
    else:
        add("Commercial potential", -1, "Limited near-term commercial value.", "negative")

    if opportunity.strategic_fit == "high":
        add("Strategic fit", 3, "Strong alignment with the fictional product strategy.", "positive")
    elif opportunity.strategic_fit == "medium":
        add("Strategic fit", 1, "Moderate strategic alignment.", "positive")
    elif opportunity.strategic_fit == "low":
        add("Strategic fit", -1, "Low strategic alignment.", "negative")
    else:
        add("Strategic fit", 0, "Strategic fit is unknown.", "uncertainty")

    if opportunity.engagement_level == "high":
        add("Engagement", 2, "The fictional prospect is actively engaged.", "positive")
    elif opportunity.engagement_level == "medium":
        add("Engagement", 1, "The fictional prospect shows moderate engagement.", "positive")
    elif opportunity.engagement_level == "low":
        add("Engagement", -1, "Current engagement is low.", "negative")
    else:
        add("Engagement", 0, "Engagement is unknown.", "uncertainty")

    if opportunity.integration_ready is True:
        add("Integration readiness", 1, "Technical prerequisites appear ready.", "positive")
    elif opportunity.integration_ready is False:
        add("Integration readiness", -1, "Technical prerequisites are not ready.", "negative")
    else:
        add("Integration readiness", 0, "Integration readiness is unknown.", "uncertainty")

    interaction = (opportunity.recent_interaction or "").lower()
    if any(term in interaction for term in ("requested demo", "requested follow-up", "asked for proposal")):
        add("Recent interaction", 1, "Recent interaction signals active buying interest.", "positive")

    return ScoringResult(
        total_score=score,
        contributions=contributions,
        force_human_review=force_human_review,
        review_reasons=review_reasons,
    )


def decide_action(
    opportunity: EnterpriseOpportunity,
    policy: DecisionPolicy = DEFAULT_POLICY,
) -> DecisionOutput:
    scoring = score_opportunity(opportunity)

    if scoring.force_human_review:
        action: AllowedAction = "NEEDS_HUMAN_REVIEW"
        confidence = 0.90
    elif scoring.total_score >= policy.prioritize_threshold:
        action = "PRIORITIZE"
        confidence = 0.86
    elif scoring.total_score >= policy.nurture_threshold:
        action = "NURTURE"
        confidence = 0.78
    else:
        action = "DEFER"
        confidence = 0.72

    positive = [
        contribution.explanation
        for contribution in scoring.contributions
        if contribution.kind == "positive"
    ]
    risks = [
        contribution.explanation
        for contribution in scoring.contributions
        if contribution.kind in {"negative", "uncertainty", "control"}
    ] + scoring.review_reasons

    return DecisionOutput(
        recommended_action=action,
        confidence=confidence,
        total_score=scoring.total_score,
        reasoning_summary=(
            f"Application policy produced a score of {scoring.total_score} and selected "
            f"{action} from the fixed action set."
        ),
        key_factors=positive,
        risks_or_uncertainties=list(dict.fromkeys(risks)),
        human_review_required=action == "NEEDS_HUMAN_REVIEW",
    )


def generate_business_explanation(
    opportunity: EnterpriseOpportunity,
    decision: DecisionOutput,
) -> str:
    next_steps = {
        "PRIORITIZE": "Route the opportunity to timely human follow-up with relevant preparation materials.",
        "NURTURE": "Keep the opportunity in a structured nurture path and monitor for stronger intent.",
        "DEFER": "Do not prioritize immediate outreach; retain the fictional opportunity for future review.",
        "NEEDS_HUMAN_REVIEW": "Pause automated follow-up and send the opportunity to a human reviewer.",
    }

    return (
        f"{opportunity.opportunity_name} was assigned {decision.recommended_action}. "
        f"{decision.reasoning_summary} "
        f"Next step: {next_steps[decision.recommended_action]}"
    )


def check_explanation_guardrails(
    explanation: str,
    expected_action: AllowedAction,
) -> ExplanationReview:
    text = explanation.lower()
    flagged_terms = {
        "performance_or_outcome_promise": [
            "guarantee",
            "guaranteed",
            "cannot fail",
            "certain to close",
            "will definitely close",
            "risk-free",
        ],
        "unauthorized_action": [
            "sign the contract",
            "approve the contract",
            "commit the company",
            "send payment",
            "override compliance",
        ],
        "exaggerated_urgency": [
            "must act immediately",
            "no review needed",
            "skip human review",
        ],
    }

    flags: list[dict[str, str]] = []
    for category, terms in flagged_terms.items():
        for term in terms:
            if term in text:
                flags.append({"category": category, "term": term})

    action_preserved = expected_action.lower() in text
    return ExplanationReview(
        expected_action=expected_action,
        action_preserved=action_preserved,
        flags=flags,
        passes_guardrail_check=(not flags and action_preserved),
    )


def run_decision_iter(
    opportunity: EnterpriseOpportunity,
    explanation_builder: Optional[ExplanationBuilder] = None,
    policy: DecisionPolicy = DEFAULT_POLICY,
) -> Iterable[tuple[DecisionEvent, Optional[DecisionRunResult]]]:
    yield DecisionEvent(
        stage="input_validated",
        message="Structured opportunity input passed the application schema.",
    ), None

    scoring = score_opportunity(opportunity)
    yield DecisionEvent(
        stage="factors_scored",
        message=f"Application policy scored the approved factors. Total score: {scoring.total_score}.",
    ), None

    if scoring.force_human_review:
        gate_message = "The application review gate requires a human decision."
    else:
        gate_message = "No mandatory human-review condition was triggered."
    yield DecisionEvent(stage="review_gate_checked", message=gate_message), None

    decision = decide_action(opportunity, policy=policy)
    yield DecisionEvent(
        stage="action_selected",
        message=f"Application code selected bounded action: {decision.recommended_action}.",
    ), None

    builder = explanation_builder or generate_business_explanation
    candidate = builder(opportunity, decision)
    yield DecisionEvent(
        stage="explanation_generated",
        message="The explanation layer described the already-made decision.",
    ), None

    review = check_explanation_guardrails(candidate, decision.recommended_action)
    yield DecisionEvent(
        stage="explanation_reviewed",
        message=(
            "Explanation passed publication guardrails."
            if review.passes_guardrail_check
            else "Explanation failed publication guardrails; deterministic fallback will be used."
        ),
    ), None

    fallback = generate_business_explanation(opportunity, decision)
    used_fallback = not review.passes_guardrail_check
    published = fallback if used_fallback else candidate

    result = DecisionRunResult(
        opportunity=opportunity,
        scoring=scoring,
        decision=decision,
        candidate_explanation=candidate,
        published_explanation=published,
        explanation_review=review,
        used_fallback_explanation=used_fallback,
    )

    yield DecisionEvent(
        stage="result_published",
        message="A bounded decision and guardrail-approved explanation are ready for review.",
    ), result


def run_decision(
    opportunity: EnterpriseOpportunity,
    explanation_builder: Optional[ExplanationBuilder] = None,
    policy: DecisionPolicy = DEFAULT_POLICY,
) -> DecisionRunResult:
    final_result: Optional[DecisionRunResult] = None
    for _, result in run_decision_iter(
        opportunity=opportunity,
        explanation_builder=explanation_builder,
        policy=policy,
    ):
        if result is not None:
            final_result = result

    if final_result is None:
        raise RuntimeError("Decision pipeline completed without a final result.")
    return final_result
