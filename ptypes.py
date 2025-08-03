from pchar import *
from subroutine import *

def type_repr(main_type, sub_type=None):
    return main_type + (f"<{sub_type}>" if sub_type else "")

class Type:
    def __init__(self, name, bind, default):
        self.name, self.bind, self.default = name, bind, default

TYPES = {
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

def get_type(value):
    raw_type = type(value)

    if raw_type in [Procedure, Function]:
        return raw_type.__name__.upper()

    for i, _ in TYPES.items():
        if raw_type == TYPES[i].bind:
            return type_repr(i, get_type(value[0]) if i == "ARRAY" else None)