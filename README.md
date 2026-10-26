# Chinese Open Wordnet (COW)

The Chinese Open Wordnet is a wordnet for Mandarin Chinese (simplified
characters), linked to the Princeton WordNet and the Collaborative
Interlingual Index (CILI).

Web page: <https://bond-lab.github.io/cow/>

## Version 1.1 (2026-10)

| | |
|---|---|
| Synsets | 46,189 (46,147 with Chinese words) |
| Words (lexical entries) | 82,660 (82,404 with pinyin) |
| Senses | 105,175 |
| Chinese definitions | 6,534 |
| Chinese examples | 614 |

COW 1.1 removes 4,948 senses found wrong or malformed in a review of
every COW 1.0 sense (Claude Haiku flagged suspects, two blind Claude Opus
runs judged them, an Opus adjudicator decided disagreements), lowers the
confidence of 120 undecided ones, fixes the form of 539 lemmas (spaces,
traditional or full-width characters), adds back 1,078 checked senses
from the excluded automatic sources for synsets left with none, and adds
examples.  See `corrections/README.md`.

COW is the curated Chinese wordnet maintained in the
[NTU Multilingual Corpus](https://github.com/bond-lab/NTUMC) (NTU-MC)
database.  It contains COW 0.9 (2014) and the senses, words and
definitions added and checked since then while sense-tagging the
Chinese part of the NTU-MC.  This release adds about 6,000 Chinese
definitions and a review of lemmas by Jia Qi Yeo (made in 2020,
applied in 2026).

Senses that come only from automatically linked resources (BOW, SEW,
Wiktionary) and segmented variants (购物 中心) are left out; the full,
unfiltered data is in the NTU-MC database and its `ntumc-cmn` export.
Pinyin is added from CC-CEDICT.

The synsets and relations are based on Princeton WordNet 3.0.  COW also
adds 2,028 synsets of its own (concepts lexicalised in Chinese, *chengyu*,
classifiers and pronouns), linked into the hierarchy by 4,796 relations.

The wordnet is in WN-LMF 1.4 format and extends the English
`omw-en:2.0` wordnet: it declares `<Requires ref="omw-en" version="2.0"/>`
and leaves out structure shared with it.

### Agentive nouns (not yet in a release)

`data/agentive_links.tsv` has 56 links between a verb sense and a noun
sense formed from it with an agentive suffix, checked by hand by Ryan Lim
Dao Wei (Bond and Wei 2019), almost all with 器: 放大 → 放大器 *amplifier*
(instrument).  Only 203 of the 769 Chinese candidates were checked, once;
one accepted pair with no link type is left out.  As in the Open English
Wordnet, the verb sense gets a `SenseRelation` of type `other` with the link
type in `dc:type` (44 instrument, 11 uses, 1 by_means_of), and the two senses
are linked by `derivation` both ways.  `build_cow.py` adds the 50 whose
senses are in COW (`--links`); `scripts/agentive_links.py` remakes the file
from the source spreadsheet, which is kept with the
[Japanese wordnet](https://github.com/bond-lab/wnja) (`data/sources/`),
where the same method gave 769 links.

Francis Bond and Ryan Lim Dao Wei (2019). Generating Derivational
Relations for the Japanese WordNet: The Case of Agentive Nouns. In
*2019 International Conference on Asian Language Processing (IALP)*.
<https://ieeexplore.ieee.org/abstract/document/8939615>

## Using it with `wn`

```python
import wn
wn.download("omw-en:2.0")
wn.download("https://github.com/bond-lab/cow/releases/download/v1.1/cow-1.1.tar.xz")
cow = wn.Wordnet("cow:1.1")
cow.words("狗")
```

## Building

COW is built from the curated Chinese export of the NTU-MC database.  The
export used for 1.1 is `wn-ntumc-cmn.xml.xz` in the NTU-MC release
[wn-2026.10](https://github.com/bond-lab/NTUMC/releases/tag/wn-2026.10)
(checksums in its `SHA256SUMS`):

    xz -d wn-ntumc-cmn.xml.xz
    scripts/build_cow.py wn-ntumc-cmn.xml --version 1.1 --cedict CEDICT

`build_cow.py` applies `corrections/senses.tsv` and writes
`release/cow-1.1.xml` and `release/cow-1.1.tar.xz`.  `--cedict` gives
entries new in the corrections their pinyin with NTU-MC's `addpinyin.py`,
so it needs an NTU-MC checkout next to this one (`--ntumc`).

## History

* 1.1 (2026-10): reviewed senses (LLM review, see `corrections/`); examples
* 1.0 (2026-10): first release in WN-LMF; built from the NTU-MC database
* 0.9 (2014-01-23): initial public beta (in `docs/data/0.9/`)

## People

Shan Wang and Francis Bond built COW (2013–2014).  Francis Bond and
Luís Morgado da Costa extended it (2015–2022), with the annotators of
the NTU-MC.  Gao Huini Eshley, Hazel Mok Shu Wen and Jeanette Yiwen
Tan also contributed.  Jia Qi Yeo added definitions and reviewed
lemmas (2020).

## License

A WordNet-style permissive license: see [LICENSE](docs/LICENSE).

## Citation

Shan Wang and Francis Bond (2013). Building the Chinese Open Wordnet
(COW): Starting from Core Synsets. In *Proceedings of the 11th Workshop
on Asian Language Resources (ALR-11), IJCNLP 2013*, pp 10–18. Nagoya.
See [citation.bib](data/citation.bib), which also has the papers on
the sense-tagged corpora COW was extended from (Bond et al. 2013;
Wang and Bond 2014; Bond and Wang 2014), numeral classifiers (Mok et
al. 2012; Morgado da Costa et al. 2016), pronouns (Seah and Bond 2014)
and exclamatives (Morgado da Costa and Bond 2016).
