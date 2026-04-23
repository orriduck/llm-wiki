import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import wiki_path


def make_content_repo(path: Path) -> None:
    (path / "wiki").mkdir(parents=True)
    (path / "index.md").write_text("# Index\n", encoding="utf-8")
    (path / "log.md").write_text("# Log\n", encoding="utf-8")


class WikiPathTests(unittest.TestCase):
    def test_env_var_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp) / "content"
            make_content_repo(content)

            with patch.dict(os.environ, {"LLM_WIKI_PATH": str(content)}, clear=True):
                self.assertEqual(wiki_path.get_wiki_path(), str(content.resolve()))

    def test_config_file_is_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            content = Path(tmp) / "vault"
            make_content_repo(content)
            config_dir = home / ".llm-wiki"
            config_dir.mkdir(parents=True)
            (config_dir / "config.json").write_text(
                json.dumps({"content_path": str(content)}),
                encoding="utf-8",
            )

            with patch.dict(os.environ, {"HOME": str(home)}, clear=True):
                self.assertEqual(
                    wiki_path.get_wiki_path(config_path=config_dir / "config.json"),
                    str(content.resolve()),
                )

    def test_nearby_content_checkout_is_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = Path(tmp) / "llm-wiki"
            scripts = plugin / "scripts"
            scripts.mkdir(parents=True)
            content = Path(tmp) / "llm-wiki-content"
            make_content_repo(content)

            resolved = wiki_path.get_wiki_path(script_file=scripts / "wiki_path.py")

            self.assertEqual(resolved, str(content.resolve()))

    def test_missing_path_explains_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"

            with patch.dict(os.environ, {"HOME": str(home)}, clear=True):
                with self.assertRaises(RuntimeError) as ctx:
                    wiki_path.get_wiki_path(script_file=Path(tmp) / "plugin/scripts/wiki_path.py")

            self.assertIn("run /llm-wiki:setup", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
