globals()["__builtins__"].__dict__["__import__"] = None

try:
    import os
except Exception as e: print(e)
try:
    def test():
        import sys
        return sys.argv
    print(os.getcwd(),test())
except Exception as e: print(e)