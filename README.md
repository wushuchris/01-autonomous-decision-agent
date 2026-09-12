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

## Live Demo

Hugging Face Space: https://huggingface.co/spaces/FlyingNunchucks/01-autonomous-decision-agent

The final live presentation was human-reviewed and approved after production validation of both deterministic and LLM-assisted explanation modes.

## Core Pattern

```text
Validate → Score → Review gate → Select bounded action → LLM explain → Guardrail → Publish
```

The design principle is:

> **Application code decides. The LLM explains. Guardrails decide what gets published.**

The original project shorthand still holds:

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
Deterministic or LLM-assisted explanation
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

### The LLM owns only

- wording of the explanation after the action has already been selected.

The model receives the already-selected action and supporting application data. It never receives authority to change the action, score, threshold, review gate, or approved action set.

If live inference is unavailable or the candidate explanation fails guardrail review, the system publishes a deterministic fallback while preserving the application-selected decision.

## Hugging Face Runtime Configuration

Agent 1 follows the same deployment/runtime separation used by later agents in the portfolio:

- `HF_DEPLOY_TOKEN` — GitHub repository secret used only for GitHub → Hugging Face deployment,
- `HF_TOKEN` — Hugging Face Space secret used only for runtime inference,
- `MODEL_ID` — Hugging Face Space variable that selects the live model,
- `HF_BASE_URL` — optional Hugging Face Space variable for the OpenAI-compatible router endpoint.

The production Space was live-validated with:

```text
MODEL_ID=Qwen/Qwen3.8-27B:ovhcloud
HF_BASE_URL=https://router.huggingface.co/v1
```

Model selection is therefore runtime configuration rather than a hardcoded production dependency.

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

The rebuilt project includes deterministic pytest coverage, adapter-level LLM tests with fake clients, a synthetic decision benchmark, public-repository hygiene checks, and a GitHub Actions production gate. Hugging Face deployment is allowed only after software tests and evaluation pass.

Final production validation on the sanitized public tree:

- **28 automated tests passed**
- **7/7 deterministic evaluation cases passed**
- all five synthetic scenarios produced their expected bounded actions
- unsafe explanation text was rejected and replaced with a deterministic fallback
- action-changing explanation text was rejected without changing the application-selected action
- model adapter routing, prompt authority boundaries, environment configuration, and empty-response handling are regression-tested without spending live inference credits in CI
- public-repository hygiene checks passed
- GitHub → Hugging Face deployment succeeded
- live LLM-assisted explanation succeeded using the configured `MODEL_ID`
- final centered 1080px business-first presentation passed human review

## Presentation Retrofit

Agent 1 originally began as a Colab-era engineering exercise. The production retrofit turned it into a portfolio-quality live system with:

- centered 1080px business-first layout,
- fictional enterprise-opportunity story,
- visible application-vs-model authority boundary,
- real stage-by-stage decision activity,
- explicit explanation-mode selector,
- readable light-theme controls and tab states,
- decision evidence and guardrail views underneath the business outcome,
- deterministic fallback when inference is unavailable,
- and live LLM-assisted explanation when runtime configuration is present.

Several Hugging Face / Gradio presentation issues discovered during live review—dropdown contrast, inline action labels, tab states, and ambiguous checkbox state—were converted into regression protections.

## Public-Demo Safety Boundary

- All demo data is fictional and synthetic.
- Visitor inputs are not persisted back into repository files.
- Runtime outputs are not committed as public logs.
- API keys and tokens are never stored in source.
- The private curriculum and private planning material are not part of the public demo corpus, tests, screenshots, or deployment artifacts.
- Repository hygiene tests scan tracked public text for private-source markers and common secret patterns.
- Generated output artifacts and compiled bytecode are excluded from the public project.
- The current public branch begins from a sanitized root commit rather than the original notebook-era history.
- The Hugging Face Space was created only after the sanitized branch and deployment gate were established.

## Local Setup

```bash
pip install -r requirements.txt
python app.py
```

For optional local LLM-assisted explanations:

```text
HF_TOKEN=your_runtime_token
MODEL_ID=your_model_id
HF_BASE_URL=https://router.huggingface.co/v1
```

Never commit real secret values.

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

Later agents reuse this principle for planning, memory, tools, workflows, multi-agent routing, verification, role coherence, and distributed coordination.

## Limitations

- Scoring weights and thresholds are hand-designed for the synthetic demo.
- The benchmark measures policy consistency, not real-world conversion performance.
- The explanation guardrail is deterministic and intentionally narrow.
- No CRM or production identity/access system is connected.
- Live LLM availability depends on the configured Hugging Face model/provider route.
- The public demo is decision support, not an automated system for making decisions about real people.

## Tech

Python, Pydantic, Gradio, Hugging Face Inference Providers, OpenAI-compatible API client, Qwen3.8, pytest, GitHub Actions, Hugging Face Spaces
