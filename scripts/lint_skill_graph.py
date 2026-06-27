"""Lint the agentic-framework skill / command / agent reference graph.

静态扫描 skills、commands、agents、docs 下的 Markdown，校验跨文件引用：

- dangling：动词（加载 / 调用 …）或链路箭头后引用了一个「长得像本框架 skill」
  （命名空间前缀匹配）但实际不存在的目标——改名、拼错、未创建。
- command 目标：每个 command 指向的 skill 必须存在。
- name 一致：每个 SKILL.md 的 frontmatter name 必须等于其目录名。
- orphan：定义了却无人引用的 skill（warning，不阻断）。

能力边界：只查「引用目标是否存在 / 是否连通」，查不出「引用存在但语义没接对」
（如链路图声明了某 skill 但工作流步骤实际没加载它）——那是 code review 的职责。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable


# 强位置引用：动词 / 链路箭头后的 kebab token（至少两段，避免单词误命中）
KEBAB = r"[a-z][a-z0-9]*(?:-[a-z0-9]+)+"
VERB_REF = re.compile(r"(?:加载|调用|运行|执行|使用|派)\s*[`/]?(" + KEBAB + r")`?")
ARROW_REF = re.compile(r"(?:→|->)\s*`?(" + KEBAB + r")`?")
CMD_TARGET = re.compile(r"调用\s*`?([a-z][a-z0-9-]+)`?\s*skill")
FRONTMATTER_NAME = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)


def read(path: Path) -> str:
    """Read a file as UTF-8, tolerating stray bytes."""
    return path.read_text(encoding="utf-8", errors="replace")


def collect_nodes(root: Path) -> tuple[dict[str, Path], set[str], set[str], list[str]]:
    """Return (skills{name:skill_md}, commands, agents, name_errors)."""
    skills: dict[str, Path] = {}
    name_errors: list[str] = []
    skills_dir = root / "skills"
    for sub in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_md = sub / "SKILL.md"
        if not skill_md.is_file():
            name_errors.append(f"{sub}: 目录下缺少 SKILL.md")
            continue
        skills[sub.name] = skill_md
        match = FRONTMATTER_NAME.search(read(skill_md))
        declared = match.group(1).strip() if match else None
        if declared != sub.name:
            name_errors.append(
                f"{skill_md}: frontmatter name `{declared}` 与目录名 `{sub.name}` 不一致"
            )

    commands = {p.stem for p in (root / "commands").glob("*.md")}
    agents = {p.stem for p in (root / "agents").glob("*.md")}
    return skills, commands, agents, name_errors


def markdown_files(root: Path) -> list[Path]:
    """All Markdown files that may contain references."""
    files: list[Path] = []
    for area in ("skills", "commands", "agents", "docs"):
        files.extend((root / area).rglob("*.md"))
    return sorted(files)


def find_dangling(
    files: Iterable[Path], known: set[str], namespaces: set[str]
) -> list[str]:
    """Flag strong-position refs that look like our skill but don't exist."""
    errors: list[str] = []
    for path in files:
        for lineno, line in enumerate(read(path).splitlines(), start=1):
            for match in VERB_REF.finditer(line):
                _check_token(match.group(1), known, namespaces, path, lineno, errors)
            for match in ARROW_REF.finditer(line):
                _check_token(match.group(1), known, namespaces, path, lineno, errors)
    return errors


def _check_token(
    token: str,
    known: set[str],
    namespaces: set[str],
    path: Path,
    lineno: int,
    errors: list[str],
) -> None:
    if token in known:
        return
    if token.split("-")[0] not in namespaces:
        return  # 不属于本框架命名空间，是普通技术词
    errors.append(f"{path}:{lineno}: 引用了不存在的目标 `{token}`")


def find_command_target_errors(root: Path, skills: set[str]) -> list[str]:
    """Each command must target an existing skill."""
    errors: list[str] = []
    for cmd in sorted((root / "commands").glob("*.md")):
        match = CMD_TARGET.search(read(cmd))
        if not match:
            continue
        target = match.group(1)
        if target not in skills:
            errors.append(f"{cmd}: 调用的 skill `{target}` 不存在")
    return errors


def find_orphans(skills: dict[str, Path], files: list[Path]) -> list[str]:
    """Skills referenced by no other file (whole-word match)."""
    blobs = {path: read(path) for path in files}
    orphans: list[str] = []
    for name, own_md in skills.items():
        pattern = re.compile(r"(?<![a-z0-9-])" + re.escape(name) + r"(?![a-z0-9-])")
        referenced = any(
            pattern.search(text) for path, text in blobs.items() if path != own_md
        )
        if not referenced:
            orphans.append(f"{name}: 未被任何 command / skill / doc 引用（疑似漏接线）")
    return orphans


def frontmatter_end(lines: list[str]) -> int:
    """1-based line number of the closing frontmatter `---`, or 0 if none."""
    if not lines or lines[0].strip() != "---":
        return 0
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return idx + 1
    return 0


def outgoing_edges(text: str, targets: set[str], self_name: str) -> list[tuple[str, int, str]]:
    """Yield (target, lineno, snippet) for references to other nodes in `text`.

    跳过 frontmatter（description 里的散文提及不算出边）和 URL 行（参考来源链接），
    避免与外部同名 skill（如 Anthropic frontend-design）产生假边。
    """
    patterns = {
        name: re.compile(r"(?<![a-z0-9-])" + re.escape(name) + r"(?![a-z0-9-])")
        for name in targets
        if name != self_name
    }
    lines = text.splitlines()
    fm_end = frontmatter_end(lines)
    edges: list[tuple[str, int, str]] = []
    for lineno, line in enumerate(lines, start=1):
        if lineno <= fm_end or "http" in line:
            continue
        for name, pattern in patterns.items():
            if pattern.search(line):
                edges.append((name, lineno, line.strip()[:90]))
    return edges


def print_graph(skills: dict[str, Path], known: set[str], files: list[Path]) -> None:
    """Emit a Markdown reference graph for LLM review of missing / spurious links."""
    blobs = {path: read(path) for path in files}
    print("# Skill 引用图\n")
    print("> 由 lint_skill_graph.py --graph 生成。出边带行号 + 原文，便于判断是\n"
          "> 「工作流里真加载」还是「仅链路图 / description 提及」。供 LLM 判定遗漏与多余。\n")
    for name in sorted(skills):
        skill_md = skills[name]
        text = read(skill_md)
        match = FRONTMATTER_NAME.search(text)
        desc_match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
        desc = desc_match.group(1).strip()[:160] if desc_match else "（无 description）"
        print(f"## {name}")
        print(f"- 职责：{desc}")

        edges = outgoing_edges(text, known, name)
        if edges:
            print("- 出边（本 skill 引用了）：")
            for target, lineno, snippet in edges:
                print(f"    - `{target}`  ({skill_md.name}:{lineno})  「{snippet}」")
        else:
            print("- 出边：无")

        inbound = sorted(
            path.relative_to(skill_md.parents[2]).as_posix()
            for path, body in blobs.items()
            if path != skill_md
            and re.search(r"(?<![a-z0-9-])" + re.escape(name) + r"(?![a-z0-9-])", body)
        )
        print(f"- 入边（被引用于）：{', '.join(inbound) if inbound else '无（孤儿）'}")
        print()


def main(argv: list[str]) -> int:
    """Run the linter and report errors / warnings."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows 控制台默认非 UTF-8，避免中文乱码

    parser = argparse.ArgumentParser(description="校验 agentic-framework 的 skill 引用图")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "agentic-framework",
        help="agentic-framework 根目录。默认取仓库内同级目录。",
    )
    parser.add_argument(
        "--graph",
        action="store_true",
        help="输出 Markdown 引用图（出边带行号 + 原文、入边）供 LLM 判定遗漏 / 多余，不做 lint。",
    )
    args = parser.parse_args(argv)
    root: Path = args.root.resolve()
    if not (root / "skills").is_dir():
        print(f"error: {root} 下没有 skills/ 目录", file=sys.stderr)
        return 2

    skills, commands, agents, name_errors = collect_nodes(root)
    known = set(skills) | commands | agents
    namespaces = {name.split("-")[0] for name in known}
    files = markdown_files(root)

    if args.graph:
        print_graph(skills, known, files)
        return 0

    errors: list[str] = []
    errors.extend(name_errors)
    errors.extend(find_command_target_errors(root, set(skills)))
    errors.extend(find_dangling(files, known, namespaces))
    warnings = find_orphans(skills, files)

    for message in errors:
        print(f"ERROR  {message}")
    for message in warnings:
        print(f"WARN   {message}")

    print(
        f"\nskills={len(skills)} commands={len(commands)} agents={len(agents)} "
        f"| errors={len(errors)} warnings={len(warnings)}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
