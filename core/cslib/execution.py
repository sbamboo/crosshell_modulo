import traceback
import os
import sys
import subprocess
import re

from cslib.buffering import BufferedStdout
from cslib.externalLibs.filesys import filesys as fs
from cslib import handleOSinExtensionsList,CrosshellExit,CrosshellDebErr
from cslib._crosshellParsingEngine import splitByDelimiters
from cslib.longPathHandler import lph_isAllowed
from cslib._crosshellParsingEngine import split_string_by_spaces
from cslib.externalLibs.limitExec import DummyObject,ReturningDummyObject,RaisingDummyObject

parent = os.path.abspath(os.path.dirname(__file__))

def prep_globals(globalValue=dict,entries=list):
    '''CSlib.execution: Function to filter globals by entries.'''
    newGlobals = {}
    for entry in entries:
        newGlobals[entry] = globalValue[entry]
    return newGlobals

def determine_reader(fending=str,registry=dict) -> str:
    '''CSlib.execution: Function to determine the reader from the registry using fending.'''
    if fending == None:
        fending = "MIME_EXECUTABLE"
    # Match
    readers = registry["readerData"]
    for reader in readers:
        if fending in handleOSinExtensionsList(reader["extensions"]):
            return reader

def get_command_data(command=str,registry=dict) -> str:
    '''CSlib.execution: Function to get command data from the registry.'''
    for cmdlet,cmdletData in registry["cmdlets"].items():
        if cmdlet.lower() == command.lower():
            if cmdletData.get("options") != None:
                if cmdletData["options"].get("dontLoad") == True:
                    return None
            return cmdletData

def safe_decode_utf8_cp437(bytestring,defencoding="utf-8"):
    '''CSlib.execution: Function safely handle unicode and/or cp437.'''
    try:
        decoded_string = bytestring.decode(defencoding)
    except:
        decoded_string = bytestring.decode('cp437', errors='replace')
    return decoded_string

def runShell(csSession,shellExecPath=str,shellExecArgs=[],capture=False,cmdletpath=str,cmdletargs=[],defencoding="utf-8"):
    '''CSlib.execution: Function to execute a command using a shell program.'''
    execList = [f'{shellExecPath}', *shellExecArgs, cmdletpath, *cmdletargs]
    # check long path safety
    if lph_isAllowed(' '.join(execList)) == False:
        csSession.deb.perror("lng:cs.cmdletexec.longpath.nonallowed",raiseEx=False)
    # Capture output if enabled otherwise just execute the subprocess
    if capture == False:
        subprocess.run(execList, stderr=sys.stderr, stdout=sys.stdout)
    else:
        proc = subprocess.Popen(execList, stderr=sys.stderr, stdout=subprocess.PIPE)
        out = proc.communicate()[0] # Get output
        out = safe_decode_utf8_cp437(out,defencoding)
        return out

def exec_reader(csSession,readerPath=str,command=str,cmdargs=list,encoding=str,isCaptured=bool,globalValues=dict,globalsToReader=dict,retVars=False):
    '''CSlib.execution: Function to execute a command using a reader.'''
    # get def encoding
    readerEncoding = csSession.data["set"].getProperty("crsh","Formats.DefaultEncoding")
    # setup globals
    globalsToReader["cs_isCaptured"] = isCaptured
    globalsToReader["cs_defEncoding"] = readerEncoding
    globalsToReader["cs_readerPath"] = readerPath
    globalsToReader["cs_lph_isAllowed"] = lph_isAllowed
    globalsToReader["cs_runShell"] = runShell
    # create and exec command
    try:
        exec(open(readerPath,'r',encoding=readerEncoding).read(),globalsToReader)
    except FileNotFoundError:
        csSession.deb.perror("lng:cs.cmdletexec.reader.errornotfound",{"reader":os.path.basename(readerPath),"readerPath":readerPath})
    except Exception as e:
        csSession.deb.perror("lng:cs.cmdletexec.reader.errorinexec",{"reader":os.path.basename(readerPath),"readerPath":readerPath,"traceback":e})
    # execute reader-defined main command
    try:
        retVars = main(csSession,cmddata=command,args=cmdargs,encoding=encoding,defencoding=readerEncoding,isCaptured=isCaptured,globalValues=globalValues)
    except CrosshellDebErr as e:
        raise
    except Exception as e:
        if 'main' not in locals() or not callable(locals()['main']):
            csSession.deb.perror("lng:cs.cmdletexec.reader.nomainfunc",{"reader":os.path.basename(readerPath),"readerPath":readerPath,"traceback":e})
        else:
            csSession.deb.perror("lng:cs.cmdletexec.reader.errorincall",{"reader":os.path.basename(readerPath),"readerPath":readerPath,"traceback":e})
    if retVars != False:
        return retVars

def getPackdir(basedir,scriptroot,index=0):
    bpackdir = f'{basedir}{os.sep}packages'
    scriptroot = scriptroot.replace(bpackdir,"")
    scriptroot = scriptroot.lstrip(os.sep)
    childFolder = scriptroot.split(os.sep)[index]
    return f"{bpackdir}{os.sep}{childFolder}"

def getCleanAliasesDict(aliases=list) -> dict:
    splits = {}
    for i,elem in enumerate(aliases):
        if ":" in elem:
            _elem = elem.split(":")
            args = _elem[-1].split(" ")
            _elem.pop(-1)
            elem = ':'.join(_elem)
            splits[elem] = args
        else:
            splits[elem] = []
    return splits

def find_absname(cmdletData,command):
    if command not in list(cmdletData.keys()):
        for cmd,data in cmdletData.items():
            aliases = data.get("aliases")
            if aliases != None:
                cleanAliases = getCleanAliasesDict(aliases)
                if command in cleanAliases.keys():
                    i = list(cleanAliases.keys()).index(command)
                    return cmd,list(cleanAliases.values())[i]
    return command,None

def safe_exit(code=None):
    raise CrosshellExit(code)

def getCmdletData(csSession,command,args):
    ## use tmp var incase nontype return
    command,addArgs = find_absname(csSession.registry["cmdlets"],command)
    if addArgs != None:
        args.extend(addArgs)
    cmdletData = get_command_data(command,csSession.registry)
    return command,args,cmdletData

def getGlobals(csSession,command,args,cmdletData,globalValues,entries,reader,capture=False,inpipeLine=False):
    # Check internal-restriction-mode whitelist validity
    prep_globals_v = False
    if csSession.data["set"].getProperty("crsh_debugger","Execution.AllowRunAsInternal") != True:
        if cmdletData["options"]["restrictionMode"].lower() == "internal":
            whitelist = _fileHandler("json","get",f"{parent}{os.sep}..{os.sep}internalRestrictWhitelist.json").get("whitelist")
            if whitelist == None:
                whitelist = []
            whitelist_name = os.path.basename(cmdletData["path"]).split(".")
            whitelist_name.pop(-1)
            whitelist_name = ".".join(whitelist_name)
            if whitelist_name not in whitelist:
                prep_globals_v = True
        else:
            prep_globals_v = True
    else:
        if cmdletData["options"]["restrictionMode"].lower() != "internal":
            prep_globals_v = True
    # Prep globals
    if prep_globals_v == True:
        globalValues = prep_globals(globalValues,entries)
    # Restricted Mode
    if cmdletData["options"]["restrictionMode"].lower() == "restricted":
        globalValues["__builtins__"] = DummyObject()
        globalValues["__import__"] = DummyObject()
    if cmdletData["options"]["restrictionMode"].lower() == "restricted:strict":
        globalValues["__builtins__"] = RaisingDummyObject()
        globalValues["__import__"] = RaisingDummyObject()
    if cmdletData["options"]["restrictionMode"].lower() == "restricted:returning":
        globalValues["__builtins__"] = ReturningDummyObject()
        globalValues["__import__"] = ReturningDummyObject()
    # Add standard values
    scriptroot = os.path.abspath(os.path.dirname(cmdletData["path"]))
    globalValues["argv"] = args
    globalValues["sargv"] = " ".join(args)
    globalValues["CSScriptRoot"] = scriptroot
    globalValues["CSScriptData"] = cmdletData["reader"] = reader
    globalValues["CS_PackDir"] = getPackdir( csSession.data["ptm"].getTag("CS_BaseDir"),scriptroot,0 )
    globalValues["CS_CurDir"] = csSession.data["dir"]
    globalValues["CS_BaseDir"] = csSession.data["bdr"]
    globalValues["CS_CoreDir"] = csSession.data["cdr"]
    globalValues["CS_IsCaptured"] = capture
    # Add exception types
    globalValues["CrosshellDebErr"] = CrosshellDebErr
    globalValues["CrosshellExit"] = CrosshellExit
    # add elementsAfter if passed
    if inpipeLine != None:
        globalValues["CS_InPipeline"] = inpipeLine
    else:
        globalValues["CS_InPipeline"] = False
    # Safe exit handling
    if csSession.data["set"].getProperty("crsh","Execution.SafelyHandleExit"):
        globalValues["exit"] = safe_exit # overwrite exit
        globalValues["CS_oexit"] = exit # give orgexit
    # Fix pathtags for error printing
    cmdletData["name"] = command
    ept = cmdletData
    # If capture is true, redirect stdout
    if capture == True:
        buffer = BufferedStdout(sys.stdout,input)
        csSession.tmpSet("buffer",buffer)
        buffer.printToConsole = False
        old_stdout = sys.stdout
        globalValues["buffer_bwrite"] = buffer.bwrite
        globalValues["buffer_cwrite"] = buffer.cwrite
        globalValues["buffer_cwrite_adv"] = buffer.cwrite_adv
        globalValues["buffer_bwrite_autoNL"] = buffer.bwrite_autoNL
        globalValues["buffer_cwrite_autoNL"] = buffer.cwrite_autoNL
        globalValues["input"] = buffer.safe_input
        globalValues["CS_oinput"] = input
    else:
        buffer = None
        old_stdout = None
    # Reuturn
    return globalValues,ept,old_stdout,buffer

def execute_expression(csSession,command=str,args=list,capture=False,globalValues=dict,entries=list,inpipeLine=None):
    '''CSlib.execution: Main expression executer.

    Entries are a list of al globalValue entries that should be included, no other ones will get sent to the cmdlet!
    ^ Except the ones added by this function:
     - argv/sargv:   arguments sent to cmdlet
     - CSScriptRoot: path to parent of cmdlet
     - CSScriptData: dictionary containing cmdlet data, inkl. reader
     - CS_PackDir:   The /packages path
     - CS_CurDir:    The current dictionary from the sesison (shortcut)
     - CS_BaseDir:   The base directory of crosshell (/) from session (shortcut)
     - CS_CoreDir:   The core directory of crosshell (/core) from session (shortcut)
     - input:        if capture is set to true a custom "safe" input function will be set ("safe" = buffer safe)
     - exit:         crosshell will replace the standard exit function with a "safe" one ("safe" = non-crosshell terminating)
     - CS_oinput:    the standard input function
     - CS_oexit:     the standard exit function

    '''
    # Some setting up
    captured_output = None
    ## use tmp var incase nontype return
    command,args,_cmdletData = getCmdletData(csSession,command,args)
    ## handle no cmdlet found
    if _cmdletData == None:
        csSession.deb.perror("lng:cs.cmdletexec.notfound, txt:Cmdlet '{command}' not found!",{"command":command,"args":args},raiseEx=True)
    ## copy to var that can be used (copy needed to not f with registry)
    cmdletData = _cmdletData.copy()
    reader = determine_reader(cmdletData["fending"],csSession.registry)
    # Get globals and stdout based on abunch of stuff
    globalValues,ept,old_stdout,buffer = getGlobals(csSession,command,args,cmdletData,globalValues,entries,reader,capture,inpipeLine)
    if capture == True:
        sys.stdout = buffer
    # Execute script
    CatchSystemExit   = csSession.data["set"].getProperty("crsh","Execution.SafelyHandleExit")
    HandleCmdletError = csSession.data["set"].getProperty("crsh","Execution.HandleCmdletError")
    PrintCmdletDebug  = csSession.data["set"].getProperty("crsh","Execution.PrintCmdletDebug")
    # Handle cmdleterror
    if HandleCmdletError == True:
        try:
            # INTERNAL_PYTHON
            if reader["name"] == "INTERNAL_PYTHON":
                exec(open(cmdletData["path"],encoding=cmdletData["encoding"]).read(), globalValues)
            # Other reader
            else:
                _retVars = cmdletData["options"]["readerReturnVars"]
                # Check if should sendback vars
                _readerReturn = exec_reader(csSession,reader["exec"],cmdletData,args,cmdletData["encoding"],capture,globalValues,globals(),retVars=_retVars)
                if _retVars == True and _readerReturn != None:
                    csSession.uppVarScope(_readerReturn)

        # CrosshellExit
        except CrosshellExit as CS_CmdletExitcode:
            if CatchSystemExit:
                if str(CS_CmdletExitcode) == "cs.exit": exit()
                else: pass
            else: exit()
        # SystemExit
        except SystemExit as CS_CmdletExitcode:
            if CatchSystemExit:
                if str(CS_CmdletExitcode) == "cs.exit": exit()
                else: pass
            else: exit()
        # Other
        except Exception:
            if PrintCmdletDebug == True:
                ept["traceback"] = traceback.format_exc()
                # MAKE THEESE USE crshDebug
                csSession.deb.perror("lng:cs.cmdletexec.traceback",ept)

            else:
                csSession.deb.perror("lng:cs.cmdletexec.error",ept)
    # Don't handle cmdleterror
    else:
        try:
            # INTERNAL_PYTHON
            if reader["name"] == "INTERNAL_PYTHON":
                exec(open(cmdletData["path"],encoding=cmdletData["encoding"]).read(), globalValues)
            # Other reader
            else:
                # Check if should sendback vars
                _readerReturn = exec_reader(csSession,reader["exec"],cmdletData,args,cmdletData["encoding"],capture,globalValues,globals(),retVars=cmdletData["options"]["readerReturnVars"])
                if _readerReturn != None:
                    csSession.uppVarScope(_readerReturn)
        # CrosshellExit
        except CrosshellExit as CS_CmdletExitcode:
            if CatchSystemExit:
                if str(CS_CmdletExitcode) == "cs.exit": exit()
                else: pass
            else: exit()
        # SystemExit
        except SystemExit as CS_CmdletExitcode:
            if CatchSystemExit:
                if str(CS_CmdletExitcode) == "cs.exit": exit()
                else: pass
            else: exit()
    # If capture output is true, restore stdout settings and save the captured output
    if capture == True:
        sys.stdout = old_stdout
        captured_output = buffer.getBufferS()
        buffer.clearBuffer()
    # Set ANS
    if captured_output != None and captured_output != "" and captured_output.replace(" ","") != "":
        curVal = csSession.data["cvm"].getvar("ans")
        if curVal != None:
            if captured_output.strip() != curVal.strip():
                csSession.data["cvm"].chnvar("ans",captured_output)
        else:
            csSession.data["cvm"].setvar("ans",captured_output)
    # Return
    if captured_output != None:
        return captured_output
    else:
        return ""

# Execline class
class execline():
    '''CSlib.execution: Main crosshell exec-line class.'''
    def __init__(self):
        self._reset_execline()
        self.session = None
    def _reset_execline(self):
        self.execline = {
            "segments": [],
            "current_content": None
        }
    def setSegments(self,segments=list):
        self._reset_execline()
        self.execline["segments"] = segments
    def execute(self,csSession,globalValues=dict,globalEntries=list):
        # Segments are basicly diffrent piplines, that each contain pipeline elements, such elements contain expressions
        segments = self.execline["segments"]
        # Iterate segments
        for segment in segments:
            # Reset content for next segment
            self.execline["current_content"] = None
            # Loop elements
            for elemIndex,element in enumerate(segment):
                # If content != None add to args
                if self.execline["current_content"] != None:
                    if "%" in element["args"]:
                        for i,arg in enumerate(element["args"]):
                            if arg == "%":
                                element["args"][i] = self.execline["current_content"]
                    else:
                        element["args"] = [self.execline["current_content"],*element["args"]]
                # Add modified globals to globalValues so that they are available to the next expression
                if self.session != None:
                    globalValues.update(self.session.getVarScope())
                # Execute expression
                _cont = execute_expression(
                    csSession    = csSession,
                    command      = element["cmd"],
                    args         = element["args"],
                    #capture      = elemIndex < len(segment)-1,
                    capture      = True,
                    globalValues = globalValues,
                    entries= globalEntries,
                    inpipeLine= len(segment) > 1
                )
                if _cont != None:
                    self.execline["current_content"] = _cont
        out = self.execline["current_content"]
        self._reset_execline()
        return out.strip("\n")

def extract_codeblocks(s):
    '''CSlib.execution: Function to extract codeblock regions'''
    # Use a regular expression to find all blocks enclosed in brackets
    matches = re.findall(r'\{[^{}]*\}', s)
    # Sort matches by length in descending order
    sorted_matches = sorted(matches, key=len, reverse=True)
    # Filter out matches that are contained within others
    non_overlapping_matches = []
    for i, match in enumerate(sorted_matches):
        if not any(match in other for other in sorted_matches[:i] + sorted_matches[i + 1:]):
            non_overlapping_matches.append(match)
    return non_overlapping_matches

def exclude_codeblocks(input_string):
    extracts = extract_codeblocks(input_string)
    for extract in extracts:
        input_string = input_string.replace(extract,"!cs.codeblock!")
    return (input_string, extracts)

def include_codeblocks(input_string, substrings):
    for substring in substrings:
        input_string = input_string.replace("!cs.codeblock!", substring, 1)
    return input_string

def determine_delims(csSession,baseDelims=["||"]) -> list:
    '''CSlib.execution: Function to determine delims to use by settings.'''
    splitByNewline = csSession.data["set"].getProperty("crsh","Execution.SplitByNewline")
    if splitByNewline == True: baseDelims.append("\n")
    return baseDelims

def input_to_pipelineStructure(csSession,sinput=str,basicExecutionDelimiters=["||"]) -> list:
    '''CSlib.execution: Function to convert input to the pipeline structure.'''
    # Split to execution order
    execution_order = splitByDelimiters(sinput,basicExecutionDelimiters)
    # Split into pipeline (Note! this function should only ever be called with simple pipeline syntax: " | ")
    pipelineSplit_executionOrder = []
    for partial in execution_order:
        partial = partial.strip() # strip partials
        spartial = partial.split("|")
        # Expression
        for i,expression in enumerate(spartial):
            stripped_expression = expression.strip() # strip expression
            # split by spaces to sepparete args from cmd
            split_expression = split_string_by_spaces(stripped_expression)
            # sort
            if len(split_expression) > 0:
                cmd = split_expression[0]
                split_expression.pop(0)
                for i2,part in enumerate(split_expression):
                    split_expression[i2] = part.replace("!cs.nl!","\n")
            else:
                cmd,split_expression = expression,[]
            dict_expression = {"cmd":cmd, "args":split_expression}
            # add
            spartial[i] = dict_expression
        # add to partial
        pipelineSplit_executionOrder.append(spartial)
    # return
    return pipelineSplit_executionOrder

from .datafiles import _fileHandler

def execute_string(string,csSession,capture=False,globalVals={},entries=None):
    print(string)
    # Get entries
    _entries = _fileHandler("json","get",csSession.data["gef"])
    if entries != [] and entries != None:
        entries.extend(_entries)
    else:
        entries = _entries
    split_expression = split_string_by_spaces(string.strip())
    # sort
    if len(split_expression) > 0:
        cmd = split_expression[0]
        split_expression.pop(0)
    return execute_expression(csSession,cmd,split_expression,capture,globalVals,entries)
    