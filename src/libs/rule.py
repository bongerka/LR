class Rule:
    def __init__(self, premise: str, result: str):
        self.premise: str = premise
        self.result: str = result

    def __key(self):
        return self.premise, self.result

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Rule):
            return self.__key() == other.__key()
        return NotImplemented

    def __copy__(self):
        return Rule(self.premise, self.result)
