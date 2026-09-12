# Guardrails — Agent 1 Bounded Decision System

## Design Principle

> **Rules decide. The LLM explains. Guardrails review.**

The explanation model is deliberately downstream of the decision. It cannot alter the score, thresholds, action set, or mandatory-review status.

## Decision Guardrails

The application enforces:

- a fixed four-action output space,
- structured Pydantic input validation,
- deterministic factor scoring,
- mandatory review for high policy risk,
- mandatory review when commercial-potential data is missing.

A high score cannot override a mandatory review condition.

## Explanation Guardrails

Candidate explanation text is rejected if it:

- fails to preserve the exact selected action,
- makes guarantees or outcome promises,
- claims authority to sign/approve contracts or commit the fictional company,
- suggests bypassing required human review.

If rejected, a deterministic explanation is published instead.

## Provider Failure

The optional Hugging Face explanation provider is not a control dependency. If the provider is unavailable, misconfigured, or returns an error, the application falls back to the deterministic explanation path.

## Public Safety

The public repository and demo must contain only synthetic data. Do not include real prospects, clients, private sales/distribution strategy, curriculum files, private planning notes, tokens, API keys, or generated logs containing sensitive material.

The CI suite includes a hygiene scan for private-source markers and common credential patterns.

## Limitations

These guardrails are intentionally narrow and educational. A production system would require authenticated users, policy configuration, stronger content controls, monitoring, audit retention rules, and domain-specific legal/compliance review.
