# Code developed using ChatGPT (ChatGPT, 2026) as a paired programmer.

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.append(str(SRC_DIR))

from decision_agent import (
    AdvisorLead,
    decide_action,
    generate_business_explanation,
    check_explanation_guardrails,
    summarize_batch_results
)


def run_agent_on_lead(lead: AdvisorLead) -> dict:
    """
    Run the autonomous decision-making agent on a single lead.

    This standalone script uses the non-LLM explanation layer so it can
    run without API keys.
    """

    decision = decide_action(lead)
    explanation = generate_business_explanation(lead, decision)
    guardrail_check = check_explanation_guardrails(
        explanation=explanation,
        expected_action=decision.recommended_action
    )

    return {
        "lead": lead.model_dump(),
        "decision": decision.model_dump(),
        "business_explanation": explanation,
        "guardrail_check": guardrail_check
    }


def main() -> None:
    """
    Load sample leads, run the agent, and save output artifacts.
    """

    input_path = PROJECT_ROOT / "data" / "sample_leads.json"
    output_dir = PROJECT_ROOT / "outputs"
    output_json_path = output_dir / "batch_decision_log.json"
    output_csv_path = output_dir / "batch_decision_summary.csv"

    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(
            f"sample_leads.json not found at {input_path}."
        )

    with input_path.open("r", encoding="utf-8") as file:
        raw_leads = json.load(file)

    leads = [AdvisorLead(**lead) for lead in raw_leads]

    batch_results = [run_agent_on_lead(lead) for lead in leads]

    batch_log = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "agent_name": "Autonomous Decision-Making Agent",
        "agent_version": "2.0-non-llm-runner",
        "record_count": len(batch_results),
        "results": batch_results
    }

    with output_json_path.open("w", encoding="utf-8") as file:
        json.dump(batch_log, file, indent=2)

    summary_rows = summarize_batch_results(batch_results)
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(output_csv_path, index=False)

    print(f"Processed {len(batch_results)} leads.")
    print(f"Saved full decision log to: {output_json_path}")
    print(f"Saved summary CSV to: {output_csv_path}")


if __name__ == "__main__":
    main()
