class ExecutingDummyObject:
    '''CSlib.externalLibs.LimitExec: Dummy object.'''
    def __init__(self,method=None):
        self.method = method
    # Subscribable
    def __getitem__(self, key):
        return ExecutingDummyObject(self.method)
    # Callable
    def __call__(self, *args, **kwargs):
        if self.method != None:
            self.method()


class ctx():
    def __init__(self,globalData={},restrict=None):
        self.restrict = restrict
        self.globalData = globalData
        self.oldGlobals = None

        self.oldImport = None
    
    def __enter__(self):
        # regular
        self.oldGlobals = globals().copy()
        for k in self.oldGlobals.keys():
            del globals()[k]
        for k,v in self.globalData.items():
            globals()[k] = v
        # restrict?
        if self.restrict != None:
            import builtins
            self.oldImport = builtins.__import__
            builtins.__import__ = self.restrict

    def __exit__(self, exc_type, exc_value, traceback):
        # regular
        for k in self.globalData.keys():
            del globals()[k]
        for k,v in self.oldGlobals.items():
            globals()[k] = v
        # restrict?
        if self.restrict != None:
            import builtins
            builtins.__import__ = self.oldImport


def call():
    print("CATCHED!")

with ctx( restrict=ExecutingDummyObject(call) ):
    import os