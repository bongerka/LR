from libs.parser import LR
from libs.grammar import Grammar
from libs.rule import Rule


def main():
    g = Grammar("SCD", "cd", 'S')
    g.append_rules([Rule('S', "CD"), Rule('C', ""), Rule('C', 'c'), Rule('D', ""), Rule('D', 'd')])
    parser = LR()
    parser.fit(g)
    parser.getFirst('S')


if __name__ == "__main__":
    main()
