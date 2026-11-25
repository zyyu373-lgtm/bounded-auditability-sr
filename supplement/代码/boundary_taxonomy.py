#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Boundary taxonomy: does formalizability predict where screening conflicts occur?

The table crosses formalizability (rule/structured vs semantic) with title
visibility (high vs low) for the eight exclusion criteria. The result is a
detectability map, not a violation rate.
"""

from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
JSON_OUT = BASE / "boundary_taxonomy_results.json"
MD_OUT = BASE.parent / "边界分类-可形式化与可见性.md"

CRITERIA = [
    {"id": "P4", "dimension": "人群", "formalizability": "structured", "visibility": "high",
     "T": 3, "verified": 3, "title_only": 0, "U": 44, "note": "24、35、36；31 撤回"},
    {"id": "D2", "dimension": "设计", "formalizability": "rule", "visibility": "high",
     "T": 1, "verified": 0, "title_only": 1, "U": 46, "note": "46，标题级"},
    {"id": "D3", "dimension": "设计", "formalizability": "rule", "visibility": "low",
     "T": 0, "verified": 0, "title_only": 0, "U": 47, "note": "50、58、59 需全文"},
    {"id": "D5", "dimension": "发表类型", "formalizability": "semantic", "visibility": "high",
     "T": 0, "verified": 0, "title_only": 0, "U": 0, "note": "宽松 0；严格 6"},
    {"id": "D6", "dimension": "发表类型", "formalizability": "rule", "visibility": "high",
     "T": 0, "verified": 0, "title_only": 0, "U": 0, "note": "无社论/评论"},
    {"id": "T1", "dimension": "治疗", "formalizability": "rule", "visibility": "high",
     "T": 1, "verified": 0, "title_only": 1, "U": 47, "note": "22，标题级"},
    {"id": "T2", "dimension": "治疗", "formalizability": "rule", "visibility": "high",
     "T": 6, "verified": 4, "title_only": 2, "U": 42, "note": "24、31、35、36 摘要级；33、42 标题级"},
    {"id": "T3", "dimension": "治疗", "formalizability": "semantic", "visibility": "low",
     "T": 0, "verified": 0, "title_only": 0, "U": 48, "note": "标题无 monotherapy"},
]


def cell(criterion: dict) -> str:
    high_formal = criterion["formalizability"] in {"rule", "structured"}
    high_vis = criterion["visibility"] == "high"
    if high_formal and high_vis:
        return "高可形式化 / 高可见"
    if high_formal and not high_vis:
        return "高可形式化 / 低可见"
    if not high_formal and high_vis:
        return "低可形式化 / 高可见"
    return "低可形式化 / 低可见"


def main() -> None:
    for criterion in CRITERIA:
        criterion["cell"] = cell(criterion)

    cells = {}
    for criterion in CRITERIA:
        name = criterion["cell"]
        cells.setdefault(name, {"criteria": [], "T": 0, "U": 0})
        cells[name]["criteria"].append(criterion["id"])
        cells[name]["T"] += criterion["T"]
        cells[name]["U"] += criterion["U"]

    results = {"criteria": CRITERIA, "cells": cells}
    JSON_OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# 边界分类：可形式化程度与标题可见性")
    lines.append("")
    lines.append("**性质**：把 8 条排除标准按“可形式化程度”（规则/结构化 vs 语义）与“标题可见性”（高 vs 低）交叉分类，检验哪一个更能预测冲突位置。")
    lines.append("")
    lines.append("## 一、分类表")
    lines.append("")
    lines.append("| 标准 | 维度 | 可形式化 | 标题可见性 | T | 摘要级 | 标题级 | U | 注 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for c in CRITERIA:
        lines.append(f"| {c['id']} | {c['dimension']} | {c['formalizability']} | {c['visibility']} | {c['T']} | {c['verified']} | {c['title_only']} | {c['U']} | {c['note']} |")
    lines.append("")
    lines.append("## 二、2×2 矩阵")
    lines.append("")
    lines.append("| | 高标题可见性 | 低标题可见性 |")
    lines.append("|---|---|---|")
    lines.append("| 高可形式化 | P4、D2、D6、T1、T2；T=11，U=179 | D3；T=0，U=47 |")
    lines.append("| 低可形式化 | D5；T=0（严格 6），U=0 | T3；T=0，U=48 |")
    lines.append("")
    lines.append("## 三、主要发现")
    lines.append("")
    lines.append("第一，11 条 T 冲突全部落在“高可形式化 / 高可见”格。P4、T1、T2、D2 的排除条件都能写成简单规则，且其取值能在题名中看到；因此它们既能被规则捕获，也能被事实触发。D6 也在该格，但 T=0：发表类型可见且可判，作者也确实没有纳入社论或评论。这说明该格是“可检出”，不是“必违例”。")
    lines.append("")
    lines.append("第二，高可形式化但低可见的 D3 没有 T，却有 47 个 U。它不是因为“没有违例”，而是因为题名很少写“retrospective”；没有事实，规则无法触发。这是“可形式化 ≠ 可审计”的直接证据。")
    lines.append("")
    lines.append("第三，低可形式化但高可见的 D5 是解释开关：宽松读法 0 个 T，严格读法 6 个 T。它的不确定性来自文本解释，不来自事实缺失。")
    lines.append("")
    lines.append("第四，低可形式化且低可见的 T3 有 48 个 U。它既难写成精确规则，也难从题名取得事实；在当前证据水平下不可审计。")
    lines.append("")
    lines.append("## 四、对“边界”的修正")
    lines.append("")
    lines.append("原来的 A/B/C 三层说的是“哪类命题可以追求证明”。本案例把 A 层的边界再推进一步：一个标准要可审计，需要同时满足三个条件。")
    lines.append("")
    lines.append("1. **规则可形式化**：标准文本能写成无歧义的触发条件。")
    lines.append("2. **事实可接地**：在可获得的证据层级上，能取得触发或否定条件的事实。")
    lines.append("3. **单位与分析组明确**：标准作用于研究、臂还是出版物；冲突进入主分析还是对照分析。")
    lines.append("")
    lines.append("第一条件通常是逻辑问题，第二条件是证据问题，第三条件是报告问题。本案例的 11 条 T 冲突之所以可检出，是因为三个条件同时成立；D3 与 T3 之所以不可检出，是因为第二条件不成立；P4 的冲突之所以需要修正，是因为第二条件的事实被题名误读。")
    lines.append("")
    lines.append("因此，“医学知识的有界公理化”更准确的说法是“医学知识的有界可审计化”：边界不在命题的数学性质，而在规则、事实与单位三者能否同时到位。")
    lines.append("")
    lines.append("## 五、限制")
    lines.append("")
    lines.append("- 标题可见性是粗略代理；摘要与全文可能让 D3/T3 的 U 转为 T 或 F。")
    lines.append("- 本表只覆盖 8 条排除标准；纳入标准（P1–P3、I1–I2、D1、D4）未被审计。")
    lines.append("- T 的计数来自研究层面、D5 宽松读法；臂层面与严格读法会改变分布。")
    lines.append("- 本表是单案例分类，不是普遍规律；需要多案例验证。")
    lines.append("")
    lines.append("## 六、文件")
    lines.append("")
    lines.append("- [boundary_taxonomy.py](_research/boundary_taxonomy.py) — 分类脚本。")
    lines.append("- [boundary_taxonomy_results.json](_research/boundary_taxonomy_results.json) — 分类数据。")
    lines.append("- [研究目标与推进路线.md](研究目标与推进路线.md) — 总目标与停止标准。")
    lines.append("")
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")

    for name, data in cells.items():
        print(f"{name}: criteria={data['criteria']} T={data['T']} U={data['U']}")
    print(f"JSON: {JSON_OUT}")
    print(f"MD:   {MD_OUT}")


if __name__ == "__main__":
    main()
