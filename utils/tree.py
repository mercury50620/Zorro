import re
from typing import List, Tuple, Union
HASH = re.compile(r"#.*$")


class Tree:
    def __init__(self, pos: str, children: Union[List["Tree"], List[str]]) -> None:
        self.pos, self.feature = Tree.from_pos_string(pos)
        self.children = children
        assert len(self.children) > 0, "children must contain some Tree|str"

    @staticmethod
    def from_pos_string(
        txt: str,
    ) -> Union[Tuple[str], List[str]]:  # remove indices like (NP-SBJ-1 -> NP-SBJ)
        if "#" in txt:
            txt = HASH.sub("", txt)
        if "-" in txt:
            if txt.count("-") == 1:
                return txt.split("-")
            else:
                if txt[0] == ('-'):  # -NONE- -> -NONE-
                    return txt, ""
                else:  # some POSs have more than three '-': ADVP-PRD-TPC-2, ADVP-LOC-PRD-TPC-1,  NP-TTL-SBJ-1,...
                    pos, feature = txt.split("-", 1)
                    return pos, feature.split("-", 1)[0]
        else:
            return txt, ""

    def __len__(self) -> int:
        return len(self.leaves)

    @property
    def leaves(self) -> List["Tree"]:
        def rec(node: Tree) -> None:
            if node.is_terminal:
                result.append(node)
            else:
                for child in node.children:
                    rec(child)

        result: List["Tree"] = []
        rec(self)
        return result

    @property
    def token(self) -> str:
        assert self.is_terminal, "Tree.token must be called on terminal objects"
        token = self.children[0]
        return token

    @property
    def tokens(self) -> List[str]:
        result: List[str] = []
        for leaf in self.leaves:
            result.append(leaf.token)
        return result

    @property
    def is_terminal(self) -> bool:
        assert self.children != [], f"An empty list is detected: pos = {self.pos}"
        return isinstance(self.children[0], str)

    @property
    def is_unary(self) -> bool:
        return isinstance(self.children[0], Tree) and len(self.children) == 1

    def draw(self) -> str:
        def _rec(node: Tree) -> str:
            if node.is_terminal:
                token = node.token
                if node.feature == "":
                    pos = node.pos
                else:
                    pos = f'{node.pos}-{node.feature}'
                return f"({pos} {token})"
            else:
                if node.feature == "":
                    pos = node.pos
                else:
                    pos = f'{node.pos}-{node.feature}'
                children = " ".join(_rec(child) for child in node.children)
            return f"({pos} {children})"

        return f"{_rec(self)}"

    def draw_forest(self) -> str:
        REGEX = re.compile(r"[_$%]")

        def _rec(node: Tree) -> str:
            if node.is_terminal:
                token = node.token
                token = REGEX.sub(lambda match: "\\" + match.group(0), token)
                if token in {".", ","}:
                    token = f"{{{token}}}"
                return f"[{token}]"
            else:
                children = " ".join(_rec(child) for child in node.children)
                return f"[{children}]"

        return "\\begin{forest} " + f"{_rec(self)}" + " \\end{forest}\\\\"

    def draw_terminal(self) -> str:
        result: List[str] = []
        for leaf in self.leaves:
            result.append(leaf.token)
        return " ".join(result)