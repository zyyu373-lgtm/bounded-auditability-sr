#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Minimal formal model for the Sorin 2024 screening-consistency audit.

The model is a tiny forward-chaining engine over ground facts. It derives
ExcludedBy(item, criterion) from asserted study/arm attributes, propagates
arm-level violations to the parent study, and reports Conflict(study, criterion)
when an included study is derived to violate an exclusion criterion.

Two unit modes:
  - study: attributes are asserted at the study/publication level.
  - arm:   attributes are asserted at the extracted-arm level where eTable 3
           provides a reclassification; otherwise the study is its own item.

Two D5 modes:
  - trial_level: conference abstracts with trial-level data are not treated as
                 "abstracts without trial-level evidence" (the review's stated
                 reading).
  - strict:      every conference abstract is treated as excluded by D5.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "sorin2024_included_consistency.csv"
JSON_OUT = BASE / "formal_model_results.json"
MD_OUT = BASE.parent / "胸外科meta分析筛选形式化证明原型-Sorin2024.md"

ARTICLES = {8, 10} | set(range(21, 61))
ABSTRACTS = {11, 61, 62, 63, 64, 65}
FOLLOW_UP = {11, 28, 36, 64, 65}
ALL_ITEMS = sorted(ARTICLES | ABSTRACTS)
ARM_RECLASSIFIED = {22, 24, 33, 35, 36, 46}

CONF_ORDER = {"low": 1, "medium": 2, "high": 3}
CONF_NAME = {1: "low", 2: "medium", 3: "high"}


# ---------------------------------------------------------------------------
# Atoms, rules, derivations
# ---------------------------------------------------------------------------

Atom = tuple  # (predicate, arg1, arg2, ...)


@dataclass(frozen=True)
class Rule:
    id: str
    head_pred: str
    head_args: tuple
    body: tuple  # ((pred, (arg, ...)), ...)
    text: str
    criterion: str | None = None


@dataclass
class Derivation:
    atom: Atom
    rule_id: str | None
    rule_text: str | None
    premises: tuple
    source: str | None
    confidence: str
    note: str = ""


def is_var(x) -> bool:
    return isinstance(x, str) and x.startswith("?")


def unify_args(pattern: tuple, actual: tuple, binding: dict) -> dict | None:
    if len(pattern) != len(actual):
        return None
    b = dict(binding)
    for p, a in zip(pattern, actual):
        if is_var(p):
            if p in b:
                if b[p] != a:
                    return None
            else:
                b[p] = a
        elif p != a:
            return None
    return b


def instantiate(args: tuple, binding: dict) -> tuple:
    return tuple(binding[a] if is_var(a) else a for a in args)


class Engine:
    def __init__(self, rules: Iterable[Rule]):
        self.rules = list(rules)
        self.derivations: dict[Atom, Derivation] = {}

    def assert_fact(self, atom: Atom, source: str, confidence: str, note: str = "") -> None:
        if atom in self.derivations:
            return
        self.derivations[atom] = Derivation(
            atom=atom,
            rule_id=None,
            rule_text=None,
            premises=(),
            source=source,
            confidence=confidence,
            note=note,
        )

    def _match_body(self, body: tuple, binding: dict):
        if not body:
            yield binding
            return
        (pred, args), rest = body[0], body[1:]
        for atom in list(self.derivations):
            if atom[0] != pred or len(atom) - 1 != len(args):
                continue
            b = unify_args(args, atom[1:], binding)
            if b is not None:
                yield from self._match_body(rest, b)

    def run(self) -> None:
        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                for binding in list(self._match_body(rule.body, {})):
                    head = (rule.head_pred,) + instantiate(rule.head_args, binding)
                    if head in self.derivations:
                        continue
                    premises = tuple(
                        (pred,) + instantiate(args, binding)
                        for pred, args in rule.body
                    )
                    self.derivations[head] = Derivation(
                        atom=head,
                        rule_id=rule.id,
                        rule_text=rule.text,
                        premises=premises,
                        source=None,
                        confidence="derived",
                        note="",
                    )
                    changed = True

    def query(self, pred: str, arity: int | None = None) -> list[Atom]:
        return [
            a for a in self.derivations
            if a[0] == pred and (arity is None or len(a) - 1 == arity)
        ]

    def proof_tree(self, atom: Atom, seen: frozenset = frozenset()) -> dict:
        d = self.derivations[atom]
        if d.rule_id is None:
            return {
                "kind": "fact",
                "atom": list(atom),
                "source": d.source,
                "confidence": d.confidence,
                "note": d.note,
            }
        if atom in seen:
            return {
                "kind": "cycle",
                "atom": list(atom),
                "rule": d.rule_id,
                "rule_text": d.rule_text,
                "premises": [],
            }
        return {
            "kind": "derived",
            "atom": list(atom),
            "rule": d.rule_id,
            "rule_text": d.rule_text,
            "premises": [self.proof_tree(p, seen | {atom}) for p in d.premises],
        }


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

RULES = [
    Rule(
        id="R_P4",
        head_pred="ExcludedBy",
        head_args=("?x", "P4"),
        body=(("Population", ("?x", "egfr_mutant_only")),),
        text="Studies that included only patients with NSCLC with EGFR variants were excluded.",
        criterion="P4",
    ),
    Rule(
        id="R_D2",
        head_pred="ExcludedBy",
        head_args=("?x", "D2"),
        body=(("Design", ("?x", "observational")),),
        text="Observational studies were excluded.",
        criterion="D2",
    ),
    Rule(
        id="R_D3",
        head_pred="ExcludedBy",
        head_args=("?x", "D3"),
        body=(("Design", ("?x", "retrospective")),),
        text="Retrospective studies were excluded.",
        criterion="D3",
    ),
    Rule(
        id="R_T1",
        head_pred="ExcludedBy",
        head_args=("?x", "T1"),
        body=(("Treatment", ("?x", "chemoradiotherapy")),),
        text="Trials reporting the use of neoadjuvant radiotherapy, including chemoradiotherapy, were excluded.",
        criterion="T1",
    ),
    Rule(
        id="R_T2",
        head_pred="ExcludedBy",
        head_args=("?x", "T2"),
        body=(("Treatment", ("?x", "molecular_targeted_therapy")),),
        text="Trials reporting the use of molecular targeted therapy were excluded.",
        criterion="T2",
    ),
    Rule(
        id="R_T3",
        head_pred="ExcludedBy",
        head_args=("?x", "T3"),
        body=(("Treatment", ("?x", "immunotherapy_monotherapy")),),
        text="Trials reporting the use of immunotherapy monotherapy were excluded.",
        criterion="T3",
    ),
    Rule(
        id="R_D5",
        head_pred="ExcludedBy",
        head_args=("?x", "D5"),
        body=(("PublicationType", ("?x", "abstract_without_trial_level_evidence")),),
        text="Abstracts without trial-level evidence were excluded.",
        criterion="D5",
    ),
    Rule(
        id="R_D6",
        head_pred="ExcludedBy",
        head_args=("?x", "D6"),
        body=(("PublicationType", ("?x", "editorial_comment_gray")),),
        text="Editorials, comments, and gray literature were excluded.",
        criterion="D6",
    ),
    Rule(
        id="R_ARM",
        head_pred="ExcludedBy",
        head_args=("?s", "?c"),
        body=(
            ("ArmOf", ("?a", "?s")),
            ("ExcludedBy", ("?a", "?c")),
        ),
        text="An arm-level violation propagates to the parent study.",
        criterion=None,
    ),
    Rule(
        id="R_CONFLICT",
        head_pred="Conflict",
        head_args=("?s", "?c"),
        body=(
            ("Included", ("?s",)),
            ("ExcludedBy", ("?s", "?c")),
        ),
        text="An included study that violates an exclusion criterion is a conflict.",
        criterion=None,
    ),
    Rule(
        id="R_NEEDS_FULL_TEXT_D3",
        head_pred="NeedsFullText",
        head_args=("?x", "D3"),
        body=(("Design", ("?x", "unknown")),),
        text="Design unknown at title level; full text is needed to decide D3.",
        criterion="D3",
    ),
]


# ---------------------------------------------------------------------------
# Facts
# ---------------------------------------------------------------------------

# Study-level attributes. Only facts that are visible from the title or the
# reference list are asserted; everything else is left unknown.
STUDY_ATTRS = {
    22: [
        ("Design", ("rct",), "title", "high", "Title: 'a phase 3 randomised trial'."),
        ("Treatment", ("chemoradiotherapy",), "title", "high", "Title: 'Induction chemoradiation'."),
    ],
    24: [
        ("Population", ("egfr_mutant_only",), "abstract (PubMed)", "high",
         "86 patients with stage IIIA EGFR-mutant lung adenocarcinoma; all patients were EGFR-mutant."),
        ("Treatment", ("molecular_targeted_therapy",), "title/abstract", "high",
         "Erlotinib vs pemetrexed + cisplatin; the erlotinib arm is molecular targeted therapy."),
    ],
    31: [
        ("Population", ("mixed",), "abstract (Crossref)", "high",
         "31 patients: 15 EGFR-mutant received erlotinib; 16 EGFR-wild-type received cisplatin-based chemotherapy. The title describes the erlotinib subgroup, not the whole study population."),
        ("Treatment", ("molecular_targeted_therapy",), "title/abstract", "high",
         "Erlotinib was given to the EGFR-mutant subgroup."),
    ],
    33: [
        ("Treatment", ("molecular_targeted_therapy",), "title", "medium",
         "Title: 'antiangiogenic therapy'; eTable 3 extracts the chemotherapy arm, so this is a study-level potential conflict."),
    ],
    35: [
        ("Population", ("egfr_mutant_only",), "title", "high", "Title: 'EGFR-mutant'."),
        ("Treatment", ("molecular_targeted_therapy",), "title", "high", "Title: 'erlotinib versus gemcitabine + cisplatin'."),
    ],
    36: [
        ("Population", ("egfr_mutant_only",), "title", "high", "Title: 'EGFR-mutant'."),
        ("Treatment", ("molecular_targeted_therapy",), "title", "high", "Title: 'erlotinib versus gemcitabine + cisplatin'."),
    ],
    42: [
        ("Treatment", ("molecular_targeted_therapy",), "title", "medium",
         "Title: 'surgery and erlotinib'; erlotinib is postoperative, so the T2 reading is ambiguous."),
    ],
    46: [
        ("Design", ("observational",), "title", "high", "Title: 'open, observational, three-arm clinical study'."),
    ],
    50: [
        ("Design", ("unknown",), "title", "low", "Title does not report design; full text needed."),
    ],
    58: [
        ("Design", ("unknown",), "title", "low", "Title does not report design; full text needed."),
    ],
    59: [
        ("Design", ("unknown",), "title", "low", "Title does not report design; full text needed."),
    ],
}

# Arm-level attributes from eTable 3. The first element is the arm id.
ARM_ATTRS = {
    22: ("22_chemo", [
        ("Treatment", ("chemotherapy",), "eTable 3", "high",
         "Chemotherapy / Single-arm / Cisplatin + docetaxel."),
        ("Design", ("rct",), "eTable 3", "medium",
         "Parent study is a randomised trial; the extracted arm is a chemotherapy arm."),
    ]),
    24: ("24_chemo", [
        ("Treatment", ("chemotherapy",), "eTable 3", "high",
         "Chemotherapy / Single-arm / Pemetrexed + cisplatin."),
        ("Population", ("egfr_mutant_only",), "eTable 3", "high",
         "eTable 3 population: EGFR mutant."),
    ]),
    33: ("33_chemo", [
        ("Treatment", ("chemotherapy",), "eTable 3", "high",
         "Chemotherapy / Single-arm / Cisplatin + vinorelbine."),
    ]),
    35: ("35_chemo", [
        ("Treatment", ("chemotherapy",), "eTable 3", "high",
         "Chemotherapy / Single-arm / Gemcitabine + cisplatin."),
        ("Population", ("egfr_mutant_only",), "eTable 3", "high",
         "eTable 3 population: EGFR mutant."),
    ]),
    36: ("36_chemo", [
        ("Treatment", ("chemotherapy",), "eTable 3", "high",
         "Chemotherapy / Single-arm / Gemcitabine + cisplatin."),
        ("Population", ("egfr_mutant_only",), "eTable 3", "high",
         "eTable 3 population: EGFR mutant."),
    ]),
    46: ("46_chemo", [
        ("Treatment", ("chemotherapy",), "eTable 3", "high",
         "Chemotherapy / Single-arm / Chemotherapy."),
        ("Design", ("observational",), "eTable 3", "high",
         "Parent study is observational; the arm inherits the design."),
    ]),
}


def load_items() -> dict[int, dict]:
    rows = {}
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            rows[int(row["ref"])] = row
    return rows


def build_facts(mode: str, d5_mode: str) -> Engine:
    engine = Engine(RULES)
    rows = load_items()

    for ref in ALL_ITEMS:
        row = rows[ref]
        engine.assert_fact(("Included", str(ref)), "Results, PMC10958389", "high")
        engine.assert_fact(("Year", str(ref), row["year"]), "reference list", "high")
        if ref in ABSTRACTS:
            engine.assert_fact(("PublicationType", str(ref), "abstract"), "reference list", "high")
            if d5_mode == "strict":
                engine.assert_fact(
                    ("PublicationType", str(ref), "abstract_without_trial_level_evidence"),
                    "criterion D5, strict reading",
                    "medium",
                    "Strict reading: every conference abstract is excluded by D5.",
                )
        else:
            engine.assert_fact(("PublicationType", str(ref), "article"), "reference list", "high")

    if mode == "study":
        for ref in ALL_ITEMS:
            engine.assert_fact(("ArmOf", str(ref), str(ref)), "unit mode: study", "high")
            for pred, args, source, confidence, note in STUDY_ATTRS.get(ref, []):
                engine.assert_fact((pred, str(ref)) + args, source, confidence, note)
    elif mode == "arm":
        for ref in ALL_ITEMS:
            if ref in ARM_RECLASSIFIED:
                arm_id, attrs = ARM_ATTRS[ref]
                engine.assert_fact(("ArmOf", arm_id, str(ref)), "eTable 3", "high")
                for pred, args, source, confidence, note in attrs:
                    engine.assert_fact((pred, arm_id) + args, source, confidence, note)
            else:
                engine.assert_fact(
                    ("ArmOf", str(ref), str(ref)),
                    "unit mode: study (no arm reclassification)",
                    "high",
                )
                for pred, args, source, confidence, note in STUDY_ATTRS.get(ref, []):
                    engine.assert_fact((pred, str(ref)) + args, source, confidence, note)
    else:
        raise ValueError(mode)

    engine.run()
    return engine


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

def linear_trace(node: dict) -> list[dict]:
    steps = []

    def walk(n):
        if n["kind"] == "derived":
            for p in n["premises"]:
                walk(p)
            steps.append({
                "kind": "derived",
                "atom": n["atom"],
                "rule": n["rule"],
                "rule_text": n["rule_text"],
            })
        else:
            steps.append({
                "kind": "fact",
                "atom": n["atom"],
                "source": n["source"],
                "confidence": n["confidence"],
                "note": n.get("note", ""),
            })

    walk(node)
    return steps


def min_confidence(node: dict) -> int:
    if node["kind"] == "fact":
        return CONF_ORDER.get(node["confidence"], 0)
    vals = [min_confidence(p) for p in node["premises"]]
    return min(vals) if vals else 3


def summarize(engine: Engine, mode: str, d5_mode: str) -> dict:
    conflicts = []
    for atom in sorted(engine.query("Conflict", 2), key=lambda a: (int(a[1]), a[2])):
        _, study, criterion = atom
        tree = engine.proof_tree(atom)
        conflicts.append({
            "study": study,
            "criterion": criterion,
            "confidence": CONF_NAME[min_confidence(tree)],
            "proof": tree,
            "trace": linear_trace(tree),
        })

    needs_full_text = []
    for atom in sorted(engine.query("NeedsFullText", 2), key=lambda a: (int(a[1]), a[2])):
        _, item, criterion = atom
        tree = engine.proof_tree(atom)
        needs_full_text.append({
            "item": item,
            "criterion": criterion,
            "proof": tree,
            "trace": linear_trace(tree),
        })

    return {
        "mode": mode,
        "d5_mode": d5_mode,
        "asserted_facts": sum(1 for d in engine.derivations.values() if d.rule_id is None),
        "derived_facts": sum(1 for d in engine.derivations.values() if d.rule_id is not None),
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
        "conflict_studies": sorted({c["study"] for c in conflicts}, key=int),
        "needs_full_text": needs_full_text,
    }


def rule_rows() -> list[dict]:
    return [
        {
            "id": r.id,
            "head": f"{r.head_pred}({', '.join(r.head_args)})",
            "body": "; ".join(f"{p}({', '.join(a)})" for p, a in r.body),
            "text": r.text,
            "criterion": r.criterion,
        }
        for r in RULES
    ]


def fact_rows() -> list[dict]:
    rows = []
    for ref, attrs in sorted(STUDY_ATTRS.items()):
        for pred, args, source, confidence, note in attrs:
            rows.append({
                "predicate": pred,
                "args": [str(ref)] + list(args),
                "source": source,
                "confidence": confidence,
                "note": note,
            })
    for ref, (arm_id, attrs) in sorted(ARM_ATTRS.items()):
        for pred, args, source, confidence, note in attrs:
            rows.append({
                "predicate": pred,
                "args": [arm_id] + list(args),
                "source": source,
                "confidence": confidence,
                "note": note,
            })
    return rows


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def atom_str(atom: list | tuple) -> str:
    return f"{atom[0]}({', '.join(atom[1:])})"


def render_trace_table(conflict: dict, level: int = 4) -> str:
    heading = "#" * level
    lines = [
        f"{heading} {conflict['study']} / {conflict['criterion']}（置信：{conflict['confidence']}）",
        "",
        "| # | 命题 | 依据 |",
        "|---|---|---|",
    ]
    for i, step in enumerate(conflict["trace"], 1):
        if step["kind"] == "fact":
            basis = f"事实；来源：{step['source']}；置信：{step['confidence']}"
            if step["note"]:
                basis += f"；注：{step['note']}"
        else:
            basis = f"规则 `{step['rule']}`：{step['rule_text']}"
        lines.append(f"| {i} | `{atom_str(step['atom'])}` | {basis} |")
    lines.append("")
    return "\n".join(lines)


def group_by_study(conflicts: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for c in conflicts:
        groups[c["study"]].append(c)
    return groups


def render_report(results: dict) -> str:
    modes = results["modes"]
    study = modes["study_trial_level"]
    arm = modes["arm_trial_level"]
    study_strict = modes["study_strict"]
    arm_strict = modes["arm_strict"]

    study_map = {(c["study"], c["criterion"]): c for c in study["conflicts"]}
    arm_map = {(c["study"], c["criterion"]): c for c in arm["conflicts"]}
    study_strict_map = {(c["study"], c["criterion"]): c for c in study_strict["conflicts"]}
    arm_strict_map = {(c["study"], c["criterion"]): c for c in arm_strict["conflicts"]}

    study_groups = group_by_study(study["conflicts"])
    arm_groups = group_by_study(arm["conflicts"])

    lines: list[str] = []

    lines.append("# 胸外科 meta 分析筛选的形式化证明原型：Sorin 等（2024）")
    lines.append("")
    lines.append("**性质**：桌面原型。把 17 条筛选标准中的排除类标准写成规则，把纳入清单、题名与补充材料 eTable 3 的标注写成事实，用一个小型前向推理引擎生成冲突的证明轨迹。它不重跑筛选，不重做 meta 分析，也不读取患者级数据。")
    lines.append("")
    lines.append("**对象**：Sorin M, et al. Neoadjuvant Chemoimmunotherapy for NSCLC: A Systematic Review and Meta-Analysis. *JAMA Oncology*. 2024. DOI 10.1001/jamaoncol.2024.0057；PMID 38512301；PMCID PMC10958389。")
    lines.append("")
    lines.append("**输入**：48 项纳入项；17 条结构化标准；eTable 3 中 6 项研究的臂级标注。")
    lines.append("")
    lines.append("**输出**：4 种模式（研究层面／臂层面 × D5 宽松／严格）的冲突清单、逐条证明轨迹与单位对照。")
    lines.append("")

    lines.append("## 一、原型做了什么")
    lines.append("")
    lines.append("原型把“标准—事实—纳入集”三者放进同一个形式系统：")
    lines.append("")
    lines.append("1. **规则**：把 P4、D2、D3、D5、D6、T1、T2、T3 八条排除标准写成蕴含式。")
    lines.append("2. **事实**：把“哪项研究被纳入”“题名说明它用了什么治疗／什么设计／什么人群”“eTable 3 把它标成哪个臂”写成带来源与置信度的 ground facts。")
    lines.append("3. **推理**：前向链推导 `ExcludedBy(item, criterion)`；臂级违例经 `ArmOf` 传播到父研究；若父研究同时 `Included`，则推出 `Conflict`。")
    lines.append("4. **证明轨迹**：每个 `Conflict` 都保留完整推导链，可逐步回放到原始事实。")
    lines.append("")
    lines.append("核心结果：研究层面推出 6 项高置信直接冲突（22、24、31、35、36、46）与 2 项中置信潜在冲突（33、42）；臂层面把 22 的 T1、24／33／35／36 的 T2 消解，但 24／35／36 的 P4 与 46 的 D2 保留；31 与 42 因未取得臂级标注而保留研究层面事实。")
    lines.append("")
    lines.append("| 模式 | 冲突原子 | 涉及研究 | 高置信研究 | 中置信研究 |")
    lines.append("|---|---|---|---|---|")
    for key, label in [
        ("study_trial_level", "研究层面 / trial_level"),
        ("arm_trial_level", "臂层面 / trial_level"),
        ("study_strict", "研究层面 / strict"),
        ("arm_strict", "臂层面 / strict"),
    ]:
        res = modes[key]
        high = {c["study"] for c in res["conflicts"] if c["confidence"] == "high"}
        medium = {c["study"] for c in res["conflicts"] if c["confidence"] == "medium"}
        lines.append(f"| {label} | {res['conflict_count']} | {len(res['conflict_studies'])} | {len(high)} | {len(medium)} |")
    lines.append("")

    lines.append("## 二、形式系统")
    lines.append("")
    lines.append("### 2.1 类型与谓词")
    lines.append("")
    lines.append("| 谓词 | 含义 | 元数 |")
    lines.append("|---|---|---|")
    lines.append("| `Included(s)` | 研究 s 在纳入清单中 | 1 |")
    lines.append("| `ArmOf(a, s)` | 臂／条目 a 属于研究 s | 2 |")
    lines.append("| `Design(x, d)` | 条目 x 的设计为 d | 2 |")
    lines.append("| `Population(x, p)` | 条目 x 的人群为 p | 2 |")
    lines.append("| `Treatment(x, t)` | 条目 x 的治疗为 t | 2 |")
    lines.append("| `PublicationType(x, pt)` | 条目 x 的发表类型为 pt | 2 |")
    lines.append("| `ExcludedBy(x, c)` | 条目 x 违反排除标准 c | 2 |")
    lines.append("| `Conflict(s, c)` | 纳入研究 s 与排除标准 c 冲突 | 2 |")
    lines.append("| `NeedsFullText(x, c)` | 条目 x 在标题层面不足以判定标准 c | 2 |")
    lines.append("")
    lines.append("`Design` 取值：`rct`、`observational`、`retrospective`、`unknown`。`Population` 取值：`egfr_mutant_only`、`mixed`、`unknown`。`Treatment` 取值：`chemotherapy`、`chemoradiotherapy`、`molecular_targeted_therapy`、`immunotherapy_monotherapy`、`unknown`。")
    lines.append("")

    lines.append("### 2.2 规则")
    lines.append("")
    lines.append("| 规则 | 头 | 体 | 标准文本 |")
    lines.append("|---|---|---|---|")
    for r in results["rules"]:
        lines.append(f"| `{r['id']}` | `{r['head']}` | `{r['body']}` | {r['text']} |")
    lines.append("")
    lines.append("`R_ARM` 与 `R_CONFLICT` 是结构规则，不对应具体标准；`R_NEEDS_FULL_TEXT_D3` 只标记“标题层面不可判定”，不产生冲突。")
    lines.append("")

    lines.append("### 2.3 事实与来源")
    lines.append("")
    lines.append("下表只列驱动冲突的属性事实；`Included`、`Year`、`PublicationType` 对 48 项逐条断言，未在表中展开。")
    lines.append("")
    lines.append("| 谓词 | 参数 | 来源 | 置信 | 注 |")
    lines.append("|---|---|---|---|---|")
    for row in results["study_facts"]:
        args = ", ".join(row["args"])
        note = row["note"] or ""
        lines.append(f"| `{row['predicate']}` | `{args}` | {row['source']} | {row['confidence']} | {note} |")
    lines.append("")

    lines.append("## 三、研究层面的证明")
    lines.append("")
    lines.append("以下 6 项是研究层面的高置信直接冲突。每张表都是一条可逐步回放的推导链：从事实出发，经规则，得到 `Conflict`。")
    lines.append("")
    lines.append("### 3.1 六项直接冲突")
    lines.append("")

    study_order = ["46", "24", "31", "35", "36", "22"]
    for study_id in study_order:
        group = study_groups.get(study_id, [])
        if not group:
            continue
        for conflict in group:
            lines.append(render_trace_table(conflict))

    lines.append("### 3.2 P4 的最终核对：撤回 31，确认 24")
    lines.append("")
    lines.append("原型最初按题名把 31 断定为 `Population(31, egfr_mutant_only)`，并推出 P4 冲突。核对摘要后，这一事实被撤回：该研究共 31 例患者，15 例 EGFR 突变者接受厄洛替尼，16 例 EGFR 野生型者接受含铂双药化疗；题名描述的是厄洛替尼亚组，不是整个研究人群。因此 P4（“仅纳入 EGFR 变异患者的研究被排除”）对 31 不成立，`Population` 事实改为 `mixed`，P4 证明撤回。31 的 T2 冲突仍然成立，因为研究报告了厄洛替尼的使用。")
    lines.append("")
    lines.append("随后核对 24 的摘要：86 例ⅢA 期 EGFR 突变型肺腺癌患者随机分为厄洛替尼组与培美曲塞＋顺铂组，全部患者均为 EGFR 突变型；P4 成立。35/36 的摘要也确认人群为 EGFR 外显子 19 或 21 突变、R0 切除的ⅢA-N2 NSCLC；P4 成立，且 35/36 是同一试验的两次发表。因此 P4 的稳健集合为 24、35、36，按试验计为 2 项（24 与 EMERGING-CTONG 1103）。")
    lines.append("")
    lines.append("这是原型条件性的一次具体演示：证明对断言事实成立，但断言事实可能来自题名的误读；核对摘要既可能撤回证明，也可能确认证明。")
    lines.append("")

    lines.append("### 3.3 中置信潜在冲突")
    lines.append("")
    lines.append("33 与 42 的冲突依赖题名的字面解读，置信度为 medium；它们在臂层面是否消解，见第四节。")
    lines.append("")
    for study_id in ["33", "42"]:
        for conflict in study_groups.get(study_id, []):
            lines.append(render_trace_table(conflict))

    lines.append("### 3.4 标题层面不可判定")
    lines.append("")
    lines.append("50、58、59 的题名没有报告研究设计，模型只能推出 `NeedsFullText(·, D3)`，不能推出冲突。这说明“未判定”与“无冲突”是两件事。")
    lines.append("")
    for item in study["needs_full_text"]:
        lines.append(f"- `{atom_str(item['trace'][-1]['atom'])}` — 由 `Design({item['item']}, unknown)` 推出；需全文核实 D3。")
    lines.append("")

    lines.append("## 四、臂层面的证明")
    lines.append("")
    lines.append("臂层面把每个被 eTable 3 重新分类的研究拆成一个臂条目，用 `ArmOf(arm, study)` 连接到父研究。若臂级违例成立，`R_ARM` 把它传播到父研究；若臂级事实不再触发排除规则，父研究的该条冲突就不出现。")
    lines.append("")

    lines.append("### 4.1 保留的冲突")
    lines.append("")
    lines.append("#### 4.1.1 臂级事实仍触发")
    lines.append("")
    lines.append("24、35、36 的 P4 来自臂级人群仍为 EGFR 突变仅限；46 的 D2 来自观察性设计不因按臂提取而改变。")
    lines.append("")
    for study_id in ["46", "24", "35", "36"]:
        for conflict in arm_groups.get(study_id, []):
            lines.append(render_trace_table(conflict, level=5))

    lines.append("#### 4.1.2 无臂级标注、保留研究层面事实")
    lines.append("")
    lines.append("31 与 42 的 eTable 3 臂级标注未取得，臂模式对它们没有臂级条目，因此保留研究层面事实。它们的臂层面状态是“未派生”，不是“臂级仍触发”。")
    lines.append("")
    for study_id in ["31", "42"]:
        for conflict in arm_groups.get(study_id, []):
            lines.append(render_trace_table(conflict, level=5))

    lines.append("### 4.2 被臂层面消解的冲突")
    lines.append("")
    lines.append("| 研究 | 标准 | 研究层面为何成立 | 臂层面为何消解 |")
    lines.append("|---|---|---|---|")
    resolved = []
    for key in sorted(study_map):
        if key not in arm_map:
            resolved.append(key)
    for study_id, criterion in resolved:
        if study_id == "22" and criterion == "T1":
            reason = "臂级 `Treatment(22_chemo, chemotherapy)` 不匹配 R_T1"
        elif study_id == "24" and criterion == "T2":
            reason = "臂级 `Treatment(24_chemo, chemotherapy)` 不匹配 R_T2"
        elif study_id == "33" and criterion == "T2":
            reason = "臂级 `Treatment(33_chemo, chemotherapy)` 不匹配 R_T2"
        elif study_id in {"35", "36"} and criterion == "T2":
            reason = f"臂级 `Treatment({study_id}_chemo, chemotherapy)` 不匹配 R_T2"
        else:
            reason = "臂级事实不触发对应排除规则"
        study_reason = {
            ("22", "T1"): "`Treatment(22, chemoradiotherapy)` 触发 R_T1",
            ("24", "T2"): "`Treatment(24, molecular_targeted_therapy)` 触发 R_T2",
            ("33", "T2"): "`Treatment(33, molecular_targeted_therapy)` 触发 R_T2",
            ("35", "T2"): "`Treatment(35, molecular_targeted_therapy)` 触发 R_T2",
            ("36", "T2"): "`Treatment(36, molecular_targeted_therapy)` 触发 R_T2",
        }.get((study_id, criterion), "研究层面事实触发排除规则")
        lines.append(f"| {study_id} | {criterion} | {study_reason} | {reason} |")
    lines.append("")

    lines.append("### 4.3 单位对照表")
    lines.append("")
    lines.append("“两模式均成立”表示研究层面与臂层面都推出冲突；“臂层面消解”表示臂级事实不再触发该标准；“臂层面未派生”表示没有取得该研究的臂级标注，保留研究层面事实，不等于冲突已被解释。")
    lines.append("")
    lines.append("| 研究 | 标准 | 研究层面 | 臂层面 | 置信 | 说明 |")
    lines.append("|---|---|---|---|---|---|")
    all_keys = sorted(set(study_map) | set(arm_map), key=lambda k: (int(k[0]), k[1]))
    reclassified = {str(x) for x in ARM_RECLASSIFIED}
    for key in all_keys:
        study_id, criterion = key
        in_study = key in study_map
        in_arm = key in arm_map
        if in_study and in_arm:
            status_study = "冲突"
            if study_id in reclassified:
                status_arm = "冲突（臂级）"
                note = "两模式均成立；臂级事实仍触发该标准"
            else:
                status_arm = "保留（无臂级标注）"
                note = "未取得臂级标注；臂模式保留研究层面事实"
        elif in_study and not in_arm:
            status_study = "冲突"
            if study_id in reclassified:
                status_arm = "消解（臂级）"
                note = "臂级事实为化疗臂，不触发该标准"
            else:
                status_arm = "未派生"
                note = "未取得该研究的臂级标注，保留研究层面事实"
        else:
            status_study = "—"
            status_arm = "冲突（臂级）"
            note = "仅臂层面成立"
        conf = (study_map.get(key) or arm_map.get(key))["confidence"]
        lines.append(f"| {study_id} | {criterion} | {status_study} | {status_arm} | {conf} | {note} |")
    lines.append("")

    lines.append("### 4.4 这些冲突在哪个分析组")
    lines.append("")
    lines.append("主文 Results 给出了两个关键名单。8 项 chemoimmunotherapy vs chemotherapy 的 RCT 是 CheckMate 816、KEYNOTE-671、NADIM II、AEGEAN、Neotorch、Checkmate 77T、TD-FOREKNOW、RATIONALE 315；24、31、33、35、36 都不在其中。27 个新辅助化疗臂的编号则包含 24、31、33、35、36。换句话说，这些研究是以**化疗臂**进入单臂／非随机化疗对照组的，不是以 chemoimmunotherapy 研究进入 8 项 RCT 合并的。")
    lines.append("")
    lines.append("这改变了 P4 冲突的解释。P4 的 24、35、36 位于单臂化疗对照组，因此它影响的是单臂化疗比例的合并与间接比较，不是主 RCT 的 OS／EFS／MPR／pCR 合并。主 RCT 合并仍由 8 项 chemoimmunotherapy 试验支撑，P4 冲突不改变其数值。")
    lines.append("")
    lines.append("同时，这也说明作者的实际做法是一条**未写明的臂级例外**：EGFR 突变仅限试验、放化疗试验、靶向治疗试验与观察性研究的化疗臂，被允许作为化疗对照。P4、T1、T2、D2 的文本都是研究层面的，没有写这条例外。更准确的写法应是：“上述研究作为整体被排除，但其化疗臂可作为化疗对照进入单臂分析”；或者把这些臂从单臂化疗组中剔除。")
    lines.append("")
    lines.append("单臂比较在正文中被明确描述为易受偏倚的间接比较（“the inclusion of single-arm studies results in indirect comparisons that are prone to high levels of bias”）。因此，P4 冲突的实务影响主要集中在次要的单臂分析，而不是主 RCT 结论。")
    lines.append("")

    lines.append("## 五、D5 的两种读法")
    lines.append("")
    lines.append("D5 的文本是“无试验级证据的摘要……被排除”，但正文又说 2023 年 ASCO、ESMO、ELCC、WCLC、AACR 的会议摘要被用于更新已发表 RCT 或纳入新 RCT。原型把这句话形式化为两种读法：")
    lines.append("")
    lines.append("- **trial_level（宽松）**：有试验级数据的会议摘要不落入 D5，6 篇摘要不产生冲突。")
    lines.append("- **strict（严格）**：所有会议摘要都落入 D5，6 篇摘要全部产生冲突。")
    lines.append("")
    lines.append(f"trial_level 模式下 D5 冲突数为 0；strict 模式下 D5 冲突数为 {sum(1 for c in study_strict['conflicts'] if c['criterion'] == 'D5')}。")
    lines.append("")
    lines.append("| 研究 | D5 trial_level | D5 strict |")
    lines.append("|---|---|---|")
    for ref in sorted(ABSTRACTS):
        key = (str(ref), "D5")
        lines.append(f"| {ref} | {'冲突' if key in study_map else '不冲突'} | {'冲突' if key in study_strict_map else '不冲突'} |")
    lines.append("")
    lines.append("这不是事实层面的差异，而是文本解释层面的差异。形式化的价值在于把两种读法的后果算出来，而不是替作者选择一种读法。")
    lines.append("")

    lines.append("## 六、这个原型证明了什么")
    lines.append("")
    lines.append("**证明了**：在“P4／D2／T1／T2 按题名、摘要与 eTable 3 的字面含义形式化”这一前提下，标准、事实与纳入清单三者不相容。具体地：")
    lines.append("")
    lines.append("- 研究层面：6 项高置信直接冲突（22、24、31、35、36、46），覆盖 T1、P4、T2、D2 四类排除标准；另有 2 项中置信潜在冲突（33、42）。")
    lines.append("- 臂层面：22 的 T1，24／33／35／36 的 T2 被 eTable 3 的化疗臂标注消解；24／35／36 的 P4 与 46 的 D2 保留。")
    lines.append("- 分析组：24、31、33、35、36 都在 27 个新辅助化疗臂中，不在 8 项 chemoimmunotherapy RCT 中；P4 冲突影响单臂化疗对照与间接比较，不影响主 RCT 合并。")
    lines.append("- 31 与 42 在臂层面保留研究层面事实，因为原型没有取得这两项的臂级标注；这是数据缺口，不是逻辑结论。")
    lines.append("")
    lines.append("**没有证明**：")
    lines.append("")
    lines.append("- 没有证明这篇 meta 分析的结论错误。")
    lines.append("- 没有证明作者有不当行为；冲突可以由未说明的例外、标准文本与实际行动不一致、或标准解释不同造成。")
    lines.append("- 没有证明事实标注一定正确；每个事实都带来源与置信度，改动事实就会改动证明。")
    lines.append("- 没有证明纳入标准（P1—P3、I1—I2、D1、D4）被满足；原型只检查了有题名层面事实的排除标准。")
    lines.append("")
    lines.append("这正是“条件证明”的含义：证明对形式化选择与事实基础成立，不对现实世界无条件成立。")
    lines.append("")

    lines.append("## 七、限制")
    lines.append("")
    lines.append("- **事实基础不完整**：48 项中只有 11 项有研究层面属性事实，6 项有臂级属性事实；其余项的设计、人群、治疗未断言。模型采用封闭世界假设，未断言不等于满足标准，也不等于违反标准。")
    lines.append("- **eTable 3 覆盖有限**：只建模了 6 项研究的臂级标注；31、42 等研究的臂级信息未取得，因此臂层面结论对它们是“未派生”，不是“已消解”。")
    lines.append("- **只检查排除标准**：纳入标准需要全文与语义判断，原型没有把它们写成规则。")
    lines.append("- **D5 是解释选择**：strict 模式的 D5 事实标为 medium，因为它是对文本的严格解读，不是题名直接陈述的事实。")
    lines.append("- **没有评审者级数据**：原型不检查双人独立、仲裁、kappa；这些属于流程层，需要决策日志。")
    lines.append("- **没有全文核实**：所有事实来自题名、摘要、参考文献表与 eTable 3；全文可能改变设计、人群或治疗的判定。")
    lines.append("- **原型不是验证过的工具**：它是一个可复核的桌面模型，不是 screening 系统，也不构成对作者的指控。")
    lines.append("")

    lines.append("## 八、文件")
    lines.append("")
    lines.append("- [formal_model_sorin2024.py](_research/formal_model_sorin2024.py) — 形式模型与推理引擎。")
    lines.append("- [validate_formal_model.py](_research/validate_formal_model.py) — 证明结构校验脚本；本轮校验通过。")
    lines.append("- [formal_model_results.json](_research/formal_model_results.json) — 四种模式的完整结果与证明树。")
    lines.append("- [sorin2024_included_consistency.csv](_research/sorin2024_included_consistency.csv) — 48 项纳入清单。")
    lines.append("- [sorin2024_criteria.json](_research/sorin2024_criteria.json) — 17 条结构化标准。")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    assert len(ALL_ITEMS) == 48, len(ALL_ITEMS)

    results = {
        "model": {
            "review": "Sorin et al., JAMA Oncology 2024",
            "doi": "10.1001/jamaoncol.2024.0057",
            "pmcid": "PMC10958389",
            "items": len(ALL_ITEMS),
            "note": "Conditional proof: criteria formalization + asserted facts + inclusion list.",
        },
        "rules": rule_rows(),
        "study_facts": fact_rows(),
        "modes": {},
    }

    for mode in ["study", "arm"]:
        for d5_mode in ["trial_level", "strict"]:
            engine = build_facts(mode, d5_mode)
            key = f"{mode}_{d5_mode}"
            results["modes"][key] = summarize(engine, mode, d5_mode)

    with JSON_OUT.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    MD_OUT.write_text(render_report(results), encoding="utf-8")

    for key, res in results["modes"].items():
        high = sorted({c["study"] for c in res["conflicts"] if c["confidence"] == "high"}, key=int)
        medium = sorted({c["study"] for c in res["conflicts"] if c["confidence"] == "medium"}, key=int)
        print(f"{key}: {res['conflict_count']} conflict atoms")
        print(f"  high-confidence studies:   {', '.join(high) or '-'}")
        print(f"  medium-confidence studies: {', '.join(medium) or '-'}")
        print(f"  needs full text:           {', '.join(item['item'] for item in res['needs_full_text']) or '-'}")
    print(f"JSON: {JSON_OUT}")
    print(f"MD:   {MD_OUT}")


if __name__ == "__main__":
    main()
