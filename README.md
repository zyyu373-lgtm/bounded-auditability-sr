# Bounded Auditability of Medical Knowledge

**A desk study of whether eligibility criteria in published systematic reviews can be turned into replayable audit traces — and which modeling choices such a trace depends on.**

This repository accompanies a Chinese-language methods manuscript (v0.3) targeting *Research Synthesis Methods* / *Journal of Clinical Epidemiology*. It contains the manuscript, two simulated review reports, the audit reports, the derived data, and the code needed to reproduce the headline numbers.

## What is in this repository

| Path | Contents |
|---|---|
| `manuscript/论文初稿-医学知识有界公理化.md` | Manuscript v0.3 (Chinese) |
| `manuscript/模拟审稿报告-医学知识有界公理化.md` | First-round simulated review (v0.1) |
| `manuscript/模拟审稿报告-v0.2复审.md` | Second-round verification review (v0.2, with v0.3 post-review fixes) |
| `supplement/README.md` | Supplement guide, S-number mapping, data dictionary |
| `supplement/审计报告/` | Three-valued audits, full-record audit summary, cross-case review, boundary taxonomy, fact-grounding protocol, revision experiment, formal-model prototype |
| `supplement/数据/` | JSON audit matrices, cross-case results, fact-grounding and revision results, P4 abstracts |
| `supplement/代码/` | Formal model, audit builders, cross-case analysis, revision experiment, validation |
| `supplement/版本/` | v0.1 backup for comparison |
| `_research/` | Minimal input files used by `check_screening_protocol.py` |

## Headline numbers

- **Case**: Sorin et al. 2024, *JAMA Oncology* — 42 publications + 6 conference abstracts = **48 records**, **43 trials**, **54 arms**, 5,431 patients.
- **Record-level audit**: **11 conflict atoms** (7 E1 abstract-level, 4 E0 title-level); **1 retracted** (S31/P4 after the abstract showed a mixed EGFR population).
- **Record-insufficiency rate**: **71.4%** (95% CI 66.6–75.6) at record level; **68.0%** (63.1–72.4) at arm level.
- **After joint revision** (P4 arm-level exception + arm-level unit): **3 residual records** — S31/T2 (E1), S42/T2 (E0), S46/D2 (E0, provisional).
- **Cross-case review**: 11 purposively sampled 2026 meta-analyses, **114 criteria**; **91.2%** formalizable, **61.4%** title/abstract-visible.
- **Full-record audits**: 5 cases, 6 grids, **1,078 codes** (694 unique cells, 79 independent units); homogeneous RCT/dose-response/IPD/umbrella cases show **8.3%–16.7%** record insufficiency, versus **68.0%–71.4%** for the mixed-design case.

## What is new

The contribution is **not** any single technique. Rule-based eligibility criteria, forward chaining, provenance-tagged facts, and three-valued judgments all overlap with existing work in ontology, guideline formalization, and screening automation. The contribution is the **combination**, under four explicit conditions:

1. **Post hoc** — the audit targets published criteria and a published included set; it does not re-screen or re-run the meta-analysis.
2. **Machine-replayable** — every conflict derivation can be replayed to its source facts.
3. **Provenance** — every fact carries a source and an evidence level (E0 title, E1 abstract, E2 full text, E3 author/protocol).
4. **Analysis-group localization** — conflicts are mapped to the specific statistical analysis group (main RCT synthesis, single-arm chemotherapy comparison, etc.), not merely reported as "a conflict exists".

The manuscript is explicit that this is a **conditional audit**, not a proof of medical conclusions; the B-layer (process/protocol) is untested, and the C-layer (empirical/causal) is argued, not proved.

## Reproduce

Requires Python 3.10+; the scripts use the standard library only.

```bash
cd supplement/代码
python formal_model_sorin2024.py      # 11 / 6 / 17 / 12 conflict atoms
python revision_experiment.py         # retraction/addition/retention counts
python fact_grounding_audit.py        # 7 E1 / 4 E0 / 1 retracted
python boundary_taxonomy.py           # 2x2 boundary classification
python build_audit_reports.py         # Fu / Lixa / Chen full-record audits
python cross_case_analysis.py         # 114 criteria, 91.2% / 61.4%
```

`check_screening_protocol.py` expects the repository root as the working directory:

```bash
python supplement/代码/check_screening_protocol.py
```

Expected outputs include:

- `11` record-level loose, `6` arm-level loose, `17` record-level strict, `12` arm-level strict;
- record-insufficiency `71.4%` / `68.0%`;
- cross-case `91.2%` formalizable, `61.4%` visible, `1,078` codes / `694` unique cells / `79` independent units;
- full-record audits: Ren `15.0%`, Fu `8.3%`, Lixa `16.7%`, Chen `11.1%`.

The model's console output still uses the internal `high/medium/low` confidence labels. These are implementation markers, not the E0–E3 evidence levels used in the manuscript; see §3.2 of the manuscript.

## Status and caveats

- This is a **research prototype**, not a validated reporting guideline. The three candidate reporting items are a **candidate extension**, not a consensus standard.
- The cross-case sample is **purposive maximal variation**, not a systematic search; there is no search log, codebook, second coder, or kappa yet.
- The three-valued audit does **not** code NA separately; record-insufficiency rates are conservative upper bounds.
- The S46/D2 classification (observational vs. prospective non-randomized) is **provisional** and awaits author clarification.
- The single-arm chemotherapy sensitivity analysis (excluding S24/S35/S36) is **not yet done**.
- No OSF/Zenodo DOI yet; this GitHub repository is the working archive. A DOI will be added before submission.
- The manuscript is in Chinese; an English submission version is planned.
- The two review reports are **AI-simulated** (five role-separated seats, same model family), not formal peer review and not independent verification.

## License

- Text, data, and figures: **CC BY 4.0** — see `LICENSE-CC-BY-4.0.txt`.
- Code: **MIT** — see `LICENSE-MIT.txt`.

## Citation

If you use this material, please cite the manuscript repository:

> zyyu373-lgtm. *Bounded Auditability of Medical Knowledge: Replayable Derivations and Four Modeling Choices in Systematic Review Screening*. GitHub, 2026. https://github.com/zyyu373-lgtm/bounded-auditability-sr

---

## 中文摘要

本仓库是方法学论文《医学知识的有界可审计化：系统综述筛选的可回放推导与四个建模选择》的配套材料（v0.3）。核心主张是：已发表系统综述的资格标准可以被写成规则，并生成可回放到原始事实的冲突推导；但这是**条件性审计**，不是医学结论的证明。论文的增量不在单一技术，而在四个限定条件的组合：**事后审计、可机器重放、证据溯源、分析组定位**。

仓库包含稿件、两轮模拟审稿报告、审计报告、派生数据与可运行脚本。复现入口与预期数字见上文英文部分；补充材料说明见 `supplement/README.md`。

当前限制：目的性样本、单一编码者、未编码 NA、S46/D2 暂定、单臂化疗敏感性分析未做、尚无公开 DOI。上述限制在稿件 §5.5 与复审报告中均有记录。
