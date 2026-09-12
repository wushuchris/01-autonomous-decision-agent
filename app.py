from __future__ import annotations

import json
import time
from functools import lru_cache
from pathlib import Path

import gradio as gr

from demo_presentation import (
    APP_CSS,
    BUSINESS_STORY_HTML,
    HERO_HTML,
    render_activity,
    render_guardrail,
    render_outcome,
    render_scoring,
)
from src.decision_agent import (
    EnterpriseOpportunity,
    generate_business_explanation,
    run_decision_iter,
)
from src.explanation_provider import HuggingFaceExplanationProvider


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_FILE = PROJECT_ROOT / "data" / "sample_opportunities.json"


@lru_cache(maxsize=1)
def load_scenarios() -> dict[str, EnterpriseOpportunity]:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {
        item["opportunity_name"]: EnterpriseOpportunity(**item)
        for item in data
    }


SCENARIO_DESCRIPTIONS = {
    "Northstar Systems": "Strong commercial value, fit, engagement, and readiness — expected bounded outcome: PRIORITIZE.",
    "Juniper Works": "Moderate value and engagement — expected bounded outcome: NURTURE.",
    "Cedar Ridge Labs": "Low value, fit, engagement, and readiness — expected bounded outcome: DEFER.",
    "Atlas Civic Network": "Strong opportunity but high policy risk — the review gate must override the score.",
    "Blue Harbor Group": "Strong fit but missing commercial value — incomplete decision data must route to human review.",
}


def scenario_summary(name: str) -> str:
    scenario = load_scenarios()[name]
    value = (
        f"${scenario.annual_contract_potential:,.0f}"
        if scenario.annual_contract_potential is not None
        else "Missing"
    )
    return (
        f"**Synthetic scenario:** {SCENARIO_DESCRIPTIONS[name]}\n\n"
        f"Organization type: **{scenario.organization_type}** · "
        f"Potential annual value: **{value}** · "
        f"Strategic fit: **{scenario.strategic_fit}** · "
        f"Engagement: **{scenario.engagement_level}** · "
        f"Policy risk: **{scenario.policy_risk}**"
    )


def _explanation_builder(use_llm: bool, mode_state: dict[str, str]):
    if not use_llm:
        mode_state["status"] = "Deterministic explanation mode. The bounded action is unchanged."
        return generate_business_explanation

    provider = HuggingFaceExplanationProvider()
    if not provider.configured:
        mode_state["status"] = (
            "LLM explanation was requested, but HF_TOKEN is not configured. "
            "The deterministic explanation fallback is being used."
        )
        return generate_business_explanation

    def builder(opportunity, decision):
        try:
            explanation = provider(opportunity, decision)
            mode_state["status"] = (
                "LLM-assisted explanation mode. Application code still owns the action and publication guardrail."
            )
            return explanation
        except Exception:
            mode_state["status"] = (
                "The optional LLM provider was unavailable, so the deterministic explanation fallback was used. "
                "The bounded action was unaffected."
            )
            return generate_business_explanation(opportunity, decision)

    return builder


def stream_decision(scenario_name: str, use_llm: bool):
    opportunity = load_scenarios()[scenario_name]
    mode_state: dict[str, str] = {}
    builder = _explanation_builder(bool(use_llm), mode_state)
    events = []

    for event, result in run_decision_iter(
        opportunity=opportunity,
        explanation_builder=builder,
    ):
        events.append(event)
        complete = result is not None
        published_explanation = (
            result.published_explanation
            if result is not None
            else "The application is still moving through the bounded decision pipeline."
        )
        scoring = result.scoring if result is not None else None
        guardrail = render_guardrail(result)
        mode_note = mode_state.get(
            "status",
            "The explanation layer has not run yet. Application code already owns the decision policy.",
        )

        yield (
            render_activity(events, complete=complete),
            render_outcome(result),
            published_explanation,
            mode_note,
            render_scoring(scoring),
            guardrail,
        )
        if not complete:
            time.sleep(0.18)


with gr.Blocks(
    title="01. Autonomous Decision-Making Agent",
    theme=gr.themes.Default(),
    css=APP_CSS,
    analytics_enabled=False,
) as demo:
    gr.HTML(HERO_HTML)
    gr.HTML(BUSINESS_STORY_HTML)

    gr.Markdown("## Try the bounded decision system", elem_classes=["section-title"])
    scenario_input = gr.Dropdown(
        choices=list(load_scenarios().keys()),
        value="Northstar Systems",
        label="Fictional enterprise opportunity",
        elem_id="scenario-picker",
    )
    scenario_preview = gr.Markdown(scenario_summary("Northstar Systems"))
    scenario_input.change(
        fn=scenario_summary,
        inputs=scenario_input,
        outputs=scenario_preview,
        show_progress="hidden",
    )

    llm_toggle = gr.Checkbox(
        label="Use optional LLM-assisted explanation when HF_TOKEN is configured",
        value=False,
        elem_id="llm-toggle",
    )
    run_button = gr.Button(
        "Run bounded decision",
        variant="primary",
        elem_id="run-decision",
    )

    activity_output = gr.HTML(render_activity([], complete=False))

    gr.Markdown("## Business decision", elem_classes=["section-title"])
    outcome_output = gr.HTML(render_outcome(None))

    gr.Markdown("## Published explanation", elem_classes=["section-title"])
    explanation_output = gr.Markdown(
        "Run a synthetic scenario to generate a guardrail-reviewed explanation.",
    )
    mode_output = gr.Markdown(
        "The explanation layer has not run yet. Application code already owns the decision policy."
    )

    with gr.Tabs():
        with gr.Tab("Decision Evidence"):
            gr.Markdown(
                "These are the exact application-owned factor contributions behind the bounded action. The explanation model does not control these scores."
            )
            scoring_output = gr.HTML(render_scoring(None))

        with gr.Tab("Guardrail Boundary"):
            gr.Markdown(
                "The explanation must preserve the application-selected action and avoid prohibited promises or unauthorized commitments. If it fails, a deterministic fallback is published instead."
            )
            guardrail_output = gr.HTML(render_guardrail(None))

        with gr.Tab("Architecture"):
            gr.Markdown(
                """
### Control boundary

**Application authority:** validate structured input, score approved factors, enforce mandatory review, select one action from the fixed action set, and decide whether an explanation may be published.

**Optional model authority:** explain the action after it has already been selected. The model receives no authority to change the action, threshold, score, or human-review requirement.

### Fixed action set

- `PRIORITIZE`
- `NURTURE`
- `DEFER`
- `NEEDS_HUMAN_REVIEW`

### Public-demo boundary

All opportunity records are fictional synthetic data. The public app does not persist visitor inputs, customer records, business-development lists, or generated runtime logs back into the repository.

### Reusable primitive

**Validate → Score → Review gate → Select bounded action → Explain → Guardrail → Publish**

This primitive becomes the portfolio baseline for later planning, memory, tool-use, workflow, and multi-agent systems where application code must retain authority over consequential actions.
"""
            )

    run_button.click(
        fn=stream_decision,
        inputs=[scenario_input, llm_toggle],
        outputs=[
            activity_output,
            outcome_output,
            explanation_output,
            mode_output,
            scoring_output,
            guardrail_output,
        ],
        show_progress="hidden",
    )


demo.queue()

if __name__ == "__main__":
    demo.launch()
