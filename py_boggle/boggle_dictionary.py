"""
This module contains the definition of an abstract dictionary class.

Your concrete implementation should inherit from the abstract class.

Example
-------
```
# in file `py_boggle/game_dictionary.py`:

from py_boggle.boggle_dictionary import BoggleDictionary

class GameDictionary(BoggleDictionary):
    ...
```
"""

import typing
from abc import ABC, abstractmethod
from collections.abc import Iterable


class BoggleDictionary(ABC, Iterable):
    """
    This abstract class defines the basic operations of a dictionary
    (collection of words) for use with a game.
    """

    @abstractmethod
    def load_dictionary(self, filename: str) -> None:
        """Load words from a file to this dictionary.

        This file should contain one word per line, with the words in
        ascending lexicographic order.

        Args:
            filename: The name or path to the dictionary file.

        Raises:
            OSError: The file cannot be opened or read.

        Note:
            This is not the constructor for the class. Instead, it
            sets the words in the dictionary to the words in the file.
            Your `GameDictionary` constructor must not take any
            parameters.

        Example
        -------
        ```
        dictionary: BoggleDictionary = GameDictionary()
        dictionary.load_dictionary("words.txt")
        ```
        """
        raise NotImplementedError("abstract method `load_dictionary`")

    @abstractmethod
    def is_prefix(self, prefix: str) -> bool:
        """Test whether a string is the prefix of some word in this
        dictionary.

        This method should be case-insensitive.

        Args:
            prefix: The string to test.

        Returns:
            True if the string is a prefix of some word in this
            dictionary, False otherwise.

        Example
        -------
        ```
        assert dictionary.is_prefix("a") == dictionary.is_prefix("A")
        ```
        """
        raise NotImplementedError("abstract method `is_prefix`")

    @abstractmethod
    def contains(self, word: str) -> bool:
        """Test whether a string is a word in this dictionary.

        This method should be case-insensitive.

        Args:
            word: The string to test.

        Returns:
            True if the string is a word in this dictionary,
            False otherwise.

        Example
        -------
        ```
        assert dictionary.contains("a") == dictionary.contains("A")
        ```
        """
        raise NotImplementedError("abstract method `contains`")

    @abstractmethod
    def __iter__(self) -> typing.Iterator[str]:
        """Return a new iterator object over this dictionary.

        Words returned by the iterator do not need to be in any
        particular order.

        Iterator objects returned by this method should have
        independent states. Multiple iterators iterating over
        the dictionary at the same time should not interfere
        with one another.

        When an iterator has been exhausted, the iterator's
        `__next__()` method **MUST** raise `StopIteration`.

        Documentation:
            https://docs.python.org/3/glossary.html#term-iterable
            https://docs.python.org/3/glossary.html#term-iterator
            https://docs.python.org/3/library/stdtypes.html#typeiter

        Additional Resources:
            https://wiki.python.org/moin/Iterator
            https://www.programiz.com/python-programming/iterator
        """
        raise NotImplementedError("abstract method `__iter__`")
