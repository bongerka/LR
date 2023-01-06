from typing import Set, Dict, Optional
from .rule import Rule


class Situation:
    def __init__(self, rule: Rule, point: int, _next: str):
        self.rule: Rule = rule
        self.point: int = point
        self.next: str = _next

    def __key(self):
        return self.rule, self.point, self.next

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Situation):
            return self.__key() == other.__key()
        return NotImplemented

    def __copy__(self):
        return Situation(self.rule.__copy__(), self.point, self.next)


class Instruction:
    def __init__(self, reduce_rule: Optional[Rule] = None, dest_node: Optional[int] = None, goto: Optional[int] = None):
        self.reduce_rule: Optional[Rule] = reduce_rule
        self.goto: Optional[int] = goto
        self.dest_node: Optional[int] = dest_node

    @classmethod
    def from_reduce(cls, rule: Rule):
        return cls(reduce_rule=rule)

    @classmethod
    def from_shift(cls, node: int):
        return cls(dest_node=node)

    @classmethod
    def from_goto(cls, node: int):
        return cls(goto=node)

    def is_reduce(self) -> bool:
        return self.reduce_rule is not None

    def is_shift(self) -> bool:
        return self.dest_node is not None

    def is_goto(self) -> bool:
        return self.goto is not None

    def get_rule(self) -> Rule:
        return self.reduce_rule

    def get_node(self) -> int:
        if self.dest_node is not None:
            return self.dest_node
        return self.goto


class Node:
    def __init__(self):
        self.situations: Set[Situation] = set()
        self.instructions: Dict[str, Instruction] = dict()
