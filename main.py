import sys
sys.dont_write_bytecode = True

from interpreter import *

with open("test.txt", "r") as f:
    program = f.read()

parser.parse(program)