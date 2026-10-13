
import pytest

from src.trie import Trie


def test_insert_and_search():
    trie = Trie()
    trie.insert("CAT")

    assert trie.search("CAT")
    assert not trie.search("CAR")


def test_shared_prefixes():
    trie = Trie()

    for word in ["CAT", "CAR", "CARD"]:
        trie.insert(word)

    assert trie.search("CAT")
    assert trie.search("CAR")
    assert trie.search("CARD")
    assert trie.starts_with("CA")
    assert trie.starts_with("CAR")
    assert not trie.search("CA")


def test_case_insensitive_search():
    trie = Trie()
    trie.insert("Python")

    assert trie.search("PYTHON")
    assert trie.search("python")


def test_duplicate_words_are_counted_once():
    trie = Trie()
    trie.insert("CAT")
    trie.insert("CAT")
    trie.insert("cat")

    assert len(trie) == 1


def test_invalid_words_are_rejected():
    trie = Trie()

    for word in ["", "123", "CAT!", "CAFÉ"]:
        with pytest.raises(ValueError):
            trie.insert(word)


def test_non_string_is_rejected():
    trie = Trie()

    with pytest.raises(ValueError):
        trie.insert(None)


def test_missing_prefix():
    trie = Trie()
    trie.insert("DOG")

    assert not trie.starts_with("CA")
    assert not trie.search("DO")
