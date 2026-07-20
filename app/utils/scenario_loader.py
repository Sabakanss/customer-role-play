from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel

SCENARIOS_DIR = Path(__file__).resolve().parent.parent / "scenarios"


class Scenario(BaseModel):
    id: str
    industry: str
    customer_role: str
    opening_line: str
    hidden_facts: list[str]
    constraints: list[str]
    review_criteria: list[str]


@lru_cache
def load_scenario(scenario_id: str = "sample_cafe") -> Scenario:
    """シナリオYAMLを読み込み、Scenarioとして返す。同一IDの結果はキャッシュする。"""
    path = SCENARIOS_DIR / f"{scenario_id}.yaml"
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Scenario(**data)
