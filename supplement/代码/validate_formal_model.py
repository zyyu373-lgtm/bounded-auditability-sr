#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the formal-model output against the expected proof structure."""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "formal_model_results.json"

with RESULTS.open(encoding="utf-8") as f:
    data = json.load(f)

failures = []


def check(condition, message):
    if not condition:
        failures.append(message)


for mode_key, mode in data["modes"].items():
    conflicts = mode["conflicts"]
    check(mode["conflict_count"] == len(conflicts), f"{mode_key}: conflict_count mismatch")
    check(
        mode["conflict_studies"] == sorted({c["study"] for c in conflicts}, key=int),
        f"{mode_key}: conflict_studies mismatch",
    )

    for conflict in conflicts:
        study = conflict["study"]
        criterion = conflict["criterion"]
        trace = conflict["trace"]
        check(bool(trace), f"{mode_key}/{study}/{criterion}: empty trace")
        if not trace:
            continue
        check(
            trace[-1]["atom"] == ["Conflict", study, criterion],
            f"{mode_key}/{study}/{criterion}: trace does not end with Conflict",
        )
        check(
            any(
                step["kind"] == "fact" and step["atom"] == ["Included", study]
                for step in trace
            ),
            f"{mode_key}/{study}/{criterion}: no Included({study}) fact",
        )
        check(
            any(step.get("rule") == "R_CONFLICT" for step in trace),
            f"{mode_key}/{study}/{criterion}: no R_CONFLICT step",
        )

    if mode["mode"] == "arm":
        for conflict in conflicts:
            study = conflict["study"]
            criterion = conflict["criterion"]
            trace = conflict["trace"]
            uses_arm = any(step.get("rule") == "R_ARM" for step in trace)
            has_armof = any(
                step["kind"] == "fact" and step["atom"][0] == "ArmOf"
                for step in trace
            )
            if study in {"24", "35", "36", "46"} and criterion in {"P4", "D2"}:
                check(uses_arm, f"{mode_key}/{study}/{criterion}: expected R_ARM propagation")
                check(has_armof, f"{mode_key}/{study}/{criterion}: expected ArmOf fact")
            if study in {"31", "42"}:
                check(not uses_arm, f"{mode_key}/{study}/{criterion}: unexpected R_ARM propagation")

    d5 = [c for c in conflicts if c["criterion"] == "D5"]
    if mode["d5_mode"] == "trial_level":
        check(not d5, f"{mode_key}: unexpected D5 conflicts")
    else:
        check(len(d5) == 6, f"{mode_key}: expected 6 D5 conflicts, got {len(d5)}")

    check(
        [item["item"] for item in mode["needs_full_text"]] == ["50", "58", "59"],
        f"{mode_key}: unexpected NeedsFullText items",
    )

expected = {
    "study_trial_level": (11, 8, 6, 2),
    "arm_trial_level": (6, 6, 5, 1),
    "study_strict": (17, 14, 6, 8),
    "arm_strict": (12, 12, 5, 7),
}
for key, (atoms, studies, high, medium) in expected.items():
    mode = data["modes"][key]
    high_set = {c["study"] for c in mode["conflicts"] if c["confidence"] == "high"}
    medium_set = {c["study"] for c in mode["conflicts"] if c["confidence"] == "medium"}
    actual = (mode["conflict_count"], len(mode["conflict_studies"]), len(high_set), len(medium_set))
    check(actual == (atoms, studies, high, medium), f"{key}: expected {expected[key]}, got {actual}")

if failures:
    print("VALIDATION FAILED")
    for failure in failures:
        print(f"- {failure}")
    sys.exit(1)

print("VALIDATION PASSED")
for key in expected:
    mode = data["modes"][key]
    print(
        f"{key}: atoms={mode['conflict_count']}, "
        f"studies={len(mode['conflict_studies'])}, "
        f"needs_full_text={[i['item'] for i in mode['needs_full_text']]}"
    )
