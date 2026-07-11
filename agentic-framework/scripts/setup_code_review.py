"""Prepare the open-code-review (ocr) environment for a project.

Three idempotent steps:
1. Ensure the global ``ocr`` CLI is installed (install only if missing).
2. Write a project-level ``.opencodereview/rule.json`` template.
3. Print the remaining manual step (configure the LLM provider / key).

The ``open-code-review`` skill itself is distributed by
``install_agentic_framework.py`` (it copies the whole ``skills`` tree); this
script only sets up what that skill needs at runtime.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


NPM_PACKAGE = "@alibaba-group/open-code-review"

# One rule.json preset per language. Test files are excluded by ocr's own
# defaults, so exclude lists here only cover build / generated / dependency dirs.
RULE_TEMPLATES = {
    "generic": {
        "rules": [
            {
                "path": "**",
                "rule": "检查空指针、并发/线程安全、SQL 注入、XSS 等常见缺陷。",
                "merge_system_rule": True,
            }
        ],
        "exclude": ["**/generated/**", "**/vendor/**", "**/node_modules/**"],
    },
    "python": {
        "rules": [
            {
                "path": "**/*.py",
                "rule": (
                    "检查 None 处理与 KeyError、可变默认参数、bare except 吞异常、"
                    "资源未用 with 关闭、eval/exec 与 subprocess(shell=True) 注入、"
                    "字符串拼接 SQL 注入、多线程共享可变状态。"
                ),
                "merge_system_rule": True,
            }
        ],
        "exclude": ["**/__pycache__/**", "**/.venv/**", "**/venv/**", "**/migrations/**"],
    },
    "java": {
        "rules": [
            {
                "path": "**/*.java",
                "rule": (
                    "检查空指针(NPE)、线程安全与共享可变状态、流/连接资源泄漏"
                    "(优先 try-with-resources)、Statement 拼接 SQL 注入(应用 "
                    "PreparedStatement)、equals/hashCode 一致性、异常被吞没、"
                    "输出未转义导致的 XSS。"
                ),
                "merge_system_rule": True,
            }
        ],
        "exclude": ["**/target/**", "**/build/**", "**/*.class"],
    },
    "cpp": {
        "rules": [
            {
                "path": "**/*.{c,cc,cpp,cxx,h,hpp,hxx}",
                "rule": (
                    "检查内存安全(悬垂指针、use-after-free、越界、内存泄漏)、"
                    "裸 new/delete 与 RAII/智能指针、空指针解引用、未初始化变量、"
                    "整数溢出、拷贝/移动语义、并发数据竞争。"
                ),
                "merge_system_rule": True,
            }
        ],
        "exclude": ["**/build/**", "**/cmake-build-*/**", "**/third_party/**"],
    },
    "go": {
        "rules": [
            {
                "path": "**/*.go",
                "rule": (
                    "检查 nil 解引用、error 被忽略未处理、goroutine 泄漏、"
                    "并发数据竞争(共享 map/变量未加锁)、channel 死锁、"
                    "循环中 defer 误用、字符串拼接 SQL 注入。"
                ),
                "merge_system_rule": True,
            }
        ],
        "exclude": ["**/vendor/**"],
    },
}

DEFAULT_LANG = "generic"


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Set up the open-code-review (ocr) environment: ensure the CLI "
            "is installed and write a project rule.json template."
        )
    )
    parser.add_argument(
        "target_dir",
        type=Path,
        help="Project root where .opencodereview/rule.json is written.",
    )
    parser.add_argument(
        "--lang",
        choices=sorted(RULE_TEMPLATES),
        default=DEFAULT_LANG,
        help="Language preset for rule.json (default: generic).",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Do not auto-install ocr; only check and report.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing rule.json. By default it is kept.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without changing anything.",
    )
    return parser.parse_args(argv)


def ocr_installed() -> bool:
    """Return whether the ocr CLI is on PATH."""
    return shutil.which("ocr") is not None


def install_ocr(dry_run: bool) -> bool:
    """Install ocr globally via npm. Return whether ocr is available after."""
    npm = shutil.which("npm")
    if npm is None:
        print(
            "error: npm not found; install Node.js first, then run "
            f"`npm install -g {NPM_PACKAGE}`",
            file=sys.stderr,
        )
        return False

    if dry_run:
        print(f"[dry-run] npm install -g {NPM_PACKAGE}")
        return False

    print(f"installing ocr: npm install -g {NPM_PACKAGE}")
    result = subprocess.run([npm, "install", "-g", NPM_PACKAGE], check=False)
    if result.returncode != 0:
        print("error: ocr install failed; install it manually", file=sys.stderr)
        return False
    return ocr_installed()


def ensure_ocr(skip_install: bool, dry_run: bool) -> bool:
    """Ensure ocr is installed. Return whether it is available."""
    if ocr_installed():
        print("ocr already installed")
        return True
    if skip_install:
        print(
            f"ocr not installed; run `npm install -g {NPM_PACKAGE}` to install"
        )
        return False
    return install_ocr(dry_run)


def write_rule_template(
    target_dir: Path, lang: str, force: bool, dry_run: bool
) -> None:
    """Write .opencodereview/rule.json, keeping an existing file unless forced."""
    rule_path = target_dir / ".opencodereview" / "rule.json"

    if rule_path.exists() and not force:
        print(f"rule.json exists, kept: {rule_path}")
        return

    if dry_run:
        print(f"[dry-run] write {rule_path} (lang={lang})")
        return

    rule_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(RULE_TEMPLATES[lang], ensure_ascii=False, indent=4)
    rule_path.write_text(content + "\n", encoding="utf-8")
    print(f"wrote {rule_path} (lang={lang})")


def print_llm_hint(ocr_ready: bool) -> None:
    """Print the remaining manual LLM configuration step."""
    if not ocr_ready:
        return
    print(
        "\nnext: configure the LLM provider (one-time, per machine):\n"
        "  ocr config provider\n"
        "  ocr config model\n"
        "  ocr llm test"
    )


def setup(
    target_dir: Path,
    *,
    lang: str = DEFAULT_LANG,
    skip_install: bool = False,
    force: bool = False,
    dry_run: bool = False,
) -> None:
    """Run the full ocr environment setup."""
    target_dir = target_dir.resolve()
    ocr_ready = ensure_ocr(skip_install, dry_run)
    write_rule_template(target_dir, lang, force, dry_run)
    print_llm_hint(ocr_ready)


def main(argv: Sequence[str]) -> int:
    """Run the setup from the command line."""
    args = parse_args(argv)
    setup(
        args.target_dir,
        lang=args.lang,
        skip_install=args.skip_install,
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
