import typing
from collections.abc import Iterator

from py_boggle.boggle_dictionary import BoggleDictionary


class GameDictionary(BoggleDictionary):
    """
    Your implementation of BoggleDictionary.
    """

    def __init__(self):
        WORDS_FILE = "words.txt"
        self.game_dict = {}
        self.words = set()
        with open(WORDS_FILE) as fin:
            for line in fin:
                line = line.strip().upper()
                self.words.add(line)
        # raise NotImplementedError("method __init__") # TODO: implement your code here

    def load_dictionary(self, filename: str) -> None:
        
        with open(filename) as wordfile:
            for line in wordfile:
                word = line.strip().upper()
                if len(word) > 0:
                    self.game_dict[word] = len(word)
                    
        # raise NotImplementedError("method load_dictionary") # TODO: implement your code here

    def is_prefix(self, prefix: str) -> bool:
        raise NotImplementedError("method is_prefix") # TODO: implement your code here

    def contains(self, word: str) -> bool:
        # return word in self.words
        for word in self.words:
            if word in self.game_dict:
                return True
            else:
                return False
        # raise NotImplementedError("method contains") # TODO: implement your code here

    def __iter__(self) -> typing.Iterator[str]:
        raise NotImplementedError("method __iter__") # TODO: implement your code here
