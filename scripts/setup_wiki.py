import argparse
import json
import subprocess
from pathlib import Path

from wiki_path import CONFIG_PATH, is_content_repo


DEFAULT_REPO = "git@github.com:orriduck/llm-wiki-content.git"


def default_content_path():
    return (
        Path.home()
        / "Library/Mobile Documents/iCloud~md~obsidian/Documents/llm-wiki-content"
    )


def run(command, cwd=None):
    subprocess.run(command, cwd=cwd, check=True)


def write_config(content_path, content_repo, config_path=CONFIG_PATH):
    config_path = Path(config_path).expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config = {
        "content_path": str(Path(content_path).expanduser()),
        "content_repo": content_repo,
    }
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def setup(content_repo=DEFAULT_REPO, content_path=None, config_path=CONFIG_PATH):
    using_default_path = content_path is None
    target = Path(content_path).expanduser() if content_path else default_content_path()

    if target.exists():
        if not is_content_repo(target):
            raise RuntimeError(
                f"{target} exists but does not look like llm-wiki-content "
                "(expected wiki/, index.md, and log.md)."
            )
    else:
        if using_default_path and not target.parent.exists():
            raise RuntimeError(
                "Default Obsidian iCloud folder does not exist. Install/open "
                "Obsidian with iCloud Drive enabled, or pass an explicit target path."
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", content_repo, str(target)])

    if not (target / ".git").exists():
        raise RuntimeError(f"{target} is not a git checkout.")

    write_config(target, content_repo, config_path=config_path)
    return target


def parse_args():
    parser = argparse.ArgumentParser(
        description="Clone/connect llm-wiki-content and save its path."
    )
    parser.add_argument(
        "content_repo",
        nargs="?",
        default=DEFAULT_REPO,
        help=f"Git URL for the content repo. Default: {DEFAULT_REPO}",
    )
    parser.add_argument(
        "content_path",
        nargs="?",
        default=None,
        help="Target checkout path. Defaults to the Obsidian iCloud Documents folder.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    path = setup(args.content_repo, args.content_path)
    print(path)
