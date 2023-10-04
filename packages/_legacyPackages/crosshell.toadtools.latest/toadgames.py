import os
import argparse
import time
from cslib.externalLibs.conUtils import pause,clear

parser = argparse.ArgumentParser(description='Toad Games')
parser.add_argument('--cookie', help='Give toad a cookie', action="store_true")
parser.add_argument('--candycane', help='Christmas feeling!', action="store_true")
args = parser.parse_args(argv)

encoding = CS_GetEncoding()

toad = csSession.registry["toadInstance"]

class toadGame():
    def __init__(self,toadInstance,name=str,title=None):
        self.toad = toadInstance
        self.title = None
        self.name = name
        if title != None:
            self.title = title
        else:
            self.title = f"ToadGame: {name}"
    def start(self):
        self.reset()
        self.p(self.title)
    def reset(self):
        self.toad.resOnetime()
        self.toad.resPersMsg()
    def sc(self,msg):
        self.toad.screamToadNow(msg)
    def p(self,msg):
        self.toad.setPersMsg(msg)
        self.sc(msg)
    def pause(self):
        pause()
    def clear(self):
        clear()
    def sleep(self,seconds):
        time.sleep(seconds)

# Cookie
if args.cookie:
    game = os.path.join(CSScriptRoot,".toadgames","cookie.py")
    toadG = toadGame(toad,"Cookie")
    exec(open(game,'r',encoding=encoding).read(),globals())

# Candycane
if args.candycane:
    game = os.path.join(CSScriptRoot,".toadgames","candycane.py")
    toadG = toadGame(toad,"Candycane")
    exec(open(game,'r',encoding=encoding).read(),globals())