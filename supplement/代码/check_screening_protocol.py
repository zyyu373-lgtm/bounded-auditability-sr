import json
from collections import Counter, defaultdict

PATH = "_research/sorin2024_criteria.json"
OUT = "_research/sorin2024_check_results.json"

with open(PATH, encoding="utf-8") as f:
    data = json.load(f)

criteria = data["criteria"]
review = data["review"]
flow = data["flow"]
wf = data["workflow"]
pico = data["pico_coverage"]

print("=== REVIEW ===")
print(f"{review['title']} | {review['journal']} {review['year']} | DOI {review['doi']} | PMID {review['pmid']} | {review['prospero']}")
print()

print("=== CRITERIA TABLE ===")
print("ID | Dimension | Type | Value | Stage | Formalizability")
for c in criteria:
    print(f"{c['id']} | {c['dimension']} | {c['type']} | {c['value']} | {c['stage']} | {c['formalizability']}")
print()

# 1. Duplicate IDs
ids = [c["id"] for c in criteria]
dup_ids = sorted([k for k, v in Counter(ids).items() if v > 1])
print("=== CHECK 1: DUPLICATE IDS ===")
print("PASS" if not dup_ids else f"FAIL: {dup_ids}")
print()

# 2. Contradictory (dimension, value) pairs
pairs = defaultdict(set)
for c in criteria:
    pairs[(c["dimension"], c["value"])].add(c["type"])
conflicts = [f"{d}:{v} -> {sorted(t)}" for (d, v), t in pairs.items() if len(t) > 1]
print("=== CHECK 2: EXACT CONTRADICTIONS ===")
print("PASS" if not conflicts else "FAIL: " + "; ".join(conflicts))
print()

# 3. Missing stage
missing_stage = [c["id"] for c in criteria if not c.get("stage")]
print("=== CHECK 3: STAGE ASSIGNMENT ===")
print("PASS" if not missing_stage else f"FAIL: {missing_stage}")
print()

# 4. PICO coverage
print("=== CHECK 4: PICO / ELIGIBILITY DIMENSION COVERAGE ===")
for k, v in pico.items():
    print(f"{k}: {'covered' if v else 'NOT explicitly covered'}")
print()

# 5. Formalizability load
counts = Counter(c["formalizability"] for c in criteria)
print("=== CHECK 5: FORMALIZABILITY LOAD ===")
for k in ["rule", "structured", "semantic"]:
    print(f"{k}: {counts.get(k, 0)} / {len(criteria)}")
print()

# 6. Semantic ambiguity list
print("=== CHECK 6: SEMANTIC / AMBIGUITY FINDINGS ===")
for c in criteria:
    if c["formalizability"] == "semantic":
        print(f"{c['id']} [{c['value']}]: {c['note']}")
print()

# 7. Workflow properties
print("=== CHECK 7: WORKFLOW PROPERTIES ===")
checks = {
    "dual_independent_title_abstract": wf["title_abstract_reviewers_per_record"] >= 2 and wf["independence"],
    "dual_independent_full_text": wf["full_text_reviewers_per_record"] >= 2 and wf["independence"],
    "adjudication_available": wf["adjudicator"] >= 1,
    "inclusion_requires_full_text": wf["inclusion_requires_full_text"],
    "exclusion_reason_required": wf["exclusion_reason_required"],
    "inter_rater_reliability_reported": wf["inter_rater_reliability_reported"],
}
for k, v in checks.items():
    print(f"{k}: {'PASS' if v else 'FAIL / NOT REPORTED'}")
print()

# 8. PRISMA count closure
print("=== CHECK 8: PRISMA COUNT CLOSURE ===")
duplicates = flow["identified_total"] - flow["unique"]
full_text_assessed = flow["unique"] - flow["title_abstract_excluded"]
publications_after_full_text = full_text_assessed - flow["full_text_excluded"]
items = flow["publications_included"] + flow["abstracts_included"]
trial_items = flow["trials"] + flow["follow_up_studies"]
print(f"identified_total = {flow['identified_total']}")
print(f"unique = {flow['unique']} (duplicates = {duplicates})")
print(f"title_abstract_excluded = {flow['title_abstract_excluded']}")
print(f"full_text_assessed = {full_text_assessed}")
print(f"full_text_excluded = {flow['full_text_excluded']}")
print(f"publications_after_full_text = {publications_after_full_text}")
print(f"publications_included = {flow['publications_included']} -> {'PASS' if publications_after_full_text == flow['publications_included'] else 'FAIL'}")
print(f"items = publications + abstracts = {items}")
print(f"trial_items = trials + follow_up = {trial_items} -> {'PASS' if items == trial_items else 'FAIL'}")
print()

# Save summary
summary = {
    "review": review,
    "checks": {
        "duplicate_ids": not dup_ids,
        "exact_contradictions": not conflicts,
        "stage_assignment": not missing_stage,
        "pico_outcome_covered": pico["outcome"],
        "workflow": checks,
        "publication_count_closure": publications_after_full_text == flow["publications_included"],
        "item_count_closure": items == trial_items,
    },
    "counts": {
        "criteria_total": len(criteria),
        "formalizability": dict(counts),
        "duplicates": duplicates,
        "full_text_assessed": full_text_assessed,
        "publications_after_full_text": publications_after_full_text,
        "items": items,
        "trial_items": trial_items,
    },
    "semantic_findings": [
        {"id": c["id"], "value": c["value"], "note": c["note"]}
        for c in criteria if c["formalizability"] == "semantic"
    ],
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"Summary written to {OUT}")
