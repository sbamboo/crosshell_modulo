# Palette Formats:
# Hex Foreground:   "f#<hex>"
# Hex Background:   "b#<hex>"
# RGB Foreground:   "f@<R>;<G>;<B>"
# RGB Background:   "b@<R>;<G>;<B>"
# ANSI:             "<ansicode>" EXCLUDING m
# Webcolor Fground: "f:<colorName>" IF ENABLED
# Webcolor Bground: "b:<colorName>" IF ENABLED

'''
CSlib: CrosshellGlobalTextSystem containes code for parsing and handling text
'''

import re

from .externalLibs.stringTags import formatStringTags
from .cslib import intpip

standardHexPalette = {
    # Text colors (normal intensity)
    "30": "f#000000",  # Black
    "31": "f#FF0000",  # Red
    "32": "f#00FF00",  # Green
    "33": "f#FFFF00",  # Yellow
    "34": "f#0000FF",  # Blue
    "35": "f#FF00FF",  # Magenta
    "36": "f#00FFFF",  # Cyan
    "37": "f#FFFFFF",  # White
    # Text colors (bright intensity)
    "90": "f#555555",  # Black
    "91": "f#FF5555",  # Red
    "92": "f#55FF55",  # Green
    "93": "f#FFFF55",  # Yellow
    "94": "f#5555FF",  # Blue
    "95": "f#FF55FF",  # Magenta
    "96": "f#55FFFF",  # Cyan
    "97": "f#FFFFFF",  # White
    # Background colors (normal intensity)
    "40": "b#000000",  # Black
    "41": "b#FF0000",  # Red
    "42": "b#00FF00",  # Green
    "43": "b#FFFF00",  # Yellow
    "44": "b#0000FF",  # Blue
    "45": "b#FF00FF",  # Magenta
    "46": "b#00FFFF",  # Cyan
    "47": "b#FFFFFF",  # White
    # Background colors (bright intensity)
    "100": "b#555555",  # Black
    "101": "b#FF5555",  # Red
    "102": "b#55FF55",  # Green
    "103": "b#FFFF55",  # Yellow
    "104": "b#5555FF",  # Blue
    "105": "b#FF55FF",  # Magenta
    "106": "b#55FFFF",  # Cyan
    "107": "b#FFFFFF",  # White
}

def parsePalettedColor(key,palette,paletteMode,parseWebcolor=True,safeParseWebcolorWhenDisabled=True,returnWithEsc=False):
    if palette.get(key) == None:
        if "&" in key:
            key = _multipleAnsiKeyWrapper(key, palette, paletteMode,parseWebcolor, safeParseWebcolorWhenDisabled,returnWithEsc)
        if returnWithEsc == True:
            return f"\033[{key}m"
        else:
            return key
    else:
        # ansi
        if paletteMode.lower() == "ansi":
            return f"\033[{palette[key]}m"
        else:
            # Hex / RGB / Webcolor
            ## foreground or background?
            value = palette[key]
            if value[0] == "f":
                background = False
                value = value.lstrip("f")
            elif value[0] == "b":
                background = True
                value = value.lstrip("b")
            # Hex
            if value[0] == "#":
                value = value.lstrip("#")
                lv = len(value) # lv: LengthOfValue
                r,g,b = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
                return '\033[{};2;{};{};{}m'.format(48 if background else 38, r, g, b)
            # RGB
            elif value[0] == "@":
                value = value.lstrip("@")
                r,g,b = value.split(";")
                return '\033[{};2;{};{};{}m'.format(48 if background else 38, r, g, b)
            # Webcolor
            elif parseWebcolor == True:
                try:
                    import webcolors
                except:
                    intpip("install webcolors")
                    import webcolors
                value = value.lstrip(":")
                r,g,b = webcolors.name_to_rgb(value)
                return '\033[{};2;{};{};{}m'.format(48 if background else 38, r, g, b)
            # Return
            else:
                if safeParseWebcolorWhenDisabled == True:
                    try:
                        int(value)
                        return value
                    except:
                        return key
                else:
                    return value

def _multipleAnsiKeyWrapper(key,palette,paletteMode,parseWebcolor=True,safeParseWebcolorWhenDisabled=True,returnWithEsc=False):
    keyList = key.split("&")
    parsedString = ""
    for k in keyList:
        parsedString += parsePalettedColor(k,palette,paletteMode,parseWebcolor,safeParseWebcolorWhenDisabled,returnWithEsc)
    if parsedString == key.replace("&",""):
        parsedString = f"\033[{key}m"
    return parsedString

def _getWebcolorMappings():
    try:
        import webcolors
    except:
        intpip("install webcolors")
        import webcolors
    colorMapping = {}
    for color,_hex in webcolors.CSS3_NAMES_TO_HEX.items():
        _hex = _hex.lstrip("#")
        lv = len(_hex)
        r,g,b = tuple(int(_hex[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
        colorMapping[f"f:{color}"] = '\033[{};2;{};{};{}m'.format(38, r, g, b)
        colorMapping[f"b:{color}"] = '\033[{};2;{};{};{}m'.format(48, r, g, b)
    return colorMapping

class crosshellGlobalTextSystem():
    '''CSlib.CGTS: Main formatter function taking text, parameters and then continuing
    Palette Formats:
      Hex Foreground:   "f#<hex>"
      Hex Background:   "b#<hex>"
      RGB Foreground:   "f@<R>;<G>;<B>"
      RGB Background:   "b@<R>;<G>;<B>"
      ANSI:             "<ansicode>" EXCLUDING m
      Webcolor Fground: "f:<colorName>" IF ENABLED
      Webcolor Bground: "b:<colorName>" IF ENABLED
    '''
    def __init__(self,pathtagInstance=None,palette=standardHexPalette,paletteMode="hex",stripAnsi=False,allowedVariables=None,customTags=None,parseWebcolor=True,safeParseWebcolorWhenDisabled=True):
        self.pathtagInstance = pathtagInstance
        self.palette = palette
        self.paletteMode = paletteMode
        self.stripAnsi = stripAnsi
        self.parseWebcolor = parseWebcolor
        self.safeParseWebcolorWhenDisabled = safeParseWebcolorWhenDisabled
        if allowedVariables != None:
            self.allowedVariables = allowedVariables
        else:
            self.allowedVariables = {}
        if customTags != None:
            self.customTags = customTags
        else:
            self.customTags = {}
    def setAllowedVariables(self,variables={}):
        self.allowedVariables = variables
    def resetAllowedVariables(self):
        self.allowedVariables = {}
    def updateAllowedVariables(self,data=dict):
        self.allowedVariables.update(data)
    def addToAllowedVariables(self,key,value):
        self.allowedVariables[key] = value
    def setCustomTags(self,customTags={}):
        self.customTags = customTags
    def resetCustomTags(self):
        self.customTags = {}
    def updateCustomTags(self,data=dict):
        self.customTags.update(data)
    def addToCustomTags(self,key,value):
        self.customTags[key] = value
    def parse(self,inputText,_stripAnsi=False,addCustomTags=None):
        customTags = self.customTags
        if addCustomTags != None:
            customTags.update(addCustomTags)
        # WebcolorTags
        if self.parseWebcolor == True:
            customTags.update(_getWebcolorMappings())
        # Pathtags
        if self.pathtagInstance != None:
            inputText = self.pathtagInstance.eval(inputText)
        # Standard Tags
        inputText = formatStringTags(inputText,self.allowedVariables,customTags)
        # Palette / Strip ANSI
        ## placeholder for reset
        inputText = inputText.replace("\033[0m","§CSlib.CGTS.placeholder.reset§")
        ## match for escape chars
        pattern = r"\033\[(.*?)m"
        matches = re.findall(pattern, inputText)
        ## replace with paletteValue
        for match in matches:
            if self.stripAnsi == False and _stripAnsi == False:
                palettedValue = parsePalettedColor(match,self.palette,self.paletteMode,self.parseWebcolor,self.safeParseWebcolorWhenDisabled,True)
                #palettedValue = _multipleAnsiKeyWrapper(match,self.palette,self.paletteMode,self.parseWebcolor)
                inputText = inputText.replace(f"\033[{match}m", palettedValue)
            # Strip ANSI
            else:
                inputText = inputText.replace(f"\033[{match}m", "")
        # ReReplace Resets
        if self.stripAnsi == False and _stripAnsi == False:
            inputText = inputText.replace("§CSlib.CGTS.placeholder.reset§","\033[0m")
        else:
            inputText = inputText.replace("§CSlib.CGTS.placeholder.reset§","")
        return inputText

def croshellGlobalTextSystemQuick(inputText,pathtagInstance=None,palette=standardHexPalette,paletteMode="hex",stripAnsi=False,instance=None):
    '''CSlib.CGTS: Main formatter function taking text, parameters and then continuing, in function form.'''
    if instance == None:
        tempInstance = crosshellGlobalTextSystem(pathtagInstance,standardHexPalette,stripAnsi)
    else:
        tempInstance = instance
    return tempInstance.parse(inputText)

def parsePrefixDirTag(inputText=str,currentDirectory=str,dirInPrefixEnabled=bool,fallbackPrefix=None):
    '''CSlib.CGTS: Parses the {dir}/{wdir} tag in crosshell'''
    # Fallback
    if fallbackPrefix != None:
        if inputText == None or inputText == "":
            inputText = fallbackPrefix
    # ensure slash
    if "{dir:ensureSlash}" in inputText:
        inputText = inputText.replace("{dir:ensureSlash}","{dir}")
        if currentDirectory.endswith("\\") != True: currentDirectory += "\\"
    # Fix {dir} syntax into {wdir}
    simpleSyntax  = "{dir}"
    complexSyntax = "{dir:"
    inputText = inputText.replace(simpleSyntax,"{wdir}")
    inputText = inputText.replace(complexSyntax,"{wdir:")
    # Parse complex Syntax:
    if "{wdir:" in inputText:
        # Add in a placeholder character as a fix to the regex matcher
        pattern =      '{wdir:"{wdir}"}'
        fixedPattern = '{wdir:"{wdir}␀"}' # nul is placeholder
        inputText = inputText.replace(pattern, fixedPattern)
        # Match for dir element
        pattern = r'{wdir:([^]]+)"}'
        matchresult = re.search(pattern,inputText)
        # Save raw
        matchraw = matchresult.group()
        # Strip {wdir:} syntax
        matchContent = matchraw.lstrip("{")
        matchContent = matchContent.replace('wdir:"',"",1)
        matchContent = matchContent[::-1]
        matchContent = matchContent.replace('}"',"",1)
        matchContent = matchContent[::-1]
        # Turned {wdir:"<content>"} >> raw:{wdir:"<content>"} content:<content>
        # Remove the placeholder character that was put in as a fix
        inputText = inputText.replace("␀", "")
        matchraw = matchraw.replace("␀", "")
        matchContent = matchContent.replace("␀", "")
        # Handle the dir element if dir is enabled (and prefix is enabled)
        if dirInPrefixEnabled == True:
            toReplaceWith = matchContent
        else:
            toReplaceWith = ""
        inputText = inputText.replace(matchraw,toReplaceWith) # This removes the {wdir:} syntax from inputText
        inputText = inputText.replace("{wdir}",currentDirectory) # Same but for the accuall directory
    # Parse simpleSyntax
    elif "{wdir}" in inputText:
        if dirInPrefixEnabled == True:
            inputText = inputText.replace("{wdir}", currentDirectory)
        else:
            inputText = inputText.replace("{wdir}", "")
    # Return
    return inputText


def removeAnsiSequences(inputString):
    '''CSlib.CGTS: Strips ansi sequences from a string.'''
    # Define a regular expression pattern to match ANSI escape sequences
    ansiPattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    # Use re.sub to replace ANSI sequences with an empty string
    cleanedString = ansiPattern.sub('', inputString)
    return cleanedString