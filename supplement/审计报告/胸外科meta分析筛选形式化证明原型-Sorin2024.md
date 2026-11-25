# 胸外科 meta 分析筛选的形式化证明原型：Sorin 等（2024）

**性质**：桌面原型。把 17 条筛选标准中的排除类标准写成规则，把纳入清单、题名与补充材料 eTable 3 的标注写成事实，用一个小型前向推理引擎生成冲突的证明轨迹。它不重跑筛选，不重做 meta 分析，也不读取患者级数据。

**对象**：Sorin M, et al. Neoadjuvant Chemoimmunotherapy for NSCLC: A Systematic Review and Meta-Analysis. *JAMA Oncology*. 2024. DOI 10.1001/jamaoncol.2024.0057；PMID 38512301；PMCID PMC10958389。

**输入**：48 项纳入项；17 条结构化标准；eTable 3 中 6 项研究的臂级标注。

**输出**：4 种模式（研究层面／臂层面 × D5 宽松／严格）的冲突清单、逐条证明轨迹与单位对照。

## 一、原型做了什么

原型把“标准—事实—纳入集”三者放进同一个形式系统：

1. **规则**：把 P4、D2、D3、D5、D6、T1、T2、T3 八条排除标准写成蕴含式。
2. **事实**：把“哪项研究被纳入”“题名说明它用了什么治疗／什么设计／什么人群”“eTable 3 把它标成哪个臂”写成带来源与置信度的 ground facts。
3. **推理**：前向链推导 `ExcludedBy(item, criterion)`；臂级违例经 `ArmOf` 传播到父研究；若父研究同时 `Included`，则推出 `Conflict`。
4. **证明轨迹**：每个 `Conflict` 都保留完整推导链，可逐步回放到原始事实。

核心结果：研究层面推出 6 项高置信直接冲突（22、24、31、35、36、46）与 2 项中置信潜在冲突（33、42）；臂层面把 22 的 T1、24／33／35／36 的 T2 消解，但 24／35／36 的 P4 与 46 的 D2 保留；31 与 42 因未取得臂级标注而保留研究层面事实。

| 模式 | 冲突原子 | 涉及研究 | 高置信研究 | 中置信研究 |
|---|---|---|---|---|
| 研究层面 / trial_level | 11 | 8 | 6 | 2 |
| 臂层面 / trial_level | 6 | 6 | 5 | 1 |
| 研究层面 / strict | 17 | 14 | 6 | 8 |
| 臂层面 / strict | 12 | 12 | 5 | 7 |

## 二、形式系统

### 2.1 类型与谓词

| 谓词 | 含义 | 元数 |
|---|---|---|
| `Included(s)` | 研究 s 在纳入清单中 | 1 |
| `ArmOf(a, s)` | 臂／条目 a 属于研究 s | 2 |
| `Design(x, d)` | 条目 x 的设计为 d | 2 |
| `Population(x, p)` | 条目 x 的人群为 p | 2 |
| `Treatment(x, t)` | 条目 x 的治疗为 t | 2 |
| `PublicationType(x, pt)` | 条目 x 的发表类型为 pt | 2 |
| `ExcludedBy(x, c)` | 条目 x 违反排除标准 c | 2 |
| `Conflict(s, c)` | 纳入研究 s 与排除标准 c 冲突 | 2 |
| `NeedsFullText(x, c)` | 条目 x 在标题层面不足以判定标准 c | 2 |

`Design` 取值：`rct`、`observational`、`retrospective`、`unknown`。`Population` 取值：`egfr_mutant_only`、`mixed`、`unknown`。`Treatment` 取值：`chemotherapy`、`chemoradiotherapy`、`molecular_targeted_therapy`、`immunotherapy_monotherapy`、`unknown`。

### 2.2 规则

| 规则 | 头 | 体 | 标准文本 |
|---|---|---|---|
| `R_P4` | `ExcludedBy(?x, P4)` | `Population(?x, egfr_mutant_only)` | Studies that included only patients with NSCLC with EGFR variants were excluded. |
| `R_D2` | `ExcludedBy(?x, D2)` | `Design(?x, observational)` | Observational studies were excluded. |
| `R_D3` | `ExcludedBy(?x, D3)` | `Design(?x, retrospective)` | Retrospective studies were excluded. |
| `R_T1` | `ExcludedBy(?x, T1)` | `Treatment(?x, chemoradiotherapy)` | Trials reporting the use of neoadjuvant radiotherapy, including chemoradiotherapy, were excluded. |
| `R_T2` | `ExcludedBy(?x, T2)` | `Treatment(?x, molecular_targeted_therapy)` | Trials reporting the use of molecular targeted therapy were excluded. |
| `R_T3` | `ExcludedBy(?x, T3)` | `Treatment(?x, immunotherapy_monotherapy)` | Trials reporting the use of immunotherapy monotherapy were excluded. |
| `R_D5` | `ExcludedBy(?x, D5)` | `PublicationType(?x, abstract_without_trial_level_evidence)` | Abstracts without trial-level evidence were excluded. |
| `R_D6` | `ExcludedBy(?x, D6)` | `PublicationType(?x, editorial_comment_gray)` | Editorials, comments, and gray literature were excluded. |
| `R_ARM` | `ExcludedBy(?s, ?c)` | `ArmOf(?a, ?s); ExcludedBy(?a, ?c)` | An arm-level violation propagates to the parent study. |
| `R_CONFLICT` | `Conflict(?s, ?c)` | `Included(?s); ExcludedBy(?s, ?c)` | An included study that violates an exclusion criterion is a conflict. |
| `R_NEEDS_FULL_TEXT_D3` | `NeedsFullText(?x, D3)` | `Design(?x, unknown)` | Design unknown at title level; full text is needed to decide D3. |

`R_ARM` 与 `R_CONFLICT` 是结构规则，不对应具体标准；`R_NEEDS_FULL_TEXT_D3` 只标记“标题层面不可判定”，不产生冲突。

### 2.3 事实与来源

下表只列驱动冲突的属性事实；`Included`、`Year`、`PublicationType` 对 48 项逐条断言，未在表中展开。

| 谓词 | 参数 | 来源 | 置信 | 注 |
|---|---|---|---|---|
| `Design` | `22, rct` | title | high | Title: 'a phase 3 randomised trial'. |
| `Treatment` | `22, chemoradiotherapy` | title | high | Title: 'Induction chemoradiation'. |
| `Population` | `24, egfr_mutant_only` | abstract (PubMed) | high | 86 patients with stage IIIA EGFR-mutant lung adenocarcinoma; all patients were EGFR-mutant. |
| `Treatment` | `24, molecular_targeted_therapy` | title/abstract | high | Erlotinib vs pemetrexed + cisplatin; the erlotinib arm is molecular targeted therapy. |
| `Population` | `31, mixed` | abstract (Crossref) | high | 31 patients: 15 EGFR-mutant received erlotinib; 16 EGFR-wild-type received cisplatin-based chemotherapy. The title describes the erlotinib subgroup, not the whole study population. |
| `Treatment` | `31, molecular_targeted_therapy` | title/abstract | high | Erlotinib was given to the EGFR-mutant subgroup. |
| `Treatment` | `33, molecular_targeted_therapy` | title | medium | Title: 'antiangiogenic therapy'; eTable 3 extracts the chemotherapy arm, so this is a study-level potential conflict. |
| `Population` | `35, egfr_mutant_only` | title | high | Title: 'EGFR-mutant'. |
| `Treatment` | `35, molecular_targeted_therapy` | title | high | Title: 'erlotinib versus gemcitabine + cisplatin'. |
| `Population` | `36, egfr_mutant_only` | title | high | Title: 'EGFR-mutant'. |
| `Treatment` | `36, molecular_targeted_therapy` | title | high | Title: 'erlotinib versus gemcitabine + cisplatin'. |
| `Treatment` | `42, molecular_targeted_therapy` | title | medium | Title: 'surgery and erlotinib'; erlotinib is postoperative, so the T2 reading is ambiguous. |
| `Design` | `46, observational` | title | high | Title: 'open, observational, three-arm clinical study'. |
| `Design` | `50, unknown` | title | low | Title does not report design; full text needed. |
| `Design` | `58, unknown` | title | low | Title does not report design; full text needed. |
| `Design` | `59, unknown` | title | low | Title does not report design; full text needed. |
| `Treatment` | `22_chemo, chemotherapy` | eTable 3 | high | Chemotherapy / Single-arm / Cisplatin + docetaxel. |
| `Design` | `22_chemo, rct` | eTable 3 | medium | Parent study is a randomised trial; the extracted arm is a chemotherapy arm. |
| `Treatment` | `24_chemo, chemotherapy` | eTable 3 | high | Chemotherapy / Single-arm / Pemetrexed + cisplatin. |
| `Population` | `24_chemo, egfr_mutant_only` | eTable 3 | high | eTable 3 population: EGFR mutant. |
| `Treatment` | `33_chemo, chemotherapy` | eTable 3 | high | Chemotherapy / Single-arm / Cisplatin + vinorelbine. |
| `Treatment` | `35_chemo, chemotherapy` | eTable 3 | high | Chemotherapy / Single-arm / Gemcitabine + cisplatin. |
| `Population` | `35_chemo, egfr_mutant_only` | eTable 3 | high | eTable 3 population: EGFR mutant. |
| `Treatment` | `36_chemo, chemotherapy` | eTable 3 | high | Chemotherapy / Single-arm / Gemcitabine + cisplatin. |
| `Population` | `36_chemo, egfr_mutant_only` | eTable 3 | high | eTable 3 population: EGFR mutant. |
| `Treatment` | `46_chemo, chemotherapy` | eTable 3 | high | Chemotherapy / Single-arm / Chemotherapy. |
| `Design` | `46_chemo, observational` | eTable 3 | high | Parent study is observational; the arm inherits the design. |

## 三、研究层面的证明

以下 6 项是研究层面的高置信直接冲突。每张表都是一条可逐步回放的推导链：从事实出发，经规则，得到 `Conflict`。

### 3.1 六项直接冲突

#### 46 / D2（置信：high）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(46)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `Design(46, observational)` | 事实；来源：title；置信：high；注：Title: 'open, observational, three-arm clinical study'. |
| 3 | `ExcludedBy(46, D2)` | 规则 `R_D2`：Observational studies were excluded. |
| 4 | `Conflict(46, D2)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

#### 24 / P4（置信：high）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(24)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `Population(24, egfr_mutant_only)` | 事实；来源：abstract (PubMed)；置信：high；注：86 patients with stage IIIA EGFR-mutant lung adenocarcinoma; all patients were EGFR-mutant. |
| 3 | `ExcludedBy(24, P4)` | 规则 `R_P4`：Studies that included only patients with NSCLC with EGFR variants were excluded. |
| 4 | `Conflict(24, P4)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

#### 24 / T2（置信：high）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(24)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `Treatment(24, molecular_targeted_therapy)` | 事实；来源：title/abstract；置信：high；注：Erlotinib vs pemetrexed + cisplatin; the erlotinib arm is molecular targeted therapy. |
| 3 | `ExcludedBy(24, T2)` | 规则 `R_T2`：Trials reporting the use of molecular targeted therapy were excluded. |
| 4 | `Conflict(24, T2)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

#### 31 / T2（置信：high）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(31)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `Treatment(31, molecular_targeted_therapy)` | 事实；来源：title/abstract；置信：high；注：Erlotinib was given to the EGFR-mutant subgroup. |
| 3 | `ExcludedBy(31, T2)` | 规则 `R_T2`：Trials reporting the use of molecular targeted therapy were excluded. |
| 4 | `Conflict(31, T2)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

#### 35 / P4（置信：high）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(35)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `Population(35, egfr_mutant_only)` | 事实；来源：title；置信：high；注：Title: 'EGFR-mutant'. |
| 3 | `ExcludedBy(35, P4)` | 规则 `R_P4`：Studies that included only patients with NSCLC with EGFR variants were excluded. |
| 4 | `Conflict(35, P4)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

#### 35 / T2（置信：high）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(35)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `Treatment(35, molecular_targeted_therapy)` | 事实；来源：title；置信：high；注：Title: 'erlotinib versus gemcitabine + cisplatin'. |
| 3 | `ExcludedBy(35, T2)` | 规则 `R_T2`：Trials reporting the use of molecular targeted therapy were excluded. |
| 4 | `Conflict(35, T2)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

#### 36 / P4（置信：high）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(36)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `Population(36, egfr_mutant_only)` | 事实；来源：title；置信：high；注：Title: 'EGFR-mutant'. |
| 3 | `ExcludedBy(36, P4)` | 规则 `R_P4`：Studies that included only patients with NSCLC with EGFR variants were excluded. |
| 4 | `Conflict(36, P4)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

#### 36 / T2（置信：high）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(36)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `Treatment(36, molecular_targeted_therapy)` | 事实；来源：title；置信：high；注：Title: 'erlotinib versus gemcitabine + cisplatin'. |
| 3 | `ExcludedBy(36, T2)` | 规则 `R_T2`：Trials reporting the use of molecular targeted therapy were excluded. |
| 4 | `Conflict(36, T2)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

#### 22 / T1（置信：high）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(22)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `Treatment(22, chemoradiotherapy)` | 事实；来源：title；置信：high；注：Title: 'Induction chemoradiation'. |
| 3 | `ExcludedBy(22, T1)` | 规则 `R_T1`：Trials reporting the use of neoadjuvant radiotherapy, including chemoradiotherapy, were excluded. |
| 4 | `Conflict(22, T1)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

### 3.2 P4 的最终核对：撤回 31，确认 24

原型最初按题名把 31 断定为 `Population(31, egfr_mutant_only)`，并推出 P4 冲突。核对摘要后，这一事实被撤回：该研究共 31 例患者，15 例 EGFR 突变者接受厄洛替尼，16 例 EGFR 野生型者接受含铂双药化疗；题名描述的是厄洛替尼亚组，不是整个研究人群。因此 P4（“仅纳入 EGFR 变异患者的研究被排除”）对 31 不成立，`Population` 事实改为 `mixed`，P4 证明撤回。31 的 T2 冲突仍然成立，因为研究报告了厄洛替尼的使用。

随后核对 24 的摘要：86 例ⅢA 期 EGFR 突变型肺腺癌患者随机分为厄洛替尼组与培美曲塞＋顺铂组，全部患者均为 EGFR 突变型；P4 成立。35/36 的摘要也确认人群为 EGFR 外显子 19 或 21 突变、R0 切除的ⅢA-N2 NSCLC；P4 成立，且 35/36 是同一试验的两次发表。因此 P4 的稳健集合为 24、35、36，按试验计为 2 项（24 与 EMERGING-CTONG 1103）。

这是原型条件性的一次具体演示：证明对断言事实成立，但断言事实可能来自题名的误读；核对摘要既可能撤回证明，也可能确认证明。

### 3.3 中置信潜在冲突

33 与 42 的冲突依赖题名的字面解读，置信度为 medium；它们在臂层面是否消解，见第四节。

#### 33 / T2（置信：medium）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(33)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `Treatment(33, molecular_targeted_therapy)` | 事实；来源：title；置信：medium；注：Title: 'antiangiogenic therapy'; eTable 3 extracts the chemotherapy arm, so this is a study-level potential conflict. |
| 3 | `ExcludedBy(33, T2)` | 规则 `R_T2`：Trials reporting the use of molecular targeted therapy were excluded. |
| 4 | `Conflict(33, T2)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

#### 42 / T2（置信：medium）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(42)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `Treatment(42, molecular_targeted_therapy)` | 事实；来源：title；置信：medium；注：Title: 'surgery and erlotinib'; erlotinib is postoperative, so the T2 reading is ambiguous. |
| 3 | `ExcludedBy(42, T2)` | 规则 `R_T2`：Trials reporting the use of molecular targeted therapy were excluded. |
| 4 | `Conflict(42, T2)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

### 3.4 标题层面不可判定

50、58、59 的题名没有报告研究设计，模型只能推出 `NeedsFullText(·, D3)`，不能推出冲突。这说明“未判定”与“无冲突”是两件事。

- `NeedsFullText(50, D3)` — 由 `Design(50, unknown)` 推出；需全文核实 D3。
- `NeedsFullText(58, D3)` — 由 `Design(58, unknown)` 推出；需全文核实 D3。
- `NeedsFullText(59, D3)` — 由 `Design(59, unknown)` 推出；需全文核实 D3。

## 四、臂层面的证明

臂层面把每个被 eTable 3 重新分类的研究拆成一个臂条目，用 `ArmOf(arm, study)` 连接到父研究。若臂级违例成立，`R_ARM` 把它传播到父研究；若臂级事实不再触发排除规则，父研究的该条冲突就不出现。

### 4.1 保留的冲突

#### 4.1.1 臂级事实仍触发

24、35、36 的 P4 来自臂级人群仍为 EGFR 突变仅限；46 的 D2 来自观察性设计不因按臂提取而改变。

##### 46 / D2（置信：high）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(46)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `ArmOf(46_chemo, 46)` | 事实；来源：eTable 3；置信：high |
| 3 | `Design(46_chemo, observational)` | 事实；来源：eTable 3；置信：high；注：Parent study is observational; the arm inherits the design. |
| 4 | `ExcludedBy(46_chemo, D2)` | 规则 `R_D2`：Observational studies were excluded. |
| 5 | `ExcludedBy(46, D2)` | 规则 `R_ARM`：An arm-level violation propagates to the parent study. |
| 6 | `Conflict(46, D2)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

##### 24 / P4（置信：high）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(24)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `ArmOf(24_chemo, 24)` | 事实；来源：eTable 3；置信：high |
| 3 | `Population(24_chemo, egfr_mutant_only)` | 事实；来源：eTable 3；置信：high；注：eTable 3 population: EGFR mutant. |
| 4 | `ExcludedBy(24_chemo, P4)` | 规则 `R_P4`：Studies that included only patients with NSCLC with EGFR variants were excluded. |
| 5 | `ExcludedBy(24, P4)` | 规则 `R_ARM`：An arm-level violation propagates to the parent study. |
| 6 | `Conflict(24, P4)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

##### 35 / P4（置信：high）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(35)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `ArmOf(35_chemo, 35)` | 事实；来源：eTable 3；置信：high |
| 3 | `Population(35_chemo, egfr_mutant_only)` | 事实；来源：eTable 3；置信：high；注：eTable 3 population: EGFR mutant. |
| 4 | `ExcludedBy(35_chemo, P4)` | 规则 `R_P4`：Studies that included only patients with NSCLC with EGFR variants were excluded. |
| 5 | `ExcludedBy(35, P4)` | 规则 `R_ARM`：An arm-level violation propagates to the parent study. |
| 6 | `Conflict(35, P4)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

##### 36 / P4（置信：high）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(36)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `ArmOf(36_chemo, 36)` | 事实；来源：eTable 3；置信：high |
| 3 | `Population(36_chemo, egfr_mutant_only)` | 事实；来源：eTable 3；置信：high；注：eTable 3 population: EGFR mutant. |
| 4 | `ExcludedBy(36_chemo, P4)` | 规则 `R_P4`：Studies that included only patients with NSCLC with EGFR variants were excluded. |
| 5 | `ExcludedBy(36, P4)` | 规则 `R_ARM`：An arm-level violation propagates to the parent study. |
| 6 | `Conflict(36, P4)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

#### 4.1.2 无臂级标注、保留研究层面事实

31 与 42 的 eTable 3 臂级标注未取得，臂模式对它们没有臂级条目，因此保留研究层面事实。它们的臂层面状态是“未派生”，不是“臂级仍触发”。

##### 31 / T2（置信：high）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(31)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `Treatment(31, molecular_targeted_therapy)` | 事实；来源：title/abstract；置信：high；注：Erlotinib was given to the EGFR-mutant subgroup. |
| 3 | `ExcludedBy(31, T2)` | 规则 `R_T2`：Trials reporting the use of molecular targeted therapy were excluded. |
| 4 | `Conflict(31, T2)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

##### 42 / T2（置信：medium）

| # | 命题 | 依据 |
|---|---|---|
| 1 | `Included(42)` | 事实；来源：Results, PMC10958389；置信：high |
| 2 | `Treatment(42, molecular_targeted_therapy)` | 事实；来源：title；置信：medium；注：Title: 'surgery and erlotinib'; erlotinib is postoperative, so the T2 reading is ambiguous. |
| 3 | `ExcludedBy(42, T2)` | 规则 `R_T2`：Trials reporting the use of molecular targeted therapy were excluded. |
| 4 | `Conflict(42, T2)` | 规则 `R_CONFLICT`：An included study that violates an exclusion criterion is a conflict. |

### 4.2 被臂层面消解的冲突

| 研究 | 标准 | 研究层面为何成立 | 臂层面为何消解 |
|---|---|---|---|
| 22 | T1 | `Treatment(22, chemoradiotherapy)` 触发 R_T1 | 臂级 `Treatment(22_chemo, chemotherapy)` 不匹配 R_T1 |
| 24 | T2 | `Treatment(24, molecular_targeted_therapy)` 触发 R_T2 | 臂级 `Treatment(24_chemo, chemotherapy)` 不匹配 R_T2 |
| 33 | T2 | `Treatment(33, molecular_targeted_therapy)` 触发 R_T2 | 臂级 `Treatment(33_chemo, chemotherapy)` 不匹配 R_T2 |
| 35 | T2 | `Treatment(35, molecular_targeted_therapy)` 触发 R_T2 | 臂级 `Treatment(35_chemo, chemotherapy)` 不匹配 R_T2 |
| 36 | T2 | `Treatment(36, molecular_targeted_therapy)` 触发 R_T2 | 臂级 `Treatment(36_chemo, chemotherapy)` 不匹配 R_T2 |

### 4.3 单位对照表

“两模式均成立”表示研究层面与臂层面都推出冲突；“臂层面消解”表示臂级事实不再触发该标准；“臂层面未派生”表示没有取得该研究的臂级标注，保留研究层面事实，不等于冲突已被解释。

| 研究 | 标准 | 研究层面 | 臂层面 | 置信 | 说明 |
|---|---|---|---|---|---|
| 22 | T1 | 冲突 | 消解（臂级） | high | 臂级事实为化疗臂，不触发该标准 |
| 24 | P4 | 冲突 | 冲突（臂级） | high | 两模式均成立；臂级事实仍触发该标准 |
| 24 | T2 | 冲突 | 消解（臂级） | high | 臂级事实为化疗臂，不触发该标准 |
| 31 | T2 | 冲突 | 保留（无臂级标注） | high | 未取得臂级标注；臂模式保留研究层面事实 |
| 33 | T2 | 冲突 | 消解（臂级） | medium | 臂级事实为化疗臂，不触发该标准 |
| 35 | P4 | 冲突 | 冲突（臂级） | high | 两模式均成立；臂级事实仍触发该标准 |
| 35 | T2 | 冲突 | 消解（臂级） | high | 臂级事实为化疗臂，不触发该标准 |
| 36 | P4 | 冲突 | 冲突（臂级） | high | 两模式均成立；臂级事实仍触发该标准 |
| 36 | T2 | 冲突 | 消解（臂级） | high | 臂级事实为化疗臂，不触发该标准 |
| 42 | T2 | 冲突 | 保留（无臂级标注） | medium | 未取得臂级标注；臂模式保留研究层面事实 |
| 46 | D2 | 冲突 | 冲突（臂级） | high | 两模式均成立；臂级事实仍触发该标准 |

### 4.4 这些冲突在哪个分析组

主文 Results 给出了两个关键名单。8 项 chemoimmunotherapy vs chemotherapy 的 RCT 是 CheckMate 816、KEYNOTE-671、NADIM II、AEGEAN、Neotorch、Checkmate 77T、TD-FOREKNOW、RATIONALE 315；24、31、33、35、36 都不在其中。27 个新辅助化疗臂的编号则包含 24、31、33、35、36。换句话说，这些研究是以**化疗臂**进入单臂／非随机化疗对照组的，不是以 chemoimmunotherapy 研究进入 8 项 RCT 合并的。

这改变了 P4 冲突的解释。P4 的 24、35、36 位于单臂化疗对照组，因此它影响的是单臂化疗比例的合并与间接比较，不是主 RCT 的 OS／EFS／MPR／pCR 合并。主 RCT 合并仍由 8 项 chemoimmunotherapy 试验支撑，P4 冲突不改变其数值。

同时，这也说明作者的实际做法是一条**未写明的臂级例外**：EGFR 突变仅限试验、放化疗试验、靶向治疗试验与观察性研究的化疗臂，被允许作为化疗对照。P4、T1、T2、D2 的文本都是研究层面的，没有写这条例外。更准确的写法应是：“上述研究作为整体被排除，但其化疗臂可作为化疗对照进入单臂分析”；或者把这些臂从单臂化疗组中剔除。

单臂比较在正文中被明确描述为易受偏倚的间接比较（“the inclusion of single-arm studies results in indirect comparisons that are prone to high levels of bias”）。因此，P4 冲突的实务影响主要集中在次要的单臂分析，而不是主 RCT 结论。

## 五、D5 的两种读法

D5 的文本是“无试验级证据的摘要……被排除”，但正文又说 2023 年 ASCO、ESMO、ELCC、WCLC、AACR 的会议摘要被用于更新已发表 RCT 或纳入新 RCT。原型把这句话形式化为两种读法：

- **trial_level（宽松）**：有试验级数据的会议摘要不落入 D5，6 篇摘要不产生冲突。
- **strict（严格）**：所有会议摘要都落入 D5，6 篇摘要全部产生冲突。

trial_level 模式下 D5 冲突数为 0；strict 模式下 D5 冲突数为 6。

| 研究 | D5 trial_level | D5 strict |
|---|---|---|
| 11 | 不冲突 | 冲突 |
| 61 | 不冲突 | 冲突 |
| 62 | 不冲突 | 冲突 |
| 63 | 不冲突 | 冲突 |
| 64 | 不冲突 | 冲突 |
| 65 | 不冲突 | 冲突 |

这不是事实层面的差异，而是文本解释层面的差异。形式化的价值在于把两种读法的后果算出来，而不是替作者选择一种读法。

## 六、这个原型证明了什么

**证明了**：在“P4／D2／T1／T2 按题名、摘要与 eTable 3 的字面含义形式化”这一前提下，标准、事实与纳入清单三者不相容。具体地：

- 研究层面：6 项高置信直接冲突（22、24、31、35、36、46），覆盖 T1、P4、T2、D2 四类排除标准；另有 2 项中置信潜在冲突（33、42）。
- 臂层面：22 的 T1，24／33／35／36 的 T2 被 eTable 3 的化疗臂标注消解；24／35／36 的 P4 与 46 的 D2 保留。
- 分析组：24、31、33、35、36 都在 27 个新辅助化疗臂中，不在 8 项 chemoimmunotherapy RCT 中；P4 冲突影响单臂化疗对照与间接比较，不影响主 RCT 合并。
- 31 与 42 在臂层面保留研究层面事实，因为原型没有取得这两项的臂级标注；这是数据缺口，不是逻辑结论。

**没有证明**：

- 没有证明这篇 meta 分析的结论错误。
- 没有证明作者有不当行为；冲突可以由未说明的例外、标准文本与实际行动不一致、或标准解释不同造成。
- 没有证明事实标注一定正确；每个事实都带来源与置信度，改动事实就会改动证明。
- 没有证明纳入标准（P1—P3、I1—I2、D1、D4）被满足；原型只检查了有题名层面事实的排除标准。

这正是“条件证明”的含义：证明对形式化选择与事实基础成立，不对现实世界无条件成立。

## 七、限制

- **事实基础不完整**：48 项中只有 11 项有研究层面属性事实，6 项有臂级属性事实；其余项的设计、人群、治疗未断言。模型采用封闭世界假设，未断言不等于满足标准，也不等于违反标准。
- **eTable 3 覆盖有限**：只建模了 6 项研究的臂级标注；31、42 等研究的臂级信息未取得，因此臂层面结论对它们是“未派生”，不是“已消解”。
- **只检查排除标准**：纳入标准需要全文与语义判断，原型没有把它们写成规则。
- **D5 是解释选择**：strict 模式的 D5 事实标为 medium，因为它是对文本的严格解读，不是题名直接陈述的事实。
- **没有评审者级数据**：原型不检查双人独立、仲裁、kappa；这些属于流程层，需要决策日志。
- **没有全文核实**：所有事实来自题名、摘要、参考文献表与 eTable 3；全文可能改变设计、人群或治疗的判定。
- **原型不是验证过的工具**：它是一个可复核的桌面模型，不是 screening 系统，也不构成对作者的指控。

## 八、文件

- [formal_model_sorin2024.py](_research/formal_model_sorin2024.py) — 形式模型与推理引擎。
- [validate_formal_model.py](_research/validate_formal_model.py) — 证明结构校验脚本；本轮校验通过。
- [formal_model_results.json](_research/formal_model_results.json) — 四种模式的完整结果与证明树。
- [sorin2024_included_consistency.csv](_research/sorin2024_included_consistency.csv) — 48 项纳入清单。
- [sorin2024_criteria.json](_research/sorin2024_criteria.json) — 17 条结构化标准。
