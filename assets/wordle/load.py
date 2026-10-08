import os
import sys
from pathlib import Path
import urllib.request

TARGETS_URL = "https://gist.githubusercontent.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b/raw/wordle-answers-alphabetical.txt"
VALID_GUESSES_URL = "https://gist.githubusercontent.com/cfreshman/cdcdf777450c5b5301e439061d29694c/raw/wordle-allowed-guesses.txt"

def _resolve_resource_path(relative_path: str) -> Path:
    """Resolve packaged resources for both source runs and PyInstaller bundles."""
    source_root = Path(__file__).resolve().parents[2]
    bundled_root = Path(getattr(sys, "_MEIPASS", source_root))

    normalized_parts = relative_path.replace("\\", "/").split("/")
    bundled_candidate = bundled_root.joinpath(*normalized_parts)
    if bundled_candidate.exists():
        return bundled_candidate

    return source_root.joinpath(*normalized_parts)


def load_word_file(relative_path: str, url: str) -> list[str]:
    """Downloads word list in dev mode if missing, then loads uppercase strings."""
    file_path = _resolve_resource_path(relative_path)

    if not file_path.exists():
        if getattr(sys, "frozen", False):
            raise FileNotFoundError(f"Required resource missing in packaged app: {file_path}")

        file_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {relative_path}...")
        urllib.request.urlretrieve(url, str(file_path))

    with file_path.open("r", encoding="utf-8") as f:
        return [line.strip().upper() for line in f if len(line.strip()) == 5]

# Load lists into memory
TARGET_WORDS = load_word_file("assets/wordle/targets.txt", TARGETS_URL)
VALID_GUESSES = load_word_file("assets/wordle/valid_guesses.txt", VALID_GUESSES_URL)

# Full dictionary for O(1) guess validation lookups
FULL_DICTIONARY = set(TARGET_WORDS).union(set(VALID_GUESSES))