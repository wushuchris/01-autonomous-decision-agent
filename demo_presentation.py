from __future__ import annotations

from html import escape
from typing import Iterable, Optional

from src.decision_agent import DecisionEvent, DecisionRunResult, ScoringResult


APP_CSS = """
:root, .gradio-container {
    color-scheme: light !important;
    --body-background-fill: #f8fafc !important;
    --body-text-color: #0f172a !important;
    --block-background-fill: #ffffff !important;
    --block-label-text-color: #334155 !important;
    --input-background-fill: #ffffff !important;
    --input-border-color: #cbd5e1 !important;
    --button-primary-background-fill: #4f46e5 !important;
    --button-primary-background-fill-hover: #4338ca !important;
    --button-primary-text-color: #ffffff !important;
}
.gradio-container {
    max-width: 1080px !important;
    margin: 0 auto !important;
    padding: 26px 24px 48px !important;
    background: #f8fafc !important;
    color: #0f172a !important;
}
.gradio-container label, .gradio-container label span, .gradio-container .label-wrap {
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
}
.gradio-container input, .gradio-container textarea {
    background: #ffffff !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}
.hero-card, .business-story, .boundary-card, .activity-card, .outcome-card, .evidence-panel {
    background: #ffffff !important;
    border: 1px solid #dbe3ee !important;
    box-shadow: 0 8px 28px rgba(15,23,42,.06) !important;
    color: #0f172a !important;
}
.hero-card { padding: 30px; border-radius: 18px; margin-bottom: 18px; }
.hero-eyebrow { font-size: .82rem; font-weight: 850; letter-spacing: .08em; text-transform: uppercase; color: #4338ca !important; }
.hero-card h1 { margin: 8px 0 14px; font-size: 2.35rem; line-height: 1.1; color: #0f172a !important; }
.hero-card p { margin: 0; line-height: 1.65; color: #475569 !important; font-size: 1.05rem; }
.pattern-line { margin-top: 18px; padding: 13px 15px; border-radius: 12px; background: #eef2ff; color: #312e81 !important; font-weight: 850; }
.business-story { border-radius: 18px; padding: 24px; margin: 4px 0 20px; }
.business-kicker { color: #4f46e5 !important; text-transform: uppercase; font-size: .78rem; letter-spacing: .07em; font-weight: 850; }
.business-story h2 { color: #0f172a !important; margin: 7px 0 10px; font-size: 1.4rem; }
.business-story p { color: #475569 !important; line-height: 1.62; margin: 0; }
.boundary-grid { display: grid; grid-template-columns: 1fr; gap: 12px; margin: 14px 0 24px; }
.boundary-card { border-radius: 16px; padding: 18px 20px; }
.boundary-card h3 { margin: 0 0 7px; color: #0f172a !important; }
.boundary-card p, .boundary-card li { color: #475569 !important; line-height: 1.55; }
.boundary-card ul { margin: 8px 0 0 20px; padding: 0; }
.section-title, .section-title h2 { color: #0f172a !important; }
#scenario-picker, #llm-toggle { background: #ffffff !important; border: 1px solid #dbe3ee !important; border-radius: 14px !important; padding: 12px 14px !important; }
#run-decision { background: #4f46e5 !important; border: 1px solid #4f46e5 !important; color: #ffffff !important; border-radius: 12px !important; min-height: 48px !important; font-weight: 800 !important; }
#run-decision:hover { background: #4338ca !important; border-color: #4338ca !important; }
.activity-card { padding: 20px; min-height: 118px; border-radius: 18px; margin-top: 10px; }
.activity-header, .outcome-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
.activity-title, .outcome-title { font-weight: 850; color: #0f172a !important; }
.badge { border-radius: 999px; padding: 4px 10px; background: #e2e8f0; color: #334155 !important; font-size: .76rem; font-weight: 850; }
.badge.running { background: #e0e7ff; color: #3730a3 !important; }
.badge.complete { background: #dcfce7; color: #166534 !important; }
.event-row { border-left: 3px solid #cbd5e1; padding: 7px 0 7px 12px; margin: 7px 0; }
.event-label { font-weight: 800; color: #1e293b !important; }
.event-message { color: #475569 !important; margin-top: 2px; }
.outcome-card { border-radius: 18px; padding: 22px; }
.outcome-action { font-size: 1.45rem; font-weight: 900; color: #312e81 !important; }
.outcome-card p, .outcome-card li { color: #334155 !important; line-height: 1.6; }
.evidence-panel { border-radius: 18px; overflow: hidden; }
.evidence-table-wrap { overflow-x: auto; }
.evidence-table { width: 100%; border-collapse: collapse; background: #ffffff; color: #1e293b; font-size: .9rem; }
.evidence-table th { text-align: left; padding: 11px 12px; background: #f1f5f9; color: #334155 !important; border-bottom: 1px solid #dbe3ee; white-space: nowrap; }
.evidence-table td { vertical-align: top; padding: 11px 12px; color: #334155 !important; border-bottom: 1px solid #edf2f7; line-height: 1.45; }
.evidence-empty { padding: 18px 20px; color: #64748b !important; }
.gradio-container [role="tab"] { background: transparent !important; color: #334155 !important; -webkit-text-fill-color: #334155 !important; border-bottom: 2px solid transparent !important; }
.gradio-container [role="tab"]:hover, .gradio-container [role="tab"]:focus { background: #eef2ff !important; color: #312e81 !important; -webkit-text-fill-color: #312e81 !important; }
.gradio-container [role="tab"][aria-selected="true"] { background: transparent !important; color: #4f46e5 !important; -webkit-text-fill-color: #4f46e5 !important; border-bottom-color: #4f46e5 !important; }
@media (min-width: 860px) { .boundary-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 700px) { .gradio-container { padding: 18px 14px 36px !important; } .hero-card { padding: 22px; } .hero-card h1 { font-size: 1.9rem; } }
footer { display: none !important; }
"""


HERO_HTML = """
<div class="hero-card">
  <div class="hero-eyebrow">01 · Autonomous Decision-Making Agent</div>
  <h1>How do you let AI recommend an autonomous action without letting the model invent the action space?</h1>
  <p>This demo follows a fictional B2B software company triaging enterprise opportunities. Application code owns the approved actions, scoring rules, and mandatory review gates. An optional LLM may explain the decision, but it cannot change it.</p>
  <div class="pattern-line">Validate → Score → Review gate → Select bounded action → Explain → Guardrail → Publish</div>
</div>
"""


BUSINESS_STORY_HTML = """
<div class="business-story">
  <div class="business-kicker">The business problem</div>
  <h2>A fictional software company receives more enterprise opportunities than its team can pursue at once.</h2>
  <p>The company wants consistent triage without giving a generative model authority to invent actions, ignore missing data, or bypass policy-risk review. Agent 1 demonstrates bounded autonomy: software decides from a fixed policy; AI can help communicate the result.</p>
</div>
<div class="boundary-grid">
  <div class="boundary-card"><h3>Application code controls</h3><ul><li>The four allowed outcomes</li><li>Factor weights and thresholds</li><li>Mandatory human-review conditions</li><li>Explanation publication guardrails</li></ul></div>
  <div class="boundary-card"><h3>The optional LLM can</h3><ul><li>Explain the already-selected action</li><li>Summarize approved factors</li><li>Improve business readability</li><li>Never change the action or bypass review</li></ul></div>
</div>
"""


_STAGE_LABELS = {
    "input_validated": "Input validated",
    "factors_scored": "Approved factors scored",
    "review_gate_checked": "Human-review gate checked",
    "action_selected": "Bounded action selected",
    "explanation_generated": "Explanation generated",
    "explanation_reviewed": "Explanation guardrails checked",
    "result_published": "Decision ready",
}


def render_activity(events: Iterable[DecisionEvent], complete: bool = False) -> str:
    events = list(events)
    if not events:
        return '<div class="activity-card"><div class="activity-header"><div class="activity-title">Live Decision Activity</div><div class="badge">IDLE</div></div><div class="event-message">Run a synthetic opportunity to watch the real bounded-decision pipeline.</div></div>'
    rows = []
    for event in events:
        rows.append(
            '<div class="event-row">'
            f'<div class="event-label">{escape(_STAGE_LABELS.get(event.stage, event.stage))}</div>'
            f'<div class="event-message">{escape(event.message)}</div>'
            '</div>'
        )
    badge_class = "complete" if complete else "running"
    badge_text = "COMPLETE" if complete else "RUNNING"
    return '<div class="activity-card"><div class="activity-header"><div class="activity-title">Live Decision Activity</div>' + f'<div class="badge {badge_class}">{badge_text}</div></div>' + ''.join(rows) + '</div>'


def render_outcome(result: Optional[DecisionRunResult]) -> str:
    if result is None:
        return '<div class="outcome-card"><div class="outcome-header"><div class="outcome-title">Business decision</div><div class="badge">WAITING</div></div><p>Run a scenario to see the bounded outcome and the reason it was selected.</p></div>'
    decision = result.decision
    factors = ''.join(f'<li>{escape(item)}</li>' for item in decision.key_factors[:4]) or '<li>No positive factors were required.</li>'
    risks = ''.join(f'<li>{escape(item)}</li>' for item in decision.risks_or_uncertainties[:4]) or '<li>No material uncertainty surfaced.</li>'
    return (
        '<div class="outcome-card"><div class="outcome-header"><div class="outcome-title">Business decision</div>'
        f'<div class="badge complete">{escape(result.opportunity.opportunity_name)}</div></div>'
        f'<div class="outcome-action">{escape(decision.recommended_action)}</div>'
        f'<p><strong>Application score:</strong> {decision.total_score} &nbsp; <strong>Confidence:</strong> {decision.confidence:.0%}</p>'
        f'<p>{escape(decision.reasoning_summary)}</p><strong>Positive factors</strong><ul>{factors}</ul><strong>Risks / uncertainties</strong><ul>{risks}</ul></div>'
    )


def render_scoring(scoring: Optional[ScoringResult]) -> str:
    if scoring is None:
        return '<div class="evidence-panel"><div class="evidence-empty">Run a scenario to inspect the application-owned factor contributions.</div></div>'
    rows = []
    for item in scoring.contributions:
        rows.append(f'<tr><td>{escape(item.factor)}</td><td>{item.points:+d}</td><td>{escape(item.kind)}</td><td>{escape(item.explanation)}</td></tr>')
    return '<div class="evidence-panel"><div class="evidence-table-wrap"><table class="evidence-table"><thead><tr><th>Factor</th><th>Points</th><th>Type</th><th>Application rationale</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div></div>'


def render_guardrail(result: Optional[DecisionRunResult]) -> str:
    if result is None:
        return '<div class="outcome-card"><div class="outcome-title">Explanation publication boundary</div><p>The explanation has not been generated yet.</p></div>'
    review = result.explanation_review
    status = "PASSED" if review.passes_guardrail_check else "FALLBACK USED"
    flags = ', '.join(f"{flag['category']}: {flag['term']}" for flag in review.flags) or "None"
    return (
        '<div class="outcome-card"><div class="outcome-header"><div class="outcome-title">Explanation publication boundary</div>'
        f'<div class="badge">{status}</div></div>'
        f'<p><strong>Action preserved:</strong> {review.action_preserved}<br><strong>Flags:</strong> {escape(flags)}<br><strong>Deterministic fallback used:</strong> {result.used_fallback_explanation}</p></div>'
    )
