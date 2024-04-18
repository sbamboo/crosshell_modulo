# LimitExec: Library to limit the capabilities of an executed script
# Author: Simon Kalmi Claesson

# [imports]
import os

# [Dummy classes]
class DummyObject:
    '''CSlib.externalLibs.LimitExec: Dummy object.'''
    # Subscribable
    def __getitem__(self, key):
        return DummyObject()
    # Callable
    def __call__(self, *args, **kwargs):
        pass

class ReturningDummyObject:
    '''CSlib.externalLibs.LimitExec: Dummy object, returns input.'''
    # Subscribable
    def __getitem__(self, key):
        return key
    # Callable
    def __call__(self, *args, **kwargs):
        return args, kwargs
    
class RaisingDummyObject:
    '''CSlib.externalLibs.LimitExec: Dummy object, raises.'''
    # Subscribable
    def __getitem__(self, key):
        raise NameError("Callable '"+key+"' Not found in restricted session.")
    # Callable
    def __call__(self, *args, **kwargs):
        raise NameError()

# [Functions]
def LimitedExec(path,allowed_locals,return_scope,mode=None):
    '''CSlib.externalLibs.LimitExec: Main function for calling restricted functions.'''
    # Get code content
    code = open(path,'r').read()
    # Specify Dummys for blocked sents
    allowed_globals = {
        '__builtins__': DummyObject(),
        '__import__': DummyObject()
    }
    # Overwrite dummys depending on mode
    if mode == "strict": allowed_globals = {'__builtins__': RaisingDummyObject(), '__import__': RaisingDummyObject()}
    elif mode == "returning": allowed_globals = {'__builtins__': ReturningDummyObject(), '__import__': ReturningDummyObject()}
    #Combine what should be returned with allowed_locals
    allowed_locals = allowed_locals | return_scope
    # Backup previous dictionary
    prev_allowed_locals = allowed_locals.copy()
    # Execute code
    exec(code, allowed_globals, allowed_locals)
    # If Dictionary has changed return any key in return scope
    if str(allowed_locals) != str(prev_allowed_locals) and allowed_locals != None:
        # Retrive keys existing in both dictionaries using two sets
        common_keys = set(allowed_locals.keys()) & set(return_scope.keys())
        # Dictionary Comprehension to return dictionary of all changed keys
        return {key: allowed_locals[key] for key in common_keys}
    # Otherwise return the return scope unchanged
    else:
        return return_scope
    
# [Classes]
# Context-Manager that can restrict the enviroment for calls
class RestrictingContextManager:
    def __init__(self,mode):
        allowedModes = ["restricted","restricted:strict","restricted:returning"]
        if mode.lower() not in allowedModes:
            raise Exception(f"Faulty restriction-mode '{mode.lower()}', use one of '{','.join(allowedModes)}'")
        self.mode = mode
        self.store = {}

    def __enter__(self):
        self.store = {
            "__builtins__": __builtins__,
            "__builtins__.__import__": __builtins__.__import__,
            "__import__": __import__
        }
        toUse = None
        if self.mode.lower() == "restricted":
            toUse = DummyObject()
        elif self.mode.lower() == "restricted:strict":
            toUse = RaisingDummyObject()
        elif self.mode.lower() == "restricted:returning":
            toUse = ReturningDummyObject()
        if toUse != None:
            __builtins__ = toUse
            __builtins__.__import__ = toUse
            __import__ = toUse

    def __exit__(self, exc_type, exc_value, traceback):
        if self.store.get("__builtins__") != None:
            __builtins__ = self.store.get("__builtins__")
        elif self.store.get("__builtins__.__import__"):
            __builtins__.__import__ = self.store.get("__builtins__.__import__")
        elif self.store.get("__import__"):
            __import__ = self.store.get("__import__")

# Context manager working similar to the Restricting one but taking inclusions as a dict
class CustomizableContextManager:
    """
    restMode set to None will turn restriction off.
    """
    def __init__(self,inclusions=None,restMode=None):
        self.allowedRestModes = ["restricted","restricted:strict","restricted:returning"]
        if restMode != None:
            if restMode.lower() not in self.allowedRestModes:
                raise Exception(f"Faulty restriction-mode '{restMode.lower()}', use one of '{','.join(self.allowedRestModes)}'")
        self.restMode = restMode
        self.inclusions = inclusions
        self.store = {}

    def __enter__(self):
        self.store = {
            "__builtins__": __builtins__,
            "__builtins__.__import__": __builtins__.__import__,
            "__import__": __import__
        }
        if self.restMode != None:
            toUse = None
            if self.mode.lower() == "restricted":
                toUse = DummyObject()
            elif self.mode.lower() == "restricted:strict":
                toUse = RaisingDummyObject()
            elif self.mode.lower() == "restricted:returning":
                toUse = ReturningDummyObject()
            if toUse != None:
                __builtins__ = toUse
                __builtins__.__import__ = toUse
                __import__ = toUse
        if self.inclusions not in [None,{}]:
            for k,v in self.inclusions.items():
                setattr(__builtins__,k,v)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.store.get("__builtins__") != None:
            __builtins__ = self.store.get("__builtins__")
        elif self.store.get("__builtins__.__import__"):
            __builtins__.__import__ = self.store.get("__builtins__.__import__")
        elif self.store.get("__import__"):
            __import__ = self.store.get("__import__")
