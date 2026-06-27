#!/usr/bin/env python3
"""corpus-research 行为层评测：核对 skill 真跑产出的报告是否达成召回真值。

确定性评测（零 LLM）：
  - 召回率：must_recall 每篇的锚词是否出现在报告「非排除区」。
  - 误纳：should_not_include 每篇的锚词若出现在「非排除区」即判误纳。

「非排除区」= 报告全文去掉「## 排除…」小节。利用 corpus-research 报告的
固定结构（相关文章 / 单篇摘要在前，排除资料在后）区分「召回」与「正确排除」。

用法：
  python check_recall.py <report.md> <case_id> [behavior_gt.json]
  默认 GT 为脚本同级上一层的 behavior_gt.json。
  case_id 选择 behavior_gt.json::cases 里的某个 case（如 skill-eval-methods）。

退出码：0 = 召回率 100% 且无误纳；1 = 未达标；2 = 用法/找不到 case。
可被 skill-evolver 的 script_check 断言调用，也可独立运行。
"""
import json
import re
import sys
from pathlib import Path


def normalize(s: str) -> str:
    """忽略大小写和所有空白，便于跨标点 / 空格匹配锚词。"""
    return re.sub(r"\s+", "", s).lower()


def relevant_zone(report: str) -> str:
    """提取报告的「相关区」= 「## 相关文章」+「## 单篇…摘要」两个 section 拼接。

    只在结构化列出文章的区域判定召回 / 误纳，避免「## 不确定性」「## 综合总结」
    等叙述区里顺带提到的文章名被误判为召回（与 not_contains 否定语境同源的坑）。
    若报告缺这两个 section（skill 未按格式输出），回退到「全文去掉排除区」并告警。
    """
    lines = report.splitlines()
    zone, in_zone = [], False
    found = False
    for line in lines:
        if re.match(r"^##\s", line):
            in_zone = bool(re.search(r"相关文章|单篇", line))
            found = found or in_zone
        elif in_zone:
            zone.append(line)
    if found:
        return "\n".join(zone)

    # 回退：全文去掉「## 排除…」区
    print("[warn] 报告缺『相关文章/单篇摘要』结构化区，回退到全文去排除区判定",
          file=sys.stderr)
    keep, in_excl = [], False
    for line in lines:
        if re.match(r"^##\s", line):
            in_excl = bool(re.match(r"^##\s*排除", line))
        if not in_excl:
            keep.append(line)
    return "\n".join(keep)


def any_anchor(anchors: list[str], text_norm: str) -> str | None:
    for a in anchors:
        if normalize(a) in text_norm:
            return a
    return None


def load_case(gt_path: Path, case_id: str) -> tuple[dict, str]:
    """从 GT 取指定 case。兼容多 case（cases 数组）与旧单 case（顶层 must_recall）。"""
    data = json.loads(gt_path.read_text(encoding="utf-8"))
    if "cases" in data:
        for c in data["cases"]:
            if c.get("id") == case_id:
                return c, data.get("corpus", "")
        ids = [c.get("id") for c in data["cases"]]
        raise SystemExit(f"[err] 找不到 case '{case_id}'，可选：{ids}")
    return data, data.get("corpus", "")  # 旧格式：整个文件即一个 case


def main() -> int:
    if len(sys.argv) < 3:
        print("用法: python check_recall.py <report.md> <case_id> [behavior_gt.json]")
        return 2

    report_path = Path(sys.argv[1])
    case_id = sys.argv[2]
    gt_path = Path(sys.argv[3]) if len(sys.argv) > 3 else \
        Path(__file__).resolve().parent.parent / "behavior_gt.json"

    report = report_path.read_text(encoding="utf-8")
    gt, _corpus = load_case(gt_path, case_id)

    zone = relevant_zone(report)
    zone_norm = normalize(zone)

    recalled, missed = [], []
    for item in gt["must_recall"]:
        hit = any_anchor(item["anchors"], zone_norm)
        (recalled if hit else missed).append({**item, "hit": hit})

    false_incl = []
    for item in gt["should_not_include"]:
        hit = any_anchor(item["anchors"], zone_norm)
        if hit:
            false_incl.append({**item, "hit": hit})

    n_must = len(gt["must_recall"])
    recall_rate = len(recalled) / n_must if n_must else 0.0
    passed = recall_rate == 1.0 and not false_incl

    print(f"report     : {report_path}")
    print(f"question   : {gt.get('question', '')}")
    print(f"召回率     : {recall_rate:.3f}  ({len(recalled)}/{n_must})")
    for m in missed:
        print(f"  [漏召回] {m['id']:16s} anchors={m['anchors']}  — {m['note']}")
    print(f"误纳       : {len(false_incl)}")
    for f in false_incl:
        print(f"  [误纳]   {f['id']:16s} 命中锚词「{f['hit']}」出现在非排除区 — {f['note']}")
    print(f"\n=== {'PASS' if passed else 'FAIL'} ===")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
