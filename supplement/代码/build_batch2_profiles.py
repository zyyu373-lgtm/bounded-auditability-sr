#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build corrected batch-2 case profiles from the workflow output."""

from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = BASE / "cases" / "workflow_batch2_raw.json"
BIB = BASE / "cases" / "case_meta_batch2_bib.json"
OUT = BASE / "cases" / "case_profiles_batch2.json"

raw = json.loads(RAW.read_text(encoding="utf-8"))
bib = json.loads(BIB.read_text(encoding="utf-8"))
classified = raw["classified"]


ALIASES = {"amh_pcos": "AMH 诊断 PCOS（DTA）"}


def get(case_key: str) -> dict:
    target = ALIASES.get(case_key, case_key)
    for key, value in classified.items():
        if value.get("case") == target or key == target:
            return value
    raise KeyError(case_key)


def find_index(findings: list[dict], needle: str) -> int:
    for i, f in enumerate(findings):
        if needle in f.get("text", ""):
            return i
    raise KeyError(needle)


profiles = []

# ---------------------------------------------------------------- AMH / DTA
amh = get("amh_pcos")
amh["id"] = "amh_pcos"
amh["label"] = "AMH 诊断 PCOS（DTA）"
amh["journal"] = bib["amh_pcos"]["journal"]
amh["year"] = int(bib["amh_pcos"]["year"])
amh["pmid"] = bib["amh_pcos"]["ids"].get("pmid", "")
amh["pmcid"] = bib["amh_pcos"]["ids"].get("pmcid", "")
amh["n_patients"] = None
amh["n_publications"] = 92
amh["pub_note"] = "文献数未单列，按 92 项研究计"
amh["unit"] = (
    "研究水平的 2×2 表（TP/FP/FN/TN）或由其导出的敏感度-特异度配对，按各研究自己的 AMH 阈值提取；"
    "同一文献可贡献多行（Zhang 2023 两行），不同文献也可能同属一个队列（Dietz de Loos 2021 与 2019，"
    "原文未说明去重）。三个 KQ 分别合并：83 + 6 + 11 = 100 项研究条目，超过 92 项 unique studies，"
    "跨 KQ 重叠的处理未报告。"
)
i = find_index(amh["findings"], "并补充韩国国内研究")
amh["findings"][i]["text"] = amh["findings"][i]["text"].replace(
    "并补充韩国国内研究", "并在补充分析中纳入韩国国内研究"
)
i = find_index(amh["findings"], "3 项（Kim 2017、Sopher 2014、Villarroel 2015）")
amh["findings"][i]["source"] = "METHODS（Eligibility criteria）；RESULTS（Study characteristics）；Table 2"
amh["unknown"]["note"] = (
    "KQ2 Table 1 共 9 行（按行计；正文 KQ2 为 6 项研究）；Indran et al. (2018) 的 PCOM/对照人数与 "
    "TP/FP/FN/TN 均标 NS（1/9 行）。正文未报告去重后的总受试者数（各 KQ 为 33,376、11,436、1,090；"
    "讨论仅称 over 45,000 participants）。"
)
profiles.append(amh)

# ---------------------------------------------------------------- statin
st = get("statin_crc")
st["id"] = "statin_crc"
st["label"] = "他汀与结直肠癌预后"
st["journal"] = bib["statin_crc"]["journal"]
st["year"] = int(bib["statin_crc"]["year"])
st["pmid"] = bib["statin_crc"]["ids"].get("pmid", "")
st["pmcid"] = bib["statin_crc"]["ids"].get("pmcid", "")
st["unit"] = (
    "基本分析单位为研究（按单篇 publication 识别）；同一研究可同时进入 prediagnostic 与 postdiagnostic "
    "两个暴露窗口（Cardwell 2014、Erkinantti 2022、Gray 2016 三项重叠），也可同时贡献 ACM 与 CSM 两个结局。"
    "患者例数按研究-暴露窗口累计（131,599 + 75,442 = 207,041），未按 3 项重叠研究去重；"
    "同一研究有多套数据时仅取 PSM 的一套。"
)
i = find_index(st["findings"], "限定这 5 项时变协变量研究")
st["findings"][i]["text"] = (
    "postdiagnostic 暴露定义不统一：作者按暴露定义对全部研究分类（Supplementary Table 3），"
    "其中 CSM 分析有 5 项、ACM 分析有 4 项将他汀暴露建模为 Cox 时变协变量；限定这些时变协变量研究的"
    "敏感性合并为 CSM HR 0.74（95% CI 0.67–0.83）、ACM HR 0.77（95% CI 0.68–0.87）。"
)
i = find_index(st["findings"], "prediagnostic 10 项中仅 4 项报告 ACM")
st["findings"][i]["source"] = "Results 3.2–3.4; Table 2"
st["unknown"] = {
    "n": 13, "d": 13,
    "note": "全部 13 项 postdiagnostic 研究均未按化疗意图（治愈 vs 姑息）分层，也未单独报告 IV 期患者估计；"
            "stage I–III 与 I–IV 的 ACM 差异无法与治疗意图的混淆分离。",
}
profiles.append(st)

# ---------------------------------------------------------------- hearing
hl = get("hearing_loss")
hl["id"] = "hearing_loss"
hl["label"] = "个人听设备与听力损失"
hl["journal"] = bib["hearing_loss"]["journal"]
hl["year"] = int(bib["hearing_loss"]["year"])
hl["pmid"] = bib["hearing_loss"]["ids"].get("pmid", "")
hl["pmcid"] = bib["hearing_loss"]["ids"].get("pmcid", "")
hl["unit"] = (
    "研究：60 项纳入研究（67,404 人，20 国）；主合并以研究级 OR 为单位（12 项横断面研究，7,824 人）。"
    "EHF、OAE 与耳鸣为叙述性汇总，不构成同一研究的多次合并；同一研究是否进入多个结局的定量合成，"
    "原文未说明。"
)
hl["analysis_group"] = (
    "主分析：PLD 使用者 vs 非使用者（12 项横断面研究，7,824 人）。年龄亚组为 <18 岁 3 项（3,588 人）"
    "与 ≥18 岁 8 项（1,901 人），合计 11 项、5,489 人，另 1 项（2,335 人）未列入；设备亚组为耳塞/入耳"
    "3 项 vs 头戴 1 项；时长与音量各分三档（11 项、12 项）。敏感性分析剔除 5 项低质量横断面研究（余 7 项），"
    "并行 REML/HKSJ 调整。"
)
i = find_index(hl["findings"], "3–8 kHz 高频 >20 dB 7 项")
hl["findings"][i]["text"] = hl["findings"][i]["text"].replace(
    "3–8 kHz 高频 >20 dB 7 项", "3–8 kHz 高频、≥2 个频率 >20 dB 7 项"
)
i = find_index(hl["findings"], "年龄分层：<18 岁 14 项")
hl["findings"][i]["text"] = (
    "60 项纳入研究的人口学年龄分布为 <18 岁 14 项、≥18 岁 35 项、跨 18 岁 10 项单列 mixed、1 项未报告"
    "（这是描述性分层，不是 12 项主分析的年龄亚组）；主分析年龄亚组为 <18 岁 3 项与 ≥18 岁 8 项，"
    "Basjo 2016 [61] 与 Swierniak 2020 [70] 同时出现于两组文献列表，作者未说明重复贡献处理。"
)
profiles.append(hl)

# ---------------------------------------------------------------- BFR umbrella
bfr = get("bfr_umbrella")
bfr["id"] = "bfr_umbrella"
bfr["label"] = "BFR 训练伞状综述"
bfr["journal"] = bib["bfr_umbrella"]["journal"]
bfr["year"] = int(bib["bfr_umbrella"]["year"])
bfr["pmid"] = bib["bfr_umbrella"]["ids"].get("pmid", "")
bfr["pmcid"] = bib["bfr_umbrella"]["ids"].get("pmcid", "")
bfr["unknown"] = {
    "n": 9, "d": 9,
    "note": "0/9 篇综述报告 AOP/LOP 测量或运动中的体位；14 个 BFR 报告域中 8 个在所有综述中均未报告；"
            "主要力量/肥大综述 0/14 项试验定量报告力竭接近度。",
}
profiles.append(bfr)

# ---------------------------------------------------------------- floating hip IPD
fh = get("floating_hip_ipd")
fh["id"] = "floating_hip_ipd"
fh["label"] = "浮动髋 IPD meta 分析"
fh["journal"] = bib["floating_hip_ipd"]["journal"]
fh["year"] = int(bib["floating_hip_ipd"]["year"])
fh["pmid"] = bib["floating_hip_ipd"]["ids"].get("pmid", "")
fh["pmcid"] = bib["floating_hip_ipd"]["ids"].get("pmcid", "")
fh["unit"] = (
    "个体患者（individual participant）为分析单位，研究为聚类单位（随机截距）。12 项研究共 271 例进入"
    "描述性汇总；其中 7 项报告逐例患者数据（112 例）进入一阶段 IPD 分析，其余 5 项仅汇总数据。"
    "各模型分母随协变量与缺失变化（HO 吲哚美辛模型 59 例、HHS 至手术时间模型 51 例、AVN 模型报告 44 例）；"
    "原文未报告研究间样本重叠或重复病例的处理规则。"
)
fh["analysis_group"] = (
    "IPD 可得性划分的是嵌套子集而非并列组：描述性汇总 12 项/271 例，IPD 分析 7 项/112 例（子集）。"
    "IPD 内按结局分别建模（HO、创伤后骨关节炎、AVN、骨不连、HHS）；四个二分类结局按手术入路、"
    "吲哚美辛使用、固定顺序、Matta 复位评分分组；HHS 的协变量集合不同（至手术时间及是否发生 AVN、HO、"
    "创伤后骨关节炎、骨不连）。"
)
i = find_index(fh["findings"], "HHS 分析 51 例")
fh["findings"][i]["text"] = (
    "各模型分母随协变量与缺失变化：HO 吲哚美辛分析 59 例（24 vs 35；事件 9 vs 1；OR 0.09，95% CI "
    "0.01–0.65，P=0.018）；HHS 至手术时间模型 51 例；AVN 行报告 5 vs 39（合计 44 例），未给出 51 例分母。"
    "AVN 与骨不连的固定顺序模型未收敛（原文脚注），未给出 OR；股骨优先组 22 例 0 事件为观察数据，"
    "不是原文给出的未收敛原因。"
)
for cr in fh["criteria"]:
    if cr["id"] == "I7":
        cr["note"] = "IPD 分析条件，非综述筛选标准；" + cr["note"]
fh["unknown"] = {
    "n": 159, "d": 271,
    "note": "IPD 未覆盖 5/12 项研究、159/271 例患者（仅汇总数据）；并发症报告于 9 项/211 例，"
            "髋关节脱位仅 3 项/61 例，HHS 仅 3 项。",
}
profiles.append(fh)

# ---------------------------------------------------------------- TyG dose-response
tyg = get("tyg_pad")
tyg["id"] = "tyg_pad"
tyg["label"] = "TyG 指数与 PAD 剂量反应"
tyg["journal"] = bib["tyg_pad"]["journal"]
tyg["year"] = int(bib["tyg_pad"]["year"])
tyg["pmid"] = bib["tyg_pad"]["ids"].get("pmid", "")
tyg["pmcid"] = bib["tyg_pad"]["ids"].get("pmcid", "")
tyg["unknown"] = {
    "n": 1, "d": 5,
    "note": "剂量反应分析仅覆盖 4/5 项纳入研究（17 个 TyG 暴露类别）；Sbriscia 2025 按中位数切点分类，"
            "未列入剂量反应分析。",
}
profiles.append(tyg)

OUT.write_text(json.dumps(profiles, ensure_ascii=False, indent=2), encoding="utf-8")

for p in profiles:
    print(f"{p['id']}: criteria={len(p['criteria'])} unit={p['unit'][:50]}...")
print(f"written {OUT}")
