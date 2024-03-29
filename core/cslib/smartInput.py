import os
import sys
import re

from .cslib import intpip,_handleAnsi
from .datafiles import getKeyPath,_fileHandler
from .smartInputCompleters import getCompleter

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
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import History
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.cursor_shapes import CursorShape # This is used by eval() later, thus shows as non-referenced.
from prompt_toolkit.styles import Style

parent = os.path.abspath(os.path.dirname(__file__))

def capped_string_with_ansi(input_string, max_length):
    # Regular expression to match ANSI escape codes
    ansi_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    # Initialize variables to keep track of rendered and original lengths
    rendered_length = 0
    original_length = 0
    # Iterate through the input string
    i = 0
    while i < len(input_string):
        # Check if the current character is the escape character (27) which indicates the start of an ANSI escape code
        if ord(input_string[i]) == 27:
            # Find the end of the ANSI escape code using regular expression
            match = ansi_pattern.match(input_string[i:])
            if match:
                # Increase rendered length by 0 for ANSI codes
                rendered_length += 0
                # Move the index past the ANSI escape code
                i += len(match.group(0))
            else:
                # If it's not a valid ANSI code, treat it as a regular character
                rendered_length += 1
                original_length += 1
                i += 1
        else:
            # If it's a regular character, increase both rendered and original lengths
            rendered_length += 1
            original_length += 1
            i += 1
        # Check if the rendered length exceeds the maximum length
        if rendered_length > max_length:
            # Trim the original string to the desired length
            input_string = input_string[:original_length]
            break
    return input_string
def sInput_autoIntTuple(pre=tuple) -> tuple:
    post = list(pre)
    for i in range(len(pre)):
        post[i] = int(pre[i])
    return tuple(post)
def sInput_hex_to_rgb(hex=str) -> str:
    lv = len(hex)
    tup = tuple(int(hex[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    return sInput_autoIntTuple(tup)
def sInput_rgb_to_ansi(rgb=tuple, background=False) -> str:
    return '\033[{};2;{};{};{}m'.format(48 if background else 38, *rgb)
def swapp_ansi_ground(ansicode=str,strip=False):
    _swapp_mapping = {
        "0": "0",
        "30": "40",
        "31": "41",
        "32": "42",
        "33": "43",
        "34": "44",
        "35": "45",
        "36": "46",
        "37": "47",
        "90": "100",
        "91": "101",
        "92": "102",
        "93": "103",
        "94": "104",
        "95": "105",
        "96": "106",
        "97": "107",
    }
    swapp_mapping = _swapp_mapping.copy()
    for key,value in _swapp_mapping.items():
        swapp_mapping[value] = key
    # Find
    ansi_escape_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])') # Define a regular expression pattern to match ANSI escape codes
    matches = ansi_escape_pattern.finditer(ansicode)                           # Use re.finditer to find all matches in the input string
    # Replace
    for match in matches:
        code = str(match.group())
        ocode = code
        if "38;2" in code or "48;2" in code:
            # replace rgb
            code = code.replace("48;2","§rgb-swapp§")
            code = code.replace("38;2","48;2")
            code = code.replace("§rgb-swapp§","38;2")
        else:
            if len(code) == 8 or len(code) == 9:
                code = swapp_mapping[code]
        if strip == True:
            ansicode = ansicode.replace(ocode,"",1)
        else:
            ansicode = ansicode.replace(ocode,code,1)
    return ansicode
def ptk_style_to_ansi(ptk_style):
    styles = ptk_style.strip(" ").split(" ")
    ansi_style = ""
    for style in styles:
        if style.startswith("fg:"):
            _hex = style.replace("fg:#","")
            rgb = sInput_hex_to_rgb(_hex)
            ansi_style += sInput_rgb_to_ansi(rgb,background=True)
        elif style.startswith("bg:"):
            _hex = style.replace("bg:#","")
            rgb = sInput_hex_to_rgb(_hex)
            ansi_style += sInput_rgb_to_ansi(rgb,background=False)
    return ansi_style

def update_bottom_toolbar_message(promptSession=None,seti=dict,new_message=str,printer=None,noformat=False):
    # stripansi
    if promptSession.csSession.data["sta"] == True:
        return
    # set session msg
    if promptSession != None:
        promptSession.bottom_toolbar = ANSI(new_message)
    # Prep msg formatting
    ptk_style = getKeyPath(seti,"SmartInput.Styling.Options.bottom-toolbar")
    if ptk_style == None or noformat == True:
        formatting = ""
    else:
        formatting = ptk_style_to_ansi(ptk_style)
    new_message = swapp_ansi_ground(new_message)
    new_message = new_message.replace("\033[0m",formatting)
    # Define ansi codes
    clear_line = "\x1b[K"    # ANSI escape code to clear the line
    save_line = "\x1b[s"    # ANSI escape code to save pos
    load_line = "\x1b[u"    # ANSI escape code to load poss
    move_to_beginning = "\r" # ANSI escape code to move the cursor to the beginning of the line
    width,height = os.get_terminal_size()
    move_to_last_line = f"\x1b[{height};0H"
    # handle msg
    ansi_escape_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    new_message_na = ansi_escape_pattern.sub("",new_message)
    spacing = width-len(new_message_na)
    spacing -= 2
    spaces = " "*spacing
    new_message = new_message + spaces
    new_message = capped_string_with_ansi(new_message,width)
    # Move up one line, clear the line, and redraw the new line
    if printer != None:
        printer(save_line + move_to_last_line + clear_line + move_to_beginning + formatting + new_message + load_line)
    else:
        sys.stdout.write(save_line + move_to_last_line + clear_line + move_to_beginning + formatting + new_message + load_line)
        sys.stdout.flush()
    
def bottom_toolbar(csSession):
    '''cslib.smartInput: Function to get toolbar msg.'''
    stdMsg = csSession.registry["toadInstance"].getToadMsg()
    pers = csSession.data["per"].getProperty("crsh","sInput.btoolbar_msg")
    nonAllowed = ["","STDTITLE","stdtitle",None,"none","None","Null","null"]
    if pers in nonAllowed:
        msg = stdMsg
    else:
        msg = _handleAnsi(pers)
    if msg.startswith("toad:"):
        msg = msg.replace("toad:","")
        msg = csSession.registry["toadInstance"].sayToad(msg)
    # stripansi fix
    if csSession.data["sta"] == True:
        return swapp_ansi_ground(msg,True)
    return ANSI(msg)

class MyHistory(History):
    '''cslib.smartInput: Class for history.'''
    def load_history_strings(self):
        # Load the history strings from some source (e.g. a file or database)
        # and return them as a list of strings
        return []

    def store_string(self, string):
        # Store the given string in some source (e.g. a file or database)
        pass

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
        self.ansiStrippedFormatters = _fileHandler("json","get",f"{parent}{os.sep}..{os.sep}sInputNoFormatOpts.json")
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
        self.csSession.tmpSet("completerData",{})
        if getKeyPath(seti,"SmartInput.TabComplete") == True:
            self.sessionArgs["completer"] = getCompleter(self.csSession)
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
        # Strip ansi
        if self.csSession.data["sta"] == True:
            self.styleOpts.update(self.ansiStrippedFormatters)
            if self.sessionArgs.get("lexer") != None:
                self.sessionArgs["lexer"] = None
                self._createSession()
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
        ## update completerData
        _d = self.csSession.tmpGet("completerData")
        _d["pSession"] = self.pSession
        self.csSession.tmpSet("completerData",_d)
        ## prompt
        inp = self.pSession.prompt(ANSI(_prefix))
        # Post Handle
        if self.styleEna == True and self.inject == True:
            if self.old_defstyle != None:
                defstyle.PROMPT_TOOLKIT_STYLE = self.old_defstyle.copy()
                self.old_defstyle = None
        # Return
        return inp
    def liveSetBToolbarMsg(self,msg):
        seti = self.csSession.data["set"].getModule("crsh")
        update_bottom_toolbar_message(self.pSession,seti,msg)