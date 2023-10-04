import os
import argparse
import time
from cslib.externalLibs.conUtils import pause,clear
from cslib import fromPath

parser = argparse.ArgumentParser(prog="toadgames.py",description='Toad Games')
parser.add_argument('--cookie', help='Give toad a cookie.', action="store_true")
parser.add_argument('--candycane', help='Christmas feeling!', action="store_true")
parser.add_argument('--walk', help='Take toad out for a walk.', action="store_true")
parser.add_argument('--nosound', help='Silence to the toad.', action="store_true")
parser.add_argument('game_args', nargs=argparse.REMAINDER, help='Arguments to be passed to the game.')
args = parser.parse_args(argv)

encoding = CS_GetEncoding()

toad = csSession.registry["toadInstance"]

soundMap = fromPath(os.path.join(CSScriptRoot,".soundMap.py"))
keyboard = fromPath(os.path.join(CSScriptRoot,".keyboard.py"))

class toadGame():
    def __init__(self,toadInstance,name=str,title=None,prefix=None,noSound=False):
        self.toad = toadInstance
        self.title = None
        self.name = name
        self.started = False
        self.noSound = noSound
        if title != None:
            self.title = title
        else:
            self.title = f"ToadGame: {name}"
        self.prefix = toad.prefix
        if prefix != None:
            self.prefix = prefix
        self.prefixEnabled = True
        self.soundMap = soundMap.SoundMap()
        self.keyboard = keyboard.Keyboard()
        self.bgMusic = None
    def enablePrefix(self):
        self.prefixEnabled = True
    def disablePrefix(self):
        self.prefixEnabled = False
    def togglePrefix(self):
        if self.prefixEnabled == True:
            self.prefixEnabled = False
        else:
            self.prefixEnabled = True
    def setBgMusic(self,wavFilePath):
        self.bgMusic = wavFilePath
    def resBgMusic(self):
        if self.bgMusic != None:
            self.stopSound()
        self.bgMusic = None
    def start(self):
        self.started = True
        self.reset(False)
        self.p(self.title)
        if self.bgMusic != None:
            self.playSound(self.bgMusic, True)
    def reset(self,resBGmusic=True):
        self.toad.resOnetime()
        self.toad.resPersMsg()
        self.stopSound()
        if resBGmusic == True:
            self.resBgMusic()
    def exit(self):
        self.reset()
        exit()
    def sc(self,msg):
        if self.prefixEnabled:
            self.toad.screamToadNow(msg,self.prefix)
        else:
            self.toad.screamToadNow(msg,"")
    def p(self,msg):
        self.toad.setPersMsg(msg)
        self.sc(msg)
    def pause(self):
        pause()
    def clear(self):
        clear()
    def sleep(self,seconds):
        time.sleep(seconds)

    def playSound(self, wavFilePath, loop=False):
        if self.noSound != True:
            self.soundMap.playSound(wavFilePath,loop)
    def stopSound(self):
        self.soundMap.stopAll()

globs = globals()
globs["argv"] = args.game_args

# Cookie
if args.cookie:
    game = os.path.join(CSScriptRoot,".toadgames","cookie","main.py")
    globs["__file__"] = game
    toadG = toadGame(toad,"Cookie",noSound=args.nosound)
    exec(open(game,'r',encoding=encoding).read(),globs)

# Candycane
if args.candycane:
    game = os.path.join(CSScriptRoot,".toadgames","candycane","main.py")
    globs["__file__"] = game
    toadG = toadGame(toad,"Candycane",noSound=args.nosound)
    exec(open(game,'r',encoding=encoding).read(),globs)

# Walk
if args.walk:
    game = os.path.join(CSScriptRoot,".toadgames","walk","main.py")
    globs["__file__"] = game
    toadG = toadGame(toad,"Walk",noSound=args.nosound)
    exec(open(game,'r',encoding=encoding).read(),globs)