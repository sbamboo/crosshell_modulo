import os
import argparse
import time
import random
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
    '''Toadgame main class, (Game-Engine)'''
    def __init__(self,toadInstance,name=str,title=None,prefix=None,noSound=False):
        '''Initializer function.'''
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
        self.bgMusicType = None

    def enablePrefix(self):
        '''Enables the toad-prefix-'''
        self.prefixEnabled = True
    def disablePrefix(self):
        '''Disables the toad-prefix-'''
        self.prefixEnabled = False
    def togglePrefix(self):
        '''Toggles the toad-prefix on/off-'''
        if self.prefixEnabled == True:
            self.prefixEnabled = False
        else:
            self.prefixEnabled = True
    def setBgMusic(self,sound,playType="single"):
        '''
        Sets the background music, that will auto-loop play apon start().
        sound: can be a string filepath to a wav file, or a list of paths.
        playType: (if str-type sound input, playType will alwasy be single)
            single: play the first song in the list.
            single-last: play the last song in the list.
            list: play one after the other.
            list-reverse: same as list but reverse-order.
            random: plays a random song.
        '''
        self.bgMusic = sound
        self.bgMusicType = playType
    def resBgMusic(self):
        '''Resets the background music.'''
        if self.bgMusic != None:
            self.stopSound()
        self.bgMusic = None
        self.bgMusicType = None
    def start(self):
        '''Preps toad for start and starts any defined bg music-'''
        self.started = True
        self.reset(False)
        self.p(self.title)
        if self.bgMusic != None:
            self.playMultiSound(self.bgMusic, self.bgMusicType, True)
    def reset(self,resBGmusic=True):
        '''Post-prepps toad, resets the persistance messages and stops any sounds.'''
        self.toad.resOnetime()
        self.toad.resPersMsg()
        self.stopSound()
        if resBGmusic == True:
            self.resBgMusic()
    def exit(self):
        '''Same as reset() but also exists.'''
        self.reset()
        exit()
    def sc(self,msg):
        '''Sends a message to toad, non-peristant. (Calls screamToadNow)'''
        if self.prefixEnabled:
            self.toad.screamToadNow(msg,self.prefix)
        else:
            self.toad.screamToadNow(msg,"")
    def p(self,msg):
        '''Sends a message to toad, also sets to peristant.'''
        self.toad.setPersMsg(msg)
        self.sc(msg)
    def pause(self):
        '''Alias for conUtils.pause, waits for X input.'''
        pause()
    def clear(self):
        '''Alias for conUtils.clear, clears the terminal.'''
        clear()
    def sleep(self,seconds):
        '''Waits/Sleeps for X seconds (Alias for time.sleep)'''
        time.sleep(seconds)
    # [Sound]
    def playSound(self, wavFilePath, loop=False):
        '''Plays a wavfile sound, also takes bool if should loop.'''
        if self.noSound != True:
            self.soundMap.playSound(wavFilePath,loop)
    def playMultiSound(self, sound, playType="single", loop=False):
        '''
        Plays a sound or multiple of them (a list).
        sound: str or single wavFilePath or list of them.
        playType: (if str-type sound input, playType will alwasy be single)
            single: play the first song in the list.
            single-last: play the last song in the list.
            list: play one after the other.
            list-reverse: same as list but reverse-order.
            random: plays a random song.
        loop: Should it loop? (Only works with playType: single,single-last,random)
        '''
        playType = playType.lower()
        if type(sound) == str:
            playType = "single"
            sound = [sound]
        if playType == "single":
            self.playSound(sound[0],loop)
        if playType == "single-last":
            self.playSound(sound[-1],loop)
        if playType == "random":
            self.playSound(random.choice(sound),loop)
        if playType == "list":
            self.soundMap.playList(sound,loop)
        if playType == "list-reverse":
            self.soundMap.playList(sound[::-1],loop)
    def stopSound(self):
        '''Stops al currently playing sounds from continuing.'''
        self.soundMap.stopAll()
    # [Keyboard]
    def waitForKey(self) -> str:
        '''Waits for a keypress and returns it. (First-indiffrent key, so if last key was y, it won't could until another key was pressed)'''
        return self.keyboard.waitForKey()
    def getLastPress(self) -> str:
        '''Gets the last key pressed.'''
        return self.keyboard.getLastPress()

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