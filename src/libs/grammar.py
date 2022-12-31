from .rule import Rule
from typing import List


class Grammar:
    def __init__(self, non_terminals: str, letters: str, start_non_terminal: str):
        self.non_terminals: str = non_terminals
        self.letters: str = letters
        self.Start: str = start_non_terminal
        self.rules: List[Rule] = []

    def append_rules(self, addition: List[Rule]) -> None:
        self.rules += addition

    def change_start(self) -> None:
        new_start: str = min(self.non_terminals + self.letters)
        new_start = chr(ord(new_start) - 1)
        self.non_terminals += new_start
        self.rules.append(Rule(new_start, self.Start))
        self.Start = new_start

    def get_rules(self) -> List[Rule]:
        return self.rules

    def get_certain_rules(self, premise: str) -> List[Rule]:
        return [rule for rule in self.rules if rule.premise == premise]

    def get_non_terminals(self) -> str:
        return self.non_terminals

    def get_alphabet(self) -> str:
        return self.letters

    def get_start(self) -> str:
        return self.Start
