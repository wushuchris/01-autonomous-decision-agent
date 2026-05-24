# Architecture: Autonomous Decision-Making Agent

## Purpose

This agent evaluates financial advisor leads and recommends a bounded next action.

The agent is designed around a simple but important principle:

```text
Rules decide. The LLM explains.
```

The rule-based logic makes the decision. The LLM is used only to improve the quality of the explanation.

## High-Level Workflow

```text
Advisor Lead Input
→ Input Validation
→ Scoring Engine
→ Guardrail Check
→ Bounded Decision
→ Explanation Layer
→ Explanation Guardrail Review
→ Decision Log
→ Batch Summary
```

## 1. Input Validation

The agent uses a Pydantic schema called `AdvisorLead`.

This schema defines the information the agent can evaluate:

- advisor name
- firm type
- assets under management
- interest level
- model marketplace usage
- current equity manager
- client base
- recent interaction
- compliance risk

Using a schema helps keep the input structured and predictable.

## 2. Scoring Engine

The scoring engine evaluates the lead using deterministic rules.

The agent assigns points based on:

- AUM fit
- interest level
- model marketplace usage
- recent engagement
- compliance risk

The scoring engine also identifies risks and missing information.

## 3. Guardrail-Based Escalation

Some inputs trigger human review automatically.

For example:

- high compliance risk
- missing AUM

This is important because the agent should not force a decision when uncertainty or risk is too high.

## 4. Bounded Decision

The agent can only recommend one of four approved actions:

- `HIGH_PRIORITY_FOLLOW_UP`
- `NURTURE`
- `LOW_PRIORITY`
- `NEEDS_HUMAN_REVIEW`

This prevents the agent from inventing actions outside the intended workflow.

## 5. Explanation Layer

The notebook version includes a Hugging Face LLM explanation layer.

The LLM receives:

- the advisor lead
- the structured decision
- key factors
- risks and uncertainties

The LLM is instructed not to change the recommendation.

Its only role is to explain the decision clearly.

The standalone `run_agent.py` script uses a non-LLM fallback explanation so that the project can run without an API token.

## 6. Explanation Guardrail Review

The explanation guardrail checker scans generated explanations for risky language.

It looks for language that may suggest:

- performance promises
- specific investment recommendations
- exaggerated claims

This is not a complete compliance system. It is a lightweight safety screen.

## 7. Decision Logging

The project saves decision results to JSON.

The log includes:

- timestamp
- agent name
- agent version
- lead input
- structured decision
- explanation
- guardrail check

This creates a simple audit trail.

## 8. Batch Processing

The batch runner can process multiple leads.

It creates:

- a full JSON decision log
- a CSV summary table

The summary table is useful for business review and prioritization.

## Design Benefits

This architecture is:

- bounded
- explainable
- testable
- auditable
- easy to improve
- safer than open-ended LLM decision-making

## Future Improvements

A production system could add:

- real CRM integration
- persistent database logging
- human approval queues
- historical lead conversion data
- configurable scoring weights
- more advanced guardrails
- model fallback logic
- dashboard reporting
- regression testing
