from ptypes import *

class Variable:
    def __init__(self, type, value, mutable, subtype=None):
        self.type, self.value, self.mutable = type, value, mutable
        self.subtype = subtype

# for variable scopes
class Scope:
    def __init__(self):
        self.stack = [{}]

    def get(self, name):
        for scope in self.stack[::-1]:
            if name in scope:
                return getattr(scope[name], "value", scope[name])
        
        raise Exception(f'Variable "{name}" is not defined')
    
    def define(self, name, variable):
        self.stack[-1][name] = variable

    def assign(self, name, value):
        for scope in self.stack[::-1]:
            if name in scope:
                assert scope[name].type.name != "ARRAY", f'Cannot assign to "{get_type(scope[name].value)}"'
                assert isinstance(scope[name], Variable), f'Cannot assign to "{str(scope[name])}"'
                assert scope[name].mutable, f'Cannot assign to constant "{name}"'
                assert type(value) == scope[name].type.bind, f'Assignment type mismatch, expected "{get_type(scope[name].value)}", got "{get_type(value)}"'
                
                scope[name].value = value
                return
            
        raise Exception(f'Variable "{name}" is not declared')
    
    def assign_index(self, name, indices, value):
        for scope in self.stack[::-1]:
            if name in scope:
                arr = scope[name].value

                if len(indices) > 1:
                    arr[indices[0]][indices[1]] = value
                else:
                    arr[indices[0]] = value
                return

        raise Exception(f'Array "{name}" is not declared')
    
    def add_scope(self):
        self.stack.append({})

    def remove_scope(self):
        self.stack.pop()