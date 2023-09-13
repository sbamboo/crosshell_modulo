from cslib.execution import execline
from cslib.externalLibs.conUtils import setConTitle
from cslib._crosshellParsingEngine import exclude_nonToFormat,include_nonToFormat
from cslib import CrosshellDebErr

CS_PipeLine = execline()
while True:
    title = CS_Persistance.getProperty("crsh","Title")
    if title == None:
        title = CS_Settings.getProperty("crsh","Console.DefTitle")
    setConTitle( title )
    _prefix = getPrefix(csSession,"> ")
    CS_LastInput = input(_prefix)
    CS_LastOutput = None
    if CS_LastInput != "":
        CS_Inpparse.execute_internally(globals())
        CS_Exec.execute_internally(globals())
    if CS_LastOutput != None and CS_LastOutput != "":
        if type(CS_LastOutput) == str:
            # Global Text System
            pre,subs = exclude_nonToFormat(CS_LastOutput)
            mid = csSession.data["txt"].parse(pre)
            end = include_nonToFormat(mid,subs)
            print(end)
        elif type(CS_LastOutput) == CrosshellDebErr:
            print(CS_LastOutput)