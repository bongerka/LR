from .grammar import Grammar
from .node import Node, Situation, Instruction
from .rule import Rule

from typing import List, Dict, Set, Optional
from copy import deepcopy
from collections import deque


class LR:
    def __init__(self):
        self.grammar: Optional[Grammar] = None
        self.new_start: str = ''
        self.prev_start: str = ''
        self.END: str = '$'
        self.nodes: List[Node] = list()
        self.FIRST: Dict[str, Set[str]] = dict()
        self.epsilon_creators: Set[str] = set()

    def fit(self, source_grammar: Grammar) -> None:
        self.grammar = source_grammar
        self.prev_start = self.grammar.get_start()
        self.grammar.change_start()
        self.new_start = self.grammar.get_start()
        self.count_epsilon_creators()
        for NonTerm in self.grammar.get_non_terminals():
            self.FIRST[NonTerm]: Set[str] = set()
            self.countFirst(NonTerm, NonTerm, set())
        self.build_automation()

    def build_automation(self) -> None:
        self.nodes.append(Node())
        self.nodes[0].situations.add(Situation(Rule(self.new_start, self.prev_start), 0, self.END))
        process_queue = deque()
        process_queue.append(0)
        self.make_closure(0)
        while process_queue:
            for i in self.process_node(process_queue[0]):
                process_queue.append(i)
            process_queue.popleft()

    def process_node(self, vertex: int) -> List[int]:
        new_nodes: List[int] = []
        reduces: Dict[str, Rule] = {}
        moves: Dict[str, List[Situation]] = {}
        for situation in deepcopy(self.nodes[vertex].situations):
            if situation.point == len(situation.rule.result):
                if reduces.get(situation.next) is not None:
                    raise BaseException("reduce conflict")
                reduces[situation.next] = situation.rule
            else:
                next_symbol: str = situation.rule.result[situation.point]
                if moves.get(next_symbol) is None:
                    moves[next_symbol] = []
                moves[next_symbol].append(situation)
                moves[next_symbol][-1].point += 1

        shifts: Dict[str, int] = {}
        for key, value in moves.items():
            self.nodes.append(Node())
            for situation in value:
                self.nodes[-1].situations.add(situation)
            self.make_closure(len(self.nodes) - 1)
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

        for symbol in self.grammar.get_alphabet() + self.grammar.get_non_terminals() + self.END:
            if reduces.get(symbol) is not None and shifts.get(symbol) is not None:
                raise "shift conflict"
            if reduces.get(symbol) is not None:
                self.nodes[vertex].instructions[symbol] = Instruction.from_rule(reduces[symbol])
            if shifts.get(symbol) is not None:
                self.nodes[vertex].instructions[symbol] = Instruction.from_node(shifts[symbol])
        return new_nodes

    '''def make_closure(self, _id: int) -> None:
        changed: bool = True
        print("closure", len(self.nodes[_id].situations), _id)
        while changed:
            size: int = len(self.nodes[_id].situations)
            new_set = {}
            while new_set != self.nodes[_id].situations:
                new_set = self.nodes[_id].situations.copy()
                for situation in new_set:
                    length: int = len(situation.rule.result)
                    point: int = situation.point
                    if point == length:
                        continue
                    next_symbol: str = situation.rule.result[situation.point]
                    next_symbols: Set[str] = self.getFirst(situation.rule.result[point+1:length] + ('' if situation.next == self.END else situation.next))
                    for rule in self.grammar.get_certain_rules(next_symbol):
                        for _next in next_symbols:
                            self.nodes[_id].situations.add(Situation(rule=rule, point=0, _next=_next))
            changed = (size != len(self.nodes[_id].situations))'''

    def make_closure(self, _id: int) -> None:
        changed: bool = True
        while changed:
            size: int = len(self.nodes[_id].situations)
            for situation in self.nodes[_id].situations.copy():
                length: int = len(situation.rule.result)
                point: int = situation.point
                if point == length:
                    continue
                next_symbol: str = situation.rule.result[situation.point]
                next_symbols: Set[str] = self.getFirst(situation.rule.result[point+1:length] +
                                                       ('' if situation.next == self.END else situation.next))
                for rule in self.grammar.get_certain_rules(next_symbol):
                    for _next in next_symbols:
                        self.nodes[_id].situations.add(Situation(rule=rule, point=0, _next=_next))
            changed = (size != len(self.nodes[_id].situations))

    def count_epsilon_creators(self) -> None:
        changed: bool = True
        while changed:
            size: int = len(self.epsilon_creators)
            for rule in self.grammar.get_rules():
                epsilon_maker: bool = True
                for symbol in rule.result:
                    if symbol not in self.epsilon_creators:
                        epsilon_maker = False
                        break
                if epsilon_maker:
                    self.epsilon_creators.add(rule.premise)
            changed = (size != len(self.epsilon_creators))

    def countFirst(self, current: str, target: str, processed: Set[str]) -> None:
        processed.add(current)
        for rule in self.grammar.get_certain_rules(current):
            if len(rule.result) == 0:
                continue
            for symbol in rule.result:
                if symbol in self.grammar.get_alphabet():
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
            if self.nodes[node].instructions.get(process_word[-1]) is None:
                if process_word[-1] == self.new_start:
                    break
                return False

            instruction: Instruction = self.nodes[node].instructions.get(process_word[-1])
            if instruction.is_shift():
                node = instruction.get_node()
                node_stack.append(node)
                process_word = process_word[:-1]
            else:
                if len(node_stack) + 1 < len(instruction.get_rule().result):
                    return False

                for i in range(len(instruction.get_rule().result)):
                    node_stack.pop()
                process_word += instruction.get_rule().premise
                node = node_stack[-1]

        return len(node_stack) == 1 and node_stack[-1] == 0 and len(process_word) == 2

    def get_epsilon_creators(self) -> Set[str]:
        return self.epsilon_creators

    def getFirst(self, expression: str):
        ret: Set[str] = {self.END}
        for symbol in expression:
            if symbol not in self.epsilon_creators:
                ret.discard(self.END)
                break
        if len(expression) == 0:
            return ret
        if expression[0] in self.grammar.get_alphabet():
            ret.add(expression[0])
            return ret
        if self.FIRST.get(expression[0]) is None:
            return ret
        ans: Set[str] = self.FIRST[expression[0]]
        ans.union(ret)
        return ans
