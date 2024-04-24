# Custom stdout-buffer class
class BufferedStdout:
    """Crosshells main buffer-collector, working as an inplace sys.stdout that also saves the content.
    Note on it's reliance on sys.stdout in the backend, more or less just wrapps it."""
    # Usage: sys.stdout, input
    def __init__(self, original_stdout, orgInput=None):
        self.original_stdout = original_stdout
        self.buffer = []
        self.saveToBuffer = True
        self.printToConsole = True
        self.orgInput = orgInput

    def _getBools(self):
        """
        Function to get the current set boolean values for:
          stb: saveToBuffer
          ptc: printToConsole
        returns: (stb,ptc)
        """
        return self.saveToBuffer,self.printToConsole
    
    def _setBools(self,stb=None,ptc=None):
        """
        Function to set the boolean values for:
          stb: saveToBuffer
          ptc: printToConsole
        takes: stb,ptc
        """
        if stb != None and type(stb) == bool:
            self.saveToBuffer = stb
        if ptc != None and type(ptc) == bool:
            self.printToConsole = ptc

    def write(self, text):
        """
        Writes some text-input to the buffer and console.
        (depending on the current boolean settings, see `._getBools()`)
        """
        # add to buffer
        if self.saveToBuffer != False:
            self.buffer.append(text)
        # original write
        if self.printToConsole != False:
            self.original_stdout.write(text)

    def flush(self):
        """
        Calls flush on the backend sys.stdout.
        """
        self.original_stdout.flush()

    def safe_input(self, prompt=None) -> str:
        """
        Alternative to input() that still shows in console whilst not being collected to the buffer.
        """
        if prompt == None:
            prompt = ""
        old_stb, old_ptc = self._getBools()      # get old
        self._setBools(stb=False,ptc=True)       # set new
        out = self.orgInput(prompt)
        self._setBools(stb=old_stb,ptc=old_ptc) # set new
        return out

    def getBuffer(self) -> list:
        """
        Function to get the buffer content as a list split by newlines.
        (Ignoring `None` entries and entries consisting of just a newline)
        Also normalizes `\\r\\n` to `\\n`
        """
        toret = []
        for line in self.buffer:
            if line != "\n" and line != None and line != "None":
                line = line.replace("\r\n","\n")
                toret.append(line)
        return toret
    
    def getBufferRaw(self) -> list:
        """
        Returns the buffer content without any parsing or stitching.
        """
        return self.buffer
    
    def clearBuffer(self):
        """
        Clears the buffer content by reseting it.
        """
        self.buffer = []

    def getBufferS(self):
        """
        Function to get the buffer as a `\\n` joined string.
        """
        lst = self.getBuffer()
        st = '\n'.join(lst)
        return st.strip("\n")

    def bwrite(self,text,end=None):
        """
        Function to only write to the buffer, not the console.
        (Appends to buffer content)
        """
        if end != None: text += end
        self.buffer.append(text)
    
    def cwrite(self,text,end=None):
        """
        Function to only write to the console, not the buffer.
        (Pushes to sys.stdout)
        """
        if end != None: text += end
        self.original_stdout.write(text)

    def cwrite_adv(self, text=str, end=None):
        """
        Function to only write to the console, not the buffer.
        (Uses a call to `print()` after updating the boolean vars.)
        """
        old_stb, old_ptc = self._getBools()      # get old
        self._setBools(stb=False,ptc=True)       # set new
        out = print(text,end=end)
        self._setBools(stb=old_stb,ptc=old_ptc) # set new
        return out

    def bwrite_autoNL(self,text=str,end="\n"):
        """
        Same as `.bwrite` but assuming and "end" of `\\n`
        """
        self.bwrite(text,end)
        
    def cwrite_autoNL(self,text=str,end="\n"):
        """
        Same as `.cwrite` but assuming and "end" of `\\n`
        """
        self.cwrite(text,end)