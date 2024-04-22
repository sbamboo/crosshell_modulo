import ast
import builtins

class ImportForbiddenError(Exception):
    pass

class BuiltinsForbiddenError(Exception):
    pass

class ForbiddenContextManager:
    def __enter__(self):
        self.original_import = builtins.__import__
        self.original_builtins = builtins.__dict__.copy()
        builtins.__import__ = None
        builtins.__dict__.clear()

    def __exit__(self, exc_type, exc_value, traceback):
        # Reset __builtins__ after exiting the context manager
        builtins.__import__ = self.original_import
        builtins.__dict__.update(self.original_builtins)

# Function definition outside of the context manager
def test():
    import os
    print(os.getcwd())

# Usage
with ForbiddenContextManager():
    try:
        test()
    except (ImportForbiddenError, BuiltinsForbiddenError) as e:
        print("Caught the error:", e)
