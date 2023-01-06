import pytest

from src.libs.parser import LR, Grammar, Rule


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
    assert parser.getFirst("") == {LR.END}
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
    assert parser.process("cdd") is True
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
    assert parser.getFirst('S') == {'c', 'd', LR.END}
    assert parser.getFirst('C') == {'c', LR.END}
    assert parser.getFirst('D') == {'d', LR.END}
    assert parser.getFirst('B') == {'c', 'd', LR.END}


def test_epsilon_LR():
    parser = get_epsilon_LR()
    assert parser.process("") is True
    assert parser.process('a') is False
    assert parser.process('c') is True
    assert parser.process('d') is True
    assert parser.process("cd") is True
    assert parser.process("cc") is False


def get_cycled_LR() -> LR:
    g = Grammar('S', "ab", 'S')
    g.append_rules([Rule('S', "SaSb"), Rule('S', "")])
    parser = LR()
    parser.fit(g)
    return parser


def test_get_first3():
    parser = get_cycled_LR()
    assert parser.get_epsilon_creators() == {'R', 'S'}
    assert parser.getFirst('S') == {'a', LR.END}
    assert parser.getFirst('R') == {'a', LR.END}


def test_cycled_LR():
    parser = get_cycled_LR()
    assert parser.process("") is True
    assert parser.process("a") is False
    assert parser.process("c") is False
    assert parser.process("ab") is True
    assert parser.process("ba") is False
    assert parser.process("abab") is True
    assert parser.process("aababb") is True
    assert parser.process("aabb") is True


def test_LR4():
    g = Grammar('SD', "abc", 'S')
    g.append_rules([Rule('S', "SaSb"), Rule('S', "c"), Rule('S', 'D'), Rule('D', 'a')])
    parser = LR()
    parser.fit(g)
    assert parser.process("") is False
    assert parser.process("caab") is True
    assert parser.process("aacbaab") is True
    assert parser.process("aacbaaa") is False


def test_LR5():
    g = Grammar("SRT", "ab", 'S')
    g.append_rules([Rule('R', "aRa"), Rule('R', "bRb"), Rule('R', 'T'), Rule('T', "aSb"), Rule('T', "bSa"),
                    Rule('S', "aRa"), Rule('S', "bRb"), Rule('S', 'a'), Rule('S', 'b'), Rule('S', 'T'), Rule('S', "")])
    try:
        parser = LR()
        parser.fit(g)
    except Exception as e:
        assert isinstance(e, KeyError)


def test_new_getFirst():
    g = Grammar("SRT", "ab", 'S')
    g.append_rules([Rule('S', "RTS"), Rule('S', "a"), Rule('R', ""), Rule('R', 'a'), Rule('T', 'b')])
    parser = LR()
    parser.fit(g)
    assert parser.getFirst("RTS") == {'a', 'b'}


if __name__ == "__main__":
    pytest.main()
