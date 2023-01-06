from .rule import Rule
from typing import List


class Grammar:
    def __init__(self, non_terminals: str, letters: str, start: str):
        self._non_terminals: str = non_terminals
        self._letters: str = letters
        self._start: str = start
        self._rules: List[Rule] = []

    def append_rules(self, addition: List[Rule]) -> None:
        self._rules += addition

    def change_start(self) -> None:
        new_start: str = min(self._non_terminals + self._letters)
        new_start = chr(ord(new_start) - 1)
        self._non_terminals += new_start
        self._rules.append(Rule(new_start, self._start))
        self._start = new_start

    def get_rules(self) -> List[Rule]:
        return self._rules.copy()

    def get_certain_rules(self, premise: str) -> List[Rule]:
        return [rule for rule in self._rules if rule.premise == premise]

    def get_non_terminals(self) -> str:
        return self._non_terminals

    def get_alphabet(self) -> str:
        return self._letters

    def get_start(self) -> str:
        return self._start
