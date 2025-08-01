import sys
sys.dont_write_bytecode = True

from interpreter import *

with open("test.txt", "r") as f:
    program = "\n".join([line.strip() for line in f.read().split("\n")])

with open("grammar.lark", "r") as f:
    grammar = f.read().strip()

parser = Lark(grammar, parser='lalr')
Interpreter().visit(parser.parse(program))