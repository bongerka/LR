from .grammar import Grammar
from .node import Node, Situation, Instruction
from .rule import Rule

from copy import deepcopy
from typing import List, Dict, Set, Optional
from collections import deque


class LR:
    END: str = '$'

    def __init__(self):
        self._grammar: Optional[Grammar] = None
        self._new_start: str = ""
        self._prev_start: str = ""
        self._nodes: List[Node] = list()
        self._FIRST: Dict[str, Set[str]] = dict()
        self._epsilon_creators: Set[str] = set()

    def process(self, word: str) -> bool:
        node: int = 0
        node_stack: List[int] = [node]
        process_word: str = (word + self.END)[::-1]
        while process_word:
            if self._nodes[node].instructions.get(process_word[-1]) is None:
                break

            instruction: Instruction = self._nodes[node].instructions.get(process_word[-1])
            if instruction.is_accept():
                return True

            if instruction.is_shift() or instruction.is_goto():
                node = instruction.get_node()
                node_stack.append(node)
                process_word = process_word[:-1]

            elif instruction.is_reduce():
                if len(node_stack) + 1 < len(instruction.get_rule().result):
                    return False

                for i in range(len(instruction.get_rule().result)):
                    node_stack.pop()
                process_word += instruction.get_rule().premise
                node = node_stack[-1]

        return False

    def fit(self, source_grammar: Grammar) -> None:
        self._nodes.clear()
        self._FIRST.clear()
        self._epsilon_creators.clear()
        
        self._grammar = source_grammar
        self._prev_start = self._grammar.get_start()
        self._grammar.change_start()
        self._new_start = self._grammar.get_start()
        self.__count_epsilon_creators()
        self.ACCEPT: Situation = Situation(Rule(self._new_start, self._prev_start), 1, self.END)
        for NonTerm in self._grammar.get_non_terminals():
            self._FIRST[NonTerm]: Set[str] = set()
            self.__countFirst(NonTerm, NonTerm, set())
        self.__build_automation()

    def __build_automation(self) -> None:
        self._nodes.append(Node())
        self._nodes[0].situations.add(Situation(Rule(self._new_start, self._prev_start), 0, self.END))
        self.__make_closure(0)

        process_queue = deque([0])
        while process_queue:
            for i in self.__process_node(process_queue[0]):
                process_queue.append(i)
            process_queue.popleft()

    def __process_node(self, vertex: int) -> List[int]:
        new_nodes: List[int] = []
        accept_next: Optional[str] = None
        reduces: Dict[str, Rule] = {}
        moves: Dict[str, Set[Situation]] = {}
        for situation in deepcopy(self._nodes[vertex].situations):
            if situation.point == len(situation.rule.result):
                if reduces.get(situation.next) is not None:
                    raise BaseException("reduce-reduce conflict")
                if situation == self.ACCEPT:
                    accept_next = self.END
                reduces[situation.next] = situation.rule
            else:
                next_symbol: str = situation.rule.result[situation.point]
                situation.point += 1
                moves.setdefault(next_symbol, set()).add(situation)

        shifts: Dict[str, int] = {}
        goto: Dict[str, int] = {}
        for key, value in moves.items():
            self._nodes.append(Node())
            self._nodes[-1].situations = value

            self.__make_closure(len(self._nodes) - 1)
            _id: int = len(self._nodes) - 1
            for i in range(_id):
                if self._nodes[-1].situations == self._nodes[i].situations:
                    _id = i
                    break
            if _id == len(self._nodes) - 1:
                new_nodes.append(len(self._nodes) - 1)
            else:
                self._nodes.pop()

            if key in self._grammar.get_alphabet():
                shifts[key] = _id
            else:
                goto[key] = _id

        for symbol in self._grammar.get_alphabet() + self.END:
            if reduces.get(symbol) is not None and shifts.get(symbol) is not None:
                raise KeyError("conflict")
            if reduces.get(symbol) is not None:
                self._nodes[vertex].instructions[symbol] = Instruction.from_reduce(reduces[symbol])
            if shifts.get(symbol) is not None:
                self._nodes[vertex].instructions[symbol] = Instruction.from_shift(shifts[symbol])
            if symbol == accept_next:
                self._nodes[vertex].instructions[symbol].accept = True

        for symbol in self._grammar.get_non_terminals():
            if goto.get(symbol) is not None:
                self._nodes[vertex].instructions[symbol] = Instruction.from_goto(goto[symbol])

        return new_nodes

    def __make_closure(self, _id: int) -> None:
        new_set = set()
        while new_set != self._nodes[_id].situations:
            new_set = deepcopy(self._nodes[_id].situations)
            for situation in new_set:
                point: int = situation.point
                if point == len(situation.rule.result):
                    continue
                next_symbol: str = situation.rule.result[situation.point]
                next_symbols: Set[str] = self.getFirst(
                    situation.rule.result[point + 1:] + ('' if situation.next == self.END else situation.next)
                )
                for rule in deepcopy(self._grammar.get_certain_rules(next_symbol)):
                    for _next in sorted(deepcopy(next_symbols)):
                        self._nodes[_id].situations.add(Situation(rule=rule, point=0, _next=_next))

    def __count_epsilon_creators(self) -> None:
        changed: bool = True
        while changed:
            size: int = len(self._epsilon_creators)
            for rule in self._grammar.get_rules():
                epsilon_maker: bool = True
                for symbol in rule.result:
                    if symbol not in self._epsilon_creators:
                        epsilon_maker = False
                        break
                if epsilon_maker:
                    self._epsilon_creators.add(rule.premise)
            changed = (size != len(self._epsilon_creators))

    def __countFirst(self, current: str, target: str, processed: Set[str]) -> None:
        processed.add(current)
        for rule in self._grammar.get_certain_rules(current):
            if rule.result == "":
                self._FIRST[target].add("")
            for symbol in rule.result:
                if symbol in self._grammar.get_alphabet():
                    self._FIRST[target].add(symbol)
                    break
                if symbol not in processed:
                    self.__countFirst(symbol, target, processed)
                if symbol not in self._epsilon_creators:
                    break

    def sets_sum(self, set1: Set[str], set2: Set[str]):
        ret: Set[str] = set()
        for word1 in set1:
            for word2 in set2:
                ret.add((word1 + word2)[:1])
        return ret

    def getFirst(self, expression) -> Set[str]:
        ret = {""}
        for X in expression:
            ret = self.sets_sum(ret, self._FIRST.get(X) if X in self._grammar.get_non_terminals() else {X})

        if "" in ret:
            ret.discard("")
            ret = ret.union(self.END)

        return ret

    def get_epsilon_creators(self) -> Set[str]:
        return self._epsilon_creators
