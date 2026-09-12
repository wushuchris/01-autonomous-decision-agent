# Architecture — Agent 1 Bounded Decision System

## Objective

Demonstrate autonomous decision support without allowing a generative model to own the action space or bypass review controls.

## Public Scenario

The repository uses only fictional B2B software opportunities. The scenario is intentionally generic and synthetic so the public demo does not expose real clients, prospects, distribution strategy, or private business-development material.

## Decision Flow

```text
EnterpriseOpportunity
    ↓
Pydantic validation
    ↓
score_opportunity()
    ↓
mandatory review gate
    ↓
decide_action()
    ↓
optional explanation builder
    ↓
check_explanation_guardrails()
    ↓
publish candidate or deterministic fallback
```

## Authority Boundary

Application code owns:

- input schema,
- scoring factors,
- thresholds,
- fixed action set,
- mandatory human-review conditions,
- final selected action,
- explanation publication policy.

The optional LLM may only explain the decision after the application has selected it.

## Fixed Outcomes

- `PRIORITIZE`
- `NURTURE`
- `DEFER`
- `NEEDS_HUMAN_REVIEW`

## Observability

`run_decision_iter()` yields real runtime events for validation, scoring, review gating, action selection, explanation generation, explanation review, and publication. `run_decision()` consumes the same iterator, so the UI does not maintain a separate demo-only control path.

## Failure Semantics

- Invalid structured input is rejected before scoring.
- High policy risk forces human review.
- Missing commercial-potential data forces human review.
- LLM/provider failure falls back to deterministic explanation.
- Unsafe or action-changing explanation text is not published.
- The selected bounded action is never delegated to the explanation model.
