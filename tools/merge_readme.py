"""Merge docs/readme/*.md, in filename order, into README.md."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README_DIR = ROOT / "docs" / "readme"
OUTPUT_PATH = ROOT / "README.md"

REQUIRED_FILES = [
    "01-overview.md",
    "02-data.md",
    "03-method.md",
    "04-results.md",
    "05-findings.md",
    "06-how-to-run.md",
    "07-team-and-credits.md",
]


def find_missing() -> list[str]:
    """Return the required readme section files that do not exist."""
    return [name for name in REQUIRED_FILES if not (README_DIR / name).exists()]


def merge() -> str:
    """Return the merged README text, sections joined by a blank line."""
    paths = sorted(README_DIR.glob("*.md"))
    sections = [path.read_text().strip() for path in paths]
    return "\n\n".join(sections) + "\n"


def main() -> int:
    """Write README.md, or print the missing files and return a non-zero code."""
    missing = find_missing()
    if missing:
        print(f"ERROR: missing readme sections: {', '.join(missing)}", file=sys.stderr)
        return 1
    OUTPUT_PATH.write_text(merge())
    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
