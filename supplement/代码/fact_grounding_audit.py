#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fact-grounding audit: assign an evidence level to each conflict-driving fact.

Evidence levels:
  E0 title
  E1 abstract
  E2 full text
  E3 author / protocol

A conflict whose lowest premise is E0 is PROVISIONAL; E1 or above is VERIFIED.
A fact contradicted by a higher level is RETRACTED and its proof withdrawn.
"""

from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
JSON_OUT = BASE / "fact_grounding_results.json"
MD_OUT = BASE.parent / "事实接地协议-证据层级.md"

LEVEL_NAME = {"E0": "题名", "E1": "摘要", "E2": "全文", "E3": "作者/协议"}
LEVEL_ORDER = {"E0": 0, "E1": 1, "E2": 2, "E3": 3}

FACTS = [
    {"ref": "22", "criterion": "T1", "predicate": "Treatment", "value": "chemoradiotherapy",
     "level": "E0", "source": "题名", "status": "TITLE_ONLY",
     "note": "题名明确为 chemoradiation；未核对摘要。"},
    {"ref": "24", "criterion": "P4", "predicate": "Population", "value": "egfr_mutant_only",
     "level": "E1", "source": "PubMed 摘要 PMID 29502374", "status": "VERIFIED",
     "note": "86 例ⅢA 期 EGFR 突变型肺腺癌，全部为 EGFR 突变。"},
    {"ref": "24", "criterion": "T2", "predicate": "Treatment", "value": "molecular_targeted_therapy",
     "level": "E1", "source": "PubMed 摘要 PMID 29502374", "status": "VERIFIED",
     "note": "厄洛替尼 vs 培美曲塞＋顺铂。"},
    {"ref": "31", "criterion": "P4", "predicate": "Population", "value": "egfr_mutant_only",
     "level": "E0", "source": "题名（修正前）", "status": "RETRACTED",
     "note": "摘要显示 15 例 EGFR 突变 + 16 例野生型；P4 撤回。"},
    {"ref": "31", "criterion": "T2", "predicate": "Treatment", "value": "molecular_targeted_therapy",
     "level": "E1", "source": "Crossref 摘要 DOI 10.1177/0300060519887275", "status": "VERIFIED",
     "note": "厄洛替尼用于 EGFR 突变亚组；T2 成立。"},
    {"ref": "33", "criterion": "T2", "predicate": "Treatment", "value": "molecular_targeted_therapy",
     "level": "E0", "source": "题名", "status": "TITLE_ONLY",
     "note": "题名为抗血管生成治疗；eTable 3 提取化疗臂。"},
    {"ref": "35", "criterion": "P4", "predicate": "Population", "value": "egfr_mutant_only",
     "level": "E1", "source": "JCO 摘要 DOI 10.1200/JCO.19.00075", "status": "VERIFIED",
     "note": "ⅢA-N2 NSCLC，EGFR 外显子 19 或 21 突变。"},
    {"ref": "35", "criterion": "T2", "predicate": "Treatment", "value": "molecular_targeted_therapy",
     "level": "E1", "source": "JCO 摘要", "status": "VERIFIED",
     "note": "厄洛替尼 vs 吉西他滨＋顺铂。"},
    {"ref": "36", "criterion": "P4", "predicate": "Population", "value": "egfr_mutant_only",
     "level": "E1", "source": "STTT 摘要 DOI 10.1038/s41392-022-01286-3", "status": "VERIFIED",
     "note": "EGFR 敏感突变，R0 切除ⅢA-N2 NSCLC。"},
    {"ref": "36", "criterion": "T2", "predicate": "Treatment", "value": "molecular_targeted_therapy",
     "level": "E1", "source": "STTT 摘要", "status": "VERIFIED",
     "note": "厄洛替尼 vs GC。"},
    {"ref": "42", "criterion": "T2", "predicate": "Treatment", "value": "molecular_targeted_therapy",
     "level": "E0", "source": "题名", "status": "TITLE_ONLY",
     "note": "术后厄洛替尼；T2 解释待定。"},
    {"ref": "46", "criterion": "D2", "predicate": "Design", "value": "observational",
     "level": "E0", "source": "题名", "status": "TITLE_ONLY",
     "note": "题名明确为 observational；未核对摘要/全文。"},
]


def main() -> None:
    for fact in FACTS:
        fact["level_name"] = LEVEL_NAME[fact["level"]]
        fact["level_order"] = LEVEL_ORDER[fact["level"]]

    current = [f for f in FACTS if f["status"] != "RETRACTED"]
    verified = [f for f in current if f["status"] == "VERIFIED"]
    title_only = [f for f in current if f["status"] == "TITLE_ONLY"]
    retracted = [f for f in FACTS if f["status"] == "RETRACTED"]

    results = {
        "protocol": {
            "levels": LEVEL_NAME,
            "rule": "冲突证据等级 = 最低前提等级；E0 为 PROVISIONAL，E1 及以上为 VERIFIED；被更高等级事实否定者为 RETRACTED。",
        },
        "facts": FACTS,
        "summary": {
            "current_conflicts": len(current),
            "verified": len(verified),
            "title_only": len(title_only),
            "retracted": len(retracted),
            "verified_items": sorted({f["ref"] for f in verified}, key=int),
            "title_only_items": sorted({f["ref"] for f in title_only}, key=int),
        },
    }
    JSON_OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# 事实接地协议：证据层级与冲突的证明强度")
    lines.append("")
    lines.append("**性质**：把 P4 的修正流程一般化为一条证据层级协议，并对 11 条当前冲突逐条标注最低证据等级。它不是新的判决，而是给已有冲突加上“证明强度”标签。")
    lines.append("")
    lines.append("## 一、协议")
    lines.append("")
    lines.append("| 等级 | 证据 | 用途 |")
    lines.append("|---|---|---|")
    lines.append("| E0 | 题名 | 只能作为线索；不足以单独支持排除冲突 |")
    lines.append("| E1 | 摘要 | 人群、设计、治疗的显式陈述可作为冲突的最低证据 |")
    lines.append("| E2 | 全文 | 纳入条件、提取表、分析组的最终依据 |")
    lines.append("| E3 | 作者/协议 | 对未写明的例外、单位、分析组映射的澄清 |")
    lines.append("")
    lines.append("两条规则。第一，冲突的证据等级等于其最低前提的等级；E0 冲突标为 `PROVISIONAL`，E1 及以上标为 `VERIFIED`。第二，若更高等级证据否定低等级事实，低等级事实标为 `RETRACTED`，其证明撤回。31 的 P4 就是第二条规则的实例。")
    lines.append("")
    lines.append("## 二、逐条冲突的证据等级")
    lines.append("")
    lines.append("| Ref | 标准 | 事实 | 等级 | 来源 | 状态 |")
    lines.append("|---|---|---|---|---|---|")
    for fact in FACTS:
        lines.append(f"| {fact['ref']} | {fact['criterion']} | `{fact['predicate']}({fact['value']})` | {fact['level']}（{fact['level_name']}） | {fact['source']} | {fact['status']} |")
    lines.append("")
    lines.append("## 三、汇总")
    lines.append("")
    lines.append(f"当前冲突 {len(current)} 条：`VERIFIED` {len(verified)} 条，`TITLE_ONLY` {len(title_only)} 条；另有 `RETRACTED` {len(retracted)} 条（31/P4）。")
    lines.append("")
    lines.append(f"- `VERIFIED` 涉及研究：{', '.join(sorted({f['ref'] for f in verified}, key=int))}。")
    lines.append(f"- `TITLE_ONLY` 涉及研究：{', '.join(sorted({f['ref'] for f in title_only}, key=int))}。")
    lines.append("")
    lines.append("## 四、主要发现")
    lines.append("")
    lines.append("第一，11 条当前冲突中只有 7 条达到摘要级证据；4 条仍是标题级。也就是说，约三分之一的冲突尚未达到“可对外正式报告”的证据门槛。")
    lines.append("")
    lines.append("第二，P4 的 3 条冲突全部达到摘要级：24、35、36 的人群均由摘要确认。P4 是本文最稳健的冲突组。")
    lines.append("")
    lines.append("第三，46 的 D2 仍是标题级。题名中的 “observational” 很强，但按协议，它还需要摘要或全文确认；这使得“最稳健的 D2 冲突”在证据层级上反而不如 P4。")
    lines.append("")
    lines.append("第四，31 的 P4 是唯一被撤回的冲突。它的题名足以触发 P4，但摘要否定了“仅 EGFR 突变”的前提；这正是“证明对事实成立、事实可能错”的实例。")
    lines.append("")
    lines.append("## 五、对论文的含义")
    lines.append("")
    lines.append("论文应把冲突分成三档：`VERIFIED`（摘要级及以上）、`PROVISIONAL`（标题级）、`RETRACTED`（被更高证据否定）。这比“11 条冲突”更精确，也比“6 项高置信”更可复核。")
    lines.append("")
    lines.append("形式化的价值在这里再次显现：证明轨迹让每条冲突的最低前提可见；没有轨迹，读者只能看到一个总数，无法知道哪一条依赖题名、哪一条依赖摘要。")
    lines.append("")
    lines.append("## 六、限制")
    lines.append("")
    lines.append("- 本协议只标注证据等级，不评估研究质量或偏倚风险；E2 全文也可能有错误。")
    lines.append("- 4 条 `TITLE_ONLY` 冲突可以通过摘要或全文升级为 `VERIFIED`，也可能被否定为 `RETRACTED`；本轮未逐一核对。")
    lines.append("- 证据等级是离散标签，不是概率；它不表达“有多大把握”，只表达“依据在哪一层”。")
    lines.append("")
    lines.append("## 七、文件")
    lines.append("")
    lines.append("- [fact_grounding_audit.py](_research/fact_grounding_audit.py) — 协议与审计脚本。")
    lines.append("- [fact_grounding_results.json](_research/fact_grounding_results.json) — 逐条事实与汇总。")
    lines.append("- [研究目标与推进路线.md](研究目标与推进路线.md) — 总目标与停止标准。")
    lines.append("")
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"current={len(current)} verified={len(verified)} title_only={len(title_only)} retracted={len(retracted)}")
    print(f"verified items: {sorted({f['ref'] for f in verified}, key=int)}")
    print(f"title-only items: {sorted({f['ref'] for f in title_only}, key=int)}")
    print(f"JSON: {JSON_OUT}")
    print(f"MD:   {MD_OUT}")


if __name__ == "__main__":
    main()
