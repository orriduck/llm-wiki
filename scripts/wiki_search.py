import subprocess
import sys
from pathlib import Path

from wiki_path import get_wiki_path

query = " ".join(sys.argv[1:])
if not query:
    print("Usage: wiki_search.py <query>")
    sys.exit(1)

root = Path(get_wiki_path())
wiki_dir = root / "wiki"

# simple grep-based search
print(f"Searching for: {query}\n")

try:
    subprocess.run(["grep", "-rni", query, str(wiki_dir)], check=False)
except Exception as e:
    print("Search failed:", e)
