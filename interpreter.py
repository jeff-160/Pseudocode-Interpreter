from lark.visitors import Token, Interpreter

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

    def check_newline(self, stmt):
        return isinstance(stmt, Token) and stmt.type == "NEWLINE"

    # data types
    def number(self, tree):
        n = tree.children[0]
        return float(n) if '.' in n else int(n)
    
    def string(self, tree):
        return tree.children[0][1:-1]
    
    def boolean(self, tree):
        return tree.children[0] == "TRUE"

    # arithmetic operators
    def neg(self, tree):
        return -self.visit(tree.children[0])

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

        assert name in self.vars, f'Variable "{name}" is not declared yet!'
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

    # conditionals
    def conditional(self, tree):
        for branch in tree.children[0].children:
            if "if_branch" in branch.data:
                if not self.visit(branch.children[0]):
                    continue
            
            for stmt in branch.children[1:]:
                if not self.check_newline(stmt):
                    self.visit(stmt)
            return
        
    # loops
    def while_loop(self, tree):
        block = tree.children[0].children

        while self.visit(block[0]):
            for stmt in block[1:]:
                if not self.check_newline(stmt):
                    self.visit(stmt)

    def repeat_until(self, tree):
        block = [line for line in tree.children[0].children if not self.check_newline(line)]

        condition = True

        while condition:
            for stmt in block[:-1]:
                self.visit(stmt)
                
            condition = not self.visit(block[-1])

    def for_loop(self, tree):
        block = tree.children[0].children

        iterator, start, end = block[0], self.visit(block[1]), self.visit(block[2])
        
        self.vars[iterator] = Variable(self.types['INTEGER'], start, True)

        for i in range(start, end + 1):
            for stmt in block[3:]:
                if not self.check_newline(stmt):
                    self.visit(stmt)
            
            if i < end:
                self.vars[iterator].value += 1