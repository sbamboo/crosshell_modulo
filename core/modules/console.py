from cslib.execution import execline
from cslib.externalLibs.conUtils import setConTitle

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
        print( csSession.data["txt"].parse(CS_LastOutput) )