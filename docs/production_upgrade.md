# Production Upgrade Notes — Agent 1

The public project is a synthetic portfolio system, not a production decision service.

## What the Retrofit Adds

- typed Pydantic input and output contracts,
- deterministic bounded scoring,
- mandatory review gates,
- optional LLM explanation behind the decision boundary,
- explanation publication guardrails,
- real runtime observability,
- deterministic evaluation,
- public-repository hygiene checks,
- test/evaluation-gated deployment,
- a live Gradio portfolio interface.

## Production Requirements Beyond the Demo

A real deployment would still require:

- authenticated users and authorization,
- organization-specific policy configuration,
- versioned decision policies,
- immutable audit storage with retention controls,
- human-review workflow ownership and service levels,
- monitoring for distribution drift and policy exceptions,
- historical outcome analysis before changing thresholds,
- fairness and impact analysis appropriate to the real domain,
- provider reliability controls for optional LLM explanations,
- change management and approval for consequential policy updates.

## Model Boundary

The optional LLM should remain non-authoritative. Moving score calculation, action selection, or mandatory review logic into a free-form prompt would weaken the central learning objective of Agent 1.

## Public Portfolio Boundary

The hosted demo should remain synthetic. Real customer/prospect records, private strategy, personal information, confidential company documents, private curriculum material, and secrets must not be introduced into the public repository, tests, logs, screenshots, or Space history.

## Deployment Standard

The intended production gate for the portfolio demo is:

```text
GitHub change
    ↓
pytest
    ↓
synthetic decision benchmark
    ↓
public-repo hygiene scan
    ↓
all green
    ↓
GitHub → Hugging Face deployment
    ↓
live human validation
```
