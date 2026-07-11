"""Install agentic-framework assets into Codex and Claude directories."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import setup_code_review


CONTENT_DIRS = ("skills", "agents", "commands")
CLIENT_DIRS = (".codex", ".claude")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Install agentic-framework skills, agents, and commands into "
            "the specified directory's .codex and .claude folders."
        )
    )
    parser.add_argument(
        "target_dir",
        type=Path,
        help="Directory that contains or will contain .codex and .claude.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help=(
            "Source agentic-framework directory. "
            "Defaults to this script's parent framework directory."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite changed target files. By default, conflicts fail.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned copy operations without writing files.",
    )
    parser.add_argument(
        "--skip-code-review",
        action="store_true",
        help=(
            "Skip setting up the open-code-review (ocr) environment. By "
            "default the CLI is installed if missing and a rule.json written."
        ),
    )
    return parser.parse_args(argv)


def missing_content_dirs(source_dir: Path) -> Iterable[Path]:
    """Yield required source directories that do not exist."""
    for content_dir in CONTENT_DIRS:
        path = source_dir / content_dir
        if not path.is_dir():
            yield path


def conflicting_paths(source_dir: Path, target_dir: Path) -> Iterable[Path]:
    """Yield target paths that would be overwritten with different content."""
    if not target_dir.exists():
        return

    for source_path in source_dir.rglob("*"):
        target_path = target_dir / source_path.relative_to(source_dir)
        if not target_path.exists():
            continue
        if source_path.is_dir():
            if target_path.is_file():
                yield target_path
            continue
        if target_path.is_dir():
            yield target_path
            continue
        if source_path.read_bytes() != target_path.read_bytes():
            yield target_path


def copy_tree(
    source_dir: Path,
    target_dir: Path,
    dry_run: bool,
    force: bool,
) -> None:
    """Copy one directory tree, preserving existing unrelated target files."""
    conflicts = list(conflicting_paths(source_dir, target_dir))
    if conflicts and not force:
        conflict_list = "\n".join(str(path) for path in conflicts[:20])
        raise FileExistsError(
            "Refusing to overwrite changed target files. "
            f"Use --force to overwrite:\n{conflict_list}"
        )

    if dry_run:
        print(f"[dry-run] copy {source_dir} -> {target_dir}")
        return

    target_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
    print(f"copied {source_dir} -> {target_dir}")


def install(
    source_dir: Path,
    target_root: Path,
    dry_run: bool,
    force: bool,
) -> None:
    """Install framework content into both client configuration folders."""
    source_dir = source_dir.resolve()
    target_root = target_root.resolve()

    missing_dirs = list(missing_content_dirs(source_dir))
    if missing_dirs:
        missing = "\n".join(str(path) for path in missing_dirs)
        raise FileNotFoundError(
            f"Missing required source directories:\n{missing}"
        )

    for client_dir in CLIENT_DIRS:
        for content_dir in CONTENT_DIRS:
            copy_tree(
                source_dir / content_dir,
                target_root / client_dir / content_dir,
                dry_run,
                force,
            )


def main(argv: Sequence[str]) -> int:
    """Run the installer."""
    args = parse_args(argv)
    install(args.source, args.target_dir, args.dry_run, args.force)
    if not args.skip_code_review:
        setup_code_review.setup(
            args.target_dir,
            force=args.force,
            dry_run=args.dry_run,
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
