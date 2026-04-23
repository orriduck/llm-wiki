import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import setup_wiki


def make_content_repo(path: Path) -> None:
    (path / ".git").mkdir(parents=True)
    (path / "wiki").mkdir()
    (path / "index.md").write_text("# Index\n", encoding="utf-8")
    (path / "log.md").write_text("# Log\n", encoding="utf-8")


class SetupWikiTests(unittest.TestCase):
    def test_existing_content_repo_writes_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp) / "icloud" / "llm-wiki-content"
            make_content_repo(content)
            config_path = Path(tmp) / "config.json"

            result = setup_wiki.setup(
                "git@example.com:me/wiki.git",
                content,
                config_path=config_path,
            )

            self.assertEqual(result, content)
            config = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(config["content_path"], str(content))
            self.assertEqual(config["content_repo"], "git@example.com:me/wiki.git")

    def test_missing_content_repo_is_cloned(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp) / "icloud" / "llm-wiki-content"
            config_path = Path(tmp) / "config.json"

            def fake_run(command, cwd=None):
                self.assertEqual(command[0], "git")
                self.assertEqual(command[1], "clone")
                self.assertEqual(command[2], "git@example.com:me/wiki.git")
                self.assertEqual(command[3], str(content))
                make_content_repo(content)

            with patch.object(setup_wiki, "run", side_effect=fake_run):
                result = setup_wiki.setup(
                    "git@example.com:me/wiki.git",
                    content,
                    config_path=config_path,
                )

            self.assertEqual(result, content)
            self.assertTrue(config_path.exists())

    def test_existing_non_content_path_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp) / "icloud" / "llm-wiki-content"
            content.mkdir(parents=True)

            with self.assertRaises(RuntimeError) as ctx:
                setup_wiki.setup(
                    "git@example.com:me/wiki.git",
                    content,
                    config_path=Path(tmp) / "config.json",
                )

            self.assertIn("does not look like llm-wiki-content", str(ctx.exception))

    def test_default_path_requires_existing_obsidian_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"

            with patch.object(setup_wiki.Path, "home", return_value=home):
                with self.assertRaises(RuntimeError) as ctx:
                    setup_wiki.setup(config_path=Path(tmp) / "config.json")

            self.assertIn("Default Obsidian iCloud folder does not exist", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
