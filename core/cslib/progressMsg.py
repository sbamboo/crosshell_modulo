import os
import re

def removeAnsiSequences(inputString):
    '''CSlib.CGTS: Strips ansi sequences from a string.'''
    # Define a regular expression pattern to match ANSI escape sequences
    ansiPattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    # Use re.sub to replace ANSI sequences with an empty string
    cleanedString = ansiPattern.sub('', inputString)
    return cleanedString

class progressBar():
    def __init__(self,length=10,start=0,stripAnsi=False,style=None):
        if style == None:
            #self.style = {"start":"", "fill_done":"\033[38;2;12;10;127m█", "fill":"\033[38;2;6;10;77m█", "end":""}
            self.style = {"start":"", "fill_done":"\033[48;2;31;10;41m\033[38;2;92;30;122m▓", "fill":"\033[38;2;31;10;41m█", "end":""}
        else:
            self.style = style
        self.length = length
        self.start = start
        self.current = start
        self.stripAnsi = stripAnsi
    def get(self):
        string = self.style["start"]
        string += self.style["fill_done"]*(self.current)
        string += self.style["fill"]*(self.length-self.current)
        string += "\033[0m"
        string += self.style["end"]
        if self.stripAnsi == True:
            return removeAnsiSequences(string)
        else:
            string += "\033[0m"
            return string
    def print(self):
        print(self.get())
    def draw(self,x,y):
        print(f"\033[{y};{x}H{self.get()}")
    def incr(self,x=1):
        self.current += x
    def decr(self,x=1):
        self.current -= x
    def setL(self,length=int):
        self.length = length
    def setC(self,current=int):
        self.current = current
    def setS(self,start=int):
        self.start = start
    def rese(self):
        self.current = 0
    def defa(self):
        self.current = self.start
    def styl(self,style=dict):
        self.style = style
    def sSta(self,style_start=str):
        self.style["start"] = style_start
    def sDon(self,style_done=str):
        self.style["fill_done"] = style_done
    def sFill(self,style_fill=str):
        self.style["fill"] = style_fill
    def sEnd(self,style_end=str):
        self.style["end"] = style_end
    def isDo(self):
        return self.current >= self.length

class startupMessagingWProgress():
    def __init__(self,enabled=True,stripAnsi=False,debugger=None,pgMax=30,pgIncr=1):
        self.enabled = enabled
        self.stripAnsi = stripAnsi
        self.debugger = debugger
        if self.debugger == None:
            self.debugger = crosshellDebugger()
        self.pgMax = pgMax
        self.pgIncr = pgIncr
        self.pg = progressBar(pgMax,stripAnsi=stripAnsi)
    def verb(self,text,l=None,scope="info",ct={},noPrefix=False):
        '''l: langID'''
        if self.enabled != True:
            return
        if self.stripAnsi == False: print("\033[s", end="")
        if self.pg.isDo() == True:
            self.pg.rese()
        else:
            self.pg.print()
            self.pg.incr(self.pgIncr)
        if self.debugger.scope == self.debugger.defScope:
            scope = self.debugger.defScope
        w,_ = os.get_terminal_size()
        if l != None:
            if self.debugger.languageProvider != None:
                txt = self.debugger.get(f"lng:{l},txt:{text}",onScope=scope,ct=ct,noPrefix=noPrefix)
                if self.stripAnsi == False: txt = txt + (" "*(w-len(txt)))
                print(txt)
            else:
                txt = self.debugger.get(text,onScope=scope,ct=ct,noPrefix=noPrefix)
                if self.stripAnsi == False: txt = txt + (" "*(w-len(txt)))
                print(txt)
        else:
            txt = self.debugger.get(text,onScope=scope,ct=ct,noPrefix=noPrefix)
            if self.stripAnsi == False: txt = txt + (" "*(w-len(txt)))
            print(txt)
        if self.stripAnsi == False: print("\033[u", end="")
    def clr(self):
        if self.stripAnsi == False: 
            w,_ = os.get_terminal_size()
            print(" "*w)
            print(" "*w)
            print("\033[u", end="")