import os,sys,subprocess
from cslib._crosshellParsingEngine import splitByDelimiters,split_string_by_spaces
from cslib.longPathHandler import lph_isAllowed
from cslib.pipeline import argumentHandler
from cslib.datafiles import _fileHandler
from cslib.pathtools import normPathSep
from cslib.exceptions import CrosshellDebErr
from cslib.piptools import fromPath
from cslib.customImplements import customMethod_exit

def input_to_pipelineStructure(sinput=str,basicExecutionDelimiters=["||"]) -> list:
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
            dict_expression = {"cmd":cmd, "args":split_expression, "type":"file"}
            # add
            spartial[i] = dict_expression
        # add to partial
        pipelineSplit_executionOrder.append(spartial)
    # return
    return pipelineSplit_executionOrder

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
    # setup globals
    globalsToReader["cs_isCaptured"] = isCaptured
    globalsToReader["cs_defEncoding"] = csSession.getEncoding()
    globalsToReader["cs_readerPath"] = readerPath
    globalsToReader["cs_lph_isAllowed"] = lph_isAllowed
    globalsToReader["cs_runShell"] = runShell
    # create and exec command
    module = None
    try:
        #exec(open(readerPath,'r',encoding=csSession.getEncoding()).read(),globalsToReader)
        module = fromPath(readerPath,globalsToReader)
    except FileNotFoundError:
        csSession.deb.perror("lng:cs.cmdletexec.reader.errornotfound",{"reader":os.path.basename(readerPath),"readerPath":readerPath})
    except Exception as e:
        csSession.deb.perror("lng:cs.cmdletexec.reader.errorinexec",{"reader":os.path.basename(readerPath),"readerPath":readerPath,"traceback":e})
    # execute reader-defined main command
    if module != None:
        try:
            retVars = module.main(csSession,cmddata=command,args=cmdargs,encoding=encoding,defencoding=csSession.getEncoding(),isCaptured=isCaptured,globalValues=globalValues)
        except CrosshellDebErr as e:
            raise
        except Exception as e:
            if not hasattr(module, 'main') or not callable(getattr(module,'main')):
                csSession.deb.perror("lng:cs.cmdletexec.reader.nomainfunc",{"reader":os.path.basename(readerPath),"readerPath":readerPath,"traceback":e})
            else:
                csSession.deb.perror("lng:cs.cmdletexec.reader.errorincall",{"reader":os.path.basename(readerPath),"readerPath":readerPath,"traceback":e})
        if retVars != False:
            return retVars
    else:
        csSession.deb.perror("lng:cs.cmdletexec.reader.failedtoloadmodule",{"reader":os.path.basename(readerPath),"readerPath":readerPath})

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
    def execute(self,csSession):
        for segment in self.execline["segments"]:
            for partial in segment:
                # Make globaldata
                globalData = csSession.initDefaults["cmdletGlobals"]
                globalData["args"] = argumentHandler(partial.get("args"))
                if csSession.getregister("set").getProperty("crsh","Execution.SafelyHandleExit") == True:
                    globalData["exit"] = customMethod_exit
                    globalData["CS_oexit"] = exit
                # Act based on handle
                handle = partial.get("handle")
                if handle != None:
                    # Run
                    if handle == "valid":
                        cmdData = partial["cmd"]
                        if cmdData["type"] == "file":
                            path = cmdData["path"]
                            if cmdData.get("reader") != None:
                                if cmdData["reader"] == "INTERNAL_PYTHON":
                                    exec(open(path,'r',encoding=csSession.getEncoding()).read(),globalData)
                                else:
                                    # Get reader file content
                                    readerPath = None
                                    for entry in csSession.regionalGet("ReaderRegistry"):
                                        if entry["name"] == cmdData["reader"]:
                                            readerPath = entry["exec"]
                                            break
                                    readerPath = normPathSep(csSession.getregister("stm").eval("ptm",readerPath))
                                    if readerPath != None and os.path.exists(readerPath):
                                        cmdletEncoding = cmdData["data"].get("encoding")
                                        exec_reader(
                                            csSession = csSession,
                                            readerPath = readerPath,
                                            command = cmdData,
                                            cmdargs = partial["args"],
                                            encoding = cmdletEncoding if cmdletEncoding != "CMDLET_ENCODING" else None,
                                            isCaptured = False,
                                            globalValues = globalData,
                                            globalsToReader = csSession.initDefaults["readerCallGlobals"],
                                            retVars = False
                                        )
                            else:
                                csSession.deb.perror("lng:cs.cmdletexec.emptyreaderfield, txt:No reader was found for the cmdlet '{command}'!",{"command":cmdData.get("name"),"args":partial.get("args"),"type":partial.get("type")},raiseEx=True)
                        elif cmdData["type"] == "method":
                            cmdData["method"](globalData)
                    # Raise
                    elif handle == "invalid":
                        cmdData = partial.get("cmd")
                        if type(cmdData) == dict:
                            cmdData = cmdData.get("name")
                        if cmdData == None:
                            cmdData = ""
                        csSession.deb.perror("lng:cs.cmdletexec.notfound, txt:Cmdlet '{command}' not found!",{"command":cmdData,"args":partial.get("args"),"type":partial.get("type")},raiseEx=True)