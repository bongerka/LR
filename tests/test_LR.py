import pytest

from src.libs.parser import LR
from src.libs.grammar import Grammar
from src.libs.rule import Rule


def test_grammar():
    g = Grammar("SABC", "abc", 'S')
    assert g.get_non_terminals() == "SABC"
    assert g.get_alphabet() == "abc"
    assert g.get_start() == 'S'


def test_rules():
    g = Grammar("SABC", "abc", 'S')
    g.append_rules([Rule('S', "AB"), Rule('A', "Ab"), Rule('B', "bA")])
    assert g.get_certain_rules('A') == [Rule('A', "Ab")]


def test_change_start():
    g = Grammar("SX", "ab", 'S')
    g.change_start()
    assert g.get_start() == 'R'


def get_simple_parser() -> LR:
    g = Grammar("SC", "cd", 'S')
    g.append_rules([Rule('S', "CC"), Rule('C', "cC"), Rule('C', 'd')])
    parser = LR()
    parser.fit(g)
    return parser


def test_get_first1():
    parser = get_simple_parser()
    assert parser.get_epsilon_creators() == set()
    assert parser.getFirst('C') == {'c', 'd'}
    assert parser.getFirst('S') == {'c', 'd'}
    assert parser.getFirst('B') == {'c', 'd'}
    assert parser.getFirst("") == {'$'}
    assert parser.getFirst('c') == {'c'}


def test_LR():
    parser = get_simple_parser()
    assert parser.process("") is False
    assert parser.process('a') is False
    assert parser.process('c') is False
    assert parser.process("cdcd") is True
    assert parser.process("ccdd") is True
    assert parser.process("cc") is False
    assert parser.process("ddd") is False
    assert parser.process("ccccdcccd") is True


def get_epsilon_LR() -> LR:
    g = Grammar("SCD", "cd", 'S')
    g.append_rules([Rule('S', "CD"), Rule('C', ""), Rule('C', 'c'), Rule('D', ""), Rule('D', 'd')])
    parser = LR()
    parser.fit(g)
    return parser


def test_get_first2():
    parser = get_epsilon_LR()
    assert parser.get_epsilon_creators() == {'B', 'S', 'C', 'D'}
    assert parser.getFirst('S') == {'c', 'd', '$'}
    assert parser.getFirst('C') == {'c', '$'}
    assert parser.getFirst('D') == {'d', '$'}
    assert parser.getFirst('B') == {'c', 'd', '$'}


def test_epsilon_LR():
    parser = get_epsilon_LR()
    assert parser.process("") is True
    assert parser.process('a') is False
    assert parser.process('c') is True
    assert parser.process('d') is True
    assert parser.process("cd") is True
    assert parser.process("cc") is False


if __name__ == "__main__":
    pytest.main()
