---
description: Clone or connect the llm-wiki-content repository in the Obsidian iCloud folder and save the content path for all llm-wiki skills.
---

Set up this machine for llm-wiki.

## Purpose

The installed plugin repository is tooling only. The durable notes live in a separate `llm-wiki-content` Git repository, ideally inside Obsidian's iCloud Drive folder so Obsidian and all agents use the same vault.

## Steps

1. Confirm Obsidian is installed and iCloud Drive is enabled if the user wants the default iCloud location.

2. Parse optional arguments:
   - No arguments: use `git@github.com:orriduck/llm-wiki-content.git` and the default Obsidian iCloud path.
   - One argument: treat it as the content repo Git URL.
   - Two arguments: treat them as content repo Git URL and target checkout path.

3. Run setup:
   ```bash
   python3 scripts/setup_wiki.py $ARGUMENTS
   ```

4. Validate the resolved wiki path:
   ```bash
   python3 scripts/wiki_path.py
   ```

5. Report:
   - content repo path
   - config file: `~/.llm-wiki/config.json`
   - Obsidian vault path to open

If setup fails because the default iCloud folder is missing, ask the user to install/open Obsidian once or rerun setup with an explicit target path.
