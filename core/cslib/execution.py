from io import StringIO
import traceback
import os
import sys
import subprocess

from cslib.externalLibs.filesys import filesys as fs
from cslib import handleOSinExtensionsList,CrosshellExit,CrosshellDebErr
from cslib._crosshellParsingEngine import splitByDelimiters
from cslib.longPathHandler import lph_isAllowed
from cslib._crosshellParsingEngine import split_string_by_spaces

def prep_globals(globalValue=dict,entries=list):
    '''CSlib: Function to filter globals by entries.'''
    newGlobals = {}
    for entry in entries:
        newGlobals[entry] = globalValue[entry]
    return newGlobals

def determine_reader(fending=str,registry=dict) -> str:
    '''CSlib: Function to determine the reader from the registry using fending.'''
    if fending == None:
        fending = "MIME_EXECUTABLE"
    # Match
    readers = registry["readerData"]
    for reader in readers:
        if fending in handleOSinExtensionsList(reader["extensions"]):
            return reader

def get_command_data(command=str,registry=dict) -> str:
    '''CSlib: Function to get command data from the registry.'''
    for cmdlet,cmdletData in registry["cmdlets"].items():
        if cmdlet.lower() == command.lower():
            return cmdletData

def safe_decode_utf8_cp437(bytestring,defencoding="utf-8"):
    '''CSlib: Function safely handle unicode and/or cp437.'''
    try:
        decoded_string = bytestring.decode(defencoding)
    except:
        decoded_string = bytestring.decode('cp437', errors='replace')
    return decoded_string

def runShell(csSession,shellExecPath=str,shellExecArgs=[],capture=False,cmdletpath=str,cmdletargs=[],defencoding="utf-8"):
    '''CSlib: Function to execute a command using a shell program.'''
    execList = [f'{shellExecPath}', *shellExecArgs, cmdletpath, *cmdletargs]
    # check long path safety
    if lph_isAllowed(' '.join(execList)) == False:
        csSession.deb.perror("lng:cs.cmdletexec.longpath.disabled",raiseEx=True)
    # Capture output if enabled otherwise just execute the subprocess
    if capture == False:
        subprocess.run(execList, stderr=sys.stderr, stdout=sys.stdout)
    else:
        proc = subprocess.Popen(execList, stderr=sys.stderr, stdout=subprocess.PIPE)
        out = proc.communicate()[0] # Get output
        out = safe_decode_utf8_cp437(out,defencoding)
        return out

def exec_reader(csSession,readerPath=str,command=str,cmdargs=list,encoding=str,isCaptured=bool,globalValues=dict,globalsToReader=dict,retVars=False):
    '''CSlib: Function to execute a command using a reader.'''
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
        raise # << DEBUG
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

def safe_exit(code=None):
    raise CrosshellExit(code)

def execute_expression(csSession,command=str,args=list,capture=False,globalValues=dict,entries=list):
    '''CSlib: Main expression executer.
    Entries are a list of al globalValue entries that should be included, no other ones will get sent to the cmdlet!'''
    # Some setting up
    cmdletData = get_command_data(command,csSession.registry)
    if cmdletData == None:
        csSession.deb.perror("lng:cs.cmdletexec.notfound, txt:Cmdlet '{command}' not found!",{"command":command,"args":args},raiseEx=True)
    reader = determine_reader(cmdletData["fending"],csSession.registry)
    # Fix global values to use
    if cmdletData["options"]["restrictionMode"].lower() != "internal" or csSession.data["set"].getProperty("crsh_debugger","Execution.AllowRunAsInternal") != True:
        globalValues = prep_globals(globalValues,entries)
    # Add standard values
    scriptroot = os.path.abspath(os.path.dirname(cmdletData["path"]))
    globalValues["argv"] = args
    globalValues["sargv"] = (" ".join(args)).strip(" ")
    globalValues["CSScriptRoot"] = scriptroot
    globalValues["CSScriptData"] = cmdletData["reader"] = reader
    globalValues["CS_PackDir"] = getPackdir( csSession.data["ptm"].getTag("CS_BaseDir"),scriptroot,0 )
    globalValues["CS_CurDir"] = csSession.data["dir"]
    globalValues["CS_BaseDir"] = csSession.data["bdr"]
    globalValues["CS_CoreDir"] = csSession.data["cdr"]
    # Safe exit handling
    if csSession.data["set"].getProperty("crsh","Execution.SafelyHandleExit"):
        globalValues["exit"] = safe_exit # overwrite exit
    # Fix pathtags for error printing
    cmdletData["name"] = command
    ept = cmdletData
    # If capture is true, redirect stdout
    if capture == True:
        old_stdout = sys.stdout
        redirected_stdout = sys.stdout = StringIO()
    # Execute script
    CatchSystemExit   = csSession.data["set"].getProperty("crsh","Execution.CatchSystemExit")
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
        captured_output = redirected_stdout.getvalue()
    # Set ANS
    if captured_output != None and captured_output != "" and captured_output.replace(" ","") != "":
        if captured_output.strip() != csSession.data["cvm"].getvar("ans").strip():
            csSession.data["cvm"].chnvar("ans",captured_output)
    # Return
    if captured_output != None:
        return captured_output
    else:
        return ""

# Execline class
class execline():
    '''CSlib: Main crosshell exec-line class.'''
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
            for element in segment:
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
                self.execline["current_content"] = execute_expression(
                    csSession    = csSession,
                    command      = element["cmd"],
                    args         = element["args"],
                    capture      = True,
                    globalValues = globalValues,
                    entries= globalEntries
                )
        out = self.execline["current_content"]
        self._reset_execline()
        return out.strip("\n")

def determine_delims(csSession,baseDelims=["||"]) -> list:
    '''CSlib: Function to determine delims to use by settings.'''
    splitByNewline = csSession.data["set"].getProperty("crsh","Execution.SplitByNewline")
    if splitByNewline == True: baseDelims.append("\n")
    return baseDelims

def input_to_pipelineStructure(csSession,sinput=str,basicExecutionDelimiters=["||"]) -> list:
    '''CSlib: Function to convert input to the pipeline structure.'''
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
            else:
                cmd,split_expression = expression,[]
            dict_expression = {"cmd":cmd, "args":split_expression}
            # add
            spartial[i] = dict_expression
        # add to partial
        pipelineSplit_executionOrder.append(spartial)
    # return
    return pipelineSplit_executionOrder