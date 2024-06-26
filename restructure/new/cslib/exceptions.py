
class CrosshellDebErr(Exception):
    def __init__(self, message="The crosshell debugger raised an exception!"):
        self.message = message
        super().__init__(self.message)

class CrosshellExit(Exception):
    def __init__(self, message="Crosshell Exit Exception Raised!"):
        self.message = message
        super().__init__(self.message)