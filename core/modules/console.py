from cslib.execution import execline

CS_PipeLine = execline()
while True:
    _prefix = getPrefix(csSession,"> ")
    CS_LastInput = input(_prefix)
    CS_LastOutput = None
    CS_Inpparse.execute_internally(globals())
    CS_Exec.execute_internally(globals())
    if CS_LastOutput != None:
        print(CS_LastOutput)