# COW corrections

Corrections to the Chinese export of the NTU-MC wordnet, applied by
`scripts/build_cow.py` when it builds a release.  The export is a build
artefact, so fixes are kept here as data: auditable, reviewable as diffs and
reapplied on every rebuild.

## `senses.tsv`

Tab-separated, UTF-8, with a header row:

```
synset_id	lemma	action	confidence	reason	source	date	new_lemma
```

A sense is named by its COW synset ID (e.g. `cow-00001740-a`) and the
entry's lemma (written form).  `action` is

* `remove`: delete the sense, and the entry if it has no senses left;
* `lower`: set `confidenceScore` to `confidence` unless it is already lower;
* `rename`: move the sense to the entry for `new_lemma` (same part of
  speech), creating it with the old entry's pinyin, or drop the sense if
  that entry already has the synset;
* `add`: add the sense; a lemma ending in `+的`/`+地` loses the `+` and the
  sense is marked non-lexicalized, as `addpinyin.py` does.

After the corrections, synsets left with no senses and no definition are
dropped, since the base wordnet has them through the ILI.  `build_cow.py`
reports how many rows matched no sense.  New entries get pinyin by running
NTU-MC's `addpinyin.py` again on the built XML (it only fills lemmas that
have none):

    scripts/build_cow.py NTUMC_CMN_XML --version 1.1 -o release
    ../NTUMC/.venv/bin/python ../NTUMC/scripts/addpinyin.py CEDICT \
        release/cow-1.1.xml --db ../NTUMC/build/wn-ntumc.db

### 2026-10-24: review of every COW 1.0 sense

Claude Haiku flagged 9,850 of 109,045 senses as suspect; two blind Claude
Opus runs judged each flagged sense, and an Opus adjudicator decided where
they disagreed.  Each run also noted malformed lemmas; a note counts when
both runs gave it.

* `remove`, 4,185: the sense is wrong (e.g. a different sense of an
  ambiguous English word);
* `remove`, 705 with source `... + form note`: both runs found the lemma
  malformed (a phrase or explanation, a pattern like 除了...之外, English)
  and it has no mechanical fix, or its meaning was also judged wrong;
* `rename`, 396: a malformed lemma with a mechanical fix (spaces between
  characters joined, traditional characters simplified with OpenCC, e.g.
  可以 接受 → 可以接受, 黑花槐樹 → 黑花槐树) whose meaning was not judged
  wrong;
* `remove`, 42: such a fix gives a form the synset already has (最後 → 最后);
* `lower` to 0.5, 120: undecided.

### 2026-10-24: senses rescued from excluded sources

COW leaves out senses that come only from automatic sources (BOW, SEW,
Wiktionary).  After the review, 395 COW synsets had a definition but no
senses, although the NTU-MC wordnet had 1,313 candidate lemmas for them from
those sources.  Two blind Opus runs and an adjudicator judged them; the
1,078 judged right and not malformed are `add` rows (source `rescue: ...`),
filling 380 of the 395 synsets.

### 2026-10-24: mechanical form fixes

143 `rename` rows with source `form: mechanical`, made by NTU-MC's
`scripts/form_fixes.py` for lemmas the review did not flag: 80 with spaces
between Han characters (游戏 规则 → 游戏规则), 48 with traditional
characters (開齋節 → 开斋节; a character whose simplified form is outside
the basic CJK block, such as 鰤 → 𫚕, is kept), and 15 with full-width
digits or letters (４月 → 4月, 卡拉ＯＫ → 卡拉OK).

The reviews, reasons and scripts are in the NTU-MC repository
(`scripts/triage_review.py`, `scripts/cow_rescue.py`; the run files are in
`build/triage*/` and `build/rescue*/`).
