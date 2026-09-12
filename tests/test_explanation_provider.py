from types import SimpleNamespace

import pytest

from src.decision_agent import decide_action
from src.explanation_provider import DEFAULT_MODEL, HuggingFaceExplanationProvider
import app


class FakeCompletions:
    def __init__(self, content: str):
        self.content = content
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))]
        )


class FakeClient:
    def __init__(self, content: str):
        self.completions = FakeCompletions(content)
        self.chat = SimpleNamespace(completions=self.completions)


def test_provider_can_use_injected_client_without_secret():
    opportunity = app.load_scenarios()["Northstar Systems"]
    decision = decide_action(opportunity)
    client = FakeClient(
        "Northstar Systems is assigned PRIORITIZE because the approved factors produced a strong bounded score."
    )
    provider = HuggingFaceExplanationProvider(client=client)

    explanation = provider(opportunity, decision)

    assert provider.configured is True
    assert "PRIORITIZE" in explanation
    assert client.completions.last_kwargs["model"] == DEFAULT_MODEL


def test_provider_prompt_preserves_application_authority():
    opportunity = app.load_scenarios()["Atlas Civic Network"]
    decision = decide_action(opportunity)
    client = FakeClient(
        "Atlas Civic Network is assigned NEEDS_HUMAN_REVIEW because the application review gate requires it."
    )
    provider = HuggingFaceExplanationProvider(client=client)

    provider(opportunity, decision)

    messages = client.completions.last_kwargs["messages"]
    prompt = "\n".join(message["content"] for message in messages)
    assert "Application code owns the decision" in prompt
    assert "The action is immutable" in prompt
    assert "NEEDS_HUMAN_REVIEW" in prompt
    assert "Atlas Civic Network" in prompt


def test_provider_label_discloses_model_and_hugging_face():
    provider = HuggingFaceExplanationProvider(token="synthetic-test-token")
    assert DEFAULT_MODEL in provider.provider_label
    assert "Hugging Face Inference Providers" in provider.provider_label


def test_provider_rejects_empty_response():
    opportunity = app.load_scenarios()["Juniper Works"]
    decision = decide_action(opportunity)
    provider = HuggingFaceExplanationProvider(client=FakeClient("   "))

    with pytest.raises(RuntimeError, match="empty response"):
        provider(opportunity, decision)
