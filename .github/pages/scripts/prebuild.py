"""Copy external Markdown sources into docs/_imported/ for build-time inclusion.

Run before `mkdocs build` / `mkdocs serve`. The workflow runs this automatically;
locally, run `python scripts/prebuild.py` from the .github/pages/ directory.
"""

from pathlib import Path
import shutil

SCRIPT_DIR = Path(__file__).resolve().parent
PAGES_DIR = SCRIPT_DIR.parent
REPO_ROOT = PAGES_DIR.parent.parent
IMPORTED = PAGES_DIR / "docs" / "_imported"

SOURCES = [
    (REPO_ROOT / "git-sutras" / "README.md", "git-sutras.md"),
    (REPO_ROOT / "gh-sutras" / "README.md", "gh-sutras.md"),
    (REPO_ROOT / "python" / "AI-COMMIT-COMPARISON.md", "ai-commit-comparison.md"),
    (REPO_ROOT / "cursor" / "atomic-git-commits.md", "atomic-git-commits.md"),
]

HEADER = "<!-- auto-imported from {src} — do not edit here; edit the source. -->\n\n"


def main() -> int:
    IMPORTED.mkdir(parents=True, exist_ok=True)
    for src, dest_name in SOURCES:
        if not src.exists():
            print(f"warn: missing source {src}")
            continue
        dest = IMPORTED / dest_name
        rel_src = src.relative_to(REPO_ROOT).as_posix()
        body = src.read_text(encoding="utf-8")
        dest.write_text(HEADER.format(src=rel_src) + body, encoding="utf-8")
        print(f"copied {rel_src} -> {dest.relative_to(PAGES_DIR).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
