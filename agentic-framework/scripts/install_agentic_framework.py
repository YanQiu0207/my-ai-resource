"""Install agentic-framework assets into Codex and Claude directories."""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from typing import Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import setup_code_review


CONTENT_DIRS = ("skills", "agents", "commands")
CLIENT_DIRS = (".codex", ".claude")


def _path_exists(path: Path) -> bool:
    """Return whether a path exists without following a broken link."""
    return os.path.lexists(path)


def _is_directory_link(path: Path) -> bool:
    """Return whether path is a directory symlink or Windows junction."""
    if path.is_symlink():
        return path.is_dir()
    is_junction = getattr(path, "is_junction", None)
    if is_junction and is_junction():
        return True
    try:
        attributes = path.lstat().st_file_attributes
    except (AttributeError, OSError):
        return False
    return path.is_dir() and bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def _remove_path(path: Path) -> None:
    """Remove a path without traversing directory links."""
    if path.is_symlink():
        path.unlink()
    elif _is_directory_link(path):
        path.rmdir()
    elif path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def _restore_directory_contents(source: Path, target: Path) -> None:
    """Restore a directory snapshot while retaining the target directory node."""
    target.mkdir(parents=True, exist_ok=True)
    for child in target.iterdir():
        _remove_path(child)
    shutil.copytree(source, target, dirs_exist_ok=True, symlinks=True)


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

    operations = [
        (source_dir / content_dir, target_root / client_dir / content_dir)
        for client_dir in CLIENT_DIRS
        for content_dir in CONTENT_DIRS
    ]
    conflicts = [
        path
        for source, target in operations
        for path in conflicting_paths(source, target)
    ]
    if conflicts and not force:
        conflict_list = "\n".join(str(path) for path in conflicts[:20])
        raise FileExistsError(
            "Refusing to overwrite changed target files. "
            f"Use --force to overwrite:\n{conflict_list}"
        )

    if dry_run:
        for source, target in operations:
            copy_tree(source, target, True, force)
        return

    with tempfile.TemporaryDirectory() as backup_root_text:
        backup_root = Path(backup_root_text)
        backups: dict[Path, tuple[Path, str | None, Path | None]] = {}
        for index, (_, target) in enumerate(operations):
            if _path_exists(target):
                backup = backup_root / str(index)
                link_target = os.readlink(target) if _is_directory_link(target) else None
                resolved_target = target.resolve() if link_target is not None else None
                shutil.copytree(target, backup, symlinks=True)
                backups[target] = (backup, link_target, resolved_target)
        try:
            for source, target in operations:
                copy_tree(source, target, False, force)
        except OSError as copy_error:
            rollback_errors: list[str] = []
            for index, (_, target) in enumerate(operations):
                try:
                    backup_info = backups.get(target)
                    if backup_info and backup_info[1] is not None:
                        backup, _, resolved_target = backup_info
                        _restore_directory_contents(backup, resolved_target)
                        continue
                    if _path_exists(target):
                        _remove_path(target)
                    if backup_info:
                        backup, _, _ = backup_info
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copytree(backup, target, symlinks=True)
                except OSError as rollback_error:
                    rollback_errors.append(f"{target}: {rollback_error}")
            if rollback_errors and hasattr(copy_error, "add_note"):
                copy_error.add_note(
                    "Rollback errors:\n" + "\n".join(rollback_errors)
                )
            raise


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
