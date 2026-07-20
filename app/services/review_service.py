from sqlalchemy.orm import Session as DBSession

from app.llm.factory import get_llm_client
from app.repositories import review_repository
from app.services.prompt_service import build_review_system_prompt
from app.utils.scenario_loader import load_scenario


def review_proposal(db: DBSession, session_id: str, proposal: str) -> str:
    """改善提案をCustomer Agentにレビューさせ、結果をDBに保存して返す。"""
    scenario = load_scenario()
    system_prompt = build_review_system_prompt(scenario)

    client = get_llm_client()
    result = client.chat(system_prompt, [{"role": "user", "content": proposal}])

    review_repository.add_review(db, session_id, proposal, result)
    return result
