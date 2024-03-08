import os
import re
import platform

from cslib.externalLibs.conUtils import getConSize
from cslib._crosshellParsingEngine import removeAnsiSequences

class progressBar():
    def __init__(self,length=10,start=0,stripAnsi=False,style=None,unicodeSymbols=True):
        if style == None:
            #self.style = {"start":"", "fill_done":"\033[38;2;12;10;127m█", "fill":"\033[38;2;6;10;77m█", "end":""}
            if unicodeSymbols == True:
                self.style = {"start":"", "fill_done":"\033[48;2;31;10;41m\033[38;2;92;30;122m▓", "fill":"\033[38;2;31;10;41m█", "end":""}
            else:
                self.style = {"start":"[", "fill_done":"\033[48;2;31;10;41m\033[38;2;92;30;122m#", "fill":"\033[38;2;31;10;41m ", "end":"]"}
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
    def _fixcp1252_auto(self,string):
        if platform.system() == "Windows":
            string_e = string.encode('cp1252', 'replace')
            string = string_e.decode('cp1252')
        else:
            string_e = string.encode('utf-8', 'replace')
            string = string_e.decode('utf-8')
        return string
    def _print_fixcp1252_auto(self,string):
        try:
            print(string)
        except UnicodeEncodeError:
            string = self._fixcp1252_auto(string)
            print(string)
    def print(self):
        self._print_fixcp1252_auto(self.get())
    def draw(self,x,y):
        self._print_fixcp1252_auto(f"\033[{y};{x}H{self.get()}")
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
    def __init__(self,debugger,enabled=True,stripAnsi=False,pgMax=30,pgIncr=1,unicodeSymbols=True):
        self.enabled = enabled
        self.stripAnsi = stripAnsi
        self.debugger = debugger
        self.pgMax = pgMax
        self.pgIncr = pgIncr
        self.pg = progressBar(pgMax,stripAnsi=stripAnsi,unicodeSymbols=unicodeSymbols)
    def _print(self,text):
        if self.stripAnsi == True:
            print( removeAnsiSequences(text) )
        else:
            print( text )
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
        w,_ = getConSize()
        if l != None:
            if self.debugger.languageProvider != None:
                txt = self.debugger.get(f"lng:{l},txt:{text}",onScope=scope,ct=ct,noPrefix=noPrefix)
                if self.stripAnsi == False: txt = txt + (" "*(w-len(txt)))
                self._print(txt)
            else:
                txt = self.debugger.get(text,onScope=scope,ct=ct,noPrefix=noPrefix)
                if self.stripAnsi == False: txt = txt + (" "*(w-len(txt)))
                self._print(txt)
        else:
            txt = self.debugger.get(text,onScope=scope,ct=ct,noPrefix=noPrefix)
            if self.stripAnsi == False: txt = txt + (" "*(w-len(txt)))
            self._print(txt)
        if self.stripAnsi == False: print("\033[u", end="")
    def clr(self):
        if self.stripAnsi == False: 
            w,_ = getConSize()
            print(" "*w)
            print(" "*w)
            print("\033[u", end="")