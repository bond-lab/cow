#!/usr/bin/env python3
"""Extract the Chinese agentive noun links of Bond and Lim (2019).

Ryan Lim Dao Wei generated candidate pairs of a verb sense and a noun sense
whose lemma is the verb plus an agentive suffix (者, 人, 手, 员, 器, ...:
放大 → 放大器), and checked them by hand, typing the good ones with the
morphosemantic relations of Fellbaum et al. (2009).  The Japanese pairs were
checked twice; the Chinese ones once, and only 203 of 769, almost all with
器.  The data (sheet ``agents``) and the tagging report are kept in the
Japanese wordnet's repository, in wnja/data/sources/.

A pair is used if the check (column ``link``) accepted it and gave it a link
type, unless it is listed (by S/N) in corrections/agentive-removed.tsv,
where a later review judged that the two senses are not linked this way.
Writes data/agentive_links.tsv, which build_cow.py applies as OEWN
does: the verb sense gets relType ``other`` with the type in dc:type, and the
two senses get ``derivation`` both ways.

Usage:
    uv run --with openpyxl scripts/agentive_links.py \\
        ../wnja/data/sources/agents_240619.xlsx
"""

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "agentive_links.tsv"
REMOVED = ROOT / "corrections" / "agentive-removed.tsv"

#: the report's link types -> the dc:type of OEWN's ``other`` sense relations
REL_TYPES = {
    "agent": "agent",
    "instrument": "instrument",
    "undergoer/patient": "undergoer",
    "vehicle": "vehicle",
    "body-part": "body_part",
    "inanimate agent/cause": "by_means_of",
    "purpose/function": "uses",
}
HEAD = ["verb_synset", "verb", "noun_synset", "noun", "suffix", "rel_type",
        "link_type", "check", "sn"]


def link(row: dict) -> list | None:
    """The output row for one accepted Chinese pair, or None."""
    if row.get("lang") != "cmn" or row.get("link") != "yes":
        return None
    label = row.get("link type")
    if label not in REL_TYPES:
        return None
    return ["cow-" + row["verbsynset"], row["verb"], "cow-" + row["nounsynset"],
            row["noun"], row["match type"], REL_TYPES[label], label, row["link"],
            row["S/N"]]


def main() -> None:
    """Entry point."""
    import openpyxl

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("xlsx", help="agents_240619.xlsx")
    args = parser.parse_args()
    sheet = openpyxl.load_workbook(args.xlsx, read_only=True)["agents"]
    rows = sheet.iter_rows(values_only=True)
    head = next(rows)
    rows = [dict(zip(head, r)) for r in rows]
    removed = set()
    if REMOVED.exists():
        with REMOVED.open(encoding="utf-8", newline="") as f:
            removed = {r["sn"] for r in csv.DictReader(f, delimiter="\t")}
    out = sorted((x for r in rows if (x := link(r)) and str(x[-1]) not in removed),
                 key=lambda x: x[:4])
    untyped = sum(1 for r in rows if r.get("lang") == "cmn" and r.get("link") == "yes"
                  and r.get("link type") not in REL_TYPES)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(HEAD)
        w.writerows(out)
    print(f"{len(out)} links -> {OUT} {dict(Counter(x[5] for x in out))}; "
          f"{untyped} accepted without a type and {len(removed)} removed by review left out")


if __name__ == "__main__":
    main()
