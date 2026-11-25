#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply verification corrections and normalize the three audit grids."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = BASE / "cases" / "audits_batch3_raw.json"
OUT = BASE / "cases" / "audits_batch3.json"

raw = json.loads(RAW.read_text(encoding="utf-8"))
audits = raw["audits"]
verifs = raw["verifications"]

KEYMAP = {
    "tyg_pad": "tyg_pad",
    "Lixa 2026 浮动髋 IPD": "floating_hip_ipd",
    "Chen 2026 BFR 伞状综述": "bfr_umbrella",
}

DESIGNS = {
    "tyg_pad": "纵向观察性（剂量反应）",
    "floating_hip_ipd": "观察性（IPD）",
    "bfr_umbrella": "伞状综述",
}

TIERS = {
    "Fabero-Garrido 2022": "核心定量",
    "Fabero-Garrido 2024": "核心定量",
    "Gronlund 2020": "核心叙述/证据缺口",
    "Hsieh 2024": "核心定量",
    "Labata-Lezaun 2022": "支持/敏感性",
    "Maciel Batista 2020": "支持/敏感性",
    "Rodrigo-Mallorca 2021": "年龄边界敏感性",
    "Silva 2024": "核心叙述（有氧）",
    "Tiss 2025": "单独临床亚组",
}


def cells_of(audit: dict):
    return {(c["unit"], c["criterion"]): c for c in audit["cells"]}


def set_cell(audit: dict, unit: str, crit_prefix: str, **changes) -> None:
    for c in audit["cells"]:
        if c["unit"] == unit and c["criterion"].startswith(crit_prefix):
            c.update(changes)
            return
    raise KeyError((unit, crit_prefix))


normalized = {}
for raw_key, audit in audits.items():
    key = KEYMAP[raw_key]
    audit["case"] = key
    audit["design"] = DESIGNS[key]
    normalized[key] = {"audit": audit, "verification": verifs[raw_key]}

# ---------------------------------------------------------------- tyg
tyg = normalized["tyg_pad"]["audit"]
tyg_note = (
    "综述 Methods 排除标准(5)已报告重复发表/重叠队列的处理规则（仅保留样本量最大者），"
    "但表 1 与结果未逐研究报告本研究的队列重叠核查结果"
)
for c in tyg["cells"]:
    if c["criterion"] == "T11":
        c["note"] = tyg_note
tyg["narrative"] = (
    "Fu 2026 的 60 个格子中 T 54、F 1、U 5，未知负载 8.3%（5/60）。5 个 U 全部落在 T11："
    "综述在 Methods 排除标准(5)写明了重复发表/重叠队列的处理规则（仅保留样本量最大者），"
    "但没有逐研究报告这五项研究的重叠核查结果，故逐研究状态无法判定。唯一的 F 是 Sbriscia 2025 的 T12："
    "该研究仅按中位数二分类，只有 2 个 TyG 类别，未进入 4 项研究、17 个类别的剂量反应分析。"
    "其余格子大多可由表 1 的切点、设计、诊断与调整变量直接判定；T6（同行评审全文、英文、人体）"
    "依赖纳入推断，记为 E2。可见本案例的未知负载虽低，但并非为零：当纳入标准涉及“重叠队列如何处理”"
    "这类过程性事实时，规则已写而逐研究事实不在，审计只能落到 U。"
)

# ---------------------------------------------------------------- lixa
lixa = normalized["floating_hip_ipd"]["audit"]
std_i5 = next(c for c in lixa["criteria"] if c.startswith("I5"))
for c in lixa["cells"]:
    if c["criterion"].startswith("I5 DN"):
        c["criterion"] = std_i5
perumal_note = (
    "表 2 髋臼栏全为缺失；正文仅汇总称 10 项用 Letournel、其余用 AO（未点名）；"
    "AO 62A/62B/62C 合计 47 例，较 Perumal 23 + Hammad 27 = 50 例少 3 例，属综述层面推断"
)
set_cell(lixa, "Perumal", "I3", note=perumal_note)
set_cell(lixa, "Hammad", "I3", note=perumal_note)
lixa["narrative"] = (
    "Lixa 2026 的 84 个格子中 T 70、U 14，无 F，未知负载 16.7%。14 个 U 集中在两处。"
    "第一，I7（IPD 分析仅纳入报告逐例数据的研究）在 12 项研究上全部为 U：综述只称 7/12 项、112/271 例"
    "进入 IPD 分析，却没有列出这 7 项研究的名单，因此无法把“是否进入 IPD”映射到具体研究。"
    "第二，I5（type A 病例能否分离）在 Siavashi 与 Cech 两项为 U：原文分别只从 11 例和 69 例中提取 4 例和 3 例，"
    "其余病例是否为 type A 未说明。这两处都不是规则缺失，而是逐研究事实缺失；IPD 审计的关键标准恰好最不可审计。"
)

# ---------------------------------------------------------------- chen
chen = normalized["bfr_umbrella"]["audit"]
chen["tiers"] = TIERS
for c in chen["cells"]:
    if c["status"] == "S":
        c["status"] = "T"
        c["note"] = (
            c["note"]
            .replace("；支持/敏感性证据", "")
            .replace("；年龄边界敏感性", "")
            .replace("；临床亚组", "")
        )
        tier = TIERS.get(c["unit"], "")
        if tier:
            c["note"] = c["note"] + f"；层级：{tier}"

set_cell(chen, "Hsieh 2024", "U10", status="T",
         note="综述以老年人为目标；两项原始研究含 <60 岁者属年龄间接性，已在 U5/U6 判 F")
set_cell(chen, "Rodrigo-Mallorca 2021", "U10", status="T",
         note="综述定位非活动老年人；一项试验 59–71 岁属年龄边界问题，已在 U5/U6 判 F，U7 记分级")
set_cell(chen, "Tiss 2025", "U10", status="T",
         note="TKA 术前康复临床亚组，不是混合成人人群；≥50 岁问题留在 U5/U6")
set_cell(chen, "Tiss 2025", "U3", status="T",
         note="综述均龄 67.0 岁，目标为老年 TKA 人群；一项试验门槛 ≥50 岁留在 U5/U6")
set_cell(chen, "Fabero-Garrido 2022", "U13", status="F",
         note="表 1 结局仅肌力、肥大与袖带压力；安全性不是主要结局")
chen["narrative"] = (
    "Chen 2026 的 126 个格子中 T 103、F 9、U 14，未知负载 11.1%。F 集中在 U5/U6（原始研究年龄与 ≥60 不相容："
    "Hsieh 两项含 <60 岁、Rodrigo 一项 59–71 岁、Tiss 一项门槛 ≥50 岁）与 U13/U14（安全性或次要结局不匹配）。"
    "U 集中在 U6/U7（仅报告均龄、个体年龄与可分离性不明）与 U13（不良事件监测不足）。"
    "本案例的关键发现不在 T/F/U 本身，而在三值之外的“层级”：9 篇综述中 4 篇被作者归为支持/敏感性、"
    "年龄边界敏感性或单独临床亚组。层级不是资格违反，也不是未知，而是资格之后的证据定位；"
    "三值逻辑可以判资格，但不能表达层级，需要单独一列。"
)

# ---------------------------------------------------------------- verify counts
for key, payload in normalized.items():
    cnt = Counter(c["status"] for c in payload["audit"]["cells"])
    payload["audit"]["counts"] = dict(cnt)
    print(key, dict(cnt), "total", len(payload["audit"]["cells"]))

OUT.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
print("written", OUT)
