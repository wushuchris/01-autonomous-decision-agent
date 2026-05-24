# Code developed using ChatGPT (ChatGPT, 2026) as a paired programmer.

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


AllowedAction = Literal[
    "HIGH_PRIORITY_FOLLOW_UP",
    "NURTURE",
    "LOW_PRIORITY",
    "NEEDS_HUMAN_REVIEW"
]


class AdvisorLead(BaseModel):
    advisor_name: str
    firm_type: str
    aum: Optional[float] = Field(
        default=None,
        description="Advisor or firm assets under management in dollars"
    )
    interest_level: Literal["low", "medium", "high", "unknown"]
    uses_model_marketplace: Optional[bool] = None
    current_equity_manager: Optional[str] = None
    client_base: Optional[str] = None
    recent_interaction: Optional[str] = None
    compliance_risk: Literal["low", "medium", "high", "unknown"]


class DecisionOutput(BaseModel):
    recommended_action: AllowedAction
    confidence: float
    reasoning_summary: str
    key_factors: List[str]
    risks_or_uncertainties: List[str]
    human_review_required: bool


def score_lead(lead: AdvisorLead) -> dict:
    """
    Evaluate an advisor lead and return a scoring summary.

    This function does not make the final decision.
    It evaluates the lead and prepares the information needed for the decision step.
    """

    score = 0
    key_factors = []
    risks = []
    force_human_review = False

    if lead.compliance_risk == "high":
        force_human_review = True
        risks.append("High compliance risk requires human review.")
    elif lead.compliance_risk == "medium":
        score -= 1
        risks.append("Medium compliance risk may require careful messaging.")
    elif lead.compliance_risk == "low":
        score += 1
        key_factors.append("Low compliance risk.")

    if lead.aum is None:
        risks.append("AUM is missing.")
        force_human_review = True
    elif lead.aum >= 250_000_000:
        score += 3
        key_factors.append("Strong AUM fit.")
    elif lead.aum >= 100_000_000:
        score += 2
        key_factors.append("Moderate AUM fit.")
    elif lead.aum >= 25_000_000:
        score += 1
        key_factors.append("Smaller but potentially relevant AUM.")
    else:
        score -= 1
        risks.append("AUM may be too small for immediate prioritization.")

    if lead.interest_level == "high":
        score += 3
        key_factors.append("High stated interest.")
    elif lead.interest_level == "medium":
        score += 1
        key_factors.append("Moderate stated interest.")
    elif lead.interest_level == "low":
        score -= 1
        risks.append("Low stated interest.")
    else:
        risks.append("Interest level is unknown.")

    if lead.uses_model_marketplace is True:
        score += 2
        key_factors.append("Uses model marketplace or platform access.")
    elif lead.uses_model_marketplace is None:
        risks.append("Model marketplace usage is unknown.")

    if lead.recent_interaction:
        interaction_text = lead.recent_interaction.lower()

        if "workshop" in interaction_text:
            score += 2
            key_factors.append("Recent workshop engagement.")

        if "asked" in interaction_text or "follow up" in interaction_text:
            score += 1
            key_factors.append("Recent interaction suggests active curiosity.")

    return {
        "score": score,
        "key_factors": key_factors,
        "risks": risks,
        "force_human_review": force_human_review
    }


def decide_action(lead: AdvisorLead) -> DecisionOutput:
    """
    Convert a scored advisor lead into a bounded decision.

    This is the core decision-making function for the agent.
    """

    result = score_lead(lead)
    score = result["score"]

    if result["force_human_review"]:
        action = "NEEDS_HUMAN_REVIEW"
        confidence = 0.90
    elif score >= 7:
        action = "HIGH_PRIORITY_FOLLOW_UP"
        confidence = 0.85
    elif score >= 3:
        action = "NURTURE"
        confidence = 0.75
    else:
        action = "LOW_PRIORITY"
        confidence = 0.70

    reasoning_summary = (
        f"The lead received a score of {score}. "
        f"The recommended action is {action} based on fit, interest, risk, and recent engagement."
    )

    return DecisionOutput(
        recommended_action=action,
        confidence=confidence,
        reasoning_summary=reasoning_summary,
        key_factors=result["key_factors"],
        risks_or_uncertainties=result["risks"],
        human_review_required=action == "NEEDS_HUMAN_REVIEW"
    )


def generate_business_explanation(lead: AdvisorLead, decision: DecisionOutput) -> str:
    """
    Generate a non-LLM business-facing explanation.

    This function is useful as a fallback if an LLM provider is unavailable.
    """

    explanation = f"""
Advisor Lead: {lead.advisor_name}

Recommended Action: {decision.recommended_action}

Why this decision was made:
{decision.reasoning_summary}

Key positive factors:
{chr(10).join(["- " + factor for factor in decision.key_factors]) if decision.key_factors else "- No major positive factors identified."}

Risks or uncertainties:
{chr(10).join(["- " + risk for risk in decision.risks_or_uncertainties]) if decision.risks_or_uncertainties else "- No major risks or uncertainties identified."}

Human Review Required: {decision.human_review_required}

Suggested next step:
"""

    if decision.recommended_action == "HIGH_PRIORITY_FOLLOW_UP":
        explanation += "Schedule a timely follow-up conversation and prepare relevant materials based on the advisor's interests."
    elif decision.recommended_action == "NURTURE":
        explanation += "Add the advisor to a nurture sequence and continue providing educational content."
    elif decision.recommended_action == "LOW_PRIORITY":
        explanation += "Do not prioritize immediate outreach, but keep the lead in the database for future engagement."
    elif decision.recommended_action == "NEEDS_HUMAN_REVIEW":
        explanation += "Send this lead to a human reviewer before taking action."

    return explanation.strip()


def check_explanation_guardrails(explanation: str, expected_action: str) -> dict:
    """
    Run a lightweight guardrail check on an explanation.

    This function looks for potentially problematic language.
    """

    explanation_lower = explanation.lower()

    flagged_terms = {
        "performance_promises": [
            "guarantee",
            "guaranteed",
            "will outperform",
            "will beat",
            "superior returns",
            "risk-free",
            "no risk",
            "certain return"
        ],
        "specific_investment_recommendations": [
            "buy ",
            "sell ",
            "invest in ",
            "recommend this fund",
            "recommend this strategy",
            "allocate to "
        ],
        "exaggerated_claims": [
            "best-in-class",
            "unmatched",
            "cannot fail",
            "perfect fit",
            "sure thing",
            "must act immediately"
        ]
    }

    flags = []

    for category, terms in flagged_terms.items():
        for term in terms:
            if term in explanation_lower:
                flags.append({
                    "category": category,
                    "term": term
                })

    normalized_explanation = explanation_lower.replace(" ", "_").replace("-", "_")
    action_preserved = expected_action.lower() in normalized_explanation

    return {
        "expected_action": expected_action,
        "action_preserved": action_preserved,
        "flag_count": len(flags),
        "flags": flags,
        "passes_guardrail_check": len(flags) == 0
    }


def summarize_batch_results(batch_results: list[dict]) -> list[dict]:
    """
    Create a lightweight summary of batch agent results.
    """

    summary_rows = []

    for result in batch_results:
        summary_rows.append({
            "advisor_name": result["lead"]["advisor_name"],
            "firm_type": result["lead"]["firm_type"],
            "aum": result["lead"]["aum"],
            "recommended_action": result["decision"]["recommended_action"],
            "confidence": result["decision"]["confidence"],
            "human_review_required": result["decision"]["human_review_required"],
            "guardrail_passed": result["guardrail_check"]["passes_guardrail_check"],
            "guardrail_flag_count": result["guardrail_check"]["flag_count"]
        })

    return summary_rows
