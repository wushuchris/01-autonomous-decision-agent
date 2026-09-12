import app


def test_demo_builds_without_provider_secret():
    assert app.demo is not None
    assert len(app.load_scenarios()) == 5


def test_business_presentation_is_centered_and_bounded():
    assert "max-width: 1080px" in app.APP_CSS
    assert "without letting the model invent the action space" in app.HERO_HTML
    assert "Application code controls" in app.BUSINESS_STORY_HTML
    assert "The optional LLM can" in app.BUSINESS_STORY_HTML


def test_tab_navigation_has_explicit_light_states():
    assert '[role="tab"]:hover' in app.APP_CSS
    assert '[role="tab"][aria-selected="true"]' in app.APP_CSS
    assert "background: #eef2ff" in app.APP_CSS


def test_dropdown_and_action_labels_have_explicit_light_contrast():
    assert '[role="listbox"]' in app.APP_CSS
    assert '[role="option"]' in app.APP_CSS
    assert '#scenario-picker input' in app.APP_CSS
    assert '.gradio-container code' in app.APP_CSS
    assert '-webkit-text-fill-color: #0f172a' in app.APP_CSS
    assert '-webkit-text-fill-color: #312e81' in app.APP_CSS


def test_llm_explanation_is_the_default_live_mode():
    assert app.explanation_mode.value == app.LLM_MODE
    provider = app.HuggingFaceExplanationProvider(token="test")
    assert "Hugging Face Inference Providers" in provider.provider_label
    assert app.DEFAULT_MODEL in provider.provider_label


def test_explanation_mode_status_is_explicit():
    assert "LLM ON" in app.explanation_mode_status(app.LLM_MODE)
    assert app.DEFAULT_MODEL in app.explanation_mode_status(app.LLM_MODE)
    assert "LLM OFF" in app.explanation_mode_status(app.DETERMINISTIC_MODE)


def test_default_scenario_preview_is_explicitly_synthetic():
    preview = app.scenario_summary("Northstar Systems")
    assert "Synthetic scenario" in preview
    assert "PRIORITIZE" in preview


def test_stream_decision_exposes_real_runtime_stages():
    frames = list(app.stream_decision("Northstar Systems", app.DETERMINISTIC_MODE))
    assert len(frames) == 7
    assert "RUNNING" in frames[0][0]
    combined = "".join(frame[0] for frame in frames)
    assert "Approved factors scored" in combined
    assert "Human-review gate checked" in combined
    assert "Bounded action selected" in combined
    assert "Explanation guardrails checked" in combined
    assert "COMPLETE" in frames[-1][0]
    assert "PRIORITIZE" in frames[-1][1]
    assert "Deterministic explanation mode" in frames[-1][3]


def test_human_review_story_visibly_overrides_score():
    frames = list(app.stream_decision("Atlas Civic Network", app.DETERMINISTIC_MODE))
    assert "NEEDS_HUMAN_REVIEW" in frames[-1][1]
    assert "High policy risk" in frames[-1][1]
