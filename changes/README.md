# Changes

From COW 1.1 on, the master copy of COW is

* the last release, `cow-1.1.xml` (fetched from the GitHub release and
  checked against its checksum by `release.py`), and
* `cow-1.1.jsonl`: every change made since, one per line, in order.

`../NTUMC/.venv/bin/python release.py 1.2` applies the changes to the
base and writes `release/cow-1.2.xml` and its package.  After a release,
the new XML is the base and a new, empty `cow-1.2.jsonl` is started; the
old file stays as the history.

Nothing is rebuilt from the NTU-MC export any more: `scripts/build_cow.py`
and `corrections/` are how 1.1 and the first change log were made, and
are kept for the record.

## A change record

```json
{"id": "cow-1.1-4", "action": "remove_sense", "lexicon": "cow",
 "synset": "cow-03066849-n", "lemma": "过滤器", "pos": "n",
 "user": "fcbond", "date": "2026-10-26",
 "source": "agentive review: 2 blind sonnet (both runs)",
 "reason": "not colander: filter, not colander", "base": "cow-1.1"}
```

To make a change, add a line at the end.  Never edit or delete an
earlier line: to undo a change, add the opposite one.

* `id` is unique; `user`, `source` (the evidence: a person, a
  dictionary, a corpus) and `reason` are required.
* A model alone is not a source for an addition.
* A synset left with no sense and nothing of its own (definition,
  example) is dropped by `release.py`, as the old build did: omw-en has
  the concept through the ILI.  No record is needed.  (The one
  `remove_synset` record in the first log was written before this rule
  was put back; it is harmless.)
* A new entry has no pinyin: `release.py` lists new entries without it,
  to be filled by NTU-MC's `addpinyin.py`.
* `reject_sense_relation` records a decision that two senses are not
  related; adding that relation later is a conflict.

The actions and the fields each needs are in NTU-MC
`docs/wordnet-model.md`.

## The first log

`cow-1.1.jsonl` starts with the 135 changes between the 1.1 release and
the repository on 2026-11-13: 5 senses removed, 1 synset dropped, and
129 sense relations (the 43 agentive noun links of Bond and Lim 2019,
three relations each).  They were made by building once more the old way
and comparing with 1.1 (`scripts/migrate_to_changes.py`); each has the
source, reason and date of its row in `corrections/`.

They are followed by 9 `reject_sense_relation` records: the pairs a
review rejected (`corrections/agentive-removed.tsv`), which were never
in a release and so made no change.
