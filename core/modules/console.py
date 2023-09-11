from cslib.execution import execline
from cslib.externalLibs.conUtils import setConTitle
from cslib._crosshellParsingEngine import exclude_nonToFormat,include_nonToFormat

CS_PipeLine = execline()
while True:
    setConTitle( CS_Persistance.getProperty("crsh","Title") )
    _prefix = getPrefix(csSession,"> ")
    CS_LastInput = input(_prefix)
    CS_LastOutput = None
    CS_Inpparse.execute_internally(globals())
    CS_Exec.execute_internally(globals())
    if CS_LastOutput != None and CS_LastOutput != "":
        # Global Text System
        pre,subs = exclude_nonToFormat(CS_LastOutput)
        mid = csSession.data["txt"].parse(pre)
        end = include_nonToFormat(mid,subs)
        print(end)