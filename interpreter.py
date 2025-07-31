from lark import Lark, Transformer

class Interpreter(Transformer):
    def __init__(self):
        self.types = {
            "INTEGER": (int, 0),
            "REAL": (float, 0.0),
            "STRING": (str, ""),
            "BOOLEAN": (bool, False)
        }

        self.vars = {} # [type, value]

    # data types
    def number(self, items):
        n = items[0]

        return float(n) if '.' in n else int(n)
    
    def string(self, s):
        return s[0][1:-1]

    # operators
    def add(self, items):
        return items[0] + items[1]

    def sub(self, items):
        return items[0] - items[1]

    def mul(self, items):
        return items[0] * items[1]

    def div(self, items):
        return items[0] // items[1]
    
    # variables
    def declaration(self, items):
        name, type = items
        
        self.vars[name] = [type, self.types[type][1]]

    def assignment(self, items):
        name, value = items

        assert type(value) == self.types[self.vars[name][0]][0], "Type mismatch!"
        self.vars[name][1] = value

    def var(self, items):
        name = items[0]

        assert name in self.vars, f'Variable "{name}" is not defined!'

        return self.vars[name][1]

    # i/o
    def output(self, items):
        print(items[0])

    def input(self, items):
        print(items)

with open("grammar.txt", "r") as f:
    grammar = f.read().strip()

parser = Lark(grammar, parser='lalr', transformer=Interpreter())