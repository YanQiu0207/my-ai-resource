"""会话遥测分析（可追踪 · 第一层：transcript 后处理）。

从 Claude Code 会话 transcript（~/.claude/projects/<proj>/<session>.jsonl）
回溯重建每个工作流阶段的耗时、token 消耗与请求数，回答
「review 占比多少」「修复循环跑了几轮」这类问题。零运行时侵入。

阶段锚点（仅主会话链）三类，任一出现即切换当前阶段：
1. assistant 正文中的 skill 首行标记（`Using workflow-xxx`）；
2. `Skill` 工具调用（input.skill）；
3. 用户侧 `<command-name>/xxx</command-name>` 命令注入。
不使用 tool_result 里的标记——Read 技能文件正文会误触发。

子 agent 成本从会话伴生目录 `<session>/subagents/agent-*.jsonl` 精确汇总，
按其首条时间戳归入所处阶段，类型取自 meta.json 的 agentType。

耗时口径：活跃时长 = 相邻条目间隔之和，单个间隔超过 --idle-gap 秒（默认
300）的部分视为空闲（等待用户输入）剔除，避免用户离开把阶段耗时撑大。

用法：
    python analyze_session_metrics.py <session.jsonl> [more.jsonl ...]
    python analyze_session_metrics.py --project-dir <dir>   # 目录下全部 *.jsonl
    可选 --json <out.json> 输出机器可读结果；--min-share 过滤零头阶段。
"""

from __future__ import annotations

import argparse
import bisect
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

MARKER_RE = re.compile(r"\bUsing ([a-z][a-z0-9]*(?:-[a-z0-9]+)+)\b")
COMMAND_RE = re.compile(r"<command-name>/([a-z0-9-]+)</command-name>")
UNMARKED = "(未标记)"


def parse_ts(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def content_text(content) -> str:
    """用户消息 content 可能是字符串或块列表，取纯文本部分。"""
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(parts)


def read_main_entries(path: Path) -> list[dict]:
    """主链条目：ts / usage / anchors（本条触发的阶段名列表）/ tools。"""
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") not in ("user", "assistant") or "timestamp" not in obj:
                continue
            if obj.get("isSidechain"):
                continue
            msg = obj.get("message") or {}
            anchors: list[str] = []
            tools: list[str] = []
            usage = None
            if obj["type"] == "assistant":
                usage = msg.get("usage")
                for block in msg.get("content") or []:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "text":
                        anchors.extend(MARKER_RE.findall(block.get("text", "")))
                    elif block.get("type") == "tool_use":
                        tools.append(block.get("name", "?"))
                        if block.get("name") == "Skill":
                            skill = (block.get("input") or {}).get("skill")
                            if skill:
                                anchors.append(skill)
            else:
                anchors.extend("/" + c for c in
                               COMMAND_RE.findall(content_text(msg.get("content"))))
            entries.append({
                "ts": parse_ts(obj["timestamp"]),
                "usage": usage,
                "anchors": anchors,
                "tools": tools,
            })
    entries.sort(key=lambda e: e["ts"])
    return entries


def read_subagents(session_path: Path) -> list[dict]:
    """伴生目录下每个子 agent 的类型、起止时间与 token 汇总。"""
    agents = []
    sub_dir = session_path.with_suffix("") / "subagents"
    if not sub_dir.is_dir():
        return agents
    for jsonl in sorted(sub_dir.glob("agent-*.jsonl")):
        meta_path = jsonl.with_name(jsonl.stem + ".meta.json")
        agent_type = jsonl.stem
        if meta_path.is_file():
            try:
                agent_type = json.loads(
                    meta_path.read_text(encoding="utf-8")).get("agentType", agent_type)
            except (json.JSONDecodeError, OSError):
                pass
        first = last = None
        tokens = Counter()
        requests = 0
        with open(jsonl, encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "timestamp" not in obj:
                    continue
                ts = parse_ts(obj["timestamp"])
                first = ts if first is None else first
                last = ts
                usage = ((obj.get("message") or {}).get("usage")
                         if obj.get("type") == "assistant" else None)
                if usage:
                    requests += 1
                    add_usage(tokens, usage)
        if first is not None:
            agents.append({"agent_type": agent_type, "first": first, "last": last,
                           "tokens": tokens, "requests": requests})
    return agents


def new_bucket() -> dict:
    return {
        "active_seconds": 0.0,
        "requests": 0,
        "enter_count": 0,
        "tokens": Counter(),
        "sub_tokens": Counter(),
        "sub_agents": Counter(),
        "tools": Counter(),
    }


def add_usage(counter: Counter, usage: dict) -> None:
    counter["input"] += usage.get("input_tokens", 0)
    counter["output"] += usage.get("output_tokens", 0)
    counter["cache_read"] += usage.get("cache_read_input_tokens", 0)
    counter["cache_write"] += usage.get("cache_creation_input_tokens", 0)


def analyze_session(path: Path, idle_gap: float) -> dict:
    entries = read_main_entries(path)
    phases: dict[str, dict] = defaultdict(new_bucket)
    timeline: list[tuple[float, str]] = []  # (start_ts, phase)
    current = UNMARKED
    prev_ts: float | None = None
    idle_seconds = 0.0

    for e in entries:
        if prev_ts is not None:
            gap = e["ts"] - prev_ts
            phases[current]["active_seconds"] += min(gap, idle_gap)
            idle_seconds += max(0.0, gap - idle_gap)
        prev_ts = e["ts"]
        for name in e["anchors"]:
            if name != current:
                current = name
                phases[current]["enter_count"] += 1
                timeline.append((e["ts"], current))
        bucket = phases[current]
        for t in e["tools"]:
            bucket["tools"][t] += 1
        if e["usage"] is not None:
            bucket["requests"] += 1
            add_usage(bucket["tokens"], e["usage"])

    starts = [t for t, _ in timeline]
    agent_types = Counter()
    for agent in read_subagents(path):
        idx = bisect.bisect_right(starts, agent["first"]) - 1
        phase = timeline[idx][1] if idx >= 0 else UNMARKED
        phases[phase]["sub_tokens"].update(agent["tokens"])
        phases[phase]["sub_agents"][agent["agent_type"]] += 1
        agent_types[agent["agent_type"]] += 1

    return {
        "session": path.stem,
        "entries": len(entries),
        "wall_seconds": (entries[-1]["ts"] - entries[0]["ts"]) if entries else 0.0,
        "idle_seconds": idle_seconds,
        "subagent_types": dict(agent_types),
        "phases": {
            name: {
                "active_seconds": round(b["active_seconds"], 1),
                "enter_count": b["enter_count"],
                "requests": b["requests"],
                "tokens": dict(b["tokens"]),
                "sub_tokens": dict(b["sub_tokens"]),
                "sub_agents": dict(b["sub_agents"]),
                "top_tools": b["tools"].most_common(5),
            }
            for name, b in phases.items()
        },
    }


def fmt_duration(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m{s:02d}s"


def fmt_tokens(n: int) -> str:
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def print_report(results: list[dict], min_share: float) -> None:
    rollup: dict[str, dict] = defaultdict(lambda: {"active": 0.0, "out": 0, "enter": 0})
    for r in results:
        total_active = sum(p["active_seconds"] for p in r["phases"].values()) or 1.0
        print(f"\n== 会话 {r['session']}  条目 {r['entries']}  "
              f"活跃 {fmt_duration(total_active)}  空闲剔除 {fmt_duration(r['idle_seconds'])}")
        if r["subagent_types"]:
            summary = "  ".join(f"{k}×{v}" for k, v in
                                sorted(r["subagent_types"].items(), key=lambda x: -x[1]))
            print(f"   子 agent：{summary}")
        print(f"{'阶段':<34}{'进入':>4}{'活跃时长':>10}{'占比':>7}"
              f"{'请求':>6}{'主链out':>9}{'子agent-out':>12}")
        ordered = sorted(r["phases"].items(),
                         key=lambda kv: kv[1]["active_seconds"], reverse=True)
        for name, p in ordered:
            share = p["active_seconds"] / total_active
            out = p["tokens"].get("output", 0)
            sub_out = p["sub_tokens"].get("output", 0)
            roll = rollup[name]
            roll["active"] += p["active_seconds"]
            roll["out"] += out + sub_out
            roll["enter"] += p["enter_count"]
            if share < min_share:
                continue
            print(f"{name:<34}{p['enter_count']:>4}{fmt_duration(p['active_seconds']):>10}"
                  f"{share:>6.0%}{p['requests']:>6}{fmt_tokens(out):>9}{fmt_tokens(sub_out):>12}")

    if len(results) > 1:
        total = sum(v["active"] for v in rollup.values()) or 1.0
        print(f"\n== 跨会话汇总（{len(results)} 个会话，按阶段）")
        print(f"{'阶段':<34}{'进入':>4}{'活跃时长':>10}{'占比':>7}{'output合计':>12}")
        for name, v in sorted(rollup.items(), key=lambda kv: kv[1]["active"], reverse=True):
            if v["active"] / total < min_share:
                continue
            print(f"{name:<34}{v['enter']:>4}{fmt_duration(v['active']):>10}"
                  f"{v['active'] / total:>6.0%}{fmt_tokens(v['out']):>12}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", help="session .jsonl 路径")
    parser.add_argument("--project-dir", help="分析目录下全部 *.jsonl")
    parser.add_argument("--idle-gap", type=float, default=300.0,
                        help="超过该秒数的条目间隔按空闲剔除（默认 300）")
    parser.add_argument("--min-share", type=float, default=0.01,
                        help="低于该占比的阶段不打印（默认 0.01）")
    parser.add_argument("--json", help="额外输出 JSON 文件路径")
    args = parser.parse_args()

    paths = [Path(p) for p in args.paths]
    if args.project_dir:
        paths.extend(sorted(Path(args.project_dir).glob("*.jsonl")))
    if not paths:
        parser.error("未指定任何 session 文件（位置参数或 --project-dir）")

    results = []
    for path in paths:
        if not path.is_file():
            print(f"跳过（不存在）：{path}", file=sys.stderr)
            continue
        results.append(analyze_session(path, args.idle_gap))
    if not results:
        return 1

    print_report(results, args.min_share)
    if args.json:
        Path(args.json).write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON 已写入 {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
