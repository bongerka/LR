from typing import Set, Dict
from rule import Rule


class Situation:
    def __init__(self, rule: Rule = Rule(), point: int = 0, _next: str = ''):
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
        return not (self.compare_situations(other) or other.compare_situation(self))

    def __key(self):
        return self.rule, self.point, self.next

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Situation):
            return self.__key() == other.__key()
        return NotImplemented


class Instruction:
    def __init__(self, is_reduce: bool, reduce_rule: Rule = Rule(), dest_node: int = 0):
        self.is_reduce: bool = is_reduce
        self.reduce_rule: Rule = reduce_rule
        self.dest_node: int = dest_node

    @classmethod
    def from_rule(cls, rule: Rule):
        return cls(is_reduce=True, reduce_rule=rule)

    @classmethod
    def from_node(cls, node: int):
        return cls(is_reduce=False, dest_node=node)

    def isReduce(self) -> bool:
        return self.is_reduce

    def isShift(self) -> bool:
        return not self.is_reduce

    def getRule(self) -> Rule:
        return self.reduce_rule

    def getNode(self) -> int:
        return self.dest_node


class Node:
    def __init__(self):
        self.situations: Set[Situation] = set()
        self.instructions: Dict[str, Instruction] = dict()
