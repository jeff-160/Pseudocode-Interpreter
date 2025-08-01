class Procedure:
    def __init__(self, params, code):
        self.params, self.code = params, code

class Function(Procedure):
    def __init__(self, return_type, params, code):
        super().__init__(params, code)
        
        self.return_type = return_type