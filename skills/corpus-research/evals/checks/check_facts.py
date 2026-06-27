#!/usr/bin/env python3
"""corpus-research C 层评测：核对 skill 报告是否覆盖了 GT 标注的关键事实。

这是 fact_coverage 的确定性近似（eval_strategy.md 的 Online/keyword 模式）：
每个 key_fact 配若干锚词，任一锚词在报告全文出现即视为该事实被覆盖。
不需要 LLM，结果可复现。若需语义级判断（同义改写也算覆盖），换用
skill-evolver 的 fact_coverage Preset 模式（LLM 二分类）。

用法：
  python check_facts.py <report.md> <case_id> [behavior_gt.json] [min_coverage]
  min_coverage 默认 1.0（要求全覆盖）。

退出码：0 = 覆盖率 >= 阈值；1 = 未达标；2 = 用法/找不到 case。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_recall as cr  # noqa: E402  复用 normalize / any_anchor / load_case


def main() -> int:
    if len(sys.argv) < 3:
        print("用法: python check_facts.py <report.md> <case_id> "
              "[behavior_gt.json] [min_coverage]")
        return 2

    report_path = Path(sys.argv[1])
    case_id = sys.argv[2]
    gt_path = Path(sys.argv[3]) if len(sys.argv) > 3 and not _is_float(sys.argv[3]) \
        else Path(__file__).resolve().parent.parent / "behavior_gt.json"
    min_cov = _last_float(sys.argv, default=1.0)

    report = report_path.read_text(encoding="utf-8")
    gt, _corpus = cr.load_case(gt_path, case_id)
    facts = gt.get("key_facts", [])

    if not facts:
        print(f"[warn] case '{case_id}' 没有 key_facts，跳过事实覆盖检查")
        return 0

    report_norm = cr.normalize(report)
    covered, missing = [], []
    for f in facts:
        hit = cr.any_anchor(f["anchors"], report_norm)
        (covered if hit else missing).append({**f, "hit": hit})

    cov = len(covered) / len(facts)
    passed = cov >= min_cov

    print(f"report     : {report_path}")
    print(f"case       : {case_id}  —  {gt.get('question', '')}")
    print(f"事实覆盖率 : {cov:.3f}  ({len(covered)}/{len(facts)})  阈值 {min_cov}")
    for m in missing:
        print(f"  [未覆盖] {m['fact']}  anchors={m['anchors']}")
    print(f"\n=== {'PASS' if passed else 'FAIL'} ===")
    return 0 if passed else 1


def _is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def _last_float(argv: list[str], default: float) -> float:
    for a in reversed(argv[3:]):
        if _is_float(a):
            return float(a)
    return default


if __name__ == "__main__":
    sys.exit(main())
