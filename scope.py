class Type:
    def __init__(self, bind, default):
        self.bind, self.default = bind, default

class Variable:
    def __init__(self, type, value, mutable):
        self.type, self.value, self.mutable = type, value, mutable

# for variable scopes
class Scope:
    def __init__(self):
        self.stack = [{}]

    def get(self, name):
        for scope in self.stack[::-1]:
            if name in scope:
                return scope[name].value
        
        raise Exception(f'Variable {name}" is not defined!')
    
    def define(self, name, variable):
        self.stack[-1][name] = variable

    def assign(self, name, value):
        for scope in self.stack[::-1]:
            if name in scope:
                assert scope[name].mutable, f'Cannot assign to constant "{name}"!'
                assert type(value) == scope[name].type.bind, "Type mismatch!"
                
                scope[name].value = value
                return
        raise Exception(f'Variable "{name}" is not declared!')
    
    def add_scope(self):
        self.stack.append({})

    def remove_scope(self):
        self.stack.pop()