class Procedure:
    def __init__(self, params, code):
        self.params, self.code = params, code

    def __str__(self):
        return "<Procedure>"

class Function(Procedure):
    def __init__(self, return_type, params, code):
        super().__init__(params, code)
        
        self.return_type = return_type

    def __str__(self):
        return "<Function>"
    
class ReturnCall(Exception):
    def __init__(self, value):
        self.value = value