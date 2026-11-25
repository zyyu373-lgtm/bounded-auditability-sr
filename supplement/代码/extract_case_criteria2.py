#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract eligibility criteria sections from the second batch of case XMLs."""

from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET

CASES = ["amh_pcos", "statin_crc", "hearing_loss", "bfr_umbrella",
         "floating_hip_ipd", "tyg_pad"]

KEYWORDS = ("eligib", "inclusion", "exclusion", "criteria", "study selection",
            "selection criteria", "patient selection", "methods")


def ln(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def tx(elem) -> str:
    return re.sub(r"\s+", " ", "".join(elem.itertext())).strip()


def find_sections(root) -> list[dict]:
    hits = []
    for sec in root.iter():
        if ln(sec.tag) != "sec":
            continue
        title = ""
        for child in sec:
            if ln(child.tag) == "title":
                title = tx(child)
                break
        low = title.lower()
        if any(k in low for k in KEYWORDS):
            hits.append({"title": title, "text": tx(sec)})
    return hits


def article_meta(root) -> dict:
    meta = {}
    for elem in root.iter():
        if ln(elem.tag) == "article-title":
            meta["title"] = tx(elem)
            break
    for elem in root.iter():
        if ln(elem.tag) == "journal-title":
            meta["journal"] = tx(elem)
            break
    for elem in root.iter():
        if ln(elem.tag) == "abstract":
            meta["abstract"] = tx(elem)
            break
    years = [tx(e) for e in root.iter() if ln(e.tag) == "year"]
    meta["year"] = years[0] if years else ""
    return meta


def main() -> None:
    for name in CASES:
        path = f"_research/cases/{name}.xml"
        if not os.path.exists(path):
            print(f"MISSING {path}")
            continue
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            print(f"PARSE FAIL {name}: {exc}")
            continue
        meta = article_meta(root)
        sections = find_sections(root)
        out_path = f"_research/cases/{name}_criteria.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"TITLE: {meta.get('title','')}\n")
            f.write(f"JOURNAL: {meta.get('journal','')}  YEAR: {meta.get('year','')}\n\n")
            f.write("ABSTRACT:\n" + meta.get("abstract", "")[:5000] + "\n\n")
            f.write(f"SECTIONS MATCHED: {len(sections)}\n")
            for i, sec in enumerate(sections):
                f.write(f"\n=== [{i}] {sec['title']} ===\n")
                f.write(sec["text"][:8000] + "\n")
        print(f"OK {name}: {len(sections)} sections -> {out_path}")
        for sec in sections:
            print(f"   - {sec['title']} ({len(sec['text'])} chars)")


if __name__ == "__main__":
    main()
