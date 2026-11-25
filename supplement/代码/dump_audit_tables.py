#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dump all tables of the three audit cases as readable row-per-line text."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

CASES = ["tyg_pad", "floating_hip_ipd", "bfr_umbrella"]


def ln(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def tx(elem) -> str:
    return re.sub(r"\s+", " ", "".join(elem.itertext())).strip()


def main() -> None:
    for name in CASES:
        root = ET.parse(f"_research/cases/{name}.xml").getroot()
        out_path = f"_research/cases/{name}_tables.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            for tw in root.iter():
                if ln(tw.tag) != "table-wrap":
                    continue
                label = ""
                caption = ""
                for child in tw:
                    if ln(child.tag) == "label":
                        label = tx(child)
                    if ln(child.tag) == "caption":
                        caption = tx(child)
                f.write(f"\n===== {label}: {caption} =====\n")
                for tr in tw.iter():
                    if ln(tr.tag) != "tr":
                        continue
                    cells = [tx(td) for td in tr if ln(td.tag) in ("td", "th")]
                    if cells:
                        f.write(" || ".join(cells) + "\n")
        print(f"OK {name} -> {out_path}")


if __name__ == "__main__":
    main()
