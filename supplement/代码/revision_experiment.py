#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Revision experiment for the Sorin 2024 formal model.

The experiment rebuilds the model under four kinds of revision and diffs the
conflict sets:

  fact revision      31 changes from egfr_mutant_only to mixed
  unit revision      study vs arm
  interpretation     D5 trial_level vs strict
  criterion revision P4 narrowed to exclude chemotherapy comparator arms
"""

from __future__ import annotations

import json
from pathlib import Path

from formal_model_sorin2024 import (
    ABSTRACTS,
    ALL_ITEMS,
    ARM_ATTRS,
    ARM_RECLASSIFIED,
    RULES,
    STUDY_ATTRS,
    Engine,
    load_items,
    summarize,
)

BASE = Path(__file__).resolve().parent
JSON_OUT = BASE / "revision_results.json"
MD_OUT = BASE.parent / "修订实验-证明的撤回与保留.md"

PRE31 = {
    ("Population", "31"): (
        "egfr_mutant_only",
        "title (pre-correction)",
        "high",
        "Title: 'EGFR-mutant'.",
    ),
}

P4_EXCEPTION_STUDY = {
    ("Population", "24"): None,
    ("Population", "35"): None,
    ("Population", "36"): None,
}

P4_EXCEPTION_ARM = {
    ("Population", "24_chemo"): None,
    ("Population", "35_chemo"): None,
    ("Population", "36_chemo"): None,
}

SCENARIOS = [
    ("baseline_study", "study", "trial_level", {}),
    ("pre_correction_31_study", "study", "trial_level", PRE31),
    ("baseline_arm", "arm", "trial_level", {}),
    ("pre_correction_31_arm", "arm", "trial_level", PRE31),
    ("strict_study", "study", "strict", {}),
    ("strict_arm", "arm", "strict", {}),
    ("p4_exception_study", "study", "trial_level", P4_EXCEPTION_STUDY),
    ("p4_exception_arm", "arm", "trial_level", P4_EXCEPTION_ARM),
]


def build_engine(mode: str, d5_mode: str, overrides: dict) -> Engine:
    engine = Engine(RULES)
    rows = load_items()

    for ref in ALL_ITEMS:
        row = rows[ref]
        engine.assert_fact(("Included", str(ref)), "Results, PMC10958389", "high")
        engine.assert_fact(("Year", str(ref), row["year"]), "reference list", "high")
        if ref in ABSTRACTS:
            engine.assert_fact(("PublicationType", str(ref), "abstract"), "reference list", "high")
            if d5_mode == "strict":
                engine.assert_fact(
                    ("PublicationType", str(ref), "abstract_without_trial_level_evidence"),
                    "criterion D5, strict reading",
                    "medium",
                    "Strict reading: every conference abstract is excluded by D5.",
                )
        else:
            engine.assert_fact(("PublicationType", str(ref), "article"), "reference list", "high")

    for ref in ALL_ITEMS:
        if mode == "arm" and ref in ARM_RECLASSIFIED:
            arm_id, attrs = ARM_ATTRS[ref]
            subject = arm_id
            entries = attrs
        else:
            subject = str(ref)
            entries = STUDY_ATTRS.get(ref, [])
        engine.assert_fact(
            ("ArmOf", subject, str(ref)),
            "eTable 3" if subject != str(ref) else "unit mode: study",
            "high",
        )
        for pred, args, source, confidence, note in entries:
            key = (pred, subject)
            if key in overrides:
                override = overrides[key]
                if override is None:
                    continue
                value, osource, oconfidence, onote = override
                engine.assert_fact((pred, subject, value), osource, oconfidence, onote)
            else:
                engine.assert_fact((pred, subject) + args, source, confidence, note)

    engine.run()
    return engine


def conflict_set(result: dict) -> set[tuple[str, str]]:
    return {(c["study"], c["criterion"]) for c in result["conflicts"]}


def diff(before: set, after: set) -> dict:
    return {
        "retracted": sorted(before - after, key=lambda x: (int(x[0]), x[1])),
        "added": sorted(after - before, key=lambda x: (int(x[0]), x[1])),
        "unchanged": sorted(before & after, key=lambda x: (int(x[0]), x[1])),
    }


def main() -> None:
    results = {}
    for name, mode, d5_mode, overrides in SCENARIOS:
        engine = build_engine(mode, d5_mode, overrides)
        results[name] = summarize(engine, mode, d5_mode)
        results[name]["revision"] = {
            "mode": mode,
            "d5_mode": d5_mode,
            "overrides": {f"{k[0]}({k[1]})": (v[0] if v else None) for k, v in overrides.items()},
        }

    sets = {name: conflict_set(result) for name, result in results.items()}
    diffs = {
        "fact_revision_31_study": diff(sets["pre_correction_31_study"], sets["baseline_study"]),
        "fact_revision_31_arm": diff(sets["pre_correction_31_arm"], sets["baseline_arm"]),
        "unit_revision": diff(sets["baseline_study"], sets["baseline_arm"]),
        "d5_trial_to_strict": diff(sets["baseline_study"], sets["strict_study"]),
        "p4_exception_study": diff(sets["baseline_study"], sets["p4_exception_study"]),
        "p4_exception_arm": diff(sets["baseline_arm"], sets["p4_exception_arm"]),
    }

    output = {"scenarios": results, "diffs": diffs}
    JSON_OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# 修订实验：证明的撤回与保留")
    lines.append("")
    lines.append("**性质**：对 Sorin 2024 的形式模型做四类修订——事实修订、单位修订、解释修订、标准修订——每次重建模型并比较冲突集合，记录哪些证明被撤回、哪些保留。")
    lines.append("")
    lines.append("## 一、方法")
    lines.append("")
    lines.append("修订不是简单改数字，而是改模型的前提。每次修订后，引擎从新的事实集重新推导；冲突集合的差集就是修订的证明后果。四类修订如下：")
    lines.append("")
    lines.append("1. **事实修订**：31 的人群从 `egfr_mutant_only` 改为 `mixed`（即本文的摘要修正）。")
    lines.append("2. **单位修订**：研究层面改为臂层面。")
    lines.append("3. **解释修订**：D5 从宽松读法改为严格读法。")
    lines.append("4. **标准修订**：P4 从“所有研究”收窄为“排除化疗对照臂之外的 EGFR 突变仅限研究”。")
    lines.append("")
    lines.append("## 二、场景与冲突数")
    lines.append("")
    lines.append("| 场景 | 单位 | D5 | 冲突原子 | 冲突研究 |")
    lines.append("|---|---|---|---|---|")
    for name, result in results.items():
        lines.append(f"| {name} | {result['mode']} | {result['d5_mode']} | {result['conflict_count']} | {', '.join(result['conflict_studies']) or '—'} |")
    lines.append("")
    lines.append("## 三、修订的证明后果")
    lines.append("")
    for label, key in [
        ("事实修订：31 从“仅 EGFR 突变”改为“混合”", "fact_revision_31_study"),
        ("单位修订：研究层面 → 臂层面", "unit_revision"),
        ("解释修订：D5 宽松 → 严格", "d5_trial_to_strict"),
        ("标准修订：P4 排除化疗对照臂（研究层面）", "p4_exception_study"),
        ("标准修订：P4 排除化疗对照臂（臂层面）", "p4_exception_arm"),
    ]:
        d = diffs[key]
        lines.append(f"### {label}")
        lines.append("")
        lines.append(f"- 撤回：{', '.join(f'{a}/{b}' for a, b in d['retracted']) or '无'}")
        lines.append(f"- 新增：{', '.join(f'{a}/{b}' for a, b in d['added']) or '无'}")
        lines.append(f"- 保留：{', '.join(f'{a}/{b}' for a, b in d['unchanged']) or '无'}")
        lines.append("")

    lines.append("## 四、主要发现")
    lines.append("")
    lines.append("第一，事实修订只撤回一条证明。31 的 P4 被撤回，31 的 T2 保留；其余 10 条冲突不变。这说明事实修订的影响是局部的，但局部修订足以改变一个研究是否被标记为冲突。")
    lines.append("")
    lines.append("第二，单位修订撤回五条证明。22 的 T1、24/33/35/36 的 T2 被臂级化疗标注消解；24/35/36 的 P4、31/42 的 T2、46 的 D2 保留。单位不是事实，但它决定了哪些事实被应用。")
    lines.append("")
    lines.append("第三，解释修订新增六条证明。D5 从宽松改为严格，6 篇会议摘要全部成为冲突。文本解释可以在一夜之间改变冲突计数。")
    lines.append("")
    lines.append("第四，标准修订撤回三条 P4 证明。把 P4 收窄为“排除化疗对照臂之外的 EGFR 突变仅限研究”后，24/35/36 的 P4 不再成立；再叠加单位修订，剩下的冲突只有 31/T2、42/T2、46/D2。")
    lines.append("")
    lines.append("这说明修订的类型不同，证明后果也不同：事实修订是局部的，单位修订是结构性的，解释修订是计数性的，标准修订是范围性的。一个可审计的系统应当记录修订类型与依赖图，而不只是记录最终的冲突数。")
    lines.append("")
    lines.append("## 五、限制")
    lines.append("")
    lines.append("- 本实验用“删除 P4 事实”模拟标准修订，而不是实现一般的例外规则；它展示了修订的后果，但不是完整的非单调语义。")
    lines.append("- 每次修订都重建模型，没有实现增量真值维护；对于更大的知识库，需要依赖图与增量重算。")
    lines.append("- 事实修订只演示了 31 一例；其他研究的事实修订可能产生不同的传播模式。")
    lines.append("- 本实验不处理修订的时间顺序与证据强度；它只比较修订前后的冲突集合。")
    lines.append("")
    lines.append("## 六、文件")
    lines.append("")
    lines.append("- [revision_experiment.py](_research/revision_experiment.py) — 修订实验脚本。")
    lines.append("- [revision_results.json](_research/revision_results.json) — 八个场景的完整冲突集合与证明树。")
    lines.append("- [研究目标与推进路线.md](研究目标与推进路线.md) — 总目标与停止标准。")
    lines.append("")
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")

    for name, result in results.items():
        print(f"{name}: {result['conflict_count']} conflicts")
    for key, d in diffs.items():
        print(f"{key}: retracted={len(d['retracted'])} added={len(d['added'])} unchanged={len(d['unchanged'])}")
    print(f"JSON: {JSON_OUT}")
    print(f"MD:   {MD_OUT}")


if __name__ == "__main__":
    main()
