from cslib.execution import input_to_pipelineStructure,execline
from cslib.externalLibs.conUtils import clear,setConTitle
from cslib.exceptions import CrosshellDebErr,CrosshellExit

# region: [Components]
def console_component(csSession):

    # Create a persistant pipeline to not have to recreate it on each prompt
    _pipeline = execline()

    # Get settings obj
    _set = csSession.getregister("set")

    # Prep console
    if _set.getProperty("crsh","Console.ClearOnStart") == True:
        if csSession.regionalGet("Pargs").nocls != True:
            clear(skipSetXY=csSession.regionalGet("StripAnsi"))
    if _set.getProperty("crsh","Console.TitleEnabled") == True:
        setConTitle( csSession.getTitle() )

    # Get prefix
    if _set.getProperty("crsh","Console.PrefixEnabled") == True:
        prefix = csSession.getPrefix()
    else:
        prefix = ""

    # Define "running" state
    csSession.flags.enable("--consoleRunning")

    # Loop and prompt
    ret = None
    try:
        while csSession.flags.has("--consoleRunning"):
            ret = csSession.eprompt(prefix,_pipeline=_pipeline)
            if ret != None: print(ret)
    except KeyboardInterrupt:
        print("\n[Crosshell]: Ended by keyboard interrupt. Bya <3")
    del _set
    return ret

def interpriter_component(csSession,input_=str,_pipeline=None) -> object:
    # Ensure a execline obj
    if _pipeline == None:
        pipeline = execline()
    else:
        pipeline = _pipeline

    # Get it into a basic pipeline-structure
    pipelineStructure = input_to_pipelineStructure(input_,basicExecutionDelimiters=["||",";"])
    # Retrive the path/method to exec
    for segI,segment in enumerate(pipelineStructure):
        for parI,partial in enumerate(segment):
            if partial["cmd"].strip() != "":
                for cmdletID,cmdletData in csSession.regionalGet("LoadedPackageData")["cmdlets"]["data"].items():
                    cmdAliases = cmdletData["data"].get("aliases")
                    if cmdAliases == None: cmdAliases = []
                    if partial["cmd"] == cmdletData["name"] or partial["cmd"] in cmdAliases: #TODO: assuming string aliases might not be the best
                        pipelineStructure[segI][parI]["cmd"] = cmdletData
                        pipelineStructure[segI][parI]["handle"] = "valid"
                        break
                else:
                    pipelineStructure[segI][parI]["handle"] = "invalid"
            else:
                pipelineStructure[segI][parI]["handle"] = "ignore"
    pipeline.setSegments(pipelineStructure)
    return pipeline

def execute_component(csSession,execline=object) -> object:
    catchSysExit = csSession.getregister("set").getProperty("crsh","Execution.SafelyHandleExit")
    try:
        return execline.execute(csSession)
    except CrosshellExit as e:
        if catchSysExit == True and str(e) == "cs.exit": exit()
        else: pass
    except CrosshellDebErr as e:
        return e
    except SystemExit as e:
        if catchSysExit == True and str(e) == "cs.exit": exit()
        else: pass

def prompt_component(csSession,prompt=str) -> str:
    return input(prompt)
# endregion