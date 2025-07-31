from lark import Lark, Transformer

class Type:
    def __init__(self, bind, default):
        self.bind, self.default = bind, default

class Variable:
    def __init__(self, type, value, mutable):
        self.type, self.value, self.mutable = type, value, mutable

class Interpreter(Transformer):
    def __init__(self):
        self.types = {
            "INTEGER": Type(int, 0),
            "REAL": Type(float, 0.0),
            "STRING": Type(str, ""),
            "BOOLEAN": Type(bool, False)
        }

        self.vars = {}

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
    def var(self, items):
        name = items[0]

        assert name in self.vars, f'Variable "{name}" is not defined!'

        return self.vars[name].value
    
    def declaration(self, items):
        name, type = items
        
        self.vars[str(name)] = Variable(self.types[type], self.types[type].default, True)

    def assignment(self, items):
        name, value = items

        assert self.vars[name].mutable, f'Cannot assign to constant "{name}"!'
        assert type(value) == self.vars[name].type.bind, "Type mismatch!"
        
        self.vars[name].value = value

    def constant(self, items):
        name, value = items
        
        self.vars[str(name)] = Variable(None, value, False)

    # logical operators
    def and_op(self, items):
        a, b = items
        return a and b
    
    def or_op(self, items):
        a, b = items
        return a or b
    
    # comparision operators
    def gt(self, items):
        a, b = items
        return a > b
    
    def lt(self, items):
        a, b = items
        return a < b
    
    def gte(self, items):
        a, b = items
        return a >= b
    
    def lte(self, items):
        a, b = items
        return a <= b
    
    def eq(self, items):
        a, b = items
        return a == b
    
    def neq(self, items):
        a, b = items
        return a != b

    # i/o
    def output(self, items):
        print(items[0])

    def input(self, items):
        self.vars[items[0]] = Variable(self.types["STRING"], input(), True)


with open("grammar.lark", "r") as f:
    grammar = f.read().strip()

parser = Lark(grammar, parser='lalr', transformer=Interpreter())