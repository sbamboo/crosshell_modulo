import sys
import subprocess

'''
CSlib: CrosshellModulariyEngine contains crosshells code to allow for modules to replace and/or inject code into crosshell.
'''

class linkedFileModularise():
    def __init__(self,baseFile=None):
        self.base = baseFile
        self.file = self.base
    def execute_internally(self,globals=globals()):
        exec(open(self.file).read(),globals)
    def execute_externally(self,newwindow=False):
        if self.file != None:
            if newwindow == True:
                subprocess.Popen([sys.executable, self.file], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([sys.executable, self.file])
    def exein(self,*args,**kwargs):
        self.execute_internally(*args,**kwargs)
    def exeex(self,*args,**kwargs):
        self.execute_externally(*args,**kwargs)
    def link(self,baseFile):
        self.base = baseFile
        self.file = self.base
    def load(self,replacementFile):
        self.file = replacementFile
    def unload(self):
        self.file = self.base

class linkedFileModulariseId():
    def __init__(self,baseFile=None):
        self.default = baseFile
        self.defid = "Default"
        self.defids = {self.defid:self.default}
        self.ids = self.defids
        self.current = self.defid
    def _getFile(self):
        return self.ids[self.current]
    def execute_internally(self,id=None):
        if id == None:
            file = self._getFile()
        else:
            file = self.ids[id]
        exec(open(file).read())
    def execute_externally(self,newwindow=False,id=None):
        if id == None:
            file = self._getFile()
        else:
            file = self.ids[id]
        if file != None:
            if newwindow == True:
                subprocess.Popen([sys.executable, file], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([sys.executable, file])
    def exein(self,*args,**kwargs):
        self.execute_internally(*args,**kwargs)
    def exeex(self,*args,**kwargs):
        self.execute_externally(*args,**kwargs)
    def link(self,baseFile):
        self.base = baseFile
        self.ids[self.defid] = self.base
    def load(self,id,filepath):
        self.ids[id] = filepath
    def unload(self,id):
        self.ids.pop(id)
    def setdef(self,id):
        self.current = id
    def resdef(self):
        self.current = self.defid
    def resids(self):
        self.ids = self.defids

class linkedFunctionInject():
    def __init__(self,baseFunction=None):
        self.base  = baseFunction
        self.injects = {} # Should contain:  {"<id>":{"mode":"pre","func":<function>}}
    def _wrapper(self,*args, **kwargs):
        result = None
        if len(self.injects.values()) > 0:
            for Inj in self.injects.values():
                if Inj.mode == "pre":
                    Inj.injec()
                if self.base != None: result = self.base(*args, **kwargs)
                if Inj.mode == "post":
                    Inj.injec()
                return result
        else:
            if self.base != None:result = self.base(*args, **kwargs)
            return result
    def link(self,baseFunction):
        self.base = baseFunction
    def inject(self,function,id,mode):
        self.injects[id] = {"mode":mode,"func":function}
    def exject(self,id):
        self.exjects.pop(id)
    def execute(self,*args,**kwargs):
        self._wrapper(*args,**kwargs)