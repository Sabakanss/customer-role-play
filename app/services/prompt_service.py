from app.utils.prompt_loader import render_prompt
from app.utils.scenario_loader import Scenario, load_scenario


def build_customer_system_prompt(scenario: Scenario | None = None) -> str:
    """ヒアリング対応（Customer Agent）用のシステムプロンプトを組み立てる。"""
    scenario = scenario or load_scenario()
    return render_prompt("customer.md", scenario=scenario)


def build_review_system_prompt(scenario: Scenario | None = None) -> str:
    """提案レビュー用のシステムプロンプトを組み立てる。"""
    scenario = scenario or load_scenario()
    return render_prompt("review.md", scenario=scenario)
