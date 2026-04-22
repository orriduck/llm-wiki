import os
import json
from pathlib import Path

def get_wiki_path():
    # 1. env var
    env = os.environ.get("LLM_WIKI_PATH")
    if env:
        return env

    # 2. repo root (assume script inside repo)
    repo_root = Path(__file__).resolve().parents[1]
    if (repo_root / "wiki").exists():
        return str(repo_root)

    # 3. Claude plugin fallback
    try:
        p = os.path.expanduser('~/.claude/plugins/installed_plugins.json')
        data = json.load(open(p))
        for key, entries in data.get('plugins', {}).items():
            if 'llm-wiki' in key:
                return entries[-1]['installPath']
    except Exception:
        pass

    raise RuntimeError("Cannot locate llm-wiki path")

if __name__ == "__main__":
    print(get_wiki_path())
