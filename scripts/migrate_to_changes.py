#!/usr/bin/env python3
"""One-off: turn the work done since COW 1.1 into change records.

COW 1.1 was built by build_cow.py from the NTU-MC export and
corrections/.  From 1.1 on, the released XML is the base and changes/
is the master (see changes/README.md).  This script made the first
change log:

    scripts/build_cow.py wn-ntumc-cmn.xml --version 1.1 -o build/old --cedict CEDICT
    cd ../NTUMC && uv run python -m ntumc.wordnet diff \
        ../cow/build/base/cow-1.1.xml ../cow/build/old/cow-1.1.xml \
        ../cow/build/since-1.1.jsonl \
        --user fcbond --source build --reason "since 1.1" --base cow-1.1
    cd ../cow && PYTHONPATH=../NTUMC:. ../NTUMC/.venv/bin/python \
        scripts/migrate_to_changes.py build/since-1.1.jsonl changes/cow-1.1.jsonl

It gives each record from the diff the source, reason and date of the
row in corrections/senses.tsv or data/agentive_links.tsv that caused it,
and adds a ``reject_sense_relation`` record for each pair in
corrections/agentive-removed.tsv: those pairs were never in a release,
so leaving them out made no change.
"""

import csv
import sys
from pathlib import Path

from ntumc.wordnet import changes

ROOT = Path(__file__).resolve().parent.parent
AGENTIVE = ("Bond and Lim (2019): pairs checked once by hand "
            "(data/agentive_links.tsv)")
DROPPED = "scripts/build_cow.py: a synset with no sense and no definition is dropped"


def rows(path: Path) -> list[dict[str, str]]:
    """The rows of a tab-separated file with a header."""
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def main() -> None:
    """Entry point."""
    raw, out = Path(sys.argv[1]), Path(sys.argv[2])
    senses = {(r["synset_id"], r["lemma"]): r
              for r in rows(ROOT / "corrections" / "senses.tsv") if r["action"] == "remove"}
    links = {}
    for r in rows(ROOT / "data" / "agentive_links.tsv"):
        links[(r["verb_synset"], r["verb"], r["noun_synset"], r["noun"])] = r
        links[(r["noun_synset"], r["noun"], r["verb_synset"], r["verb"])] = r
    records, emptied, unmatched = [], {}, 0
    for n, c in enumerate(changes.read(raw), start=1):
        c.id = f"cow-1.1-{n}"
        if c.action == "remove_sense" and (row := senses.get((c.synset, c.lemma))):
            c.source, c.reason, c.date = row["source"], row["reason"], row["date"]
            emptied[c.synset] = row["date"]
        elif c.action == "add_sense_relation" and (
                link := links.get((c.synset, c.lemma, c.target, c.target_lemma))):
            c.source = AGENTIVE
            c.reason = f"agentive noun link, {link['link_type']} (S/N {link['sn']})"
        elif c.action == "remove_synset" and c.synset in emptied:
            c.source, c.date = DROPPED, emptied[c.synset]
            c.reason = "its last sense was removed; omw-en has the concept through the ILI"
        else:
            unmatched += 1
        records.append(c)
    linked = {(r.synset, r.lemma, r.target, r.target_lemma) for r in records
              if r.action == "add_sense_relation"}
    for row in rows(ROOT / "corrections" / "agentive-removed.tsv"):
        pair = ("cow-" + row["verb_synset"], row["verb"],
                "cow-" + row["noun_synset"], row["noun"])
        if pair in linked:
            print("linked and rejected, left for a person:", row["sn"], *pair)
            continue
        records.append(changes.Change(
            id=f"cow-1.1-{len(records) + 1}", action="reject_sense_relation",
            lexicon="cow", synset=pair[0], lemma=pair[1], target=pair[2],
            target_lemma=pair[3], user="fcbond", date=row["date"], source=row["source"],
            reason=f"{row['reason']} (S/N {row['sn']})", base="cow-1.1"))
    n = changes.write(out, records)
    print(f"{n} records, {unmatched} without a corrections row")


if __name__ == "__main__":
    main()
