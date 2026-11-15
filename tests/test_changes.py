"""The change records must be well formed and fit the base."""

import sys
from collections import Counter
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
release = pytest.importorskip("release", reason="needs ../NTUMC (ntumc.wordnet)")

from ntumc.wordnet import changes, lmf, validate  # noqa: E402
from ntumc.wordnet.model import Entry, Pronunciation  # noqa: E402


def test_every_record_is_well_formed() -> None:
    # Act
    records = list(changes.read(release.CHANGES))
    problems = [(r.id, p) for r in records for p in changes.validate(r)]
    ids = Counter(r.id for r in records)
    # Assert
    assert problems == []
    assert [i for i, n in ids.items() if n > 1] == []
    assert {r.lexicon for r in records} == {"cow"}


def test_the_records_apply_to_the_base_without_conflict() -> None:
    # Arrange
    if not release.BASE.exists():
        pytest.skip("base release not downloaded: run release.py once")
    # Act
    _, conflicts = changes.apply(lmf.read(release.BASE), changes.read(release.CHANGES))
    # Assert
    assert conflicts == []


def test_the_lexicon_passes_the_validation_of_wn(tmp_path: Path) -> None:
    # Arrange
    pytest.importorskip("wn")
    if not release.BASE.exists():
        pytest.skip("base release not downloaded: run release.py once")
    items, _ = changes.apply(lmf.read(release.BASE), changes.read(release.CHANGES))
    xml = tmp_path / "changed.xml"
    lmf.write(xml, items)
    # Act
    good = validate.check(xml)
    # Assert
    assert good


def test_without_pinyin_lists_only_new_entries() -> None:
    # Arrange
    items = [Entry(lemma="狗", pos="n"),
             Entry(lemma="猫", pos="n"),
             Entry(lemma="鸟", pos="n", pronunciations=[Pronunciation(text="niao3")])]
    # Act
    found = release.without_pinyin(items, {("狗", "n")})
    # Assert
    assert found == ["猫"]
