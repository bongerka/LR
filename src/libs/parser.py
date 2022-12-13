from typing import List, Dict, Set
from grammar import Grammar
from node import Node, Situation, Instruction
from rule import Rule
from collections import deque


class LR:
    def __init__(self):
        self.grammar: Grammar = Grammar()
        self.new_start: str = ''
        self.prev_start: str = ''
        self.END: str = '$'
        self.nodes: List[Node] = list()
        self.FIRST: Dict[str, Set[str]] = dict()
        self.epsilon_creators: Set[str] = set()

    def fit(self, sourceGrammar: Grammar) -> None:
        self.grammar = sourceGrammar
        self.prev_start = self.grammar.getStart()
        self.grammar.changeStart()
        self.new_start = self.grammar.getStart()
        self.countEpsilonCreators()
        for NonTerm in self.grammar.getNonTerminals():
            self.FIRST[NonTerm] = set()
            self.countFirst(NonTerm, NonTerm, set())
        self.buildAutomation()

    def buildAutomation(self) -> None:
        self.nodes.append(Node())
        self.nodes[0].situations.add(Situation(Rule(self.new_start, self.prev_start), 0, self.END))
        process_queue = deque()
        process_queue.append(0)
        self.makeClosure(0)
        while process_queue:
            for i in self.processNode(process_queue[-1]):
                process_queue.append(i)
            process_queue.pop()

    def processNode(self, vertex: int) -> List[int]:
        new_nodes: List[int] = []
        reduces: Dict[str, Rule] = {}
        moves: Dict[str, List[Situation]] = {}
        for situation in self.nodes[vertex].situations:
            if situation.point == len(situation.rule.result):
                if reduces.get(situation.next):
                    print(1)
                    #raise "reduce conflict"
                reduces[situation.next] = situation.rule
            else:
                next_symbol: str = situation.rule.result[situation.point]
                if not moves.get(next_symbol):
                    moves[next_symbol] = []
                moves[next_symbol].append(situation)
                moves[next_symbol][-1].point += 1

        shifts: Dict[str, int] = {}
        for key, value in moves.items():
            self.nodes.append(Node())
            for situation in value:
                self.nodes[-1].situations.add(situation)
            self.makeClosure(len(self.nodes) - 1)
            _id: int = len(self.nodes) - 1
            for i in range(len(self.nodes) - 1):
                if self.nodes[-1].situations == self.nodes[i].situations:
                    _id = i
                    break
            if _id == len(self.nodes) - 1:
                new_nodes.append(len(self.nodes) - 1)
            else:
                self.nodes.pop()
            shifts[key] = _id

        for symbol in self.grammar.getAlphabet() + self.grammar.getNonTerminals() + self.END:
            if reduces.get(symbol) and shifts.get(symbol):
                raise "shift conflict"
            if reduces.get(symbol):
                self.nodes[vertex].instructions[symbol] = Instruction.from_rule(reduces[symbol])
            if shifts.get(symbol):
                self.nodes[vertex].instructions[symbol] = Instruction.from_node(shifts[symbol])

        return new_nodes

    def makeClosure(self, _id: int) -> None:
        changed: bool = True
        while changed:
            size: int = len(self.nodes[_id].situations)
            for situation in self.nodes[_id].situations.copy():
                length: int = len(situation.rule.result)
                point: int = situation.point
                if point == length:
                    continue
                next_symbol: str = situation.rule.result[situation.point]
                next_symbols: Set[str] = self.getFirst(situation.rule.result[point+1:length] + ('' if situation.next == self.END else situation.next))
                for rule in self.grammar.getCertainRules(next_symbol):
                    for _next in next_symbols:
                        self.nodes[_id].situations.add(Situation(rule=rule, point=0, _next=_next))

            changed = size != len(self.nodes[_id].situations)

    def countEpsilonCreators(self) -> None:
        changed: bool = True
        while changed:
            size: int = len(self.epsilon_creators)
            for rule in self.grammar.getRules():
                epsilon_maker: bool = True
                for symbol in rule.result:
                    if symbol in self.epsilon_creators:
                        epsilon_maker = False
                        break
                if epsilon_maker:
                    self.epsilon_creators.add(rule.premise)
            changed = size != len(self.epsilon_creators)

    def countFirst(self, current: str, target: str, processed: Set[str]) -> None:
        processed.add(current)
        for rule in self.grammar.getCertainRules(current):
            if not len(rule.result):
                continue
            for symbol in rule.result:
                if symbol in self.grammar.getAlphabet():
                    self.FIRST[target].add(symbol)
                    break
                if symbol not in processed:
                    self.countFirst(symbol, target, processed)
                if symbol not in self.epsilon_creators:
                    break

    def process(self, word: str) -> bool:
        node: int = 0
        node_stack: List[int] = [node]
        process_word: str = (word + self.END)[::-1]
        while process_word:
            if not self.nodes[node].instructions.get(process_word[-1]):
                if process_word[-1] == self.new_start:
                    break
                return False

            instruction: Instruction = self.nodes[node].instructions.get(process_word[-1])
            if instruction.isShift():
                node = instruction.getNode()
                node_stack.append(node)
                process_word = process_word[:-1]
            else:
                if len(node_stack) + 1 < len(instruction.getRule().result):
                    return False

                for i in range(len(instruction.getRule().result)):
                    node_stack.pop()
                process_word += instruction.getRule().premise
                node = node_stack[-1]

        return len(node_stack) == 1 and node_stack[-1] == 0 and len(process_word) == 2

    def getEpsilonCreators(self) -> Set[str]:
        return self.epsilon_creators

    def getFirst(self, expression: str):
        ret: Set[str] = {self.END}
        for symbol in expression:
            if symbol not in self.epsilon_creators:
                ret.discard(self.END)
                break

        if not expression:
            return ret
        if expression[0] in self.grammar.getAlphabet():
            ret.add(expression[0])
            return ret
        if not self.FIRST.get(expression[0]):
            return ret
        concl: Set[str] = self.FIRST[expression[0]]
        concl.union(ret)
        return concl


g = Grammar("SC", "cd", 'S')
rules = [Rule('S', "CC"), Rule('C', "cC"), Rule('C', "d")]
g.appendRules(rules)
algo = LR()
algo.fit(g)

print(algo.getEpsilonCreators())
