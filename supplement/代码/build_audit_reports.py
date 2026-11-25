#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render full-record audit grids and the cross-audit summary."""

from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE / "cases" / "audits_batch3.json"

LABELS = {
    "tyg_pad": ("三值审计-Fu2026-TyG.md", "Fu 2026：TyG 指数与 PAD 剂量反应", "研究", "5 × 12"),
    "floating_hip_ipd": ("三值审计-Lixa2026-IPD.md", "Lixa 2026：浮动髋 IPD meta 分析", "研究", "12 × 7"),
    "bfr_umbrella": ("三值审计-Chen2026-伞状.md", "Chen 2026：BFR 训练伞状综述", "综述", "9 × 14"),
}


def load() -> dict:
    return json.loads(SRC.read_text(encoding="utf-8"))


def counts(audit: dict) -> dict:
    c = {"T": 0, "F": 0, "U": 0, "S": 0}
    for cell in audit["cells"]:
        c[cell["status"]] += 1
    c["total"] = len(audit["cells"])
    c["unknown_load"] = round(c["U"] / c["total"], 3) if c["total"] else 0.0
    return c


def render_case(key: str, payload: dict) -> None:
    filename, title, unit_word, shape = LABELS[key]
    audit = payload["audit"]
    crit_ids = audit["criteria"]
    units = audit["units"]
    by_key = {(c["unit"], c["criterion"]): c for c in audit["cells"]}
    cnt = counts(audit)

    lines = [f"# {title}：全记录三值审计", ""]
    lines.append(f"**性质**：对 {len(units)} 个{unit_word} × {len(crit_ids)} 条标准（共 {cnt['total']} 格）逐格判定。T = 满足，F = 违反，U = 已发表记录不足" + ("，S = 合格但被降为支持/单独亚组" if cnt["S"] else "") + "。")
    lines.append("")
    lines.append("## 一、审计矩阵")
    lines.append("")
    tiers = audit.get("tiers") or {}
    if tiers:
        lines.append("| 单位 | 层级 | " + " | ".join(crit_ids) + " |")
        lines.append("|---|---|" + "---|" * len(crit_ids))
    else:
        lines.append("| 单位 | " + " | ".join(crit_ids) + " |")
        lines.append("|---|" + "---|" * len(crit_ids))
    for unit in units:
        row = [unit]
        if tiers:
            row.append(tiers.get(unit, ""))
        for cid in crit_ids:
            cell = by_key.get((unit, cid))
            row.append(cell["status"] if cell else "?")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append(f"合计：T {cnt['T']}、F {cnt['F']}、U {cnt['U']}" + (f"、S {cnt['S']}" if cnt["S"] else "") + f"；未知负载 **{cnt['unknown_load']*100:.1f}%**。")
    lines.append("")

    interesting = [c for c in audit["cells"] if c["status"] in ("F", "U", "S")]
    lines.append("## 二、非 T 格子")
    lines.append("")
    if interesting:
        lines.append("| 单位 | 标准 | 状态 | 证据 | 说明 |")
        lines.append("|---|---|---|---|---|")
        for cell in interesting:
            lines.append(f"| {cell['unit']} | {cell['criterion']} | {cell['status']} | {cell['ev']} | {cell['note']} |")
    else:
        lines.append("无。")
    lines.append("")

    lines.append("## 三、解释")
    lines.append("")
    lines.append(audit.get("narrative", ""))
    lines.append("")
    lines.append("## 四、核验")
    lines.append("")
    ver = payload.get("verification") or {}
    issues = ver.get("issues", [])
    lines.append(f"核验代理检查 {ver.get('checked', 0)} 格，提出 {len(issues)} 条意见。")
    if issues:
        lines.append("")
        lines.append("| 单位 | 标准 | 当前 | 建议 | 问题 | 严重度 |")
        lines.append("|---|---|---|---|---|---|")
        for issue in issues:
            lines.append(f"| {issue['unit']} | {issue['criterion']} | {issue['current']} | {issue['suggested']} | {issue['problem']} | {issue['severity']} |")
    lines.append("")
    lines.append("## 五、限制")
    lines.append("")
    lines.append("- 事实来源限于该综述的主文与表；未读原始研究的全文。")
    lines.append("- “纳入推断”的格子记 T，但依据是综述的筛选行为，不是逐研究原始记录。")
    lines.append("- 单一审计者加一个核验代理，未计算评分者一致性。")
    lines.append("")
    lines.append("## 六、文件")
    lines.append("")
    lines.append(f"- [_research/cases/{key}_criteria.txt](_research/cases/{key}_criteria.txt) — 标准抽取。")
    lines.append(f"- [_research/cases/{key}_tables.txt](_research/cases/{key}_tables.txt) — 逐研究表。")
    lines.append("- [全记录审计汇总.md](全记录审计汇总.md) — 与 Sorin、Ren 的对比。")
    lines.append("")

    (BASE.parent / filename).write_text("\n".join(lines), encoding="utf-8")
    print(f"{filename}: T={cnt['T']} F={cnt['F']} U={cnt['U']} S={cnt['S']} unknown={cnt['unknown_load']*100:.1f}%")


def render_summary(data: dict) -> None:
    rows = [
        ("Sorin 2024（研究层面）", "混合", "48", "384", "11", "99", "274", "—", "71.4%"),
        ("Sorin 2024（臂层面）", "混合", "48", "384", "6", "117", "261", "—", "68.0%"),
        ("Ren 2026（RCT）", "仅 RCT", "5", "40", "34", "0", "6", "—", "15.0%"),
    ]
    for key, (_, title, unit_word, _) in LABELS.items():
        audit = data[key]["audit"]
        cnt = counts(audit)
        short = title.split("：")[0]
        tiers = audit.get("tiers") or {}
        non_core = sum(1 for v in tiers.values() if not v.startswith("核心")) if tiers else 0
        rows.append((short, audit.get("design", ""), str(len(audit["units"])), str(cnt["total"]),
                     str(cnt["T"]), str(cnt["F"]), str(cnt["U"]),
                     str(non_core) if tiers else "—", f"{cnt['unknown_load']*100:.1f}%"))

    lines = ["# 全记录审计汇总：未知负载随设计与报告变化", ""]
    lines.append("**性质**：把五个案例的逐记录三值审计放在同一张表上。T/F 的语义在不同案例间不完全相同（Sorin 的 8 条是排除标准，T 表示被排除；其余案例 T 表示满足），因此只比较未知负载量级，不比较 T/F 分布。“非核心单位”只对伞状案例有意义：被作者归为支持/敏感性、年龄边界或单独临床亚组的综述数。")
    lines.append("")
    lines.append("| 审计 | 设计 | 单位数 | 格数 | T | F | U | 非核心单位 | 未知负载 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append("## 主要发现")
    lines.append("")
    lines.append("第一，未知负载从混合设计的约七成，降到仅 RCT 的 15.0%、剂量反应的 8.3%、IPD 的 16.7% 与伞状的 11.1%，说明它首先是设计与报告属性。")
    lines.append("")
    lines.append("第二，同一案例内部，未知集中在少数标准：剂量反应的“重叠队列处理”、IPD 的“type A 可分离性”与“逐例数据可得性”、伞状的年龄适用性。规则可写，事实不在。")
    lines.append("")
    lines.append("第三，伞状案例的 9 篇综述中 4 篇被作者归为支持/敏感性、年龄边界敏感性或单独临床亚组。层级不是资格违反，也不是未知，而是资格之后的证据定位；三值逻辑可以判资格，但不能表达层级，需要单独一列。")
    lines.append("")
    lines.append("## 文件")
    lines.append("")
    for key, (filename, _, _, _) in LABELS.items():
        lines.append(f"- [{filename}]({filename})")
    lines.append("")
    (BASE.parent / "全记录审计汇总.md").write_text("\n".join(lines), encoding="utf-8")
    print("全记录审计汇总.md written")


def main() -> None:
    data = load()
    for key in LABELS:
        if key in data:
            render_case(key, data[key])
    render_summary(data)


if __name__ == "__main__":
    main()
