import os
import json
from pathlib import Path


CONFIG_PATH = Path("~/.llm-wiki/config.json")
REQUIRED_CONTENT_FILES = ("wiki", "index.md", "log.md")


def is_content_repo(path):
    root = Path(path).expanduser()
    return all((root / name).exists() for name in REQUIRED_CONTENT_FILES)


def _read_config(config_path=CONFIG_PATH):
    try:
        return json.loads(Path(config_path).expanduser().read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid llm-wiki config: {config_path}") from exc


def get_wiki_path(script_file=None, config_path=CONFIG_PATH):
    # 1. env var
    env = os.environ.get("LLM_WIKI_PATH")
    if env and is_content_repo(env):
        return str(Path(env).expanduser().resolve())

    # 2. persistent setup config
    config = _read_config(config_path)
    configured = config.get("content_path")
    if configured and is_content_repo(configured):
        return str(Path(configured).expanduser().resolve())

    # 3. nearby development checkout
    script_path = Path(script_file or __file__).resolve()
    repo_root = script_path.parents[1]
    nearby_candidates = [
        repo_root.parent / "llm-wiki-content",
        repo_root / "llm-wiki-content",
    ]
    for candidate in nearby_candidates:
        if is_content_repo(candidate):
            return str(candidate.resolve())

    # 4. common Obsidian/iCloud locations
    home = Path.home()
    common_candidates = [
        home / "Library/Mobile Documents/iCloud~md~obsidian/Documents/llm-wiki-content",
        home / "Library/Mobile Documents/iCloud~md~obsidian/Documents/llm-wiki",
        home / "Documents/Obsidian/llm-wiki-content",
        home / "Devs/llm-wiki-content",
    ]
    for candidate in common_candidates:
        if is_content_repo(candidate):
            return str(candidate.resolve())

    raise RuntimeError(
        "Cannot locate llm-wiki content repo. run /llm-wiki:setup or set "
        "LLM_WIKI_PATH to your llm-wiki-content checkout."
    )

if __name__ == "__main__":
    print(get_wiki_path())
