import os,re

from .execution import getCleanAliasesDict
from ._crosshellParsingEngine import splitByDelimiters
from .datafiles import _fileHandler

from prompt_toolkit.completion import Completer, Completion

parent = os.path.abspath(os.path.dirname(__file__))

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

def remove_sections_within_quotes(s):
    result = []
    inside_quotes = False
    current_quote = None

    for char in s:
        if char == "'" or char == '"':
            if not inside_quotes:
                inside_quotes = True
                current_quote = char
            elif current_quote == char:
                inside_quotes = False
                current_quote = None
        elif not inside_quotes:
            result.append(char)

    return ''.join(result)

def has_unclosed_brackets(s):
    # Remove sections within quotes
    s_without_quotes = remove_sections_within_quotes(s)

    # Check for unclosed brackets in the modified string
    stack_brackets = []

    for char in s_without_quotes:
        if char == '{':
            stack_brackets.append(char)
        elif char == '}':
            if not stack_brackets:
                return True  # Found a closing bracket without a matching opening bracket
            stack_brackets.pop()

    return bool(stack_brackets)

def getCompleter(csSession):
    completer = csSession.data["set"].getProperty("crsh","SmartInput.Completions.Completer").lower()
    if completer == "legacy":
        return legacy_CustomCompleter(csSession)
    elif completer == "v1":
        return optimized_CustomCompleterV1(csSession)
    elif completer == "v2":
        return optimized_CustomCompleterV2(csSession)

class legacy_CustomCompleter(Completer):
    '''cslib.smartInputCompleters: LEGACY class for tabCompletion.'''
    def __init__(self,csSession=None):
        self.csSession = csSession
    def get_completions(self, document, complete_event):
        colorAliases = self.csSession.data["set"].getProperty("crsh","SmartInput.Completions.ColorAliases")
        # Get the current word being typed by the user
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        beforeCursor = document.text_before_cursor
        beforeCursor = beforeCursor.strip(" ")
        segments = beforeCursor.split(" ")

        # Dynamic multiline
        mlMode = self.csSession.data["set"].getProperty("crsh", "SmartInput.MultiLine")
        dynMultiline = mlMode.lower() == "dynamic" if type(mlMode) == str else False
        if dynMultiline == True:
            pSession = self.csSession.tmpGet("completerData").get("pSession")
            if pSession != None:
                if has_unclosed_brackets(beforeCursor):
                    pSession.multiline = True
                else:
                    pSession.multiline = False

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

class optimized_CustomCompleterV1(Completer):
    '''cslib.smartInputCompleters: V1 class for tabCompletion.'''
    def __init__(self, csSession=None):
        self.csSession = csSession
        self.cache_values()

    def cache_values(self):
        self.colorAliases = self.csSession.data["set"].getProperty("crsh", "SmartInput.Completions.ColorAliases")
        self.includeCustoms = self.csSession.data["set"].getProperty("crsh", "SmartInput.Completions.IncludeCmdCustoms")
        self.includeArgs = self.csSession.data["set"].getProperty("crsh", "SmartInput.Completions.IncludeArgs")
        self.includeStandards = self.csSession.data["set"].getProperty("crsh","SmartInput.Completions.IncludeStandards")
        self.IncludeCurDir = self.csSession.data["set"].getProperty("crsh","SmartInput.Completions.IncludeCurDir")
        self.hideByContext = self.csSession.data["set"].getProperty("crsh", "SmartInput.Completions.HideByContext")
        mlMode = self.csSession.data["set"].getProperty("crsh", "SmartInput.MultiLine")
        self.dynMultiline = mlMode.lower() == "dynamic" if type(mlMode) == str else False
        if self.csSession.data["sta"] != True:
            self.styles = self.csSession.data["set"].getProperty("crsh", "SmartInput.Styling.Completions")
        else:
            self.styles = _fileHandler("json","get",f"{parent}{os.sep}..{os.sep}sInputNoFormatStyles.json")

    def get_completions(self, document, complete_event):
        # Get text/word before cursor
        word_before_cursor = document.get_word_before_cursor(WORD=True).strip()
        before_cursor = document.text_before_cursor.strip(" ")
        segments = before_cursor.split(" ") # split by " " to get segments

        # Dynamic multiline
        if self.dynMultiline == True:
            pSession = self.csSession.tmpGet("completerData").get("pSession")
            if pSession != None:
                if has_unclosed_brackets(before_cursor):
                    pSession.multiline = True
                else:
                    pSession.multiline = False

        # Collect items and aliases in a single pass from registry. Aliases are suffixed by "_alias"
        items = set()
        for item, data in self.csSession.registry["cmdlets"].items():
            items.add(item)
            items.update(
                [key+"_alias" for key in getCleanAliasesDict(data.get("aliases", {})).keys()]
            )

        # Get al commands/aliases that are matching with our word-before-cursor.
        wMatches = {item for item in items if item.startswith(word_before_cursor) and item}

        aMatches = set()
        cMatches = set()
        if self.csSession:
            # Get first-segment (usualy command), extract first word and check if in cmdlet/alias list
            key = segments[0] if segments[0] in items else next((m for m in wMatches if m in items), None)
            # Get the data for that command
            data = self.csSession.registry["cmdlets"].get(key)
            if data == None: data = {}
            # Extract arguments from cmdletdata, excluding "optional:" prefix aswell as parsing out "ors" (<arg>/<arg> => <arg> or <arg>) also exclude <> and any arg containing special characters, also ensure the arg beings with "-"
            if self.includeArgs and data.get("args"):
                args = {arg.strip(" ").replace("optional:", "") for arg in splitByDelimiters(data["args"], [" ", "/"]) if not arg.strip(" ").startswith("<") and not arg.strip(" ").endswith(">") and not contains_special_characters(arg.strip(" ")) and arg.strip(" ").startswith("-")}
                aMatches.update(args)
            # If extras should be included then extract the extra sInputCompletions from the extras data and add them.
            if self.includeCustoms and data.get("extras", {}).get("sInputCompletions"):
                cmdletCompletions = data["extras"]["sInputCompletions"]
                if isinstance(cmdletCompletions, str):
                    cmdletCompletions = cmdletCompletions.split(";")
                cMatches.update(cmdletCompletions)

        # hide by context
        if self.hideByContext and segments[0] in items:
            se = segments[-1].strip(" ") # last segment
            # get cmdlet matches for the last word instead of previous input
            new_wMatches = {item for item in items if item.startswith(se) and not document.text_before_cursor.endswith(" ")}
            # apply only theese matches unless current writing ends with delim ";" or "||"
            if not se.endswith(";") and not se.endswith("||"):
                wMatches = new_wMatches
            # if the the last word is an argument that means we are writing a command, args and customs should then be omitted.
            else:
                aMatches = set()
                cMatches = set()

        # Combine a completions list, from the arg and custom matches
        completions = [
            Completion(match, start_position=-len(word_before_cursor), style=self.styles["arg"]) for match in aMatches
        ] + [
            Completion(match, start_position=-len(word_before_cursor), style=self.styles["custom"]) for match in cMatches
        ]
        
        # If includestandards are turned off then clear command completions
        if self.includeStandards == False:
            wMatches = []

        # If aliases should be colored diffrently from commands then extract them sepparately and color them accordingly.
        if self.colorAliases:
            completions += [Completion(match, start_position=-len(word_before_cursor), style=self.styles["cmd"]) for match in wMatches if "_alias" not in match]
            wMatches_ali = {item[::-1].replace("saila_", "", 1)[::-1] for item in wMatches if item.endswith("_alias")}
            completions += [Completion(match, start_position=-len(word_before_cursor), style=self.styles["alias"]) for match in wMatches_ali]
        # Else strip the _alias suffix and include everything.
        else:
            completions += [Completion(match[::-1].replace("saila_", "", 1)[::-1], start_position=-len(word_before_cursor), style=self.styles["cmd"]) for match in wMatches]
        # If the current directory should be included (by settings) check its data and add them to completions
        if self.csSession and self.IncludeCurDir == True:
            for ent in os.listdir(self.csSession.data["dir"]):
                if word_before_cursor in ent:
                    if os.path.isdir(ent) == True:
                        completions.append(Completion(ent, start_position=-len(word_before_cursor), style=self.styles["dir"]))
                    else:
                        if os.path.splitext(ent)[1] in [".crsh",".crcmd"]:
                            completions.append(Completion(ent, start_position=-len(word_before_cursor), style=self.styles["script"]))
                        else:
                            completions.append(Completion(ent, start_position=-len(word_before_cursor), style=self.styles["file"]))
            # Show recursive info
            if word_before_cursor.strip().endswith("/"):
                dirPreCur = os.path.join( self.csSession.data["dir"] , word_before_cursor.strip().rstrip("/") )
                for ent in os.listdir(dirPreCur):
                    entp = os.path.join(dirPreCur,ent).replace(self.csSession.data["dir"]+os.sep,"").replace(os.sep,"/")
                    if os.path.isdir(entp) == True:
                        completions.append(Completion(entp, start_position=-len(word_before_cursor), style=self.styles["dir"]))
                    else:
                        if os.path.splitext(entp)[1] in [".crsh",".crcmd"]:
                            completions.append(Completion(entp, start_position=-len(word_before_cursor), style=self.styles["script"]))
                        else:
                            completions.append(Completion(entp, start_position=-len(word_before_cursor), style=self.styles["file"]))


        # Return completions
        return completions

class optimized_CustomCompleterV2(Completer):
    '''cslib.smartInputCompleters: V2 class for tabCompletion.'''
    def __init__(self, csSession=None):
        self.csSession = csSession
        self.cache_values()

    def cache_values(self):
        self.colorAliases = self.csSession.data["set"].getProperty("crsh", "SmartInput.Completions.ColorAliases")
        self.includeCustoms = self.csSession.data["set"].getProperty("crsh", "SmartInput.Completions.IncludeCmdCustoms")
        self.includeArgs = self.csSession.data["set"].getProperty("crsh", "SmartInput.Completions.IncludeArgs")
        self.includeStandards = self.csSession.data["set"].getProperty("crsh","SmartInput.Completions.IncludeStandards")
        self.IncludeCurDir = self.csSession.data["set"].getProperty("crsh","SmartInput.Completions.IncludeCurDir")
        self.hideByContext = self.csSession.data["set"].getProperty("crsh", "SmartInput.Completions.HideByContext")
        mlMode = self.csSession.data["set"].getProperty("crsh", "SmartInput.MultiLine")
        self.dynMultiline = mlMode.lower() == "dynamic" if type(mlMode) == str else False
        if self.csSession.data["sta"] != True:
            self.styles = self.csSession.data["set"].getProperty("crsh", "SmartInput.Styling.Completions")
        else:
            self.styles = _fileHandler("json","get",f"{parent}{os.sep}..{os.sep}sInputNoFormatStyles.json")

    def get_completions(self, document, complete_event):
        # Get text/word before cursor
        last_word_befCursor = document.get_word_before_cursor(WORD=True).strip()
        text_befCursor = document.text_before_cursor.strip(" ")
        segments = text_befCursor.split(" ") # split by " " to get segments

        # Dynamic multiline
        if self.dynMultiline == True:
            pSession = self.csSession.tmpGet("completerData").get("pSession")
            if pSession != None:
                if has_unclosed_brackets(text_befCursor):
                    pSession.multiline = True
                else:
                    pSession.multiline = False

        # Setup
        wMatches = set()
        aMatches = set()
        cMatches = set()
        cmdletNm = set() # Cmdlets and Aliases

        # If session is defined then commands and aliases
        if self.csSession:
            # Collect entries from the registry, whilst suffixing aliases with _alias
            for entry, data in self.csSession.registry["cmdlets"].items():
                cmdletNm.add(entry)
                cmdletNm.update(
                    [key+"_alias" for key in getCleanAliasesDict(data.get("aliases", {})).keys()]
                )
            # Add matching entries to wMatches, checking using the last_word_before_cursor.
            wMatches = {entry for entry in cmdletNm if entry.startswith(last_word_befCursor) and entry}

            # Hide by context?
            

            # If includeStandards are turned off, clear the wMatches field
            if self.includeStandards == False:
                wMatches = set()

        # Return Completions
        return []
