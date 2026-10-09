from __future__ import annotations

from pathlib import Path
from typing import TypedDict

ROOT_DIR = Path(__file__).resolve().parents[1]


class AppSpec(TypedDict):
    display_name: str
    entry_script: str
    asset_dir: str


APP_REGISTRY: dict[str, AppSpec] = {
    "Wordle by Chinmay Mokashi": {
        "display_name": "Wordle by Chinmay Mokashi",
        "entry_script": "wordle_ui.py",
        "asset_dir": "assets/wordle",
    },
    "Sudoku by Chinmay Mokashi": {
        "display_name": "Sudoku by Chinmay Mokashi",
        "entry_script": "sudoku.py",
        "asset_dir": "assets/sudoku",
    },
}

DEFAULT_APP_NAME = "Wordle by Chinmay Mokashi"


def list_app_names() -> list[str]:
    return list(APP_REGISTRY.keys())


def resolve_app_name(app_name: str | None) -> str:
    candidate = (app_name or "").strip()
    if not candidate:
        return DEFAULT_APP_NAME

    if candidate in APP_REGISTRY:
        return candidate

    normalized = candidate.casefold()
    exact_matches = [name for name in APP_REGISTRY if name.casefold() == normalized]
    if exact_matches:
        return exact_matches[0]

    prefix_matches = [name for name in APP_REGISTRY if name.casefold().startswith(normalized)]
    if prefix_matches:
        return prefix_matches[0]

    raise ValueError(
        f"Unknown app '{app_name}'. Available apps: {', '.join(list_app_names())}"
    )


def resolve_app_spec(app_name: str | None = None) -> AppSpec:
    name = resolve_app_name(app_name)
    spec = APP_REGISTRY[name].copy()
    spec["entry_script"] = spec["entry_script"].replace("\\", "/")
    spec["asset_dir"] = spec["asset_dir"].replace("\\", "/")
    return spec


if __name__ == "__main__":
    import json
    import sys

    selected = sys.argv[1] if len(sys.argv) > 1 else None
    if selected in {"--list", "-l", "list"}:
        print(json.dumps(list_app_names()))
    else:
        print(json.dumps(resolve_app_spec(selected)))
