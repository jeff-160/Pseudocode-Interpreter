from lark.visitors import Token, Tree, Interpreter
from ast import literal_eval
from pchar import *
from scope import *
from subroutine import *

class Param:
    def __init__(self, type, sub_type=None):
        self.type, self.sub_type = type, sub_type

def format_error(file, line_no, error, line):
    return f'{file}:{line_no}: {error}\n\t{line}'

class Interpreter(Interpreter):
    def __init__(self, file, code, no_newlines):
        self.file, self.code = file, code
        self.no_newlines = no_newlines

        self.types = {
            type.name: type

            for type in [
                Type("INTEGER", int, 0),
                Type("REAL", float, 0.0),
                Type("STRING", str, ""),
                Type("BOOLEAN", bool, False),
                Type("CHAR", PChar, PChar("\x00")),
                Type("ARRAY", list, [])
            ]
        }

        self.scope = Scope()
        self.call_stack = []

    def check_newline(self, stmt):
        return isinstance(stmt, Token) and stmt.type == "NEWLINE"
    
    def get_type(self, value):
        raw_type = type(value)

        if raw_type in [Procedure, Function]:
            return raw_type.__name__

        for i, _ in self.types.items():
            if raw_type == self.types[i].bind:
                return type_repr(i, self.get_type(value[0]) if i == "ARRAY" else None)
            
    def check_indices(self, collection, indices):
        for i in range(len(indices)):
            index = indices[i]
            a = collection[0] if len(indices) > 1 and i > 0 else collection

            assert isinstance(index, int), "Index must be an integer"
            assert index in range(1, len(a) + 1), f'Index "{index}" out of bounds'

    def catch_error(func):
        def wrapper(self, tree):
            try:
                return func(self, tree)
            except ReturnCall:
                raise
            # except TypeError:
            #     a, b = map(self.visit, tree.children)
            #     raise Exception(f'Operation not supported between "{self.get_type(a)}" and "{self.get_type(b)}"')
            # except Exception as e:
            #     exit(format_error(self.file, tree.meta.line, e, self.code.splitlines()[tree.meta.line - 1]))
        return wrapper

    # data types
    def number(self, tree):
        n = tree.children[0]
        return float(n) if '.' in n else int(n)
    
    def string(self, tree):
        return literal_eval(tree.children[0])
    
    def boolean(self, tree):
        return tree.children[0] == "TRUE"
    
    def char(self, tree):
        return PChar(literal_eval(tree.children[0]))

    # arithmetic operators
    @catch_error
    def neg(self, tree):
        return -self.visit(tree.children[0])

    @catch_error
    def add(self, tree):
        return self.visit(tree.children[0]) + self.visit(tree.children[1])

    @catch_error
    def sub(self, tree):
        return self.visit(tree.children[0]) - self.visit(tree.children[1])

    @catch_error
    def mul(self, tree):
        return self.visit(tree.children[0]) * self.visit(tree.children[1])

    @catch_error
    def div(self, tree):
        return self.visit(tree.children[0]) / self.visit(tree.children[1])
    
    @catch_error
    def mod(self, tree):
        return self.visit(tree.children[0]) % self.visit(tree.children[1])
    
    # logical operators
    @catch_error
    def and_op(self, tree):
        return self.visit(tree.children[0]) and self.visit(tree.children[1])

    @catch_error
    def or_op(self, tree):
        return self.visit(tree.children[0]) or self.visit(tree.children[1])
     
    # comparision operators
    @catch_error
    def gt(self, tree):
        return self.visit(tree.children[0]) > self.visit(tree.children[1])
    
    @catch_error
    def lt(self, tree):
        return self.visit(tree.children[0]) < self.visit(tree.children[1])
    
    @catch_error
    def gte(self, tree):
        return self.visit(tree.children[0]) >= self.visit(tree.children[1])
    
    @catch_error
    def lte(self, tree):
        return self.visit(tree.children[0]) <= self.visit(tree.children[1])
    
    @catch_error
    def eq(self, tree):
        return self.visit(tree.children[0]) == self.visit(tree.children[1])
    
    @catch_error
    def neq(self, tree):
        return self.visit(tree.children[0]) != self.visit(tree.children[1])
    
    # variables
    @catch_error
    def var(self, tree):
        return self.scope.get(tree.children[0])

    @catch_error
    def declaration(self, tree):
        name, block = tree.children

        if hasattr(block, "data"):
            dimensions = []

            for bounds in block.children[:-1]:
                l, u = map(self.visit, bounds.children)

                assert isinstance(l, int) and isinstance(u, int), self.get_error("Array indices must be integers", tree)
                assert u >= l, "Invalid array bounds"
                assert l == 1, "Array must be 1-indexed"

                dimensions.append((l, u))

            type = block.children[-1]

            
            if len(dimensions) > 1:
                value = [[self.types[type].default] * dimensions[1][1] for _ in range(dimensions[0][1])]
            else:
                value = [self.types[type].default] * dimensions[0][1]


            self.scope.define(str(name), Variable(self.types["ARRAY"], value, True, type))
        else:
            self.scope.define(str(name), Variable(self.types[block], self.types[block].default, True))

    @catch_error
    def constant(self, tree):
        name, value = tree.children[0], self.visit(tree.children[1])
        self.scope.define(str(name), Variable(None, value, False))

    @catch_error
    def assignment(self, tree):
        name, value = tree.children[0], self.visit(tree.children[1])
        self.scope.assign(name, value)

    @catch_error
    def index_assignment(self, tree):
        name, indices, value = tree.children[0], *map(self.visit, tree.children[1:])

        var = self.scope.get(name)
    
        assert isinstance(var, list), f'Cannot apply index assignment to "{self.get_type(var)}"'
        
        if len(indices) == 1 and isinstance(var[0], list):
            raise Exception(f'Cannot assign to "{self.get_type(var[0])}"')

        assert type(value) == type(var[0][0] if len(indices) > 1 else var[0]), f'Assignment type mismatch, expected "{self.get_type(var[0])}"'

        self.check_indices(var, indices)

        self.scope.assign_index(name, [*map(lambda x: x - 1, indices)], value)

    # indexing
    @catch_error
    def get_index(self, tree):
        value, indices = map(self.visit, tree.children)

        assert type(value) in [str, list], f'Cannot apply indexing to "{self.get_type(value)}"'
        
        if len(indices) > 1 and not isinstance(value[0], list):
            raise Exception(f'Cannot apply 2D indexing to "{self.get_type(value)}"')

        self.check_indices(value, indices)

        indices = [*map(lambda x: x - 1, indices)]

        return value[indices[0]][indices[1]] if len(indices) > 1 else value[indices[0]]

    # i/o
    @catch_error
    def output(self, tree):
        out = [self.visit(child) for child in tree.children if not self.check_newline(child)]
        print(" ".join(map(str, out)), end=("" if self.no_newlines else "\n"))

    @catch_error
    def input(self, tree):
        self.scope.define(tree.children[0], Variable(self.types["STRING"], input(), True))

    # conditionals
    @catch_error
    def conditional(self, tree):
        for branch in tree.children[0].children:
            if "if_branch" in branch.data:
                if not self.visit(branch.children[0]):
                    continue
            
            for stmt in branch.children[1:]:
                if not self.check_newline(stmt):
                    self.visit(stmt)
            return

    @catch_error
    def switch(self, tree):
        block = tree.children[0].children

        identifier = block[0]

        for branch in block[1:]:
            if self.check_newline(branch):
                continue

            if branch.data == "otherwise_branch":
                self.visit(branch)
                return

            condition = self.visit(branch.children[0])
            
            if condition == self.scope.get(identifier):
                self.visit(branch.children[1])
                return
     
    # loops
    @catch_error
    def while_loop(self, tree):
        block = tree.children[0].children

        while self.visit(block[0]):
            for stmt in block[1:]:
                if not self.check_newline(stmt):
                    self.visit(stmt)

    @catch_error
    def repeat_until(self, tree):
        block = [line for line in tree.children[0].children if not self.check_newline(line)]

        condition = True

        while condition:
            for stmt in block[:-1]:
                self.visit(stmt)
                
            condition = not self.visit(block[-1])

    @catch_error
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

            # pass arrays by value
            if isinstance(arg, list):
                arg = arg[:]

            if isinstance(params[i][1].sub_type, Param):
                sub_type = type_repr(params[i][1].sub_type.type.name, params[i][1].sub_type.sub_type.name)
            else:
                sub_type = getattr(params[i][1].sub_type, "name", None)

            param_type = type_repr(params[i][1].type.name, sub_type)
            assert self.get_type(arg) == param_type, f'Expected "{param_type}" argument type, got "{self.get_type(arg)}"'

            self.scope.define(params[i][0], Variable(self.types[params[i][1].type.name], arg, True))

    def get_params(self, param_tree):
        offset = 1
        params = {}

        if isinstance(param_tree, Tree) and param_tree.data == "param_list":
            for param in param_tree.children:
                name, type = param.children

                assert name not in params, f'Duplicate parameter name "{name}"'

                if getattr(type, "data", None) == "arg_param":
                    if getattr(type.children[0], "data", None) == "arg_param":
                        params[str(name)] = Param(self.types["ARRAY"], Param(self.types["ARRAY"], self.types[type.children[0].children[0]]))
                    else:
                        params[str(name)] = Param(self.types["ARRAY"], self.types[type.children[0]])
                else:
                    params[str(name)] = Param(self.types[type])
            offset += 1

        return params, offset

    @catch_error
    def procedure(self, tree):
        block = tree.children[0].children
        
        params, body = self.get_params(block[1])

        self.scope.define(block[0], Procedure(params, block[body:]))

    @catch_error
    def call_procedure(self, tree):
        self.call_stack.append("procedure")

        name = tree.children[0]
        
        try:
            proc = self.scope.get(name)
        except:
            raise Exception(f'Procedure "{name}" is not defined')
        
        assert not isinstance(proc, Function), f'Cannot "CALL" Function, directly invoke instead'
        
        args = tree.children[1].children if len([i for i in tree.children if not self.check_newline(i)]) > 1 else []
        self.set_args([*proc.params.items()], args)

        for line in proc.code:
            if not self.check_newline(line):
                self.visit(line)
            
        self.scope.remove_scope()
        self.call_stack.pop()

    @catch_error
    def function(self, tree):
        block = tree.children[0].children

        params, body = self.get_params(block[1])

        if getattr(block[body], "data", None) == "arg_param":
            ret_type = Param(self.types["ARRAY"], self.types[block[body].children[0]])
        else:
            ret_type = Param(self.types[block[body]])

        self.scope.define(str(block[0]), Function(ret_type, params, block[body + 1:]))

    @catch_error
    def call_function(self, tree):
        self.call_stack.append("function")

        name = tree.children[0]
        
        try:
            func = self.scope.get(name)
        except:
            raise Exception(f'Function "{name}" is not defined')
        
        assert isinstance(func, Function), f'Cannot directly invoke Procedure "{name}", use "CALL"'

        self.set_args([*func.params.items()], tree.children[1].children)

        try:
            for line in func.code:
                if not self.check_newline(line):
                    self.visit(line)
        except ReturnCall as rc:
            call_type = self.get_type(rc.value) 
            ret_type = type_repr(func.return_type.type.name, getattr(func.return_type.sub_type, "name", None))

            assert call_type == ret_type, f'Expected "{ret_type}" RETURN type, got "{call_type}"'

            self.scope.remove_scope()
            return rc.value
            
        self.scope.remove_scope()
        self.call_stack.pop()

        return func.return_type.type.default
    
    @catch_error
    def return_stmt(self, tree):
        assert len(self.call_stack) and self.call_stack[-1] == "function", "RETURN statement ouside Function block"

        raise ReturnCall(self.visit(tree.children[0]))
    
    # builtin functions
    @catch_error
    def length(self, tree):
        value = self.visit(tree.children[0])
        
        assert type(value) in [str, list], f'Cannot apply LENGTH() to "{self.get_type(value)}"'

        return len(value)
    
    @catch_error
    def type_cast(self, tree):
        cast, value = self.types[tree.children[0]], self.visit(tree.children[1])
        
        try:
            return cast.bind(value)
        except:
            raise Exception(f'Cannot cast "{self.get_type(value)}" to "{cast.name}"')