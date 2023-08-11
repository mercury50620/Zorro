import re
from typing import List
from nltk import Tree

class PTBReader:
    def __init__(self, line: str) -> None:
        self.line = line
        self.index = 0
        self.tokens = []
    def _next(self, target: str) -> str:
        start = self.index
        end = self.line.find(target, self.index)
        result = self.line[start:end]
        self.index = end + 1
        return result

    def _is_current_idx(self, text: str) -> None:
        if self.line[self.index] != text:
            raise RuntimeError("the position of 'index' is not correct")

    def peek_current_index_str(self) -> str:
        return self.line[self.index]
    
    def parse(self) -> Tree:
        return self._next_node()

    @property
    def _next_node(self):
        end = self.line.find(' ', self.index)
        if self.line[end + 1] == '(':
            return self.parse_tree
        else:
            return self.parse_terminal

    def parse_terminal(self) -> Tree:
        self._is_current_idx('(')
        pos = self._next(' ')[1:]
        token = self._next(')')
        self.tokens.append(token)
        return Tree(pos, [token])

    def parse_tree(self) -> Tree:
        self._is_current_idx('(')
        pos = self._next(' ')[1:]
        self._is_current_idx('(')

        children = []
        while self.peek_current_index_str() != ')':
            children.append(self._next_node())
            if self.peek_current_index_str() == ' ':
                self._next(' ')

        self._next(')')

        return Tree(pos, children)


def ptb_reader(filepath: str) -> List[Tree]:
    with open(filepath, 'r', encoding="utf-8", errors='ignore') as f:
        lines = f.read()
        trees = []
        for line in split_sentences(lines):
            trees.append(PTBReader(line).parse())
        return trees


SPACE = re.compile(r"\s+")
FIRST_PAREN = re.compile(r"\(\s*\(")
# END_PAREN = re.compile(r"\).*$")


def split_sentences(string: str) -> List[str]:
    string = SPACE.sub(' ', string)
    sentences = FIRST_PAREN.split(string)
    if sentences[0] == " ":
        sentences = sentences[1:]
    sentences = ["(" + sentence[:-2] for sentence in sentences]
    # sentences = [END_PAREN.sub('', sentence) for sentence in sentences]
    return sentences