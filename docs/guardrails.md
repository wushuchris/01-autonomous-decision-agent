# Guardrails: Autonomous Decision-Making Agent

## Purpose

This document explains the guardrails used in the Autonomous Decision-Making Agent.

The agent evaluates financial advisor leads and recommends a bounded next action.

The core design principle is:

```text
Rules decide. The LLM explains.
```

The agent uses rules to make the decision and uses an LLM only to explain the decision.

## Why Guardrails Matter

Autonomous agents can create risk if they are allowed to make open-ended decisions.

This project limits the agent's autonomy by:

- restricting the action set
- using structured input schemas
- using structured output schemas
- escalating risky cases to human review
- preventing the LLM from changing the decision
- checking explanations for risky language
- saving decision logs for auditability

## Allowed Actions

The agent can only recommend one of four actions:

- `HIGH_PRIORITY_FOLLOW_UP`
- `NURTURE`
- `LOW_PRIORITY`
- `NEEDS_HUMAN_REVIEW`

The agent is not allowed to invent new actions.

## Decision Guardrails

The rule-based engine applies several decision guardrails.

### High Compliance Risk

If `compliance_risk` is high, the agent automatically recommends:

```text
NEEDS_HUMAN_REVIEW
```

Reason: high-risk cases should not be handled autonomously.

### Missing AUM

If AUM is missing, the agent recommends:

```text
NEEDS_HUMAN_REVIEW
```

Reason: AUM is a key input for lead prioritization, and missing critical data creates uncertainty.

### Low Interest or Low Fit

If a lead has low interest, limited AUM fit, and no strong engagement signals, the agent may recommend:

```text
LOW_PRIORITY
```

Reason: the agent should help prioritize limited business development time.

## LLM Explanation Guardrails

The LLM explanation layer is not allowed to:

- change the recommended action
- recommend specific investments
- promise investment performance
- imply guaranteed results
- make exaggerated claims
- use high-pressure sales language

The LLM should:

- explain the decision clearly
- preserve the recommendation
- identify risks and uncertainties
- use professional business language
- explain why human review is needed when applicable

## Keyword-Based Explanation Checks

The prototype includes a lightweight keyword-based checker.

It flags language related to:

### Performance Promises

Examples:

- guaranteed
- will outperform
- superior returns
- risk-free
- certain return

### Investment Recommendations

Examples:

- buy
- sell
- invest in
- allocate to
- recommend this fund

### Exaggerated Claims

Examples:

- best-in-class
- unmatched
- cannot fail
- perfect fit
- sure thing
- must act immediately

## Limitations of the Guardrail Checker

The current guardrail checker is intentionally simple.

It may produce false positives or false negatives.

For example:

- It may flag innocent uses of certain words.
- It may miss risky language that uses different wording.
- It does not replace compliance review.
- It does not understand the full legal context of advisor communications.

## Production Improvements

A production guardrail system could add:

- compliance-reviewed phrase libraries
- semantic risk classification
- model-based safety review
- human approval queue
- audit dashboards
- CRM notes review
- role-based permissions
- escalation routing
- record retention policies
- versioned guardrail rules

## Key Lesson

The goal of guardrails is not to eliminate all risk.

The goal is to make agent behavior more bounded, visible, reviewable, and correctable.

For this project, the safest pattern is:

```text
Rules decide. The LLM explains. Guardrails review.
```
