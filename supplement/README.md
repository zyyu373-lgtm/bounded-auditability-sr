# 补充材料包（v0.3）

**对应稿件**：`manuscript/论文初稿-医学知识有界公理化.md`（v0.3，2026-11-25）

**公开仓库**：https://github.com/zyyu373-lgtm/bounded-auditability-sr

**性质**：本包把稿件引用的审计报告、派生数据与脚本集中存放，便于复核。GitHub 仓库是当前工作归档；投稿前将另行存入 OSF 或 Zenodo，并在稿件的数据可用性声明中补 DOI。

## 一、目录

| 目录 | 内容 |
|---|---|
| `审计报告/` | 三值审计、全记录审计汇总、跨案例复核、边界分类、事实接地协议、修订实验、形式模型原型的报告副本 |
| `数据/` | `audits_batch3.json`（Fu/Lixa/Chen 的逐格审计）、`cross_case_results.json`（11 案例标准层分类）、`case_profiles_batch2.json`（6 个案例的结构化档案）、`boundary_taxonomy_results.json`、`fact_grounding_results.json`、`revision_results.json`、`p4_abstracts.json`、`formal_model_results.json`、`sorin2024_included_consistency.csv` |
| `代码/` | 形式模型、跨案例分析、审计报告生成、修订实验、事实接地、边界分类、筛选协议检查、校验脚本 |
| `代码/cases/` | 脚本直接读取的两个 JSON：`audits_batch3.json`、`case_profiles_batch2.json` |
| `版本/` | v0.1 备份，用于对照修订 |

本包不包含受版权约束的全文 XML。稿件只共享派生事实表、PMCID 与检索/提取规则。

## 二、Sorin 内部编号映射（表 S1，初版）

Sorin 等（2024）的内部参考文献编号与本文的 S 编号对应如下。未列出的编号（S11、S22、S33、S42、S50、S58、S59、S61–S65）待从 Sorin eTable 3 与主文参考文献表补全；在补全之前，正文只把它们当作 Sorin 内部编号使用，不声称完整出处。

| S 编号 | 研究 | 出处 | PMID/DOI | 在本文中的角色 |
|---|---|---|---|---|
| S24 | Chen 等, 2018 | 中华肿瘤杂志 | PMID 29502374 | P4/T2 摘要级冲突；单臂化疗对照 |
| S31 | Xiong 等, 2020 | J Int Med Res | PMID 31885349 | P4 撤回；T2 保留 |
| S35 | Zhong 等, 2019 | J Clin Oncol | 见 Sorin eTable 3；PMID 待补 | P4/T2 摘要级冲突；EMERGING-CTONG 1103 |
| S36 | Zhong 等, 2023 | Signal Transduct Target Ther | 见 Sorin eTable 3；PMID 待补 | 同一试验的最终 OS 分析 |
| S46 | Gu 等, 2022 | Front Immunol | PMID 36059450；NCT04197076 | D2 暂定冲突；开放、三臂、非随机研究 |

## 三、D5 的六篇会议摘要（表 S2，待补）

Sorin 的 Results 说明，2023 年 ASCO、ESMO、ELCC、WCLC 与 AACR 的会议摘要被用于更新已发表随机对照试验或纳入新随机对照试验。本文的宽松读法认为这些摘要不落入 D5；严格读法把它们全部视为落入，作为压力测试。六篇摘要对应 Sorin 内部编号 S11、S61–S65；逐篇的试验、会议与试验级证据待补。补全之前，稿件不逐篇声称其内容，只报告 0/6 的读法差异。

## 四、数据字典（主要文件）

### `数据/audits_batch3.json`

- `audit.criteria`：审计使用的标准 ID 列表。
- `audit.units`：判定单元列表（研究或综述）。
- `audit.cells`：逐格记录，字段包括 `unit`、`criterion`、`status`（T/F/U）、`ev`（证据来源）、`note`（说明）。
- `audit.tiers`：仅 Chen 案例使用，记录核心/支持/单独亚组等层级。
- `verification`：核验代理的检查数与意见列表。

### `数据/cross_case_results.json`

- 每个案例的标准数、A/B/C 分类、rule/structured/judgment 分类、高/低可见性计数。
- 2×2 汇总与案例层比例。

### `数据/case_profiles_batch2.json`

- 六个第二批案例的结构化档案：设计、单位、分析组、关键发现、未知说明、来源。

### `数据/formal_model_results.json`

- 四种模式（记录/臂层面 × D5 宽松/严格）的冲突原子、推导树与来源。

### `数据/sorin2024_included_consistency.csv`

- 48 条纳入记录的事实表；字段包括编号、作者、年份、设计、人群、治疗、发表类型、来源与内部置信标记。

## 五、复现步骤

1. 使用 Python 3.10+（开发环境为 Python 3.13）；脚本只用标准库。
2. 进入代码目录：

```bash
cd supplement/代码
python formal_model_sorin2024.py
python revision_experiment.py
python fact_grounding_audit.py
python boundary_taxonomy.py
python build_audit_reports.py
python cross_case_analysis.py
```

3. 筛选协议检查从仓库根目录运行：

```bash
python supplement/代码/check_screening_protocol.py
```

4. 预期输出：
   - 形式模型：记录层面宽松 11、臂层面宽松 6、记录层面严格 17、臂层面严格 12 个冲突原子。
   - 修订实验：事实修订撤回 1 条；单位修订撤回 5 条；D5 严格化新增 6 条；P4 例外在记录层面撤回 3 条、在臂层面撤回 3 条。
   - 事实接地：7 条 E1、4 条 E0、1 条 RETRACTED。
   - 全记录审计：Ren 15.0%、Fu 8.3%、Lixa 16.7%、Chen 11.1%；Sorin 记录层面 71.4%、臂层面 68.0%。
   - 跨案例：114 条标准中 104 条可形式化（91.2%）、70 条高可见（61.4%）；122 条 2×2 为 75/35/1/11。
   - 汇总：1,078 个编码、694 个唯一格子、79 个独立单位。

5. 脚本会把报告副本写到 `supplement/` 根目录；仓库中的正式副本在 `审计报告/`。若重复运行，可用 `git status` 查看生成文件，不要覆盖归档副本。

## 六、已知缺口

- 表 S1 与表 S2 未补全；S11、S22、S33、S42、S50、S58、S59、S61–S65 仍无法解析到完整出处；S35/S36 的 PMID 待补。
- 48 条记录、43 项试验、54 个臂的逐条映射尚未完成。
- 114 条标准的分类由单一评审者完成，没有第二编码者与 kappa。
- 三值审计没有单独编码 NA；记录不足率是保守上界。
- 单臂化疗合并的敏感性分析尚未完成。
- S46/D2 的 D1/D2 分类待作者澄清；表 1a 暂标“待核对”。
- 脚本的路径与运行说明只在本机与仓库布局下验证过，尚未做容器化或跨平台测试。
- 尚无 OSF/Zenodo DOI；GitHub 是当前工作归档。

## 七、许可与归档（建议）

- 文本与派生数据：CC BY 4.0。
- 代码：MIT。
- 归档：投稿前存入 OSF 或 Zenodo，补 DOI；GitHub 仓库作为工作版本保留。

上述许可与归档方案为建议，最终由作者决定。
