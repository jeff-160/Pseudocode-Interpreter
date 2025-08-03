from lark.visitors import Token, Tree, Interpreter
from ast import literal_eval
from pchar import *
from scope import *

class Param:
    def __init__(self, type, sub_type=None):
        self.type, self.sub_type = type, sub_type

    def get_type(self, t=None):
        if t is None:
            t = self

        if isinstance(t, Type):
            return t.name
        
        if isinstance(t, Param):
            result = t.type.name
            if t.sub_type:
                result += f'<{self.get_type(t.sub_type)}>'
            return result

        return str(t)

def format_error(file, line_no, error, line):
    return f'{file}:{line_no}: {error}\n\t{line}'

class Interpreter(Interpreter):
    def __init__(self, file, code, no_newlines):
        self.file, self.code = file, code
        self.no_newlines = no_newlines

        self.scope = Scope()
        self.call_stack = []

    def check_newline(self, stmt):
        return isinstance(stmt, Token) and stmt.type == "NEWLINE"
            
    def check_indices(self, collection, indices):
        for i in range(len(indices)):
            index = indices[i]
            a = collection[0] if len(indices) > 1 and i > 0 else collection

            assert isinstance(index, int), "Index must be an integer"
            assert index in range(1, len(a) + 1), f'Index "{index}" out of bounds'

    def catch_error(func):
        def wrapper(self, tree):
            try:
                try:
                    return func(self, tree)
                except TypeError:
                    a, b = map(self.visit, tree.children)
                    raise Exception(f'Operation not supported between "{get_type(a)}" and "{get_type(b)}"')
            except ReturnCall:
                raise
            except Exception as e:
                import sys
                
                sys.exit(format_error(self.file, tree.meta.line, e, self.code.splitlines()[tree.meta.line - 1]))
        return wrapper
    
    def scoped(func):
        def wrapper(self, *args, **kwargs):
            self.scope.add_scope()
            
            func(self, *args, **kwargs)

            self.scope.remove_scope()
        
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
                value = [[TYPES[type].default] * dimensions[1][1] for _ in range(dimensions[0][1])]
            else:
                value = [TYPES[type].default] * dimensions[0][1]


            self.scope.define(str(name), Variable(TYPES["ARRAY"], value, True, type))
        else:
            self.scope.define(str(name), Variable(TYPES[block], TYPES[block].default, True))

    @catch_error
    def constant(self, tree):
        name, value = tree.children[0], self.visit(tree.children[1])
        self.scope.define(str(name), Variable(TYPES[get_type(value)], value, False))

    @catch_error
    def assignment(self, tree):
        name, value = tree.children[0], self.visit(tree.children[1])
        self.scope.assign(name, value)

    @catch_error
    def index_assignment(self, tree):
        name, indices, value = tree.children[0], *map(self.visit, tree.children[1:])

        var = self.scope.get(name)
    
        assert isinstance(var, list), f'Cannot apply index assignment to "{get_type(var)}"'
        
        if len(indices) == 1 and isinstance(var[0], list):
            raise Exception(f'Cannot assign to "{get_type(var[0])}"')
        
        cmp = var[0][0] if len(indices) > 1 else var[0]
        assert type(value) == type(cmp), f'Assignment type mismatch, expected "{get_type(cmp)}", got "{get_type(value)}"'

        self.check_indices(var, indices)

        self.scope.assign_index(name, [*map(lambda x: x - 1, indices)], value)

    # indexing
    @catch_error
    def get_index(self, tree):
        value, indices = map(self.visit, tree.children)

        assert type(value) in [str, list], f'Cannot apply indexing to "{get_type(value)}"'
        
        if len(indices) > 1 and not isinstance(value[0], list):
            raise Exception(f'Cannot apply 2D indexing to "{get_type(value)}"')

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
        self.scope.define(tree.children[0], Variable(TYPES["STRING"], input(), True))

    # conditionals
    @scoped
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

    @scoped
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
    @scoped
    @catch_error
    def while_loop(self, tree):
        block = tree.children[0].children

        while self.visit(block[0]):
            for stmt in block[1:]:
                if not self.check_newline(stmt):
                    self.visit(stmt)

    @scoped
    @catch_error
    def repeat_until(self, tree):
        block = [line for line in tree.children[0].children if not self.check_newline(line)]

        condition = True

        while condition:
            for stmt in block[:-1]:
                self.visit(stmt)
                
            condition = not self.visit(block[-1])

    @scoped
    @catch_error
    def for_loop(self, tree):
        block = tree.children[0].children

        is_step = getattr(block[3], "data", None) == 'step'

        step = self.visit(block[3])[0] if is_step else 1
        iterator, start, stop = block[0], self.visit(block[1]), self.visit(block[2]) + (-1 if step < 0 else 1)

        assert step != 0, "Iteration step cannot be 0"
        
        self.scope.define(iterator, Variable(TYPES['INTEGER'], start, True))

        for i in range(start, stop, step):
            self.scope.assign(iterator, i)

            for stmt in block[4:] if is_step else block[3:]:
                if not self.check_newline(stmt):
                    self.visit(stmt)

    # subroutines
    def set_args(self, params, args):
        assert len(params) == len(args), f"Expected {len(params)} arguments, got {len(args)}"

        self.scope.add_scope()

        for i in range(len(args)):
            arg = self.visit(args[i])

            # pass arrays by value
            if isinstance(arg, list):
                arg = arg[:]

            param_type = params[i][1].get_type()
            assert get_type(arg) == param_type, f'Expected "{param_type}" argument type, got "{get_type(arg)}"'

            self.scope.define(params[i][0], Variable(TYPES[params[i][1].type.name], arg, True))

    def get_param(self, block):
        if getattr(block, "data", None) == "arg_param":
            if getattr(block.children[0], "data", None) == "arg_param":
                return Param(TYPES["ARRAY"], Param(TYPES["ARRAY"], TYPES[block.children[0].children[0]]))
            else:
                return Param(TYPES["ARRAY"], TYPES[block.children[0]])
        else:
            return Param(TYPES[block])

    def get_params(self, param_tree):
        offset = 1
        params = {}

        if isinstance(param_tree, Tree) and param_tree.data == "param_list":
            for param in param_tree.children:
                name, type = param.children

                assert name not in params, f'Duplicate parameter name "{name}"'

                params[str(name)] = self.get_param(type)
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

        ret_type = self.get_param(block[body])

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
            call_type = get_type(rc.value) 
            ret_type = func.return_type.get_type()

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
        
        assert type(value) in [str, list], f'Cannot apply LENGTH() to "{get_type(value)}"'

        return len(value)
    
    @catch_error
    def type_cast(self, tree):
        cast, value = TYPES[tree.children[0]], self.visit(tree.children[1])
        
        try:
            return cast.bind(value)
        except:
            raise Exception(f'Cannot cast "{get_type(value)}" to "{cast.name}"')