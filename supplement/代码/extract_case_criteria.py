#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract eligibility criteria and study counts from case full-text XML."""

from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET

CASES = ["robotic_vats", "cabg_nma", "lidocaine_vats", "pediatric_empyema"]

KEYWORDS = ("eligib", "inclusion", "exclusion", "criteria", "study selection",
            "selection criteria", "patient selection")


def localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def text_of(elem) -> str:
    return re.sub(r"\s+", " ", "".join(elem.itertext())).strip()


def walk(elem, out: list) -> None:
    out.append(elem)


def find_sections(root) -> list[dict]:
    hits = []
    for sec in root.iter():
        if localname(sec.tag) != "sec":
            continue
        title = ""
        for child in sec:
            if localname(child.tag) == "title":
                title = text_of(child)
                break
        low = title.lower()
        if any(k in low for k in KEYWORDS):
            body = text_of(sec)
            hits.append({"title": title, "text": body})
    return hits


def article_meta(root) -> dict:
    meta = {}
    for elem in root.iter():
        if localname(elem.tag) == "article-title":
            meta["title"] = text_of(elem)
            break
    for elem in root.iter():
        if localname(elem.tag) == "journal-title":
            meta["journal"] = text_of(elem)
            break
    for elem in root.iter():
        if localname(elem.tag) == "abstract":
            meta["abstract"] = text_of(elem)
            break
    years = [text_of(e) for e in root.iter() if localname(e.tag) == "year"]
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
            f.write("ABSTRACT:\n" + meta.get("abstract", "")[:4000] + "\n\n")
            f.write(f"SECTIONS MATCHED: {len(sections)}\n")
            for i, sec in enumerate(sections):
                f.write(f"\n=== [{i}] {sec['title']} ===\n")
                f.write(sec["text"][:7000] + "\n")
        print(f"OK {name}: {len(sections)} sections -> {out_path}")
        for sec in sections:
            print(f"   - {sec['title']} ({len(sec['text'])} chars)")


if __name__ == "__main__":
    main()
