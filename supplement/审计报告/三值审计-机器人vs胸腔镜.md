# 三值审计：机器人 vs 胸腔镜（Ren 2026）

**性质**：对 Ren 2026 的 5 个试验 × 8 条标准做全记录三值审计，与 Sorin 2024 的 48×8 审计同口径（T 满足、F 违反、U 记录不足）。两案例的 T/F 语义不同（Sorin 的 8 条是排除标准，T 表示被排除），因此只比较未知负载，不比较 T/F 分布。

## 一、试验

| 试验 | 文献 | 例数 | 人群 | 设计 |
|---|---|---|---|---|
| BRAVO | Terra 2022 | 76 | Resectable NSCLC or lung metastasis (tumor <5 cm) | Single-center, open-label RCT |
| RVlob | Jin 2022; Jin 2023; Niu 2024 | 320 | Resectable NSCLC (clinical stage I–IIIa) | Single-center, open-label RCT |
| Catelli | Catelli 2023 | 75 | Early-stage NSCLC (cT1–T2, N0–N1) | Single-center, prospective RCT |
| RAVAL | Patel 2023 | 164 | Early-stage NSCLC (clinical stage I–IIIa) | Multicenter, double-blind RCT |
| ROMAN | Veronesi 2021 | 77 | Early-stage NSCLC (cT1–T2, N0–N1) | Multicenter RCT, early termination for futility |

## 二、审计结果

| 标准 | 文本 | 证据层级 | T | F | U |
|---|---|---|---|---|---|
| R1 | RCT | E0 | 5 | 0 | 0 |
| R2 | 成人 ≥18 岁 | E1 | 5 | 0 | 0 |
| R3 | 病理确诊 NSCLC | E1 | 4 | 0 | 1 |
| R4 | VATS vs RATS | E0 | 5 | 0 | 0 |
| R5 | 至少报告 1 项预设结局 | E1 | 5 | 0 | 0 |
| R6 | 非 RCT 的排除条件不触发 | E0 | 5 | 0 | 0 |
| R7 | 数据足以进入至少 1 项合并 | E2 | 5 | 0 | 0 |
| R8 | 严重合并症的排除标准已按 NYHA/LVEF/FEV1 操作化并应用 | E2 | 0 | 0 | 5 |

合计：40 个判定单元，T 34、F 0、U 6；未知负载 **15.0%**。

## 三、未知单元

| 试验 | 标准 | 状态 | 说明 |
|---|---|---|---|
| BRAVO | R3 | U | 表 1 人群为“NSCLC or lung metastasis”；是否仅 NSCLC 亚组进入分析未报告 |
| BRAVO | R8 | U | 表 1 未报告该试验的合并症排除标准 |
| RVlob | R8 | U | 表 1 未报告该试验的合并症排除标准 |
| Catelli | R8 | U | 表 1 未报告该试验的合并症排除标准 |
| RAVAL | R8 | U | 表 1 未报告该试验的合并症排除标准 |
| ROMAN | R8 | U | 表 1 未报告该试验的合并症排除标准 |

## 四、与 Sorin 2024 的对比

| 案例 | 设计 | 单元数 | 未知负载 |
|---|---|---|---|
| Sorin 2024（研究层面） | 混合 | 384 | 71.4% |
| Sorin 2024（臂层面） | 混合 | 384 | 68.0% |
| Ren 2026 | 仅 RCT | 40 | 15.0% |

## 五、解释

第一，未知负载从约七成降到一成半，主要不是规则更简单，而是**设计与报告更同质**：5 个试验都是 RCT，题名与表 1 覆盖了设计、人群、干预与结局，只有 R8（严重合并症的操作化）在表 1 中完全没有记录。

第二，唯一的人群边界是 BRAVO：表 1 写“NSCLC or lung metastasis”，与标准“病理确诊 NSCLC”不完全一致；是否仅 NSCLC 亚组进入分析，需要全文或作者澄清。这与 Sorin 的 31 是同一类问题——题名/标准与表级事实的粒度差。

第三，F=0 不表示“没有问题”，而表示在这 8 条标准与 5 个试验的组合中，已发表记录足以判定“满足”或“未知”，没有足以判定“违反”的单元。审计报告应写成“无已知违反 + 15% 未知”，而不是“全部合格”。

## 六、限制

- 事实来源限于 Ren 2026 的主文与表 1、表 2；未读 5 个试验的原始全文。
- R8 的 5 个 U 可能经全文核对转为 T，也可能发现某个试验未按该标准排除合并症。
- 单一评审者，未计算评分者一致性。

## 七、文件

- [three_valued_robotic.py](_research/three_valued_robotic.py) — 审计脚本。
- [three_valued_robotic_results.json](_research/three_valued_robotic_results.json) — 审计数据。
