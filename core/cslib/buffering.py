import sys

class BufferedStdout:
    def __init__(self, original_stdout, orgInput=None):
        self.original_stdout = original_stdout
        self.buffer = []
        self.saveToBuffer = True
        self.printToConsole = True
        self.orgInput = orgInput

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
        old_stb = self.saveToBuffer
        old_ptc = self.printToConsole
        self.saveToBuffer = False
        self.printToConsole = True
        out = self.orgInput(prompt)
        self.saveToBuffer = old_stb
        self.printToConsole = old_ptc
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
