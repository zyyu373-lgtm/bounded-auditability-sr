#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cross-case replication of the four modeling choices.

Cases: Sorin 2024 (reference, already audited) plus four open-access
meta-analyses fetched for this study. Each case contributes:

  - criterion-level classification: type (A/B/C), formalizability
    (rule/structured/judgment), title visibility (high/low), evidence level;
  - the unit-of-analysis and analysis-group structure;
  - record-level boundary findings quoted from the source text;
  - the reported or computable unknown load for its key boundary criterion.

The script does not re-audit every record of every case. It tests whether the
four modeling choices and the 2x2 boundary pattern replicate at the level the
sources permit, and it keeps the denominators explicit.
"""

from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
JSON_OUT = BASE / "cross_case_results.json"
MD_OUT = BASE.parent / "多案例对比-四个建模选择的复现.md"

# ---------------------------------------------------------------- profiles

CASES = [
    {
        "id": "robotic_vats",
        "label": "RATS vs VATS（仅 RCT）",
        "journal": "J Thorac Dis",
        "year": 2026,
        "pmid": "42583305",
        "pmcid": "PMC13460117",
        "design": "仅 RCT",
        "n_studies": 5,
        "n_publications": 7,
        "n_patients": 712,
        "unit": "试验：RVlob 3 篇文献合并为 1 个试验单位（引用 Cochrane 指南，显式处理）",
        "analysis_group": "结局特异：QoL 仅 3 项试验，其中 2 项仅有定性描述；定量合并用 RAVAL + RVlob（446 例）",
        "criteria": [
            {"id": "R1", "text": "RCTs", "type": "A", "formal": "rule", "vis": "high", "ev": "E0"},
            {"id": "R2", "text": "成人 ≥18 岁", "type": "A", "formal": "rule", "vis": "high", "ev": "E1"},
            {"id": "R3", "text": "病理确诊 NSCLC", "type": "A", "formal": "rule", "vis": "high", "ev": "E1",
             "note": "BRAVO 表 1 记为 NSCLC 或肺转移"},
            {"id": "R4", "text": "VATS vs RATS", "type": "A", "formal": "rule", "vis": "high", "ev": "E0"},
            {"id": "R5", "text": "至少报告 1 项预设结局", "type": "A", "formal": "structured", "vis": "high", "ev": "E1"},
            {"id": "R6", "text": "排除非 RCT", "type": "A", "formal": "rule", "vis": "high", "ev": "E0"},
            {"id": "R7", "text": "排除数据不完整、无法合并", "type": "C", "formal": "judgment", "vis": "low", "ev": "E2"},
            {"id": "R8", "text": "排除严重合并症（操作化为 NYHA III/IV、LVEF <50%、术后 FEV1 <40% 等）",
             "type": "A", "formal": "structured", "vis": "low", "ev": "E2",
             "note": "原文先写“严重合并症”，再按 ROMAN 标准操作化"},
        ],
        "findings": [
            {"text": "RVlob 试验占 3 篇文献（Jin 2022 Ann Surg；Jin 2023 Chest；Niu 2024 EClinicalMedicine），7 篇文献对应 5 个试验",
             "source": "Results / Methods",
             "layer": "E2",
             "kind": "单位"},
            {"text": "BRAVO（Terra 2022）表 1 人群记为“Resectable NSCLC or lung metastasis”，宽于标准 II“pathologically diagnosed with NSCLC”；正文未说明如何处理",
             "source": "Table 1",
             "layer": "E2",
             "kind": "人群边界"},
            {"text": "ROMAN 试验因无效提前终止（early termination for futility）",
             "source": "Table 1",
             "layer": "E2",
             "kind": "设计事实"},
            {"text": "英语限制写在检索方法，不在纳入/排除标准清单",
             "source": "Methods",
             "layer": "E2",
             "kind": "标准完整性"},
        ],
        "unknown": {"n": 1, "d": 5, "note": "BRAVO 人群是否符合标准 II，表级不可判"},
    },
    {
        "id": "lidocaine_vats",
        "label": "VATS 围术期静脉利多卡因",
        "journal": "J Pain Res",
        "year": 2026,
        "pmid": "42454005",
        "pmcid": "PMC13367487",
        "design": "仅 RCT",
        "n_studies": 16,
        "n_publications": 16,
        "n_patients": 1045,
        "unit": "研究：16 项两臂 RCT，一篇对应一个试验",
        "analysis_group": "结局与时点特异：疼痛分析各时点 6–10 项试验",
        "criteria": [
            {"id": "L1", "text": "成人", "type": "A", "formal": "rule", "vis": "high", "ev": "E1"},
            {"id": "L2", "text": "接受 VATS", "type": "A", "formal": "rule", "vis": "high", "ev": "E1",
             "note": "2/16 项表 1 记为“thoracic surgery”，VATS 状态需全文"},
            {"id": "L3a", "text": "静脉利多卡因（药物与途径）", "type": "A", "formal": "rule", "vis": "high", "ev": "E1"},
            {"id": "L3b", "text": "围术期给药（时机）", "type": "B", "formal": "structured", "vis": "low", "ev": "E2",
             "note": "无剂量/时机阈值；术后才开始者排除"},
            {"id": "L4", "text": "对照为静脉生理盐水安慰剂", "type": "A", "formal": "rule", "vis": "high", "ev": "E1"},
            {"id": "L5", "text": "仅 RCT", "type": "A", "formal": "rule", "vis": "high", "ev": "E0"},
            {"id": "L6", "text": "报告预设结局", "type": "A", "formal": "structured", "vis": "high", "ev": "E1"},
            {"id": "L7", "text": "排除儿童、非 RCT、动物、离体、其他给药途径", "type": "A", "formal": "rule", "vis": "high", "ev": "E0"},
            {"id": "L8", "text": "排除仅术后开始给药的研究", "type": "B", "formal": "structured", "vis": "low", "ev": "E2"},
        ],
        "findings": [
            {"text": "Cui 2010、Cui 2011 两行手术栏记为“Thoracic surgery lasting 3–6 h”，未写 VATS；正文未说明",
             "source": "Table 1",
             "layer": "E2",
             "kind": "人群边界"},
            {"text": "剂量谱系：维持 1.0–2.0 mg/kg/h；负荷 1.0–1.5 mg/kg；Ren 2023 用 8.0 mg/kg/h × 15 min；时机从术前 30 min 到诱导时；终点从手术结束到术后 24 h",
             "source": "Table 1",
             "layer": "E2",
             "kind": "干预定义"},
            {"text": "作者在局限中承认剂量与输注时长变异，并归因于临床异质性；疼痛评分 I² 95.6%（6–8 h）、87.9%（24 h）",
             "source": "Limitations / Results",
             "layer": "E2",
             "kind": "干预定义"},
            {"text": "语言限制“English or Chinese”只写在局限，不在标准清单",
             "source": "Limitations",
             "layer": "E2",
             "kind": "标准完整性"},
        ],
        "unknown": {"n": 2, "d": 16, "note": "Cui 2010/2011 是否 VATS，表级不可判"},
    },
    {
        "id": "cabg_nma",
        "label": "CABG 技术网状 meta 分析",
        "journal": "PLoS One",
        "year": 2026,
        "pmid": "42986881",
        "pmcid": "PMC13739143",
        "design": "观察性 + RCT（132 项中 8 项 RCT）",
        "n_studies": 132,
        "n_publications": 132,
        "n_patients": 779773,
        "unit": "臂/对照：每项研究的每个治疗臂映射到 3 个主技术或 9 个亚技术节点；单臂研究排除",
        "analysis_group": "网络节点：9 个亚技术；8 项 RCT 与 124 项观察性研究同网",
        "criteria": [
            {"id": "G1", "text": "观察性（前瞻/回顾）或 RCT", "type": "A", "formal": "rule", "vis": "high", "ev": "E0"},
            {"id": "G2", "text": "比较机器人 vs 传统和/或微创及其亚技术", "type": "A", "formal": "structured", "vis": "high", "ev": "E1",
             "note": "9 个亚技术节点需先定义"},
            {"id": "G3", "text": "CABG", "type": "A", "formal": "rule", "vis": "high", "ev": "E0"},
            {"id": "G4", "text": "排除数据不完整或仅有定性结局", "type": "C", "formal": "judgment", "vis": "low", "ev": "E2"},
            {"id": "G5", "text": "排除无对照/单臂", "type": "B", "formal": "rule", "vis": "high", "ev": "E1"},
            {"id": "G6", "text": "网络连通性（隐含，分析层）", "type": "B", "formal": "structured", "vis": "low", "ev": "analysis"},
            {"id": "G7", "text": "转递性（隐含，分析层）", "type": "C", "formal": "judgment", "vis": "low", "ev": "analysis"},
        ],
        "findings": [
            {"text": "9 个亚技术显式枚举：RADCAB、TECAB；MIDCAB、MICS、PA-CABG、Endo-CABG；C-ONCAB、BH-ONCAB、OPCAB",
             "source": "Introduction",
             "layer": "E2",
             "kind": "节点定义"},
            {"text": "转递性用效应修饰因子分布比较来评估；病变血管数与 LVEF 在两技术间存在显著差异，作者承认假设只部分成立",
             "source": "Results / Methods",
             "layer": "E2",
             "kind": "分析层假设"},
            {"text": "132 项研究中仅 8 项 RCT（2,762 例），其余为队列/注册/PSM；作者称结果为 hypothesis-generating",
             "source": "Results / Abstract",
             "layer": "E1",
             "kind": "证据结构"},
        ],
        "unknown": None,
    },
    {
        "id": "pediatric_empyema",
        "label": "儿童脓胸治疗策略（配对 + 网状）",
        "journal": "Front Pediatr",
        "year": 2026,
        "pmid": "43005199",
        "pmcid": "PMC13745557",
        "design": "RCT + 队列 + 病例对照 + 病例系列（>10 例）",
        "n_studies": 77,
        "n_publications": 77,
        "n_patients": 7378,
        "unit": "臂：40 项比较研究进入 NMA；37 项单臂或超范围臂仅作描述",
        "analysis_group": "治疗线：33/145 臂（23%）为升级/挽救治疗；敏感性分析限制为一线臂",
        "criteria": [
            {"id": "E1", "text": "原始研究、儿童 <18 岁、脓胸管理", "type": "A", "formal": "rule", "vis": "high", "ev": "E0"},
            {"id": "E2", "text": "设计：RCT/队列/病例对照/病例系列 >10 例", "type": "A", "formal": "rule", "vis": "high", "ev": "E1"},
            {"id": "E3", "text": "脓胸确诊（生化/影像/微生物/操作/手术任一）", "type": "A", "formal": "structured", "vis": "high", "ev": "E1"},
            {"id": "E4", "text": "Stage II/III 定义（pH <7.20、葡萄糖 <35 mg/dL、LDH >1000 IU/L 等）", "type": "A", "formal": "rule", "vis": "low", "ev": "E2",
             "note": "定义可写成判定规则，但仅 25/77 项报告分期"},
            {"id": "E5", "text": "含 Stage I 者仅在可分离提取 II/III 数据时纳入", "type": "B", "formal": "structured", "vis": "low", "ev": "E2"},
            {"id": "E6", "text": "仅英文", "type": "A", "formal": "rule", "vis": "high", "ev": "E0"},
            {"id": "E7", "text": "排除真菌/结核/创伤后/术后/转移性、仅发病率、仅 Stage I、病例报告、<10 例、综述/社论/预印本/会议摘要", "type": "A", "formal": "rule", "vis": "high", "ev": "E1"},
            {"id": "E8", "text": "会议摘要需有足够结局数据", "type": "C", "formal": "judgment", "vis": "low", "ev": "E2"},
        ],
        "findings": [
            {"text": "分期仅在 25/77 项（32.5%）报告，按分期的亚组分析不可行",
             "source": "Results",
             "layer": "E2",
             "kind": "事实缺失"},
            {"text": "治疗成功的定义不统一：有的要求症状缓解且无需再次手术，有的用影像清除或免于二次操作",
             "source": "Results / Supplementary Table S4",
             "layer": "E2",
             "kind": "结局定义"},
            {"text": "37/77 项为单臂或含超范围治疗臂，仅进入描述性综合；40 项进入配对与网络分析",
             "source": "Results",
             "layer": "E2",
             "kind": "分析组"},
            {"text": "33/145 臂（23%）为升级或挽救治疗；限制为一线臂后，thoracotomy 的死亡率优势失去显著性",
             "source": "Results",
             "layer": "E2",
             "kind": "分析组"},
        ],
        "unknown": {"n": 52, "d": 77, "note": "分期未报告，作者自报 32.5% 可判"},
    },
    {
        "id": "radiomics_prediction",
        "label": "影像组学 AI 预测病理缓解",
        "journal": "J Med Internet Res",
        "year": 2026,
        "pmid": "42596052",
        "pmcid": "PMC13472773",
        "design": "回顾/前瞻队列（模型验证研究）",
        "n_studies": 23,
        "n_publications": 23,
        "n_patients": 2004,
        "unit": "验证队列：互不重叠的验证队列各自独立；同一人群多个模型只取主模型（作者给出主模型层级：原研究指定者优先，否则取主验证队列 AUC 最高者）；重叠队列经敏感性分析排除",
        "analysis_group": "验证类型：内验证 vs 外验证；影像模态：CT vs PET/CT；算法亚组",
        "criteria": [
            {"id": "F1", "text": "病理确诊 NSCLC，接受新辅助免疫化疗并根治性切除", "type": "A", "formal": "rule", "vis": "high", "ev": "E1"},
            {"id": "F2", "text": "CT 或 PET/CT 衍生的 AI 模型（机器学习/深度学习）", "type": "A", "formal": "rule", "vis": "high", "ev": "E1"},
            {"id": "F3", "text": "目标条件：MPR（残留活肿瘤 ≤10%）与 pCR（0%）", "type": "A", "formal": "rule", "vis": "high", "ev": "E1"},
            {"id": "F4", "text": "参考标准：手术标本的标准病理评估", "type": "A", "formal": "structured", "vis": "high", "ev": "E1"},
            {"id": "F5", "text": "结局：敏感度、特异度、AUC", "type": "A", "formal": "structured", "vis": "high", "ev": "E1"},
            {"id": "F6", "text": "场景：回顾或前瞻队列，单中心、多中心或公共数据库", "type": "A", "formal": "rule", "vis": "high", "ev": "E1"},
            {"id": "F7", "text": "排除综述、病例报告、会议摘要、meta 分析、读者来信", "type": "A", "formal": "rule", "vis": "high", "ev": "E0"},
            {"id": "F8", "text": "排除非影像组学 AI 或目标条件不符", "type": "A", "formal": "rule", "vis": "high", "ev": "E1"},
            {"id": "F9", "text": "排除无法重建 2×2 列联表的数据", "type": "C", "formal": "judgment", "vis": "low", "ev": "E2"},
        ],
        "findings": [
            {"text": "三层单位规则：重叠队列按作者、机构、招募期交叉核对；多个互不重叠验证队列各自作为独立单位提取；同一人群多个模型只取主模型，主模型按“原研究指定优先，否则主验证队列 AUC 最高”确定",
             "source": "Methods / Outcome Measures",
             "layer": "E2",
             "kind": "单位"},
            {"text": "Ye 等两篇（[20,21]）可能重叠；排除两篇后 pCR 的 AUC 由 0.85 降至 0.83、敏感度由 0.77 降至 0.73，结论不变",
             "source": "Results",
             "layer": "E2",
             "kind": "单位"},
            {"text": "30 篇全文评估中 5 篇因无法提供 TP/FP/FN/TN 而被排除，属 C 型“数据充分性”条件",
             "source": "Study Selection",
             "layer": "E2",
             "kind": "数据充分性"},
            {"text": "“影像组学 AI”涵盖 LASSO、逻辑回归、随机森林、SVM、XGBoost、CNN、GBM、LDA 等；干预定义按模型家族处理",
             "source": "Results / Figure 3",
             "layer": "E2",
             "kind": "干预定义"},
            {"text": "13 项 pCR 研究中 11 项用内验证、5 项用外验证（部分两者兼有）；亚组按内/外验证、CT/PET-CT 与算法划分",
             "source": "Results",
             "layer": "E2",
             "kind": "分析组"},
        ],
        "unknown": None,
    },
]

# Second batch: six structurally distinct cases classified by a parallel
# workflow and independently verified; corrections applied in
# build_batch2_profiles.py.
BATCH2 = BASE / "cases" / "case_profiles_batch2.json"
if BATCH2.exists():
    CASES.extend(json.loads(BATCH2.read_text(encoding="utf-8")))

# Sorin 2024 reference: the eight audited exclusion criteria, carrying the
# classifications already used in boundary_taxonomy.py.
SORIN = {
    "id": "sorin2024",
    "label": "Sorin 2024（新辅助化疗免疫治疗）",
    "journal": "JAMA Oncol",
    "year": 2024,
    "n_items": 48,
    "n_trials": 43,
    "n_patients": None,
    "unknown_study": 0.714,
    "unknown_arm": 0.680,
    "criteria": [
        {"id": "P4", "formal": "structured", "vis": "high"},
        {"id": "D2", "formal": "rule", "vis": "high"},
        {"id": "D3", "formal": "rule", "vis": "low"},
        {"id": "D5", "formal": "judgment", "vis": "high"},
        {"id": "D6", "formal": "rule", "vis": "high"},
        {"id": "T1", "formal": "rule", "vis": "high"},
        {"id": "T2", "formal": "rule", "vis": "high"},
        {"id": "T3", "formal": "judgment", "vis": "low"},
    ],
}

CHOICES = [
    {
        "choice": "标准形式化",
        "sorin": "D5“无试验级证据”严格化后新增 6 条 T（宽松 0）",
        "robotic_vats": "“严重合并症”先写成模糊谓词，再按 NYHA/LVEF/FEV1 操作化",
        "lidocaine_vats": "“围术期”无剂量/时机阈值，按方案家族纳入",
        "cabg_nma": "9 个亚技术节点需先定义，节点即分析单位",
        "pediatric_empyema": "Stage II/III 写成数值判定规则（pH/葡萄糖/LDH）",
        "radiomics_prediction": "MPR/pCR 写成数值阈值（≤10%、0%），2×2 重建为数据条件",
        "amh_pcos": "参考标准按 Rotterdam/NIH/超声操作定义分别纳入；KQ2 合并值为操作定义的平均表现，未做阈值分层",
        "statin_crc": "postdiagnostic 暴露无统一定义；按暴露定义分类，并限定时变协变量研究做敏感性分析",
        "hearing_loss": "“prolonged”由原始研究定义（≥1 h/日、≥1 年、≥3 日/周等），无统一阈值",
        "bfr_umbrella": "年龄适用性写成分级判定（核心/支持/单独亚组），不是二值纳入",
        "floating_hip_ipd": "floating hip type A/B 分型；仅 type B（真浮动髋）",
        "tyg_pad": "TyG 分类切点由各研究定义；剂量反应需 ≥3 个定量类别",
    },
    {
        "choice": "事实接地",
        "sorin": "31 题名示 EGFR，摘要为混合人群；P4 撤回",
        "robotic_vats": "BRAVO 人群“NSCLC 或肺转移”只在表 1 出现",
        "lidocaine_vats": "Cui 2010/2011 手术栏写“thoracic surgery”，未写 VATS",
        "cabg_nma": "无逐研究边界发现；证据结构（8 RCT/124 观察）在摘要即见",
        "pediatric_empyema": "分期仅 25/77 报告，作者自报",
        "radiomics_prediction": "Ye 等两篇可能重叠，按作者、机构与招募期核对",
        "amh_pcos": "KQ3 有 3/11 项用 NIH 定义，与纳入标准的 Rotterdam 不符，正文未解释",
        "statin_crc": "摘要 prediagnostic CSM 的 CI 下限 0.78，正文 3.2 为 0.79",
        "hearing_loss": "语言限制写在检索策略，不在 PICO 清单；16/125 因仅自报证据被排除，但自报症状又列为次要结局",
        "bfr_umbrella": "无逐研究边界发现；年龄间接性按综述层面记录（3 篇含 <60 岁）",
        "floating_hip_ipd": "摘要称 11 项 retrospective cohort，正文称 case series；纳入设计写 prospective，实际无前瞻研究",
        "tyg_pad": "无逐研究边界发现；第 5 项研究因切点方式未进入剂量反应分析",
    },
    {
        "choice": "分析单位",
        "sorin": "48 项 vs 43 试验，单位选择未记录",
        "robotic_vats": "RVlob 3 篇合并为 1 试验，显式记录",
        "lidocaine_vats": "16 研究 = 16 试验，无单位问题",
        "cabg_nma": "臂/对照进入网络；单臂排除",
        "pediatric_empyema": "40 项比较研究进入 NMA，37 项仅描述",
        "radiomics_prediction": "三层规则：重叠队列、多个验证队列、多模型取主模型",
        "amh_pcos": "2×2 表/敏感度-特异度对；同一文献可多行；三 KQ 条目 100 > 92 项 unique studies",
        "statin_crc": "研究；3 项研究同时进入两个暴露窗口；207,041 为窗口贡献之和",
        "hearing_loss": "研究；12/60 进入主合并；年龄亚组中 2 项研究同时出现于两组",
        "bfr_umbrella": "综述；80 次重叠、36 项唯一原始研究，CCA 15.28%",
        "floating_hip_ipd": "受试者；7/12 项、112/271 例进入 IPD",
        "tyg_pad": "研究内暴露类别；4 项研究、17 个类别；同一研究多类别用聚类协方差",
    },
    {
        "choice": "分析组",
        "sorin": "27 个新辅助化疗臂 vs 8 个化疗免疫 RCT；P4 只影响对照臂",
        "robotic_vats": "QoL 仅 3 项有数据，定量合并用 2 项",
        "lidocaine_vats": "各时点 6–10 项试验，非同一组研究",
        "cabg_nma": "9 节点网络，RCT 与观察性同网",
        "pediatric_empyema": "33/145 臂为挽救治疗；一线臂敏感性分析改变结论",
        "radiomics_prediction": "内验证 vs 外验证；13 项 pCR 研究中 11 内、5 外",
        "amh_pcos": "三个 KQ；83/6/11 项",
        "statin_crc": "暴露窗口 × 结局四组；ACM/CSM 研究数不同",
        "hearing_loss": "主合并 12 项；年龄亚组 3 vs 8；设备亚组 3 vs 1",
        "bfr_umbrella": "四层证据等级；主结论仅用核心证据",
        "floating_hip_ipd": "描述性 12 项/271 例 vs IPD 7 项/112 例（嵌套）",
        "tyg_pad": "分类对比 5 项 vs 剂量反应 4 项/17 类别",
    },
]


def cell(formal: str, vis: str) -> str:
    high_formal = formal in {"rule", "structured"}
    high_vis = vis == "high"
    if high_formal and high_vis:
        return "高可形式化/高可见"
    if high_formal and not high_vis:
        return "高可形式化/低可见"
    if not high_formal and high_vis:
        return "低可形式化/高可见"
    return "低可形式化/低可见"


def summarize_case(case: dict) -> dict:
    criteria = case["criteria"]
    counts = {
        "criteria": len(criteria),
        "type_A": sum(1 for c in criteria if c["type"] == "A"),
        "type_B": sum(1 for c in criteria if c["type"] == "B"),
        "type_C": sum(1 for c in criteria if c["type"] == "C"),
        "rule": sum(1 for c in criteria if c["formal"] == "rule"),
        "structured": sum(1 for c in criteria if c["formal"] == "structured"),
        "judgment": sum(1 for c in criteria if c["formal"] == "judgment"),
        "vis_high": sum(1 for c in criteria if c["vis"] == "high"),
        "vis_low": sum(1 for c in criteria if c["vis"] == "low"),
    }
    cells = {}
    for c in criteria:
        name = cell(c["formal"], c["vis"])
        cells[name] = cells.get(name, 0) + 1
    counts["cells"] = cells
    return counts


def main() -> None:
    case_summaries = {c["id"]: summarize_case(c) for c in CASES}

    totals = {
        "criteria": sum(s["criteria"] for s in case_summaries.values()),
        "type_A": sum(s["type_A"] for s in case_summaries.values()),
        "type_B": sum(s["type_B"] for s in case_summaries.values()),
        "type_C": sum(s["type_C"] for s in case_summaries.values()),
        "rule": sum(s["rule"] for s in case_summaries.values()),
        "structured": sum(s["structured"] for s in case_summaries.values()),
        "judgment": sum(s["judgment"] for s in case_summaries.values()),
        "vis_high": sum(s["vis_high"] for s in case_summaries.values()),
        "vis_low": sum(s["vis_low"] for s in case_summaries.values()),
    }
    totals["formalizable"] = totals["rule"] + totals["structured"]
    totals["formalizable_share"] = round(totals["formalizable"] / totals["criteria"], 3)
    totals["vis_high_share"] = round(totals["vis_high"] / totals["criteria"], 3)

    new_cells = {}
    for s in case_summaries.values():
        for k, v in s["cells"].items():
            new_cells[k] = new_cells.get(k, 0) + v

    sorin_cells = {}
    for c in SORIN["criteria"]:
        name = cell(c["formal"], c["vis"])
        sorin_cells[name] = sorin_cells.get(name, 0) + 1

    combined = dict(new_cells)
    for k, v in sorin_cells.items():
        combined[k] = combined.get(k, 0) + v

    results = {
        "cases": CASES,
        "sorin": SORIN,
        "case_summaries": case_summaries,
        "totals_new_cases": totals,
        "cells_new_cases": new_cells,
        "cells_sorin": sorin_cells,
        "cells_combined": combined,
        "choices": CHOICES,
    }
    JSON_OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    # ------------------------------------------------------------ report
    lines = []
    lines.append("# 多案例对比：四个建模选择的复现")
    lines.append("")
    lines.append("**性质**：把 Sorin 2024 案例中得到的四个建模选择（标准形式化、事实接地、分析单位、分析组）与 2×2 边界分类，放到另外十一篇开放获取的 meta 分析上复核。本报告是跨案例的结构性验证，不是对每篇全部记录的穷尽审计；每个案例的分母都单独标明。")
    lines.append("")
    lines.append("## 一、案例特征")
    lines.append("")
    lines.append("| 案例 | 期刊/年 | 设计 | 研究数 | 文献数 | 例数 | 分析单位 | 分析组 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for c in CASES:
        patients = f"{c['n_patients']:,}" if c.get("n_patients") else "—"
        pubs = f"{c['n_publications']}"
        if c.get("pub_note"):
            pubs += f"（{c['pub_note']}）"
        lines.append(
            f"| {c['label']} | {c['journal']} {c['year']} | {c['design']} | {c['n_studies']} | "
            f"{pubs} | {patients} | {c['unit']} | {c['analysis_group']} |"
        )
    lines.append("")
    lines.append("## 二、标准的类型与可见性")
    lines.append("")
    lines.append("类型：A = 定义/分类命题；B = 流程/结构命题；C = 经验/判断命题。可形式化：rule = 无歧义谓词；structured = 结构化字段或时序谓词；judgment = 需文本解释或分析层判断。可见性：high = 题名/摘要可判；low = 需全文、表或分析层信息。")
    lines.append("")
    for c in CASES:
        s = case_summaries[c["id"]]
        lines.append(f"### {c['label']}")
        lines.append("")
        lines.append("| 标准 | 文本 | 类型 | 可形式化 | 可见性 | 证据层级 | 注 |")
        lines.append("|---|---|---|---|---|---|---|")
        for cr in c["criteria"]:
            lines.append(
                f"| {cr['id']} | {cr['text']} | {cr['type']} | {cr['formal']} | {cr['vis']} | {cr['ev']} | {cr.get('note','')} |"
            )
        lines.append("")
        lines.append(
            f"小计：{s['criteria']} 条；A {s['type_A']}、B {s['type_B']}、C {s['type_C']}；"
            f"rule {s['rule']}、structured {s['structured']}、judgment {s['judgment']}；"
            f"高可见 {s['vis_high']}、低可见 {s['vis_low']}。"
        )
        lines.append("")
    lines.append("## 三、四类建模选择的复现")
    lines.append("")
    headers = ["建模选择", "Sorin 2024"] + [c["label"] for c in CASES]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "---|" * len(headers))
    for ch in CHOICES:
        row = [ch["choice"], ch["sorin"]] + [ch[c["id"]] for c in CASES]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append("## 四、2×2 边界分类的跨案例汇总")
    lines.append("")
    lines.append("| | 高标题可见性 | 低标题可见性 |")
    lines.append("|---|---|---|")
    order = ["高可形式化/高可见", "高可形式化/低可见", "低可形式化/高可见", "低可形式化/低可见"]
    lines.append(f"| 高可形式化 | 新案例 {new_cells.get('高可形式化/高可见',0)}；Sorin {sorin_cells.get('高可形式化/高可见',0)} | "
                 f"新案例 {new_cells.get('高可形式化/低可见',0)}；Sorin {sorin_cells.get('高可形式化/低可见',0)} |")
    lines.append(f"| 低可形式化 | 新案例 {new_cells.get('低可形式化/高可见',0)}；Sorin {sorin_cells.get('低可形式化/高可见',0)} | "
                 f"新案例 {new_cells.get('低可形式化/低可见',0)}；Sorin {sorin_cells.get('低可形式化/低可见',0)} |")
    lines.append("")
    lines.append(f"十一个新案例共 {totals['criteria']} 条标准：可形式化 {totals['formalizable']} 条（{totals['formalizable_share']*100:.1f}%），高可见 {totals['vis_high']} 条（{totals['vis_high_share']*100:.1f}%）。高可形式化/高可见格占 {new_cells.get('高可形式化/高可见',0)}/{totals['criteria']}（{new_cells.get('高可形式化/高可见',0)/totals['criteria']*100:.1f}%）。")
    lines.append("")
    lines.append("## 五、边界发现与未知负载")
    lines.append("")
    lines.append("| 案例 | 边界发现 | 层级 | 类型 |")
    lines.append("|---|---|---|---|")
    for c in CASES:
        for f in c["findings"]:
            lines.append(f"| {c['label']} | {f['text']} | {f['layer']} | {f['kind']} |")
    lines.append("")
    lines.append("关键标准的未知负载（分母单列）：")
    lines.append("")
    lines.append("| 案例 | 关键标准 | 可判/总数 | 未知比例 | 来源 |")
    lines.append("|---|---|---|---|---|")
    for c in CASES:
        u = c.get("unknown")
        if u:
            lines.append(f"| {c['label']} | 见注 | {u['d']-u['n']}/{u['d']} | {u['n']/u['d']*100:.1f}% | {u['note']} |")
    lines.append(f"| Sorin 2024 | 8 条排除标准 × 研究层面 | — | 71.4% | 三值审计 |")
    lines.append(f"| Sorin 2024 | 8 条排除标准 × 臂层面 | — | 68.0% | 三值审计 |")
    lines.append("| Ren 2026（全记录） | 8 条标准 × 5 试验 | 34/40 | 15.0% | 5×8 三值审计 |")
    lines.append("")
    lines.append("## 六、主要发现")
    lines.append("")
    lines.append("第一，**四个建模选择在十一个独立案例中全部复现，但承担的角色不同。** 分析单位的形态至少有七种：研究（Liu 2026）、试验（Ren 2026 把 RVlob 的 3 篇文献合并为 1 个试验，并引用 Cochrane 指南说明）、验证队列（Jiang 2026 的多验证队列与主模型规则）、2×2 表（Jeong 2026 的三个 KQ，条目数 100 超过 92 项 unique studies）、综述（Chen 2026 的 80 次重叠对应 36 项原始研究，CCA 15.28%）、受试者（Lixa 2026 仅 7 项/112 例进入 IPD）与研究内暴露类别（Fu 2026 的 4 项研究 17 个类别）。同一问题在 Sorin 2024 中未被记录；Jiang T 2026 则有 3 项研究同时进入两个暴露窗口，207,041 例为窗口贡献之和。这说明单位不是“有没有”的问题，而是“是否记录”的问题。")
    lines.append("")
    lines.append("第二，**事实接地错误集中在“表 1 比题名更宽”的位置，并有更细的变体。** Sorin 的 31 是题名示 EGFR、摘要为混合人群；机器人案例的 BRAVO 是题名/标准示 NSCLC、表 1 示“NSCLC 或肺转移”；利多卡因案例的 Cui 2010/2011 是标准示 VATS、表 1 示“thoracic surgery”。另有三处不是人群边界，而是同一文献内部的数字或标签不一致：AMH 案例的 KQ3 有 3/11 项用 NIH 定义，与纳入标准的 Rotterdam 不符；他汀案例的 prediagnostic CSM 在摘要中 CI 下限 0.78、正文 3.2 为 0.79；浮动髋案例摘要称 11 项 retrospective cohort，正文称 case series。")
    lines.append("")
    lines.append("第三，**可形式化但不报告，等于不可审计。** 儿童脓胸的 Stage II/III 定义是本系列中最完整的判定规则（pH、葡萄糖、LDH 等阈值俱全），但分期只在 25/77 项（32.5%）报告，未知负载 67.5%，与 Sorin 的研究层面 71.4%、臂层面 68.0% 同量级。同类缺口还有：BFR 伞状综述的 9 篇综述无一报告 AOP/LOP 测量或运动体位；他汀案例的 13 项 postdiagnostic 研究无一按化疗意图分层；听力案例有 26/60 项未说明设备类型。规则可写，事实不在，是跨案例的稳定模式。")
    lines.append("")
    lines.append("第四，**分析组问题有多种形态。** Sorin 与儿童脓胸是“治疗线/臂”的形态：27 个化疗臂 vs 8 个 RCT；33/145 臂为挽救治疗，限制为一线后 thoracotomy 的死亡率优势消失。CABG 是“网络节点”的形态：9 个亚技术节点、RCT 与观察性同网、转递性只部分成立。BFR 伞状综述是“证据层级”的形态：核心/支持/单独康复四层，主结论仅用核心证据。IPD 案例是“嵌套子集”的形态：7/12 项、112/271 例。TyG 案例是“剂量反应子集”的形态：4/5 项研究、17 个类别。")
    lines.append("")
    lines.append("第五，**标准清单不等于标准全集。** 机器人案例的英语限制写在检索方法，利多卡因案例的语言限制写在局限，听力案例的语言限制写在检索策略，都不在纳入/排除标准清单里；听力案例还有 16/125 因仅自报证据被排除，但自报症状又列为次要结局。形式化若只读“Eligibility criteria”一节，会漏掉实际执行的限制，甚至会得到与正文相反的语言政策。")
    lines.append("")
    lines.append("第六，**资格判定本身可以是多值的。** Chen 2026 把年龄不直接符合的综述降为支持/敏感性证据或单独临床亚组，主结论只用核心证据；Lixa 2026 的 IPD 组是描述性组的嵌套子集（7/12 项、112/271 例）；Fu 2026 的剂量反应组只含 4/5 项研究。“进入分析”不是单一状态，三值 T/F/U 之外还需要分级纳入语义。")
    lines.append("")
    lines.append("## 七、限制")
    lines.append("")
    lines.append("- 十一个新案例中，Ren 2026 另做了 5×8 全记录三值审计（未知 15.0%），其余十个只做标准层分类与已报告的记录层事实核对；各案例的 T/F/U 分布不可直接比较。")
    lines.append("- 未知负载的分母不同：Sorin 是 8 条标准 × 48 项，儿童脓胸是分期一项 × 77 项，利多卡因是 VATS 一项 × 16 项，机器人是人群一项 × 5 项。只可比量级，不可比精确值。")
    lines.append("- CABG 的 132 项研究清单在补充材料，未逐项核对；该案例只用于分析层结构（节点、网络、转递性）。")
    lines.append("- 标准分类由单一评审者完成，未计算评分者一致性。")
    lines.append("")
    lines.append("## 八、文件")
    lines.append("")
    lines.append("- [cross_case_analysis.py](_research/cross_case_analysis.py) — 本报告的数据与计算脚本。")
    lines.append("- [cross_case_results.json](_research/cross_case_results.json) — 结构化结果。")
    lines.append("- [cases/](_research/cases/) — 四个案例的全文 XML 与标准抽取文本。")
    lines.append("")
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")

    print("Per-case criteria:", {k: v["criteria"] for k, v in case_summaries.items()})
    print("Totals:", totals)
    print("Cells new:", new_cells)
    print("Cells Sorin:", sorin_cells)
    print("Cells combined:", combined)
    print(f"JSON: {JSON_OUT}")
    print(f"MD:   {MD_OUT}")


if __name__ == "__main__":
    main()
