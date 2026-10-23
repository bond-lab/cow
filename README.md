# Chinese Open Wordnet (COW)

The Chinese Open Wordnet is a wordnet for Mandarin Chinese (simplified
characters), linked to the Princeton WordNet and the Collaborative
Interlingual Index (CILI).

Web page: <https://bond-lab.github.io/cow/>

## Version 1.0 (2026-10)

| | |
|---|---|
| Synsets | 47,124 (46,757 with Chinese words; 2,028 new) |
| Words (lexical entries) | 85,147 (84,790 with pinyin) |
| Senses | 109,045 |
| Chinese definitions | 6,534 |

COW 1.0 is the curated Chinese wordnet maintained in the
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

## Using it with `wn`

```python
import wn
wn.download("omw-en:2.0")
wn.download("https://github.com/bond-lab/cow/releases/download/v1.0/cow-1.0.tar.xz")
cow = wn.Wordnet("cow:1.0")
cow.words("狗")
```

## History

* 1.0 (2026-10): first release in WN-LMF; built from the NTU-MC database
* 0.9 (2014-01-23): initial public beta (in `docs/data/0.9/`)

## People

Shan Wang and Francis Bond built COW (2013–2014).  Francis Bond and
Luís Morgado da Costa extended it (2015–2022), with the annotators of
the NTU-MC.  Jia Qi Yeo added definitions and reviewed lemmas (2020).

## License

A WordNet-style permissive license: see [LICENSE](docs/LICENSE).

## Citation

Shan Wang and Francis Bond (2013). Building the Chinese Open Wordnet
(COW): Starting from Core Synsets. In *Proceedings of the 11th Workshop
on Asian Language Resources (ALR-11), IJCNLP 2013*, pp 10–18. Nagoya.
See [citation.bib](data/citation.bib).
