class Procedure:
    def __init__(self, params, code):
        self.params, self.code = params, code

    def __str__(self):
        return f'<{self.__class__.__name__}>'

class Function(Procedure):
    def __init__(self, return_type, params, code):
        super().__init__(params, code)
        
        self.return_type = return_type
    
class ReturnCall(Exception):
    def __init__(self, value):
        self.value = value