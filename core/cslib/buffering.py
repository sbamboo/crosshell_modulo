import sys

# Custom stdout-buffer class
class BufferedStdout:
    def __init__(self, original_stdout, orgInput=None):
        self.original_stdout = original_stdout
        self.buffer = []
        self.saveToBuffer = True
        self.printToConsole = True
        self.orgInput = orgInput

    def _getBools(self):
        '''returns: (stb,ptc)'''
        return self.saveToBuffer,self.printToConsole
    
    def _setBools(self,stb=None,ptc=None):
        '''takes stb,ptc'''
        if stb != None and type(stb) == bool:
            self.saveToBuffer = stb
        if ptc != None and type(ptc) == bool:
            self.printToConsole = ptc

    def write(self, text):
        # add to buffer
        if self.saveToBuffer != False:
            self.buffer.append(text)
        # original write
        if self.printToConsole != False:
            self.original_stdout.write(text)

    def flush(self):
        self.original_stdout.flush()

    def safe_input(self, prompt=None):
        if prompt == None:
            prompt = ""
        old_stb, old_ptc = self._getBools()      # get old
        self._setBools(stb=False,ptc=True)       # set new
        out = self.orgInput(prompt)
        self._setBools(stb=old_stb,ptc=old_ptc) # set new
        return out
        
    def getBuffer(self):
        toret = []
        for line in self.buffer:
            if line != "\n" and line != None and line != "None":
                line = line.replace("\r\n","\n")
                toret.append(line)
        return toret
    
    def clearBuffer(self):
        self.buffer = []

    def getBufferS(self):
        lst = self.getBuffer()
        st = '\n'.join(lst)
        return st.strip("\n")

    def bwrite(self,text):
        '''buffer-only write'''
        self.buffer.append(text)
    
    def cwrite(self,text):
        '''console-only write'''
        self.original_stdout.write(text)