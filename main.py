import sys
sys.dont_write_bytecode = True

from lark import Lark
import argparse
from interpreter import *

arg_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

arg_parser.add_argument('file', help="source file to run")

arg_parser.add_argument(
    "--no-newlines",
    action="store_true",
    default=False,
    help="toggle auto newlines when printing"
)


def get_parser():
    with open("syntax.lark", "r") as f:
        grammar = f.read().strip()

    return Lark(grammar, parser='lalr')

def main():
    args = arg_parser.parse_args()
    file_path = args.file

    try:
        with open(file_path, "r") as f:
            program = "\n".join([line.strip() for line in f.read().split("\n")])
        
        Interpreter(args.no_newlines).visit(get_parser().parse(program))
    except FileNotFoundError:
        print(f'Could not locate file: "{file_path}"')
    # except Exception as e:
    #     print(e)

if __name__ == "__main__":
    main()