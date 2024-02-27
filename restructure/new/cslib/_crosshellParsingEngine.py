from cslib.externalLibs.filesys import filesys

def tagSubstition_parse(string,toParse=dict) -> str:
    """CSlib.CSPE: Function to parse only a given set of tags, once!"""
    for tagName,tagValue in toParse.items():
        tagString = '{' + tagName + '}'
        string = string.replace(tagString,tagValue)
    return string

def tagSubstition_parseDict(_dict,toParse=dict) -> dict:
    """CSlib.CSPE: Function to parse only a given set of tags, once! (dict)"""
    for key,val in _dict.items():
        if type(val) == str:
            _dict[key] = tagSubstition_parse(val,toParse)
        else:
            _dict[key] = tagSubstition_parseDict(val,toParse)
    return _dict

class tagSubstitionManager():
    '''CSlib.CSPE: TagSubstitionManager class'''
    def __init__(self,defaultSubsttags={}):
        self.defSubsttags = defaultSubsttags
        self.substTags = self.defSubsttags.copy()
        self.evalFailMsg = "If defined, extraSubstTags must be of type dict!"
    def addTag(self,tag,value):
        self.substTags[tag] = value
    def remTag(self,tag):
        if self.substTags.get(tag) != None:
            self.substTags.pop(tag)
    def getTag(self,tag=None):
        if tag == None:
            return self.substTags
        else:
            return self.substTags[tag]
    def getTags(self):
        return self.substTags
    def updateTag(self,tagDict=dict):
        self.substTags.update(tagDict)
    def eval(self,string,extraSubstTags=None) -> str:
        toParse = self.substTags.copy()
        if extraSubstTags != None:
            if type(extraSubstTags) != dict:
                raise Exception(self.evalFailMsg)
            toParse.update(extraSubstTags)
        return tagSubstition_parse(string,toParse)

class pathTagManager(tagSubstitionManager):
    def __init__(self,defaultSubsttags=dict):
        super().__init__(defaultSubsttags)
        self.evalFailMsg = "If defined, extraPathTags must be of type dict!"
    def ensureAl(self):
        for _,tagValue in self.substTags.items():
            if filesys.notExist(tagValue) == True:
                    filesys.ensureDirPath(tagValue)

class collectionalTagManager():
    def __init__(self,pathtags={},substtags={}):
        self.stm = tagSubstitionManager(substtags)
        self.ptm = pathTagManager(pathtags)
        self.modes = {
            "stm": ["stm","sub"],
            "ptm": ["ptm","path"]
        }
    def _checkMode(self,mode):
        coal = []
        for p in self.modes.values(): coal.extend(p)
        if mode.lower() not in self.modes:
            raise Exception(f"Invalid mode, must be one of: {coal}")
        for k,v in self.modes.items():
            if mode.lower() in v:
                return k
        else:
            raise Exception(f"Invalid mode, must be one of: {coal}")
    def _a(self,mode):
        mode = self._checkMode(mode)
        if mode == "ptm":
            return self.ptm
        elif mode == "stm":
            return self.stm
    def addTag(self,mode,tag):
        self._a(mode).addTag(tag)
    def remTag(self,mode,tag):
        self._a(mode).remTag(tag)
    def getTag(self,mode,tag=None):
        return self._a(mode).getTag(tag)
    def getTags(self,mode):
        return self._a(mode).getTags()
    def updateTag(self,mode,tagDict=dict):
        self._a(mode).updateTag(tagDict)
    def eval(self,mode,string,extraSubstTags=None):
        return self._a(mode).eval(string,extraSubstTags)
    
    def getAlTags(self):
        _t = self.getTags("ptm")
        _v = self.getTags("stm")
        if _v != None:
            _t.update(_v)
        return _t