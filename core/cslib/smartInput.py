import os
import re

from .cslib import intpip,_handleAnsi
from .execution import getCleanAliasesDict
from ._crosshellParsingEngine import splitByDelimiters
from .datafiles import getKeyPath
from .toad import getToad

try:
    from pygments.lexers import PythonLexer
except:
    intpip("install pygments")
    from pygments.lexers import PythonLexer

try:
    from prompt_toolkit import PromptSession
except:
    intpip("install prompt_toolkit")
    from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import History
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.cursor_shapes import CursorShape
from prompt_toolkit.styles import Style

def isAliasFor(possibleAlias,registry):
    for key,value in registry["cmdlets"].items():
        if value.get("aliases") != None:
            if possibleAlias in value.get("aliases"):
                return key
    else:
        possibleAlias 

def contains_special_characters(input_string):
    # Define a regular expression pattern to match non-alphanumeric and non-hyphen characters
    pattern = r'[^a-zA-Z0-9-]'
    # Use re.search to find the first occurrence of the pattern in the string
    match = re.search(pattern, input_string)
    # If a match is found, return True (contains special characters), else return False
    return match is not None

class CustomCompleter(Completer):
    '''cslib.smartInput: Class for tabCompletion.'''
    def __init__(self,csSession=None):
        self.csSession = csSession
    def get_completions(self, document, complete_event):
        colorAliases = self.csSession.data["set"].getProperty("crsh","SmartInput.Completions.ColorAliases")
        # Get the current word being typed by the user
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        beforeCursor = document.text_before_cursor
        beforeCursor = beforeCursor.strip(" ")
        segments = beforeCursor.split(" ")
        # Find all items that start with the current word
        items = []
        for item,data in self.csSession.registry["cmdlets"].items():
            items.append(item)
            aliases = data.get("aliases")
            if aliases != None:
                if colorAliases == True:
                    items.extend( [m+"_alias" for m in list(getCleanAliasesDict(aliases).keys())] )
                else:
                    items.extend( list(getCleanAliasesDict(aliases).keys()) )
        wMatches = [x for x in items if x.startswith(word_before_cursor) and x != ""]
        # CSSession
        aMatches = []
        cMatches = []
        if self.csSession != None:
            # Add per commands
            includeCustoms = self.csSession.data["set"].getProperty("crsh","SmartInput.Completions.IncludeCmdCustoms")
            includeArgs    = self.csSession.data["set"].getProperty("crsh","SmartInput.Completions.IncludeArgs")
            if includeCustoms == True or includeArgs == True:
                fS = segments[0]
                key = None
                if fS in items:
                    key = fS
                else:
                    for m in wMatches:
                        if m in items:
                            key = m
                            break
                if key != None:
                    data = {}
                    data = self.csSession.registry["cmdlets"].get(key)
                    if data == None:
                        data = self.csSession.registry["cmdlets"].get( isAliasFor(key,self.csSession.registry) )
                    if data == None:
                        data = {}
                    if includeArgs == True:
                        if data.get("args") != None:
                            args = splitByDelimiters(data.get("args"),[" ","/"])
                            newargs = []
                            for arg in args:
                                _s = arg.strip(" ")
                                if _s.startswith("<") == False and _s.endswith(">") == False:
                                    if contains_special_characters(_s) == False and _s.startswith("-"):
                                        _s = _s.replace("optional:","")
                                        aMatches.append(_s)
                    if includeCustoms == True:
                        if data.get("extras") != None:
                            cmdletCompletions = data["extras"].get("sInputCompletions")
                            if cmdletCompletions != None:
                                if type(cmdletCompletions) == str:
                                    cmdletCompletions = cmdletCompletions.split(";")
                                cMatches.extend(cmdletCompletions)
            # Remove word-matches if not enabled
            if self.csSession.data["set"].getProperty("crsh","SmartInput.Completions.IncludeStandards") != True:
                wMatches = []
        # Assemble
        completions = []
        ## get styles
        styles = self.csSession.data["set"].getProperty("crsh","SmartInput.Styling.Completions")
        ## rem empties
        aMatches = [x for x in aMatches if x.startswith(word_before_cursor) and x != ""]
        cMatches = [x for x in cMatches if x.startswith(word_before_cursor) and x != ""]
        ## no-inkl cmd
        if self.csSession.data["set"].getProperty("crsh","SmartInput.Completions.HideByContext") == True:
            if segments[0] in items:
                se = segments[-1].strip(" ")
                new_wMatches = []
                for item in items:
                    if item.startswith(se) and document.text_before_cursor.endswith(" ") != True:
                        new_wMatches.append(item)
                if se.endswith(";") == False and se.endswith("||") == False:
                    wMatches = new_wMatches
                else:
                    aMatches = []
                    cMatches = []
        ## split aliases and cmds
        if colorAliases == True:
            wMatches_cmd = []
            wMatches_ali = []
            for item in wMatches:
                if item.endswith("_alias"):
                    wMatches_ali.append(item[::-1].replace("saila_","",1)[::-1])
                else:
                    wMatches_cmd.append(item)
        else:
            wMatches_cmd = wMatches
        ## add objs
        completions.extend(
            [Completion(match, start_position=-len(word_before_cursor), style=styles["arg"]) for match in aMatches]
        )
        completions.extend(
            [Completion(match, start_position=-len(word_before_cursor), style=styles["custom"]) for match in cMatches]
        )
        completions.extend(
            [Completion(match, start_position=-len(word_before_cursor), style=styles["cmd"]) for match in wMatches_cmd]
        )
        if colorAliases == True:
            completions.extend(
                [Completion(match, start_position=-len(word_before_cursor), style=styles["alias"]) for match in wMatches_ali]
            )
        # Return a list of Completion objects for the matches
        return completions


class MyHistory(History):
    '''cslib.smartInput: Class for history.'''
    def load_history_strings(self):
        # Load the history strings from some source (e.g. a file or database)
        # and return them as a list of strings
        return []

    def store_string(self, string):
        # Store the given string in some source (e.g. a file or database)
        pass

def bottom_toolbar(csSession):
    '''cslib.smartInput: Function to get toolbar msg.'''
    stdMsg = getToad(csSession)
    pers = csSession.data["per"].getProperty("crsh","sInput.btoolbar_msg")
    nonAllowed = ["","STDTITLE","stdtitle",None,"none","None","Null","null"]
    if pers in nonAllowed:
        msg = stdMsg
    else:
        msg = _handleAnsi(pers)
    return ANSI(msg)

def sInputCreateHistoryObj(csSession):
    '''cslib.smartInput: Creates a history instance if it dosen't exists.'''
    return MyHistory()

def sInputCreateHistoryInstance(csSession):
    '''cslib.smartInput: Creates a history instance if it dosen't exists (and links it).'''
    # Create history instance
    if csSession.registry["sInput_historyInstance"] == None:
        csSession.registry["sInput_historyInstance"] = sInputCreateHistoryObj(csSession)

def sInputClearHistoryInstance(csSession):
    '''cslib.smartInput: Resets the history instance if it does exists.'''
    # Reset history instance
    if csSession.registry["sInput_historyInstance"] != None:
        csSession.registry["sInput_historyInstance"] = None

class sInputPrompt():
    '''cslib.smartInput: Class to handle sInput prompting.'''
    def __init__(self,csSession):
        self.csSession = csSession
        self.sessionArgs = {}
        self.old_defstyle = None
        self.inject = False
        self.styleOpts = {}
        self.styleEna = False
        self.pSession = None
        self.history = None
        self._createHistory()
        self._updateSettings()
    def _createHistory(self):
        self.history = sInputCreateHistoryObj(self.csSession)
    def _createSession(self):
        self.pSession = PromptSession(**self.sessionArgs)
    def _clearHistory(self):
        self.history = None
    def _reset(self):
        self.pSession = None
        self.history = None
        self.sessionArgs = {}
        self.inject = False
        self.styleOpts = {}
        self.styleEna = False
    def _clearSettings(self):
        self.sessionArgs = {}
        self._createSession()
    def _updateSettings(self):
        # Clear sessionArgs
        self.sessionArgs = {}
        # Open settings
        seti = self.csSession.data["set"].getModule("crsh")
        # Tabcomplete
        if getKeyPath(seti,"SmartInput.TabComplete") == True:
            self.sessionArgs["completer"] = CustomCompleter(self.csSession)
        # History
        if getKeyPath(seti,"SmartInput.History") == True:
            # History type
            hisType = getKeyPath(seti,"SmartInput.HistoryType")
            hisFile = getKeyPath(seti,"SmartInput.HistoryFile")
            hisFile = self.csSession.data["ptm"].eval(hisFile)
            if hisType.strip('"') == "File":
                self.sessionArgs["history"] = FileHistory(hisFile)
            else:
                if self.history == None:
                    self.sessionArgs["history"] = sInputCreateHistoryObj(self.csSession)
                else:
                    self.sessionArgs["history"] = self.history
            # History suggest
            if getKeyPath(seti,"SmartInput.HistorySuggest") == True:
                self.sessionArgs["auto_suggest"] = AutoSuggestFromHistory()
        # Highlight
        if getKeyPath(seti,"SmartInput.Highlight") == True:
            self.sessionArgs["lexer"] = PygmentsLexer(PythonLexer)
        # Toolbar
        if getKeyPath(seti,"SmartInput.ShowToolbar") == True:
            self.sessionArgs["bottom_toolbar"] = bottom_toolbar(self.csSession)
        # Multiline
        if getKeyPath(seti,"SmartInput.MultiLine") == True:
            self.sessionArgs["multiline"] = True
        # MouseSupport
        if getKeyPath(seti,"SmartInput.MouseSupport") == True:
            self.sessionArgs["mouse_support"] = True
        # LineWrap
        if getKeyPath(seti,"SmartInput.LineWrap") == False:
            self.sessionArgs["wrap_lines"] = False
        # CursorChar
        curChar = getKeyPath(seti,"SmartInput.CursorChar")
        if curChar != "" and curChar != None:
            self.sessionArgs["cursor"] = eval("CursorShape." + curChar)
        # EnhancedStyling
        self.inject = getKeyPath(seti, "SmartInput.Styling.Inject")
        self.styleOpts = getKeyPath(seti,"SmartInput.Styling.Options")
        self.styleEna = getKeyPath(seti,"SmartInput.Styling.Enabled")
        if self.styleEna == True:
            if self.inject != True:
                self.sessionArgs["style"] = Style.from_dict(
                    self.styleOpts
                )
        # Create new session
        self._createSession()
    def prompt(self,_prefix):
        if self.pSession == None:
            self._createSession()
        if self.history == None:
            self._createHistory()
        # Hackie color inject
        if self.styleEna == True and self.inject == True:
            if self.old_defstyle == None:
                import sys
                defstyle = sys.modules['prompt_toolkit.styles.defaults']
                self.old_defstyle = defstyle.PROMPT_TOOLKIT_STYLE.copy()
                for key,value in self.styleOpts.items():                
                    defstyle.PROMPT_TOOLKIT_STYLE.append((key,value))
        # Update toolbar
        if self.sessionArgs.get("bottom_toolbar") != None:
            self.pSession.bottom_toolbar = bottom_toolbar(self.csSession)
        # Ask
        inp = self.pSession.prompt(ANSI(_prefix))
        # Post Handle
        if self.styleEna == True and self.inject == True:
            if self.old_defstyle != None:
                defstyle.PROMPT_TOOLKIT_STYLE = self.old_defstyle.copy()
                self.old_defstyle = None
        # Return
        return inp