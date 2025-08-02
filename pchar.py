# blame python
class PChar:
    def __init__(self, value):
        if isinstance(value, PChar):
            self._char = value._char
        elif isinstance(value, int):
            try:
                self._char = chr(value)
            except:
                raise Exception(f'Integer "{value}" out of range for CHAR: {value}')
        elif isinstance(value, str):
            assert len(value) == 1, f"CHAR must be a single character, got '{value}'"
            self._char = value
        
        else:
            raise TypeError(f'Cannot convert "{value}" to "CHAR"')
    
    def __str__(self):
        return self._char
    
    def __eq__(self, other):
        if isinstance(other, PChar):
            return self._char == other._char
        if isinstance(other, str) and len(other) == 1:
            return self._char == other
        return False