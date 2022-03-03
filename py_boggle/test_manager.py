import copy
import random
import string
from typing import List, Optional, Set, Tuple

import pytest
from py_boggle.boggle_dictionary import BoggleDictionary
from py_boggle.game_dictionary import GameDictionary
from py_boggle.boggle_game import BoggleGame
from py_boggle.game_manager import GameManager


# read words file
CUBE_FILE = "cubes.txt"
WORDS_FILE = "words.txt"
words: Set[str] = set()
with open(WORDS_FILE, "r") as fin:
    for line in fin:
        line = line.strip().upper()
        words.add(line)

# handout
example_board = [
    ["E", "E", "C", "A"],
    ["A", "L", "E", "P"],
    ["H", "N", "B", "O"],
    ["Q", "T", "T", "Y"],
]
example_words = set("""
alec alee anele becap bent benthal blae blah blent bott cape capelan capo celeb cent
cento clan clean elan hale hant lane lean leant leap lent lento neap open pace peace
peel pele penal pent thae than thane toby toecap tope topee
""".upper().strip().split())

def test_set_game():
    """Test that set_game initialized the board correctly.
    """

    game_dict = GameDictionary()
    game_dict.load_dictionary(WORDS_FILE)

    game = GameManager()
    game.new_game(len(example_board), 2, CUBE_FILE, game_dict)
    game.set_game(example_board)

    game_board = game.get_board()

    # check dimensions
    assert len(game_board) == len(example_board)
    for row in range(len(example_board)):
        assert len(game_board[row]) == len(example_board[row])

    # check contents
    for row in range(len(game_board)):
        for col in range(len(game_board)):
            assert game_board[row][col].upper() == example_board[row][col]

def _check_all_words(game: BoggleGame, expected: Set[str]) -> Tuple[bool, str]:
    """Test the words returned by get_all_words against our word set.

    Args:
        game: a game with the appropriate search tactic set

    Returns:
        Tuple[bool, str]
        The bool indicates whether this check passed.
        The str is a comment for an assertion failure
    """
    game_word_set: Set[str] = set()
    for word in game.get_all_words():
        if len(word) < 4:
            return (False, "returns words with length <4")
        game_word_set.add(word.upper())

    if game_word_set == expected:
        return (True, "")
    elif game_word_set < expected:
        # proper subset
        return (False, "fails to find all words")
    else:
        # if `game_word_set` is not a subset of `expected`,
        # then it must contain words that are not in `expected`
        return (False, "finds extraneous words")


def test_board_tactic():
    game_dict = GameDictionary()
    game_dict.load_dictionary(WORDS_FILE)

    game = GameManager()
    game.new_game(len(example_board), 2, CUBE_FILE, game_dict)
    game.set_game(example_board)

    game.set_search_tactic(BoggleGame.SearchTactic.SEARCH_BOARD)

    result = _check_all_words(game, example_words)
    comment = f"Your board search {result[1]} when using our game board"

    assert result[0], comment


def test_dictionary_tactic():
    game_dict = GameDictionary()
    game_dict.load_dictionary(WORDS_FILE)

    game = GameManager()
    game.new_game(len(example_board), 2, CUBE_FILE, game_dict)
    game.set_game(example_board)

    game.set_search_tactic(BoggleGame.SearchTactic.SEARCH_DICT)

    result = _check_all_words(game, example_words)
    comment = f"Your dictionary search {result[1]} when using our game board"

    assert result[0], comment
