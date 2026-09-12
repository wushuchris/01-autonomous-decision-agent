---
title: 01 Autonomous Decision-Making Agent
emoji: 🎯
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: "5.0.0"
python_version: "3.10"
app_file: app.py
pinned: false
---

# 01. Autonomous Decision-Making Agent — Bounded Decision System

## Business Question

> **How do you let AI recommend an autonomous action without letting the model invent the action space or bypass the guardrails?**

This project demonstrates bounded autonomy using a fully fictional B2B software opportunity-triage scenario. Application code validates the input, scores approved factors, enforces mandatory human-review conditions, and selects exactly one action from a fixed set. An optional LLM may explain the already-made decision, but it cannot change the score, action, threshold, or review requirement.

All public-demo records are synthetic.

## Core Pattern

```text
Validate → Score → Review gate → Select bounded action → Explain → Guardrail → Publish
```

The design principle is:

> **Rules decide. The LLM explains. Guardrails review.**

## Fixed Action Set

- `PRIORITIZE`
- `NURTURE`
- `DEFER`
- `NEEDS_HUMAN_REVIEW`

The model never invents a fifth action.

## Architecture

```text
Synthetic opportunity
    ↓
Pydantic validation
    ↓
Application-owned factor scoring
    ↓
Mandatory human-review gate
    ↓
Bounded action selection
    ↓
Deterministic or optional LLM explanation
    ↓
Explanation publication guardrail
    ├── pass → publish candidate explanation
    └── fail → publish deterministic fallback
```

## Decision Authority

### Application code owns

- the allowed action set,
- scoring factors and point values,
- decision thresholds,
- mandatory human-review conditions,
- final selected action,
- explanation publication rules.

### Optional LLM owns only

- wording of the explanation after the action has already been selected.

The public app works without an LLM provider. If `HF_TOKEN` is configured in the deployment environment, the visitor may optionally request an LLM-assisted explanation. Provider failure never changes the bounded decision.

## Human-Review Boundary

Two current controls force `NEEDS_HUMAN_REVIEW` regardless of an otherwise strong score:

- high policy risk,
- missing commercial-potential data.

This is intentional: a score is not allowed to override a mandatory review gate.

## Explanation Guardrail

The explanation layer is checked for:

- action preservation,
- guarantees or outcome promises,
- unauthorized contract/commitment language,
- instructions to bypass human review.

If the explanation fails, the candidate text is not published. The system uses a deterministic fallback while preserving the application-selected action.

## Real Runtime Observability

`run_decision_iter()` exposes the actual decision stages used by the application:

1. input validated,
2. factors scored,
3. review gate checked,
4. bounded action selected,
5. explanation generated,
6. explanation guardrails checked,
7. result published.

`run_decision()` consumes the same iterator and returns the final result. The live activity feed is therefore derived from the real execution path rather than a separate demo-only animation.

## Synthetic Demo Stories

The public demo includes five fictional opportunities designed to exercise the full action space:

- strong fit → `PRIORITIZE`,
- moderate fit → `NURTURE`,
- weak fit → `DEFER`,
- high policy risk → `NEEDS_HUMAN_REVIEW`,
- missing decision data → `NEEDS_HUMAN_REVIEW`.

No real prospects, clients, advisor lists, firm strategy, or business-development records are included.

## Evaluation and Deployment

The upgraded project adds deterministic pytest coverage, a synthetic decision benchmark, public-repository hygiene checks, and a GitHub Actions production gate. Hugging Face deployment is allowed only after software tests and evaluation pass.

## Public-Demo Safety Boundary

- All demo data is fictional and synthetic.
- Visitor inputs are not persisted back into repository files.
- Runtime outputs are not committed as public logs.
- API keys and tokens are never stored in source.
- The private curriculum and private planning material are not part of the public demo corpus, tests, screenshots, or deployment artifacts.
- Repository hygiene tests scan tracked public text for private-source markers and common secret patterns.

## Local Setup

```bash
pip install -r requirements.txt
python app.py
```

Run tests:

```bash
python -m pytest -q
```

Run the deterministic batch example:

```bash
python scripts/run_agent.py
```

## Reusable Primitive

Agent 1 contributes the portfolio's foundational autonomy primitive:

> **Application code defines and enforces the decision boundary; models may assist inside that boundary but do not own consequential authority.**

Later agents reuse this principle for planning, memory, tools, workflows, multi-agent routing, verification, and distributed coordination.

## Limitations

- Scoring weights and thresholds are hand-designed for the synthetic demo.
- The benchmark measures policy consistency, not real-world conversion performance.
- The explanation guardrail is deterministic and intentionally narrow.
- No CRM or production identity/access system is connected.
- The public demo is decision support, not an automated system for making decisions about real people.

## Tech

Python, Pydantic, Gradio, optional Hugging Face Inference Provider via an OpenAI-compatible client, pytest, GitHub Actions, Hugging Face Spaces
