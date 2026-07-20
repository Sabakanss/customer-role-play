from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


@lru_cache
def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(PROMPTS_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_prompt(template_name: str, **context: object) -> str:
    """prompts/配下のテンプレートをJinja2で描画する。"""
    template = _environment().get_template(template_name)
    return template.render(**context)
