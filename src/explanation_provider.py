from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI

from src.decision_agent import DecisionOutput, EnterpriseOpportunity


DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"


class HuggingFaceExplanationProvider:
    """Optional LLM adapter that can explain, but never select, a decision."""

    def __init__(
        self,
        token: Optional[str] = None,
        model: str = DEFAULT_MODEL,
    ) -> None:
        self.token = token or os.getenv("HF_TOKEN")
        self.model = model

    @property
    def configured(self) -> bool:
        return bool(self.token)

    def __call__(
        self,
        opportunity: EnterpriseOpportunity,
        decision: DecisionOutput,
    ) -> str:
        if not self.token:
            raise RuntimeError("HF_TOKEN is not configured for optional LLM explanations.")

        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=self.token,
        )

        prompt = f"""
You explain a decision that application code has already made.
You may not change the action, imply authority to approve contracts, or make guarantees.

Fictional opportunity:
{opportunity.model_dump_json(indent=2)}

Application decision:
{decision.model_dump_json(indent=2)}

Write a concise business explanation in 2-4 sentences.
You MUST include the exact action token: {decision.recommended_action}
Do not add facts that are not present above.
""".strip()

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a bounded explanation layer. Application code owns the decision. "
                        "Explain the supplied result without changing it."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=220,
        )

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("The explanation provider returned an empty response.")
        return content.strip()
