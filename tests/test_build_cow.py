"""Tests for the sense corrections in build_cow.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_cow import apply_sense_corrections

HEAD = "synset_id\tlemma\taction\tconfidence\treason\tsource\tdate\n"


def lexicon() -> dict:
    """Two entries: 猫 in two synsets, 狗 in one; cow-2 is otherwise empty."""
    return {
        "entries": [
            {"id": "e1", "lemma": {"writtenForm": "猫", "partOfSpeech": "n"},
             "senses": [{"id": "s1", "synset": "cow-1"}, {"id": "s2", "synset": "cow-2"}]},
            {"id": "e2", "lemma": {"writtenForm": "狗", "partOfSpeech": "n"},
             "senses": [{"id": "s3", "synset": "cow-3"}]},
        ],
        "synsets": [
            {"id": "cow-1", "members": ["s1"], "relations": [{"target": "cow-2"}]},
            {"id": "cow-2", "members": ["s2"]},
            {"id": "cow-3", "members": ["s3"], "definitions": [{"text": "狗"}]},
        ],
    }


def test_remove_lower_and_drop_empty_synsets(tmp_path: Path) -> None:
    # Arrange
    tsv = tmp_path / "senses.tsv"
    tsv.write_text(HEAD + "cow-2\t猫\tremove\t\twrong\tt\td\n"
                   "cow-3\t狗\tremove\t\twrong\tt\td\n"
                   "cow-1\t猫\tlower\t0.5\tunsure\tt\td\n"
                   "cow-9\t鱼\tremove\t\tgone\tt\td\n", encoding="utf-8")
    lex = lexicon()

    # Act
    removed, lowered, unmatched, _ = apply_sense_corrections(lex, tsv)

    # Assert
    assert (removed, lowered, unmatched) == (2, 1, 1)
    assert [e["id"] for e in lex["entries"]] == ["e1"]
    assert lex["entries"][0]["senses"] == [
        {"id": "s1", "synset": "cow-1", "meta": {"confidenceScore": 0.5}}]
    # cow-2 is empty with no definition: dropped, with the relation to it;
    # cow-3 is empty but has a definition: kept
    assert [ss["id"] for ss in lex["synsets"]] == ["cow-1", "cow-3"]
    assert lex["synsets"][0]["relations"] == []


def test_missing_file_changes_nothing(tmp_path: Path) -> None:
    lex = lexicon()
    assert apply_sense_corrections(lex, tmp_path / "none.tsv") == (0, 0, 0, 0)
    assert len(lex["synsets"]) == 3


def test_rename_moves_sense_or_drops_duplicate(tmp_path: Path) -> None:
    # Arrange: 可以 接受 -> new entry; 狗 狗 -> 狗, which already has cow-3
    tsv = tmp_path / "senses.tsv"
    tsv.write_text(HEAD.rstrip("\n") + "\tnew_lemma\n"
                   "cow-1\t可以 接受\trename\t\tspaces\tt\td\t可以接受\n"
                   "cow-3\t狗 狗\trename\t\tspaces\tt\td\t狗\n", encoding="utf-8")
    lex = lexicon()
    lex["entries"] += [
        {"id": "e3", "lemma": {"writtenForm": "可以 接受", "partOfSpeech": "n",
                               "pronunciations": [{"text": "ke3 yi3 jie1 shou4"}]},
         "senses": [{"id": "s4", "synset": "cow-1"}]},
        {"id": "e4", "lemma": {"writtenForm": "狗 狗", "partOfSpeech": "n"},
         "senses": [{"id": "s5", "synset": "cow-3"}]}]
    lex["synsets"][0]["members"].append("s4")
    lex["synsets"][2]["members"].append("s5")

    # Act
    removed, _, unmatched, _ = apply_sense_corrections(lex, tsv)

    # Assert
    forms = {e["lemma"]["writtenForm"]: e for e in lex["entries"]}
    assert set(forms) == {"猫", "狗", "可以接受"}
    assert forms["可以接受"]["senses"] == [{"id": "s4", "synset": "cow-1"}]
    assert forms["可以接受"]["lemma"]["pronunciations"] == [{"text": "ke3 yi3 jie1 shou4"}]
    assert (removed, unmatched) == (1, 0)
    assert lex["synsets"][2]["members"] == ["s3"]


def test_add_particle_lemma_with_copied_pinyin(tmp_path: Path) -> None:
    # Arrange: cow-2 loses 猫, then gains 明亮的 (non-lexicalized) and 猫 again
    tsv = tmp_path / "senses.tsv"
    tsv.write_text(HEAD.rstrip("\n") + "\tnew_lemma\n"
                   "cow-2\t明亮+的\tadd\t\trescued\tt\td\t\n"
                   "cow-3\t狗\tadd\t\talready\tt\td\t\n", encoding="utf-8")
    lex = lexicon()
    lex["synsets"][1]["partOfSpeech"] = "n"
    lex["synsets"][2]["partOfSpeech"] = "n"
    lex["entries"].append({"id": "e9", "lemma": {"writtenForm": "明亮的", "partOfSpeech": "a",
                                                 "pronunciations": [{"text": "ming2 liang4 de5"}]},
                           "senses": [{"id": "s9", "synset": "cow-1"}]})

    # Act
    *_, added = apply_sense_corrections(lex, tsv)

    # Assert: one new entry (n, not the a entry), pinyin copied; 狗 already in cow-3
    assert added == 1
    new = next(e for e in lex["entries"] if e["lemma"]["partOfSpeech"] == "n"
               and e["lemma"]["writtenForm"] == "明亮的")
    assert new["lemma"]["pronunciations"] == [{"text": "ming2 liang4 de5"}]
    assert new["senses"][0]["lexicalized"] is False
    assert new["senses"][0]["id"] in lex["synsets"][1]["members"]


def test_add_sense_links_typed_and_derivation(tmp_path: Path) -> None:
    # Arrange
    from build_cow import add_sense_links
    lex = {"entries": [
        {"id": "e1", "lemma": {"writtenForm": "放大", "partOfSpeech": "v"},
         "senses": [{"id": "v1", "synset": "cow-1-v"}]},
        {"id": "e2", "lemma": {"writtenForm": "放大器", "partOfSpeech": "n"},
         "senses": [{"id": "n1", "synset": "cow-2-n"}]}]}
    tsv = tmp_path / "links.tsv"
    tsv.write_text("verb_synset\tverb\tnoun_synset\tnoun\trel_type\n"
                   "cow-1-v\t放大\tcow-2-n\t放大器\tinstrument\n"
                   "cow-1-v\t放大\tcow-2-n\t放大器\tinstrument\n"
                   "cow-1-v\t放大\tcow-3-n\t缩小器\tinstrument\n", encoding="utf-8")
    # Act
    added, skipped = add_sense_links(lex, tsv)
    # Assert
    verb, noun = lex["entries"][0]["senses"][0], lex["entries"][1]["senses"][0]
    assert (added, skipped) == (1, 1)
    assert verb["relations"] == [
        {"target": "n1", "relType": "other", "meta": {"type": "instrument"}},
        {"target": "n1", "relType": "derivation"}]
    assert noun["relations"] == [{"target": "v1", "relType": "derivation"}]
