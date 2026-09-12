from __future__ import annotations

import os
from typing import Any, Optional

from openai import OpenAI

from src.decision_agent import DecisionOutput, EnterpriseOpportunity


DEFAULT_BASE_URL = "https://router.huggingface.co/v1"


class HuggingFaceExplanationProvider:
    """LLM adapter that may explain, but never select, a bounded decision."""

    def __init__(
        self,
        token: Optional[str] = None,
        model_id: Optional[str] = None,
        base_url: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> None:
        self.token = (token or os.getenv("HF_TOKEN") or "").strip()
        self.model_id = (model_id or os.getenv("MODEL_ID") or "").strip()
        self.base_url = (base_url or os.getenv("HF_BASE_URL") or DEFAULT_BASE_URL).strip()
        self._client = client

    @property
    def configured(self) -> bool:
        return bool(self._client or (self.token and self.model_id))

    @property
    def configuration_issue(self) -> Optional[str]:
        if self._client is not None:
            return None
        missing = []
        if not self.token:
            missing.append("HF_TOKEN secret")
        if not self.model_id:
            missing.append("MODEL_ID variable")
        if missing:
            return "Missing " + " and ".join(missing) + "."
        return None

    @property
    def provider_label(self) -> str:
        model = self.model_id or "MODEL_ID not configured"
        return f"{model} via Hugging Face Inference Providers"

    def _get_client(self):
        if self._client is not None:
            return self._client
        if self.configuration_issue:
            raise RuntimeError(self.configuration_issue)
        return OpenAI(
            base_url=self.base_url,
            api_key=self.token,
            timeout=30.0,
        )

    def __call__(
        self,
        opportunity: EnterpriseOpportunity,
        decision: DecisionOutput,
    ) -> str:
        if not self.model_id:
            raise RuntimeError("MODEL_ID is not configured for LLM explanations.")

        client = self._get_client()

        prompt = f"""
You explain a bounded business decision that application code has already made.
The action is immutable. You may not change it, recommend a different action,
imply authority to approve contracts, make guarantees, or invent facts.

Fictional opportunity:
{opportunity.model_dump_json(indent=2)}

Application decision:
{decision.model_dump_json(indent=2)}

Write a concise business explanation in 2-4 sentences.
You MUST include the exact action token: {decision.recommended_action}
Use only facts contained in the supplied opportunity and application decision.
""".strip()

        response = client.chat.completions.create(
            model=self.model_id,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a non-authoritative explanation layer. Application code owns the "
                        "decision, action space, score, thresholds, and human-review requirements. "
                        "Explain the supplied result without changing or extending it."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=220,
        )

        content = response.choices[0].message.content
        if not content or not content.strip():
            raise RuntimeError("The explanation provider returned an empty response.")
        return content.strip()
