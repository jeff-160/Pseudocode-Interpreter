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

    return Lark(grammar, parser='lalr', propagate_positions=True)

def main():
    args = arg_parser.parse_args()
    file_path = args.file

    ext = ".pseudo"

    try:
        assert file_path[::-1].startswith(ext[::-1]), f'File must have "{ext}" extension'

        with open(file_path, "r") as f:
            program = "\n".join([line.strip() for line in f.read().split("\n")])
        
        ast = get_parser().parse(program)
        Interpreter(file_path, program, args.no_newlines).visit(ast)
    except FileNotFoundError:
        print(f'Could not locate file: "{file_path}"')
    except Exception as e:
        if hasattr(e, "get_context"):
            print(format_error(file_path, e.line, str(e).splitlines()[0], program.split("\n")[e.line - 1]))
        else:
            print(e)

if __name__ == "__main__":
    main()