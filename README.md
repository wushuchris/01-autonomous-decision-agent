# Autonomous Decision-Making Agent

## Overview

This project builds an autonomous decision-making agent that evaluates financial advisor leads and recommends a bounded next action.

The agent is designed around a key safety principle:

**Rules decide. The LLM explains.**

The rule-based system makes the actual decision using transparent scoring logic and guardrails. A Hugging Face-hosted LLM is used only to generate a clearer business-facing explanation of the decision.

## Use Case

The agent evaluates advisor leads for business development prioritization.

It recommends one of four approved actions:

- `HIGH_PRIORITY_FOLLOW_UP`
- `NURTURE`
- `LOW_PRIORITY`
- `NEEDS_HUMAN_REVIEW`

The agent does not recommend investments, promise performance, or replace human judgment. It helps prioritize leads consistently and flags cases that require human review.

## Architecture

The agent workflow is:

```text
Advisor Lead Input
→ Pydantic Validation
→ Rule-Based Scoring
→ Guardrail Check
→ Bounded Decision
→ Hugging Face LLM Explanation
→ Explanation Guardrail Review
→ Decision Log Export
```

## Core Components

### Input Schema

The `AdvisorLead` schema defines the structured information the agent can evaluate.

### Decision Output Schema

The `DecisionOutput` schema defines the structured decision returned by the agent.

### Scoring Engine

The scoring engine assigns points based on AUM fit, interest level, model marketplace fit, recent engagement, and compliance risk.

### LLM Explanation Layer

The Hugging Face LLM does not make the decision. It only explains the structured decision in professional business language.

### Guardrail Checker

The explanation guardrail checker scans the LLM-generated explanation for potentially risky language, such as performance promises, investment recommendations, and exaggerated claims.

### Evaluation Suite

The notebook includes evaluation cases for high-quality leads, missing AUM, high compliance risk, low-priority leads, and nurture candidates.

### Batch Runner

The batch runner processes multiple leads and creates a summary table.

## Example Output

```json
{
  "recommended_action": "HIGH_PRIORITY_FOLLOW_UP",
  "confidence": 0.85,
  "reasoning_summary": "The lead received a score of 11. The recommended action is HIGH_PRIORITY_FOLLOW_UP based on fit, interest, risk, and recent engagement.",
  "key_factors": [
    "Low compliance risk.",
    "Strong AUM fit.",
    "High stated interest.",
    "Uses model marketplace or platform access.",
    "Recent workshop engagement.",
    "Recent interaction suggests active curiosity."
  ],
  "risks_or_uncertainties": [],
  "human_review_required": false
}
```

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Required packages:

- pydantic
- pandas
- matplotlib
- openai

The project uses the OpenAI-compatible Hugging Face router client, so the `openai` package is included even though the LLM provider is Hugging Face.

## Hugging Face Token

This notebook expects a Hugging Face token stored in Colab Secrets as:

```text
HF_01_Agent
```

The token should have permission for:

```text
Inference → Make calls to Inference Providers
```

The notebook loads the secret and stores it as:

```text
HF_TOKEN
```

for compatibility with Hugging Face tooling.

## Limitations

This is a prototype agent, not a production system.

Current limitations include:

- scoring weights are hand-coded
- evaluation set is small
- no historical conversion data
- no CRM integration
- no persistent database
- guardrail checker is keyword-based
- no human feedback loop yet

## Production Upgrade Path

A production version could add:

- larger evaluation dataset
- historical lead conversion outcomes
- configurable scoring thresholds
- CRM integration
- persistent logging
- human approval workflow
- compliance review queue
- dashboard reporting
- improved guardrail checks
- model/provider fallback logic
- monitoring and regression testing

## Key Lesson

The main lesson from this project is that useful autonomous agents should be bounded, structured, testable, and auditable.

The safest design pattern for this project is:

```text
Rules decide. The LLM explains.
```
