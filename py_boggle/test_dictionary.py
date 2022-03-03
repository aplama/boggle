import copy
import random
import string
from typing import List, Optional, Set, Tuple

import pytest
from py_boggle.boggle_dictionary import BoggleDictionary
from py_boggle.game_dictionary import GameDictionary


# read words file
WORDS_FILE = "words.txt"
words: Set[str] = set()
with open(WORDS_FILE, "r") as fin:
    for line in fin:
        line = line.strip().upper()
        words.add(line)


def test_contains_all():
    """Test that the contains() returns True for all of the words specified
    in the dictionary file.
    """

    # make dictionary
    game_dict = GameDictionary()
    game_dict.load_dictionary(WORDS_FILE)

    for s in words:
        assert game_dict.contains(s)


def test_prefixes():
    """Test that is_prefix returns True for random prefixes of words
    in the dictionary file.
    """
    game_dict = GameDictionary()
    game_dict.load_dictionary(WORDS_FILE)

    random.seed(12345)
    for s in words:
        idx = random.randint(0, len(s) - 1)
        pfx = s[:idx]
        assert game_dict.is_prefix(pfx)

def test_iterator_exception():
    """Tests that the GameDictionary iterator raises a StopIteration
    when all elements have been returned.

    Python iterators do not have a `hasNext()` method and only terminate
    when a StopIteration is raised. Many dictionary tests use the
    iterator and will hang if the exception is not raised.

    The iterator specification is provided in the handout.

    This function also tests that the empty dictionary is a valid state
    for the iterator.
    """

    game_dict = GameDictionary()
    iterator = game_dict.__iter__()

    with pytest.raises(StopIteration):
        iterator.__next__()


