import re
from cslib.externalLibs.filesys import filesys

def exclude_nonToFormat(input_string):
    # Find all substrings inside innermost double slashes
    pattern = r'//([^/]+)//'
    matches = re.findall(pattern, input_string)

    if not matches:
        # If no innermost double slashes found, return the input string as is
        return (input_string, [])

    # Replace all innermost double slashes with §cs.toNotFormat§
    replaced_string = re.sub(pattern, '§cs.toNotFormat§', input_string)

    return (replaced_string, matches)


def include_nonToFormat(input_string, substrings):
    for substring in substrings:
        # Remove // from the beginning and end of the substring
        clean_substring = substring.strip('/')
        # Replace "§cs.toNotFormat§" with the cleaned substring
        input_string = input_string.replace("§cs.toNotFormat§", clean_substring, 1)
    return input_string

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
        self.idef = "substituion"
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
    def evalData(self,data,extraSubstTags=None):
        _type = type(data)
        if _type == str:
            return self.eval(data,extraSubstTags)
        elif _type == dict:
            for k,v in data.items():
                k = self.eval(k,extraSubstTags)
                data[k] = self.evalData(v,extraSubstTags)
            return data
        elif _type == list or _type == tuple:
            for i,v in enumerate(data):
                data[i] = self.evalData(v,extraSubstTags)
            return data
        else:
            return data

class pathTagManager(tagSubstitionManager):
    def __init__(self,defaultSubsttags=dict):
        super().__init__(defaultSubsttags)
        self.evalFailMsg = "If defined, extraPathTags must be of type dict!"
        self.idef = "pathtag"
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
        self.idef = "collection"
    def _checkMode(self,mode):
        coal = []
        for p in self.modes.values(): coal.extend(p)
        if mode.lower() not in coal:
            raise Exception(f"Invalid mode, must be one of: {coal} (Given: {mode.lower()})")
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
    def evalData(self,mode,data,extraSubstTags=None):
        return self._a(mode).evalData(data,extraSubstTags)
    
    def getAlTags(self):
        _t = self.getTags("ptm")
        _v = self.getTags("stm")
        if _v != None:
            _t.update(_v)
        return _t
    
    def evalAl(self,string,extraSubstTags=None):
        string = self.eval("stm",string,extraSubstTags)
        return self.eval("ptm",string,extraSubstTags)

    def evalDataAl(self,data,extraSubstTags=None):
        data = self.evalData("stm",data,extraSubstTags)
        return self.evalData("ptm",data,extraSubstTags)

def removeAnsiSequences(inputString):
    '''CSlib.CGTS: Strips ansi sequences from a string.'''
    inputString = inputString.replace('',"\x1B")
    # Define a regular expression pattern to match ANSI escape sequences
    ansiPattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    # Use re.sub to replace ANSI sequences with an empty string
    cleanedString = ansiPattern.sub('', inputString)
    return cleanedString

def splitStringBySpaces(inputString, sp=" ", q1='"', q2="'") -> list:
    '''CSlib.CSPE: Function to split a string by spaces not inside quotes.'''
    substrings = []
    currentSubstring = []
    insideQuotes = False
    quoteChar = None
    for char in inputString:
        if char == sp and not insideQuotes:
            # If we encounter a space and we're not inside quotes, consider it as a delimiter
            if currentSubstring:
                substrings.append(''.join(currentSubstring))
                currentSubstring = []
        elif char in (q1, q2) and not insideQuotes:
            # Toggle the insideQuotes flag and set the quoteChar when encountering a quote
            insideQuotes = True
            quoteChar = char
            currentSubstring.append(char)  # Include the quote character in the substring
        elif char == quoteChar and insideQuotes:
            # End of quote, toggle insideQuotes off
            insideQuotes = False
            quoteChar = None
            currentSubstring.append(char)  # Include the quote character in the substring
        else:
            # Add the character to the current substring
            currentSubstring.append(char)
    # Add the last substring if it exists
    if currentSubstring:
        substrings.append(''.join(currentSubstring))
    return substrings

def splitByDelimiters(inputString, delimiters):
    '''CSlib.CSPE: Split a string by multiple delimiters.
    Split the input string by any of the specified delimiters.

    Args:
    input_string (str): The string to be split.
    delimiters (list): A list of delimiter strings.

    Returns:
    list: A list of substrings obtained by splitting the input string by any of the delimiters.
    '''
    substrings = [inputString]
    for delimiter in delimiters:
        newSubstrings = []
        for substring in substrings:
            newSubstrings.extend(substring.split(delimiter))
        substrings = newSubstrings
    return substrings