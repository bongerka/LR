from typing import List
from rule import Rule


class Grammar:
    def __init__(self, non_terminals: str = '', letters: str = '', StartNonTerminal: str = ''):
        self.non_terminals: str = non_terminals
        self.letters: str = letters
        self.Start: str = StartNonTerminal
        self.rules: List[Rule] = []

    def appendRules(self, addition: List[Rule]) -> None:
        self.rules += addition

    def changeStart(self) -> None:
        new_start: str = min(self.non_terminals + self.letters)
        new_start = chr(ord(new_start) - 1)
        self.non_terminals += new_start
        self.rules.append(Rule(new_start, self.Start))
        self.Start = new_start

    def getRules(self) -> List[Rule]:
        return self.rules

    def getCertainRules(self, premise: str) -> List[Rule]:
        ret: List[Rule] = []
        for rule in self.rules:
            if rule.premise == premise:
                ret.append(rule)

        return ret

    def getNonTerminals(self) -> str:
        return self.non_terminals

    def getAlphabet(self) -> str:
        return self.letters

    def getStart(self) -> str:
        return self.Start
