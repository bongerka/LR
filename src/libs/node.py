from typing import Set, Dict, Optional
from .rule import Rule


class Situation:
    def __init__(self, rule: Rule, point: int, _next: str):
        self.rule: Rule = rule
        self.point: int = point
        self.next: str = _next

    def compare_situations(self, other) -> bool:
        if self.next != other.next:
            return self.next < other.next
        if self.point != other.point:
            return self.point < other.point
        if self.rule.premise != other.rule.premise:
            return self.rule.premise < other.rule.premise
        return self.rule.result < other.rule.result

    def equal(self, other) -> bool:
        return not (self.compare_situations(other) or other.compare_situations(self))

    def __key(self):
        return self.rule, self.point, self.next

    def __lt__(self, other):
        return self.compare_situations(other)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Situation):
            return self.__key() == other.__key()
        return NotImplemented

    def __copy__(self):
        return Situation(self.rule.__copy__(), self.point, self.next)


class Instruction:
    def __init__(self, is_reduce: bool, reduce_rule: Optional[Rule] = None, dest_node: Optional[int] = None):
        self.is_reduce: bool = is_reduce
        self.reduce_rule: Optional[Rule] = reduce_rule
        self.dest_node: Optional[int] = dest_node

    @classmethod
    def from_rule(cls, rule: Rule):
        return cls(is_reduce=True, reduce_rule=rule)

    @classmethod
    def from_node(cls, node: int):
        return cls(is_reduce=False, dest_node=node)

    def is_reduce(self) -> bool:
        return self.is_reduce

    def is_shift(self) -> bool:
        return not self.is_reduce

    def get_rule(self) -> Rule:
        return self.reduce_rule

    def get_node(self) -> int:
        return self.dest_node


class Node:
    def __init__(self):
        self.situations: Set[Situation] = set()
        self.instructions: Dict[str, Instruction] = dict()
