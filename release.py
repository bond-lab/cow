#!/usr/bin/env python3
"""Make the next COW release: the last release plus the change records.

    ../NTUMC/.venv/bin/python release.py VERSION    # e.g. 1.2

The base is the released cow-BASE_VERSION.xml, downloaded once to
build/base/ and checked against its checksum.  The changes are
changes/cow-BASE_VERSION.jsonl (see changes/README.md).  A change that
does not fit the base is a conflict: they are listed, and nothing is
written until they are settled.  Synsets left with no sense and nothing
of their own (definition, example) are then dropped: omw-en has the
concept through the ILI.

Two lexicons are written.  release/cow-min-VERSION.xml is the minimal
one (id cow-min), the master: for a concept CILI does not have yet it
holds the words and the concept's identifier, and leaves the English
definition and the relations to the shared lexicon omw-ntumc.
release/cow-VERSION.xml is the export (id cow), with those put back; it
is what goes in the wn package release/cow-VERSION.tar.xz (the XML with
README, LICENSE and citation.bib).  omw-ntumc is read from a checkout
beside this one, built at its tag (uv run build.py SHARED_VERSION).  Entries that are not in
the base and have no pinyin are listed: an entry made by add_sense has
none until NTU-MC's addpinyin.py is run on the XML.

Uses ntumc.wordnet from a checkout of NTU-MC beside this one (../NTUMC).
"""

import argparse
import hashlib
import io
import logging
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "NTUMC"))

from ntumc.wordnet import changes, lmf, shared  # noqa: E402
from ntumc.wordnet.model import Entry, Item, Lexicon  # noqa: E402

WN_ID = "cow"
BASE_VERSION = "1.1"
BASE_URL = ("https://github.com/bond-lab/cow/releases/download/"
            f"v{BASE_VERSION}/cow-{BASE_VERSION}.tar.xz")
BASE_XZ_SHA256 = "93e9357dda50a38ce626904c2229479afa177df74d9c504aebfeba06ff2f241e"
BASE_XML_SHA256 = "c07e0c1e9870e344674df76d3dd50eb912c829301795c2141fa5d563d32ef13f"
BASE = ROOT / "build" / "base" / f"cow-{BASE_VERSION}.xml"
CHANGES = ROOT / "changes" / f"cow-{BASE_VERSION}.jsonl"
SHARED_VERSION = "0.1"
SHARED = ROOT.parent / "omw-ntumc" / "build" / f"omw-ntumc-{SHARED_VERSION}.xml"
SHARED_SHA256 = "6ee5f6a254907d4fbdaa0e4238dddf0c3012ee92ef27fdd7d79815c46ff7c3f0"

log = logging.getLogger("release")


def fetch_base(path: Path = BASE) -> None:
    """Download the base release to path, unless it is there; check it.

    Raises:
        ValueError: if the download or the file does not match its checksum.
    """
    if not path.exists():
        log.info("Downloading %s", BASE_URL)
        with urllib.request.urlopen(BASE_URL) as resp:
            data = resp.read()
        if hashlib.sha256(data).hexdigest() != BASE_XZ_SHA256:
            raise ValueError(f"{BASE_URL}: checksum mismatch")
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:xz") as tf:
            member = tf.extractfile(f"{WN_ID}/cow-{BASE_VERSION}.xml")
            if member is None:
                raise ValueError(f"{BASE_URL}: no cow-{BASE_VERSION}.xml inside")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(member.read())
    if hashlib.sha256(path.read_bytes()).hexdigest() != BASE_XML_SHA256:
        raise ValueError(f"{path} is not the released COW {BASE_VERSION}")


def without_pinyin(items: list[Item], known: set[tuple[str, str]]) -> list[str]:
    """New entries with no pinyin.

    Args:
        items: the lexicon's items
        known: (lemma, part of speech) of the entries of the base

    Returns:
        The lemma of each entry that is not in the base and has no pronunciation
    """
    return [str(e.lemma) for e in items
            if isinstance(e, Entry) and not e.pronunciations
            and (str(e.lemma), str(e.pos)) not in known]


def release(version: str, out: Path) -> list[str]:
    """Apply the change records to the base; write the minimal lexicon and the export.

    Args:
        version: the version of the new release
        out: the export's XML file; the minimal lexicon goes beside it.
            Neither is written if there are conflicts

    Returns:
        The conflicts, one line each.

    Raises:
        ValueError: if the export lacks something the lexicon said before
            it was split.
    """
    fetch_base()
    base = list(lmf.read(BASE))
    known = {(str(e.lemma), str(e.pos)) for e in base if isinstance(e, Entry)}
    items, conflicts = changes.apply(base, changes.read(CHANGES))
    if conflicts:
        return conflicts
    items, dropped = changes.drop_empty_synsets(items)
    if changes.shared_ilis(items):
        return changes.shared_ilis(items)
    log.info("Dropped %d synsets with no sense and nothing of their own", len(dropped))
    for lemma in without_pinyin(items, known):
        log.warning("%s is new and has no pinyin: run NTU-MC's addpinyin.py", lemma)
    next(i for i in items if isinstance(i, Lexicon)).version = version
    out.parent.mkdir(parents=True, exist_ok=True)
    shared.write_release(items, shared.load(SHARED, SHARED_SHA256), out)
    return []


def package(xml: Path, version: str) -> Path:
    """Write the wn package directory and its .tar.xz beside the XML.

    Args:
        xml: the release XML
        version: its version

    Returns:
        The tarball
    """
    pkg = xml.parent / WN_ID
    shutil.rmtree(pkg, ignore_errors=True)  # a package holds exactly one XML
    pkg.mkdir(parents=True)
    shutil.copy(xml, pkg / f"{WN_ID}-{version}.xml")
    shutil.copy(ROOT / "docs" / "LICENSE", pkg / "LICENSE")
    shutil.copy(ROOT / "README.md", pkg / "README.md")
    shutil.copy(ROOT / "data" / "citation.bib", pkg / "citation.bib")
    tar = xml.parent / f"{WN_ID}-{version}.tar.xz"
    with tarfile.open(tar, "w:xz") as tf:
        tf.add(pkg, arcname=WN_ID)
    return tar


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("version", help="version of the new release, e.g. 1.2")
    parser.add_argument("-o", "--outdir", default=str(ROOT / "release"),
                        help="output directory (default: release/)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    out = Path(args.outdir) / f"{WN_ID}-{args.version}.xml"
    conflicts = release(args.version, out)
    if conflicts:
        for line in conflicts:
            log.error(line)
        sys.exit(1)
    log.info("Wrote %s, its minimal lexicon and %s", out, package(out, args.version))


if __name__ == "__main__":
    main()
