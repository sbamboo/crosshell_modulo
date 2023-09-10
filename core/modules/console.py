from cslib.execution import execline

while True:
    CS_LastInput = input("> ")
    CS_LastOutput = None
    CS_PipeLine = execline()
    CS_Inpparse.execute_internally(globals())
    CS_Exec.execute_internally(globals())
    if CS_LastOutput != None:
        print(CS_LastOutput)