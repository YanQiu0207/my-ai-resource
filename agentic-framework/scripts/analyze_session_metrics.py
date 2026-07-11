"""会话遥测分析（可追踪 · 第一层：transcript 后处理）。

从 AI CLI 已落盘的会话数据回溯重建每个工作流阶段的耗时、token 消耗与
review 结论轨迹，回答「review 占比多少」「修复循环跑了几轮、质量如何」。
零运行时侵入，历史会话全部可回溯。

支持两种数据源（按文件内容自动识别）：
- Claude Code：~/.claude/projects/<proj>/<session>.jsonl
  （子 agent 成本从伴生目录 <session>/subagents/ 精确补齐）
- Codex CLI：~/.codex/sessions/<Y>/<M>/<D>/rollout-*.jsonl
  （token 取 token_count 事件累计值的相邻差分，天然去重）

阶段锚点：assistant 正文的 skill 首行标记（`Using workflow-xxx`，两源通用）；
Claude 额外识别 `Skill` 工具调用与 `<command-name>` 命令注入。
不使用工具返回值里的标记——Read 技能文件正文会误触发。

质量账：按 workflow-code-review 的固定报告格式（`# Code Review 报告` +
`## 总体结论`）提取每份报告的结论与 P0/P1/P2 数，输出会话内结论轨迹。

耗时口径：活跃时长 = 相邻条目间隔之和，单个间隔超过 --idle-gap 秒（默认
300）的部分视为空闲（等待用户输入）剔除。

用法：
    python analyze_session_metrics.py <session.jsonl> [more.jsonl ...]
    python analyze_session_metrics.py --project-dir <claude项目目录>
    python analyze_session_metrics.py --codex-dir ~/.codex/sessions --cwd E:/work/xxx
    可选：--json <out.json> 机器可读结果；--history <file> 按会话去重追加账本；
          --rates <rates.json> 成本折算，格式 {"模型名子串": {"input": 美元/MTok,
          "cache_read": .., "cache_write": .., "output": ..}}
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

# 标记须独占一行（允许引用/加粗/反引号包裹），防止讨论标记的正文误触发切换
MARKER_RE = re.compile(
    r"^[\s>*`-]*Using ([a-z][a-z0-9]*(?:-[a-z0-9]+)+)[\s`*]*$", re.MULTILINE)
COMMAND_RE = re.compile(r"<command-name>/([a-z0-9-]+)</command-name>")
# 行首锚定防止正文提及误报；级数与后缀放宽（历史报告存在 ## 级、带后缀的变体）
REVIEW_HEAD_RE = re.compile(r"^\s{0,3}#{1,3}\s*Code Review 报告.*$", re.MULTILINE)
REVIEW_VERDICT_RE = re.compile(r"总体结论[:：]?\s*\**\s*(PASS|NEEDS_CHANGES)")
REVIEW_P_RE = re.compile(r"^#{3,4}\s*P([012])-\d+", re.MULTILINE)
UNMARKED = "(未标记)"
TOKEN_KEYS = ("input", "output", "cache_read", "cache_write")


def parse_ts(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def entry_ts(obj: dict) -> float | None:
    """取条目时间戳；缺失 / 非字符串 / 非法格式返回 None（调用方跳过该行）。"""
    value = obj.get("timestamp")
    if not isinstance(value, str):
        return None
    try:
        return parse_ts(value)
    except ValueError:
        return None


def make_entry(ts: float, usage=None, model=None, anchors=None, tools=None) -> dict:
    return {"ts": ts, "usage": usage, "model": model,
            "anchors": anchors or [], "tools": tools or [], "reviews": []}


def extract_reviews(text: str, ts: float) -> list[dict]:
    """按 workflow-code-review 固定报告格式提取结论与 P0/P1/P2 数。"""
    reviews = []
    heads = list(REVIEW_HEAD_RE.finditer(text))
    for i, head in enumerate(heads):
        seg = text[head.start(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        verdict = REVIEW_VERDICT_RE.search(seg)
        if not verdict:
            continue
        counts = Counter(REVIEW_P_RE.findall(seg))
        reviews.append({"ts": ts, "verdict": verdict.group(1),
                        "p0": counts["0"], "p1": counts["1"], "p2": counts["2"]})
    return reviews


# ---------- Claude Code 数据源 ----------

def read_claude(path: Path) -> tuple[list[dict], list[dict], str | None]:
    entries, cwd = [], None
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") not in ("user", "assistant") or obj.get("isSidechain"):
                continue
            ts = entry_ts(obj)
            if ts is None:
                continue
            cwd = cwd or obj.get("cwd")
            msg = obj.get("message") or {}
            entry = make_entry(ts)
            if obj["type"] == "assistant":
                entry["usage"] = normalize_claude_usage(msg.get("usage"))
                entry["model"] = msg.get("model")
                for block in msg.get("content") or []:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "text":
                        text = block.get("text", "")
                        entry["anchors"].extend(MARKER_RE.findall(text))
                        entry["reviews"].extend(extract_reviews(text, entry["ts"]))
                    elif block.get("type") == "tool_use":
                        entry["tools"].append(block.get("name", "?"))
                        if block.get("name") == "Skill":
                            skill = (block.get("input") or {}).get("skill")
                            if skill:
                                entry["anchors"].append(skill)
            else:
                content = msg.get("content")
                text = content if isinstance(content, str) else "\n".join(
                    b.get("text", "") for b in content or []
                    if isinstance(b, dict) and b.get("type") == "text")
                entry["anchors"].extend("/" + c for c in COMMAND_RE.findall(text))
            entries.append(entry)
    entries.sort(key=lambda e: e["ts"])
    return entries, read_claude_subagents(path), cwd


def normalize_claude_usage(usage) -> dict | None:
    if not usage:
        return None
    return {"input": usage.get("input_tokens", 0),
            "output": usage.get("output_tokens", 0),
            "cache_read": usage.get("cache_read_input_tokens", 0),
            "cache_write": usage.get("cache_creation_input_tokens", 0)}


def read_claude_subagents(session_path: Path) -> list[dict]:
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
        first = None
        tokens = Counter()
        model_tokens: dict[str, Counter] = defaultdict(Counter)
        reviews = []
        with open(jsonl, encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = entry_ts(obj)
                if ts is None:
                    continue
                first = ts if first is None else first
                if obj.get("type") != "assistant":
                    continue
                msg = obj.get("message") or {}
                usage = normalize_claude_usage(msg.get("usage"))
                if usage:
                    tokens.update(usage)
                    model_tokens[msg.get("model") or "(unknown)"].update(usage)
                for block in msg.get("content") or []:
                    if isinstance(block, dict) and block.get("type") == "text":
                        reviews.extend(extract_reviews(block.get("text", ""), ts))
        if first is not None:
            agents.append({"agent_type": agent_type, "first": first, "tokens": tokens,
                           "model_tokens": model_tokens, "reviews": reviews})
    return agents


# ---------- Codex 数据源 ----------

def read_codex(path: Path) -> tuple[list[dict], list[dict], str | None]:
    entries, cwd, model, prev_total = [], None, None, Counter()
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = entry_ts(obj)
            if ts is None:
                continue
            payload = obj.get("payload")
            if not isinstance(payload, dict):
                payload = {}
            kind = (obj.get("type"), payload.get("type"))
            if kind[0] == "session_meta":
                cwd = cwd or payload.get("cwd")
            elif kind[0] == "turn_context":
                model = payload.get("model") or model
            elif kind == ("event_msg", "token_count"):
                info = payload.get("info") or {}
                total = normalize_codex_usage(info.get("total_token_usage"))
                if total is not None:
                    delta = {k: max(0, total[k] - prev_total[k]) for k in TOKEN_KEYS}
                    prev_total = Counter(total)
                    if any(delta.values()):
                        entries.append(make_entry(ts, usage=delta, model=model))
            elif kind[0] == "response_item":
                entry = make_entry(ts)
                if kind[1] == "message":
                    text = "\n".join(b.get("text", "") for b in payload.get("content") or []
                                     if isinstance(b, dict) and "text" in b)
                    if payload.get("role") == "assistant":
                        entry["anchors"].extend(MARKER_RE.findall(text))
                        entry["reviews"].extend(extract_reviews(text, ts))
                elif kind[1] in ("function_call", "custom_tool_call"):
                    entry["tools"].append(payload.get("name", kind[1]))
                elif kind[1] == "local_shell_call":
                    entry["tools"].append("shell")
                entries.append(entry)
    entries.sort(key=lambda e: e["ts"])
    return entries, [], cwd


def normalize_codex_usage(usage) -> dict | None:
    """OpenAI 口径映射：input 含 cached，拆出 cache_read；无 cache_write。"""
    if not usage:
        return None
    cached = usage.get("cached_input_tokens", 0)
    return {"input": max(0, usage.get("input_tokens", 0) - cached),
            "output": usage.get("output_tokens", 0),
            "cache_read": cached, "cache_write": 0}


def detect_source(path: Path) -> str:
    """解析首批合法 JSON 行，按结构判源，不做字符串猜测。"""
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            if "payload" in obj or obj.get("type") in (
                    "session_meta", "response_item", "event_msg", "turn_context"):
                return "codex"
            if "sessionId" in obj or obj.get("type") in ("user", "assistant"):
                return "claude"
    return "claude"


# ---------- 分析 ----------

def new_bucket() -> dict:
    return {"active_seconds": 0.0, "requests": 0, "enter_count": 0,
            "tokens": Counter(), "sub_tokens": Counter(),
            "sub_agents": Counter(), "tools": Counter()}


def analyze_session(path: Path, idle_gap: float) -> dict:
    source = detect_source(path)
    entries, subagents, cwd = (read_codex if source == "codex" else read_claude)(path)
    phases: dict[str, dict] = defaultdict(new_bucket)
    timeline: list[tuple[float, str]] = []
    model_tokens: dict[str, Counter] = defaultdict(Counter)
    reviews: list[dict] = []
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
        for r in e["reviews"]:
            reviews.append({**r, "phase": current})
        if e["usage"] is not None:
            bucket["requests"] += 1
            bucket["tokens"].update(e["usage"])
            model_tokens[e["model"] or "(unknown)"].update(e["usage"])

    starts = [t for t, _ in timeline]
    agent_types = Counter()
    for agent in subagents:
        idx = bisect.bisect_right(starts, agent["first"]) - 1
        phase = timeline[idx][1] if idx >= 0 else UNMARKED
        phases[phase]["sub_tokens"].update(agent["tokens"])
        phases[phase]["sub_agents"][agent["agent_type"]] += 1
        agent_types[agent["agent_type"]] += 1
        for m, c in agent.get("model_tokens", {}).items():
            model_tokens[m].update(c)
        for r in agent["reviews"]:
            reviews.append({**r, "phase": phase, "agent": agent["agent_type"]})

    reviews.sort(key=lambda r: r["ts"])
    return {
        "source": source,
        "session": path.stem,
        "cwd": cwd,
        "entries": len(entries),
        "wall_seconds": (entries[-1]["ts"] - entries[0]["ts"]) if entries else 0.0,
        "idle_seconds": idle_seconds,
        "subagent_types": dict(agent_types),
        "model_tokens": {m: dict(c) for m, c in model_tokens.items()},
        "reviews": reviews,
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


def estimate_cost(model_tokens: dict, rates: dict) -> tuple[float, list[str]]:
    """rates 键按模型名子串匹配；返回 (美元, 未折算模型列表)。"""
    cost, unmatched = 0.0, []
    for model, tokens in model_tokens.items():
        keys = [k for k in rates if k in model]
        if not keys:
            unmatched.append(model)
            continue
        rate = rates[max(keys, key=len)]  # 最长子串优先，避免泛化键抢走精确键
        cost += sum(tokens.get(key, 0) / 1e6 * rate.get(key, 0.0) for key in TOKEN_KEYS)
    return cost, unmatched


# ---------- 输出 ----------

def fmt_duration(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m{s:02d}s"


def fmt_tokens(n: int) -> str:
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def fmt_review(r: dict) -> str:
    parts = [f"P{i}×{r[f'p{i}']}" for i in range(3) if r[f"p{i}"]]
    return r["verdict"] + (f"({' '.join(parts)})" if parts else "")


def print_report(results: list[dict], min_share: float, rates: dict | None) -> None:
    rollup: dict[str, dict] = defaultdict(lambda: {"active": 0.0, "out": 0, "enter": 0})
    for r in results:
        total_active = sum(p["active_seconds"] for p in r["phases"].values()) or 1.0
        print(f"\n== [{r['source']}] {r['session']}  条目 {r['entries']}  "
              f"活跃 {fmt_duration(total_active)}  空闲剔除 {fmt_duration(r['idle_seconds'])}")
        if r["subagent_types"]:
            print("   子 agent：" + "  ".join(
                f"{k}×{v}" for k, v in sorted(r["subagent_types"].items(), key=lambda x: -x[1])))
        if r["reviews"]:
            print("   review 轨迹：" + " → ".join(fmt_review(x) for x in r["reviews"]))
        if rates:
            cost, unmatched = estimate_cost(r["model_tokens"], rates)
            note = f"（未折算模型：{', '.join(unmatched)}）" if unmatched else ""
            print(f"   估算成本：${cost:.2f}{note}")
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


def append_history(results: list[dict], history_path: Path) -> int:
    """按 (source, session) 去重追加账本，返回新增条数。"""
    seen = set()
    if history_path.is_file():
        with open(history_path, encoding="utf-8") as f:
            for line in f:
                try:
                    old = json.loads(line)
                    seen.add((old.get("source"), old.get("session")))
                except json.JSONDecodeError:
                    continue
    added = 0
    with open(history_path, "a", encoding="utf-8") as f:
        for r in results:
            key = (r["source"], r["session"])
            if key in seen:
                continue
            seen.add(key)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            added += 1
    return added


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", help="session .jsonl 路径（两种源自动识别）")
    parser.add_argument("--project-dir", help="Claude Code 项目目录，分析其下全部 *.jsonl")
    parser.add_argument("--codex-dir", help="Codex sessions 目录，递归分析 rollout-*.jsonl")
    parser.add_argument("--cwd", help="只保留工作目录匹配该前缀的会话")
    parser.add_argument("--idle-gap", type=float, default=300.0,
                        help="超过该秒数的条目间隔按空闲剔除（默认 300）")
    parser.add_argument("--min-share", type=float, default=0.01,
                        help="低于该占比的阶段不打印（默认 0.01）")
    parser.add_argument("--json", help="额外输出 JSON 文件路径")
    parser.add_argument("--history", help="按会话去重追加到该 JSONL 账本")
    parser.add_argument("--rates", help="费率表 JSON（美元/MTok），启用成本折算")
    args = parser.parse_args()

    paths = [Path(p) for p in args.paths]
    if args.project_dir:
        paths.extend(sorted(Path(args.project_dir).glob("*.jsonl")))
    if args.codex_dir:
        paths.extend(sorted(Path(args.codex_dir).rglob("rollout-*.jsonl")))
    paths = list(dict.fromkeys(paths))
    if not paths:
        parser.error("未指定任何 session 文件（位置参数 / --project-dir / --codex-dir）")

    rates = None
    if args.rates:
        rates = json.loads(Path(args.rates).read_text(encoding="utf-8"))

    results = []
    for path in paths:
        if not path.is_file():
            print(f"跳过（不存在）：{path}", file=sys.stderr)
            continue
        result = analyze_session(path, args.idle_gap)
        if args.cwd:
            want = args.cwd.replace("\\", "/").rstrip("/").lower()
            have = str(result["cwd"] or "").replace("\\", "/").rstrip("/").lower()
            if have != want and not have.startswith(want + "/"):
                continue
        if result["entries"]:
            results.append(result)
    if not results:
        print("无匹配会话。", file=sys.stderr)
        return 1

    print_report(results, args.min_share, rates)
    if args.json:
        Path(args.json).write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON 已写入 {args.json}")
    if args.history:
        added = append_history(results, Path(args.history))
        print(f"账本新增 {added} 条（已存在 {len(results) - added} 条跳过）→ {args.history}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
