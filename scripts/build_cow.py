#!/usr/bin/env python3
"""Build a Chinese Open Wordnet (COW) release from the NTU-MC export.

Input is the curated Chinese export from NTU-MC's getwn.py, which leaves
out senses only from automatic sources (BOW, SEW, Wiktionary) and the
segmented variants (cmn:mwe):

    cd ../NTUMC
    .venv/bin/python scripts/getwn.py build/wn-ntumc.db OUT --lang cmn \\
        --version 1.0 --exclude-src bow,sew,wikt,cmn:mwe \\
        --ili build/ili-map-pwn30.tab --base omw-en:2.0
    .venv/bin/python scripts/addpinyin.py CEDICT OUT/wn-ntumc-cmn.xml --db ...

This re-ids the lexicon from ntumc-cmn to cow, sets the COW metadata and
writes a wn package (cow/cow-VERSION.xml with README, LICENSE and
citation.bib) and its .tar.xz.

Usage:
    scripts/build_cow.py NTUMC_CMN_XML --version 1.0 [-o release]
"""

import argparse
import shutil
import tarfile
from pathlib import Path

from wn import lmf

ROOT = Path(__file__).resolve().parents[1]
WN_ID = "cow"
META = {
    "label": "Chinese Open Wordnet",
    "language": "cmn-Hans",
    "email": "bond@ieee.org",
    "license": "https://bond-lab.github.io/cow/LICENSE",
    "url": "https://bond-lab.github.io/cow/",
    "citation": (
        "Shan Wang and Francis Bond. 2013. Building the Chinese Open Wordnet"
        " (COW): Starting from Core Synsets. In Proceedings of the 11th"
        " Workshop on Asian Language Resources (ALR-11), IJCNLP 2013,"
        " pp 10-18. Nagoya."
    ),
}


def reprefix(lex: dict, old: str, new: str) -> None:
    """Change every ID prefix in a lexicon from old- to new-."""
    def fix(s: str) -> str:
        return new + s[len(old):] if s and s.startswith(old + "-") else s

    for ss in lex["synsets"]:
        ss["id"] = fix(ss["id"])
        for rel in ss.get("relations", []):
            rel["target"] = fix(rel["target"])
        if "members" in ss:
            ss["members"] = [fix(m) for m in ss["members"]]
    for entry in lex["entries"]:
        entry["id"] = f"{new}-{entry['id']}" if not entry["id"].startswith(new) else entry["id"]
        for sense in entry.get("senses", []):
            sense["id"] = fix(sense["id"])
            sense["synset"] = fix(sense["synset"])


def package(xml: Path, outdir: Path, version: str) -> Path:
    """Write the wn package directory and its .tar.xz; return the tarball."""
    pkg = outdir / WN_ID
    pkg.mkdir(parents=True, exist_ok=True)
    shutil.copy(xml, pkg / f"{WN_ID}-{version}.xml")
    shutil.copy(ROOT / "docs" / "LICENSE", pkg / "LICENSE")
    shutil.copy(ROOT / "README.md", pkg / "README.md")
    shutil.copy(ROOT / "data" / "citation.bib", pkg / "citation.bib")
    tar = outdir / f"{WN_ID}-{version}.tar.xz"
    with tarfile.open(tar, "w:xz") as tf:
        tf.add(pkg, arcname=WN_ID)
    return tar


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("xml", help="Curated cmn XML from NTU-MC getwn.py")
    parser.add_argument("--version", required=True, help="Release version")
    parser.add_argument("-o", "--outdir", default=str(ROOT / "release"),
                        help="Output directory (default: release/)")
    args = parser.parse_args()

    data = lmf.load(args.xml)
    lex = data["lexicons"][0]
    print(f"  {lex['id']}:{lex['version']}: {len(lex['entries'])} entries, "
          f"{len(lex['synsets'])} synsets")
    reprefix(lex, lex["id"], WN_ID)
    lex.update(META, id=WN_ID, version=args.version)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    xml = outdir / f"{WN_ID}-{args.version}.xml"
    lmf.dump(data, str(xml))
    tar = package(xml, outdir, args.version)
    print(f"  wrote {xml} and {tar}")


if __name__ == "__main__":
    main()
