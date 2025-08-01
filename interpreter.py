from lark import Lark, Visitor, Tree, Token
from lark.visitors import Interpreter

class Type:
    def __init__(self, bind, default):
        self.bind, self.default = bind, default

class Variable:
    def __init__(self, type, value, mutable):
        self.type, self.value, self.mutable = type, value, mutable

class Interpreter(Interpreter):
    def __init__(self):
        self.types = {
            "INTEGER": Type(int, 0),
            "REAL": Type(float, 0.0),
            "STRING": Type(str, ""),
            "BOOLEAN": Type(bool, False)
        }

        self.vars = {}

    # data types
    def number(self, tree):
        n = tree.children[0]
        return float(n) if '.' in n else int(n)
    
    def string(self, tree):
        return tree.children[0][1:-1]
    
    def boolean(self, tree):
        return tree.children[0] == "TRUE"

    # arithmetic operators
    def add(self, tree):
        return self.visit(tree.children[0]) + self.visit(tree.children[1])

    def sub(self, tree):
        return self.visit(tree.children[0]) - self.visit(tree.children[1])

    def mul(self, tree):
        return self.visit(tree.children[0]) * self.visit(tree.children[1])

    def div(self, tree):
        return self.visit(tree.children[0]) / self.visit(tree.children[1])
    
    # logical operators
    def and_op(self, tree):
        return self.visit(tree.children[0]) and self.visit(tree.children[1])
    
    def or_op(self, tree):
        return self.visit(tree.children[0]) or self.visit(tree.children[1])
     
    # comparision operators
    def gt(self, tree):
        return self.visit(tree.children[0]) > self.visit(tree.children[1])
    
    def lt(self, tree):
        return self.visit(tree.children[0]) < self.visit(tree.children[1])
    
    def gte(self, tree):
        return self.visit(tree.children[0]) >= self.visit(tree.children[1])
    
    def lte(self, tree):
        return self.visit(tree.children[0]) <= self.visit(tree.children[1])
    
    def eq(self, tree):
        return self.visit(tree.children[0]) == self.visit(tree.children[1])
    
    def neq(self, tree):
        return self.visit(tree.children[0]) != self.visit(tree.children[1])
    
    # variables
    def var(self, tree):
        name = tree.children[0]

        assert name in self.vars, f'Variable "{name}" is not defined!'

        return self.vars[name].value
    
    def declaration(self, tree):
        name, type = tree.children

        self.vars[str(name)] = Variable(self.types[type], self.types[type].default, True)

    def assignment(self, tree):
        name, value = tree.children[0], self.visit(tree.children[1])

        assert self.vars[name].mutable, f'Cannot assign to constant "{name}"!'
        assert type(value) == self.vars[name].type.bind, "Type mismatch!"
        
        self.vars[name].value = value

    def constant(self, tree):
        name, value = tree.children[0], self.visit(tree.children[1])
        
        self.vars[str(name)] = Variable(None, value, False)

    # i/o
    def output(self, tree):
        value = self.visit(tree.children[0])
        print(value)

    def input(self, tree):
        self.vars[tree.children[0]] = Variable(self.types["STRING"], input(), True)

    # conditional flow
    def conditional(self, tree):
        for branch in tree.children[0].children:
            if "if_branch" in branch.data:
                if not self.visit(branch.children[0]):
                    continue
            
            for stmt in branch.children[1:]:
                if stmt != "\n":
                    self.visit(stmt)
            return