from io import StringIO
import traceback

from ..cslib.externalLibs.filesys import filesys as fs
from ..cslib import handleOSinExtensionsList

def prep_globals(globalValue=dict,entries=list):
    newGlobals = {}
    for entry in entries:
        newGlobals[entry] = globalValue[entry]
    return newGlobals

def determine_reader(fending=str,registry=dict) -> str:
    if fending == None:
        fending = "MIME_EXECUTABLE"
    # Match
    readers = registry["readerData"]
    for reader in readers:
        if fending in handleOSinExtensionsList(reader["extensions"]):
            return reader

def get_command_data(command=str,registry=dict) -> str:
    for cmdlet,cmdletData in registry["cmdlets"]:
        if cmdlet.lower() == command.lower():
            return cmdletData

def execute_expression(csSession,command=str,args=list,capture=False,globalValues=dict,entries=list):
    cmdletData = command_to_path(command,csSession.registry)
    reader = determine_reader(cmdletData["fending"],csSession.registry)
    # Fix global values to use
    globalValues = prep_globals(globalValues,entries)
    # Add standard values
    globalValues["argv"] = args
    globalValues["CSScriptRoot"] = os.path.abspath(os.path.dirname(cmdletData["path"]))
    globalValues["CSScriptData"] = cmdletData["reader"] = reader
    globalValues["CSPackDir"] = csSession.data["ptm"].getTag("CS_CoreDir")
    # Fix pathtags for error printing
    ept = cmdletData
    ept["reader"].pop("obj")
    # INTERNAL_PYTHON
    if reader == "INTERNAL_PYTHON":
        # If capture is true, redirect stdout
        if capture == True:
            old_stdout = sys.stdout
            redirected_stdout = sys.stdout = StringIO()
        # Execute script
        CatchSystemExit   = csSession.data["set"].getProperty("crsh","Execution.CatchSystemExit")
        HandleCmdletError = csSession.data["set"].getProperty("crsh","Execution.HandleCmdletError")
        PrintCmdletDebug  = csSession.data["set"].getProperty("crsh","Execution.PrintCmdletDebug")
        if HandleCmdletError == True:
            try:
                exec(open(cmdletData["path"],'r',encoding=cmdletData["encoding"]).read(), globalValues)
            except Exception:
                if PrintCmdletDebug == True:
                    ept["traceback"] = traceback.format_exc()
                    csSession["lng"].print("cs.cmdletexec.traceback",ept=ept)
                else:
                    csSession["lng"].print("cs.cmdletexec.error",ept=ept)
    # PLATFORM_EXECUTABLE
    elif reader == "PLATFORM_EXECUTABLE":
        pass
    # Other readers
    else:
        pass
