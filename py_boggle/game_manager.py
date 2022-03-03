import copy
import random
import sys
from enum import Enum
from typing import Collection, List, NamedTuple, Optional, Set, Tuple

from py_boggle.boggle_dictionary import BoggleDictionary
from py_boggle.boggle_game import BoggleGame

class GameManager(BoggleGame):
    """Your implementation of `BoggleGame`
    """

    def __init__(self):
        """Constructs an empty Boggle Game.

        A newly-constructed game is unplayable. The `new_game` method
        should be called to initialize a playable game.

        Example
        -------
        ```
        dictionary: BoggleDictionary = ...
        game = GameManager()
        game.new_game(4, 2, "cubes.txt", dictionary)
        ```
        """
        raise NotImplementedError("method __init__") # TODO: implement your code here

    def new_game(
        self, size: int, num_players: int, cubefile: str, dict: BoggleDictionary
    ) -> None:
        raise NotImplementedError("method new_game") # TODO: implement your code here

    def get_board(self) -> List[List[str]]:
        raise NotImplementedError("method get_board") # TODO: implement your code here

    def add_word(self, word: str, player: int) -> int:
        raise NotImplementedError("method add_word") # TODO: implement your code here

    def get_last_added_word(self) -> Optional[List[Tuple[int, int]]]:
        raise NotImplementedError("method get_last_added_word") # TODO: implement your code here

    def set_game(self, board: List[List[str]]) -> None:
        raise NotImplementedError("method set_game") # TODO: implement your code here

    def get_all_words(self) -> Collection[str]:
        """Return a collection containing all valid words in the current
        Boggle board.

        Uses the current search tactic.

        This is a sample implementation provided to make the project easier.
        You can delete this if you don't want to use it.
        """
        if self.tactic == BoggleGame.SearchTactic.SEARCH_BOARD:
            return self.__board_driven_search()
        else:
            return self.__dictionary_driven_search()

    def set_search_tactic(self, tactic: BoggleGame.SearchTactic) -> None:
        """Set the search tactic to the given tactic.

        This tactic is used by `get_all_words()`. Valid tactics are
        defined in BoggleGame.SearchTactic.
        """
        self.tactic = tactic

    def get_scores(self) -> List[int]:
        raise NotImplementedError("method get_scores") # TODO: implement your code here

    def __dictionary_driven_search(self) -> Set[str]:
        """Find all words using a dictionary-driven search.

        The dictionary-driven search attempts to find every word in the
        dictionary on the board.

        Returns:
            A set containing all words found on the board.
        """
        raise NotImplementedError("method __dictionary_driven_search") # TODO: implement your code here

    def __board_driven_search(self) -> Set[str]:
        """Find all words using a board-driven search.

        The board-driven search constructs a string using every path on
        the board and checks whether each string is a valid word in the
        dictionary.

        Returns:
            A set containing all words found on the board.
        """
        raise NotImplementedError("method __board_driven_search") # TODO: implement your code here
