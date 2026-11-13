#!/usr/bin/env python3
"""One-off: add the senses the corpus is tagged with that the release left out.

The release leaves out senses that come only from automatic sources.
Where the NTU-MC corpus has concepts tagged with such a sense, a tagger
chose it, so it is added here as an ``add_sense`` record, with the
confidence the NTU-MC wordnet gives it.  A synset the lexicon does not
have yet is added first, with its ILI and no relations: omw-en has the
concept.  Senses that a review removed are not added (they are in
NTU-MC docs/quality-sample/removed-but-tagged/ for a ruling).

    PYTHONPATH=../NTUMC:. ../NTUMC/.venv/bin/python scripts/add_back_corpus.py \
        LEXICON CANDIDATES.tsv

CANDIDATES.tsv (synset, lemma, pos, corpus, src, confidence, new_synset,
ili, definition) was made from the NTU-MC wordnet database frozen on
2026-11-13 and the corpus database.
"""

import csv
import sys
from pathlib import Path

from ntumc.wordnet import changes

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    """Entry point."""
    lexicon, candidates = sys.argv[1], Path(sys.argv[2])
    path = next((ROOT / "changes").glob(f"{lexicon}-*.jsonl"))
    base = path.stem
    records = list(changes.read(path))
    if any("a tagger chose it" in (r.reason or "") for r in records):
        raise SystemExit(f"{path} already has these senses")
    made: set[str] = set()

    def add(action: str, **fields: str | None) -> None:
        records.append(changes.Change(
            id=f"{base}-{len(records) + 1}", action=action, lexicon=lexicon,
            user="fcbond", date="2026-11-13", base=base, **fields))

    with candidates.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if row["new_synset"] and row["synset"] not in made:
                made.add(row["synset"])
                add("add_synset", synset=row["synset"], pos=row["pos"],
                    ili=row["ili"], new=row["definition"],
                    source="NTU-MC wordnet database, frozen 2026-11-13",
                    reason="for a sense the corpus is tagged with")
            add("add_sense", synset=row["synset"], lemma=row["lemma"], pos=row["pos"],
                new=row["confidence"] or None,
                source=f"NTU-MC corpus: {row['corpus']} concepts tagged with it",
                reason=f"left out of the release for its source ({row['src']}); "
                       "a tagger chose it")
    print(changes.write(path, records), "records")


if __name__ == "__main__":
    main()
