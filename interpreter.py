from lark.visitors import Token, Tree, Interpreter
from scope import *
from subroutine import *

class Interpreter(Interpreter):
    def __init__(self):
        self.types = {
            "INTEGER": Type(int, 0),
            "REAL": Type(float, 0.0),
            "STRING": Type(str, ""),
            "BOOLEAN": Type(bool, False)
        }

        self.scope = Scope()
        self.call_stack = []

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
        return self.scope.get(tree.children[0])

    def declaration(self, tree):
        name, type = tree.children
        self.scope.define(str(name), Variable(self.types[type], self.types[type].default, True))

    def constant(self, tree):
        name, value = tree.children[0], self.visit(tree.children[1])
        self.scope.define(str(name), Variable(None, value, False))

    def assignment(self, tree):
        name, value = tree.children[0], self.visit(tree.children[1])
        self.scope.assign(name, value)

    # i/o
    def output(self, tree):
        out = [self.visit(child) for child in tree.children if not self.check_newline(child)]
        print(" ".join(map(str, out)))

    def input(self, tree):
        self.scope.define(tree.children[0], Variable(self.types["STRING"], input(), True))

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

        is_step = getattr(block[3], "data", None) == 'step'

        step = self.visit(block[3])[0] if is_step else 1
        iterator, start, stop = block[0], self.visit(block[1]), self.visit(block[2]) + (-1 if step < 0 else 1)

        assert step != 0, "Iteration step cannot be 0"

        self.scope.add_scope()
        
        self.scope.define(iterator, Variable(self.types['INTEGER'], start, True))

        for i in range(start, stop, step):
            self.scope.assign(iterator, i)

            for stmt in block[4:] if is_step else block[3:]:
                if not self.check_newline(stmt):
                    self.visit(stmt)

        self.scope.remove_scope()

    # subroutines
    def set_args(self, params, args):
        assert len(params) == len(args), f"Expected {len(params)} arguments, got {len(args)}"

        self.scope.add_scope()

        for i in range(len(args)):
            arg = self.visit(args[i])

            assert type(arg) == params[i][1].bind, f'Type mismatch in argument!'

            self.scope.define(params[i][0], Variable(params[i][1], arg, True))

    def get_params(self, param_tree):
        offset = 1
        params = {}

        if isinstance(param_tree, Tree) and param_tree.data == "param_list":
            for param in param_tree.children:
                name, type = param.children
                params[str(name)] = self.types[type]
            offset += 1

        return params, offset

    def procedure(self, tree):
        block = tree.children[0].children
        
        params, body = self.get_params(block[1])

        self.scope.define(block[0], Procedure(params, block[body:]))

    def call_procedure(self, tree):
        self.call_stack.append("procedure")

        name = tree.children[0]
        
        try:
            proc = self.scope.get(name)
        except:
            raise Exception(f'Procedure "{name}" is not defined!')

        self.set_args([*proc.params.items()], tree.children[1].children if len(tree.children) > 1 else [])

        for line in proc.code:
            if not self.check_newline(line):
                self.visit(line)
            
        self.scope.remove_scope()
        self.call_stack.pop()

    def function(self, tree):
        block = tree.children[0].children

        params, body = self.get_params(block[1])

        self.scope.define(str(block[0]), Function(self.types[block[body]], params, block[body + 1:]))

    def call_function(self, tree):
        self.call_stack.append("function")

        name = tree.children[0]
        
        try:
            func = self.scope.get(name)
        except:
            raise Exception(f'Procedure "{name}" is not defined!')

        self.set_args([*func.params.items()], tree.children[1].children)

        try:
            for line in func.code:
                if not self.check_newline(line):
                    self.visit(line)
        except ReturnCall as rc:
            ret_value = rc.value
            assert type(ret_value) == func.return_type.bind, f'Return type mismatch!'

            return ret_value
            
        self.scope.remove_scope()
        self.call_stack.pop()

        return func.return_type.default
    
    def return_stmt(self, tree):
        assert len(self.call_stack) and self.call_stack[-1] == "function", "RETURN statement ouside Function block!"

        raise ReturnCall(self.visit(tree.children[0]))