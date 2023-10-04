# [Imports]
import re,os
from .smartInput import update_bottom_toolbar_message

# [Main]
class toad():
    def __init__(self,csSession,sInputInstance=None,prefix=None):
        self.csSession = csSession
        if sInputInstance != None:
            self.sInputInstance = sInputInstance
        else:
            self.sInputInstance = None
        if prefix == None:
            self.prefix = self._getDefPref()
        else:
            self.prefix = prefix
        self.persMsg = None
        self.onetime = None
        self.no_si_hasUpdt = False
        self.no_si_showToad = False

    def link_sInput(self,sInputInstance):
        self.sInputInstance = sInputInstance

    def _getDefPref(self):
        return "\033[48;2;218;112;214m 🐸Toad:\033[0m "
    
    def setPersMsg(self, msg):
        self.persMsg = msg

    def resPersMsg(self):
        self.persMsg = None

    def setOnetime(self,msg):
        self.onetime = msg
    
    def resOnetime(self):
        self.onetime = None

    def sayToad(self,msg,ovPrefix=None):
        '''Function to add the toad prefix to any message'''
        if "hidden:" in msg:
            return msg.replace("hidden:","")
        else:
            pref = self.prefix
            if ovPrefix != None:
                pref = ovPrefix
            return pref + msg

    def getToadPrefNF(self):
        ansi_escape_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape_pattern.sub("",self.prefix)

    def getToadPrefLen(self):
        return len(self.getToadPrefNF())
    
    def getToadMaxMsgLen(self):
        return os.get_terminal_size().columns - self.getToadPrefLen() -2

    def screamToadNow(self,msg,ovPrefix=None):
        if self.sInputInstance == None:
            self.no_si_hasUpdt = True
        msg = self.sayToad(msg,ovPrefix)
        printer = None
        buffer = self.csSession.tmpGet("buffer")
        if buffer != None:
            printer = buffer.cwrite
        pSession = None
        if self.sInputInstance != None:
            pSession = self.sInputInstance
        seti = self.csSession.data["set"].getModule("crsh")
        update_bottom_toolbar_message(pSession,seti,msg,printer)

    def screamToad(self,msg,ovPrefix=None):
        if self.sInputInstance == None:
            self.no_si_hasUpdt = True
        msg = self.sayToad(msg,ovPrefix)
        pSession = None
        if self.sInputInstance != None:
            pSession = self.sInputInstance
        seti = self.csSession.data["set"].getModule("crsh")
        update_bottom_toolbar_message(pSession,seti,msg)

    def getRollingToad(self):
        '''Function to get the language-based rolling toad msg'''
        return self.sayToad(self.csSession.deb.get("lng:cs.console.toad.message._rolling_","msg",noPrefix=True))

    def getToadMsg(self,lessThenOnetimePrioMsg=None,scream=False):
        '''Function to get toad msg.'''
        stdMsg = self.getRollingToad()
        msg = stdMsg
        onetime = self.onetime
        nonAllowed = ["","STDTITLE","stdtitle",None,"none","None","Null","null","toadstd","toad:"]
        if lessThenOnetimePrioMsg != None and lessThenOnetimePrioMsg not in nonAllowed:
            msg = lessThenOnetimePrioMsg
        if onetime not in nonAllowed:
            msg = onetime
            self.resOnetime()
        if self.persMsg != None:
            msg = self.persMsg
        if msg != stdMsg:
            msg = self.sayToad(msg)
        if scream == True:
            self.screamToadNow(msg)
        return msg
    
    def showToad(self):
        self.screamToadNow(self.getToadMsg(),"")

    def updNoSIToad(self):
        if self.sInputInstance == None:
            self.no_si_hasUpdt = True
            self.showToad()

    def remNoSIToad(self):
        if self.no_si_showToad == False and self.no_si_hasUpdt == True and self.persMsg == None:
            self.no_si_hasUpdt = False
            seti = self.csSession.data["set"].getModule("crsh")
            update_bottom_toolbar_message(None,seti," "*self.getToadMaxMsgLen(),noformat=True)

    def hideNoSIToad(self):
        self.no_si_showToad = False
        self.remNoSIToad()

    def showNoSIToad(self):
        self.no_si_showToad = True
        self.showToad()

    def timedMsg(self,msg,seconds): 
        import threading
        import time
        def timed_toad_msg(seconds,msg,toad):
            toad.setOnetime(f"{msg}")
            toad.setPersMsg(f"{msg}")
            toad.showToad()
            time.sleep(float(seconds))
            toad.resPersMsg()
            if toad.no_si_showToad != False:
                toad.screamToadNow(toad.getToadMsg(),"")
            else:
                toad.remNoSIToad()
        toad_thread = threading.Thread(target=timed_toad_msg,args=(seconds,msg,self))
        toad_thread.start()

    def timedMsgNu(self,msg,seconds): 
        import threading
        import time
        def timed_toad_msg(seconds,msg,toad):
            toad.setOnetime(f"{msg}")
            toad.setPersMsg(f"{msg}")
            time.sleep(float(seconds))
            toad.resPersMsg()
            if toad.no_si_showToad != False:
                toad.screamToadNow(toad.getToadMsg(),"")
            else:
                toad.remNoSIToad()
        toad_thread = threading.Thread(target=timed_toad_msg,args=(seconds,msg,self))
        toad_thread.start()