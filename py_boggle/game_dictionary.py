from cgitb import reset
import typing
from collections.abc import Iterator

from py_boggle.boggle_dictionary import BoggleDictionary

class TrieNode:

    def __init__(self, char):
        self.char = char
        self.nodes = {}
        self.leaf = False


class Trie:
    
    def __init__(self):
        self.root = TrieNode("")
        
    def insert_word(self, word):
        node = self.root
        
        for letter in word:
            if letter not in node.nodes:
                node.nodes[letter] = TrieNode(letter)

            node = node.nodes[letter]
        
        node.leaf = True
        
    def check_prefix(self, prefix):
        
        node = self.root
        
        for letter in prefix:
            if letter in node.nodes:
                node = node.nodes[letter]
            else:
                return False
            
        return True
    
    def check_word(self, word):
        
        node = self.root
        
        word = word.lower()
    
        for letter in word:
            if letter not in node.nodes:
                return False
            node = node.nodes[letter]
        return True

class GameDictionary(BoggleDictionary):
    """
    Your implementation of BoggleDictionary.
    """

    def __init__(self):
        

        self.l = []        
        self.game_dict = {}
        self.t = Trie() # use this
        

            
        # raise NotImplementedError("method __init__") # TODO: implement your code here

    def load_dictionary(self, filename: str) -> None:
        
        # with open(filename) as wordfile:
        #     for line in wordfile:
        #         word = line.strip().upper()
        #         if len(word) > 0:
        #             self.game_dict[word] = len(word)
        # return self.t
        # WORDS_FILE = "words.txt"
        with open(filename) as file:
            for line in file:
                word = line.strip().lower()
                self.t.insert_word(word)
                self.l.append(word)
                
                # self.words.add(line)
                    
        # raise NotImplementedError("method load_dictionary") # TODO: implement your code here

    def is_prefix(self, prefix: str) -> bool:
        
        cur_dict = self.t
          
        result = cur_dict.check_prefix(prefix)
        
        return result
        # raise NotImplementedError("method is_prefix") # TODO: implement your code here

    def contains(self, word: str) -> bool:
        cur_dict = self.t
        
        result = cur_dict.check_word(word) 
               
        return result         
  
        # raise NotImplementedError("method contains") # TODO: implement your code here

    # class MyIterator:
    #     def __init__(self, my_dict):
            
    #         self.my_trie = my_dict
                
    #     def __iter__(self):
    #         pass
        
    #     def __next__(self):
    #         if True:
    #             pass
    #         else:
    #             raise StopIteration
            
    
    def __iter__(self) -> typing.Iterator[str]:
        return self.l.__iter__()
        # raise NotImplementedError("method __iter__") # TODO: implement your code here


# class MyIterator:
#     def __init__(self, my_dict):
#         self.my_trie = my_dict
            
#     def __iter__(self):
#         pass
    
#     def __next__(self):
#         if True:
#             pass
#         else:
#             raise StopIteration
        