#!/usr/bin/env python3
"""Package this skill into an installable .skill bundle.

A .skill file is a zip archive containing a single top-level directory whose
name matches the skill name, with SKILL.md at its root.

Usage:
    python package.py            # writes asm-query-builder.skill
    python package.py -o out/    # writes out/asm-query-builder.skill
"""

import argparse
import sys
import zipfile
from pathlib import Path

SKILL_NAME = "asm-query-builder"

# Everything not needed at runtime.
EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "venv", ".idea", ".vscode"}
EXCLUDE_FILES = {"package.py", ".gitignore", ".DS_Store", "Thumbs.db"}
EXCLUDE_SUFFIXES = {".skill", ".pyc", ".swp"}


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return False
    if rel.name in EXCLUDE_FILES or rel.suffix in EXCLUDE_SUFFIXES:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o", "--output-dir", default=".", help="directory to write the bundle into"
    )
    args = parser.parse_args()

    root = Path(__file__).parent.resolve()

    if not (root / "SKILL.md").is_file():
        print("error: SKILL.md not found next to package.py", file=sys.stderr)
        return 1

    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle = out_dir / f"{SKILL_NAME}.skill"

    files = sorted(
        p for p in root.rglob("*") if p.is_file() and should_include(p, root)
    )

    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            arcname = Path(SKILL_NAME) / path.relative_to(root)
            zf.write(path, arcname)
            print(f"  added {arcname}")

    size_kb = bundle.stat().st_size / 1024
    print(f"\nwrote {bundle} ({size_kb:.0f} KB, {len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
