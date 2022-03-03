import typing
from collections.abc import Iterator

from py_boggle.boggle_dictionary import BoggleDictionary


class GameDictionary(BoggleDictionary):
    """
    Your implementation of BoggleDictionary.
    """

    def __init__(self):
        raise NotImplementedError("method __init__") # TODO: implement your code here

    def load_dictionary(self, filename: str) -> None:
        raise NotImplementedError("method load_dictionary") # TODO: implement your code here

    def is_prefix(self, prefix: str) -> bool:
        raise NotImplementedError("method is_prefix") # TODO: implement your code here

    def contains(self, word: str) -> bool:
        raise NotImplementedError("method contains") # TODO: implement your code here

    def __iter__(self) -> typing.Iterator[str]:
        raise NotImplementedError("method __iter__") # TODO: implement your code here
