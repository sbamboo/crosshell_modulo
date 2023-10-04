import threading

from cslib import autopipImport

readchar = autopipImport("readchar")

def get_keypress():
    return readchar.readchar().lower()

class Keyboard():
    def __init__(self,mappings=None) -> None:
        self.mappings = None
        if mappings != None:
            self.mappings = mappings
        self.recorded = []
        self.recoding = False
        self.recordThread = None

    def loadMappings(self,mappings):
        self.mappings = mappings

    def getLastPress(self):
        lastPress = get_keypress()
        if self.mappings != None:
            return self.mappings[lastPress]
        else:
            return lastPress
        
    def _recorder(self):
        while self.recording == True:
            lp = self.getLastPress()
            if self.recorded[-1] != lp:
                self.recorded.append(lp)

    def record(self):
        self.recordThread = threading.Thread(target=self._recorder)
        self.recordThread.start()

    def endrecord(self) -> list:
        self.recoding = False
        self.recordThread.join(1)
        self.recordThread = None
        record = self.recorded
        self.recorded = []
        return record

    def waitForKey(self):
        lkp = None
        while True:
            lk = self.getLastPress()
            if lk != lkp:
                return lk